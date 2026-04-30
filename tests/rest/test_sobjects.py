"""Tests for salesforce_py.rest.operations.sobjects."""

from __future__ import annotations

from tests.rest.conftest import make_client, make_response


class TestDescribe:
    async def test_describe_global(self):
        client = await make_client(mock_get=make_response(200, json_body={"sobjects": []}))
        await client.sobjects.describe_global()
        assert client._session.get.await_args.args[0] == "sobjects"
        await client.close()

    async def test_describe_object(self):
        client = await make_client(mock_get=make_response(200, json_body={"name": "Account"}))
        await client.sobjects.describe_object("Account")
        assert client._session.get.await_args.args[0] == "sobjects/Account/describe"
        await client.close()

    async def test_describe_object_basic(self):
        client = await make_client(mock_get=make_response(200, json_body={"name": "Account"}))
        await client.sobjects.describe_object_basic("Account")
        assert client._session.get.await_args.args[0] == "sobjects/Account"
        await client.close()

    async def test_describe_layouts_with_record_type(self):
        client = await make_client(mock_get=make_response(200, json_body={}))
        await client.sobjects.describe_layouts("Account", record_type_id="012xx000000ABCD")
        assert client._session.get.await_args.args[0] == (
            "sobjects/Account/describe/layouts/012xx000000ABCD"
        )
        await client.close()

    async def test_compact_layouts_batch_joins_object_list(self):
        client = await make_client(mock_get=make_response(200, json_body={}))
        await client.sobjects.compact_layouts(["Account", "Contact", "Opportunity"])
        call = client._session.get.await_args
        assert call.args[0] == "compactLayouts"
        assert call.kwargs["params"] == {"q": "Account,Contact,Opportunity"}
        await client.close()


class TestRecordCRUD:
    async def test_create_posts_to_sobject_path(self):
        body = {"id": "001xx000003DGbZAAW", "success": True}
        client = await make_client(mock_post=make_response(201, json_body=body))

        result = await client.sobjects.create("Account", {"Name": "Acme"})

        assert result == body
        call = client._session.post.await_args
        assert call.args[0] == "sobjects/Account"
        assert call.kwargs["json"] == {"Name": "Acme"}
        await client.close()

    async def test_get_with_fields_passes_comma_joined_list(self):
        body = {"Id": "001xx", "Name": "Acme"}
        client = await make_client(mock_get=make_response(200, json_body=body))

        await client.sobjects.get("Account", "001xx", fields=["Id", "Name"])

        call = client._session.get.await_args
        assert call.args[0] == "sobjects/Account/001xx"
        assert call.kwargs["params"] == {"fields": "Id,Name"}
        await client.close()

    async def test_get_without_fields_omits_params(self):
        body = {"Id": "001xx"}
        client = await make_client(mock_get=make_response(200, json_body=body))

        await client.sobjects.get("Account", "001xx")

        call = client._session.get.await_args
        assert call.kwargs["params"] is None
        await client.close()

    async def test_update_uses_patch(self):
        client = await make_client(mock_patch=make_response(204))

        await client.sobjects.update("Account", "001xx", {"Description": "New"})

        call = client._session.patch.await_args
        assert call.args[0] == "sobjects/Account/001xx"
        assert call.kwargs["json"] == {"Description": "New"}
        await client.close()

    async def test_delete_uses_delete(self):
        client = await make_client(mock_delete=make_response(204))
        await client.sobjects.delete("Account", "001xx")
        assert client._session.delete.await_args.args[0] == "sobjects/Account/001xx"
        await client.close()


class TestUpsert:
    async def test_upsert_patches_external_id_path(self):
        body = {"id": "001xx", "success": True, "created": True}
        client = await make_client(mock_patch=make_response(201, json_body=body))

        result = await client.sobjects.upsert(
            "Account", "ExtId__c", "EXT-1", {"Name": "Acme"}
        )

        assert result == body
        call = client._session.patch.await_args
        assert call.args[0] == "sobjects/Account/ExtId__c/EXT-1"
        assert call.kwargs["json"] == {"Name": "Acme"}
        await client.close()

    async def test_get_by_external_id_passes_fields(self):
        body = {"Id": "001xx", "Name": "Acme"}
        client = await make_client(mock_get=make_response(200, json_body=body))

        await client.sobjects.get_by_external_id(
            "Account", "ExtId__c", "EXT-1", fields=["Id", "Name"]
        )

        call = client._session.get.await_args
        assert call.args[0] == "sobjects/Account/ExtId__c/EXT-1"
        assert call.kwargs["params"] == {"fields": "Id,Name"}
        await client.close()


class TestChangeFeeds:
    async def test_get_deleted_passes_start_end(self):
        body = {"deletedRecords": [], "earliestDateAvailable": "2025-01-01T00:00:00Z"}
        client = await make_client(mock_get=make_response(200, json_body=body))

        await client.sobjects.get_deleted(
            "Account",
            start="2026-01-01T00:00:00Z",
            end="2026-02-01T00:00:00Z",
        )

        call = client._session.get.await_args
        assert call.args[0] == "sobjects/Account/deleted"
        assert call.kwargs["params"] == {
            "start": "2026-01-01T00:00:00Z",
            "end": "2026-02-01T00:00:00Z",
        }
        await client.close()


class TestListViews:
    async def test_list_views_without_id(self):
        client = await make_client(mock_get=make_response(200, json_body={"listviews": []}))
        await client.sobjects.list_views("Account")
        assert client._session.get.await_args.args[0] == "sobjects/Account/listviews"
        await client.close()

    async def test_list_views_with_id(self):
        client = await make_client(mock_get=make_response(200, json_body={}))
        await client.sobjects.list_views("Account", list_view_id="00BXX0000000001")
        assert client._session.get.await_args.args[0] == (
            "sobjects/Account/listviews/00BXX0000000001"
        )
        await client.close()

    async def test_list_view_results_drops_none_params(self):
        client = await make_client(mock_get=make_response(200, json_body={"records": []}))

        await client.sobjects.list_view_results("Account", "00BXX0000000001", limit=25)

        call = client._session.get.await_args
        # _drop_none removes offset=None / q=None before dispatch
        assert call.kwargs["params"] == {"limit": 25}
        await client.close()


class TestQuickActionsOnSObject:
    async def test_sobject_quick_actions_list(self):
        client = await make_client(mock_get=make_response(200, json_body=[]))
        await client.sobjects.sobject_quick_actions("Account")
        assert client._session.get.await_args.args[0] == "sobjects/Account/quickActions"
        await client.close()

    async def test_sobject_quick_actions_describe(self):
        client = await make_client(mock_get=make_response(200, json_body={}))
        await client.sobjects.sobject_quick_actions(
            "Account", action_name="LogACall", describe=True
        )
        assert client._session.get.await_args.args[0] == (
            "sobjects/Account/quickActions/LogACall/describe"
        )
        await client.close()

    async def test_invoke_sobject_quick_action_with_context(self):
        body = {"success": True}
        client = await make_client(mock_post=make_response(200, json_body=body))

        await client.sobjects.invoke_sobject_quick_action(
            "Account", "LogACall", context_id="001xx", record={"Subject": "Follow-up"}
        )

        call = client._session.post.await_args
        assert call.args[0] == "sobjects/Account/quickActions/LogACall"
        assert call.kwargs["json"] == {
            "contextId": "001xx",
            "record": {"Subject": "Follow-up"},
        }
        await client.close()


class TestBlob:
    async def test_get_blob_returns_bytes(self):
        client = await make_client(
            mock_get=make_response(200, content=b"\x89PNG\r\n")
        )

        result = await client.sobjects.get_blob("Attachment", "00Pxx", "Body")

        assert isinstance(result, bytes)
        assert result == b"\x89PNG\r\n"
        assert client._session.get.await_args.args[0] == "sobjects/Attachment/00Pxx/Body"
        await client.close()


class TestUserPassword:
    async def test_get_user_password_status(self):
        client = await make_client(mock_get=make_response(200, json_body={"isExpired": False}))
        await client.sobjects.get_user_password_status("005xx")
        assert client._session.get.await_args.args[0] == "sobjects/User/005xx/password"
        await client.close()

    async def test_set_user_password_posts_new_password(self):
        client = await make_client(mock_post=make_response(204))
        await client.sobjects.set_user_password("005xx", "N3wP@ssword!")
        call = client._session.post.await_args
        assert call.args[0] == "sobjects/User/005xx/password"
        assert call.kwargs["json"] == {"NewPassword": "N3wP@ssword!"}
        await client.close()

    async def test_reset_user_password_uses_delete(self):
        client = await make_client(mock_delete=make_response(200, json_body={"NewPassword": "x"}))
        await client.sobjects.reset_user_password("005xx")
        assert client._session.delete.await_args.args[0] == "sobjects/User/005xx/password"
        await client.close()
