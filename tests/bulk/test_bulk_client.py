"""Tests for salesforce_py.bulk.client — BulkClient lifecycle + session."""

from __future__ import annotations

import pytest

from salesforce_py.bulk._session import BulkSession
from salesforce_py.bulk.client import BulkClient
from salesforce_py.bulk.operations import IngestOperations, QueryOperations
from salesforce_py.exceptions import AuthError, SalesforcePyError
from tests.bulk.conftest import ACCESS_TOKEN, INSTANCE_URL, make_response


class TestBulkSession:
    async def test_open_creates_client(self):
        session = BulkSession(INSTANCE_URL, ACCESS_TOKEN)
        await session.open()
        assert session._client is not None
        await session.close()

    async def test_context_manager_opens_and_closes(self):
        session = BulkSession(INSTANCE_URL, ACCESS_TOKEN)
        async with session:
            assert session._client is not None
        assert session._client is None

    async def test_get_raises_when_not_open(self):
        session = BulkSession(INSTANCE_URL, ACCESS_TOKEN)
        with pytest.raises(RuntimeError, match="not open"):
            await session.get("some/path")

    async def test_base_url_is_jobs_scoped(self):
        session = BulkSession(INSTANCE_URL, ACCESS_TOKEN, api_version="66.0")
        await session.open()
        assert str(session._client.base_url) == f"{INSTANCE_URL}/services/data/v66.0/jobs/"
        await session.close()


class TestBulkClientLifecycle:
    async def test_context_manager(self):
        async with BulkClient(INSTANCE_URL, ACCESS_TOKEN) as client:
            assert client._session._client is not None
        assert client._session._client is None

    def test_repr(self):
        client = BulkClient(INSTANCE_URL, ACCESS_TOKEN)
        assert INSTANCE_URL in repr(client)

    def test_namespaces_attached(self):
        client = BulkClient(INSTANCE_URL, ACCESS_TOKEN)
        assert isinstance(client.ingest, IngestOperations)
        assert isinstance(client.query, QueryOperations)

    def test_default_timeout_is_120s(self):
        from salesforce_py._retry import DEFAULT_TIMEOUT

        client = BulkClient(INSTANCE_URL, ACCESS_TOKEN)
        assert client._session._timeout == DEFAULT_TIMEOUT


class TestBulkBaseHandle:
    def setup_method(self):
        from salesforce_py.bulk.base import BulkBaseOperations

        self._handle = BulkBaseOperations._handle
        self._handle_status = BulkBaseOperations._handle_status

    def test_204_returns_empty_dict(self):
        assert self._handle(make_response(204)) == {}

    def test_200_returns_json(self):
        assert self._handle(make_response(200, json_body={"id": "x"})) == {"id": "x"}

    def test_401_raises_auth_error(self):
        with pytest.raises(AuthError):
            self._handle(make_response(401))

    def test_500_raises_salesforce_py_error(self):
        with pytest.raises(SalesforcePyError):
            self._handle(make_response(500, json_body={"message": "server error"}))
