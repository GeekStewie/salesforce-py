"""Tests for salesforce_py.bulk.operations.query."""

from __future__ import annotations

import pytest

from salesforce_py.bulk._soql import OrderByClause
from salesforce_py.exceptions import SalesforcePyError
from tests.bulk.conftest import make_client, make_response


class TestCreateJob:
    async def test_plain_query_passes_through(self):
        body = {"id": "750yy", "state": "UploadComplete"}
        client = await make_client(mock_post=make_response(200, json_body=body))

        result = await client.query.create_job(soql="SELECT Id FROM Account")

        assert result["id"] == "750yy"
        assert result["_stripped_order_by"] is None
        payload = client._session.post.await_args.kwargs["json"]
        assert payload["query"] == "SELECT Id FROM Account"
        assert payload["operation"] == "query"
        await client.close()

    async def test_order_by_is_stripped_and_captured(self):
        body = {"id": "750yy", "state": "UploadComplete"}
        client = await make_client(mock_post=make_response(200, json_body=body))

        soql = "SELECT Id FROM Account ORDER BY CreatedDate DESC LIMIT 100"
        result = await client.query.create_job(soql=soql)

        payload = client._session.post.await_args.kwargs["json"]
        assert payload["query"] == "SELECT Id FROM Account LIMIT 100"
        stripped = result["_stripped_order_by"]
        assert isinstance(stripped, OrderByClause)
        assert stripped.columns == (("CreatedDate", "DESC", None),)
        await client.close()

    async def test_query_all_operation(self):
        body = {"id": "750yy"}
        client = await make_client(mock_post=make_response(200, json_body=body))

        await client.query.create_job(soql="SELECT Id FROM Account", operation="queryAll")

        assert client._session.post.await_args.kwargs["json"]["operation"] == "queryAll"
        await client.close()

    async def test_invalid_query_operation_raises(self):
        client = await make_client(mock_post=make_response(200, json_body={}))
        with pytest.raises(ValueError, match="Invalid query operation"):
            await client.query.create_job(soql="SELECT Id FROM Account", operation="insert")
        client._session.post.assert_not_awaited()
        await client.close()

    async def test_unsupported_soql_rejected_before_request(self):
        client = await make_client(mock_post=make_response(200, json_body={}))
        with pytest.raises(ValueError, match="GROUP BY"):
            await client.query.create_job(soql="SELECT Id FROM Account GROUP BY Name")
        client._session.post.assert_not_awaited()
        await client.close()


class TestGetResults:
    async def test_returns_csv_and_parses_pagination_headers(self):
        csv = b"Id,Name\n001,Acme\n002,Beta\n"
        client = await make_client(
            mock_get=make_response(
                200,
                content=csv,
                headers={"Sforce-Locator": "XYZ", "Sforce-NumberOfRecords": "2"},
            )
        )

        body, locator, count = await client.query.get_results("750yy")

        assert body == csv
        assert locator == "XYZ"
        assert count == 2
        await client.close()

    async def test_null_locator_becomes_none(self):
        client = await make_client(
            mock_get=make_response(
                200,
                content=b"Id\n001\n",
                headers={"Sforce-Locator": "null", "Sforce-NumberOfRecords": "1"},
            )
        )
        _, locator, _ = await client.query.get_results("750yy")
        assert locator is None
        await client.close()


class TestGetAllResults:
    async def test_pages_are_concatenated_and_sorted(self, monkeypatch):
        """All pages are downloaded, concatenated, then re-sorted by ORDER BY."""
        from salesforce_py.bulk.operations import query as query_mod

        async def fake_get_results(self, job_id, *, locator=None, max_records=None):
            if locator is None:
                return b"Id,Name\n002,Charlie\n", "LOC2", 1
            return b"Id,Name\n001,Alice\n", None, 1

        monkeypatch.setattr(query_mod.QueryOperations, "get_results", fake_get_results)

        client = await make_client()
        clause = OrderByClause(raw="Name", columns=(("Name", "ASC", None),))

        combined = await client.query.get_all_results("750yy", order_by=clause)

        rows = combined.strip().split(b"\n")
        assert rows[0] == b"Id,Name"
        assert rows[1] == b"001,Alice"
        assert rows[2] == b"002,Charlie"
        await client.close()

    async def test_no_order_by_skips_sort(self, monkeypatch):
        from salesforce_py.bulk.operations import query as query_mod

        async def fake_get_results(self, job_id, *, locator=None, max_records=None):
            return b"Id,Name\n002,Charlie\n001,Alice\n", None, 2

        monkeypatch.setattr(query_mod.QueryOperations, "get_results", fake_get_results)

        client = await make_client()
        combined = await client.query.get_all_results("750yy", order_by=None)
        # Preserves server order — no re-sort.
        assert combined == b"Id,Name\n002,Charlie\n001,Alice\n"
        await client.close()


class TestRunQuery:
    async def test_end_to_end_completes_on_job_complete(self, monkeypatch):
        """run_query polls until JobComplete, then downloads results."""
        from salesforce_py.bulk.operations import query as query_mod

        # Make asyncio.sleep a no-op so poll loops finish immediately.
        async def _no_sleep(_seconds):
            return None

        monkeypatch.setattr(query_mod.asyncio, "sleep", _no_sleep)

        create_body = {"id": "750yy"}
        status_body = {"state": "JobComplete"}
        client = await make_client(
            mock_post=make_response(200, json_body=create_body),
            mock_get=make_response(200, json_body=status_body),
        )

        async def fake_get_all_results(self, job_id, **kwargs):
            return b"Id\n001\n"

        monkeypatch.setattr(
            query_mod.QueryOperations, "get_all_results", fake_get_all_results
        )

        result = await client.query.run_query("SELECT Id FROM Account")

        assert result == b"Id\n001\n"
        await client.close()

    async def test_failed_state_raises(self, monkeypatch):
        from salesforce_py.bulk.operations import query as query_mod

        async def _no_sleep(_seconds):
            return None

        monkeypatch.setattr(query_mod.asyncio, "sleep", _no_sleep)

        client = await make_client(
            mock_post=make_response(200, json_body={"id": "750yy"}),
            mock_get=make_response(
                200, json_body={"state": "Failed", "errorMessage": "boom"}
            ),
        )

        with pytest.raises(SalesforcePyError, match="Failed"):
            await client.query.run_query("SELECT Id FROM Account")
        await client.close()
