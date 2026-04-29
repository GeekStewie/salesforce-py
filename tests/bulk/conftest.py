"""Shared fixtures + helpers for the Bulk API test suite."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import httpx

INSTANCE_URL = "https://myorg.my.salesforce.com"
ACCESS_TOKEN = "bulk_test_token"


def make_response(
    status_code: int,
    *,
    json_body: dict | None = None,
    content: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> MagicMock:
    """Build a mock ``httpx.Response`` for Bulk API tests.

    Matches the shape used in tests/data360/test_data360.py — a MagicMock
    that mimics the attributes the client reads from a real response
    (``status_code``, ``content``, ``headers``, ``json()``,
    ``raise_for_status()``).
    """
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    if content is not None:
        resp.content = content
    elif json_body is not None:
        resp.content = b"ok"
    else:
        resp.content = b""
    resp.text = str(json_body) if json_body else ""
    resp.url = f"{INSTANCE_URL}/services/data/v66.0/jobs/test"
    resp.headers = headers or {}
    if json_body is not None:
        resp.json.return_value = json_body
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=resp
        )
    else:
        resp.raise_for_status.return_value = None
    return resp


async def make_client(
    *,
    mock_get=None,
    mock_post=None,
    mock_patch=None,
    mock_put=None,
    mock_delete=None,
):
    """Open a :class:`BulkClient` and replace its session verbs with AsyncMocks."""
    from salesforce_py.bulk.client import BulkClient

    client = BulkClient(INSTANCE_URL, ACCESS_TOKEN)
    await client.open()
    if mock_get is not None:
        client._session.get = AsyncMock(return_value=mock_get)
    if mock_post is not None:
        client._session.post = AsyncMock(return_value=mock_post)
    if mock_patch is not None:
        client._session.patch = AsyncMock(return_value=mock_patch)
    if mock_put is not None:
        client._session.put = AsyncMock(return_value=mock_put)
    if mock_delete is not None:
        client._session.delete = AsyncMock(return_value=mock_delete)
    return client
