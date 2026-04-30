"""Tests for salesforce_py.rest.operations.composite."""

from __future__ import annotations

from tests.rest.conftest import make_client, make_response


class TestComposite:
    async def test_execute_builds_correct_payload(self):
        body = {"compositeResponse": []}
        client = await make_client(mock_post=make_response(200, json_body=body))

        subs = [
            {"method": "GET", "url": "/services/data/v66.0/limits", "referenceId": "l"},
        ]
        await client.composite.execute(subs, all_or_none=True)

        call = client._session.post.await_args
        assert call.args[0] == "composite"
        assert call.kwargs["json"] == {
            "compositeRequest": subs,
            "allOrNone": True,
            "collateSubrequests": False,
        }
        await client.close()

    async def test_batch_wraps_batch_requests(self):
        body = {"results": []}
        client = await make_client(mock_post=make_response(200, json_body=body))

        requests = [{"method": "GET", "url": "v66.0/limits"}]
        await client.composite.batch(requests, halt_on_error=True)

        call = client._session.post.await_args
        assert call.args[0] == "composite/batch"
        assert call.kwargs["json"] == {
            "batchRequests": requests,
            "haltOnError": True,
        }
        await client.close()

    async def test_graph_wraps_graphs(self):
        body = {"graphs": []}
        client = await make_client(mock_post=make_response(200, json_body=body))

        graphs = [
            {"graphId": "g1", "compositeRequest": []},
        ]
        await client.composite.graph(graphs)

        call = client._session.post.await_args
        assert call.args[0] == "composite/graph"
        assert call.kwargs["json"] == {"graphs": graphs}
        await client.close()

    async def test_tree_includes_object_in_path(self):
        body = {"hasErrors": False, "results": []}
        client = await make_client(mock_post=make_response(201, json_body=body))

        records = [{"attributes": {"type": "Account", "referenceId": "a"}, "Name": "A"}]
        await client.composite.tree("Account", records)

        call = client._session.post.await_args
        assert call.args[0] == "composite/tree/Account"
        assert call.kwargs["json"] == {"records": records}
        await client.close()


class TestSObjectCollections:
    async def test_sobjects_create(self):
        body = [{"id": "001xx", "success": True}]
        client = await make_client(mock_post=make_response(200, json_body=body))

        result = await client.composite.sobjects_create(
            [{"attributes": {"type": "Account"}, "Name": "A"}],
            all_or_none=True,
        )

        assert result == body
        call = client._session.post.await_args
        assert call.args[0] == "composite/sobjects"
        assert call.kwargs["json"]["allOrNone"] is True
        await client.close()

    async def test_sobjects_update_uses_patch(self):
        body = [{"id": "001xx", "success": True}]
        client = await make_client(mock_patch=make_response(200, json_body=body))

        await client.composite.sobjects_update(
            [{"attributes": {"type": "Account"}, "Id": "001xx", "Name": "A2"}],
        )

        assert client._session.patch.await_args.args[0] == "composite/sobjects"
        await client.close()

    async def test_sobjects_upsert_includes_object_and_field(self):
        body = [{"id": "001xx", "success": True}]
        client = await make_client(mock_patch=make_response(200, json_body=body))

        await client.composite.sobjects_upsert(
            "Account",
            "ExtId__c",
            [{"attributes": {"type": "Account"}, "ExtId__c": "E1", "Name": "A"}],
        )

        assert client._session.patch.await_args.args[0] == (
            "composite/sobjects/Account/ExtId__c"
        )
        await client.close()

    async def test_sobjects_delete_passes_comma_joined_ids(self):
        body = [{"id": "001xx", "success": True}]
        client = await make_client(mock_delete=make_response(200, json_body=body))

        await client.composite.sobjects_delete(["001xx", "001yy"], all_or_none=False)

        call = client._session.delete.await_args
        assert call.args[0] == "composite/sobjects"
        assert call.kwargs["params"] == {
            "ids": "001xx,001yy",
            "allOrNone": "false",
        }
        await client.close()

    async def test_sobjects_retrieve_posts_ids_and_fields(self):
        body = [{"Id": "001xx", "Name": "A"}]
        client = await make_client(mock_post=make_response(200, json_body=body))

        await client.composite.sobjects_retrieve(
            "Account", ["001xx", "001yy"], ["Id", "Name"]
        )

        call = client._session.post.await_args
        assert call.args[0] == "composite/sobjects/Account"
        assert call.kwargs["json"] == {
            "ids": ["001xx", "001yy"],
            "fields": ["Id", "Name"],
        }
        await client.close()
