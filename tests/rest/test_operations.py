"""Tests for the smaller REST operation namespaces."""

from __future__ import annotations

from unittest.mock import AsyncMock

from tests.rest.conftest import make_client, make_response


class TestLimits:
    async def test_get_limits(self):
        client = await make_client(mock_get=make_response(200, json_body={}))
        await client.limits.get_limits()
        assert client._session.get.await_args.args[0] == "limits"
        await client.close()

    async def test_get_record_count_passes_comma_joined_list(self):
        client = await make_client(mock_get=make_response(200, json_body={"sObjects": []}))
        await client.limits.get_record_count(sobjects=["Account", "Contact"])
        call = client._session.get.await_args
        assert call.args[0] == "limits/recordCount"
        assert call.kwargs["params"] == {"sObjects": "Account,Contact"}
        await client.close()


class TestSearch:
    async def test_sosl_search(self):
        body = {"searchRecords": []}
        client = await make_client(mock_get=make_response(200, json_body=body))

        await client.search.search("FIND {Acme} IN NAME FIELDS RETURNING Account(Id, Name)")

        call = client._session.get.await_args
        assert call.args[0] == "search"
        assert call.kwargs["params"] == {
            "q": "FIND {Acme} IN NAME FIELDS RETURNING Account(Id, Name)"
        }
        await client.close()

    async def test_parameterized_search_kwargs_become_params(self):
        body = {"searchRecords": []}
        client = await make_client(mock_get=make_response(200, json_body=body))

        await client.search.parameterized_search(q="Acme", sobject="Account", fields="Id,Name")

        call = client._session.get.await_args
        assert call.args[0] == "parameterizedSearch"
        assert call.kwargs["params"] == {
            "q": "Acme",
            "sobject": "Account",
            "fields": "Id,Name",
        }
        await client.close()

    async def test_parameterized_search_post(self):
        body = {"searchRecords": []}
        client = await make_client(mock_post=make_response(200, json_body=body))

        await client.search.parameterized_search_post({"q": "Acme", "sobjects": []})

        call = client._session.post.await_args
        assert call.args[0] == "parameterizedSearch"
        assert call.kwargs["json"] == {"q": "Acme", "sobjects": []}
        await client.close()

    async def test_get_search_layouts_joins_objects(self):
        client = await make_client(mock_get=make_response(200, json_body={}))

        await client.search.get_search_layouts(["Account", "Contact"])

        call = client._session.get.await_args
        assert call.args[0] == "searchlayout"
        assert call.kwargs["params"] == {"q": "Account,Contact"}
        await client.close()


class TestActions:
    async def test_invoke_standard_action(self):
        body = [{"isSuccess": True}]
        client = await make_client(mock_post=make_response(200, json_body=body))

        await client.actions.invoke_standard_action(
            "emailSimple",
            [{"emailAddresses": "ops@acme.com", "emailSubject": "x", "emailBody": "y"}],
        )

        call = client._session.post.await_args
        assert call.args[0] == "actions/standard/emailSimple"
        assert "inputs" in call.kwargs["json"]
        await client.close()

    async def test_describe_custom_action_includes_type_and_name(self):
        client = await make_client(mock_get=make_response(200, json_body={}))

        await client.actions.describe_custom_action("apex", "MyApexAction")

        assert client._session.get.await_args.args[0] == "actions/custom/apex/MyApexAction"
        await client.close()


class TestQuickActions:
    async def test_list(self):
        client = await make_client(mock_get=make_response(200, json_body=[]))
        await client.quick_actions.list_actions()
        assert client._session.get.await_args.args[0] == "quickActions"
        await client.close()

    async def test_invoke_with_context(self):
        client = await make_client(mock_post=make_response(200, json_body={"success": True}))
        await client.quick_actions.invoke_action("MyAction", context_id="001xx")
        call = client._session.post.await_args
        assert call.args[0] == "quickActions/MyAction"
        assert call.kwargs["json"] == {"contextId": "001xx"}
        await client.close()


class TestTooling:
    async def test_execute_anonymous_passes_body_as_param(self):
        client = await make_client(
            mock_get=make_response(200, json_body={"success": True})
        )

        await client.tooling.execute_anonymous("System.debug('x');")

        call = client._session.get.await_args
        assert call.args[0] == "tooling/executeAnonymous"
        assert call.kwargs["params"] == {"anonymousBody": "System.debug('x');"}
        await client.close()

    async def test_query_uses_tooling_query_path(self):
        client = await make_client(mock_get=make_response(200, json_body={"records": []}))
        await client.tooling.query("SELECT Id FROM ApexClass")
        call = client._session.get.await_args
        assert call.args[0] == "tooling/query"
        assert call.kwargs["params"] == {"q": "SELECT Id FROM ApexClass"}
        await client.close()

    async def test_passthrough_get_prepends_tooling(self):
        client = await make_client(mock_get=make_response(200, json_body={}))
        await client.tooling.get("sobjects/ApexClass")
        assert client._session.get.await_args.args[0] == "tooling/sobjects/ApexClass"
        await client.close()


class TestUIAPI:
    async def test_get_record_joins_fields(self):
        client = await make_client(mock_get=make_response(200, json_body={}))
        await client.ui_api.get_record("001xx", fields=["Id", "Name"])
        call = client._session.get.await_args
        assert call.args[0] == "ui-api/records/001xx"
        assert call.kwargs["params"] == {"fields": "Id,Name"}
        await client.close()

    async def test_get_record_ui_joins_record_ids(self):
        client = await make_client(mock_get=make_response(200, json_body={}))
        await client.ui_api.get_record_ui(
            ["001xx", "001yy"], layout_types=["Full"], modes=["View"]
        )
        call = client._session.get.await_args
        assert call.args[0] == "ui-api/record-ui/001xx,001yy"
        assert call.kwargs["params"] == {
            "layoutTypes": "Full",
            "modes": "View",
        }
        await client.close()

    async def test_get_object_info(self):
        client = await make_client(mock_get=make_response(200, json_body={}))
        await client.ui_api.get_object_info("Account")
        assert client._session.get.await_args.args[0] == "ui-api/object-info/Account"
        await client.close()


class TestTabsThemeRecent:
    async def test_tabs(self):
        client = await make_client(mock_get=make_response(200, json_body=[]))
        await client.tabs.list_tabs()
        assert client._session.get.await_args.args[0] == "tabs"
        await client.close()

    async def test_theme(self):
        client = await make_client(mock_get=make_response(200, json_body={"themeItems": []}))
        await client.theme.get_theme()
        assert client._session.get.await_args.args[0] == "theme"
        await client.close()

    async def test_recent_with_limit(self):
        client = await make_client(mock_get=make_response(200, json_body=[]))
        await client.recent.get_recent_items(limit=5)
        call = client._session.get.await_args
        assert call.args[0] == "recent"
        assert call.kwargs["params"] == {"limit": 5}
        await client.close()


class TestPassthroughNamespaces:
    async def test_consent_get_with_subpath(self):
        client = await make_client(mock_get=make_response(200, json_body={}))
        await client.consent.get("action/email/005xx")
        assert client._session.get.await_args.args[0] == "consent/action/email/005xx"
        await client.close()

    async def test_consent_get_without_subpath(self):
        client = await make_client(mock_get=make_response(200, json_body={}))
        await client.consent.get()
        assert client._session.get.await_args.args[0] == "consent"
        await client.close()

    async def test_financial_services_uses_connect_prefix(self):
        client = await make_client(mock_get=make_response(200, json_body={}))
        await client.financial_services.get("lifeevents")
        assert client._session.get.await_args.args[0] == "connect/financialservices/lifeevents"
        await client.close()

    async def test_health_cloud_uses_connect_prefix(self):
        client = await make_client(mock_post=make_response(200, json_body={}))
        await client.health_cloud.post("reciprocal-role-relationships", json={"foo": "bar"})
        assert client._session.post.await_args.args[0] == (
            "connect/health/care-services/reciprocal-role-relationships"
        )
        await client.close()

    async def test_subpath_leading_slash_is_stripped(self):
        client = await make_client(mock_get=make_response(200, json_body={}))
        await client.chatter.get("/feeds")
        assert client._session.get.await_args.args[0] == "chatter/feeds"
        await client.close()


class TestStreaming:
    async def test_get_subscribers(self):
        client = await make_client(mock_get=make_response(200, json_body={}))
        await client.streaming.get_subscribers("0M8xx0000000001")
        assert client._session.get.await_args.args[0] == (
            "sobjects/StreamingChannel/0M8xx0000000001/push"
        )
        await client.close()

    async def test_push_notification(self):
        client = await make_client(mock_post=make_response(200, json_body={}))
        await client.streaming.push_notification(
            "0M8xx0000000001", {"pushEvents": [{"payload": "hi"}]}
        )
        call = client._session.post.await_args
        assert call.args[0] == "sobjects/StreamingChannel/0M8xx0000000001/push"
        assert call.kwargs["json"] == {"pushEvents": [{"payload": "hi"}]}
        await client.close()


class TestLightningUsage:
    async def test_usage_by_app_type(self):
        client = await make_client(mock_get=make_response(200, json_body={}))
        await client.lightning_usage.usage_by_app_type()
        assert client._session.get.await_args.args[0] == (
            "sobjects/LightningUsageByAppTypeMetrics"
        )
        await client.close()


class TestVersions:
    async def test_list_resources_hits_root(self):
        client = await make_client(mock_get=make_response(200, json_body={"sobjects": "..."}))
        await client.versions.list_resources()
        # Version base URL root — empty path
        assert client._session.get.await_args.args[0] == ""
        await client.close()

    async def test_list_versions_uses_absolute_url(self):
        from tests.rest.conftest import INSTANCE_URL

        client = await make_client()
        # Patch the underlying httpx client for this non-version-scoped call
        client._session._client.get = AsyncMock(
            return_value=make_response(
                200,
                json_body=[
                    {"version": "66.0", "label": "Spring '26", "url": "/services/data/v66.0"}
                ],
            )
        )

        versions = await client.versions.list_versions()

        assert versions[0]["version"] == "66.0"
        client._session._client.get.assert_awaited_once_with(
            f"{INSTANCE_URL}/services/data"
        )
        await client.close()
