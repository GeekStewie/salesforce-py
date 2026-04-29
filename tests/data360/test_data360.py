"""Tests for salesforce_py.data360."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from salesforce_py.data360._session import Data360Session
from salesforce_py.data360.client import Data360Client
from salesforce_py.exceptions import AuthError, SalesforcePyError

INSTANCE_URL = "https://datacloud-abc.my.salesforce.com"
ACCESS_TOKEN = "test_token_abc"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_response(
    status_code: int, json_body: dict | None = None, content: bytes = b""
) -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.content = content if content else (b"ok" if json_body is not None else b"")
    resp.text = str(json_body) if json_body else ""
    resp.url = f"{INSTANCE_URL}/services/data/v66.0/ssot/test"
    if json_body is not None:
        resp.json.return_value = json_body
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=resp
        )
    else:
        resp.raise_for_status.return_value = None
    return resp


async def _client(mock_get=None, mock_post=None, mock_patch=None, mock_put=None, mock_delete=None):
    c = Data360Client(INSTANCE_URL, ACCESS_TOKEN)
    await c.open()
    if mock_get is not None:
        c._session.get = AsyncMock(return_value=mock_get)
    if mock_post is not None:
        c._session.post = AsyncMock(return_value=mock_post)
    if mock_patch is not None:
        c._session.patch = AsyncMock(return_value=mock_patch)
    if mock_put is not None:
        c._session.put = AsyncMock(return_value=mock_put)
    if mock_delete is not None:
        c._session.delete = AsyncMock(return_value=mock_delete)
    return c


# ---------------------------------------------------------------------------
# Data360Session
# ---------------------------------------------------------------------------


class TestData360Session:
    async def test_open_creates_client(self):
        session = Data360Session(INSTANCE_URL, ACCESS_TOKEN)
        await session.open()
        assert session._client is not None
        await session.close()

    async def test_context_manager_opens_and_closes(self):
        session = Data360Session(INSTANCE_URL, ACCESS_TOKEN)
        async with session:
            assert session._client is not None
        assert session._client is None

    async def test_get_raises_when_not_open(self):
        session = Data360Session(INSTANCE_URL, ACCESS_TOKEN)
        with pytest.raises(RuntimeError, match="not open"):
            await session.get("some/path")

    async def test_put_raises_when_not_open(self):
        session = Data360Session(INSTANCE_URL, ACCESS_TOKEN)
        with pytest.raises(RuntimeError, match="not open"):
            await session.put("some/path")

    async def test_base_url_is_ssot_scoped(self):
        session = Data360Session(INSTANCE_URL, ACCESS_TOKEN, api_version="66.0")
        await session.open()
        assert str(session._client.base_url) == f"{INSTANCE_URL}/services/data/v66.0/ssot/"
        await session.close()


# ---------------------------------------------------------------------------
# Data360BaseOperations — response handling
# ---------------------------------------------------------------------------


class TestData360BaseHandle:
    def setup_method(self):
        from salesforce_py.data360.base import Data360BaseOperations

        self._handle = Data360BaseOperations._handle
        self._handle_status = Data360BaseOperations._handle_status

    def test_204_returns_empty_dict(self):
        resp = _mock_response(204)
        assert self._handle(resp) == {}

    def test_200_returns_json(self):
        resp = _mock_response(200, {"id": "abc"})
        assert self._handle(resp) == {"id": "abc"}

    def test_401_raises_auth_error(self):
        resp = _mock_response(401)
        with pytest.raises(AuthError):
            self._handle(resp)

    def test_500_raises_salesforce_py_error(self):
        resp = _mock_response(500, {"message": "server error"})
        with pytest.raises(SalesforcePyError):
            self._handle(resp)

    def test_empty_body_returns_empty_dict(self):
        resp = _mock_response(200)
        resp.content = b""
        assert self._handle(resp) == {}


# ---------------------------------------------------------------------------
# Data360Client — lifecycle
# ---------------------------------------------------------------------------


class TestData360ClientLifecycle:
    async def test_context_manager(self):
        async with Data360Client(INSTANCE_URL, ACCESS_TOKEN) as client:
            assert client._session._client is not None
        assert client._session._client is None

    def test_repr(self):
        client = Data360Client(INSTANCE_URL, ACCESS_TOKEN)
        assert INSTANCE_URL in repr(client)

    def test_operation_namespaces_attached(self):
        client = Data360Client(INSTANCE_URL, ACCESS_TOKEN)
        from salesforce_py.data360.operations import (
            ActivationTargetsOperations,
            DataCleanRoomOperations,
            QueryOperations,
            SegmentsOperations,
            UniversalIdLookupOperations,
        )

        assert isinstance(client.activation_targets, ActivationTargetsOperations)
        assert isinstance(client.data_clean_room, DataCleanRoomOperations)
        assert isinstance(client.query, QueryOperations)
        assert isinstance(client.segments, SegmentsOperations)
        assert isinstance(client.universal_id_lookup, UniversalIdLookupOperations)


# ---------------------------------------------------------------------------
# Activation Targets
# ---------------------------------------------------------------------------


class TestActivationTargets:
    async def test_list_drops_none_params(self):
        c = await _client(mock_get=_mock_response(200, {"totalCount": 0, "items": []}))
        await c.activation_targets.get_activation_targets(batch_size=50, offset=0)
        c._session.get.assert_awaited_once_with(
            "activation-targets",
            params={"batchSize": 50, "offset": 0},
            headers=None,
        )
        await c.close()

    async def test_get_by_id(self):
        c = await _client(mock_get=_mock_response(200, {"id": "TGT_1"}))
        result = await c.activation_targets.get_activation_target("TGT_1")
        assert result == {"id": "TGT_1"}
        c._session.get.assert_awaited_once_with(
            "activation-targets/TGT_1", params=None, headers=None
        )
        await c.close()

    async def test_update_patches_with_json(self):
        c = await _client(mock_patch=_mock_response(200, {"id": "TGT_1"}))
        await c.activation_targets.update_activation_target("TGT_1", {"label": "Updated"})
        c._session.patch.assert_awaited_once_with(
            "activation-targets/TGT_1",
            params=None,
            headers=None,
            json={"label": "Updated"},
        )
        await c.close()


# ---------------------------------------------------------------------------
# Activations
# ---------------------------------------------------------------------------


class TestActivations:
    async def test_get_activation_data_sets_required_header(self):
        c = await _client(mock_get=_mock_response(200, {"data": []}))
        await c.activations.get_activation_data("act_1", batch_size=100)
        c._session.get.assert_awaited_once_with(
            "activations/act_1/data",
            params={"batchSize": 100},
            headers={"X-Chatter-Entity-Encoding": "false"},
        )
        await c.close()

    async def test_publish_posts_empty_body_by_default(self):
        c = await _client(mock_post=_mock_response(202, {"jobId": "J1"}))
        await c.activations.publish_activation("act_1")
        c._session.post.assert_awaited_once_with(
            "activations/act_1/actions/publish",
            params=None,
            headers=None,
            json={},
        )
        await c.close()

    async def test_get_external_platforms(self):
        c = await _client(mock_get=_mock_response(200, {"externalPlatforms": []}))
        await c.activations.get_activation_external_platforms(limit=10)
        c._session.get.assert_awaited_once_with(
            "activation-external-platforms",
            params={"limit": 10},
            headers=None,
        )
        await c.close()


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------


class TestQuery:
    async def test_submit_sql_query_posts_to_query_sql(self):
        c = await _client(mock_post=_mock_response(200, {"queryId": "Q1"}))
        await c.query.submit_sql_query({"sql": "SELECT 1"}, dataspace="default")
        c._session.post.assert_awaited_once_with(
            "query-sql",
            params={"dataspace": "default"},
            headers=None,
            json={"sql": "SELECT 1"},
        )
        await c.close()

    async def test_get_sql_query_rows_requires_dataspace_and_offset(self):
        c = await _client(mock_get=_mock_response(200, {"rows": [[1]]}))
        await c.query.get_sql_query_rows("Q1", dataspace="default", offset=0, row_limit=500)
        c._session.get.assert_awaited_once_with(
            "query-sql/Q1/rows",
            params={"dataspace": "default", "offset": 0, "rowLimit": 500},
            headers=None,
        )
        await c.close()

    async def test_cancel_sql_query_sends_delete(self):
        c = await _client(mock_delete=_mock_response(204))
        await c.query.cancel_sql_query("Q1", dataspace="default")
        c._session.delete.assert_awaited_once_with(
            "query-sql/Q1",
            params={"dataspace": "default"},
            headers=None,
        )
        await c.close()

    async def test_query_v2_post(self):
        c = await _client(mock_post=_mock_response(200, {"data": []}))
        await c.query.query_v2({"query": "..."}, dataspace="ds1")
        c._session.post.assert_awaited_once_with(
            "queryv2",
            params={"dataspace": "ds1"},
            headers=None,
            json={"query": "..."},
        )
        await c.close()


# ---------------------------------------------------------------------------
# Segments
# ---------------------------------------------------------------------------


class TestSegments:
    async def test_create_segment_with_dataspace(self):
        c = await _client(mock_post=_mock_response(201, {"id": "S1"}))
        await c.segments.create_segment({"name": "S1"}, dataspace="default")
        c._session.post.assert_awaited_once_with(
            "segments",
            params={"dataspace": "default"},
            headers=None,
            json={"name": "S1"},
        )
        await c.close()

    async def test_publish_segment_by_id(self):
        c = await _client(mock_post=_mock_response(200, {"jobId": "P1"}))
        await c.segments.publish_segment("s_id")
        c._session.post.assert_awaited_once_with(
            "segments/s_id/actions/publish", params=None, headers=None
        )
        await c.close()

    async def test_get_segment_members_drops_none_params(self):
        c = await _client(mock_get=_mock_response(200, {"members": []}))
        await c.segments.get_segment_members("seg_1", limit=100)
        c._session.get.assert_awaited_once_with(
            "segments/seg_1/members",
            params={"limit": 100},
            headers=None,
        )
        await c.close()


# ---------------------------------------------------------------------------
# Universal ID lookup
# ---------------------------------------------------------------------------


class TestUniversalIdLookup:
    async def test_lookup_path(self):
        c = await _client(mock_get=_mock_response(200, {"unifiedId": "U_1"}))
        await c.universal_id_lookup.lookup_universal_id(
            entity_name="UnifiedIndividual__dlm",
            data_source_id="ds_sf",
            data_source_object_id="Contact",
            source_record_id="003abc",
        )
        c._session.get.assert_awaited_once_with(
            "universalIdLookup/UnifiedIndividual__dlm/ds_sf/Contact/003abc",
            params=None,
            headers=None,
        )
        await c.close()


# ---------------------------------------------------------------------------
# Data Graphs
# ---------------------------------------------------------------------------


class TestDataGraphs:
    async def test_refresh_posts_to_actions_refresh(self):
        c = await _client(mock_post=_mock_response(200, {"status": "queued"}))
        await c.data_graphs.refresh_data_graph("my_graph")
        c._session.post.assert_awaited_once_with(
            "data-graphs/my_graph/actions/refresh", params=None, headers=None
        )
        await c.close()

    async def test_get_data_by_entity_passes_lookup_keys(self):
        c = await _client(mock_get=_mock_response(200, {"data": {}}))
        await c.data_graphs.get_data_graph_data_by_entity(
            "MyEntity", lookup_keys="k1,k2", no_cache=True
        )
        c._session.get.assert_awaited_once_with(
            "data-graphs/data/MyEntity",
            params={"lookupKeys": "k1,k2", "noCache": True},
            headers=None,
        )
        await c.close()


# ---------------------------------------------------------------------------
# Connections (covers the crowded actions/schema/sitemap surface)
# ---------------------------------------------------------------------------


class TestConnections:
    async def test_get_connections_requires_connector_type(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.connections.get_connections("S3", limit=5)
        c._session.get.assert_awaited_once_with(
            "connections",
            params={"connectorType": "S3", "limit": 5},
            headers=None,
        )
        await c.close()

    async def test_run_existing_connection_action(self):
        c = await _client(mock_post=_mock_response(200, {"result": "ok"}))
        await c.connections.run_existing_connection_action("conn_1", "refresh", {"foo": "bar"})
        c._session.post.assert_awaited_once_with(
            "connections/conn_1/actions/refresh",
            params=None,
            headers=None,
            json={"foo": "bar"},
        )
        await c.close()

    async def test_upsert_schema_uses_put(self):
        c = await _client(mock_put=_mock_response(200, {}))
        await c.connections.upsert_connection_schema("conn_1", {"fields": []})
        c._session.put.assert_awaited_once_with(
            "connections/conn_1/schema",
            params=None,
            headers=None,
            json={"fields": []},
        )
        await c.close()


# ---------------------------------------------------------------------------
# Error handling end-to-end via a namespace call
# ---------------------------------------------------------------------------


class TestErrorPropagation:
    async def test_401_raises_auth_error(self):
        c = await _client(mock_get=_mock_response(401))
        with pytest.raises(AuthError):
            await c.segments.get_segments()
        await c.close()

    async def test_500_raises_salesforce_py_error(self):
        c = await _client(mock_get=_mock_response(500, {"error": "boom"}))
        with pytest.raises(SalesforcePyError):
            await c.segments.get_segments()
        await c.close()
