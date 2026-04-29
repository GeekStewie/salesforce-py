"""Tests for salesforce_py.models."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from salesforce_py.exceptions import AuthError, SalesforcePyError
from salesforce_py.models._session import ModelsSession
from salesforce_py.models.client import ModelsClient
from salesforce_py.models.supported_models import (
    GPT_4_OMNI_MINI,
    OPENAI_ADA_002,
    SUPPORTED_MODELS,
)
from salesforce_py.models.token import TokenResponse, fetch_token

ACCESS_TOKEN = "test_token_abc"
MY_DOMAIN = "https://mycompany.my.salesforce.com"
CONSUMER_KEY = "consumer_key_xyz"
CONSUMER_SECRET = "consumer_secret_xyz"


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
    resp.url = "https://api.salesforce.com/einstein/platform/v1/test"
    if json_body is not None:
        resp.json.return_value = json_body
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=resp
        )
    else:
        resp.raise_for_status.return_value = None
    return resp


async def _client(mock_get=None, mock_post=None):
    c = ModelsClient(ACCESS_TOKEN)
    await c.open()
    if mock_get is not None:
        c._session.get = AsyncMock(return_value=mock_get)
    if mock_post is not None:
        c._session.post = AsyncMock(return_value=mock_post)
    return c


# ---------------------------------------------------------------------------
# ModelsSession
# ---------------------------------------------------------------------------


class TestModelsSession:
    async def test_open_creates_client(self):
        session = ModelsSession(ACCESS_TOKEN)
        await session.open()
        assert session._client is not None
        await session.close()

    async def test_context_manager_opens_and_closes(self):
        session = ModelsSession(ACCESS_TOKEN)
        async with session:
            assert session._client is not None
        assert session._client is None

    async def test_get_raises_when_not_open(self):
        session = ModelsSession(ACCESS_TOKEN)
        with pytest.raises(RuntimeError, match="not open"):
            await session.get("some/path")

    async def test_post_raises_when_not_open(self):
        session = ModelsSession(ACCESS_TOKEN)
        with pytest.raises(RuntimeError, match="not open"):
            await session.post("some/path")

    async def test_default_base_url(self):
        session = ModelsSession(ACCESS_TOKEN)
        await session.open()
        assert str(session._client.base_url) == "https://api.salesforce.com/einstein/platform/v1/"
        await session.close()

    async def test_custom_base_url_normalised(self):
        session = ModelsSession(
            ACCESS_TOKEN, base_url="https://api.example.com/einstein/platform/v1"
        )
        await session.open()
        assert str(session._client.base_url) == "https://api.example.com/einstein/platform/v1/"
        await session.close()

    async def test_required_headers_present(self):
        session = ModelsSession(ACCESS_TOKEN)
        await session.open()
        headers = session._client.headers
        assert headers["authorization"] == f"Bearer {ACCESS_TOKEN}"
        assert headers["x-sfdc-app-context"] == "EinsteinGPT"
        assert headers["x-client-feature-id"] == "ai-platform-models-connected-app"
        await session.close()

    async def test_header_overrides(self):
        session = ModelsSession(
            ACCESS_TOKEN, app_context="CustomApp", client_feature_id="custom-feature"
        )
        await session.open()
        headers = session._client.headers
        assert headers["x-sfdc-app-context"] == "CustomApp"
        assert headers["x-client-feature-id"] == "custom-feature"
        await session.close()


# ---------------------------------------------------------------------------
# ModelsBaseOperations — response handling
# ---------------------------------------------------------------------------


class TestModelsBaseHandle:
    def setup_method(self):
        from salesforce_py.models.base import ModelsBaseOperations

        self._handle = ModelsBaseOperations._handle
        self._handle_status = ModelsBaseOperations._handle_status

    def test_204_returns_empty_dict(self):
        resp = _mock_response(204)
        assert self._handle(resp) == {}

    def test_200_returns_json(self):
        resp = _mock_response(200, {"id": "chatcmpl-abc"})
        assert self._handle(resp) == {"id": "chatcmpl-abc"}

    def test_401_raises_auth_error(self):
        resp = _mock_response(401)
        with pytest.raises(AuthError):
            self._handle(resp)

    def test_429_raises_salesforce_py_error(self):
        resp = _mock_response(429, {"message": "rate limit exceeded"})
        with pytest.raises(SalesforcePyError, match="429"):
            self._handle(resp)

    def test_500_raises_salesforce_py_error(self):
        resp = _mock_response(500, {"message": "server error"})
        with pytest.raises(SalesforcePyError):
            self._handle(resp)

    def test_empty_body_returns_empty_dict(self):
        resp = _mock_response(200)
        resp.content = b""
        assert self._handle(resp) == {}

    def test_non_json_body_raises(self):
        resp = _mock_response(200, {"ok": True})
        resp.json.side_effect = ValueError("not json")
        resp.text = "<html>oops</html>"
        resp.content = b"<html>oops</html>"
        with pytest.raises(SalesforcePyError, match="non-JSON"):
            self._handle(resp)


# ---------------------------------------------------------------------------
# ModelsClient — lifecycle
# ---------------------------------------------------------------------------


class TestModelsClientLifecycle:
    async def test_context_manager(self):
        async with ModelsClient(ACCESS_TOKEN) as client:
            assert client._session._client is not None
        assert client._session._client is None

    def test_repr(self):
        client = ModelsClient(ACCESS_TOKEN)
        assert "einstein/platform/v1" in repr(client)

    def test_operation_namespaces_attached(self):
        client = ModelsClient(ACCESS_TOKEN)
        from salesforce_py.models.operations import (
            ChatGenerationsOperations,
            EmbeddingsOperations,
            FeedbackOperations,
            GenerationsOperations,
        )

        assert isinstance(client.chat_generations, ChatGenerationsOperations)
        assert isinstance(client.embeddings, EmbeddingsOperations)
        assert isinstance(client.feedback, FeedbackOperations)
        assert isinstance(client.generations, GenerationsOperations)

    def test_default_timeout_is_120s(self):
        from salesforce_py._retry import DEFAULT_TIMEOUT

        client = ModelsClient(ACCESS_TOKEN)
        assert client._session._timeout == DEFAULT_TIMEOUT


# ---------------------------------------------------------------------------
# Retry integration — transient statuses trigger one retry
# ---------------------------------------------------------------------------


class TestModelsRetry:
    async def test_post_retries_once_on_transient_status(self, monkeypatch):
        """A 503 on the first call is retried; the 200 body is returned."""
        import salesforce_py._retry as retry_mod

        monkeypatch.setattr(retry_mod, "HTTP_RETRY_DELAY", 0.0)

        body = {"id": "chatcmpl-abc", "generation": {"content": "hi"}}
        c = ModelsClient(ACCESS_TOKEN)
        await c.open()
        c._session.post = AsyncMock(side_effect=[_mock_response(503), _mock_response(200, body)])

        result = await c.generations.generate(GPT_4_OMNI_MINI, "Hello")

        assert result == body
        assert c._session.post.call_count == 2
        await c.close()

    async def test_post_retries_on_429(self, monkeypatch):
        """429 rate-limit is retried once."""
        import salesforce_py._retry as retry_mod

        monkeypatch.setattr(retry_mod, "HTTP_RETRY_DELAY", 0.0)

        body = {"id": "chatcmpl-abc"}
        c = ModelsClient(ACCESS_TOKEN)
        await c.open()
        c._session.post = AsyncMock(side_effect=[_mock_response(429), _mock_response(200, body)])

        result = await c.generations.generate(GPT_4_OMNI_MINI, "Hello")

        assert result == body
        assert c._session.post.call_count == 2
        await c.close()

    def test_custom_base_url_passed_through(self):
        client = ModelsClient(
            ACCESS_TOKEN, base_url="https://api.example.com/einstein/platform/v1/"
        )
        assert client._session._base_url == "https://api.example.com/einstein/platform/v1/"


# ---------------------------------------------------------------------------
# Generations
# ---------------------------------------------------------------------------


class TestGenerations:
    async def test_generate_posts_prompt(self):
        c = await _client(mock_post=_mock_response(200, {"generation": {"generatedText": "hi"}}))
        result = await c.generations.generate(GPT_4_OMNI_MINI, "Say hi")
        assert result == {"generation": {"generatedText": "hi"}}
        c._session.post.assert_awaited_once_with(
            f"models/{GPT_4_OMNI_MINI}/generations",
            params=None,
            headers=None,
            json={"prompt": "Say hi"},
        )
        await c.close()

    async def test_generate_merges_extra(self):
        c = await _client(mock_post=_mock_response(200, {"generation": {}}))
        await c.generations.generate(
            GPT_4_OMNI_MINI,
            "Say hi",
            extra={"localization": {"defaultLocale": "en_US"}},
        )
        c._session.post.assert_awaited_once_with(
            f"models/{GPT_4_OMNI_MINI}/generations",
            params=None,
            headers=None,
            json={
                "prompt": "Say hi",
                "localization": {"defaultLocale": "en_US"},
            },
        )
        await c.close()

    async def test_generate_raw_passthrough(self):
        c = await _client(mock_post=_mock_response(200, {"generation": {}}))
        body = {"prompt": "x", "experimental": True}
        await c.generations.generate_raw(GPT_4_OMNI_MINI, body)
        c._session.post.assert_awaited_once_with(
            f"models/{GPT_4_OMNI_MINI}/generations",
            params=None,
            headers=None,
            json=body,
        )
        await c.close()


# ---------------------------------------------------------------------------
# Chat generations
# ---------------------------------------------------------------------------


class TestChatGenerations:
    async def test_generate_posts_messages(self):
        c = await _client(mock_post=_mock_response(200, {"generationDetails": {}}))
        messages = [
            {"role": "system", "content": "you are helpful"},
            {"role": "user", "content": "hi"},
        ]
        await c.chat_generations.generate(GPT_4_OMNI_MINI, messages)
        c._session.post.assert_awaited_once_with(
            f"models/{GPT_4_OMNI_MINI}/chat-generations",
            params=None,
            headers=None,
            json={"messages": messages},
        )
        await c.close()

    async def test_generate_merges_extra(self):
        c = await _client(mock_post=_mock_response(200, {"generationDetails": {}}))
        await c.chat_generations.generate(
            GPT_4_OMNI_MINI,
            [{"role": "user", "content": "hi"}],
            extra={"temperature": 0.2},
        )
        c._session.post.assert_awaited_once_with(
            f"models/{GPT_4_OMNI_MINI}/chat-generations",
            params=None,
            headers=None,
            json={
                "messages": [{"role": "user", "content": "hi"}],
                "temperature": 0.2,
            },
        )
        await c.close()


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------


class TestEmbeddings:
    async def test_embed_single_string(self):
        c = await _client(mock_post=_mock_response(200, {"embeddings": []}))
        await c.embeddings.embed(OPENAI_ADA_002, "text")
        c._session.post.assert_awaited_once_with(
            f"models/{OPENAI_ADA_002}/embeddings",
            params=None,
            headers=None,
            json={"input": "text"},
        )
        await c.close()

    async def test_embed_list(self):
        c = await _client(mock_post=_mock_response(200, {"embeddings": []}))
        await c.embeddings.embed(OPENAI_ADA_002, ["a", "b"])
        c._session.post.assert_awaited_once_with(
            f"models/{OPENAI_ADA_002}/embeddings",
            params=None,
            headers=None,
            json={"input": ["a", "b"]},
        )
        await c.close()


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------


class TestFeedback:
    async def test_submit_posts_to_feedback(self):
        c = await _client(mock_post=_mock_response(200, {"status": "ok"}))
        body = {"id": "chatcmpl-xyz", "feedback": "GOOD"}
        await c.feedback.submit(body)
        c._session.post.assert_awaited_once_with(
            "feedback",
            params=None,
            headers=None,
            json=body,
        )
        await c.close()


# ---------------------------------------------------------------------------
# Token helper
# ---------------------------------------------------------------------------


class TestFetchToken:
    async def test_success_returns_token_response(self):
        token_body = {
            "access_token": "eyJ0est",
            "instance_url": "https://sample.my.salesforce.com",
            "api_instance_url": "https://api.salesforce.com",
            "token_type": "Bearer",
            "issued_at": "1713195676742",
            "scope": "sfap_api einstein_gpt_api api",
            "signature": "abcd",
        }
        mock_resp = _mock_response(200, token_body)
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_resp)

        with patch("httpx.AsyncClient", return_value=mock_client):
            token = await fetch_token(MY_DOMAIN, CONSUMER_KEY, CONSUMER_SECRET)

        assert isinstance(token, TokenResponse)
        assert token.access_token == "eyJ0est"
        assert token.instance_url == "https://sample.my.salesforce.com"
        assert token.api_instance_url == "https://api.salesforce.com"
        assert token.scope == "sfap_api einstein_gpt_api api"
        assert token.raw == token_body

        mock_client.post.assert_awaited_once_with(
            f"{MY_DOMAIN}/services/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": CONSUMER_KEY,
                "client_secret": CONSUMER_SECRET,
            },
        )

    async def test_400_raises_auth_error(self):
        mock_resp = _mock_response(400, {"error": "invalid_grant"})
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_resp)

        with (
            patch("httpx.AsyncClient", return_value=mock_client),
            pytest.raises(AuthError, match="Models API token request"),
        ):
            await fetch_token(MY_DOMAIN, CONSUMER_KEY, CONSUMER_SECRET)

    async def test_401_raises_auth_error(self):
        mock_resp = _mock_response(401, {"error": "invalid_client"})
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_resp)

        with patch("httpx.AsyncClient", return_value=mock_client), pytest.raises(AuthError):
            await fetch_token(MY_DOMAIN, CONSUMER_KEY, CONSUMER_SECRET)

    async def test_500_raises_salesforce_py_error(self):
        mock_resp = _mock_response(500, {"error": "server"})
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_resp)

        with (
            patch("httpx.AsyncClient", return_value=mock_client),
            pytest.raises(SalesforcePyError),
        ):
            await fetch_token(MY_DOMAIN, CONSUMER_KEY, CONSUMER_SECRET)

    async def test_trailing_slash_stripped(self):
        token_body = {
            "access_token": "x",
            "instance_url": "https://sample.my.salesforce.com",
            "token_type": "Bearer",
            "issued_at": "1",
            "scope": "",
        }
        mock_resp = _mock_response(200, token_body)
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_resp)

        with patch("httpx.AsyncClient", return_value=mock_client):
            await fetch_token(MY_DOMAIN + "/", CONSUMER_KEY, CONSUMER_SECRET)

        called_url = mock_client.post.await_args.args[0]
        assert called_url == f"{MY_DOMAIN}/services/oauth2/token"


# ---------------------------------------------------------------------------
# Error propagation via operations
# ---------------------------------------------------------------------------


class TestErrorPropagation:
    async def test_auth_error_surfaced_from_generate(self):
        c = await _client(mock_post=_mock_response(401))
        with pytest.raises(AuthError):
            await c.generations.generate(GPT_4_OMNI_MINI, "hi")
        await c.close()

    async def test_rate_limit_surfaced_as_salesforce_py_error(self):
        c = await _client(mock_post=_mock_response(429, {"error": "too many"}))
        with pytest.raises(SalesforcePyError, match="429"):
            await c.generations.generate(GPT_4_OMNI_MINI, "hi")
        await c.close()


# ---------------------------------------------------------------------------
# Supported-model constants
# ---------------------------------------------------------------------------


class TestSupportedModels:
    def test_gpt_4_omni_mini_api_name(self):
        assert GPT_4_OMNI_MINI == "sfdc_ai__DefaultGPT4OmniMini"

    def test_all_constants_prefixed(self):
        for name in SUPPORTED_MODELS:
            assert name.startswith("sfdc_ai__Default"), name

    def test_supported_models_unique(self):
        assert len(SUPPORTED_MODELS) == len(set(SUPPORTED_MODELS))


# ---------------------------------------------------------------------------
# ModelsClient.from_env / from_org
# ---------------------------------------------------------------------------


class TestModelsClientFromEnv:
    async def test_from_env_uses_client_creds(self, monkeypatch):
        monkeypatch.setenv("SF_MODELS_CLIENT_ID", "kid")
        monkeypatch.setenv("SF_MODELS_CLIENT_SECRET", "ksecret")
        monkeypatch.setenv("SF_MODELS_INSTANCE_URL", MY_DOMAIN)

        token_resp = TokenResponse(
            access_token=ACCESS_TOKEN,
            instance_url=MY_DOMAIN,
            api_instance_url=None,
            token_type="Bearer",
            issued_at="0",
            scope="sfap_api",
            signature=None,
            raw={},
        )
        with patch("salesforce_py.models.client.fetch_token", new=AsyncMock(return_value=token_resp)):
            client = await ModelsClient.from_env()
        assert client._session._access_token == ACCESS_TOKEN
        await client.close()

    async def test_from_env_uses_sf_instance_url_fallback(self, monkeypatch):
        monkeypatch.setenv("SF_MODELS_CLIENT_ID", "kid")
        monkeypatch.setenv("SF_MODELS_CLIENT_SECRET", "ksecret")
        monkeypatch.delenv("SF_MODELS_INSTANCE_URL", raising=False)
        monkeypatch.setenv("SF_INSTANCE_URL", MY_DOMAIN)

        token_resp = TokenResponse(
            access_token=ACCESS_TOKEN,
            instance_url=MY_DOMAIN,
            api_instance_url=None,
            token_type="Bearer",
            issued_at="0",
            scope="sfap_api",
            signature=None,
            raw={},
        )
        with patch("salesforce_py.models.client.fetch_token", new=AsyncMock(return_value=token_resp)):
            client = await ModelsClient.from_env()
        assert client._session._access_token == ACCESS_TOKEN
        await client.close()

    async def test_from_env_uses_geo_routed_base_url(self, monkeypatch):
        monkeypatch.setenv("SF_MODELS_CLIENT_ID", "kid")
        monkeypatch.setenv("SF_MODELS_CLIENT_SECRET", "ksecret")
        monkeypatch.setenv("SF_MODELS_INSTANCE_URL", MY_DOMAIN)

        geo_url = "https://api.eu.salesforce.com"
        token_resp = TokenResponse(
            access_token=ACCESS_TOKEN,
            instance_url=MY_DOMAIN,
            api_instance_url=geo_url,
            token_type="Bearer",
            issued_at="0",
            scope="sfap_api",
            signature=None,
            raw={},
        )
        with patch("salesforce_py.models.client.fetch_token", new=AsyncMock(return_value=token_resp)):
            client = await ModelsClient.from_env()
        assert client._session._base_url.startswith(geo_url)
        await client.close()

    async def test_from_env_raises_without_client_id(self, monkeypatch):
        monkeypatch.delenv("SF_MODELS_CLIENT_ID", raising=False)
        monkeypatch.delenv("SF_MODELS_CLIENT_SECRET", raising=False)
        with pytest.raises(SalesforcePyError, match="SF_MODELS_CLIENT_ID"):
            await ModelsClient.from_env()

    async def test_from_env_raises_missing_instance_url(self, monkeypatch):
        monkeypatch.setenv("SF_MODELS_CLIENT_ID", "kid")
        monkeypatch.setenv("SF_MODELS_CLIENT_SECRET", "ksecret")
        monkeypatch.delenv("SF_MODELS_INSTANCE_URL", raising=False)
        monkeypatch.delenv("SF_INSTANCE_URL", raising=False)
        with pytest.raises(SalesforcePyError, match="instance URL"):
            await ModelsClient.from_env()

    async def test_from_org_mints_token(self):
        org = MagicMock()
        org.instance_url = MY_DOMAIN

        token_resp = TokenResponse(
            access_token=ACCESS_TOKEN,
            instance_url=MY_DOMAIN,
            api_instance_url=None,
            token_type="Bearer",
            issued_at="0",
            scope="sfap_api",
            signature=None,
            raw={},
        )
        with patch("salesforce_py.models.client.fetch_token", new=AsyncMock(return_value=token_resp)):
            client = await ModelsClient.from_org(org, CONSUMER_KEY, CONSUMER_SECRET)
        assert client._session._access_token == ACCESS_TOKEN
        await client.close()
