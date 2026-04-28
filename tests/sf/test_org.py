"""Tests for salesforce_py.sf.org.SFOrg."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from salesforce_py.sf.org import SFOrg


# ---------------------------------------------------------------------------
# SFOrg initialisation
# ---------------------------------------------------------------------------


def test_sforg_default_not_connected():
    org = SFOrg("my-org")
    assert not org.is_connected()
    assert org.target_org == "my-org"


def test_sforg_none_target():
    org = SFOrg()
    assert org.target_org is None


# ---------------------------------------------------------------------------
# SFOrg.env() — env dict composition
# ---------------------------------------------------------------------------


def test_env_includes_sf_defaults():
    org = SFOrg("test-org")
    env = org.env()
    assert env["SF_AUTOUPDATE_DISABLE"] == "true"
    assert env["SF_DISABLE_TELEMETRY"] == "true"
    assert env["SF_CONTAINER_MODE"] == "true"


def test_env_injects_credentials_when_connected():
    org = SFOrg("test-org")
    org.instance_url = "https://login.salesforce.com"
    org.access_token = "abc123"
    org._connected = True

    env = org.env()

    assert env["SF_INSTANCE_URL"] == "https://login.salesforce.com"
    assert env["SF_ACCESS_TOKEN"] == "abc123"


def test_env_no_credentials_when_not_connected():
    org = SFOrg("test-org")
    env = org.env()
    assert "SF_ACCESS_TOKEN" not in env
    assert "SF_INSTANCE_URL" not in env


# ---------------------------------------------------------------------------
# SFOrg.connect() — uses subprocess via _run_raw
# ---------------------------------------------------------------------------


def test_connect_populates_fields(sample_org_list):
    org = SFOrg("DevHub")
    display_result = {
        "result": {
            "instanceUrl": "https://login.salesforce.com",
            "accessToken": "TOKEN",
            "username": "devhub@example.com",
            "id": "00D000000000001EAA",
            "alias": "DevHub",
            "isScratch": False,
        }
    }

    with patch.object(org, "_run_raw", return_value=display_result):
        success = org.connect()

    assert success is True
    assert org.is_connected()
    assert org.username == "devhub@example.com"
    assert org.instance_url == "https://login.salesforce.com"
    assert org.org_id == "00D000000000001EAA"
    assert org.is_scratch is False


def test_connect_returns_false_on_error():
    org = SFOrg("bad-org")
    from salesforce_py.exceptions import SalesforcePyError

    with patch.object(org, "_run_raw", side_effect=SalesforcePyError("auth failed")):
        success = org.connect()

    assert success is False
    assert not org.is_connected()


# ---------------------------------------------------------------------------
# SFOrg.__repr__
# ---------------------------------------------------------------------------


def test_repr_includes_target_org():
    org = SFOrg("my-org")
    assert "my-org" in repr(org)
    assert "False" in repr(org)
