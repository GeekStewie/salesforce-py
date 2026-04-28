"""Tests for salesforce_py.sf.org using the mock_runner fixture."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from salesforce_py.sf.org import display, list_orgs, display_sync, list_orgs_sync


# ---------------------------------------------------------------------------
# list_orgs()
# ---------------------------------------------------------------------------


async def test_list_orgs_calls_correct_args(mock_runner, sample_org_list):
    """list_orgs() must invoke run() with ['org', 'list']."""
    mock_runner.return_value = sample_org_list

    result = await list_orgs()

    mock_runner.assert_awaited_once_with(["org", "list"])
    assert result == sample_org_list


async def test_list_orgs_returns_full_payload(mock_runner, sample_org_list):
    """list_orgs() must return the full dict returned by run()."""
    mock_runner.return_value = sample_org_list

    result = await list_orgs()

    assert "result" in result
    assert len(result["result"]["nonScratchOrgs"]) == 1
    assert len(result["result"]["scratchOrgs"]) == 1


async def test_list_orgs_scratch_org_fields(mock_runner, sample_org_list):
    """The scratch org entry must contain expected fields."""
    mock_runner.return_value = sample_org_list

    result = await list_orgs()

    scratch = result["result"]["scratchOrgs"][0]
    assert scratch["alias"] == "MyScratch"
    assert scratch["isExpired"] is False
    assert scratch["devHubUsername"] == "devhub@example.com"


async def test_list_orgs_devhub_fields(mock_runner, sample_org_list):
    """The DevHub org entry must have isDevHub=True."""
    mock_runner.return_value = sample_org_list

    result = await list_orgs()

    devhub = result["result"]["nonScratchOrgs"][0]
    assert devhub["isDevHub"] is True
    assert devhub["alias"] == "DevHub"


# ---------------------------------------------------------------------------
# display()
# ---------------------------------------------------------------------------


async def test_display_calls_correct_args(mock_runner):
    """display() must invoke run() with the correct --target-org argument."""
    mock_runner.return_value = {
        "status": 0,
        "result": {
            "orgId": "00D000000000001EAA",
            "alias": "DevHub",
            "username": "devhub@example.com",
            "instanceUrl": "https://login.salesforce.com",
            "connectedStatus": "Connected",
        },
    }

    result = await display("DevHub")

    mock_runner.assert_awaited_once_with(
        ["org", "display", "--target-org", "DevHub"]
    )
    assert result["result"]["alias"] == "DevHub"


async def test_display_passes_alias_correctly(mock_runner):
    """display() must forward the alias argument verbatim."""
    mock_runner.return_value = {"status": 0, "result": {}}

    await display("my-scratch-org@example.com")

    args = mock_runner.call_args.args[0]
    assert "--target-org" in args
    target_index = args.index("--target-org")
    assert args[target_index + 1] == "my-scratch-org@example.com"


# ---------------------------------------------------------------------------
# Sync wrappers
# ---------------------------------------------------------------------------


def test_list_orgs_sync_delegates_to_async(mock_runner, sample_org_list):
    """list_orgs_sync() must return the same value as the async variant."""
    mock_runner.return_value = sample_org_list

    result = list_orgs_sync()

    assert result == sample_org_list
    mock_runner.assert_awaited_once_with(["org", "list"])


def test_display_sync_delegates_to_async(mock_runner):
    """display_sync() must return the same value as the async variant."""
    expected = {"status": 0, "result": {"alias": "DevHub"}}
    mock_runner.return_value = expected

    result = display_sync("DevHub")

    assert result == expected
    mock_runner.assert_awaited_once_with(
        ["org", "display", "--target-org", "DevHub"]
    )
