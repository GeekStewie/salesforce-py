"""Tests for salesforce_py.rest.operations.query."""

from __future__ import annotations

from tests.rest.conftest import make_client, make_response


class TestQuery:
    async def test_query_passes_soql_as_q_param(self):
        body = {"totalSize": 1, "done": True, "records": [{"Id": "001"}]}
        client = await make_client(mock_get=make_response(200, json_body=body))

        result = await client.query.query("SELECT Id FROM Account")

        assert result == body
        call = client._session.get.await_args
        assert call.args[0] == "query"
        assert call.kwargs["params"] == {"q": "SELECT Id FROM Account"}
        await client.close()

    async def test_query_all_hits_queryall_endpoint(self):
        body = {"totalSize": 0, "done": True, "records": []}
        client = await make_client(mock_get=make_response(200, json_body=body))

        await client.query.query_all("SELECT Id FROM Account")

        call = client._session.get.await_args
        assert call.args[0] == "queryAll"
        await client.close()

    async def test_query_more_strips_version_prefix_when_present(self):
        body = {"totalSize": 0, "done": True, "records": []}
        client = await make_client(mock_get=make_response(200, json_body=body))

        await client.query.query_more(
            "/services/data/v66.0/query/01gXX000000AbcDEF"
        )

        call = client._session.get.await_args
        assert call.args[0] == "query/01gXX000000AbcDEF"
        await client.close()

    async def test_query_more_strips_any_version_prefix(self):
        body = {"totalSize": 0, "done": True, "records": []}
        client = await make_client(mock_get=make_response(200, json_body=body))

        # Different version than the client — the operation should still strip
        await client.query.query_more(
            "/services/data/v60.0/queryAll/01gXX000000AbcDEF"
        )

        call = client._session.get.await_args
        assert call.args[0] == "queryAll/01gXX000000AbcDEF"
        await client.close()

    async def test_query_more_accepts_relative_locator(self):
        body = {"totalSize": 0, "done": True, "records": []}
        client = await make_client(mock_get=make_response(200, json_body=body))

        await client.query.query_more("query/01gXX000000AbcDEF")

        call = client._session.get.await_args
        assert call.args[0] == "query/01gXX000000AbcDEF"
        await client.close()


class TestQueryAllRecords:
    async def test_drains_all_pages(self):
        page_1 = {
            "totalSize": 3,
            "done": False,
            "records": [{"Id": "001a"}, {"Id": "001b"}],
            "nextRecordsUrl": "/services/data/v66.0/query/01gXX000000Next",
        }
        page_2 = {
            "totalSize": 3,
            "done": True,
            "records": [{"Id": "001c"}],
        }
        # Alternate responses: first `query`, then `query_more`
        from unittest.mock import AsyncMock

        client = await make_client(mock_get=make_response(200, json_body=page_1))
        client._session.get = AsyncMock(
            side_effect=[
                make_response(200, json_body=page_1),
                make_response(200, json_body=page_2),
            ]
        )

        records = await client.query.query_all_records("SELECT Id FROM Account")

        assert [r["Id"] for r in records] == ["001a", "001b", "001c"]
        assert client._session.get.await_count == 2
        await client.close()

    async def test_returns_single_page_when_done(self):
        body = {
            "totalSize": 1,
            "done": True,
            "records": [{"Id": "001"}],
        }
        client = await make_client(mock_get=make_response(200, json_body=body))

        records = await client.query.query_all_records("SELECT Id FROM Account")

        assert records == [{"Id": "001"}]
        assert client._session.get.await_count == 1
        await client.close()


class TestAsyncQuery:
    async def test_submit_posts_to_async_queries(self):
        body = {"id": "08PXX0000000001"}
        client = await make_client(mock_post=make_response(200, json_body=body))

        await client.query.submit_async_query({"query": "SELECT Id FROM BigObject__b"})

        call = client._session.post.await_args
        assert call.args[0] == "async-queries"
        assert call.kwargs["json"] == {"query": "SELECT Id FROM BigObject__b"}
        await client.close()

    async def test_get_fetches_by_job_id(self):
        body = {"id": "08PXX0000000001", "status": "Completed"}
        client = await make_client(mock_get=make_response(200, json_body=body))

        await client.query.get_async_query("08PXX0000000001")

        call = client._session.get.await_args
        assert call.args[0] == "async-queries/08PXX0000000001"
        await client.close()

    async def test_delete_uses_delete_verb(self):
        client = await make_client(mock_delete=make_response(204))

        await client.query.delete_async_query("08PXX0000000001")

        call = client._session.delete.await_args
        assert call.args[0] == "async-queries/08PXX0000000001"
        await client.close()
