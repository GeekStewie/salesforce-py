"""Tests for salesforce_py.bulk.operations.ingest."""

from __future__ import annotations

import pytest

from salesforce_py.bulk._limits import MAX_UPLOAD_BYTES_RAW
from tests.bulk.conftest import make_client, make_response


class TestCreateJob:
    async def test_insert_posts_expected_payload(self):
        body = {"id": "750xx", "state": "Open", "contentUrl": "services/data/v66.0/jobs/ingest/750xx/batches"}
        client = await make_client(mock_post=make_response(200, json_body=body))

        result = await client.ingest.create_job(
            object_name="Account", operation="insert"
        )

        assert result == body
        client._session.post.assert_awaited_once()
        call = client._session.post.await_args
        assert call.args[0] == "ingest"
        assert call.kwargs["json"] == {
            "object": "Account",
            "operation": "insert",
            "columnDelimiter": "COMMA",
            "lineEnding": "LF",
            "contentType": "CSV",
        }
        await client.close()

    async def test_upsert_requires_external_id_field(self):
        client = await make_client(mock_post=make_response(200, json_body={}))
        with pytest.raises(ValueError, match="external_id_field"):
            await client.ingest.create_job(object_name="Account", operation="upsert")
        await client.close()

    async def test_upsert_includes_external_id_field_name(self):
        body = {"id": "750xx", "state": "Open"}
        client = await make_client(mock_post=make_response(200, json_body=body))

        await client.ingest.create_job(
            object_name="Account",
            operation="upsert",
            external_id_field="ExtId__c",
        )

        payload = client._session.post.await_args.kwargs["json"]
        assert payload["externalIdFieldName"] == "ExtId__c"
        await client.close()

    async def test_invalid_operation_raises_before_request(self):
        client = await make_client(mock_post=make_response(200, json_body={}))
        with pytest.raises(ValueError, match="Invalid ingest operation"):
            await client.ingest.create_job(object_name="Account", operation="query")
        client._session.post.assert_not_awaited()
        await client.close()


class TestUploadData:
    async def test_put_csv_uses_content_url_from_job(self):
        client = await make_client(mock_put=make_response(201))

        await client.ingest.upload_data(
            "750xx",
            csv_data=b"Id,Name\n001,Acme\n",
            content_url="services/data/v66.0/jobs/ingest/750xx/batches",
        )

        client._session.put.assert_awaited_once()
        call = client._session.put.await_args
        assert call.args[0] == "services/data/v66.0/jobs/ingest/750xx/batches"
        assert call.kwargs["content"] == b"Id,Name\n001,Acme\n"
        assert call.kwargs["headers"]["Content-Type"] == "text/csv"
        await client.close()

    async def test_put_csv_defaults_to_ingest_batches_path(self):
        client = await make_client(mock_put=make_response(201))

        await client.ingest.upload_data("750xx", csv_data=b"a\n1\n")

        assert client._session.put.await_args.args[0] == "ingest/750xx/batches"
        await client.close()

    async def test_oversized_payload_raises(self):
        client = await make_client(mock_put=make_response(201))

        with pytest.raises(ValueError, match="raw ceiling"):
            await client.ingest.upload_data(
                "750xx", csv_data=b"x" * (MAX_UPLOAD_BYTES_RAW + 1)
            )
        client._session.put.assert_not_awaited()
        await client.close()


class TestUploadComplete:
    async def test_patches_to_upload_complete(self):
        body = {"id": "750xx", "state": "UploadComplete"}
        client = await make_client(mock_patch=make_response(200, json_body=body))

        result = await client.ingest.upload_complete("750xx")

        assert result == body
        call = client._session.patch.await_args
        assert call.args[0] == "ingest/750xx"
        assert call.kwargs["json"] == {"state": "UploadComplete"}
        await client.close()


class TestAbortAndDelete:
    async def test_abort_sends_aborted_state(self):
        client = await make_client(
            mock_patch=make_response(200, json_body={"state": "Aborted"})
        )
        await client.ingest.abort_job("750xx")
        assert client._session.patch.await_args.kwargs["json"] == {"state": "Aborted"}
        await client.close()

    async def test_delete_hits_expected_path(self):
        client = await make_client(mock_delete=make_response(204))
        await client.ingest.delete_job("750xx")
        assert client._session.delete.await_args.args[0] == "ingest/750xx"
        await client.close()


class TestResults:
    async def test_get_successful_results_returns_bytes(self):
        csv = b"sf__Id,Name\n001,Acme\n"
        client = await make_client(mock_get=make_response(200, content=csv))

        result = await client.ingest.get_successful_results("750xx")

        assert result == csv
        assert client._session.get.await_args.args[0] == "ingest/750xx/successfulResults"
        await client.close()

    async def test_get_failed_results_returns_bytes(self):
        csv = b"sf__Error,sf__Id,Name\nReq fld missing,,NoName\n"
        client = await make_client(mock_get=make_response(200, content=csv))

        result = await client.ingest.get_failed_results("750xx")

        assert result == csv
        assert client._session.get.await_args.args[0] == "ingest/750xx/failedResults"
        await client.close()


class TestUpsertConvenience:
    async def test_upsert_chains_create_upload_complete(self):
        """`upsert` issues POST → PUT → PATCH in order."""
        post_body = {
            "id": "750xx",
            "state": "Open",
            "contentUrl": "services/data/v66.0/jobs/ingest/750xx/batches",
        }
        patch_body = {"id": "750xx", "state": "UploadComplete"}
        client = await make_client(
            mock_post=make_response(200, json_body=post_body),
            mock_put=make_response(201),
            mock_patch=make_response(200, json_body=patch_body),
        )

        result = await client.ingest.upsert(
            object_name="Account",
            external_id_field="ExtId__c",
            csv_data=b"ExtId__c,Name\nA1,Acme\n",
        )

        assert result == patch_body
        client._session.post.assert_awaited_once()
        client._session.put.assert_awaited_once()
        client._session.patch.assert_awaited_once()
        # PUT should use the contentUrl returned by POST.
        assert client._session.put.await_args.args[0] == post_body["contentUrl"]
        await client.close()
