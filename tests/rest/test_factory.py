"""Tests for :meth:`RestClient.from_env` and :meth:`RestClient.from_org`."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from salesforce_py.exceptions import SalesforcePyError
from salesforce_py.rest.client import RestClient
from tests.rest.conftest import ACCESS_TOKEN, INSTANCE_URL


class TestFromEnv:
    async def test_from_env_uses_client_creds(self, monkeypatch):
        monkeypatch.setenv("SF_REST_CLIENT_ID", "rid")
        monkeypatch.setenv("SF_REST_CLIENT_SECRET", "rsecret")
        monkeypatch.setenv("SF_REST_INSTANCE_URL", INSTANCE_URL)

        with patch(
            "salesforce_py.rest.client.fetch_org_token",
            new=AsyncMock(return_value=("tok", INSTANCE_URL)),
        ):
            client = await RestClient.from_env()

        assert client._session._access_token == "tok"
        assert client._session._instance_url == INSTANCE_URL
        await client.close()

    async def test_from_env_uses_sf_instance_url_fallback(self, monkeypatch):
        monkeypatch.setenv("SF_REST_CLIENT_ID", "rid")
        monkeypatch.setenv("SF_REST_CLIENT_SECRET", "rsecret")
        monkeypatch.delenv("SF_REST_INSTANCE_URL", raising=False)
        monkeypatch.setenv("SF_INSTANCE_URL", INSTANCE_URL)

        with patch(
            "salesforce_py.rest.client.fetch_org_token",
            new=AsyncMock(return_value=("tok", INSTANCE_URL)),
        ):
            client = await RestClient.from_env()

        assert client._session._access_token == "tok"
        await client.close()

    async def test_from_env_falls_back_to_sf_cli(self, monkeypatch):
        monkeypatch.delenv("SF_REST_CLIENT_ID", raising=False)
        monkeypatch.delenv("SF_REST_CLIENT_SECRET", raising=False)

        mock_org = MagicMock()
        mock_org.instance_url = INSTANCE_URL
        mock_org.access_token = ACCESS_TOKEN

        with patch("salesforce_py.sf.org.SFOrg", return_value=mock_org):
            client = await RestClient.from_env(target_org="my-alias")

        assert client._session._access_token == ACCESS_TOKEN
        await client.close()

    async def test_from_env_raises_without_creds_or_org(self, monkeypatch):
        monkeypatch.delenv("SF_REST_CLIENT_ID", raising=False)
        monkeypatch.delenv("SF_REST_CLIENT_SECRET", raising=False)

        with pytest.raises(SalesforcePyError, match="SF_REST_CLIENT_ID"):
            await RestClient.from_env()

    async def test_from_env_raises_missing_instance_url(self, monkeypatch):
        monkeypatch.setenv("SF_REST_CLIENT_ID", "rid")
        monkeypatch.setenv("SF_REST_CLIENT_SECRET", "rsecret")
        monkeypatch.delenv("SF_REST_INSTANCE_URL", raising=False)
        monkeypatch.delenv("SF_INSTANCE_URL", raising=False)

        with pytest.raises(SalesforcePyError, match="instance URL"):
            await RestClient.from_env()


class TestFromOrg:
    def test_from_org_uses_org_credentials(self):
        mock_org = MagicMock()
        mock_org.instance_url = INSTANCE_URL
        mock_org.access_token = ACCESS_TOKEN

        client = RestClient.from_org(mock_org)

        assert client._session._instance_url == INSTANCE_URL
        assert client._session._access_token == ACCESS_TOKEN

    def test_from_org_triggers_lazy_connect(self):
        mock_org = MagicMock()
        mock_org.instance_url = INSTANCE_URL
        mock_org.access_token = ACCESS_TOKEN

        RestClient.from_org(mock_org)

        mock_org._ensure_connected.assert_called_once()
