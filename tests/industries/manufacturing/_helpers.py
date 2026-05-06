"""Shared helpers for industries.manufacturing tests.

Mirrors the patterns in ``tests/connect/test_connect.py`` — local helpers, not
pytest fixtures, so they can be imported and called explicitly.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx

from salesforce_py.connect.client import ConnectClient

INSTANCE_URL = "https://test.my.salesforce.com"
ACCESS_TOKEN = "test_token_abc"


def _mock_response(
    status_code: int, json_body: dict[str, Any] | None = None
) -> MagicMock:
    """Build a mock ``httpx.Response`` with the given status and JSON body."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.content = b"ok" if json_body is not None else b""
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


async def _client(post_response: MagicMock) -> ConnectClient:
    """Open a ConnectClient with ``c._session.post`` patched to return ``post_response``."""
    c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
    await c.open()
    c._session.post = AsyncMock(return_value=post_response)
    return c
