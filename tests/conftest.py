"""Shared pytest fixtures for salesforce-py tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def mock_runner():
    """Patch ``salesforce_py.sf._runner.run`` with a configurable async mock.

    Yields the :class:`unittest.mock.AsyncMock` so individual tests can set
    ``mock_runner.return_value`` or ``mock_runner.side_effect`` as needed.

    Usage::

        async def test_something(mock_runner):
            mock_runner.return_value = {"status": 0, "result": {}}
            result = await some_function()
            mock_runner.assert_awaited_once_with(["org", "list"])
    """
    with patch("salesforce_py.sf._runner.run", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def sample_org_list() -> dict[str, Any]:
    """Return a realistic ``sf org list --json`` response with two orgs."""
    return {
        "status": 0,
        "result": {
            "nonScratchOrgs": [
                {
                    "orgId": "00D000000000001EAA",
                    "instanceUrl": "https://login.salesforce.com",
                    "loginUrl": "https://login.salesforce.com",
                    "username": "devhub@example.com",
                    "clientId": "PlatformCLI",
                    "connectedStatus": "Connected",
                    "isDevHub": True,
                    "alias": "DevHub",
                    "lastUsed": "2026-04-27T10:00:00.000Z",
                },
            ],
            "scratchOrgs": [
                {
                    "orgId": "00D000000000002EAA",
                    "instanceUrl": "https://cs1.salesforce.com",
                    "loginUrl": "https://test.salesforce.com",
                    "username": "test-abc123@example.com",
                    "clientId": "PlatformCLI",
                    "connectedStatus": "Connected",
                    "isDevHub": False,
                    "alias": "MyScratch",
                    "devHubUsername": "devhub@example.com",
                    "expirationDate": "2026-05-05",
                    "isExpired": False,
                    "lastUsed": "2026-04-28T08:30:00.000Z",
                },
            ],
        },
        "warnings": [],
    }
