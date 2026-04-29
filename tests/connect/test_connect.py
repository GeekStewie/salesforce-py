"""Tests for salesforce_py.connect."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from salesforce_py.connect._session import ConnectSession
from salesforce_py.connect.client import ConnectClient
from salesforce_py.exceptions import AuthError, SalesforcePyError

INSTANCE_URL = "https://test.my.salesforce.com"
ACCESS_TOKEN = "test_token_abc"
FILE_ID = "069000000000001AAA"
GROUP_ID = "0F9000000000001AAA"
TOPIC_ID = "0TO000000000001AAA"
FOLDER_ID = "00l000000000001AAA"
ASSET_ID = "asset_001"
MERCHANT_ACCOUNT_ID = "0R1xx0000000001AAA"
SAVED_PAYMENT_METHOD_ID = "0TGxx0000000001AAA"
APPLE_PAY_DOMAIN_ID = "0TFxx0000000001AAA"
AUTHORIZATION_ID = "0b1xx0000000001AAA"
PAYMENT_ID = "0b2xx0000000001AAA"
PAYMENT_INTENT_ID = "0wpxx0000000001AAA"
PAYMENT_METHOD_SET_ID = "0PSxx0000000001AAA"
PAYMENT_LINK_ID = "12fxx0000000001AAA"
FULFILLMENT_ORDER_ID = "0a7xx0000000001AAA"
RETURN_ORDER_ID = "0a8xx0000000001AAA"
UPLOAD_ID = "0UJxx0000000001AAA"
EXPORT_JOB_ID = "0EJxx0000000001AAA"
ALG_ID = "0AgRR0000004CTr0AM"
AL_ID = "0AnRR0000004CTS0A2"
COMMUNITY_ID = "0DBxx0000004CTYGA2"
REPOSITORY_ID = "0XC000000000001AAA"
REPOSITORY_FILE_ID = "document:abc123"
REPOSITORY_FOLDER_ID = "folder:xyz789"
REPOSITORY_ITEM_TYPE_ID = "itemtype:0x0101"
CUSTOM_DOMAIN_ID = "0DMxx0000004CTYGA2"
CUSTOM_URL_ID = "0JXxx0000004CTYGA2"
DUPLICATE_JOB_DEF_ID = "0POxx0000004CTYGA2"
DUPLICATE_JOB_ID = "0PPxx0000004CTYGA2"
DATA_SERVICE_ID = "0DSxx0000004CTYGA2"
NC_DEVELOPER_NAME = "SampleNamedCred"
EC_DEVELOPER_NAME = "SampleExtCred"
IDP_FULL_NAME = "ExternalIdp1"
PROMPT_TEMPLATE_DEV_NAME = "My_Template"
RECOMMENDATION_ID = "0prxx00000000M7AAI"
STRATEGY_NAME = "AcmeSupport"
REACTION_ID = "0RRxx0000004CTYGA2"
CONTEXT_RECORD_ID = "500xx000000Ylnv"
AUDIENCE_ID = "6AuRM0000004D5w0AE"
TARGET_ID = "6AtRM0000000II30AM"
ENGAGEMENT_SIGNAL_ID = "1H0xx0000004CAeCAM"
COMPOUND_METRIC_ID = "2H0xx0000004CBkCAX"
EXPERIMENT_ID = "1GaSB00000Cojr30AB"
RECOMMENDER_ID = "0heSG0000000JlpYAE"
ACTIVITY_ID = "00Txx0000004CTYGA2"
BOT_VERSION_ID = "0Xxxx0000000001AAA"
QUIP_DOC_ID = "132452345"
ORCHESTRATION_INSTANCE_ID = "0ORxx0000000001AAA"
WEBSTORE_ID = "0ZExx000000001AAAQ"
ACCOUNT_ID = "001xx0000000001AAA"
ADDRESS_ID = "8lWxx0000000001AAA"
CART_ID = "0a6xx0000000001AAA"
CART_ITEM_ID = "0a9xx0000000001AAA"
CART_COUPON_ID = "0a2xx0000000001AAA"
DELIVERY_GROUP_ID = "0a0xx0000000001AAA"
CHECKOUT_ID = "2z9xx0000000001AAA"
PRODUCT_ID = "01txx0000000001AAA"
PRODUCT_CATEGORY_ID = "0ZGxx0000000001AAA"
WISHLIST_ID = "10Wxx0000000001AAA"
WISHLIST_ITEM_ID = "10Vxx0000000001AAA"
ORDER_SUMMARY_ID = "1Osxx0000000001AAA"
SHIPMENT_ID = "0a1xx0000000001AAA"


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
    resp.url = f"{INSTANCE_URL}/services/data/v66.0/connect/test"
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
    c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
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


async def _einstein_client(mock_get=None, mock_post=None, mock_patch=None, mock_delete=None):
    """Like _client but mocks the einstein session used by agentforce_data_libraries."""
    c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
    await c.open()
    if mock_get is not None:
        c._einstein_session.get = AsyncMock(return_value=mock_get)
    if mock_post is not None:
        c._einstein_session.post = AsyncMock(return_value=mock_post)
    if mock_patch is not None:
        c._einstein_session.patch = AsyncMock(return_value=mock_patch)
    if mock_delete is not None:
        c._einstein_session.delete = AsyncMock(return_value=mock_delete)
    return c


# ---------------------------------------------------------------------------
# ConnectSession
# ---------------------------------------------------------------------------


class TestConnectSession:
    async def test_open_creates_client(self):
        session = ConnectSession(INSTANCE_URL, ACCESS_TOKEN)
        await session.open()
        assert session._client is not None
        await session.close()

    async def test_context_manager_opens_and_closes(self):
        session = ConnectSession(INSTANCE_URL, ACCESS_TOKEN)
        async with session:
            assert session._client is not None
        assert session._client is None

    async def test_get_raises_when_not_open(self):
        session = ConnectSession(INSTANCE_URL, ACCESS_TOKEN)
        with pytest.raises(RuntimeError, match="not open"):
            await session.get("some/path")

    async def test_base_url_constructed_correctly(self):
        session = ConnectSession(INSTANCE_URL, ACCESS_TOKEN, api_version="61.0")
        await session.open()
        assert str(session._client.base_url) == f"{INSTANCE_URL}/services/data/v61.0/connect/"
        await session.close()

    async def test_put_raises_when_not_open(self):
        session = ConnectSession(INSTANCE_URL, ACCESS_TOKEN)
        with pytest.raises(RuntimeError, match="not open"):
            await session.put("some/path")


# ---------------------------------------------------------------------------
# ConnectBaseOperations._handle / _handle_status / _get_bytes
# ---------------------------------------------------------------------------


class TestConnectBaseHandle:
    def setup_method(self):
        from salesforce_py.connect.base import ConnectBaseOperations

        self._handle = ConnectBaseOperations._handle
        self._handle_status = ConnectBaseOperations._handle_status

    def test_204_returns_empty_dict(self):
        resp = _mock_response(204)
        assert self._handle(resp) == {}

    def test_200_returns_json(self):
        resp = _mock_response(200, {"id": "abc"})
        assert self._handle(resp) == {"id": "abc"}

    def test_401_raises_auth_error_via_handle(self):
        resp = _mock_response(401)
        with pytest.raises(AuthError):
            self._handle(resp)

    def test_401_raises_auth_error_via_handle_status(self):
        resp = _mock_response(401)
        with pytest.raises(AuthError):
            self._handle_status(resp)

    def test_500_raises_salesforce_py_error(self):
        resp = _mock_response(500, {"message": "server error"})
        with pytest.raises(SalesforcePyError):
            self._handle(resp)

    def test_empty_content_returns_empty_dict(self):
        resp = _mock_response(200)
        resp.content = b""
        assert self._handle(resp) == {}


# ---------------------------------------------------------------------------
# ConnectClient — lifecycle
# ---------------------------------------------------------------------------


class TestConnectClientLifecycle:
    async def test_context_manager(self):
        async with ConnectClient(INSTANCE_URL, ACCESS_TOKEN) as client:
            assert client._session._client is not None
        assert client._session._client is None

    def test_repr(self):
        client = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        assert INSTANCE_URL in repr(client)

    def test_operation_namespaces_attached(self):
        client = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        from salesforce_py.connect.operations import (
            ActionLinksOperations,
            ChatterOperations,
            CommunitiesOperations,
            FilesOperations,
        )

        assert isinstance(client.action_links, ActionLinksOperations)
        assert isinstance(client.chatter, ChatterOperations)
        assert isinstance(client.files, FilesOperations)
        assert isinstance(client.communities, CommunitiesOperations)

    def test_default_timeout_is_120s(self):
        """Connect client defaults to the shared 120s timeout."""
        from salesforce_py._retry import DEFAULT_TIMEOUT

        client = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        assert client._session._timeout == DEFAULT_TIMEOUT


# ---------------------------------------------------------------------------
# Retry integration — transient statuses trigger one retry
# ---------------------------------------------------------------------------


class TestConnectRetry:
    async def test_get_retries_once_on_transient_status(self, monkeypatch):
        """A 503 on the first call is retried once, then the 200 body is returned."""
        import salesforce_py._retry as retry_mod

        monkeypatch.setattr(retry_mod, "HTTP_RETRY_DELAY", 0.0)

        body = {"items": []}
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._session.get = AsyncMock(side_effect=[_mock_response(503), _mock_response(200, body)])

        result = await c.chatter.get_feed_items()

        assert result == body
        assert c._session.get.call_count == 2
        await c.close()

    async def test_get_retries_once_on_420(self, monkeypatch):
        """Salesforce's 'enhance your calm' 420 is treated as transient."""
        import salesforce_py._retry as retry_mod

        monkeypatch.setattr(retry_mod, "HTTP_RETRY_DELAY", 0.0)

        body = {"items": []}
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._session.get = AsyncMock(side_effect=[_mock_response(420), _mock_response(200, body)])

        result = await c.chatter.get_feed_items()

        assert result == body
        assert c._session.get.call_count == 2
        await c.close()

    async def test_final_transient_surfaces_as_salesforcepyerror(self, monkeypatch):
        """When both attempts return 503, the final response surfaces as SalesforcePyError."""
        import salesforce_py._retry as retry_mod

        monkeypatch.setattr(retry_mod, "HTTP_RETRY_DELAY", 0.0)

        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._session.get = AsyncMock(side_effect=[_mock_response(503), _mock_response(503)])

        with pytest.raises(SalesforcePyError):
            await c.chatter.get_feed_items()

        assert c._session.get.call_count == 2
        await c.close()

    async def test_no_retry_on_401(self, monkeypatch):
        """401 is not retried — raises AuthError on first attempt."""
        import salesforce_py._retry as retry_mod

        monkeypatch.setattr(retry_mod, "HTTP_RETRY_DELAY", 0.0)

        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._session.get = AsyncMock(return_value=_mock_response(401))

        with pytest.raises(AuthError):
            await c.chatter.get_feed_items()

        assert c._session.get.call_count == 1
        await c.close()


# ---------------------------------------------------------------------------
# ChatterOperations — feed items (existing)
# ---------------------------------------------------------------------------


class TestChatterFeedItems:
    async def test_get_feed_items(self):
        body = {"items": [], "currentPageToken": "t1", "nextPageToken": None}
        c = await _client(mock_get=_mock_response(200, body))
        assert await c.chatter.get_feed_items() == body
        await c.close()

    async def test_get_feed_item(self):
        body = {"id": "0D5000000000001"}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.chatter.get_feed_item("0D5000000000001")
        assert result["id"] == "0D5000000000001"
        await c.close()

    async def test_post_feed_item(self):
        body = {"id": "0D5000000000002"}
        c = await _client(mock_post=_mock_response(200, body))
        result = await c.chatter.post_feed_item("Hello")
        assert result["id"] == "0D5000000000002"
        await c.close()

    async def test_delete_feed_item(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.chatter.delete_feed_item("0D5000000000001") == {}
        await c.close()

    async def test_post_comment(self):
        body = {"id": "0D7000000000001"}
        c = await _client(mock_post=_mock_response(200, body))
        result = await c.chatter.post_comment("0D5000000000001", "Nice!")
        assert result["id"] == "0D7000000000001"
        await c.close()


# ---------------------------------------------------------------------------
# ChatterOperations — feed elements (new)
# ---------------------------------------------------------------------------


class TestChatterFeedElements:
    async def test_get_feed_elements(self):
        body = {"elements": [], "currentPageToken": "t1"}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.chatter.get_feed_elements()
        assert "elements" in result
        await c.close()

    async def test_get_feed_elements_with_query(self):
        body = {"elements": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.chatter.get_feed_elements(q="contract")
        c._session.get.assert_called_once()
        call_kwargs = c._session.get.call_args
        assert "contract" in str(call_kwargs)
        await c.close()

    async def test_post_feed_element(self):
        body = {"id": "0D8000000000001"}
        c = await _client(mock_post=_mock_response(200, body))
        result = await c.chatter.post_feed_element("Hello group", "0F9000000000001")
        assert result["id"] == "0D8000000000001"
        await c.close()

    async def test_get_files_feed_elements(self):
        body = {"elements": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.chatter.get_files_feed_elements()
        c._session.get.assert_called_once()
        assert "files/me/feed-elements" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_news_feed_elements(self):
        body = {"elements": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.chatter.get_news_feed_elements()
        assert "news/me/feed-elements" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_record_feed_elements(self):
        body = {"elements": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.chatter.get_record_feed_elements("001000000000001")
        # 15-char ID is normalised to 18-char before building the URL
        assert "record/001000000000001AAA/feed-elements" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_user_profile_feed_elements(self):
        body = {"elements": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.chatter.get_user_profile_feed_elements()
        assert "user-profile/me/feed-elements" in c._session.get.call_args[0][0]
        await c.close()


# ---------------------------------------------------------------------------
# FilesOperations — file CRUD
# ---------------------------------------------------------------------------


class TestFilesCRUD:
    async def test_get_file(self):
        body = {"id": FILE_ID, "title": "test.pdf"}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.files.get_file(FILE_ID)
        assert result["title"] == "test.pdf"
        await c.close()

    async def test_upload_new_version(self):
        body = {"id": FILE_ID, "title": "v2.pdf"}
        c = await _client(mock_post=_mock_response(200, body))
        result = await c.files.upload_new_version(FILE_ID, "v2.pdf", b"data")
        assert result["title"] == "v2.pdf"
        await c.close()

    async def test_update_file_title(self):
        body = {"id": FILE_ID, "title": "renamed.pdf"}
        c = await _client(mock_patch=_mock_response(200, body))
        result = await c.files.update_file(FILE_ID, title="renamed.pdf")
        assert result["title"] == "renamed.pdf"
        await c.close()

    async def test_delete_file(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.files.delete_file(FILE_ID) == {}
        await c.close()


# ---------------------------------------------------------------------------
# FilesOperations — binary content / rendition / preview
# ---------------------------------------------------------------------------


class TestFilesBinary:
    async def test_get_file_content(self):
        raw = b"PDF content bytes"
        c = await _client(mock_get=_mock_response(200, content=raw))
        result = await c.files.get_file_content(FILE_ID)
        assert result == raw
        await c.close()

    async def test_get_file_rendition(self):
        raw = b"PNG bytes"
        c = await _client(mock_get=_mock_response(200, content=raw))
        result = await c.files.get_file_rendition(FILE_ID)
        assert result == raw
        await c.close()

    async def test_get_file_preview_content(self):
        raw = b"preview bytes"
        c = await _client(mock_get=_mock_response(200, content=raw))
        result = await c.files.get_file_preview_content(FILE_ID, "PNG")
        assert result == raw
        await c.close()

    async def test_get_file_previews_metadata(self):
        body = {"previews": []}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.files.get_file_previews(FILE_ID)
        assert "previews" in result
        await c.close()

    async def test_generate_file_previews(self):
        body = {"numPages": 5}
        c = await _client(mock_patch=_mock_response(200, body))
        result = await c.files.generate_file_previews(FILE_ID, num_pages=5)
        assert result["numPages"] == 5
        await c.close()

    async def test_get_file_image(self):
        body = {"width": 1920, "height": 1080}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.files.get_file_image(FILE_ID)
        assert result["width"] == 1920
        await c.close()


# ---------------------------------------------------------------------------
# FilesOperations — sharing & share link
# ---------------------------------------------------------------------------


class TestFilesSharing:
    async def test_get_file_shares(self):
        body = {"shares": []}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.files.get_file_shares(FILE_ID)
        assert "shares" in result
        await c.close()

    async def test_share_file_with_users(self):
        body = {"shares": [{"sharedWithId": "005000000000001"}]}
        c = await _client(mock_post=_mock_response(200, body))
        result = await c.files.share_file_with_users(FILE_ID, ["005000000000001"])
        assert len(result["shares"]) == 1
        await c.close()

    async def test_get_share_link(self):
        body = {"url": "https://example.com/share"}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.files.get_share_link(FILE_ID)
        assert "url" in result
        await c.close()

    async def test_create_share_link(self):
        body = {"url": "https://example.com/share/new"}
        c = await _client(mock_put=_mock_response(200, body))
        result = await c.files.create_share_link(FILE_ID)
        assert "url" in result
        await c.close()

    async def test_delete_share_link(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.files.delete_share_link(FILE_ID) == {}
        await c.close()


# ---------------------------------------------------------------------------
# FilesOperations — batch
# ---------------------------------------------------------------------------


class TestFilesBatch:
    async def test_get_files_batch(self):
        body = {"results": [{"id": FILE_ID}]}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.files.get_files_batch([FILE_ID])
        assert result["results"][0]["id"] == FILE_ID
        assert FILE_ID in c._session.get.call_args[0][0]
        await c.close()

    async def test_delete_files_batch(self):
        body = {"results": []}
        c = await _client(mock_delete=_mock_response(200, body))
        await c.files.delete_files_batch([FILE_ID])
        assert FILE_ID in c._session.delete.call_args[0][0]
        await c.close()


# ---------------------------------------------------------------------------
# FilesOperations — user file lists
# ---------------------------------------------------------------------------


class TestFilesUserLists:
    async def test_list_files_defaults_to_me(self):
        body = {"files": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.files.list_files()
        assert "users/me" in c._session.get.call_args[0][0]
        await c.close()

    async def test_list_files_custom_user(self):
        body = {"files": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.files.list_files("005000000000001")
        assert "users/005000000000001" in c._session.get.call_args[0][0]
        await c.close()

    async def test_upload_file(self):
        body = {"id": FILE_ID}
        c = await _client(mock_post=_mock_response(200, body))
        result = await c.files.upload_file("test.pdf", b"bytes")
        assert result["id"] == FILE_ID
        await c.close()

    async def test_list_files_shared_with_me(self):
        body = {"files": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.files.list_files_shared_with_me()
        assert "shared-with-me" in c._session.get.call_args[0][0]
        await c.close()

    async def test_list_files_in_my_groups(self):
        body = {"files": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.files.list_files_in_my_groups()
        assert "filter/groups" in c._session.get.call_args[0][0]
        await c.close()


# ---------------------------------------------------------------------------
# FilesOperations — asset files
# ---------------------------------------------------------------------------


class TestFilesAssets:
    async def test_create_asset_file(self):
        body = {"id": ASSET_ID}
        c = await _client(mock_post=_mock_response(200, body))
        result = await c.files.create_asset_file(FILE_ID, {"name": "logo", "type": "image"})
        assert result["id"] == ASSET_ID
        assert f"files/{FILE_ID}/asset" in c._session.post.call_args[0][0]
        await c.close()

    async def test_get_asset_file(self):
        body = {"id": ASSET_ID, "name": "logo"}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.files.get_asset_file(ASSET_ID)
        assert result["name"] == "logo"
        await c.close()

    async def test_update_asset_file(self):
        body = {"id": ASSET_ID, "guestAccess": True}
        c = await _client(mock_patch=_mock_response(200, body))
        result = await c.files.update_asset_file(ASSET_ID, guest_access=True)
        assert result["guestAccess"] is True
        await c.close()

    async def test_get_asset_file_content(self):
        raw = b"asset bytes"
        c = await _client(mock_get=_mock_response(200, content=raw))
        result = await c.files.get_asset_file_content("myorg__logo.png")
        assert result == raw
        await c.close()

    async def test_get_asset_file_rendition(self):
        raw = b"rendition bytes"
        c = await _client(mock_get=_mock_response(200, content=raw))
        result = await c.files.get_asset_file_rendition("myorg__logo.png")
        assert result == raw
        await c.close()

    async def test_get_asset_files_batch(self):
        body = {"results": [{"id": ASSET_ID}]}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.files.get_asset_files_batch([ASSET_ID])
        assert result["results"][0]["id"] == ASSET_ID
        await c.close()


# ---------------------------------------------------------------------------
# FilesOperations — folders
# ---------------------------------------------------------------------------


class TestFilesFolders:
    async def test_get_folder(self):
        body = {"id": FOLDER_ID, "name": "My Folder"}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.files.get_folder(FOLDER_ID)
        assert result["name"] == "My Folder"
        await c.close()

    async def test_update_folder(self):
        body = {"id": FOLDER_ID, "name": "Renamed"}
        c = await _client(mock_patch=_mock_response(200, body))
        result = await c.files.update_folder(FOLDER_ID, name="Renamed")
        assert result["name"] == "Renamed"
        await c.close()

    async def test_delete_folder(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.files.delete_folder(FOLDER_ID) == {}
        await c.close()

    async def test_list_folder_items(self):
        body = {"items": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.files.list_folder_items(FOLDER_ID)
        assert f"folders/{FOLDER_ID}/items" in c._session.get.call_args[0][0]
        await c.close()

    async def test_add_file_to_folder(self):
        body = {"items": [{"id": FILE_ID}]}
        c = await _client(mock_post=_mock_response(200, body))
        await c.files.add_file_to_folder(FOLDER_ID, FILE_ID)
        c._session.post.assert_called_once()
        await c.close()

    async def test_create_folder(self):
        body = {"id": "00l000000000002AAA", "name": "Sub Folder"}
        c = await _client(mock_post=_mock_response(200, body))
        result = await c.files.create_folder(FOLDER_ID, "Sub Folder")
        assert result["name"] == "Sub Folder"
        await c.close()


# ---------------------------------------------------------------------------
# FilesOperations — group and topic files
# ---------------------------------------------------------------------------


class TestFilesGroupTopic:
    async def test_list_group_files(self):
        body = {"files": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.files.list_group_files(GROUP_ID)
        assert f"chatter/groups/{GROUP_ID}/files" in c._session.get.call_args[0][0]
        await c.close()

    async def test_list_topic_files(self):
        body = {"files": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.files.list_topic_files(TOPIC_ID)
        assert f"topics/{TOPIC_ID}/files" in c._session.get.call_args[0][0]
        await c.close()


# ---------------------------------------------------------------------------
# ID normalisation — _ensure_18 / _ensure_18_list
# ---------------------------------------------------------------------------


class TestEnsure18:
    def setup_method(self):
        from salesforce_py.connect.base import ConnectBaseOperations

        self.ensure_18 = ConnectBaseOperations._ensure_18
        self.ensure_18_list = ConnectBaseOperations._ensure_18_list

    def test_18_char_id_unchanged(self):
        sf_id = "001D000000IqhSLIAZ"
        assert self.ensure_18(sf_id) == sf_id

    def test_15_char_id_converted(self):
        assert self.ensure_18("001D000000IqhSL") == "001D000000IqhSLIAZ"

    def test_me_alias_passes_through(self):
        assert self.ensure_18("me") == "me"

    def test_non_id_string_passes_through(self):
        name = "myorg__company_logo.png"  # longer than 15 chars — not an SF ID
        assert self.ensure_18(name) == name

    def test_list_converts_15_char_ids(self):
        result = self.ensure_18_list(["001D000000IqhSL", "001D000000IqhSLIAZ"])
        assert result == ["001D000000IqhSLIAZ", "001D000000IqhSLIAZ"]

    def test_list_passes_through_non_ids(self):
        name = "myorg__company_logo.png"
        assert self.ensure_18_list(["me", name]) == ["me", name]


class TestEnsure18InOperations:
    """Verify that 15-char IDs are expanded to 18-char before hitting the URL."""

    async def test_files_get_file_normalises_id(self):
        body = {"id": "001D000000IqhSLIAZ"}
        c = await _client(mock_get=_mock_response(200, body))
        await c.files.get_file("001D000000IqhSL")
        assert "001D000000IqhSLIAZ" in c._session.get.call_args[0][0]
        await c.close()

    async def test_files_batch_normalises_ids(self):
        body = {"results": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.files.get_files_batch(["001D000000IqhSL"])
        assert "001D000000IqhSLIAZ" in c._session.get.call_args[0][0]
        await c.close()

    async def test_chatter_get_feed_item_normalises_id(self):
        body = {"id": "001D000000IqhSLIAZ"}
        c = await _client(mock_get=_mock_response(200, body))
        await c.chatter.get_feed_item("001D000000IqhSL")
        assert "001D000000IqhSLIAZ" in c._session.get.call_args[0][0]
        await c.close()

    async def test_chatter_record_feed_elements_normalises_id(self):
        body = {"elements": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.chatter.get_record_feed_elements("001D000000IqhSL")
        assert "001D000000IqhSLIAZ" in c._session.get.call_args[0][0]
        await c.close()

    async def test_communities_get_community_normalises_id(self):
        body = {"id": "001D000000IqhSLIAZ"}
        c = await _client(mock_get=_mock_response(200, body))
        await c.communities.get_community("001D000000IqhSL")
        assert "001D000000IqhSLIAZ" in c._session.get.call_args[0][0]
        await c.close()

    async def test_me_alias_unchanged_in_list_files(self):
        body = {"files": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.files.list_files()  # default user_id="me"
        assert "users/me" in c._session.get.call_args[0][0]
        await c.close()


# ---------------------------------------------------------------------------
# CommunitiesOperations (unchanged)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# ActionLinksOperations
# ---------------------------------------------------------------------------


class TestActionLinkGroupDefinitions:
    async def test_create_group_definition(self):
        body = {"id": ALG_ID, "actionLinks": []}
        c = await _client(mock_post=_mock_response(200, body))
        result = await c.action_links.create_action_link_group_definition(
            {"actionLinks": [], "executionsAllowed": "OncePerUser"}
        )
        assert result["id"] == ALG_ID
        assert "action-link-group-definitions" in c._session.post.call_args[0][0]
        await c.close()

    async def test_create_group_definition_community_scoped(self):
        body = {"id": ALG_ID}
        c = await _client(mock_post=_mock_response(200, body))
        await c.action_links.create_action_link_group_definition({}, community_id=COMMUNITY_ID)
        assert f"communities/{COMMUNITY_ID}" in c._session.post.call_args[0][0]
        await c.close()

    async def test_get_group_definition(self):
        body = {"id": ALG_ID, "executionsAllowed": "OncePerUser"}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.action_links.get_action_link_group_definition(ALG_ID)
        assert result["id"] == ALG_ID
        assert f"action-link-group-definitions/{ALG_ID}" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_group_definition_normalises_15_char_id(self):
        body = {"id": ALG_ID}
        c = await _client(mock_get=_mock_response(200, body))
        await c.action_links.get_action_link_group_definition("0AgRR0000004CTr")
        assert "0AgRR0000004CTr0AM" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_group_definition_community_scoped(self):
        body = {"id": ALG_ID}
        c = await _client(mock_get=_mock_response(200, body))
        await c.action_links.get_action_link_group_definition(ALG_ID, community_id=COMMUNITY_ID)
        assert f"communities/{COMMUNITY_ID}" in c._session.get.call_args[0][0]
        await c.close()

    async def test_delete_group_definition(self):
        c = await _client(mock_delete=_mock_response(204))
        result = await c.action_links.delete_action_link_group_definition(ALG_ID)
        assert result == {}
        assert f"action-link-group-definitions/{ALG_ID}" in c._session.delete.call_args[0][0]
        await c.close()

    async def test_delete_group_definition_community_scoped(self):
        c = await _client(mock_delete=_mock_response(204))
        await c.action_links.delete_action_link_group_definition(ALG_ID, community_id=COMMUNITY_ID)
        assert f"communities/{COMMUNITY_ID}" in c._session.delete.call_args[0][0]
        await c.close()


class TestActionLinkGroups:
    async def test_get_group(self):
        body = {"id": ALG_ID, "actionLinks": [{"id": AL_ID, "status": "NewStatus"}]}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.action_links.get_action_link_group(ALG_ID)
        assert result["id"] == ALG_ID
        assert f"action-link-groups/{ALG_ID}" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_group_community_scoped(self):
        body = {"id": ALG_ID}
        c = await _client(mock_get=_mock_response(200, body))
        await c.action_links.get_action_link_group(ALG_ID, community_id=COMMUNITY_ID)
        assert (
            f"communities/{COMMUNITY_ID}/action-link-groups/{ALG_ID}"
            in c._session.get.call_args[0][0]
        )
        await c.close()

    async def test_get_group_normalises_15_char_id(self):
        body = {"id": ALG_ID}
        c = await _client(mock_get=_mock_response(200, body))
        await c.action_links.get_action_link_group("0AgRR0000004CTr")
        assert "0AgRR0000004CTr0AM" in c._session.get.call_args[0][0]
        await c.close()


class TestActionLinks:
    async def test_get_action_link(self):
        body = {"id": AL_ID, "status": "NewStatus", "labelKey": "Confirm"}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.action_links.get_action_link(AL_ID)
        assert result["status"] == "NewStatus"
        assert f"action-links/{AL_ID}" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_action_link_community_scoped(self):
        body = {"id": AL_ID}
        c = await _client(mock_get=_mock_response(200, body))
        await c.action_links.get_action_link(AL_ID, community_id=COMMUNITY_ID)
        assert f"communities/{COMMUNITY_ID}/action-links/{AL_ID}" in c._session.get.call_args[0][0]
        await c.close()

    async def test_update_action_link_status_pending(self):
        body = {"id": AL_ID, "status": "PendingStatus"}
        c = await _client(mock_patch=_mock_response(200, body))
        result = await c.action_links.update_action_link_status(AL_ID, "PendingStatus")
        assert result["status"] == "PendingStatus"
        assert f"action-links/{AL_ID}" in c._session.patch.call_args[0][0]
        await c.close()

    async def test_update_action_link_status_successful(self):
        body = {"id": AL_ID, "status": "SuccessfulStatus"}
        c = await _client(mock_patch=_mock_response(200, body))
        result = await c.action_links.update_action_link_status(AL_ID, "SuccessfulStatus")
        assert result["status"] == "SuccessfulStatus"
        await c.close()

    async def test_update_action_link_status_failed(self):
        body = {"id": AL_ID, "status": "FailedStatus"}
        c = await _client(mock_patch=_mock_response(200, body))
        result = await c.action_links.update_action_link_status(AL_ID, "FailedStatus")
        assert result["status"] == "FailedStatus"
        await c.close()

    async def test_update_action_link_status_community_scoped(self):
        body = {"id": AL_ID, "status": "SuccessfulStatus"}
        c = await _client(mock_patch=_mock_response(200, body))
        await c.action_links.update_action_link_status(
            AL_ID, "SuccessfulStatus", community_id=COMMUNITY_ID
        )
        assert (
            f"communities/{COMMUNITY_ID}/action-links/{AL_ID}" in c._session.patch.call_args[0][0]
        )
        await c.close()

    async def test_update_sends_status_in_body(self):
        body = {"id": AL_ID, "status": "FailedStatus"}
        c = await _client(mock_patch=_mock_response(200, body))
        await c.action_links.update_action_link_status(AL_ID, "FailedStatus")
        sent_json = c._session.patch.call_args[1]["json"]
        assert sent_json == {"status": "FailedStatus"}
        await c.close()

    async def test_get_action_link_normalises_15_char_id(self):
        body = {"id": AL_ID}
        c = await _client(mock_get=_mock_response(200, body))
        await c.action_links.get_action_link("0AnRR0000004CTS")
        assert "0AnRR0000004CTS0A2" in c._session.get.call_args[0][0]
        await c.close()


class TestActionLinkDiagnosticInfo:
    async def test_get_diagnostic_info(self):
        body = {"diagnosticInfo": "some error detail"}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.action_links.get_action_link_diagnostic_info(AL_ID)
        assert "diagnosticInfo" in result
        assert f"action-links/{AL_ID}/diagnostic-info" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_diagnostic_info_community_scoped(self):
        body = {"diagnosticInfo": "detail"}
        c = await _client(mock_get=_mock_response(200, body))
        await c.action_links.get_action_link_diagnostic_info(AL_ID, community_id=COMMUNITY_ID)
        assert (
            f"communities/{COMMUNITY_ID}/action-links/{AL_ID}/diagnostic-info"
            in c._session.get.call_args[0][0]
        )
        await c.close()

    async def test_get_diagnostic_info_normalises_15_char_id(self):
        body = {}
        c = await _client(mock_get=_mock_response(200, body))
        await c.action_links.get_action_link_diagnostic_info("0AnRR0000004CTS")
        assert "0AnRR0000004CTS0A2" in c._session.get.call_args[0][0]
        await c.close()


# ---------------------------------------------------------------------------
# CommunitiesOperations (unchanged)
# ---------------------------------------------------------------------------
# ConnectCoreOperations
# ---------------------------------------------------------------------------


class TestConnectCoreOperations:
    async def test_get_directory(self):
        body = {
            "communities": f"{INSTANCE_URL}/services/data/v66.0/connect/communities",
            "organization": f"{INSTANCE_URL}/services/data/v66.0/connect/organization",
        }
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.core.get_directory()
        assert "communities" in result
        assert "organization" in result
        # empty-string path resolves to the base URL (no extra segment)
        assert c._session.get.call_args[0][0] == ""
        await c.close()

    async def test_get_organization(self):
        body = {
            "orgId": "00Dxx0000000001AAA",
            "name": "Acme Corp",
            "accessTimeout": 3600,
            "features": {},
            "maintenanceInfo": [],
            "userSettings": {},
        }
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.core.get_organization()
        assert result["orgId"] == "00Dxx0000000001AAA"
        assert result["name"] == "Acme Corp"
        assert c._session.get.call_args[0][0] == "organization"
        await c.close()

    def test_core_namespace_attached(self):
        from salesforce_py.connect.operations import ConnectCoreOperations

        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        assert isinstance(c.core, ConnectCoreOperations)


# ---------------------------------------------------------------------------


class TestCommunitiesOperations:
    async def test_list_communities(self):
        body = {"communities": [{"id": "0DB000000000001", "name": "My Community"}]}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.communities.list_communities()
        assert len(result["communities"]) == 1
        await c.close()

    async def test_get_community(self):
        body = {"id": "0DB000000000001", "name": "My Community", "status": "Live"}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.communities.get_community("0DB000000000001")
        assert result["status"] == "Live"
        await c.close()

    async def test_get_community_members(self):
        body = {"members": [], "currentPageToken": "t1"}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.communities.get_community_members("0DB000000000001")
        assert "members" in result
        await c.close()


# ---------------------------------------------------------------------------
# AgentforceDataLibrariesOperations
# ---------------------------------------------------------------------------

LIB_ID = "1JDxx0000000001AAA"


class TestAgentforceDataLibrariesList:
    async def test_list_libraries_no_filter(self):
        body = {"libraries": [], "totalSize": 0}
        c = await _einstein_client(mock_get=_mock_response(200, body))
        result = await c.agentforce_data_libraries.list_libraries()
        assert result["totalSize"] == 0
        assert "data-libraries" in c._einstein_session.get.call_args[0][0]
        await c.close()

    async def test_list_libraries_with_source_type(self):
        body = {"libraries": [], "totalSize": 0}
        c = await _einstein_client(mock_get=_mock_response(200, body))
        await c.agentforce_data_libraries.list_libraries(source_type="SFDRIVE")
        call_kwargs = c._einstein_session.get.call_args
        assert call_kwargs[1]["params"]["sourceType"] == "SFDRIVE"
        await c.close()

    async def test_list_libraries_omits_source_type_when_not_given(self):
        body = {"libraries": [], "totalSize": 0}
        c = await _einstein_client(mock_get=_mock_response(200, body))
        await c.agentforce_data_libraries.list_libraries()
        params = c._einstein_session.get.call_args[1].get("params", {})
        assert "sourceType" not in params
        await c.close()


class TestAgentforceDataLibrariesCreate:
    async def test_create_library_minimal(self):
        body = {"id": LIB_ID, "masterLabel": "My Lib", "developerName": "My_Lib"}
        c = await _einstein_client(mock_post=_mock_response(201, body))
        result = await c.agentforce_data_libraries.create_library("My Lib", "My_Lib")
        assert result["id"] == LIB_ID
        sent = c._einstein_session.post.call_args[1]["json"]
        assert sent["masterLabel"] == "My Lib"
        assert sent["developerName"] == "My_Lib"
        assert "description" not in sent
        await c.close()

    async def test_create_library_with_all_fields(self):
        body = {"id": LIB_ID}
        c = await _einstein_client(mock_post=_mock_response(201, body))
        await c.agentforce_data_libraries.create_library(
            "My Lib",
            "My_Lib",
            description="A test library",
            data_space_scope_id="0HBxx0000001AAA",
            grounding_source={"sourceType": "SFDRIVE"},
        )
        sent = c._einstein_session.post.call_args[1]["json"]
        assert sent["description"] == "A test library"
        assert sent["dataSpaceScopeId"] == "0HBxx0000001AAA"
        assert sent["groundingSource"] == {"sourceType": "SFDRIVE"}
        await c.close()

    async def test_create_library_posts_to_correct_path(self):
        body = {"id": LIB_ID}
        c = await _einstein_client(mock_post=_mock_response(201, body))
        await c.agentforce_data_libraries.create_library("L", "L")
        assert "data-libraries" in c._einstein_session.post.call_args[0][0]
        await c.close()


class TestAgentforceDataLibrariesCRUD:
    async def test_get_library(self):
        body = {"id": LIB_ID, "masterLabel": "My Lib"}
        c = await _einstein_client(mock_get=_mock_response(200, body))
        result = await c.agentforce_data_libraries.get_library(LIB_ID)
        assert result["masterLabel"] == "My Lib"
        assert f"data-libraries/{LIB_ID}" in c._einstein_session.get.call_args[0][0]
        await c.close()

    async def test_update_library_label_and_description(self):
        body = {"id": LIB_ID, "masterLabel": "New Label"}
        c = await _einstein_client(mock_patch=_mock_response(200, body))
        result = await c.agentforce_data_libraries.update_library(
            LIB_ID, master_label="New Label", description="Updated"
        )
        assert result["masterLabel"] == "New Label"
        sent = c._einstein_session.patch.call_args[1]["json"]
        assert sent["masterLabel"] == "New Label"
        assert sent["description"] == "Updated"
        await c.close()

    async def test_update_library_omits_unset_fields(self):
        body = {"id": LIB_ID}
        c = await _einstein_client(mock_patch=_mock_response(200, body))
        await c.agentforce_data_libraries.update_library(LIB_ID, master_label="New Label")
        sent = c._einstein_session.patch.call_args[1]["json"]
        assert "description" not in sent
        assert "groundingSource" not in sent
        await c.close()

    async def test_delete_library(self):
        c = await _einstein_client(mock_delete=_mock_response(204))
        result = await c.agentforce_data_libraries.delete_library(LIB_ID)
        assert result == {}
        assert f"data-libraries/{LIB_ID}" in c._einstein_session.delete.call_args[0][0]
        await c.close()


class TestAgentforceDataLibrariesFileUpload:
    async def test_get_file_upload_urls(self):
        body = {
            "libraryId": LIB_ID,
            "uploadUrls": [
                {
                    "fileName": "manual.pdf",
                    "uploadUrl": "https://s3.example.com/presigned",
                    "filePath": f"$agentforce_data_library$/{LIB_ID}/manual.pdf",
                    "headers": {},
                }
            ],
        }
        c = await _einstein_client(mock_post=_mock_response(200, body))
        result = await c.agentforce_data_libraries.get_file_upload_urls(LIB_ID, ["manual.pdf"])
        assert result["libraryId"] == LIB_ID
        assert len(result["uploadUrls"]) == 1
        sent = c._einstein_session.post.call_args[1]["json"]
        assert sent["files"] == [{"fileName": "manual.pdf"}]
        assert (
            f"data-libraries/{LIB_ID}/file-upload-urls" in c._einstein_session.post.call_args[0][0]
        )
        await c.close()

    async def test_get_file_upload_urls_multiple_files(self):
        body = {"libraryId": LIB_ID, "uploadUrls": []}
        c = await _einstein_client(mock_post=_mock_response(200, body))
        await c.agentforce_data_libraries.get_file_upload_urls(LIB_ID, ["a.pdf", "b.pdf", "c.pdf"])
        sent = c._einstein_session.post.call_args[1]["json"]
        assert len(sent["files"]) == 3
        assert sent["files"][1] == {"fileName": "b.pdf"}
        await c.close()


class TestAgentforceDataLibrariesAddFiles:
    async def test_add_files(self):
        file_path = f"$agentforce_data_library$/{LIB_ID}/manual.pdf"
        body = {
            "libraryId": LIB_ID,
            "filesAccepted": 1,
            "groundingFileRefs": [{"fileId": "0GBxx001", "fileName": "manual.pdf"}],
        }
        c = await _einstein_client(mock_post=_mock_response(200, body))
        result = await c.agentforce_data_libraries.add_files(
            LIB_ID, [{"filePath": file_path, "fileSize": 12345}]
        )
        assert result["filesAccepted"] == 1
        sent = c._einstein_session.post.call_args[1]["json"]
        assert sent["uploadedFiles"][0]["filePath"] == file_path
        assert sent["uploadedFiles"][0]["fileSize"] == 12345
        assert f"data-libraries/{LIB_ID}/files" in c._einstein_session.post.call_args[0][0]
        await c.close()


class TestAgentforceDataLibrariesIndexing:
    async def test_start_indexing_with_files(self):
        file_path = f"$agentforce_data_library$/{LIB_ID}/manual.pdf"
        body = {
            "libraryId": LIB_ID,
            "sourceType": "SFDRIVE",
            "status": "IN_PROGRESS",
            "message": "Indexing started",
            "filesAccepted": 1,
        }
        c = await _einstein_client(mock_post=_mock_response(200, body))
        result = await c.agentforce_data_libraries.start_indexing(
            LIB_ID, [{"filePath": file_path, "fileSize": 12345}]
        )
        assert result["status"] == "IN_PROGRESS"
        sent = c._einstein_session.post.call_args[1]["json"]
        assert len(sent["uploadedFiles"]) == 1
        assert f"data-libraries/{LIB_ID}/indexing" in c._einstein_session.post.call_args[0][0]
        await c.close()

    async def test_start_indexing_no_files_sends_empty_body(self):
        body = {
            "libraryId": LIB_ID,
            "sourceType": "KNOWLEDGE",
            "status": "IN_PROGRESS",
            "message": "",
        }
        c = await _einstein_client(mock_post=_mock_response(200, body))
        await c.agentforce_data_libraries.start_indexing(LIB_ID)
        sent = c._einstein_session.post.call_args[1]["json"]
        assert sent == {}
        await c.close()


class TestAgentforceDataLibrariesStatus:
    async def test_get_status(self):
        body = {
            "indexingStatus": {
                "libraryId": LIB_ID,
                "status": "READY",
                "currentStage": "SEARCH_INDEX",
                "stages": {},
                "lastUpdatedAt": 1700000000000,
            }
        }
        c = await _einstein_client(mock_get=_mock_response(200, body))
        result = await c.agentforce_data_libraries.get_status(LIB_ID)
        assert result["indexingStatus"]["status"] == "READY"
        assert f"data-libraries/{LIB_ID}/status" in c._einstein_session.get.call_args[0][0]
        await c.close()

    async def test_get_status_in_progress(self):
        body = {
            "indexingStatus": {
                "libraryId": LIB_ID,
                "status": "IN_PROGRESS",
                "currentStage": "DATA_LAKE_OBJECT",
                "stages": {},
                "lastUpdatedAt": 0,
            }
        }
        c = await _einstein_client(mock_get=_mock_response(200, body))
        result = await c.agentforce_data_libraries.get_status(LIB_ID)
        assert result["indexingStatus"]["currentStage"] == "DATA_LAKE_OBJECT"
        await c.close()


class TestAgentforceDataLibrariesUploadReadiness:
    async def test_get_upload_readiness_ready(self):
        body = {
            "libraryId": LIB_ID,
            "ready": True,
            "sourceType": "SFDRIVE",
            "message": "UDLO is ACTIVE",
        }
        c = await _einstein_client(mock_get=_mock_response(200, body))
        result = await c.agentforce_data_libraries.get_upload_readiness(LIB_ID)
        assert result["ready"] is True
        assert (
            f"data-libraries/{LIB_ID}/upload-readiness" in c._einstein_session.get.call_args[0][0]
        )
        await c.close()

    async def test_get_upload_readiness_not_ready(self):
        body = {
            "libraryId": LIB_ID,
            "ready": False,
            "sourceType": "SFDRIVE",
            "message": "UDLO is ACTIVATING",
        }
        c = await _einstein_client(mock_get=_mock_response(200, body))
        result = await c.agentforce_data_libraries.get_upload_readiness(LIB_ID)
        assert result["ready"] is False
        await c.close()

    async def test_get_upload_readiness_with_wait_max_time(self):
        body = {"libraryId": LIB_ID, "ready": True, "sourceType": "SFDRIVE", "message": ""}
        c = await _einstein_client(mock_get=_mock_response(200, body))
        await c.agentforce_data_libraries.get_upload_readiness(LIB_ID, wait_max_time=30000)
        params = c._einstein_session.get.call_args[1]["params"]
        assert params["waitMaxTime"] == 30000
        await c.close()

    async def test_get_upload_readiness_omits_wait_max_time_by_default(self):
        body = {"libraryId": LIB_ID, "ready": False, "sourceType": "SFDRIVE", "message": ""}
        c = await _einstein_client(mock_get=_mock_response(200, body))
        await c.agentforce_data_libraries.get_upload_readiness(LIB_ID)
        params = c._einstein_session.get.call_args[1].get("params", {})
        assert "waitMaxTime" not in params
        await c.close()


class TestAgentforceDataLibrariesSessionRouting:
    """Verify Einstein endpoints use the dedicated einstein session."""

    async def test_einstein_session_base_path(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        assert c._einstein_session._base_path == "einstein"
        assert c._session._base_path == "connect"
        await c.close()

    def test_agentforce_data_libraries_namespace_attached(self):
        from salesforce_py.connect.operations import AgentforceDataLibrariesOperations

        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        assert isinstance(c.agentforce_data_libraries, AgentforceDataLibrariesOperations)


# ---------------------------------------------------------------------------
# GroupsOperations
# ---------------------------------------------------------------------------

MEMBERSHIP_ID = "0FBxx0000000001AAA"
GROUP_RECORD_ID = "0FRxx0000000001AAA"
REQUEST_ID = "0I2xx0000000001AAA"
USER_ID = "005xx000000001AAA"


class TestGroupsCRUD:
    async def test_list_groups(self):
        body = {"groups": [], "currentPageUrl": "/", "nextPageUrl": None}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.groups.list_groups()
        assert "groups" in result
        assert "chatter/groups" in c._session.get.call_args[0][0]
        await c.close()

    async def test_list_groups_with_filters(self):
        c = await _client(mock_get=_mock_response(200, {"groups": []}))
        await c.groups.list_groups(archive_status="Archived", q="eng", page=1)
        params = c._session.get.call_args[1]["params"]
        assert params["archiveStatus"] == "Archived"
        assert params["q"] == "eng"
        assert params["page"] == 1
        await c.close()

    async def test_create_group(self):
        body = {"id": GROUP_ID, "name": "Eng"}
        c = await _client(mock_post=_mock_response(200, body))
        result = await c.groups.create_group({"name": "Eng", "visibility": "PublicAccess"})
        assert result["id"] == GROUP_ID
        await c.close()

    async def test_get_group(self):
        body = {"id": GROUP_ID}
        c = await _client(mock_get=_mock_response(200, body))
        result = await c.groups.get_group(GROUP_ID)
        assert result["id"] == GROUP_ID
        assert f"chatter/groups/{GROUP_ID}" in c._session.get.call_args[0][0]
        await c.close()

    async def test_update_group(self):
        body = {"id": GROUP_ID, "name": "Renamed"}
        c = await _client(mock_patch=_mock_response(200, body))
        result = await c.groups.update_group(GROUP_ID, {"name": "Renamed"})
        assert result["name"] == "Renamed"
        await c.close()

    async def test_delete_group(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.groups.delete_group(GROUP_ID) == {}
        await c.close()

    async def test_groups_batch(self):
        body = {"results": [{"id": GROUP_ID}]}
        c = await _client(mock_get=_mock_response(200, body))
        await c.groups.get_groups_batch([GROUP_ID])
        assert GROUP_ID in c._session.get.call_args[0][0]
        assert "chatter/groups/batch/" in c._session.get.call_args[0][0]
        await c.close()

    async def test_community_prefix_applied(self):
        c = await _client(mock_get=_mock_response(200, {"id": GROUP_ID}))
        await c.groups.get_group(GROUP_ID, community_id=COMMUNITY_ID)
        url = c._session.get.call_args[0][0]
        assert f"communities/{COMMUNITY_ID}/chatter/groups/{GROUP_ID}" in url
        await c.close()


class TestGroupsMembers:
    async def test_get_group_members(self):
        body = {"members": []}
        c = await _client(mock_get=_mock_response(200, body))
        await c.groups.get_group_members(GROUP_ID, page=2)
        assert c._session.get.call_args[1]["params"]["page"] == 2
        await c.close()

    async def test_add_group_member(self):
        body = {"id": MEMBERSHIP_ID}
        c = await _client(mock_post=_mock_response(200, body))
        await c.groups.add_group_member(GROUP_ID, USER_ID, role="GroupManager")
        payload = c._session.post.call_args[1]["json"]
        assert payload["userId"] == USER_ID
        assert payload["role"] == "GroupManager"
        await c.close()

    async def test_get_membership(self):
        c = await _client(mock_get=_mock_response(200, {"id": MEMBERSHIP_ID}))
        await c.groups.get_membership(MEMBERSHIP_ID)
        assert f"group-memberships/{MEMBERSHIP_ID}" in c._session.get.call_args[0][0]
        await c.close()

    async def test_update_membership(self):
        body = {"id": MEMBERSHIP_ID, "role": "GroupOwner"}
        c = await _client(mock_patch=_mock_response(200, body))
        result = await c.groups.update_membership(MEMBERSHIP_ID, "GroupOwner")
        assert result["role"] == "GroupOwner"
        assert c._session.patch.call_args[1]["json"] == {"role": "GroupOwner"}
        await c.close()

    async def test_remove_membership(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.groups.remove_membership(MEMBERSHIP_ID) == {}
        await c.close()

    async def test_memberships_batch(self):
        body = {"results": [{"id": MEMBERSHIP_ID}]}
        c = await _client(mock_get=_mock_response(200, body))
        await c.groups.get_memberships_batch([MEMBERSHIP_ID])
        assert "group-memberships/batch/" in c._session.get.call_args[0][0]
        await c.close()


class TestGroupsMembershipRequests:
    async def test_request_membership(self):
        c = await _client(mock_post=_mock_response(200, {"id": REQUEST_ID}))
        await c.groups.request_group_membership(GROUP_ID)
        assert f"chatter/groups/{GROUP_ID}/members/requests" in c._session.post.call_args[0][0]
        await c.close()

    async def test_list_membership_requests(self):
        c = await _client(mock_get=_mock_response(200, {"requests": []}))
        await c.groups.list_group_membership_requests(GROUP_ID)
        assert f"chatter/groups/{GROUP_ID}/members/requests" in c._session.get.call_args[0][0]
        await c.close()

    async def test_update_membership_request(self):
        c = await _client(mock_patch=_mock_response(200, {"id": REQUEST_ID, "status": "Accepted"}))
        await c.groups.update_group_membership_request(REQUEST_ID, "Accepted")
        assert c._session.patch.call_args[1]["json"] == {"status": "Accepted"}
        assert f"group-membership-requests/{REQUEST_ID}" in c._session.patch.call_args[0][0]
        await c.close()


class TestGroupsRecords:
    async def test_list_group_records(self):
        c = await _client(mock_get=_mock_response(200, {"records": []}))
        await c.groups.list_group_records(GROUP_ID)
        assert f"chatter/groups/{GROUP_ID}/records" in c._session.get.call_args[0][0]
        await c.close()

    async def test_add_group_record(self):
        c = await _client(mock_post=_mock_response(200, {"id": GROUP_RECORD_ID}))
        await c.groups.add_group_record(GROUP_ID, "001xx000003DHPaAAO")
        assert c._session.post.call_args[1]["json"] == {"recordId": "001xx000003DHPaAAO"}
        await c.close()

    async def test_remove_group_record(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.groups.remove_group_record(GROUP_RECORD_ID) == {}
        assert f"group-records/{GROUP_RECORD_ID}" in c._session.delete.call_args[0][0]
        await c.close()


class TestGroupsSettingsAndMisc:
    async def test_list_group_topics(self):
        c = await _client(mock_get=_mock_response(200, {"topics": []}))
        await c.groups.list_group_topics(GROUP_ID)
        assert f"chatter/groups/{GROUP_ID}/topics" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_group_my_settings(self):
        c = await _client(mock_get=_mock_response(200, {"emailFrequency": "EachPost"}))
        await c.groups.get_group_my_settings(GROUP_ID)
        assert f"chatter/groups/{GROUP_ID}/my-settings" in c._session.get.call_args[0][0]
        await c.close()

    async def test_update_group_my_settings(self):
        c = await _client(mock_patch=_mock_response(200, {"emailFrequency": "Never"}))
        await c.groups.update_group_my_settings(GROUP_ID, {"emailFrequency": "Never"})
        assert c._session.patch.call_args[1]["json"] == {"emailFrequency": "Never"}
        await c.close()

    async def test_get_group_announcements(self):
        c = await _client(mock_get=_mock_response(200, {"announcements": []}))
        await c.groups.get_group_announcements(GROUP_ID, page=0)
        params = c._session.get.call_args[1]["params"]
        assert params["page"] == 0
        await c.close()

    async def test_invite_to_group(self):
        c = await _client(mock_post=_mock_response(200, {"invites": []}))
        await c.groups.invite_to_group(GROUP_ID, ["a@example.com", "b@example.com"])
        payload = c._session.post.call_args[1]["json"]
        assert payload["emails"] == ["a@example.com", "b@example.com"]
        assert f"chatter/group/{GROUP_ID}/invite" in c._session.post.call_args[0][0]
        await c.close()


class TestGroupsPhotos:
    async def test_get_group_photo(self):
        c = await _client(mock_get=_mock_response(200, {"url": "x"}))
        await c.groups.get_group_photo(GROUP_ID)
        assert f"chatter/groups/{GROUP_ID}/photo" in c._session.get.call_args[0][0]
        await c.close()

    async def test_set_group_photo(self):
        c = await _client(mock_post=_mock_response(200, {"url": "x"}))
        await c.groups.set_group_photo(GROUP_ID, FILE_ID, crop_size=200, crop_x=0, crop_y=10)
        payload = c._session.post.call_args[1]["json"]
        assert payload["fileId"] == FILE_ID
        assert payload["cropSize"] == 200
        assert payload["cropX"] == 0
        assert payload["cropY"] == 10
        await c.close()

    async def test_delete_group_photo(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.groups.delete_group_photo(GROUP_ID) == {}
        await c.close()

    async def test_get_group_banner_photo(self):
        c = await _client(mock_get=_mock_response(200, {"url": "x"}))
        await c.groups.get_group_banner_photo(GROUP_ID)
        assert f"chatter/groups/{GROUP_ID}/banner-photo" in c._session.get.call_args[0][0]
        await c.close()

    async def test_set_group_banner_photo(self):
        c = await _client(mock_post=_mock_response(200, {"url": "x"}))
        await c.groups.set_group_banner_photo(
            GROUP_ID, FILE_ID, crop_height=400, crop_width=1200, crop_x=0, crop_y=0
        )
        payload = c._session.post.call_args[1]["json"]
        assert payload["cropHeight"] == 400
        assert payload["cropWidth"] == 1200
        await c.close()

    async def test_delete_group_banner_photo(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.groups.delete_group_banner_photo(GROUP_ID) == {}
        await c.close()


# ---------------------------------------------------------------------------
# UsersOperations
# ---------------------------------------------------------------------------

CONVERSATION_ID = "0CVxx0000000001AAA"
MESSAGE_ID = "0IMxx0000000001AAA"


class TestUsersDirectory:
    async def test_list_users(self):
        c = await _client(mock_get=_mock_response(200, {"users": []}))
        await c.users.list_users(q="Bob", page_size=50)
        params = c._session.get.call_args[1]["params"]
        assert params["q"] == "Bob"
        assert params["pageSize"] == 50
        await c.close()

    async def test_list_users_with_search_context_id(self):
        c = await _client(mock_get=_mock_response(200, {"users": []}))
        await c.users.list_users(search_context_id="0D5000000000001")
        params = c._session.get.call_args[1]["params"]
        assert params["searchContextId"] == "0D5000000000001CAA"
        await c.close()

    async def test_get_user_defaults_to_me(self):
        c = await _client(mock_get=_mock_response(200, {"id": "005xxx"}))
        await c.users.get_user()
        assert "chatter/users/me" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_user_by_id(self):
        c = await _client(mock_get=_mock_response(200, {"id": USER_ID}))
        await c.users.get_user(USER_ID)
        assert f"chatter/users/{USER_ID}" in c._session.get.call_args[0][0]
        await c.close()

    async def test_update_user(self):
        c = await _client(mock_patch=_mock_response(200, {"id": USER_ID}))
        await c.users.update_user(USER_ID, {"aboutMe": "Hi"})
        assert c._session.patch.call_args[1]["json"] == {"aboutMe": "Hi"}
        await c.close()

    async def test_users_batch(self):
        c = await _client(mock_get=_mock_response(200, {"results": []}))
        await c.users.get_users_batch([USER_ID])
        assert "chatter/users/batch/" in c._session.get.call_args[0][0]
        assert USER_ID in c._session.get.call_args[0][0]
        await c.close()


class TestUsersFollowing:
    async def test_get_followers(self):
        c = await _client(mock_get=_mock_response(200, {"followers": []}))
        await c.users.get_followers()
        assert "chatter/users/me/followers" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_following_with_filter(self):
        c = await _client(mock_get=_mock_response(200, {"following": []}))
        await c.users.get_following(filter_type="Records")
        params = c._session.get.call_args[1]["params"]
        assert params["filter"] == "Records"
        await c.close()

    async def test_follow_record(self):
        c = await _client(mock_post=_mock_response(200, {"id": "0I0xx000"}))
        await c.users.follow_record("001xx000003DHPaAAO")
        assert c._session.post.call_args[1]["json"] == {"subjectId": "001xx000003DHPaAAO"}
        assert "chatter/users/me/following" in c._session.post.call_args[0][0]
        await c.close()


class TestUsersConversations:
    async def test_get_conversations(self):
        c = await _client(mock_get=_mock_response(200, {"conversations": []}))
        await c.users.get_conversations()
        assert "chatter/users/me/conversations" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_conversation(self):
        c = await _client(mock_get=_mock_response(200, {"id": CONVERSATION_ID}))
        await c.users.get_conversation(CONVERSATION_ID)
        assert f"conversations/{CONVERSATION_ID}" in c._session.get.call_args[0][0]
        await c.close()

    async def test_update_conversation_status(self):
        c = await _client(mock_patch=_mock_response(200, {"read": True}))
        await c.users.update_conversation_status(CONVERSATION_ID, read=True)
        assert c._session.patch.call_args[1]["json"] == {"read": True}
        await c.close()

    async def test_get_unread_conversation_count(self):
        c = await _client(mock_get=_mock_response(200, {"count": 3}))
        result = await c.users.get_unread_conversation_count()
        assert result["count"] == 3
        assert "conversations/unread-count" in c._session.get.call_args[0][0]
        await c.close()


class TestUsersMessages:
    async def test_get_messages(self):
        c = await _client(mock_get=_mock_response(200, {"messages": []}))
        await c.users.get_messages(conversation_id=CONVERSATION_ID)
        params = c._session.get.call_args[1]["params"]
        assert params["conversationId"] == CONVERSATION_ID
        await c.close()

    async def test_send_message_with_recipients(self):
        c = await _client(mock_post=_mock_response(200, {"id": MESSAGE_ID}))
        await c.users.send_message("Hi", recipient_ids=[USER_ID])
        payload = c._session.post.call_args[1]["json"]
        assert payload["body"] == "Hi"
        assert payload["recipients"] == USER_ID
        await c.close()

    async def test_send_message_reply(self):
        c = await _client(mock_post=_mock_response(200, {"id": MESSAGE_ID}))
        await c.users.send_message("Reply", in_reply_to_id=MESSAGE_ID)
        payload = c._session.post.call_args[1]["json"]
        assert payload["inReplyTo"] == MESSAGE_ID
        await c.close()

    async def test_get_message(self):
        c = await _client(mock_get=_mock_response(200, {"id": MESSAGE_ID}))
        await c.users.get_message(MESSAGE_ID)
        assert f"messages/{MESSAGE_ID}" in c._session.get.call_args[0][0]
        await c.close()


class TestUsersRecommendationsAndMisc:
    async def test_get_recommendations_no_filters(self):
        c = await _client(mock_get=_mock_response(200, {"recommendations": []}))
        await c.users.get_recommendations()
        assert "chatter/users/me/recommendations" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_recommendations_with_action(self):
        c = await _client(mock_get=_mock_response(200, {"recommendations": []}))
        await c.users.get_recommendations(action="follow", object_category="users")
        url = c._session.get.call_args[0][0]
        assert url.endswith("chatter/users/me/recommendations/follow/users")
        await c.close()

    async def test_delete_recommendation(self):
        c = await _client(mock_delete=_mock_response(204))
        await c.users.delete_recommendation("follow", USER_ID)
        url = c._session.delete.call_args[0][0]
        assert f"recommendations/follow/{USER_ID}" in url
        await c.close()

    async def test_get_user_settings(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.users.get_user_settings()
        assert "chatter/users/me/settings" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_user_topics(self):
        c = await _client(mock_get=_mock_response(200, {"topics": []}))
        await c.users.get_user_topics()
        assert "chatter/users/me/topics" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_knowledgeable_about_topics(self):
        c = await _client(mock_get=_mock_response(200, {"topics": []}))
        await c.users.get_knowledgeable_about_topics()
        assert "knowledgeable-about-topics" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_reputation_requires_community(self):
        c = await _client(mock_get=_mock_response(200, {"reputation": 42}))
        await c.users.get_reputation(USER_ID, COMMUNITY_ID)
        url = c._session.get.call_args[0][0]
        assert f"communities/{COMMUNITY_ID}/chatter/users/{USER_ID}/reputation" in url
        await c.close()

    async def test_get_user_groups(self):
        c = await _client(mock_get=_mock_response(200, {"groups": []}))
        await c.users.get_user_groups(archive_status="NotArchived")
        params = c._session.get.call_args[1]["params"]
        assert params["archiveStatus"] == "NotArchived"
        await c.close()


# ---------------------------------------------------------------------------
# UserProfilesOperations
# ---------------------------------------------------------------------------


class TestUserProfiles:
    async def test_get_profile(self):
        c = await _client(mock_get=_mock_response(200, {"id": USER_ID}))
        await c.user_profiles.get_profile(USER_ID)
        assert f"user-profiles/{USER_ID}" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_photo(self):
        c = await _client(mock_get=_mock_response(200, {"url": "x"}))
        await c.user_profiles.get_photo(USER_ID)
        assert f"user-profiles/{USER_ID}/photo" in c._session.get.call_args[0][0]
        await c.close()

    async def test_set_photo(self):
        c = await _client(mock_post=_mock_response(200, {"url": "x"}))
        await c.user_profiles.set_photo(
            USER_ID, FILE_ID, crop_size=200, crop_x=5, crop_y=10, version_number=2
        )
        payload = c._session.post.call_args[1]["json"]
        assert payload["fileId"] == FILE_ID
        assert payload["cropSize"] == 200
        assert payload["versionNumber"] == 2
        await c.close()

    async def test_delete_photo(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.user_profiles.delete_photo(USER_ID) == {}
        await c.close()

    async def test_get_banner_photo(self):
        c = await _client(mock_get=_mock_response(200, {"url": "x"}))
        await c.user_profiles.get_banner_photo(USER_ID)
        assert f"user-profiles/{USER_ID}/banner-photo" in c._session.get.call_args[0][0]
        await c.close()

    async def test_set_banner_photo(self):
        c = await _client(mock_post=_mock_response(200, {"url": "x"}))
        await c.user_profiles.set_banner_photo(
            USER_ID, FILE_ID, crop_height=300, crop_width=900, crop_x=0, crop_y=0
        )
        payload = c._session.post.call_args[1]["json"]
        assert payload["cropHeight"] == 300
        assert payload["cropWidth"] == 900
        await c.close()

    async def test_delete_banner_photo(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.user_profiles.delete_banner_photo(USER_ID) == {}
        await c.close()


# ---------------------------------------------------------------------------
# TopicsOperations
# ---------------------------------------------------------------------------

ENDORSEMENT_ID = "0enxx0000000001AAA"
OPT_OUT_ID = "0ebxx0000000001AAA"


class TestTopicsEndorsements:
    async def test_get_endorsements(self):
        c = await _client(mock_get=_mock_response(200, {"endorsements": []}))
        await c.topics.get_endorsements(TOPIC_ID, endorsee_id=USER_ID, endorser_id=USER_ID, page=0)
        params = c._session.get.call_args[1]["params"]
        assert params["endorseeId"] == USER_ID
        assert params["endorserId"] == USER_ID
        assert params["page"] == 0
        await c.close()

    async def test_endorse(self):
        c = await _client(mock_post=_mock_response(200, {"id": ENDORSEMENT_ID}))
        await c.topics.endorse(TOPIC_ID, USER_ID)
        assert c._session.post.call_args[1]["json"] == {"userId": USER_ID}
        assert f"topics/{TOPIC_ID}/endorsements" in c._session.post.call_args[0][0]
        await c.close()

    async def test_get_endorsement(self):
        c = await _client(mock_get=_mock_response(200, {"id": ENDORSEMENT_ID}))
        await c.topics.get_endorsement(ENDORSEMENT_ID)
        assert f"topic-endorsements/{ENDORSEMENT_ID}" in c._session.get.call_args[0][0]
        await c.close()

    async def test_delete_endorsement(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.topics.delete_endorsement(ENDORSEMENT_ID) == {}
        await c.close()


class TestTopicsGroupsAndKnowledge:
    async def test_get_topic_groups(self):
        c = await _client(mock_get=_mock_response(200, {"groups": []}))
        await c.topics.get_topic_groups(TOPIC_ID)
        assert f"topics/{TOPIC_ID}/groups" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_knowledgeable_users(self):
        c = await _client(mock_get=_mock_response(200, {"users": []}))
        await c.topics.get_knowledgeable_users(TOPIC_ID, page=1, page_size=10)
        params = c._session.get.call_args[1]["params"]
        assert params["page"] == 1
        assert params["pageSize"] == 10
        assert "knowledgeable-users" in c._session.get.call_args[0][0]
        await c.close()


class TestTopicsOptOuts:
    async def test_list_opt_outs(self):
        c = await _client(mock_get=_mock_response(200, {"optOuts": []}))
        await c.topics.list_topic_opt_outs(TOPIC_ID)
        assert f"topics/{TOPIC_ID}/topic-opt-outs" in c._session.get.call_args[0][0]
        await c.close()

    async def test_opt_out(self):
        c = await _client(mock_post=_mock_response(200, {"id": OPT_OUT_ID}))
        await c.topics.opt_out_of_topic(TOPIC_ID)
        assert f"topics/{TOPIC_ID}/topic-opt-outs" in c._session.post.call_args[0][0]
        await c.close()

    async def test_opt_in(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.topics.opt_in_to_topic(OPT_OUT_ID) == {}
        assert f"topic-opt-outs/{OPT_OUT_ID}" in c._session.delete.call_args[0][0]
        await c.close()


# ---------------------------------------------------------------------------
# MentionsOperations
# ---------------------------------------------------------------------------


class TestMentions:
    async def test_get_completions(self):
        c = await _client(mock_get=_mock_response(200, {"mentionCompletions": []}))
        await c.mentions.get_completions("bob", context_id="0D5000000000001", type="User")
        params = c._session.get.call_args[1]["params"]
        assert params["q"] == "bob"
        assert params["contextId"] == "0D5000000000001CAA"
        assert params["type"] == "User"
        assert "chatter/mentions/completions" in c._session.get.call_args[0][0]
        await c.close()

    async def test_validate(self):
        c = await _client(mock_get=_mock_response(200, {"hasErrors": False}))
        await c.mentions.validate([USER_ID], parent_id="0D5000000000001")
        params = c._session.get.call_args[1]["params"]
        assert params["recordIds"] == USER_ID
        assert params["parentId"] == "0D5000000000001CAA"
        assert "chatter/mentions/validations" in c._session.get.call_args[0][0]
        await c.close()


# ---------------------------------------------------------------------------
# LikesOperations
# ---------------------------------------------------------------------------

LIKE_ID = "0LKxx0000000001AAA"


class TestLikes:
    async def test_get_like(self):
        c = await _client(mock_get=_mock_response(200, {"id": LIKE_ID}))
        await c.likes.get_like(LIKE_ID)
        assert f"chatter/likes/{LIKE_ID}" in c._session.get.call_args[0][0]
        await c.close()

    async def test_delete_like(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.likes.delete_like(LIKE_ID) == {}
        await c.close()


# ---------------------------------------------------------------------------
# SubscriptionsOperations
# ---------------------------------------------------------------------------

SUBSCRIPTION_ID = "0I0xx0000000001AAA"


class TestSubscriptions:
    async def test_get_subscription(self):
        c = await _client(mock_get=_mock_response(200, {"id": SUBSCRIPTION_ID}))
        await c.subscriptions.get_subscription(SUBSCRIPTION_ID)
        assert f"chatter/subscriptions/{SUBSCRIPTION_ID}" in c._session.get.call_args[0][0]
        await c.close()

    async def test_delete_subscription(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.subscriptions.delete_subscription(SUBSCRIPTION_ID) == {}
        await c.close()


# ---------------------------------------------------------------------------
# AnnouncementsOperations
# ---------------------------------------------------------------------------

ANNOUNCEMENT_ID = "0ANxx0000000001AAA"
FEED_ITEM_ID = "0D5xx0000000001AAA"


class TestAnnouncements:
    async def test_list_announcements(self):
        c = await _client(mock_get=_mock_response(200, {"announcements": []}))
        await c.announcements.list_announcements(GROUP_ID, page=0, page_size=10)
        params = c._session.get.call_args[1]["params"]
        assert params["parentId"] == GROUP_ID
        assert params["page"] == 0
        assert params["pageSize"] == 10
        await c.close()

    async def test_create_announcement(self):
        c = await _client(mock_post=_mock_response(200, {"id": ANNOUNCEMENT_ID}))
        await c.announcements.create_announcement(
            GROUP_ID, "Big news!", "2026-12-31T23:59:59Z", send_emails=True
        )
        payload = c._session.post.call_args[1]["json"]
        assert payload["parentId"] == GROUP_ID
        assert payload["expirationDate"] == "2026-12-31T23:59:59Z"
        assert payload["body"]["messageSegments"][0]["text"] == "Big news!"
        assert payload["sendEmails"] is True
        await c.close()

    async def test_create_announcement_from_feed_item(self):
        c = await _client(mock_post=_mock_response(200, {"id": ANNOUNCEMENT_ID}))
        await c.announcements.create_announcement_from_feed_item(
            FEED_ITEM_ID, "2026-12-31T23:59:59Z"
        )
        payload = c._session.post.call_args[1]["json"]
        assert payload["feedItemId"] == FEED_ITEM_ID
        assert payload["expirationDate"] == "2026-12-31T23:59:59Z"
        await c.close()

    async def test_get_announcement(self):
        c = await _client(mock_get=_mock_response(200, {"id": ANNOUNCEMENT_ID}))
        await c.announcements.get_announcement(ANNOUNCEMENT_ID)
        assert f"chatter/announcements/{ANNOUNCEMENT_ID}" in c._session.get.call_args[0][0]
        await c.close()

    async def test_update_announcement(self):
        c = await _client(mock_patch=_mock_response(200, {"id": ANNOUNCEMENT_ID}))
        await c.announcements.update_announcement(
            ANNOUNCEMENT_ID, expiration_date="2027-01-01T00:00:00Z", is_archived=True
        )
        payload = c._session.patch.call_args[1]["json"]
        assert payload["expirationDate"] == "2027-01-01T00:00:00Z"
        assert payload["isArchived"] is True
        await c.close()

    async def test_delete_announcement(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.announcements.delete_announcement(ANNOUNCEMENT_ID) == {}
        await c.close()


# ---------------------------------------------------------------------------
# CommentsOperations
# ---------------------------------------------------------------------------

COMMENT_ID = "0D7xx0000000001AAA"


class TestCommentsCRUD:
    async def test_get_comment(self):
        c = await _client(mock_get=_mock_response(200, {"id": COMMENT_ID}))
        await c.comments.get_comment(COMMENT_ID)
        assert f"chatter/comments/{COMMENT_ID}" in c._session.get.call_args[0][0]
        await c.close()

    async def test_edit_comment(self):
        c = await _client(mock_patch=_mock_response(200, {"id": COMMENT_ID}))
        await c.comments.edit_comment(COMMENT_ID, "updated")
        payload = c._session.patch.call_args[1]["json"]
        assert payload["body"]["messageSegments"][0]["text"] == "updated"
        await c.close()

    async def test_delete_comment(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.comments.delete_comment(COMMENT_ID) == {}
        await c.close()

    async def test_comments_batch(self):
        c = await _client(mock_get=_mock_response(200, {"results": []}))
        await c.comments.get_comments_batch([COMMENT_ID])
        assert "chatter/comments/batch/" in c._session.get.call_args[0][0]
        assert COMMENT_ID in c._session.get.call_args[0][0]
        await c.close()


class TestCommentsLikesAndVotes:
    async def test_get_comment_likes(self):
        c = await _client(mock_get=_mock_response(200, {"likes": []}))
        await c.comments.get_comment_likes(COMMENT_ID, page=1)
        params = c._session.get.call_args[1]["params"]
        assert params["page"] == 1
        assert f"chatter/comments/{COMMENT_ID}/likes" in c._session.get.call_args[0][0]
        await c.close()

    async def test_like_comment(self):
        c = await _client(mock_post=_mock_response(200, {"id": LIKE_ID}))
        await c.comments.like_comment(COMMENT_ID)
        assert f"chatter/comments/{COMMENT_ID}/likes" in c._session.post.call_args[0][0]
        await c.close()

    async def test_get_up_down_vote(self):
        c = await _client(mock_get=_mock_response(200, {"upVotes": 0}))
        await c.comments.get_up_down_vote(COMMENT_ID)
        assert "capabilities/up-down-vote" in c._session.get.call_args[0][0]
        await c.close()

    async def test_set_up_down_vote(self):
        c = await _client(mock_post=_mock_response(200, {"upVotes": 1}))
        await c.comments.set_up_down_vote(COMMENT_ID, "Up")
        assert c._session.post.call_args[1]["json"] == {"upDownVote": "Up"}
        await c.close()


class TestCommentsCapabilities:
    async def test_get_verified(self):
        c = await _client(mock_get=_mock_response(200, {"isVerified": False}))
        await c.comments.get_verified(COMMENT_ID)
        assert "capabilities/verified" in c._session.get.call_args[0][0]
        await c.close()

    async def test_set_verified(self):
        c = await _client(mock_patch=_mock_response(200, {"isVerified": True}))
        await c.comments.set_verified(COMMENT_ID, True)
        assert c._session.patch.call_args[1]["json"] == {"isVerified": True}
        await c.close()

    async def test_get_status(self):
        c = await _client(mock_get=_mock_response(200, {"feedEntityStatus": "Published"}))
        await c.comments.get_status(COMMENT_ID)
        assert "capabilities/status" in c._session.get.call_args[0][0]
        await c.close()

    async def test_set_status(self):
        c = await _client(mock_patch=_mock_response(200, {"feedEntityStatus": "PendingReview"}))
        await c.comments.set_status(COMMENT_ID, "PendingReview")
        assert c._session.patch.call_args[1]["json"] == {"feedEntityStatus": "PendingReview"}
        await c.close()

    async def test_get_threaded_comments(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.comments.get_threaded_comments(COMMENT_ID)
        assert "capabilities/comments/items" in c._session.get.call_args[0][0]
        await c.close()

    async def test_post_threaded_comment(self):
        c = await _client(mock_post=_mock_response(200, {"id": COMMENT_ID}))
        await c.comments.post_threaded_comment(COMMENT_ID, "reply")
        payload = c._session.post.call_args[1]["json"]
        assert payload["body"]["messageSegments"][0]["text"] == "reply"
        assert "capabilities/comments/items" in c._session.post.call_args[0][0]
        await c.close()

    async def test_is_editable_by_me(self):
        c = await _client(mock_get=_mock_response(200, {"isEditableByMe": True}))
        result = await c.comments.is_editable_by_me(COMMENT_ID)
        assert result["isEditableByMe"] is True
        assert "capabilities/edit/is-editable-by-me" in c._session.get.call_args[0][0]
        await c.close()


# ---------------------------------------------------------------------------
# FeedsOperations
# ---------------------------------------------------------------------------

FAVORITE_ID = "0FVxx0000000001AAA"
STREAM_ID = "0F4xx0000000001AAA"


class TestFeedsDirectory:
    async def test_list_feeds(self):
        c = await _client(mock_get=_mock_response(200, {"feeds": {}}))
        await c.feeds.list_feeds()
        assert c._session.get.call_args[0][0].endswith("chatter/feeds")
        await c.close()


class TestFeedsBasic:
    async def test_get_bookmarks_feed(self):
        c = await _client(mock_get=_mock_response(200, {"elements": []}))
        await c.feeds.get_bookmarks_feed()
        assert "chatter/feeds/bookmarks/me/feed-elements" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_company_feed_with_query(self):
        c = await _client(mock_get=_mock_response(200, {"elements": []}))
        await c.feeds.get_company_feed(q="contract", sort="LastModifiedDateDesc")
        params = c._session.get.call_args[1]["params"]
        assert params["q"] == "contract"
        assert params["sort"] == "LastModifiedDateDesc"
        assert "chatter/feeds/company/feed-elements" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_news_feed(self):
        c = await _client(mock_get=_mock_response(200, {"elements": []}))
        await c.feeds.get_news_feed(page_token="abc", update_since="2026-04-01T00:00:00Z")
        params = c._session.get.call_args[1]["params"]
        assert params["pageToken"] == "abc"
        assert params["updatedSince"] == "2026-04-01T00:00:00Z"
        assert "chatter/feeds/news/me/feed-elements" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_record_feed(self):
        c = await _client(mock_get=_mock_response(200, {"elements": []}))
        await c.feeds.get_record_feed("001xx000003DHPaAAO", recent_comment_count=3)
        params = c._session.get.call_args[1]["params"]
        assert params["recentCommentCount"] == 3
        assert (
            "chatter/feeds/record/001xx000003DHPaAAO/feed-elements"
            in c._session.get.call_args[0][0]
        )
        await c.close()

    async def test_get_user_profile_feed(self):
        c = await _client(mock_get=_mock_response(200, {"elements": []}))
        await c.feeds.get_user_profile_feed()
        assert "chatter/feeds/user-profile/me/feed-elements" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_people_feed(self):
        c = await _client(mock_get=_mock_response(200, {"elements": []}))
        await c.feeds.get_people_feed()
        assert "chatter/feeds/people/me/feed-elements" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_to_feed(self):
        c = await _client(mock_get=_mock_response(200, {"elements": []}))
        await c.feeds.get_to_feed()
        assert "chatter/feeds/to/me/feed-elements" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_topic_feed(self):
        c = await _client(mock_get=_mock_response(200, {"elements": []}))
        await c.feeds.get_topic_feed(TOPIC_ID)
        assert f"chatter/feeds/topics/{TOPIC_ID}/feed-elements" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_mute_feed(self):
        c = await _client(mock_get=_mock_response(200, {"elements": []}))
        await c.feeds.get_mute_feed()
        assert "chatter/feeds/mute/me/feed-elements" in c._session.get.call_args[0][0]
        await c.close()

    async def test_get_groups_feed(self):
        c = await _client(mock_get=_mock_response(200, {"elements": []}))
        await c.feeds.get_groups_feed()
        assert "chatter/feeds/groups/me/feed-elements" in c._session.get.call_args[0][0]
        await c.close()


class TestFeedsFavoritesAndStreams:
    async def test_list_favorites(self):
        c = await _client(mock_get=_mock_response(200, {"favorites": []}))
        await c.feeds.list_favorites()
        url = c._session.get.call_args[0][0]
        assert url.endswith("chatter/feeds/favorites/me")
        await c.close()

    async def test_get_favorite_feed(self):
        c = await _client(mock_get=_mock_response(200, {"elements": []}))
        await c.feeds.get_favorite_feed(FAVORITE_ID)
        url = c._session.get.call_args[0][0]
        assert f"chatter/feeds/favorites/me/{FAVORITE_ID}/feed-elements" in url
        await c.close()

    async def test_get_stream_feed(self):
        c = await _client(mock_get=_mock_response(200, {"elements": []}))
        await c.feeds.get_stream_feed(STREAM_ID)
        url = c._session.get.call_args[0][0]
        assert f"chatter/feeds/streams/{STREAM_ID}/feed-elements" in url
        await c.close()


class TestConnectClientNewNamespaces:
    def test_new_namespaces_attached(self):
        from salesforce_py.connect.operations import (
            AnnouncementsOperations,
            CommentsOperations,
            FeedsOperations,
            GroupsOperations,
            LikesOperations,
            MentionsOperations,
            SubscriptionsOperations,
            TopicsOperations,
            UserProfilesOperations,
            UsersOperations,
        )

        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        assert isinstance(c.announcements, AnnouncementsOperations)
        assert isinstance(c.comments, CommentsOperations)
        assert isinstance(c.feeds, FeedsOperations)
        assert isinstance(c.groups, GroupsOperations)
        assert isinstance(c.likes, LikesOperations)
        assert isinstance(c.mentions, MentionsOperations)
        assert isinstance(c.subscriptions, SubscriptionsOperations)
        assert isinstance(c.topics, TopicsOperations)
        assert isinstance(c.user_profiles, UserProfilesOperations)
        assert isinstance(c.users, UsersOperations)


# ---------------------------------------------------------------------------
# CMS operations
# ---------------------------------------------------------------------------

CHANNEL_ID = "0apRR0000004CTS0A2"
CONTENT_KEY = "MCA4CCV5QS2BAB5H7YRCRPTCWGZQ"
CONTENT_ID = "20YRM0000000CPi2AM"
VARIANT_ID = "20Yxx0000000001AAA"
SPACE_ID = "0Zuxx00000003M5CAI"
SPACE_FOLDER_ID = "9PuRR0000004CTS0A2"
DAM_PROVIDER_ID = "106xxx000000001AAA"
TARGET_ID = "0DBxx0000004ExEGAU"


class TestCMSClientNamespaces:
    def test_cms_namespaces_attached(self):
        from salesforce_py.connect.operations import (
            CMSManagedContentOperations,
            CMSWorkspacesOperations,
        )

        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        assert isinstance(c.cms_content, CMSManagedContentOperations)
        assert isinstance(c.cms_workspaces, CMSWorkspacesOperations)


class TestCMSManagedContentDelivery:
    async def test_get_site_delivery(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.cms_content.get_site_delivery(
            COMMUNITY_ID,
            content_keys=[CONTENT_KEY],
            language="en_US",
            managed_content_type="cms_document",
            page=0,
            page_size=10,
            show_absolute_url=True,
            topics=["news", "products"],
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"communities/{COMMUNITY_ID}/managed-content/delivery"
        assert params["contentKeys"] == CONTENT_KEY
        assert params["language"] == "en_US"
        assert params["managedContentType"] == "cms_document"
        assert params["page"] == 0
        assert params["pageSize"] == 10
        assert params["showAbsoluteUrl"] is True
        assert params["topics"] == "news,products"
        await c.close()

    async def test_get_site_delivery_with_managed_content_ids(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.cms_content.get_site_delivery(COMMUNITY_ID, managed_content_ids=[CONTENT_ID])
        params = c._session.get.call_args[1]["params"]
        assert params["managedContentIds"] == CONTENT_ID
        await c.close()

    async def test_search_site_delivery(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.cms_content.search_site_delivery(
            COMMUNITY_ID, "BMW", scope="TitleOnly", page=1, page_size=50
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"communities/{COMMUNITY_ID}/managed-content/delivery/contents/search"
        assert params["queryTerm"] == "BMW"
        assert params["scope"] == "TitleOnly"
        assert params["page"] == 1
        assert params["pageSize"] == 50
        await c.close()

    async def test_list_delivery_channels(self):
        c = await _client(mock_get=_mock_response(200, {"channels": []}))
        await c.cms_content.list_delivery_channels(page=0, page_size=100)
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == "cms/delivery/channels"
        assert params == {"page": 0, "pageSize": 100}
        await c.close()

    async def test_get_delivery_channel(self):
        c = await _client(mock_get=_mock_response(200, {"id": CHANNEL_ID}))
        await c.cms_content.get_delivery_channel(CHANNEL_ID)
        assert c._session.get.call_args[0][0] == f"cms/delivery/channels/{CHANNEL_ID}"
        await c.close()

    async def test_query_channel_contents(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.cms_content.query_channel_contents(
            CHANNEL_ID,
            content_keys=[CONTENT_KEY],
            end_date="2026-12-31T00:00:00Z",
            include_metadata=True,
            language="en_US",
            managed_content_type="cms_image",
            page=0,
            show_absolute_url=False,
            start_date="2026-01-01T00:00:00Z",
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"cms/delivery/channels/{CHANNEL_ID}/contents/query"
        assert params["contentKeys"] == CONTENT_KEY
        assert params["endDate"] == "2026-12-31T00:00:00Z"
        assert params["includeMetadata"] is True
        assert params["startDate"] == "2026-01-01T00:00:00Z"
        await c.close()

    async def test_search_channel_contents(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.cms_content.search_channel_contents(CHANNEL_ID, "laptop", scope="All")
        params = c._session.get.call_args[1]["params"]
        assert params["queryTerm"] == "laptop"
        assert params["scope"] == "All"
        await c.close()

    async def test_get_delivery_media_content(self):
        c = await _client(mock_get=_mock_response(200, content=b"binary-bytes"))
        result = await c.cms_content.get_delivery_media_content(
            CHANNEL_ID, "media-guid-123", language="fr"
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"cms/delivery/channels/{CHANNEL_ID}/media/media-guid-123/content"
        assert params == {"language": "fr"}
        assert result == b"binary-bytes"
        await c.close()

    async def test_get_searchable_content_types(self):
        c = await _client(mock_get=_mock_response(200, {"types": []}))
        await c.cms_content.get_searchable_content_types(CHANNEL_ID, page=2)
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"cms/channels/{CHANNEL_ID}/searchable-content-types"
        assert params == {"page": 2, "pageSize": 25}
        await c.close()

    async def test_update_searchable_content_type(self):
        c = await _client(mock_patch=_mock_response(200, {"name": "Media"}))
        await c.cms_content.update_searchable_content_type(CHANNEL_ID, "Media", is_searchable=False)
        payload = c._session.patch.call_args[1]["json"]
        assert payload == {"name": "Media", "isSearchable": False}
        await c.close()

    async def test_get_content(self):
        c = await _client(mock_get=_mock_response(200, {"id": CONTENT_ID}))
        await c.cms_content.get_content(
            CONTENT_KEY, language="en_US", version="1", content_version="v2"
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"cms/contents/{CONTENT_KEY}"
        assert params == {"contentVersion": "v2", "language": "en_US", "version": "1"}
        await c.close()

    async def test_get_content_no_params(self):
        c = await _client(mock_get=_mock_response(200, {"id": CONTENT_ID}))
        await c.cms_content.get_content(CONTENT_ID)
        assert c._session.get.call_args[1]["params"] is None
        await c.close()

    async def test_get_folder(self):
        c = await _client(mock_get=_mock_response(200, {"id": SPACE_FOLDER_ID}))
        await c.cms_content.get_folder(SPACE_FOLDER_ID, context_content_space_id=SPACE_ID)
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"cms/folders/{SPACE_FOLDER_ID}"
        assert params == {"contextContentSpaceId": SPACE_ID}
        await c.close()


class TestCMSWorkspacesChannels:
    async def test_list_channels(self):
        c = await _client(mock_get=_mock_response(200, {"channels": []}))
        await c.cms_workspaces.list_channels(show_details=True)
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == "cms/channels"
        assert params["showDetails"] is True
        await c.close()

    async def test_create_channel(self):
        c = await _client(mock_post=_mock_response(200, {"id": CHANNEL_ID}))
        await c.cms_workspaces.create_channel(
            "New Channel",
            TARGET_ID,
            "Community",
            cache_control_max_age=3600,
            is_searchable=True,
        )
        payload = c._session.post.call_args[1]["json"]
        assert payload["name"] == "New Channel"
        assert payload["targetId"] == TARGET_ID
        assert payload["type"] == "Community"
        assert payload["cacheControlMaxAge"] == 3600
        assert payload["isSearchable"] is True
        await c.close()

    async def test_get_channel(self):
        c = await _client(mock_get=_mock_response(200, {"id": CHANNEL_ID}))
        await c.cms_workspaces.get_channel(CHANNEL_ID)
        assert c._session.get.call_args[0][0] == f"cms/channels/{CHANNEL_ID}"
        await c.close()

    async def test_update_channel(self):
        c = await _client(mock_patch=_mock_response(200, {"id": CHANNEL_ID}))
        await c.cms_workspaces.update_channel(CHANNEL_ID, name="Renamed", is_domain_locked=True)
        payload = c._session.patch.call_args[1]["json"]
        assert payload == {"name": "Renamed", "isDomainLocked": True}
        await c.close()

    async def test_delete_channel(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.cms_workspaces.delete_channel(CHANNEL_ID) == {}
        await c.close()


class TestCMSWorkspacesDelivery:
    async def test_get_collection_by_channel(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.cms_workspaces.get_collection("col-key", channel_id=CHANNEL_ID)
        url = c._session.get.call_args[0][0]
        assert url == f"cms/delivery/channels/{CHANNEL_ID}/collections/col-key"
        await c.close()

    async def test_get_collection_by_site(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.cms_workspaces.get_collection("col-key", site_id=COMMUNITY_ID)
        url = c._session.get.call_args[0][0]
        assert url == f"sites/{COMMUNITY_ID}/cms/delivery/collections/col-key"
        await c.close()

    async def test_get_collection_requires_exactly_one(self):
        c = await _client()
        with pytest.raises(ValueError, match="exactly one"):
            await c.cms_workspaces.get_collection("col-key")
        with pytest.raises(ValueError, match="exactly one"):
            await c.cms_workspaces.get_collection(
                "col-key", channel_id=CHANNEL_ID, site_id=COMMUNITY_ID
            )
        await c.close()

    async def test_get_delivery_contents_channel(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.cms_workspaces.get_delivery_contents(
            channel_id=CHANNEL_ID,
            content_keys=[CONTENT_KEY],
            expand_references=True,
            include_content_body=True,
            language="en_US",
            page=0,
            reference_depth=2,
            references_as_list=True,
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"cms/delivery/channels/{CHANNEL_ID}/contents"
        assert params["contentKeys"] == CONTENT_KEY
        assert params["expandReferences"] is True
        assert params["includeContentBody"] is True
        assert params["referenceDepth"] == 2
        assert params["referencesAsList"] is True
        await c.close()

    async def test_get_delivery_contents_site(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.cms_workspaces.get_delivery_contents(site_id=COMMUNITY_ID)
        url = c._session.get.call_args[0][0]
        assert url == f"sites/{COMMUNITY_ID}/cms/delivery/contents"
        await c.close()

    async def test_get_delivery_content(self):
        c = await _client(mock_get=_mock_response(200, {"id": CONTENT_ID}))
        await c.cms_workspaces.get_delivery_content(
            CONTENT_KEY, channel_id=CHANNEL_ID, show_absolute_url=True
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"cms/delivery/channels/{CHANNEL_ID}/contents/{CONTENT_KEY}"
        assert params == {"showAbsoluteUrl": True}
        await c.close()

    async def test_enhanced_search_channel(self):
        c = await _client(mock_post=_mock_response(200, {"items": []}))
        filters = {
            "taxonomyQuery": {"expression": "'T1'", "doesSearchInHierarchy": False},
            "language": "en_US",
            "contentTypeFQNs": ["sfdc_cms__news"],
        }
        await c.cms_workspaces.enhanced_search(
            "BMW", channel_id=CHANNEL_ID, filters=filters, page=0, page_size=10
        )
        url = c._session.post.call_args[0][0]
        payload = c._session.post.call_args[1]["json"]
        assert url == f"cms/delivery/channels/{CHANNEL_ID}/contents/enhanced-search"
        assert payload["queryTerm"] == "BMW"
        assert payload["filters"] == filters
        assert payload["page"] == 0
        assert payload["pageSize"] == 10
        await c.close()

    async def test_enhanced_search_site(self):
        c = await _client(mock_post=_mock_response(200, {"items": []}))
        await c.cms_workspaces.enhanced_search("laptop", site_id=COMMUNITY_ID)
        url = c._session.post.call_args[0][0]
        assert url == f"sites/{COMMUNITY_ID}/cms/delivery/contents/enhanced-search"
        await c.close()


class TestCMSWorkspacesSearchIndexes:
    async def test_get_search_indexes(self):
        c = await _client(mock_get=_mock_response(200, {"indexes": []}))
        await c.cms_workspaces.get_search_indexes(CHANNEL_ID)
        assert c._session.get.call_args[0][0] == f"cms/channels/{CHANNEL_ID}/search/indexes"
        await c.close()

    async def test_trigger_search_indexing(self):
        c = await _client(mock_post=_mock_response(200, {"status": "Queued"}))
        await c.cms_workspaces.trigger_search_indexing(
            CHANNEL_ID, is_incremental=True, fallback_to_full_index=False
        )
        params = c._session.post.call_args[1]["params"]
        assert params == {"isIncremental": True, "fallbackToFullIndex": False}
        await c.close()

    async def test_trigger_search_indexing_no_params(self):
        c = await _client(mock_post=_mock_response(200, {"status": "Queued"}))
        await c.cms_workspaces.trigger_search_indexing(CHANNEL_ID)
        assert c._session.post.call_args[1]["params"] is None
        await c.close()


class TestCMSWorkspacesContents:
    async def test_create_content(self):
        c = await _client(mock_post=_mock_response(200, {"id": CONTENT_ID}))
        body = {"excerpt": "hi", "body": "<p>hello</p>"}
        await c.cms_workspaces.create_content(
            SPACE_ID,
            "Title",
            "sfdc_cms__news",
            body,
            api_name="my_news",
            content_key=CONTENT_KEY,
            url_name="test-url",
        )
        url = c._session.post.call_args[0][0]
        payload = c._session.post.call_args[1]["json"]
        assert url == "cms/contents"
        assert payload["contentSpaceOrFolderId"] == SPACE_ID
        assert payload["title"] == "Title"
        assert payload["contentType"] == "sfdc_cms__news"
        assert payload["contentBody"] == body
        assert payload["apiName"] == "my_news"
        assert payload["contentKey"] == CONTENT_KEY
        assert payload["urlName"] == "test-url"
        await c.close()

    async def test_clone_content(self):
        c = await _client(mock_post=_mock_response(200, {"id": "new-id"}))
        await c.cms_workspaces.clone_content(
            CONTENT_KEY,
            api_name="clone_api",
            content_space_or_folder_id=SPACE_ID,
            include_variants=True,
            title="Cloned",
        )
        url = c._session.post.call_args[0][0]
        payload = c._session.post.call_args[1]["json"]
        assert url == f"cms/contents/{CONTENT_KEY}/clone"
        assert payload == {
            "apiName": "clone_api",
            "contentSpaceOrFolderId": SPACE_ID,
            "includeVariants": True,
            "title": "Cloned",
        }
        await c.close()

    async def test_get_content_taxonomy_terms(self):
        c = await _client(mock_get=_mock_response(200, {"terms": []}))
        await c.cms_workspaces.get_content_taxonomy_terms(CONTENT_KEY)
        assert c._session.get.call_args[0][0] == f"cms/contents/{CONTENT_KEY}/taxonomy-terms"
        await c.close()

    async def test_update_content_taxonomy_terms(self):
        c = await _client(mock_patch=_mock_response(200, {"terms": []}))
        await c.cms_workspaces.update_content_taxonomy_terms(
            CONTENT_KEY,
            terms_to_add=["15dxx000001X8UzBBJ"],
            terms_to_remove=["15dxx000001X8UzBCI"],
            publish=True,
        )
        url = c._session.patch.call_args[0][0]
        payload = c._session.patch.call_args[1]["json"]
        params = c._session.patch.call_args[1]["params"]
        assert url == f"cms/contents/{CONTENT_KEY}/taxonomy-terms"
        assert payload == {
            "termsToAdd": ["15dxx000001X8UzBBJ"],
            "termsToRemove": ["15dxx000001X8UzBCI"],
        }
        assert params == {"publish": True}
        await c.close()

    async def test_publish_contents(self):
        c = await _client(mock_post=_mock_response(200, {"id": "pub"}))
        await c.cms_workspaces.publish_contents(
            content_ids=[CONTENT_ID],
            description="release",
            include_content_references=True,
        )
        url = c._session.post.call_args[0][0]
        payload = c._session.post.call_args[1]["json"]
        assert url == "cms/contents/publish"
        assert payload["contentIds"] == [CONTENT_ID]
        assert payload["description"] == "release"
        assert payload["includeContentReferences"] is True
        await c.close()

    async def test_unpublish_contents(self):
        c = await _client(mock_post=_mock_response(200, {"id": "unpub"}))
        await c.cms_workspaces.unpublish_contents(
            variant_ids=[VARIANT_ID], description="pulling down"
        )
        url = c._session.post.call_args[0][0]
        payload = c._session.post.call_args[1]["json"]
        assert url == "cms/contents/unpublish"
        assert payload["variantIds"] == [VARIANT_ID]
        assert payload["description"] == "pulling down"
        await c.close()


class TestCMSWorkspacesVariants:
    async def test_create_variant(self):
        c = await _client(mock_post=_mock_response(200, {"id": VARIANT_ID}))
        body = {"excerpt": "fr excerpt", "body": "fr body"}
        await c.cms_workspaces.create_variant(
            CONTENT_KEY, "fr", body, title="Titre", url_name="fr_url"
        )
        payload = c._session.post.call_args[1]["json"]
        assert payload == {
            "managedContentKeyorId": CONTENT_KEY,
            "language": "fr",
            "contentBody": body,
            "title": "Titre",
            "urlName": "fr_url",
        }
        await c.close()

    async def test_get_variant(self):
        c = await _client(mock_get=_mock_response(200, {"id": VARIANT_ID}))
        await c.cms_workspaces.get_variant(VARIANT_ID)
        assert c._session.get.call_args[0][0] == f"cms/contents/variants/{VARIANT_ID}"
        await c.close()

    async def test_update_variant(self):
        c = await _client(mock_put=_mock_response(200, {"id": VARIANT_ID}))
        await c.cms_workspaces.update_variant(VARIANT_ID, api_name="v_api", title="New Title")
        payload = c._session.put.call_args[1]["json"]
        assert payload == {"apiName": "v_api", "title": "New Title"}
        await c.close()

    async def test_delete_variant(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.cms_workspaces.delete_variant(VARIANT_ID) == {}
        await c.close()


class TestCMSWorkspacesDAMProviders:
    async def test_list_dam_providers(self):
        c = await _client(mock_get=_mock_response(200, {"providers": []}))
        await c.cms_workspaces.list_dam_providers(content_space_id=SPACE_ID)
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == "cms/digital-asset-management-providers"
        assert params == {"contentSpaceId": SPACE_ID}
        await c.close()

    async def test_list_dam_providers_no_params(self):
        c = await _client(mock_get=_mock_response(200, {"providers": []}))
        await c.cms_workspaces.list_dam_providers()
        assert c._session.get.call_args[1]["params"] is None
        await c.close()

    async def test_create_dam_provider(self):
        c = await _client(mock_post=_mock_response(200, {"id": DAM_PROVIDER_ID}))
        await c.cms_workspaces.create_dam_provider(
            name="Bynder",
            instance_key="https://example.com",
            is_default=True,
            provider_lightning_component_id="lc123",
        )
        payload = c._session.post.call_args[1]["json"]
        assert payload == {
            "name": "Bynder",
            "instanceKey": "https://example.com",
            "isDefault": True,
            "providerLightningComponentId": "lc123",
        }
        await c.close()

    async def test_update_dam_provider(self):
        c = await _client(mock_patch=_mock_response(200, {"id": DAM_PROVIDER_ID}))
        await c.cms_workspaces.update_dam_provider(
            DAM_PROVIDER_ID, name="Updated", is_default=False
        )
        payload = c._session.patch.call_args[1]["json"]
        assert payload == {"name": "Updated", "isDefault": False}
        await c.close()

    async def test_delete_dam_provider(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.cms_workspaces.delete_dam_provider(DAM_PROVIDER_ID) == {}
        await c.close()


class TestCMSWorkspacesFolders:
    async def test_get_folder_shares(self):
        c = await _client(mock_get=_mock_response(200, {"shares": []}))
        await c.cms_workspaces.get_folder_shares(SPACE_FOLDER_ID)
        assert c._session.get.call_args[0][0] == f"cms/folders/{SPACE_FOLDER_ID}/shares"
        await c.close()

    async def test_update_folder_shares(self):
        c = await _client(mock_patch=_mock_response(200, {"shares": []}))
        await c.cms_workspaces.update_folder_shares(
            SPACE_FOLDER_ID,
            share_with=["0Zu000000000001AAA"],
            unshare_with=["0Zu000000000002AAA"],
        )
        payload = c._session.patch.call_args[1]["json"]
        assert payload == {
            "shareWith": [{"targetId": "0Zu000000000001AAA"}],
            "unshareWith": ["0Zu000000000002AAA"],
        }
        await c.close()

    async def test_get_folder_share_targets(self):
        c = await _client(mock_get=_mock_response(200, {"targets": []}))
        await c.cms_workspaces.get_folder_share_targets(SPACE_FOLDER_ID)
        url = c._session.get.call_args[0][0]
        assert url == f"cms/folders/{SPACE_FOLDER_ID}/share-targets"
        await c.close()


class TestCMSWorkspacesItemSearch:
    async def test_search_items(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.cms_workspaces.search_items(
            SPACE_ID,
            "docs",
            content_type_fqn="sfdc_cms__news",
            languages=["en", "fr"],
            page=0,
            scope="All",
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == "cms/items/search"
        assert params["contentSpaceOrFolderIds"] == SPACE_ID
        assert params["queryTerm"] == "docs"
        assert params["contentTypeFQN"] == "sfdc_cms__news"
        assert params["languages"] == "en,fr"
        assert params["scope"] == "All"
        await c.close()


class TestCMSWorkspacesSpaces:
    async def test_list_spaces(self):
        c = await _client(mock_get=_mock_response(200, {"spaces": []}))
        await c.cms_workspaces.list_spaces(name_fragment="Shoe", page=0)
        params = c._session.get.call_args[1]["params"]
        assert params["nameFragment"] == "Shoe"
        await c.close()

    async def test_create_space(self):
        c = await _client(mock_post=_mock_response(200, {"id": SPACE_ID}))
        await c.cms_workspaces.create_space(
            "ShoeStoreWorkspace",
            api_name="shoe_store_workspace",
            default_language="en_US",
            description="Shoes",
            space_type="Content",
        )
        payload = c._session.post.call_args[1]["json"]
        assert payload == {
            "name": "ShoeStoreWorkspace",
            "apiName": "shoe_store_workspace",
            "defaultLanguage": "en_US",
            "description": "Shoes",
            "spaceType": "Content",
        }
        await c.close()

    async def test_get_space(self):
        c = await _client(mock_get=_mock_response(200, {"id": SPACE_ID}))
        await c.cms_workspaces.get_space(SPACE_ID)
        assert c._session.get.call_args[0][0] == f"cms/spaces/{SPACE_ID}"
        await c.close()

    async def test_update_space(self):
        c = await _client(mock_patch=_mock_response(200, {"id": SPACE_ID}))
        await c.cms_workspaces.update_space(SPACE_ID, name="Renamed")
        payload = c._session.patch.call_args[1]["json"]
        assert payload == {"name": "Renamed"}
        await c.close()

    async def test_get_space_channels(self):
        c = await _client(mock_get=_mock_response(200, {"channels": []}))
        await c.cms_workspaces.get_space_channels(SPACE_ID, page=1, page_size=50)
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"cms/spaces/{SPACE_ID}/channels"
        assert params == {"page": 1, "pageSize": 50}
        await c.close()

    async def test_update_space_channels(self):
        c = await _client(mock_patch=_mock_response(200, {"channels": []}))
        ops = [
            {"channelId": "0ap000000000001", "operation": "Add"},
            {"channelId": "0ap000000000003", "operation": "Remove"},
        ]
        await c.cms_workspaces.update_space_channels(SPACE_ID, ops)
        payload = c._session.patch.call_args[1]["json"]
        assert payload == {"spaceChannels": ops}
        await c.close()


# ---------------------------------------------------------------------------
# Batch 2: Motifs, Quick Text, Knowledge, Email Merge Fields, Push, Notifications, ...
# ---------------------------------------------------------------------------

NOTIFICATION_ID = "0MLxx0000004CTS0A2"
QUICK_TEXT_ID = "0B3xx0000004CTS0A2"
RECORD_ID = "006xx0000004CTS0A2"
USER_ID_A = "005xx0000004CTS0A2"
USER_ID_B = "005xx0000004CTS1A2"


class TestMotifsOperations:
    async def test_get_motif(self):
        c = await _client(mock_get=_mock_response(200, {"color": "1797C0"}))
        await c.motifs.get_motif("005D0000001LLO1")
        assert c._session.get.call_args[0][0] == "motifs/005D0000001LLO1IAO"
        await c.close()

    async def test_get_motif_with_prefix(self):
        c = await _client(mock_get=_mock_response(200, {"color": "1797C0"}))
        await c.motifs.get_motif("005")
        assert c._session.get.call_args[0][0] == "motifs/005"
        await c.close()

    async def test_get_motif_community_scoped(self):
        c = await _client(mock_get=_mock_response(200, {"color": "abc"}))
        await c.motifs.get_motif("005", community_id=COMMUNITY_ID)
        assert c._session.get.call_args[0][0] == f"communities/{COMMUNITY_ID}/motifs/005"
        await c.close()

    async def test_get_motifs_batch(self):
        c = await _client(mock_get=_mock_response(200, {"results": []}))
        await c.motifs.get_motifs_batch(["005", "069D00000001FHF"])
        url = c._session.get.call_args[0][0]
        assert url.startswith("motifs/batch/005,069D00000001FHF")
        await c.close()


class TestQuickTextOperations:
    async def test_get_quick_text_body(self):
        c = await _client(mock_get=_mock_response(200, {"body": "rendered"}))
        await c.quick_text.get_quick_text_body(
            QUICK_TEXT_ID,
            what_id=RECORD_ID,
            who_id=USER_ID_A,
            channel="Email",
            quick_text_context="Runtime",
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == "quicktextbody"
        assert params["quickTextId"] == QUICK_TEXT_ID
        assert params["whatId"] == RECORD_ID
        assert params["whoId"] == USER_ID_A
        assert params["channel"] == "Email"
        assert params["quickTextContext"] == "Runtime"
        await c.close()

    async def test_get_quick_text_body_minimal(self):
        c = await _client(mock_get=_mock_response(200, {"body": "x"}))
        await c.quick_text.get_quick_text_body(QUICK_TEXT_ID, what_id=RECORD_ID, who_id=USER_ID_A)
        params = c._session.get.call_args[1]["params"]
        assert "channel" not in params
        assert "launchSource" not in params
        await c.close()


class TestKnowledgeArticleViewStat:
    async def test_increment_view_stat(self):
        c = await _client(mock_patch=_mock_response(204))
        await c.knowledge_article_view_stat.increment_view_stat("ka230000000PCiy")
        url = c._session.patch.call_args[0][0]
        body = c._session.patch.call_args[1]["json"]
        assert url == "knowledge/article/view-stat"
        assert body == {"articleOrVersionId": "ka230000000PCiyAAG"}
        await c.close()

    async def test_increment_view_stat_community(self):
        c = await _client(mock_patch=_mock_response(204))
        await c.knowledge_article_view_stat.increment_view_stat(
            "ka230000000PCiy", community_id=COMMUNITY_ID
        )
        url = c._session.patch.call_args[0][0]
        assert url == f"communities/{COMMUNITY_ID}/knowledge/article/view-stat"
        await c.close()


class TestEmailMergeFieldsOperations:
    async def test_list_merge_fields(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {"mergeFields": []}))
        await c.email_merge_fields.list_merge_fields(["Account", "Contact"])
        url = c._data_session.get.call_args[0][0]
        params = c._data_session.get.call_args[1]["params"]
        assert url == "email-merge-fields"
        assert params == {"objectApiNames": "Account,Contact"}
        await c.close()

    async def test_data_session_base_url(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        base = str(c._data_session._client.base_url)
        assert base.endswith("/services/data/v66.0/") or "/services/data/v" in base
        assert "connect" not in base.split("/services/data/")[1]
        await c.close()


class TestPushNotificationsOperations:
    async def test_send_push(self):
        c = await _client(mock_post=_mock_response(200, {"success": True}))
        await c.push_notifications.send_push(
            "TestApp",
            [USER_ID_A, USER_ID_B],
            payload="{'aps':{'alert':'x'}}",
            namespace="abc",
        )
        url = c._session.post.call_args[0][0]
        body = c._session.post.call_args[1]["json"]
        assert url == "notifications/push"
        assert body == {
            "appName": "TestApp",
            "userIds": [USER_ID_A, USER_ID_B],
            "payload": "{'aps':{'alert':'x'}}",
            "namespace": "abc",
        }
        await c.close()

    async def test_send_push_no_namespace(self):
        c = await _client(mock_post=_mock_response(200, {}))
        await c.push_notifications.send_push("TestApp", [USER_ID_A], payload="{}")
        body = c._session.post.call_args[1]["json"]
        assert "namespace" not in body
        await c.close()


class TestNotificationsOperations:
    async def test_list_notifications(self):
        c = await _client(mock_get=_mock_response(200, {"notifications": []}))
        await c.notifications.list_notifications(
            before="2019-06-25T18:24:31.000Z", size=20, trim_messages=False
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == "notifications"
        assert params["before"] == "2019-06-25T18:24:31.000Z"
        assert params["size"] == 20
        assert params["trimMessages"] == "false"
        await c.close()

    async def test_list_notifications_empty(self):
        c = await _client(mock_get=_mock_response(200, {"notifications": []}))
        await c.notifications.list_notifications()
        assert c._session.get.call_args[1]["params"] == {}
        await c.close()

    async def test_mark_notifications(self):
        c = await _client(mock_patch=_mock_response(200, {"notifications": []}))
        await c.notifications.mark_notifications(read=True, before="2024-01-01T00:00:00.000Z")
        body = c._session.patch.call_args[1]["json"]
        assert body == {"read": True, "before": "2024-01-01T00:00:00.000Z"}
        await c.close()

    async def test_mark_notifications_by_ids(self):
        c = await _client(mock_patch=_mock_response(200, {}))
        await c.notifications.mark_notifications(seen=True, notification_ids=[NOTIFICATION_ID])
        body = c._session.patch.call_args[1]["json"]
        assert body == {"seen": True, "notificationIds": [NOTIFICATION_ID]}
        await c.close()

    async def test_get_notification(self):
        c = await _client(mock_get=_mock_response(200, {"id": NOTIFICATION_ID}))
        await c.notifications.get_notification(NOTIFICATION_ID, trim_messages=True)
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"notifications/{NOTIFICATION_ID}"
        assert params == {"trimMessages": "true"}
        await c.close()

    async def test_mark_notification(self):
        c = await _client(mock_patch=_mock_response(200, {"id": NOTIFICATION_ID}))
        await c.notifications.mark_notification(NOTIFICATION_ID, read=True)
        url = c._session.patch.call_args[0][0]
        body = c._session.patch.call_args[1]["json"]
        assert url == f"notifications/{NOTIFICATION_ID}"
        assert body == {"read": True}
        await c.close()

    async def test_execute_action(self):
        c = await _client(mock_post=_mock_response(200, {"status": "ok"}))
        await c.notifications.execute_action(NOTIFICATION_ID, "approve")
        url = c._session.post.call_args[0][0]
        assert url == f"notifications/{NOTIFICATION_ID}/actions/approve"
        await c.close()

    async def test_get_status(self):
        c = await _client(mock_get=_mock_response(200, {"unreadCount": 0}))
        await c.notifications.get_status()
        assert c._session.get.call_args[0][0] == "notifications/status"
        await c.close()

    async def test_list_types(self):
        c = await _client(mock_get=_mock_response(200, {"types": []}))
        await c.notifications.list_types()
        assert c._session.get.call_args[0][0] == "notifications/types"
        await c.close()


class TestNotificationSettingsOperations:
    async def test_list_org_settings(self):
        c = await _client(mock_get=_mock_response(200, {"settings": []}))
        await c.notification_settings.list_org_settings()
        assert c._session.get.call_args[0][0] == "notifications/settings/organization"
        await c.close()

    async def test_get_org_setting(self):
        c = await _client(mock_get=_mock_response(200, {"type": "TaskAssigned"}))
        await c.notification_settings.get_org_setting("TaskAssigned")
        url = c._session.get.call_args[0][0]
        assert url == "notifications/settings/organization/TaskAssigned"
        await c.close()

    async def test_set_org_setting(self):
        c = await _client(mock_post=_mock_response(200, {"type": "TaskAssigned"}))
        await c.notification_settings.set_org_setting(
            "TaskAssigned",
            desktop_enabled=False,
            email_enabled=True,
        )
        body = c._session.post.call_args[1]["json"]
        assert body == {"desktopEnabled": False, "emailEnabled": True}
        await c.close()

    async def test_reset_org_setting(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.notification_settings.reset_org_setting("TaskAssigned") == {}
        await c.close()

    async def test_list_app_settings(self):
        c = await _client(mock_get=_mock_response(200, {"settings": []}))
        await c.notification_settings.list_app_settings(application_id="0H4xx0000004CTSCA2")
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == "notifications/app-settings/organization"
        assert params["applicationId"] == "0H4xx0000004CTSCA2"
        await c.close()

    async def test_get_app_setting(self):
        c = await _client(mock_get=_mock_response(200, {"type": "TaskAssigned"}))
        await c.notification_settings.get_app_setting("TaskAssigned")
        url = c._session.get.call_args[0][0]
        assert url == "notifications/app-settings/organization/TaskAssigned"
        await c.close()

    async def test_set_app_setting(self):
        c = await _client(mock_post=_mock_response(200, {}))
        await c.notification_settings.set_app_setting("TaskAssigned", enabled=True)
        body = c._session.post.call_args[1]["json"]
        assert body == {"enabled": True}
        await c.close()

    async def test_reset_app_setting(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.notification_settings.reset_app_setting("TaskAssigned") == {}
        await c.close()


class TestTopicsOnRecordsOperations:
    async def test_list_topics(self):
        c = await _client(mock_get=_mock_response(200, {"topics": []}))
        await c.topics_on_records.list_topics(RECORD_ID)
        url = c._session.get.call_args[0][0]
        assert url == f"records/{RECORD_ID}/topics"
        await c.close()

    async def test_add_topic_by_id(self):
        c = await _client(mock_post=_mock_response(200, {"id": TOPIC_ID}))
        await c.topics_on_records.add_topic(RECORD_ID, topic_id=TOPIC_ID)
        body = c._session.post.call_args[1]["json"]
        assert body == {"topicId": TOPIC_ID}
        await c.close()

    async def test_add_topic_by_name(self):
        c = await _client(mock_post=_mock_response(200, {"name": "API"}))
        await c.topics_on_records.add_topic(RECORD_ID, topic_name="API")
        body = c._session.post.call_args[1]["json"]
        assert body == {"topicName": "API"}
        await c.close()

    async def test_add_topic_requires_exactly_one(self):
        c = await _client()
        with pytest.raises(ValueError):
            await c.topics_on_records.add_topic(RECORD_ID)
        with pytest.raises(ValueError):
            await c.topics_on_records.add_topic(RECORD_ID, topic_id=TOPIC_ID, topic_name="API")
        await c.close()

    async def test_remove_topic(self):
        c = await _client(mock_delete=_mock_response(204))
        await c.topics_on_records.remove_topic(RECORD_ID, TOPIC_ID)
        url = c._session.delete.call_args[0][0]
        params = c._session.delete.call_args[1]["params"]
        assert url == f"records/{RECORD_ID}/topics"
        assert params == {"topicId": TOPIC_ID}
        await c.close()

    async def test_replace_topics(self):
        c = await _client(mock_put=_mock_response(200, {"topics": []}))
        await c.topics_on_records.replace_topics(
            RECORD_ID,
            ["API", "Connect"],
            topic_suggestions=["Salesforce"],
        )
        body = c._session.put.call_args[1]["json"]
        assert body == {
            "topicNames": ["API", "Connect"],
            "topicSuggestions": ["Salesforce"],
        }
        await c.close()

    async def test_community_scoped(self):
        c = await _client(mock_get=_mock_response(200, {"topics": []}))
        await c.topics_on_records.list_topics(RECORD_ID, community_id=COMMUNITY_ID)
        url = c._session.get.call_args[0][0]
        assert url == f"communities/{COMMUNITY_ID}/records/{RECORD_ID}/topics"
        await c.close()


# ---------------------------------------------------------------------------
# Batch 3: Experience Cloud family
# ---------------------------------------------------------------------------

SITE_ID_NEW = "0DBxx0000004E1vGAE"
MANAGED_TOPIC_ID = "0mtxx0000004CTS0A2"
NETWORK_DATA_CATEGORY_ID = "0P6xx0000004CTS0A2"
FORM_ID = "form_abc"


class TestCommunitiesOperationsExtended:
    async def test_list_communities_status(self):
        c = await _client(mock_get=_mock_response(200, {"communities": []}))
        await c.communities.list_communities(status="Live")
        assert c._session.get.call_args[1]["params"] == {"status": "Live"}
        await c.close()

    async def test_create_community(self):
        c = await _client(mock_post=_mock_response(200, {"id": COMMUNITY_ID}))
        await c.communities.create_community(
            "My Site",
            template_name="Build Your Own (LWR)",
            url_path_prefix="mysite",
            description="desc",
            template_params={"AuthenticationType": "AUTHENTICATED"},
        )
        body = c._session.post.call_args[1]["json"]
        assert body == {
            "name": "My Site",
            "templateName": "Build Your Own (LWR)",
            "urlPathPrefix": "mysite",
            "description": "desc",
            "templateParams": {"AuthenticationType": "AUTHENTICATED"},
        }
        await c.close()

    async def test_publish_community(self):
        c = await _client(mock_post=_mock_response(200, {"status": "InProgress"}))
        await c.communities.publish_community(COMMUNITY_ID)
        assert c._session.post.call_args[0][0] == f"communities/{COMMUNITY_ID}/publish"
        await c.close()

    async def test_get_templates(self):
        c = await _client(mock_get=_mock_response(200, {"templates": []}))
        await c.communities.get_templates()
        assert c._session.get.call_args[0][0] == "communities/templates"
        await c.close()

    async def test_get_externally_managed_accounts(self):
        c = await _client(mock_get=_mock_response(200, {"accounts": []}))
        await c.communities.get_externally_managed_accounts(COMMUNITY_ID, include_my_account=True)
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"communities/{COMMUNITY_ID}/external-managed-accounts"
        assert params == {"includeMyAccount": True}
        await c.close()

    async def test_get_preview_url(self):
        c = await _client(mock_get=_mock_response(200, {"url": "https://..."}))
        await c.communities.get_preview_url(
            COMMUNITY_ID, "Home", url_parameters="recordId%3D006xxx"
        )
        url = c._session.get.call_args[0][0]
        assert url == f"communities/{COMMUNITY_ID}/preview-url/pages/Home"
        await c.close()


class TestSitesKnowledgeOperations:
    async def test_get_trending_articles(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.sites_knowledge.get_trending_articles(COMMUNITY_ID, max_results=10)
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"communities/{COMMUNITY_ID}/trending-articles"
        assert params == {"maxResults": 10}
        await c.close()

    async def test_get_topic_trending_articles(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.sites_knowledge.get_topic_trending_articles(COMMUNITY_ID, TOPIC_ID)
        url = c._session.get.call_args[0][0]
        assert url == (f"communities/{COMMUNITY_ID}/topics/{TOPIC_ID}/trending-articles")
        await c.close()

    async def test_get_topic_top_viewed_articles(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.sites_knowledge.get_topic_top_viewed_articles(COMMUNITY_ID, TOPIC_ID, max_results=5)
        url = c._session.get.call_args[0][0]
        assert url == (f"communities/{COMMUNITY_ID}/topics/{TOPIC_ID}/top-viewed-articles")
        await c.close()


class TestSitesModerationOperations:
    async def test_get_file_flags(self):
        c = await _client(mock_get=_mock_response(200, {"flags": []}))
        await c.sites_moderation.get_file_flags(COMMUNITY_ID, FILE_ID, visibility="ModeratorsOnly")
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"communities/{COMMUNITY_ID}/files/{FILE_ID}/moderation-flags"
        assert params == {"visibility": "ModeratorsOnly"}
        await c.close()

    async def test_flag_file(self):
        c = await _client(mock_post=_mock_response(200, {"flags": []}))
        await c.sites_moderation.flag_file(
            COMMUNITY_ID, FILE_ID, note="spam", flag_type="FlagAsSpam"
        )
        body = c._session.post.call_args[1]["json"]
        assert body == {"note": "spam", "type": "FlagAsSpam"}
        await c.close()

    async def test_unflag_file(self):
        c = await _client(mock_delete=_mock_response(204))
        await c.sites_moderation.unflag_file(COMMUNITY_ID, FILE_ID, user_id=USER_ID_A)
        params = c._session.delete.call_args[1]["params"]
        assert params == {"userId": USER_ID_A}
        await c.close()

    async def test_get_flagged_files(self):
        c = await _client(mock_get=_mock_response(200, {"files": []}))
        await c.sites_moderation.get_flagged_files(COMMUNITY_ID, page=0, q="spam")
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"communities/{COMMUNITY_ID}/files/moderation"
        assert params == {"page": 0, "q": "spam"}
        await c.close()

    async def test_get_user_audit_counts(self):
        c = await _client(mock_get=_mock_response(200, {"count": 0}))
        await c.sites_moderation.get_user_audit_counts(COMMUNITY_ID, USER_ID_A)
        url = c._session.get.call_args[0][0]
        assert url == (f"communities/{COMMUNITY_ID}/chatter/users/{USER_ID_A}/audit-actions/counts")
        await c.close()


class TestMicrositesOperations:
    async def test_save_form(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {"id": FORM_ID}))
        await c.microsites.save_form(
            SITE_ID_NEW,
            "Contact Us",
            "marketing-mid",
            [{"name": "Email", "type": "EmailAddress"}],
        )
        url = c._data_session.post.call_args[0][0]
        body = c._data_session.post.call_args[1]["json"]
        assert url == f"sites/{SITE_ID_NEW}/marketing-integration/forms"
        assert body == {
            "formName": "Contact Us",
            "memberIdentificationCode": "marketing-mid",
            "formFieldsList": {"formFields": [{"name": "Email", "type": "EmailAddress"}]},
        }
        await c.close()

    async def test_get_form(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {"id": FORM_ID}))
        await c.microsites.get_form(SITE_ID_NEW, FORM_ID)
        url = c._data_session.get.call_args[0][0]
        assert url == f"sites/{SITE_ID_NEW}/marketing-integration/forms/{FORM_ID}"
        await c.close()

    async def test_submit_form(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {"submitted": True}))
        await c.microsites.submit_form(SITE_ID_NEW, FORM_ID, [{"name": "Email", "value": "a@b.c"}])
        url = c._data_session.post.call_args[0][0]
        body = c._data_session.post.call_args[1]["json"]
        assert url == f"sites/{SITE_ID_NEW}/marketing-integration/forms/{FORM_ID}/data"
        assert body == {"formFieldsList": {"formFields": [{"name": "Email", "value": "a@b.c"}]}}
        await c.close()


class TestCMSContentSearchOperations:
    async def test_search(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.cms_content_search.search(
            SITE_ID_NEW,
            "shoes",
            language="en_US",
            page_size=50,
            page_token="abc",
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"sites/{SITE_ID_NEW}/search"
        assert params == {
            "queryTerm": "shoes",
            "language": "en_US",
            "pageSize": 50,
            "pageToken": "abc",
        }
        await c.close()


class TestNavigationMenuOperations:
    async def test_list_items(self):
        c = await _client(mock_get=_mock_response(200, {"menuItems": []}))
        await c.navigation_menu.list_items(
            COMMUNITY_ID,
            navigation_link_set_id="0kRxx0000004CTS",
            publish_status="Live",
            menu_item_types_to_skip=["Event", "SystemLink"],
            add_home_menu_item=True,
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == (f"communities/{COMMUNITY_ID}/navigation-menu/navigation-menu-items")
        assert params["navigationLinkSetId"] == "0kRxx0000004CTS"
        assert params["publishStatus"] == "Live"
        assert params["menuItemTypesToSkip"] == "Event,SystemLink"
        assert params["addHomeMenuItem"] is True
        await c.close()


class TestManagedTopicsOperations:
    async def test_list_managed_topics(self):
        c = await _client(mock_get=_mock_response(200, {"managedTopics": []}))
        await c.managed_topics.list_managed_topics(
            COMMUNITY_ID,
            managed_topic_type="Navigational",
            depth=8,
            page_size=50,
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == f"communities/{COMMUNITY_ID}/managed-topics"
        assert params == {
            "managedTopicType": "Navigational",
            "depth": 8,
            "pageSize": 50,
        }
        await c.close()

    async def test_create_managed_topic_by_name(self):
        c = await _client(mock_post=_mock_response(200, {"id": MANAGED_TOPIC_ID}))
        await c.managed_topics.create_managed_topic(
            COMMUNITY_ID,
            managed_topic_type="Navigational",
            name="Child Topic",
            parent_id="0mtR000000001KLIAY",
        )
        body = c._session.post.call_args[1]["json"]
        assert body == {
            "managedTopicType": "Navigational",
            "name": "Child Topic",
            "parentId": "0mtR000000001KLIAY",
        }
        await c.close()

    async def test_create_managed_topic_by_record(self):
        c = await _client(mock_post=_mock_response(200, {"id": MANAGED_TOPIC_ID}))
        await c.managed_topics.create_managed_topic(
            COMMUNITY_ID,
            managed_topic_type="Content",
            record_id=TOPIC_ID,
        )
        body = c._session.post.call_args[1]["json"]
        assert body == {
            "managedTopicType": "Content",
            "recordId": TOPIC_ID,
        }
        await c.close()

    async def test_create_managed_topic_requires_one(self):
        c = await _client()
        with pytest.raises(ValueError):
            await c.managed_topics.create_managed_topic(
                COMMUNITY_ID, managed_topic_type="Navigational"
            )
        await c.close()

    async def test_reorder_managed_topics(self):
        c = await _client(mock_patch=_mock_response(200, {"managedTopics": []}))
        positions = [
            {"managedTopicId": MANAGED_TOPIC_ID, "position": 0},
        ]
        await c.managed_topics.reorder_managed_topics(COMMUNITY_ID, positions)
        body = c._session.patch.call_args[1]["json"]
        assert body == {"managedTopicPositions": positions}
        await c.close()

    async def test_get_managed_topic(self):
        c = await _client(mock_get=_mock_response(200, {"id": MANAGED_TOPIC_ID}))
        await c.managed_topics.get_managed_topic(COMMUNITY_ID, MANAGED_TOPIC_ID)
        url = c._session.get.call_args[0][0]
        assert url == f"communities/{COMMUNITY_ID}/managed-topics/{MANAGED_TOPIC_ID}"
        await c.close()

    async def test_delete_managed_topic(self):
        c = await _client(mock_delete=_mock_response(204))
        assert await c.managed_topics.delete_managed_topic(COMMUNITY_ID, MANAGED_TOPIC_ID) == {}
        await c.close()


class TestNetworkDataCategoryOperations:
    async def test_get_tree(self):
        c = await _client(mock_get=_mock_response(200, {"groups": []}))
        await c.network_data_category.get_tree(COMMUNITY_ID)
        url = c._session.get.call_args[0][0]
        assert url == f"communities/{COMMUNITY_ID}/data-category/network-data-category"
        await c.close()

    async def test_replace_tree(self):
        c = await _client(mock_put=_mock_response(200, {"groups": []}))
        groups = [{"categoryGroupName": "Geographic", "rootCategory": {}}]
        await c.network_data_category.replace_tree(COMMUNITY_ID, groups)
        body = c._session.put.call_args[1]["json"]
        assert body == {"dataCategoryGroups": groups}
        await c.close()

    async def test_update_category(self):
        c = await _client(mock_patch=_mock_response(200, {"id": NETWORK_DATA_CATEGORY_ID}))
        await c.network_data_category.update_category(
            COMMUNITY_ID,
            NETWORK_DATA_CATEGORY_ID,
            label="Updated",
            description="new desc",
        )
        url = c._session.patch.call_args[0][0]
        params = c._session.patch.call_args[1]["params"]
        assert url == (
            f"communities/{COMMUNITY_ID}/network-data-category/{NETWORK_DATA_CATEGORY_ID}"
        )
        assert params == {"label": "Updated", "description": "new desc"}
        await c.close()

    async def test_get_child_categories(self):
        c = await _client(mock_get=_mock_response(200, {"categories": []}))
        await c.network_data_category.get_child_categories(
            COMMUNITY_ID,
            NETWORK_DATA_CATEGORY_ID,
            language="en_US",
            sort_order="Ascending",
        )
        url = c._session.get.call_args[0][0]
        assert url.endswith("/child-category")
        await c.close()

    async def test_get_parent_path(self):
        c = await _client(mock_get=_mock_response(200, {"categories": []}))
        await c.network_data_category.get_parent_path(
            COMMUNITY_ID, NETWORK_DATA_CATEGORY_ID, language="es"
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url.endswith("/parent-path")
        assert params == {"language": "es"}
        await c.close()

    async def test_get_articles(self):
        c = await _client(mock_get=_mock_response(200, {"articles": []}))
        await c.network_data_category.get_articles(
            COMMUNITY_ID, NETWORK_DATA_CATEGORY_ID, page_size=10
        )
        url = c._session.get.call_args[0][0]
        assert url.endswith("/knowledge-article")
        await c.close()

    async def test_get_catalog_items_site_scoped(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.network_data_category.get_catalog_items(
            NETWORK_DATA_CATEGORY_ID, community_id=COMMUNITY_ID
        )
        url = c._session.get.call_args[0][0]
        assert url == (
            f"communities/{COMMUNITY_ID}/network-data-category/"
            f"{NETWORK_DATA_CATEGORY_ID}/catalog-item"
        )
        await c.close()

    async def test_get_catalog_items_org_scoped(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.network_data_category.get_catalog_items(NETWORK_DATA_CATEGORY_ID)
        url = c._session.get.call_args[0][0]
        assert url == (f"network-data-category/{NETWORK_DATA_CATEGORY_ID}/catalog-item")
        await c.close()

    async def test_list_category_groups(self):
        c = await _client(mock_get=_mock_response(200, {"groups": []}))
        await c.network_data_category.list_category_groups()
        assert c._session.get.call_args[0][0] == "data-category/category-group"
        await c.close()


# ---------------------------------------------------------------------------
# Batch 4 — Data / integration
# ---------------------------------------------------------------------------


class TestFilesConnectRepositoryOperations:
    async def test_list_repositories(self):
        c = await _client(mock_get=_mock_response(200, {"repositories": []}))
        await c.content_hub.list_repositories(can_browse_only=True, page_size=10)
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == "content-hub/repositories"
        assert params == {"canBrowseOnly": True, "pageSize": 10}
        await c.close()

    async def test_list_repositories_community_scoped(self):
        c = await _client(mock_get=_mock_response(200, {"repositories": []}))
        await c.content_hub.list_repositories(community_id=COMMUNITY_ID)
        url = c._session.get.call_args[0][0]
        assert url == f"communities/{COMMUNITY_ID}/content-hub/repositories"
        await c.close()

    async def test_get_repository(self):
        c = await _client(mock_get=_mock_response(200, {"id": REPOSITORY_ID}))
        await c.content_hub.get_repository(REPOSITORY_ID)
        url = c._session.get.call_args[0][0]
        assert url == f"content-hub/repositories/{REPOSITORY_ID}"
        await c.close()

    async def test_get_directory_entries(self):
        c = await _client(mock_get=_mock_response(200, {"entries": []}))
        await c.content_hub.get_repository_directory_entries(REPOSITORY_ID)
        url = c._session.get.call_args[0][0]
        assert url.endswith("/directory-entries")
        await c.close()

    async def test_get_repository_file(self):
        c = await _client(mock_get=_mock_response(200, {"id": REPOSITORY_FILE_ID}))
        await c.content_hub.get_repository_file(
            REPOSITORY_ID,
            REPOSITORY_FILE_ID,
            include_external_file_permissions_info=True,
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url == (f"content-hub/repositories/{REPOSITORY_ID}/files/{REPOSITORY_FILE_ID}")
        assert params == {"includeExternalFilePermissionsInfo": True}
        await c.close()

    async def test_update_repository_file(self):
        c = await _client(mock_patch=_mock_response(200, {"id": REPOSITORY_FILE_ID}))
        await c.content_hub.update_repository_file(
            REPOSITORY_ID,
            REPOSITORY_FILE_ID,
            item_type_id=REPOSITORY_ITEM_TYPE_ID,
            fields=[{"name": "name", "value": "new.txt"}],
        )
        body = c._session.patch.call_args[1]["json"]
        assert body["itemTypeId"] == REPOSITORY_ITEM_TYPE_ID
        assert body["fields"][0]["value"] == "new.txt"
        await c.close()

    async def test_get_repository_file_content(self):
        c = await _client(mock_get=_mock_response(200, content=b"bytes"))
        result = await c.content_hub.get_repository_file_content(REPOSITORY_ID, REPOSITORY_FILE_ID)
        assert result == b"bytes"
        await c.close()

    async def test_get_repository_file_previews(self):
        c = await _client(mock_get=_mock_response(200, {"previews": []}))
        await c.content_hub.get_repository_file_previews(REPOSITORY_ID, REPOSITORY_FILE_ID)
        url = c._session.get.call_args[0][0]
        assert url.endswith("/previews")
        await c.close()

    async def test_get_repository_file_preview_with_pages(self):
        c = await _client(mock_get=_mock_response(200, {"pages": []}))
        await c.content_hub.get_repository_file_preview(
            REPOSITORY_ID,
            REPOSITORY_FILE_ID,
            "pdf",
            start_page_number=1,
            end_page_number=3,
        )
        url = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert url.endswith("/previews/pdf")
        assert params == {"startPageNumber": 1, "endPageNumber": 3}
        await c.close()

    async def test_get_repository_folder(self):
        c = await _client(mock_get=_mock_response(200, {"id": REPOSITORY_FOLDER_ID}))
        await c.content_hub.get_repository_folder(REPOSITORY_ID, REPOSITORY_FOLDER_ID)
        url = c._session.get.call_args[0][0]
        assert url == (f"content-hub/repositories/{REPOSITORY_ID}/folders/{REPOSITORY_FOLDER_ID}")
        await c.close()

    async def test_get_allowed_item_types(self):
        c = await _client(mock_get=_mock_response(200, {"itemTypes": []}))
        await c.content_hub.get_allowed_item_types(
            REPOSITORY_ID, REPOSITORY_FOLDER_ID, filter_type="FilesOnly"
        )
        params = c._session.get.call_args[1]["params"]
        assert params == {"filter": "FilesOnly"}
        await c.close()

    async def test_get_repository_folder_items(self):
        c = await _client(mock_get=_mock_response(200, {"items": []}))
        await c.content_hub.get_repository_folder_items(
            REPOSITORY_ID, REPOSITORY_FOLDER_ID, page=1, page_size=50
        )
        params = c._session.get.call_args[1]["params"]
        assert params == {"page": 1, "pageSize": 50}
        await c.close()

    async def test_create_repository_folder_item(self):
        c = await _client(mock_post=_mock_response(200, {"id": "x"}))
        await c.content_hub.create_repository_folder_item(
            REPOSITORY_ID,
            REPOSITORY_FOLDER_ID,
            item_type_id=REPOSITORY_ITEM_TYPE_ID,
            fields=[{"name": "name", "value": "new.txt"}],
        )
        body = c._session.post.call_args[1]["json"]
        assert body["itemTypeId"] == REPOSITORY_ITEM_TYPE_ID
        await c.close()

    async def test_get_item_type(self):
        c = await _client(mock_get=_mock_response(200, {"id": REPOSITORY_ITEM_TYPE_ID}))
        await c.content_hub.get_item_type(REPOSITORY_ID, REPOSITORY_ITEM_TYPE_ID)
        url = c._session.get.call_args[0][0]
        assert url.endswith(f"/item-types/{REPOSITORY_ITEM_TYPE_ID}")
        await c.close()

    async def test_get_item_permissions(self):
        c = await _client(mock_get=_mock_response(200, {"permissions": []}))
        await c.content_hub.get_item_permissions(REPOSITORY_ID, REPOSITORY_FILE_ID)
        url = c._session.get.call_args[0][0]
        assert url.endswith("/permissions")
        await c.close()

    async def test_update_item_permissions(self):
        c = await _client(mock_patch=_mock_response(200, {"permissions": []}))
        await c.content_hub.update_item_permissions(
            REPOSITORY_ID,
            REPOSITORY_FILE_ID,
            permissions_to_apply=[
                {"directoryEntryId": "Anyone", "permissionTypesIds": ["CanView"]}
            ],
        )
        body = c._session.patch.call_args[1]["json"]
        assert "permissionsToApply" in body
        assert "permissionsToRemove" not in body
        await c.close()

    async def test_update_item_permissions_requires_one(self):
        c = await _client()
        with pytest.raises(ValueError):
            await c.content_hub.update_item_permissions(REPOSITORY_ID, REPOSITORY_FILE_ID)
        await c.close()

    async def test_get_permission_types(self):
        c = await _client(mock_get=_mock_response(200, {"types": []}))
        await c.content_hub.get_permission_types(REPOSITORY_ID, REPOSITORY_FILE_ID)
        url = c._session.get.call_args[0][0]
        assert url.endswith("/permissions/types")
        await c.close()

    async def test_get_repository_for_item(self):
        c = await _client(mock_get=_mock_response(200, {"id": REPOSITORY_ID}))
        await c.content_hub.get_repository_for_item(REPOSITORY_FILE_ID)
        url = c._session.get.call_args[0][0]
        assert url == f"content-hub/items/{REPOSITORY_FILE_ID}/repository"
        await c.close()


class TestCustomDomainOperations:
    async def test_list_domains(self):
        c = await _client(mock_get=_mock_response(200, {"domains": []}))
        await c.custom_domain.list_domains()
        url = c._session.get.call_args[0][0]
        assert url == "custom-domain/domains"
        await c.close()

    async def test_get_domain(self):
        c = await _client(mock_get=_mock_response(200, {"id": CUSTOM_DOMAIN_ID}))
        await c.custom_domain.get_domain(CUSTOM_DOMAIN_ID)
        url = c._session.get.call_args[0][0]
        assert url == f"custom-domain/domains/{CUSTOM_DOMAIN_ID}"
        await c.close()

    async def test_get_domain_id(self):
        c = await _client(mock_get=_mock_response(200, {"id": "x"}))
        await c.custom_domain.get_domain_id("www.example.com")
        url = c._session.get.call_args[0][0]
        assert url == "custom-domain/domains/www.example.com/domainId"
        await c.close()

    async def test_get_expected_cname(self):
        c = await _client(mock_get=_mock_response(200, {"cname": "x"}))
        await c.custom_domain.get_expected_cname("www.example.com")
        url = c._session.get.call_args[0][0]
        assert url.endswith("/expected-cname")
        await c.close()

    async def test_get_expected_cdn_cname(self):
        c = await _client(mock_get=_mock_response(200, {"cname": "x"}))
        await c.custom_domain.get_expected_cdn_cname("www.example.com")
        url = c._session.get.call_args[0][0]
        assert url.endswith("/expected-cdn-validation-cname")
        await c.close()

    async def test_list_custom_urls(self):
        c = await _client(mock_get=_mock_response(200, {"customUrls": []}))
        await c.custom_domain.list_custom_urls(CUSTOM_DOMAIN_ID)
        url = c._session.get.call_args[0][0]
        assert url == f"custom-domain/domains/{CUSTOM_DOMAIN_ID}/custom-urls"
        await c.close()

    async def test_get_custom_url(self):
        c = await _client(mock_get=_mock_response(200, {"id": CUSTOM_URL_ID}))
        await c.custom_domain.get_custom_url(CUSTOM_DOMAIN_ID, CUSTOM_URL_ID)
        url = c._session.get.call_args[0][0]
        assert url == (f"custom-domain/domains/{CUSTOM_DOMAIN_ID}/custom-urls/{CUSTOM_URL_ID}")
        await c.close()

    async def test_get_pending_configuration(self):
        c = await _client(mock_get=_mock_response(200, {"config": {}}))
        await c.custom_domain.get_pending_configuration(CUSTOM_DOMAIN_ID)
        url = c._session.get.call_args[0][0]
        assert url.endswith("/pending-configuration")
        await c.close()

    async def test_list_site_custom_urls(self):
        c = await _client(mock_get=_mock_response(200, {"customUrls": []}))
        await c.custom_domain.list_site_custom_urls(COMMUNITY_ID)
        url = c._session.get.call_args[0][0]
        assert url == (f"custom-domain/domains/sites/{COMMUNITY_ID}/custom-urls")
        await c.close()


class TestDuplicateOperations:
    async def test_get_directory(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.duplicate.get_directory()
        assert c._data_session.get.call_args[0][0] == "dedupe"
        await c.close()

    async def test_list_job_definitions(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.duplicate.list_job_definitions()
        assert c._data_session.get.call_args[0][0] == "dedupe/job-definitions"
        await c.close()

    async def test_get_job_definition(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.duplicate.get_job_definition(DUPLICATE_JOB_DEF_ID)
        assert c._data_session.get.call_args[0][0] == (
            f"dedupe/job-definitions/{DUPLICATE_JOB_DEF_ID}"
        )
        await c.close()

    async def test_list_jobs(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.duplicate.list_jobs()
        assert c._data_session.get.call_args[0][0] == "dedupe/jobs"
        await c.close()

    async def test_run_job(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.duplicate.run_job(DUPLICATE_JOB_DEF_ID)
        body = c._data_session.post.call_args[1]["json"]
        assert body == {"duplicateJobDefId": DUPLICATE_JOB_DEF_ID}
        await c.close()

    async def test_get_job(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.duplicate.get_job(DUPLICATE_JOB_ID)
        assert c._data_session.get.call_args[0][0] == f"dedupe/jobs/{DUPLICATE_JOB_ID}"
        await c.close()

    async def test_cancel_job(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.patch = AsyncMock(return_value=_mock_response(200, {}))
        await c.duplicate.cancel_job(DUPLICATE_JOB_ID)
        body = c._data_session.patch.call_args[1]["json"]
        assert body == {"status": "Canceled"}
        await c.close()

    async def test_delete_job_results(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        assert await c.duplicate.delete_job_results(DUPLICATE_JOB_ID) == {}
        await c.close()


class TestCleanOperations:
    async def test_list_data_services(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.clean.list_data_services()
        assert c._data_session.get.call_args[0][0] == "clean/data-services"
        await c.close()

    async def test_get_data_service_metrics(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.clean.get_data_service_metrics(DATA_SERVICE_ID)
        assert c._data_session.get.call_args[0][0] == (
            f"clean/data-services/{DATA_SERVICE_ID}/metrics"
        )
        await c.close()

    async def test_get_rule_statuses(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.clean.get_rule_statuses(COMMUNITY_ID)
        assert c._data_session.get.call_args[0][0] == (f"clean/{COMMUNITY_ID}/rules/statuses")
        await c.close()


class TestDataIntegrationOperations:
    async def test_list_licensed_objects(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.data_integration.list_licensed_objects()
        assert c._data_session.get.call_args[0][0] == ("data-integration/licensed-objects")
        await c.close()

    async def test_get_contract_credit(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.data_integration.get_contract_credit("Dun_Bradstreet__x")
        assert c._data_session.get.call_args[0][0] == (
            "data-integration/licensed-objects/Dun_Bradstreet__x/contracts/current"
        )
        await c.close()


class TestNamedCredentialsOperations:
    async def test_get_credential(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.get_credential(
            external_credential=EC_DEVELOPER_NAME,
            principal_type="NamedPrincipal",
            principal_name="principalA",
        )
        params = c._data_session.get.call_args[1]["params"]
        assert params == {
            "externalCredential": EC_DEVELOPER_NAME,
            "principalType": "NamedPrincipal",
            "principalName": "principalA",
        }
        await c.close()

    async def test_create_credential_with_refresh(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.create_credential(
            {"externalCredential": EC_DEVELOPER_NAME}, action="Refresh"
        )
        params = c._data_session.post.call_args[1]["params"]
        assert params == {"action": "Refresh"}
        await c.close()

    async def test_replace_credential(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.put = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.replace_credential({"externalCredential": EC_DEVELOPER_NAME})
        url = c._data_session.put.call_args[0][0]
        assert url == "named-credentials/credential"
        await c.close()

    async def test_update_credential(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.patch = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.update_credential({"x": 1})
        url = c._data_session.patch.call_args[0][0]
        assert url == "named-credentials/credential"
        await c.close()

    async def test_delete_credential_with_params(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        await c.named_credentials.delete_credential(
            external_credential=EC_DEVELOPER_NAME,
            principal_type="NamedPrincipal",
            principal_name="principalA",
            authentication_parameters=["apiKey", "apiSecret"],
        )
        params = c._data_session.delete.call_args[1]["params"]
        assert params["authenticationParameters"] == "apiKey,apiSecret"
        await c.close()

    async def test_get_oauth_url(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.get_oauth_url({"externalCredential": EC_DEVELOPER_NAME})
        url = c._data_session.post.call_args[0][0]
        assert url == "named-credentials/credential/auth-url/o-auth"
        await c.close()

    async def test_list_external_credentials(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.list_external_credentials()
        url = c._data_session.get.call_args[0][0]
        assert url == "named-credentials/external-credentials"
        await c.close()

    async def test_create_external_credential(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.create_external_credential({"developerName": EC_DEVELOPER_NAME})
        url = c._data_session.post.call_args[0][0]
        assert url == "named-credentials/external-credentials"
        await c.close()

    async def test_get_external_credential(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.get_external_credential(EC_DEVELOPER_NAME)
        url = c._data_session.get.call_args[0][0]
        assert url == f"named-credentials/external-credentials/{EC_DEVELOPER_NAME}"
        await c.close()

    async def test_update_external_credential(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.put = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.update_external_credential(
            EC_DEVELOPER_NAME, {"masterLabel": "new"}
        )
        url = c._data_session.put.call_args[0][0]
        assert url == f"named-credentials/external-credentials/{EC_DEVELOPER_NAME}"
        await c.close()

    async def test_delete_external_credential(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        assert await c.named_credentials.delete_external_credential(EC_DEVELOPER_NAME) == {}
        await c.close()

    async def test_list_named_credentials(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.list_named_credentials()
        url = c._data_session.get.call_args[0][0]
        assert url == "named-credentials/named-credential-setup"
        await c.close()

    async def test_create_named_credential(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.create_named_credential({"developerName": NC_DEVELOPER_NAME})
        url = c._data_session.post.call_args[0][0]
        assert url == "named-credentials/named-credential-setup"
        await c.close()

    async def test_get_named_credential(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.get_named_credential(NC_DEVELOPER_NAME)
        url = c._data_session.get.call_args[0][0]
        assert url == f"named-credentials/named-credential-setup/{NC_DEVELOPER_NAME}"
        await c.close()

    async def test_update_named_credential(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.put = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.update_named_credential(NC_DEVELOPER_NAME, {"masterLabel": "x"})
        url = c._data_session.put.call_args[0][0]
        assert url == f"named-credentials/named-credential-setup/{NC_DEVELOPER_NAME}"
        await c.close()

    async def test_delete_named_credential(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        assert await c.named_credentials.delete_named_credential(NC_DEVELOPER_NAME) == {}
        await c.close()

    async def test_list_identity_providers(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.list_external_auth_identity_providers()
        url = c._data_session.get.call_args[0][0]
        assert url == "named-credentials/external-auth-identity-providers"
        await c.close()

    async def test_create_identity_provider(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.create_external_auth_identity_provider(
            {"fullName": IDP_FULL_NAME}
        )
        url = c._data_session.post.call_args[0][0]
        assert url == "named-credentials/external-auth-identity-providers"
        await c.close()

    async def test_get_identity_provider(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.get_external_auth_identity_provider(IDP_FULL_NAME)
        url = c._data_session.get.call_args[0][0]
        assert url == (f"named-credentials/external-auth-identity-providers/{IDP_FULL_NAME}")
        await c.close()

    async def test_update_identity_provider(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.put = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.update_external_auth_identity_provider(
            IDP_FULL_NAME, {"label": "x"}
        )
        url = c._data_session.put.call_args[0][0]
        assert url == (f"named-credentials/external-auth-identity-providers/{IDP_FULL_NAME}")
        await c.close()

    async def test_delete_identity_provider(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        assert await c.named_credentials.delete_external_auth_identity_provider(IDP_FULL_NAME) == {}
        await c.close()

    async def test_get_identity_provider_credentials(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.get_external_auth_identity_provider_credentials(IDP_FULL_NAME)
        url = c._data_session.get.call_args[0][0]
        assert url == (
            f"named-credentials/external-auth-identity-provider-credentials/{IDP_FULL_NAME}"
        )
        await c.close()

    async def test_create_identity_provider_credentials(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.create_external_auth_identity_provider_credentials(
            IDP_FULL_NAME,
            [{"credentialName": "clientId", "credentialValue": "abc"}],
        )
        body = c._data_session.post.call_args[1]["json"]
        assert body == {"credentials": [{"credentialName": "clientId", "credentialValue": "abc"}]}
        await c.close()

    async def test_replace_identity_provider_credentials(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.put = AsyncMock(return_value=_mock_response(200, {}))
        await c.named_credentials.replace_external_auth_identity_provider_credentials(
            IDP_FULL_NAME,
            [{"credentialName": "clientId", "credentialValue": "abc"}],
        )
        body = c._data_session.put.call_args[1]["json"]
        assert "credentials" in body
        await c.close()


# ---------------------------------------------------------------------------
# PromptTemplatesOperations (Batch 5)
# ---------------------------------------------------------------------------


class TestPromptTemplatesOperations:
    async def test_list_no_filters(self):
        c = await _einstein_client(mock_get=_mock_response(200, {"records": []}))
        await c.prompt_templates.list_prompt_templates()
        path = c._einstein_session.get.call_args[0][0]
        params = c._einstein_session.get.call_args[1]["params"]
        assert path == "prompt-templates"
        assert params == {}
        await c.close()

    async def test_list_with_filters(self):
        c = await _einstein_client(mock_get=_mock_response(200, {"records": []}))
        await c.prompt_templates.list_prompt_templates(
            fields=["createdDate", "developerName"],
            is_active=True,
            offset=10,
            page_limit=25,
            query="email",
            related_entity="Contact",
            sort_by="createdDate",
            template_type="einstein_gpt__salesEmail",
        )
        params = c._einstein_session.get.call_args[1]["params"]
        assert params == {
            "fields": "createdDate,developerName",
            "isActive": "true",
            "offset": 10,
            "pageLimit": 25,
            "query": "email",
            "relatedEntity": "Contact",
            "sortBy": "createdDate",
            "type": "einstein_gpt__salesEmail",
        }
        await c.close()

    async def test_generate_minimum(self):
        c = await _einstein_client(mock_post=_mock_response(200, {}))
        await c.prompt_templates.generate(
            PROMPT_TEMPLATE_DEV_NAME,
            input_params={"valueMap": {"Input:S1": {"value": "x"}}},
            additional_config={"applicationName": "Promo"},
        )
        path = c._einstein_session.post.call_args[0][0]
        body = c._einstein_session.post.call_args[1]["json"]
        assert path == f"prompt-templates/{PROMPT_TEMPLATE_DEV_NAME}/generations"
        assert body == {
            "isPreview": False,
            "inputParams": {"valueMap": {"Input:S1": {"value": "x"}}},
            "additionalConfig": {"applicationName": "Promo"},
        }
        await c.close()

    async def test_generate_full(self):
        c = await _einstein_client(mock_post=_mock_response(200, {}))
        await c.prompt_templates.generate(
            PROMPT_TEMPLATE_DEV_NAME,
            input_params={"valueMap": {}},
            additional_config={"applicationName": "Promo"},
            is_preview=True,
            citation_mode="post_generation",
            output_language="en_US",
            tags={"valueMap": {"tag1": {"value": "v"}}},
        )
        body = c._einstein_session.post.call_args[1]["json"]
        assert body["isPreview"] is True
        assert body["citationMode"] == "post_generation"
        assert body["outputLanguage"] == "en_US"
        assert body["tags"] == {"valueMap": {"tag1": {"value": "v"}}}
        await c.close()


# ---------------------------------------------------------------------------
# EinsteinRecommendationsOperations (Batch 5)
# ---------------------------------------------------------------------------


class TestEinsteinRecommendationsOperations:
    async def test_article_metrics(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.einstein_recommendations.get_article_recommendations_metrics()
        path = c._session.get.call_args[0][0]
        assert path == "article-recommendations/metrics/runtime/case"
        await c.close()

    async def test_reply_metrics(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.einstein_recommendations.get_reply_recommendations_metrics()
        path = c._session.get.call_args[0][0]
        assert path == "reply-recommendations/metrics/runtime/chat"
        await c.close()


# ---------------------------------------------------------------------------
# NextBestActionOperations (Batch 5)
# ---------------------------------------------------------------------------


class TestNextBestActionOperations:
    async def test_get_recommendation(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.next_best_action.get_recommendation(RECOMMENDATION_ID)
        path = c._session.get.call_args[0][0]
        assert path == f"recommendations/{RECOMMENDATION_ID}"
        await c.close()

    async def test_execute_strategy_minimal(self):
        c = await _client(mock_post=_mock_response(200, {}))
        await c.next_best_action.execute_strategy(STRATEGY_NAME)
        path = c._session.post.call_args[0][0]
        body = c._session.post.call_args[1]["json"]
        assert path == f"recommendation-strategies/{STRATEGY_NAME}/recommendations"
        assert body == {}
        await c.close()

    async def test_execute_strategy_full(self):
        c = await _client(mock_post=_mock_response(200, {}))
        await c.next_best_action.execute_strategy(
            STRATEGY_NAME,
            context_record_id=CONTEXT_RECORD_ID,
            max_results=5,
            strategy_context={"k1": "v1", "k2": "v2"},
            debug_trace=True,
        )
        body = c._session.post.call_args[1]["json"]
        assert body["maxResults"] == 5
        assert body["strategyContext"] == {"k1": "v1", "k2": "v2"}
        assert body["debugTrace"] is True
        assert "contextRecordId" in body
        await c.close()

    async def test_list_reactions_no_params(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.next_best_action.list_reactions()
        path = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert path == "recommendation-strategies/reactions"
        assert params == {}
        await c.close()

    async def test_list_reactions_with_params(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.next_best_action.list_reactions(
            context_record_id=CONTEXT_RECORD_ID,
            page=1,
            page_size=50,
            target_id=RECOMMENDATION_ID,
        )
        params = c._session.get.call_args[1]["params"]
        assert params["page"] == 1
        assert params["pageSize"] == 50
        assert "contextRecordId" in params
        assert "targetId" in params
        await c.close()

    async def test_record_reaction_minimum(self):
        c = await _client(mock_post=_mock_response(200, {}))
        await c.next_best_action.record_reaction(
            reaction_type="Accepted",
            strategy_name=STRATEGY_NAME,
            target_action_name="UpgradeService",
            target_id=RECOMMENDATION_ID,
        )
        path = c._session.post.call_args[0][0]
        body = c._session.post.call_args[1]["json"]
        assert path == "recommendation-strategies/reactions"
        assert body["reactionType"] == "Accepted"
        assert body["strategyName"] == STRATEGY_NAME
        assert body["targetActionName"] == "UpgradeService"
        assert body["targetId"] == RECOMMENDATION_ID
        await c.close()

    async def test_record_reaction_full(self):
        c = await _client(mock_post=_mock_response(200, {}))
        await c.next_best_action.record_reaction(
            reaction_type="Rejected",
            strategy_name=STRATEGY_NAME,
            target_action_name="UpgradeService",
            target_id=RECOMMENDATION_ID,
            context_record_id=CONTEXT_RECORD_ID,
            on_behalf_of_id="001xx000003DGQW",
            execution_id="exec1",
            external_id="ext-1",
            target_action_id="0ADxx0000004CTYGA2",
            ai_model="m",
            recommendation_mode="rm",
            recommendation_score=0.9,
        )
        body = c._session.post.call_args[1]["json"]
        assert body["executionId"] == "exec1"
        assert body["externalId"] == "ext-1"
        assert body["recommendationScore"] == 0.9
        assert body["recommendationMode"] == "rm"
        assert body["aiModel"] == "m"
        assert "targetActionId" in body
        assert "onBehalfOfId" in body
        await c.close()

    async def test_get_reaction(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.next_best_action.get_reaction(REACTION_ID)
        path = c._session.get.call_args[0][0]
        assert path == f"recommendation-strategies/reactions/{REACTION_ID}"
        await c.close()

    async def test_delete_reaction(self):
        c = await _client(mock_delete=_mock_response(204))
        await c.next_best_action.delete_reaction(REACTION_ID)
        path = c._session.delete.call_args[0][0]
        assert path == f"recommendation-strategies/reactions/{REACTION_ID}"
        await c.close()


# ---------------------------------------------------------------------------
# SearchOperations (Batch 5)
# ---------------------------------------------------------------------------


class TestSearchOperations:
    async def test_search_result_groups(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.search.search_result_groups("issue")
        path = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert path == "search/sobjects/result-groups"
        assert params == {"q": "issue"}
        await c.close()

    async def test_search_result_groups_with_options(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.search.search_result_groups(
            "issue",
            configuration_name="MyConfig",
            highlights=True,
        )
        params = c._session.get.call_args[1]["params"]
        assert params == {
            "q": "issue",
            "configurationName": "MyConfig",
            "highlights": "true",
        }
        await c.close()

    async def test_search_object_results_minimum(self):
        c = await _client(mock_post=_mock_response(200, {}))
        await c.search.search_object_results("Knowledge__kav", q="overview")
        path = c._session.post.call_args[0][0]
        body = c._session.post.call_args[1]["json"]
        assert path == "search/sobjects/Knowledge__kav/results"
        assert body == {"q": "overview"}
        await c.close()

    async def test_search_object_results_full(self):
        c = await _client(mock_post=_mock_response(200, {}))
        await c.search.search_object_results(
            "Knowledge__kav",
            q="overview",
            configuration_name="cfg",
            data_categories=[{"groupName": "g", "operator": "Below", "categories": ["c"]}],
            display_fields=["Title"],
            filters=[{"field": "Language", "operator": "EqOp", "values": ["en_US"]}],
            highlights=True,
            offset=0,
            order_by=[{"field": "LastModifiedDate"}],
            page_size=50,
            spellcheck=False,
        )
        body = c._session.post.call_args[1]["json"]
        assert body["configurationName"] == "cfg"
        assert body["highlights"] is True
        assert body["spellcheck"] is False
        assert body["pageSize"] == 50
        assert body["displayFields"] == ["Title"]
        assert body["orderBy"] == [{"field": "LastModifiedDate"}]
        assert "filters" in body
        assert "dataCategories" in body
        await c.close()

    async def test_search_answer(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.search.search_answer("how to sign")
        path = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert path == "search/sobjects/answer"
        assert params == {"q": "how to sign"}
        await c.close()

    async def test_search_object_answer(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.search.search_object_answer(
            "Knowledge__kav",
            q="how to sign",
            display_fields=["Title", "Summary"],
        )
        path = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert path == "search/sobjects/Knowledge__kav/answer"
        assert params == {"q": "how to sign", "displayFields": "Title,Summary"}
        await c.close()


# ---------------------------------------------------------------------------
# PersonalizationAudiencesOperations (Batch 6)
# ---------------------------------------------------------------------------


class TestPersonalizationAudiencesOperations:
    async def test_list_audiences_no_params(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.personalization_audiences.list_audiences(COMMUNITY_ID)
        path = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert path == f"communities/{COMMUNITY_ID}/personalization/audiences"
        assert params == {}
        await c.close()

    async def test_list_audiences_with_params(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.personalization_audiences.list_audiences(
            COMMUNITY_ID,
            domain="acme",
            include_audience_criteria=True,
            ip_address="10.0.0.1",
            publish_status="Draft",
            target_types=["ExperienceVariation", "Topic"],
        )
        params = c._session.get.call_args[1]["params"]
        assert params == {
            "domain": "acme",
            "includeAudienceCriteria": "true",
            "ipAddress": "10.0.0.1",
            "publishStatus": "Draft",
            "targetTypes": "ExperienceVariation,Topic",
        }
        await c.close()

    async def test_create_audience(self):
        c = await _client(mock_post=_mock_response(200, {}))
        await c.personalization_audiences.create_audience(
            COMMUNITY_ID,
            name="Aud1",
            criteria=[{"criterionNumber": 1}],
            formula_filter_type="CustomLogicMatches",
            custom_formula="1",
        )
        body = c._session.post.call_args[1]["json"]
        assert body == {
            "name": "Aud1",
            "criteria": [{"criterionNumber": 1}],
            "formulaFilterType": "CustomLogicMatches",
            "customFormula": "1",
        }
        await c.close()

    async def test_get_audiences_batch(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.personalization_audiences.get_audiences_batch(COMMUNITY_ID, [AUDIENCE_ID])
        path = c._session.get.call_args[0][0]
        assert path == (f"communities/{COMMUNITY_ID}/personalization/audiences/batch/{AUDIENCE_ID}")
        await c.close()

    async def test_get_audience(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.personalization_audiences.get_audience(
            COMMUNITY_ID, AUDIENCE_ID, include_audience_criteria=True
        )
        path = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert path == (f"communities/{COMMUNITY_ID}/personalization/audiences/{AUDIENCE_ID}")
        assert params == {"includeAudienceCriteria": "true"}
        await c.close()

    async def test_update_audience(self):
        c = await _client(mock_patch=_mock_response(200, {}))
        await c.personalization_audiences.update_audience(COMMUNITY_ID, AUDIENCE_ID, name="Updated")
        body = c._session.patch.call_args[1]["json"]
        assert body == {"name": "Updated"}
        await c.close()

    async def test_delete_audience(self):
        c = await _client(mock_delete=_mock_response(204))
        await c.personalization_audiences.delete_audience(COMMUNITY_ID, AUDIENCE_ID)
        path = c._session.delete.call_args[0][0]
        assert path == (f"communities/{COMMUNITY_ID}/personalization/audiences/{AUDIENCE_ID}")
        await c.close()

    async def test_list_targets(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.personalization_audiences.list_targets(
            COMMUNITY_ID,
            group_names=["g1", "g2"],
            include_all_matching_targets_within_group=True,
            target_types=["ExperienceVariation"],
        )
        params = c._session.get.call_args[1]["params"]
        assert params["groupNames"] == "g1,g2"
        assert params["includeAllMatchingTargetsWithinGroup"] == "true"
        assert params["targetTypes"] == "ExperienceVariation"
        await c.close()

    async def test_create_targets(self):
        c = await _client(mock_post=_mock_response(200, {}))
        await c.personalization_audiences.create_targets(
            COMMUNITY_ID,
            [{"audienceId": AUDIENCE_ID, "priority": 1}],
        )
        body = c._session.post.call_args[1]["json"]
        assert body == {"targets": [{"audienceId": AUDIENCE_ID, "priority": 1}]}
        await c.close()

    async def test_update_targets(self):
        c = await _client(mock_patch=_mock_response(200, {}))
        await c.personalization_audiences.update_targets(
            COMMUNITY_ID,
            [{"targetId": TARGET_ID, "priority": 2}],
        )
        body = c._session.patch.call_args[1]["json"]
        assert "targets" in body
        await c.close()

    async def test_get_targets_batch(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.personalization_audiences.get_targets_batch(COMMUNITY_ID, [TARGET_ID])
        path = c._session.get.call_args[0][0]
        assert path == (f"communities/{COMMUNITY_ID}/personalization/targets/batch/{TARGET_ID}")
        await c.close()

    async def test_get_target(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.personalization_audiences.get_target(COMMUNITY_ID, TARGET_ID)
        path = c._session.get.call_args[0][0]
        assert path == (f"communities/{COMMUNITY_ID}/personalization/targets/{TARGET_ID}")
        await c.close()

    async def test_delete_target(self):
        c = await _client(mock_delete=_mock_response(204))
        await c.personalization_audiences.delete_target(COMMUNITY_ID, TARGET_ID)
        path = c._session.delete.call_args[0][0]
        assert path == (f"communities/{COMMUNITY_ID}/personalization/targets/{TARGET_ID}")
        await c.close()


# ---------------------------------------------------------------------------
# PersonalizationEngagementSignalsOperations (Batch 6)
# ---------------------------------------------------------------------------


class TestPersonalizationEngagementSignalsOperations:
    async def test_list_engagement_signals_no_params(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.personalization_engagement_signals.list_engagement_signals()
        path = c._data_session.get.call_args[0][0]
        params = c._data_session.get.call_args[1]["params"]
        assert path == "personalization/engagement-signals"
        assert params == {}
        await c.close()

    async def test_list_engagement_signals_with_params(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.personalization_engagement_signals.list_engagement_signals(
            dataspace_name="default",
            profile_data_graph_name="pdg",
            limit=25,
            offset=0,
        )
        params = c._data_session.get.call_args[1]["params"]
        assert params == {
            "dataspaceName": "default",
            "profileDataGraphName": "pdg",
            "limit": 25,
            "offset": 0,
        }
        await c.close()

    async def test_create_engagement_signal(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.personalization_engagement_signals.create_engagement_signal({"name": "Sig"})
        path = c._data_session.post.call_args[0][0]
        assert path == "personalization/engagement-signals"
        await c.close()

    async def test_get_engagement_signal(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.personalization_engagement_signals.get_engagement_signal(ENGAGEMENT_SIGNAL_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == f"personalization/engagement-signals/{ENGAGEMENT_SIGNAL_ID}"
        await c.close()

    async def test_delete_engagement_signal(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        await c.personalization_engagement_signals.delete_engagement_signal(ENGAGEMENT_SIGNAL_ID)
        path = c._data_session.delete.call_args[0][0]
        assert path == f"personalization/engagement-signals/{ENGAGEMENT_SIGNAL_ID}"
        await c.close()

    async def test_create_metric(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.personalization_engagement_signals.create_engagement_signal_metric(
            ENGAGEMENT_SIGNAL_ID, {"name": "m"}
        )
        path = c._data_session.post.call_args[0][0]
        assert path == (f"personalization/engagement-signals/{ENGAGEMENT_SIGNAL_ID}/metrics")
        await c.close()

    async def test_delete_metric(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        await c.personalization_engagement_signals.delete_engagement_signal_metric(
            ENGAGEMENT_SIGNAL_ID, "metric1"
        )
        path = c._data_session.delete.call_args[0][0]
        assert path == (
            f"personalization/engagement-signals/{ENGAGEMENT_SIGNAL_ID}/metrics/metric1"
        )
        await c.close()

    async def test_create_compound_metric(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.personalization_engagement_signals.create_compound_metric({"name": "cm"})
        path = c._data_session.post.call_args[0][0]
        assert path == "personalization/compound-metrics"
        await c.close()

    async def test_get_compound_metric(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.personalization_engagement_signals.get_compound_metric(COMPOUND_METRIC_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == f"personalization/compound-metrics/{COMPOUND_METRIC_ID}"
        await c.close()

    async def test_delete_compound_metric(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        await c.personalization_engagement_signals.delete_compound_metric(COMPOUND_METRIC_ID)
        path = c._data_session.delete.call_args[0][0]
        assert path == f"personalization/compound-metrics/{COMPOUND_METRIC_ID}"
        await c.close()


# ---------------------------------------------------------------------------
# PersonalizationExperimentsOperations (Batch 6)
# ---------------------------------------------------------------------------


class TestPersonalizationExperimentsOperations:
    async def test_create_experiment(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.personalization_experiments.create_experiment({"name": "exp"}, action="Start")
        path = c._data_session.post.call_args[0][0]
        params = c._data_session.post.call_args[1]["params"]
        assert path == "personalization/abn-experiments"
        assert params == {"action": "Start"}
        await c.close()

    async def test_get_experiment(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.personalization_experiments.get_experiment(EXPERIMENT_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == f"personalization/abn-experiments/{EXPERIMENT_ID}"
        await c.close()

    async def test_update_experiment(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.patch = AsyncMock(return_value=_mock_response(200, {}))
        await c.personalization_experiments.update_experiment(
            EXPERIMENT_ID, {"label": "new"}, action="Stop"
        )
        path = c._data_session.patch.call_args[0][0]
        params = c._data_session.patch.call_args[1]["params"]
        assert path == f"personalization/abn-experiments/{EXPERIMENT_ID}"
        assert params == {"action": "Stop"}
        await c.close()

    async def test_delete_experiment(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(202, {}))
        await c.personalization_experiments.delete_experiment(EXPERIMENT_ID)
        path = c._data_session.delete.call_args[0][0]
        assert path == f"personalization/abn-experiments/{EXPERIMENT_ID}"
        await c.close()


# ---------------------------------------------------------------------------
# PersonalizationRecommendersOperations (Batch 6)
# ---------------------------------------------------------------------------


class TestPersonalizationRecommendersOperations:
    async def test_list_recommenders(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.personalization_recommenders.list_recommenders(
            data_space_id_or_name="default",
            profile_data_graph_id_or_name="pdg",
        )
        path = c._data_session.get.call_args[0][0]
        params = c._data_session.get.call_args[1]["params"]
        assert path == "personalization/personalization-recommenders"
        assert params == {
            "dataSpaceIdOrName": "default",
            "profileDataGraphIdOrName": "pdg",
        }
        await c.close()

    async def test_create_recommender(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.personalization_recommenders.create_recommender({"name": "r"})
        path = c._data_session.post.call_args[0][0]
        assert path == "personalization/personalization-recommenders"
        await c.close()

    async def test_get_recommender(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.personalization_recommenders.get_recommender(RECOMMENDER_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (f"personalization/personalization-recommenders/{RECOMMENDER_ID}")
        await c.close()

    async def test_update_recommender(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.patch = AsyncMock(return_value=_mock_response(200, {}))
        await c.personalization_recommenders.update_recommender(RECOMMENDER_ID, {"label": "new"})
        path = c._data_session.patch.call_args[0][0]
        assert path == (f"personalization/personalization-recommenders/{RECOMMENDER_ID}")
        await c.close()

    async def test_delete_recommender(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        await c.personalization_recommenders.delete_recommender(RECOMMENDER_ID)
        path = c._data_session.delete.call_args[0][0]
        assert path == (f"personalization/personalization-recommenders/{RECOMMENDER_ID}")
        await c.close()

    async def test_list_recommender_jobs(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.personalization_recommenders.list_recommender_jobs(RECOMMENDER_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (f"personalization/personalization-recommenders/{RECOMMENDER_ID}/jobs")
        await c.close()


# ---------------------------------------------------------------------------
# ActivityRemindersOperations (Batch 7)
# ---------------------------------------------------------------------------


class TestActivityRemindersOperations:
    async def test_list_activity_reminders(self):
        c = await _client(mock_get=_mock_response(200, {"reminders": []}))
        await c.activity_reminders.list_activity_reminders(
            max_record_count=50,
            number_of_days=14,
            activity_type="Task",
        )
        path = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert path == "reminders/activities"
        assert params == {
            "maxRecordCount": 50,
            "numberOfDays": 14,
            "type": "Task",
        }
        await c.close()

    async def test_list_activity_reminders_no_params(self):
        c = await _client(mock_get=_mock_response(200, {"reminders": []}))
        await c.activity_reminders.list_activity_reminders()
        assert c._session.get.call_args[1]["params"] == {}
        await c.close()

    async def test_get_activity_reminder(self):
        c = await _client(mock_get=_mock_response(200, {"id": ACTIVITY_ID}))
        await c.activity_reminders.get_activity_reminder(ACTIVITY_ID)
        path = c._session.get.call_args[0][0]
        assert path == f"reminders/{ACTIVITY_ID}"
        await c.close()

    async def test_update_activity_reminder(self):
        c = await _client(mock_patch=_mock_response(200, {}))
        await c.activity_reminders.update_activity_reminder(
            ACTIVITY_ID,
            is_reminder_displayed=False,
            reminder_date_time="2026-11-22T16:00:00.000Z",
        )
        path = c._session.patch.call_args[0][0]
        payload = c._session.patch.call_args[1]["json"]
        assert path == f"reminders/{ACTIVITY_ID}"
        assert payload == {
            "isReminderDisplayed": False,
            "reminderDateTime": "2026-11-22T16:00:00.000Z",
        }
        await c.close()

    async def test_replace_activity_reminder(self):
        c = await _client(mock_put=_mock_response(200, {}))
        await c.activity_reminders.replace_activity_reminder(
            ACTIVITY_ID,
            reminder_date_time="2026-11-22T16:00:00.000Z",
        )
        path = c._session.put.call_args[0][0]
        payload = c._session.put.call_args[1]["json"]
        assert path == f"reminders/{ACTIVITY_ID}"
        assert payload == {"reminderDateTime": "2026-11-22T16:00:00.000Z"}
        await c.close()

    async def test_delete_activity_reminder(self):
        c = await _client(mock_delete=_mock_response(204))
        await c.activity_reminders.delete_activity_reminder(ACTIVITY_ID)
        path = c._session.delete.call_args[0][0]
        assert path == f"reminders/{ACTIVITY_ID}"
        await c.close()


# ---------------------------------------------------------------------------
# BotVersionActivationOperations (Batch 7)
# ---------------------------------------------------------------------------


class TestBotVersionActivationOperations:
    async def test_get_activation(self):
        c = await _client(mock_get=_mock_response(200, {"status": "Active"}))
        await c.bot_version_activation.get_activation(BOT_VERSION_ID)
        path = c._session.get.call_args[0][0]
        assert path == f"bot-versions/{BOT_VERSION_ID}/activation"
        await c.close()

    async def test_set_activation_body(self):
        c = await _client(mock_post=_mock_response(200, {"status": "Active"}))
        await c.bot_version_activation.set_activation(BOT_VERSION_ID, status="Active")
        path = c._session.post.call_args[0][0]
        payload = c._session.post.call_args[1]["json"]
        assert path == f"bot-versions/{BOT_VERSION_ID}/activation"
        assert payload == {"status": "Active"}
        await c.close()

    async def test_set_activation_query_param(self):
        c = await _client(mock_post=_mock_response(200, {"status": "Inactive"}))
        await c.bot_version_activation.set_activation(
            BOT_VERSION_ID, status="Inactive", in_body=False
        )
        path = c._session.post.call_args[0][0]
        params = c._session.post.call_args[1]["params"]
        assert path == f"bot-versions/{BOT_VERSION_ID}/activation"
        assert params == {"status": "Inactive"}
        await c.close()


# ---------------------------------------------------------------------------
# ConversationApplicationOperations (Batch 7)
# ---------------------------------------------------------------------------


class TestConversationApplicationOperations:
    async def test_get_definition(self):
        c = await _client(mock_get=_mock_response(200, {"integrationName": "MyApp"}))
        await c.conversation_application.get_definition("MyApp")
        path = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert path == "conversation-application"
        assert params == {"integrationName": "MyApp"}
        await c.close()


# ---------------------------------------------------------------------------
# ConversationsOperations (Batch 7)
# ---------------------------------------------------------------------------


class TestConversationsOperations:
    async def test_get_bulk_upload_statuses(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.conversations.get_bulk_upload_statuses(["a", "b", "c"])
        path = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert path == "conversations/upload"
        assert params == {"uploadIds": "a,b,c"}
        await c.close()

    async def test_bulk_upload(self):
        c = await _client(mock_post=_mock_response(200, {}))
        await c.conversations.bulk_upload({"payload": 1})
        path = c._session.post.call_args[0][0]
        assert path == "conversations/upload"
        assert c._session.post.call_args[1]["json"] == {"payload": 1}
        await c.close()

    async def test_get_entries(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.conversations.get_entries(
            "conv-1",
            end_timestamp=1600788018,
            query_direction="FromStart",
            record_limit=100,
            start_timestamp=0,
        )
        path = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert path == "conversation/conv-1/entries"
        assert params == {
            "endTimestamp": 1600788018,
            "queryDirection": "FromStart",
            "recordLimit": 100,
            "startTimestamp": 0,
        }
        await c.close()

    async def test_update_entries(self):
        c = await _client(mock_patch=_mock_response(200, {}))
        updates = [
            {"identifier": "36b0f4d9", "messageText": "redacted"},
        ]
        await c.conversations.update_entries("conv-1", conversation_entries_updates=updates)
        path = c._session.patch.call_args[0][0]
        payload = c._session.patch.call_args[1]["json"]
        assert path == "conversation/conv-1/entries"
        assert payload == {"conversationEntriesUpdates": updates}
        await c.close()


# ---------------------------------------------------------------------------
# FlowApprovalOperations (Batch 7)
# ---------------------------------------------------------------------------


class TestFlowApprovalOperations:
    async def test_get_status(self):
        c = await _client(mock_get=_mock_response(200, {"flowApproval": []}))
        await c.flow_approval.get_status(
            process_names=["Proc_A", "Proc_B"],
            related_record_id="001xx000003DGbz",
        )
        path = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert path == "interaction/flow-approval-process/status"
        assert params["processNames"] == "Proc_A,Proc_B"
        assert len(params["relatedRecordId"]) == 18
        await c.close()

    async def test_get_status_no_params(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.flow_approval.get_status()
        assert c._session.get.call_args[1]["params"] == {}
        await c.close()


# ---------------------------------------------------------------------------
# OrchestrationOperations (Batch 7)
# ---------------------------------------------------------------------------


class TestOrchestrationOperations:
    async def test_list_instances_by_record(self):
        c = await _client(mock_get=_mock_response(200, {"instances": []}))
        await c.orchestration.list_instances(related_record_id="001xx000003DGbz")
        path = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert path == "interaction/orchestration/instances"
        assert len(params["relatedRecordId"]) == 18
        await c.close()

    async def test_list_instances_by_orchestration(self):
        c = await _client(mock_get=_mock_response(200, {"instances": []}))
        await c.orchestration.list_instances(related_orchestration_id=ORCHESTRATION_INSTANCE_ID)
        params = c._session.get.call_args[1]["params"]
        assert params == {"relatedOrchestrationId": ORCHESTRATION_INSTANCE_ID}
        await c.close()

    async def test_get_instance_detail(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.orchestration.get_instance_detail(ORCHESTRATION_INSTANCE_ID)
        path = c._session.get.call_args[0][0]
        params = c._session.get.call_args[1]["params"]
        assert path == "interaction/orchestration/instance/detail"
        assert params == {"instanceId": ORCHESTRATION_INSTANCE_ID}
        await c.close()


# ---------------------------------------------------------------------------
# QuipOperations (Batch 7)
# ---------------------------------------------------------------------------


class TestQuipOperations:
    async def test_get_related_records(self):
        c = await _client(mock_get=_mock_response(200, {}))
        await c.quip.get_related_records(QUIP_DOC_ID)
        path = c._session.get.call_args[0][0]
        assert path == f"quip/related-records/{QUIP_DOC_ID}"
        await c.close()


# ---------------------------------------------------------------------------
# CommerceAddressesOperations (Batch 8)
# ---------------------------------------------------------------------------


class TestCommerceAddressesOperations:
    async def test_list_addresses(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_addresses.list_addresses(WEBSTORE_ID, ACCOUNT_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/accounts/{ACCOUNT_ID}/addresses")
        await c.close()

    async def test_create_address(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_addresses.create_address(WEBSTORE_ID, ACCOUNT_ID, {"street": "1 Market"})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/accounts/{ACCOUNT_ID}/addresses")
        await c.close()

    async def test_update_address(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.patch = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_addresses.update_address(
            WEBSTORE_ID, ACCOUNT_ID, ADDRESS_ID, {"street": "updated"}
        )
        path = c._data_session.patch.call_args[0][0]
        assert path == (
            f"commerce/webstores/{WEBSTORE_ID}/accounts/{ACCOUNT_ID}/addresses/{ADDRESS_ID}"
        )
        await c.close()

    async def test_delete_address(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        await c.commerce_addresses.delete_address(WEBSTORE_ID, ACCOUNT_ID, ADDRESS_ID)
        path = c._data_session.delete.call_args[0][0]
        assert path == (
            f"commerce/webstores/{WEBSTORE_ID}/accounts/{ACCOUNT_ID}/addresses/{ADDRESS_ID}"
        )
        await c.close()


# ---------------------------------------------------------------------------
# CommerceCartOperations (Batch 8)
# ---------------------------------------------------------------------------


class TestCommerceCartOperations:
    async def test_create_cart(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_cart.create_cart(WEBSTORE_ID, {"name": "My Cart"})
        path = c._data_session.post.call_args[0][0]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/carts"
        await c.close()

    async def test_get_compact_summary(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_cart.get_compact_summary(WEBSTORE_ID, effective_account_id=ACCOUNT_ID)
        path = c._data_session.get.call_args[0][0]
        params = c._data_session.get.call_args[1]["params"]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/carts/compact-summary"
        assert params == {"effectiveAccountId": ACCOUNT_ID}
        await c.close()

    async def test_get_cart_default_active(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_cart.get_cart(WEBSTORE_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/carts/active"
        await c.close()

    async def test_calculate(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_cart.calculate(WEBSTORE_ID)
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/carts/active/actions/calculate")
        await c.close()

    async def test_evaluate_shipping(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_cart.evaluate_shipping(WEBSTORE_ID)
        path = c._data_session.post.call_args[0][0]
        assert path.endswith("/actions/evaluate-shipping")
        await c.close()

    async def test_evaluate_taxes(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_cart.evaluate_taxes(WEBSTORE_ID)
        path = c._data_session.post.call_args[0][0]
        assert path.endswith("/actions/evaluate-taxes")
        await c.close()

    async def test_add_cart_to_wishlist(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_cart.add_cart_to_wishlist(
            WEBSTORE_ID, CART_ID, {"wishlistId": WISHLIST_ID}
        )
        path = c._data_session.post.call_args[0][0]
        assert path == (
            f"commerce/webstores/{WEBSTORE_ID}/carts/{CART_ID}/actions/add-cart-to-wishlist"
        )
        await c.close()

    async def test_clone(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_cart.clone(WEBSTORE_ID, CART_ID)
        assert c._data_session.post.call_args[0][0].endswith(f"/carts/{CART_ID}/actions/clone")
        await c.close()

    async def test_apply_coupon(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_cart.apply_coupon(WEBSTORE_ID, "active", {"couponCode": "SAVE10"})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/carts/active/cart-coupons")
        await c.close()

    async def test_delete_coupon(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        await c.commerce_cart.delete_coupon(WEBSTORE_ID, "active", CART_COUPON_ID)
        path = c._data_session.delete.call_args[0][0]
        assert path == (
            f"commerce/webstores/{WEBSTORE_ID}/carts/active/cart-coupons/{CART_COUPON_ID}"
        )
        await c.close()

    async def test_add_item(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_cart.add_item(
            WEBSTORE_ID,
            "active",
            {"productId": PRODUCT_ID, "quantity": "1"},
        )
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/carts/active/cart-items")
        await c.close()

    async def test_add_items_batch(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_cart.add_items_batch(WEBSTORE_ID, "active", {"cartItems": []})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/carts/active/cart-items/batch")
        await c.close()

    async def test_update_item(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.patch = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_cart.update_item(WEBSTORE_ID, "active", CART_ITEM_ID, {"quantity": "2"})
        path = c._data_session.patch.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/carts/active/cart-items/{CART_ITEM_ID}")
        await c.close()

    async def test_delete_item(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        await c.commerce_cart.delete_item(WEBSTORE_ID, "active", CART_ITEM_ID)
        path = c._data_session.delete.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/carts/active/cart-items/{CART_ITEM_ID}")
        await c.close()

    async def test_list_delivery_groups(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_cart.list_delivery_groups(WEBSTORE_ID)
        assert c._data_session.get.call_args[0][0].endswith("/carts/active/delivery-groups")
        await c.close()

    async def test_update_delivery_group(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.patch = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_cart.update_delivery_group(
            WEBSTORE_ID, "active", DELIVERY_GROUP_ID, {"name": "g1"}
        )
        path = c._data_session.patch.call_args[0][0]
        assert path == (
            f"commerce/webstores/{WEBSTORE_ID}/carts/active/delivery-groups/{DELIVERY_GROUP_ID}"
        )
        await c.close()


# ---------------------------------------------------------------------------
# CommerceCheckoutOperations (Batch 8)
# ---------------------------------------------------------------------------


class TestCommerceCheckoutOperations:
    async def test_start_checkout(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_checkout.start_checkout(WEBSTORE_ID)
        path = c._data_session.post.call_args[0][0]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/checkouts"
        await c.close()

    async def test_get_checkout(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_checkout.get_checkout(WEBSTORE_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/checkouts/active"
        await c.close()

    async def test_pay(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_checkout.pay(WEBSTORE_ID, CHECKOUT_ID, {"paymentToken": "tok_1"})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/checkouts/{CHECKOUT_ID}/payments")
        await c.close()

    async def test_place_order(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_checkout.place_order(WEBSTORE_ID, CHECKOUT_ID)
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/checkouts/{CHECKOUT_ID}/orders")
        await c.close()

    async def test_tokenize_payment(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_checkout.tokenize_payment(WEBSTORE_ID, {"cardNumber": "4111"})
        path = c._data_session.post.call_args[0][0]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/payments/token"
        await c.close()

    async def test_register_buyer(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_checkout.register_buyer(WEBSTORE_ID, {"email": "x@x.com"})
        path = c._data_session.post.call_args[0][0]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/buyers/registrations"
        await c.close()


# ---------------------------------------------------------------------------
# CommerceProductsOperations (Batch 8)
# ---------------------------------------------------------------------------


class TestCommerceProductsOperations:
    async def test_list_products(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_products.list_products(WEBSTORE_ID, ids=[PRODUCT_ID, "01txx0000000002"])
        path = c._data_session.get.call_args[0][0]
        params = c._data_session.get.call_args[1]["params"]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/products"
        assert "ids" in params
        await c.close()

    async def test_get_product(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_products.get_product(WEBSTORE_ID, PRODUCT_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/products/{PRODUCT_ID}")
        await c.close()

    async def test_list_child_categories_top_level(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_products.list_child_categories(WEBSTORE_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/product-categories/children")
        await c.close()

    async def test_get_product_category(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_products.get_product_category(WEBSTORE_ID, PRODUCT_CATEGORY_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (
            f"commerce/webstores/{WEBSTORE_ID}/product-categories/{PRODUCT_CATEGORY_ID}"
        )
        await c.close()

    async def test_search_products(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_products.search_products(WEBSTORE_ID, {"searchTerm": "laptop"})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/search/product-search")
        await c.close()

    async def test_search_products_by_term(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_products.search_products_by_term(
            WEBSTORE_ID, search_term="monitor", page=0, page_size=20
        )
        params = c._data_session.get.call_args[1]["params"]
        assert params == {"searchTerm": "monitor", "page": 0, "pageSize": 20}
        await c.close()

    async def test_get_search_suggestions(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_products.get_search_suggestions(WEBSTORE_ID, search_term="foo")
        params = c._data_session.get.call_args[1]["params"]
        assert params == {"searchTerm": "foo"}
        await c.close()


# ---------------------------------------------------------------------------
# CommercePricingOperations (Batch 8)
# ---------------------------------------------------------------------------


class TestCommercePricingOperations:
    async def test_get_product_price(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_pricing.get_product_price(WEBSTORE_ID, PRODUCT_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/pricing/products/{PRODUCT_ID}")
        await c.close()

    async def test_get_product_prices(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_pricing.get_product_prices(WEBSTORE_ID, {"pricingLineItems": []})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/pricing/products")
        await c.close()

    async def test_evaluate_promotions(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_pricing.evaluate_promotions({"webstoreId": WEBSTORE_ID})
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/promotions/actions/evaluate"
        await c.close()

    async def test_increase_coupon_use(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_pricing.increase_coupon_use({"codes": ["X"]})
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/promotions/actions/increase-use/coupon-codes"
        await c.close()


# ---------------------------------------------------------------------------
# CommerceTaxesOperations (Batch 8)
# ---------------------------------------------------------------------------


class TestCommerceTaxesOperations:
    async def test_calculate_taxes(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_taxes.calculate_taxes(WEBSTORE_ID, {"items": []})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/taxes/actions/calculate-taxes")
        await c.close()

    async def test_get_product_taxes(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_taxes.get_product_taxes(WEBSTORE_ID, PRODUCT_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/taxes/products/{PRODUCT_ID}")
        await c.close()


# ---------------------------------------------------------------------------
# CommerceWishlistsOperations (Batch 8)
# ---------------------------------------------------------------------------


class TestCommerceWishlistsOperations:
    async def test_list_wishlists(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_wishlists.list_wishlists(WEBSTORE_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/wishlists"
        await c.close()

    async def test_create_wishlist(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_wishlists.create_wishlist(WEBSTORE_ID, {"name": "Favourites"})
        path = c._data_session.post.call_args[0][0]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/wishlists"
        await c.close()

    async def test_delete_wishlist(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        await c.commerce_wishlists.delete_wishlist(WEBSTORE_ID, WISHLIST_ID)
        path = c._data_session.delete.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/wishlists/{WISHLIST_ID}")
        await c.close()

    async def test_add_to_cart(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_wishlists.add_to_cart(WEBSTORE_ID, WISHLIST_ID)
        path = c._data_session.post.call_args[0][0]
        assert path == (
            f"commerce/webstores/{WEBSTORE_ID}/wishlists/{WISHLIST_ID}/actions/add-wishlist-to-cart"
        )
        await c.close()

    async def test_add_item(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_wishlists.add_item(WEBSTORE_ID, WISHLIST_ID, {"productId": PRODUCT_ID})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/wishlists/{WISHLIST_ID}/wishlist-items")
        await c.close()

    async def test_delete_item(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        await c.commerce_wishlists.delete_item(WEBSTORE_ID, WISHLIST_ID, WISHLIST_ITEM_ID)
        path = c._data_session.delete.call_args[0][0]
        assert path == (
            f"commerce/webstores/{WEBSTORE_ID}/wishlists/{WISHLIST_ID}"
            f"/wishlist-items/{WISHLIST_ITEM_ID}"
        )
        await c.close()


# ---------------------------------------------------------------------------
# CommerceOrderSummariesOperations (Batch 8)
# ---------------------------------------------------------------------------


class TestCommerceOrderSummariesOperations:
    async def test_list_order_summaries(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_order_summaries.list_order_summaries(WEBSTORE_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/order-summaries"
        await c.close()

    async def test_get_order_summary(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_order_summaries.get_order_summary(WEBSTORE_ID, ORDER_SUMMARY_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/order-summaries/{ORDER_SUMMARY_ID}")
        await c.close()

    async def test_add_order_to_cart(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_order_summaries.add_order_to_cart(
            WEBSTORE_ID, {"orderSummaryId": ORDER_SUMMARY_ID}
        )
        path = c._data_session.post.call_args[0][0]
        assert path == (
            f"commerce/webstores/{WEBSTORE_ID}/order-summaries/actions/add-order-to-cart"
        )
        await c.close()

    async def test_list_shipment_items(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_order_summaries.list_shipment_items(WEBSTORE_ID, SHIPMENT_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/shipments/{SHIPMENT_ID}/items")
        await c.close()


# ---------------------------------------------------------------------------
# CommerceMyProfileOperations (Batch 8)
# ---------------------------------------------------------------------------


class TestCommerceMyProfileOperations:
    async def test_get_profile(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_my_profile.get_profile(WEBSTORE_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/myprofile"
        await c.close()

    async def test_update_profile(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.patch = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_my_profile.update_profile(WEBSTORE_ID, {"email": "x@x.com"})
        path = c._data_session.patch.call_args[0][0]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/myprofile"
        await c.close()

    async def test_init_otp(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_my_profile.init_otp(WEBSTORE_ID, {"method": "SMS"})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/myprofile/actions/initOTP")
        await c.close()

    async def test_verify_otp(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_my_profile.verify_otp(WEBSTORE_ID, {"code": "1234"})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/myprofile/actions/verify")
        await c.close()


# ---------------------------------------------------------------------------
# CommerceContextOperations (Batch 8)
# ---------------------------------------------------------------------------


class TestCommerceContextOperations:
    async def test_get_application_context(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_context.get_application_context(WEBSTORE_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/application-context")
        await c.close()

    async def test_get_session_context(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_context.get_session_context(WEBSTORE_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/session-context")
        await c.close()


# ---------------------------------------------------------------------------
# CommerceEinsteinWebstoreOperations (Batch 9)
# ---------------------------------------------------------------------------


class TestCommerceEinsteinWebstoreOperations:
    async def test_get_deployment_status(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_einstein_webstore.get_deployment_status(WEBSTORE_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/ai/status"
        await c.close()

    async def test_get_configuration(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_einstein_webstore.get_configuration(WEBSTORE_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/ai/configuration"
        await c.close()

    async def test_enqueue_activity_export(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_einstein_webstore.enqueue_activity_export(WEBSTORE_ID, {"cookieId": "abc"})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/ai/activities/export-jobs")
        await c.close()

    async def test_get_activity_export_status(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_einstein_webstore.get_activity_export_status(WEBSTORE_ID, EXPORT_JOB_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (
            f"commerce/webstores/{WEBSTORE_ID}/ai/activities/export-jobs/{EXPORT_JOB_ID}"
        )
        await c.close()

    async def test_download_activity_export(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, content=b"data"))
        result = await c.commerce_einstein_webstore.download_activity_export(
            WEBSTORE_ID, EXPORT_JOB_ID
        )
        assert result == b"data"
        await c.close()

    async def test_enqueue_activity_purge(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_einstein_webstore.enqueue_activity_purge(WEBSTORE_ID, {"userId": "005xx"})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/webstores/{WEBSTORE_ID}/ai/activities/purge-jobs")
        await c.close()

    async def test_get_activity_purge_status(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_einstein_webstore.get_activity_purge_status(WEBSTORE_ID, EXPORT_JOB_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (
            f"commerce/webstores/{WEBSTORE_ID}/ai/activities/purge-jobs/{EXPORT_JOB_ID}"
        )
        await c.close()

    async def test_get_recommendations(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.commerce_einstein_webstore.get_recommendations(
            WEBSTORE_ID,
            recommender="SimilarProducts",
            anchor_from_current_cart=True,
            currency_iso_code="USD",
        )
        path = c._data_session.get.call_args[0][0]
        params = c._data_session.get.call_args[1]["params"]
        assert path == f"commerce/webstores/{WEBSTORE_ID}/ai/recommendations"
        assert params["recommender"] == "SimilarProducts"
        assert params["anchorFromCurrentCart"] is True
        assert params["currencyIsoCode"] == "USD"
        await c.close()


# ---------------------------------------------------------------------------
# OmnichannelInventoryOperations (Batch 9)
# ---------------------------------------------------------------------------


class TestOmnichannelInventoryOperations:
    async def test_batch_update_availability(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.omnichannel_inventory.batch_update_availability({"records": []})
        path = c._data_session.post.call_args[0][0]
        assert path == ("commerce/oci/availability-records/actions/batch-update")
        await c.close()

    async def test_get_availability(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.omnichannel_inventory.get_availability({"products": []})
        path = c._data_session.post.call_args[0][0]
        assert path == ("commerce/oci/availability/availability-records/actions/get-availability")
        await c.close()

    async def test_upload_availability(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.omnichannel_inventory.upload_availability({"fileUpload": b"ndjson"})
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/oci/availability-records/uploads"
        await c.close()

    async def test_get_availability_upload_status(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.omnichannel_inventory.get_availability_upload_status(UPLOAD_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == f"commerce/oci/availability-records/uploads/{UPLOAD_ID}"
        await c.close()

    async def test_check_availability(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.omnichannel_inventory.check_availability(
            {"products": []}, scope=f"webStoreId Eq '{WEBSTORE_ID}'"
        )
        path = c._data_session.post.call_args[0][0]
        params = c._data_session.post.call_args[1]["params"]
        assert path == "commerce/inventory/check-availability"
        assert params["scope"] == f"webStoreId Eq '{WEBSTORE_ID}'"
        await c.close()

    async def test_get_levels(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.omnichannel_inventory.get_levels(
            scope=f"webStoreId Eq '{WEBSTORE_ID}'",
            products=["SKU1"],
            locations=["LOC1"],
        )
        path = c._data_session.get.call_args[0][0]
        params = c._data_session.get.call_args[1]["params"]
        assert path == "commerce/inventory/levels"
        assert params["products"] == ["SKU1"]
        assert params["locations"] == ["LOC1"]
        await c.close()

    async def test_upload_location_graph(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.omnichannel_inventory.upload_location_graph()
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/oci/location-graph/uploads"
        await c.close()

    async def test_get_location_graph_upload_status(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.omnichannel_inventory.get_location_graph_upload_status(UPLOAD_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == f"commerce/oci/location-graph/uploads/{UPLOAD_ID}"
        await c.close()

    async def test_create_reservation(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.omnichannel_inventory.create_reservation({"reservations": []})
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/oci/reservation/actions/reservations"
        await c.close()

    async def test_fulfill_reservation(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.omnichannel_inventory.fulfill_reservation({"fulfillments": []})
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/oci/reservation/actions/fulfillments"
        await c.close()

    async def test_release_reservation(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.omnichannel_inventory.release_reservation({"releases": []})
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/oci/reservation/actions/releases"
        await c.close()

    async def test_transfer_reservation(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.omnichannel_inventory.transfer_reservation({"transfers": []})
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/oci/reservation/actions/transfers"
        await c.close()

    async def test_update_reservation(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.omnichannel_inventory.update_reservation({"updates": []})
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/oci/reservation/actions/update"
        await c.close()


# ---------------------------------------------------------------------------
# OrderManagementOperations (Batch 9)
# ---------------------------------------------------------------------------


class TestOrderManagementOperations:
    async def test_register_guest_buyer(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.register_guest_buyer(WEBSTORE_ID, ACCOUNT_ID)
        path = c._data_session.post.call_args[0][0]
        assert path == (
            f"commerce/webstores/{WEBSTORE_ID}/accounts/{ACCOUNT_ID}/actions/register-guest-buyer"
        )
        await c.close()

    async def test_get_products_return_rate(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.get_products_return_rate(page=1, page_size=25)
        path = c._data_session.get.call_args[0][0]
        params = c._data_session.get.call_args[1]["params"]
        assert path == ("commerce/order-management/analytics/insights/products-return-rate")
        assert params == {"page": 1, "pageSize": 25}
        await c.close()

    async def test_classify_text(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.classify_text({"texts": []})
        path = c._data_session.post.call_args[0][0]
        params = c._data_session.post.call_args[1]["params"]
        assert path == ("commerce/order-management/analytics/ai/text-classifications")
        assert params == {"llmType": "open-ai"}
        await c.close()

    async def test_estimate_delivery_date(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.estimate_delivery_date({"orderId": "x"})
        path = c._data_session.post.call_args[0][0]
        assert path == (
            "commerce/delivery/estimation-setup/externalReference/estimate/estimate-date"
        )
        await c.close()

    async def test_create_fulfillment_order(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.create_fulfillment_order({"orderId": "x"})
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/fulfillment/fulfillment-orders"
        await c.close()

    async def test_cancel_fulfillment_items(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.cancel_fulfillment_items(FULFILLMENT_ORDER_ID, {"items": []})
        path = c._data_session.post.call_args[0][0]
        assert path == (
            f"commerce/fulfillment/fulfillment-orders/{FULFILLMENT_ORDER_ID}/actions/cancel-item"
        )
        await c.close()

    async def test_create_fulfillment_invoice(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.create_fulfillment_invoice(FULFILLMENT_ORDER_ID)
        path = c._data_session.post.call_args[0][0]
        assert path == (
            f"commerce/fulfillment/fulfillment-orders/{FULFILLMENT_ORDER_ID}/actions/create-invoice"
        )
        await c.close()

    async def test_distribute_picked_quantities(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.distribute_picked_quantities({"picks": []})
        path = c._data_session.post.call_args[0][0]
        assert path == ("commerce/fulfillment/pick-tickets/actions/distribute-quantities")
        await c.close()

    async def test_preview_cart_to_exchange_order(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.preview_cart_to_exchange_order({"cartId": "x"})
        path = c._data_session.post.call_args[0][0]
        assert path == (
            "commerce/order-management/exchanges/actions/preview-cart-to-exchange-order"
        )
        await c.close()

    async def test_create_order_summary(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.create_order_summary({"orderId": "x"})
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/order-management/order-summaries"
        await c.close()

    async def test_create_credit_memo(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.create_credit_memo(ORDER_SUMMARY_ID, {"changeOrderIds": []})
        path = c._data_session.post.call_args[0][0]
        assert path == (
            f"commerce/order-management/order-summaries/{ORDER_SUMMARY_ID}"
            "/actions/create-credit-memo"
        )
        await c.close()

    async def test_ensure_funds_async(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.ensure_funds_async(ORDER_SUMMARY_ID, {"invoiceId": "x"})
        path = c._data_session.post.call_args[0][0]
        assert path == (
            f"commerce/order-management/order-summaries/{ORDER_SUMMARY_ID}"
            "/async-actions/ensure-funds-async"
        )
        await c.close()

    async def test_submit_return(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.submit_return(ORDER_SUMMARY_ID, {"items": []})
        path = c._data_session.post.call_args[0][0]
        assert path == (
            f"commerce/order-management/order-summaries/{ORDER_SUMMARY_ID}/actions/submit-return"
        )
        await c.close()

    async def test_create_pending_order_summaries(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.create_pending_order_summaries({"orderSummaryGraph": {}})
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/order-summaries"
        await c.close()

    async def test_get_products_with_return_reasons(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.get_products_with_return_reasons(
            products=[PRODUCT_ID], scope="OrderSummary"
        )
        path = c._data_session.get.call_args[0][0]
        params = c._data_session.get.call_args[1]["params"]
        assert path == "commerce/order-management/products"
        assert params["scope"] == "OrderSummary"
        assert params["expand"] == "ReturnReasons"
        await c.close()

    async def test_get_product_details(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.get_product_details(
            WEBSTORE_ID, "SKU-1", currency_code="USD", exclude_media=True
        )
        path = c._data_session.get.call_args[0][0]
        params = c._data_session.get.call_args[1]["params"]
        assert path == (f"commerce/order-management/webstores/{WEBSTORE_ID}/products/SKU-1")
        assert params["currencyCode"] == "USD"
        assert params["excludeMedia"] is True
        await c.close()

    async def test_search_products(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.search_products(WEBSTORE_ID, search_term="hat")
        path = c._data_session.get.call_args[0][0]
        params = c._data_session.get.call_args[1]["params"]
        assert path == (f"commerce/order-management/webstores/{WEBSTORE_ID}/products")
        assert params["searchTerm"] == "hat"
        await c.close()

    async def test_create_return_order(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.create_return_order({"lineItems": []})
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/returns/return-orders"
        await c.close()

    async def test_process_return_items(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.process_return_items(RETURN_ORDER_ID, {"items": []})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/returns/return-orders/{RETURN_ORDER_ID}/actions/return-items")
        await c.close()

    async def test_find_routes_with_fewest_splits(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.find_routes_with_fewest_splits({"items": []})
        path = c._data_session.post.call_args[0][0]
        assert path == ("commerce/order-management/routing/actions/find-routes-with-fewest-splits")
        await c.close()

    async def test_hold_capacity(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.order_management.hold_capacity({"location": "x"})
        path = c._data_session.post.call_args[0][0]
        assert path == (
            "commerce/order-management/routing/fulfillment-order-capacity/actions/hold-capacity"
        )
        await c.close()


# ---------------------------------------------------------------------------
# PaymentsOperations (Batch 9)
# ---------------------------------------------------------------------------


class TestPaymentsOperations:
    async def test_authorize(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.authorize({"amount": 100})
        path = c._data_session.post.call_args[0][0]
        headers = c._data_session.post.call_args[1]["headers"]
        assert path == "commerce/payments/authorizations"
        assert headers is None
        await c.close()

    async def test_authorize_with_idempotency_key(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.authorize({"amount": 100}, idempotency_key="abc")
        headers = c._data_session.post.call_args[1]["headers"]
        assert headers == {"sfdc-Payments-Idempotency-Key": "abc"}
        await c.close()

    async def test_capture(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.capture(AUTHORIZATION_ID, {"amount": 50})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/payments/authorizations/{AUTHORIZATION_ID}/captures")
        await c.close()

    async def test_reverse_authorization(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.reverse_authorization(AUTHORIZATION_ID, {"amount": 50})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/payments/authorizations/{AUTHORIZATION_ID}/reversals")
        await c.close()

    async def test_post_authorization(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.post_authorization({"amount": 100})
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/payments/postAuths"
        await c.close()

    async def test_refund(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.refund(PAYMENT_ID, {"amount": 50})
        path = c._data_session.post.call_args[0][0]
        assert path == (f"commerce/payments/payments/{PAYMENT_ID}/refunds")
        await c.close()

    async def test_sale(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.sale({"amount": 500})
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/payments/sales"
        await c.close()

    async def test_tokenize_payment_method(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.tokenize_payment_method({"cardPaymentMethod": {}})
        path = c._data_session.post.call_args[0][0]
        assert path == "commerce/payments/payment-methods"
        await c.close()

    async def test_create_payment_intent(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.create_payment_intent({"amount": 8.99})
        path = c._data_session.post.call_args[0][0]
        assert path == "payments/payment-intents"
        await c.close()

    async def test_get_payment_intent_timeline(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.get_payment_intent_timeline(PAYMENT_INTENT_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == f"payments/payment-intents/{PAYMENT_INTENT_ID}/timeline"
        await c.close()

    async def test_get_payment_method_set(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.get_payment_method_set(PAYMENT_METHOD_SET_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (f"payments/payment-method-sets/{PAYMENT_METHOD_SET_ID}")
        await c.close()

    async def test_get_payment_method_set_by_developer_name(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.get_payment_method_set_by_developer_name("MySet")
        path = c._data_session.get.call_args[0][0]
        params = c._data_session.get.call_args[1]["params"]
        assert path == "payments/payment-method-sets"
        assert params == {"developerName": "MySet"}
        await c.close()

    async def test_register_apple_pay_domain(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.register_apple_pay_domain(
            MERCHANT_ACCOUNT_ID, {"domainName": "example.com"}
        )
        path = c._data_session.post.call_args[0][0]
        assert path == (f"payments/merchant-accounts/{MERCHANT_ACCOUNT_ID}/apple-pay-domains")
        await c.close()

    async def test_list_apple_pay_domains(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.list_apple_pay_domains(MERCHANT_ACCOUNT_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == (f"payments/merchant-accounts/{MERCHANT_ACCOUNT_ID}/apple-pay-domains")
        await c.close()

    async def test_delete_apple_pay_domain(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        await c.payments.delete_apple_pay_domain(MERCHANT_ACCOUNT_ID, APPLE_PAY_DOMAIN_ID)
        path = c._data_session.delete.call_args[0][0]
        assert path == (
            f"payments/merchant-accounts/{MERCHANT_ACCOUNT_ID}"
            f"/apple-pay-domains/{APPLE_PAY_DOMAIN_ID}"
        )
        await c.close()

    async def test_list_saved_payment_methods(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.list_saved_payment_methods(
            MERCHANT_ACCOUNT_ID, effective_account_id=ACCOUNT_ID, page_size=10
        )
        path = c._data_session.get.call_args[0][0]
        params = c._data_session.get.call_args[1]["params"]
        assert path == (f"payments/merchant-accounts/{MERCHANT_ACCOUNT_ID}/saved-payment-methods")
        assert params["effectiveAccountId"] == ACCOUNT_ID
        assert params["pageSize"] == 10
        await c.close()

    async def test_create_saved_payment_method(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.create_saved_payment_method(
            MERCHANT_ACCOUNT_ID, {"paymentMethodType": "card"}
        )
        path = c._data_session.post.call_args[0][0]
        assert path == (f"payments/merchant-accounts/{MERCHANT_ACCOUNT_ID}/saved-payment-methods")
        await c.close()

    async def test_update_saved_payment_method(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.patch = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.update_saved_payment_method(
            MERCHANT_ACCOUNT_ID,
            SAVED_PAYMENT_METHOD_ID,
            {"isDefault": True},
            effective_account_id=ACCOUNT_ID,
        )
        path = c._data_session.patch.call_args[0][0]
        params = c._data_session.patch.call_args[1]["params"]
        assert path == (
            f"payments/merchant-accounts/{MERCHANT_ACCOUNT_ID}"
            f"/saved-payment-methods/{SAVED_PAYMENT_METHOD_ID}"
        )
        assert params["effectiveAccountId"] == ACCOUNT_ID
        await c.close()

    async def test_delete_saved_payment_method(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.delete = AsyncMock(return_value=_mock_response(204))
        await c.payments.delete_saved_payment_method(
            MERCHANT_ACCOUNT_ID,
            SAVED_PAYMENT_METHOD_ID,
            effective_account_id=ACCOUNT_ID,
        )
        path = c._data_session.delete.call_args[0][0]
        assert path == (
            f"payments/merchant-accounts/{MERCHANT_ACCOUNT_ID}"
            f"/saved-payment-methods/{SAVED_PAYMENT_METHOD_ID}"
        )
        await c.close()

    async def test_create_save_payment_method_token(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.create_save_payment_method_token(
            MERCHANT_ACCOUNT_ID, {"paymentGatewayId": "x"}
        )
        path = c._data_session.post.call_args[0][0]
        assert path == (
            f"payments/merchant-accounts/{MERCHANT_ACCOUNT_ID}/saved-payment-methods/saveToken"
        )
        await c.close()

    async def test_get_payment_link_details(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.get = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.get_payment_link_details(PAYMENT_LINK_ID)
        path = c._data_session.get.call_args[0][0]
        assert path == f"payments/payment-link-configs/{PAYMENT_LINK_ID}"
        await c.close()

    async def test_create_payment_link_order(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        await c.open()
        c._data_session.post = AsyncMock(return_value=_mock_response(200, {}))
        await c.payments.create_payment_link_order(PAYMENT_LINK_ID, {"paymentMethod": "x"})
        path = c._data_session.post.call_args[0][0]
        assert path == f"payments/link-to-order/{PAYMENT_LINK_ID}"
        await c.close()


# ---------------------------------------------------------------------------
# ConnectClient.from_env / from_org
# ---------------------------------------------------------------------------


class TestConnectClientFromEnv:
    async def test_from_env_uses_client_creds(self, monkeypatch):
        monkeypatch.setenv("SF_CONNECT_CLIENT_ID", "cid")
        monkeypatch.setenv("SF_CONNECT_CLIENT_SECRET", "csecret")
        monkeypatch.setenv("SF_CONNECT_INSTANCE_URL", INSTANCE_URL)

        with patch(
            "salesforce_py.connect.client.fetch_org_token",
            new=AsyncMock(return_value=("tok", INSTANCE_URL)),
        ):
            client = await ConnectClient.from_env()
        assert client._session._access_token == "tok"
        await client.close()

    async def test_from_env_uses_sf_instance_url_fallback(self, monkeypatch):
        monkeypatch.setenv("SF_CONNECT_CLIENT_ID", "cid")
        monkeypatch.setenv("SF_CONNECT_CLIENT_SECRET", "csecret")
        monkeypatch.delenv("SF_CONNECT_INSTANCE_URL", raising=False)
        monkeypatch.setenv("SF_INSTANCE_URL", INSTANCE_URL)

        with patch(
            "salesforce_py.connect.client.fetch_org_token",
            new=AsyncMock(return_value=("tok", INSTANCE_URL)),
        ):
            client = await ConnectClient.from_env()
        assert client._session._access_token == "tok"
        await client.close()

    async def test_from_env_falls_back_to_sf_cli(self, monkeypatch):
        monkeypatch.delenv("SF_CONNECT_CLIENT_ID", raising=False)
        monkeypatch.delenv("SF_CONNECT_CLIENT_SECRET", raising=False)

        mock_org = MagicMock()
        mock_org.instance_url = INSTANCE_URL
        mock_org.access_token = ACCESS_TOKEN

        with patch("salesforce_py.sf.org.SFOrg", return_value=mock_org):
            client = await ConnectClient.from_env(target_org="my-alias")
        assert client._session._access_token == ACCESS_TOKEN
        await client.close()

    async def test_from_env_raises_without_creds_or_org(self, monkeypatch):
        monkeypatch.delenv("SF_CONNECT_CLIENT_ID", raising=False)
        monkeypatch.delenv("SF_CONNECT_CLIENT_SECRET", raising=False)
        with pytest.raises(SalesforcePyError, match="SF_CONNECT_CLIENT_ID"):
            await ConnectClient.from_env()

    async def test_from_env_raises_missing_instance_url(self, monkeypatch):
        monkeypatch.setenv("SF_CONNECT_CLIENT_ID", "cid")
        monkeypatch.setenv("SF_CONNECT_CLIENT_SECRET", "csecret")
        monkeypatch.delenv("SF_CONNECT_INSTANCE_URL", raising=False)
        monkeypatch.delenv("SF_INSTANCE_URL", raising=False)
        with pytest.raises(SalesforcePyError, match="instance URL"):
            await ConnectClient.from_env()

    def test_from_org_uses_org_credentials(self):
        mock_org = MagicMock()
        mock_org.instance_url = INSTANCE_URL
        mock_org.access_token = ACCESS_TOKEN

        client = ConnectClient.from_org(mock_org)
        assert client._session._access_token == ACCESS_TOKEN
        assert client._session._instance_url == INSTANCE_URL
