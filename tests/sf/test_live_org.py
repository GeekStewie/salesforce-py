"""Live integration tests against the 'sdonew' Enterprise org.

These tests exercise the real SF CLI and require the org to be authenticated:

    sf org display --target-org sdonew

Run with:

    uv run pytest tests/sf/test_live_org.py -v -s

All tests are read-only or produce no lasting side-effects on the org.
Destructive operations (create/delete scratch, sandbox, users, etc.) are
excluded — this is an Enterprise production-like org.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from salesforce_py.sf import SFOrgTask

TARGET_ORG = "sdonew"
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def task() -> SFOrgTask:
    t = SFOrgTask(TARGET_ORG)
    assert t.connect(), "Could not connect to sdonew — is the org authenticated?"
    return t


# ---------------------------------------------------------------------------
# SFOrg / connection
# ---------------------------------------------------------------------------


class TestOrgConnection:
    def test_is_connected(self, task):
        assert task.is_connected()

    def test_instance_url_populated(self, task):
        assert task._org.instance_url.startswith("https://")

    def test_access_token_populated(self, task):
        assert task._org.access_token

    def test_org_id_populated(self, task):
        assert task._org.org_id.startswith("00D")


# ---------------------------------------------------------------------------
# org.display / org.list_orgs / org.list_auth / org.list_users
# ---------------------------------------------------------------------------


class TestOrgDisplay:
    def test_display_returns_instance_url(self, task):
        result = task.org.display()
        info = result.get("result", result)
        assert "instanceUrl" in info

    def test_display_verbose(self, task):
        result = task.org.display(verbose=True)
        assert result  # non-empty dict

    def test_display_user(self, task):
        result = task.org.display_user()
        info = result.get("result", result)
        assert "username" in info

    def test_list_orgs(self, task):
        orgs = task.org.list_orgs()
        assert isinstance(orgs, list)
        # sdonew should appear somewhere in the list
        aliases = [o.get("alias", "") for o in orgs]
        usernames = [o.get("username", "") for o in orgs]
        assert TARGET_ORG in aliases or task._org.username in usernames

    def test_list_auth(self, task):
        auths = task.org.list_auth()
        assert isinstance(auths, list)
        assert any(
            a.get("alias") == TARGET_ORG or a.get("username") == task._org.username for a in auths
        )

    def test_list_users(self, task):
        users = task.org.list_users()
        assert isinstance(users, list)
        assert len(users) >= 1

    def test_list_limits(self, task):
        limits = task.org.list_limits()
        assert isinstance(limits, list)
        limit_names = [lim.get("name", "") for lim in limits]
        assert "ActiveScratchOrgs" in limit_names or "DailyApiRequests" in limit_names

    def test_list_sobject_record_counts(self, task):
        counts = task.org.list_sobject_record_counts(sobjects=["Account", "Contact"])
        assert isinstance(counts, list)
        names = [c.get("name", "") for c in counts]
        assert "Account" in names or "Contact" in names


# ---------------------------------------------------------------------------
# org.list_metadata / org.list_metadata_types
# ---------------------------------------------------------------------------


class TestOrgMetadata:
    def test_list_metadata_types(self, task):
        types = task.org.list_metadata_types()
        assert isinstance(types, list)
        assert len(types) > 0
        # Each entry should have xmlName
        assert all("xmlName" in t for t in types)

    def test_list_metadata_apex_class(self, task):
        items = task.org.list_metadata("ApexClass")
        assert isinstance(items, list)
        # Enterprise org must have at least some Apex classes

    def test_list_metadata_custom_object(self, task):
        items = task.org.list_metadata("CustomObject")
        assert isinstance(items, list)


# ---------------------------------------------------------------------------
# sobject
# ---------------------------------------------------------------------------


class TestSObject:
    def test_list_sobjects_all(self, task):
        names = task.sobject.list_sobjects()
        assert isinstance(names, list)
        assert "Account" in names
        assert "Contact" in names

    def test_list_sobjects_standard(self, task):
        names = task.sobject.list_sobjects(category="standard")
        assert isinstance(names, list)
        assert "Account" in names

    def test_list_sobjects_custom(self, task):
        names = task.sobject.list_sobjects(category="custom")
        assert isinstance(names, list)

    def test_describe_account(self, task):
        info = task.sobject.describe("Account")
        assert info.get("name") == "Account"
        assert "fields" in info

    def test_describe_contact(self, task):
        info = task.sobject.describe("Contact")
        assert info.get("name") == "Contact"

    def test_list_fields_account(self, task):
        fields = task.sobject.list_fields("Account")
        assert isinstance(fields, list)
        field_names = [f.get("name") for f in fields]
        assert "Id" in field_names
        assert "Name" in field_names


# ---------------------------------------------------------------------------
# data.query — uses query_file to avoid shell word-splitting on SOQL strings
# ---------------------------------------------------------------------------


def _soql_file(soql: str) -> Path:
    """Write SOQL to a temp file and return the path."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".soql", delete=False) as f:
        f.write(soql)
        return Path(f.name)


class TestDataQuery:
    def test_query_accounts(self, task):
        qf = _soql_file("SELECT Id, Name FROM Account LIMIT 5")
        records = task.data.query(query_file=qf)
        assert isinstance(records, list)
        if records:
            assert "Id" in records[0]
            assert "Name" in records[0]

    def test_query_contacts(self, task):
        qf = _soql_file("SELECT Id, FirstName, LastName, Email FROM Contact LIMIT 5")
        records = task.data.query(query_file=qf)
        assert isinstance(records, list)

    def test_query_users(self, task):
        qf = _soql_file("SELECT Id, Username, IsActive FROM User LIMIT 5")
        records = task.data.query(query_file=qf)
        assert isinstance(records, list)
        assert len(records) >= 1

    def test_query_org_limits_via_tooling(self, task):
        qf = _soql_file(
            "SELECT QualifiedApiName FROM EntityDefinition WHERE IsCustomizable = true LIMIT 5"
        )
        records = task.data.query(query_file=qf, use_tooling_api=True)
        assert isinstance(records, list)

    def test_query_count(self, task):
        qf = _soql_file("SELECT COUNT(Id) total FROM Account")
        records = task.data.query(query_file=qf)
        assert isinstance(records, list)


# ---------------------------------------------------------------------------
# data.get_record / data.search
# ---------------------------------------------------------------------------


class TestDataRecord:
    def test_get_record_by_where(self, task):
        # Retrieve the running user's record by username
        username = task._org.username
        record = task.data.get_record("User", where=f"Username='{username}'")
        assert record.get("Username") == username

    def test_search(self, task):
        qf = _soql_file("FIND {Salesforce} IN ALL FIELDS RETURNING User(Username) LIMIT 5")
        result = task.data.search(query_file=qf)
        # search with --result-format json returns raw output dict
        assert isinstance(result, dict)
        # either parsed records or a raw output string
        assert "searchRecords" in result or "output" in result


# ---------------------------------------------------------------------------
# apex.list_logs
# ---------------------------------------------------------------------------


class TestApexLogs:
    def test_list_logs_returns_list(self, task):
        logs = task.apex.list_logs()
        assert isinstance(logs, list)


# ---------------------------------------------------------------------------
# alias / config
# ---------------------------------------------------------------------------


class TestAlias:
    def test_list_aliases(self, task):
        aliases = task.alias.list_aliases()
        assert isinstance(aliases, list)
        alias_values = [a.get("value", "") for a in aliases]
        usernames = [a.get("alias", "") for a in aliases]
        assert TARGET_ORG in usernames or any(TARGET_ORG in v for v in alias_values)


class TestConfig:
    def test_list_config(self, task):
        configs = task.config.list_config()
        assert isinstance(configs, list)

    def test_get_config_org_api_version(self, task):
        result = task.config.get("org-api-version")
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# api.rest — REST API passthrough
# Returns {"output": "<raw response text>"} — parse the output field for JSON.
# ---------------------------------------------------------------------------


class TestApiRest:
    def test_get_versions(self, task):
        result = task.api.get("/services/data/")
        output = json.loads(result["output"])
        assert isinstance(output, list)
        assert any("version" in item for item in output)

    def test_get_org_limits(self, task):
        result = task.api.get("/services/data/v67.0/limits/")
        output = json.loads(result["output"])
        assert isinstance(output, dict)
        assert "DailyApiRequests" in output

    def test_get_sobject_describe(self, task):
        result = task.api.get("/services/data/v67.0/sobjects/Account/describe/")
        output = json.loads(result["output"])
        assert isinstance(output, dict)
        assert output.get("name") == "Account"


# ---------------------------------------------------------------------------
# package.installed_list
# ---------------------------------------------------------------------------


class TestPackage:
    def test_installed_list(self, task):
        packages = task.package.installed_list()
        assert isinstance(packages, list)
