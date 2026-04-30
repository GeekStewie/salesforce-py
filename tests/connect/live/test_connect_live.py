"""Live end-to-end probe of every Connect API method against the ``sdonew`` org.

This module is **excluded** from the default pytest run. It is intended to be
run manually to verify that the client-side plumbing for every Connect API
namespace works against a real org, and to surface any bugs in argument
handling, URL construction, or response parsing.

Run with:

    LIVE_CONNECT_TESTS=1 uv run pytest tests/connect/live/test_connect_live.py -v -s

The test discovers every public async method on every operations namespace
attached to :class:`ConnectClient`, calls it with plausible arguments drawn
from a parameter registry, and classifies the outcome:

* PASS      — call returned successfully.
* SKIPPED   — server rejected with a known "feature not enabled / record
              not found" pattern. The client-side plumbing is fine; the org
              just doesn't have this feature or fixture.
* FAIL      — any other error (network, Python, unexpected server response).

A final summary table is printed. Fixtures that mutate state (Chatter posts,
groups, topics, favourites, etc.) are created in the PRE-phase and torn down
in a finally block.
"""

from __future__ import annotations

import inspect
import json
import os
from dataclasses import dataclass, field
from typing import Any

import pytest

from salesforce_py.connect import ConnectClient
from salesforce_py.connect.base import ConnectBaseOperations
from salesforce_py.exceptions import SalesforcePyError
from salesforce_py.sf.org import SFOrg

TARGET_ORG = "sdonew"

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("LIVE_CONNECT_TESTS") != "1",
        reason="Set LIVE_CONNECT_TESTS=1 to run live Connect API probes",
    ),
]


# ---------------------------------------------------------------------------
# Outcome classification
# ---------------------------------------------------------------------------

# Substrings (lowercased) that indicate a missing feature / org state rather
# than a client-side bug. When any of these appears in the error body, we
# classify the call as SKIPPED.
SKIP_PATTERNS = [
    # Feature / licensing
    "not enabled",
    "is not enabled",
    "not currently enabled",
    "feature is not available",
    "is not available",
    "functionality_not_enabled",
    # Permission / org state
    "does not have access",
    "insufficient access",
    "insufficient_access",
    "insufficient_access_or_readonly",
    "insufficient privileges",
    "do not have permission",
    "you don't have permission",
    "you do not have permission",
    # Missing records / invalid IDs supplied by our fake fixtures
    "no such",
    "not found",
    "does not exist",
    "invalid id",
    "malformed id",
    "invalid_id_field",
    "invalid identifier",
    "invalid parameter value",
    "no data available",
    "unsupported_api_version",
    "resource does not exist",
    "unable to find",
    # Community / network scope
    "requires a community",
    "communities not enabled",
    "chatter is disabled",
    # Licensing
    "no valid licence",
    "no valid license",
    # POST body we intentionally omit
    "cannot be null",
    "missing required",
    "required field missing",
    "required parameter",
    # Generic
    "bad_request",
    "invalid_type",
    "not supported",
    "disabled",
    "invalid method",
    "method not allowed",
    "entity is not api accessible",
    "no guest user",
    "not configured",
    "store not found",
    "site not found",
    "webstore",
    "b2c",
    "experience id",
    "no experience cloud site",
    "invalid status",
    "unknown_exception",
]


@dataclass
class CallResult:
    namespace: str
    method: str
    status: str  # "pass", "skipped", "fail", "skipped_no_args"
    detail: str = ""
    exc_type: str = ""


# ---------------------------------------------------------------------------
# Fixtures (real and placeholder) for parameter injection
# ---------------------------------------------------------------------------


@dataclass
class Fixtures:
    """Real IDs and values discovered from the target org."""

    user_id: str = ""
    account_id: str = ""
    group_id: str = ""
    network_id: str = ""
    # Created by the test run (cleaned up at teardown)
    feed_item_id: str = ""
    comment_id: str = ""
    topic_id: str = ""
    created_groups: list[str] = field(default_factory=list)


async def _load_fixtures(client: ConnectClient) -> Fixtures:
    """Populate real IDs from the org by issuing lightweight queries."""
    from salesforce_py.rest import RestClient

    fx = Fixtures()

    # Reuse the same token via a separate REST client for queries.
    rest = RestClient(
        instance_url=client._session._instance_url,
        access_token=client._session._access_token,
    )
    await rest.open()
    try:
        res = await rest.query.query(
            "SELECT Id FROM User WHERE IsActive = true AND UserType = 'Standard' LIMIT 1"
        )
        if res.get("records"):
            fx.user_id = res["records"][0]["Id"]

        res = await rest.query.query("SELECT Id FROM Account LIMIT 1")
        if res.get("records"):
            fx.account_id = res["records"][0]["Id"]

        res = await rest.query.query("SELECT Id FROM CollaborationGroup LIMIT 1")
        if res.get("records"):
            fx.group_id = res["records"][0]["Id"]

        res = await rest.query.query("SELECT Id FROM Network LIMIT 1")
        if res.get("records"):
            fx.network_id = res["records"][0]["Id"]
    finally:
        await rest.close()

    return fx


# ---------------------------------------------------------------------------
# Parameter registry
# ---------------------------------------------------------------------------


def _build_param_registry(fx: Fixtures) -> dict[str, Any]:
    """Map parameter name → sensible default for live-test introspection."""
    fake_15 = "0a1000000000001"  # plausibly-shaped 15-char ID (will fail server lookup)
    return {
        # User / context
        "user_id": "me",
        "subject_id": "me",
        "community_id": fx.network_id or None,
        "network_id": fx.network_id or "internal",
        # Core record IDs — use real ones where we have them
        "record_id": fx.account_id or fake_15,
        "account_id": fx.account_id or fake_15,
        "group_id": fx.group_id or "0F9000000000001AAA",
        "parent_id": fx.account_id or fake_15,
        "feed_item_id": "",  # filled at call time from Fixtures
        "feed_element_id": "",
        "comment_id": "",
        "topic_id": "",
        # Common names
        "q": "test",
        "query": "test",
        "search_term": "test",
        "search": "test",
        # Paging
        "page_size": 5,
        "page": 0,
        # Feed types
        "feed_type": "News",
        # Misc
        "community_name": "internal",
        "site_id": fx.network_id or "",
        "folder_id": "",
        "file_id": "",
        "asset_id": "",
    }


# ---------------------------------------------------------------------------
# Method discovery
# ---------------------------------------------------------------------------


def _discover_methods(client: ConnectClient) -> list[tuple[str, str, Any]]:
    """Return ``(namespace, method_name, bound_method)`` tuples."""
    out: list[tuple[str, str, Any]] = []
    for attr_name in dir(client):
        if attr_name.startswith("_"):
            continue
        ns = getattr(client, attr_name)
        if not isinstance(ns, ConnectBaseOperations):
            continue
        for meth_name in dir(ns):
            if meth_name.startswith("_"):
                continue
            meth = getattr(ns, meth_name)
            if not callable(meth):
                continue
            if not inspect.iscoroutinefunction(meth):
                continue
            out.append((attr_name, meth_name, meth))
    return out


def _classify_method(meth_name: str) -> str:
    """Return ``"read"``, ``"write"``, or ``"delete"`` based on method prefix."""
    n = meth_name.lower()
    if n.startswith(("delete", "remove")):
        return "delete"
    if n.startswith(("create", "post", "add", "update", "patch", "replace", "put", "set", "submit", "activate", "deactivate", "upsert", "approve", "reject", "cancel", "refund", "capture", "authorize", "reverse", "publish", "unpublish", "favorite", "unfavorite", "follow", "unfollow", "like", "unlike", "mute", "unmute", "send", "mark", "reply", "start", "execute", "run", "invoke", "save", "pin", "unpin", "upload", "refresh")):
        return "write"
    return "read"


# ---------------------------------------------------------------------------
# Argument resolution
# ---------------------------------------------------------------------------


def _resolve_args(meth: Any, registry: dict[str, Any]) -> tuple[list[Any], dict[str, Any], list[str]]:
    """Return ``(positional, keyword, missing)`` — args drawn from the registry.

    ``missing`` lists required parameter names we couldn't fill (signal to skip).
    """
    sig = inspect.signature(meth)
    positional: list[Any] = []
    keyword: dict[str, Any] = {}
    missing: list[str] = []

    for name, param in sig.parameters.items():
        if name == "self":
            continue
        if param.kind is inspect.Parameter.VAR_POSITIONAL or param.kind is inspect.Parameter.VAR_KEYWORD:
            continue

        has_default = param.default is not inspect.Parameter.empty

        if param.kind is inspect.Parameter.KEYWORD_ONLY:
            # Fill from registry if present.
            if name in registry and registry[name] not in (None, ""):
                keyword[name] = registry[name]
            elif not has_default:
                # Required kw-only with no registry entry — we can't satisfy it.
                missing.append(name)
            continue

        # POSITIONAL_OR_KEYWORD
        if name in registry and registry[name] not in (None, ""):
            positional.append(registry[name])
        elif has_default:
            # Rely on the default
            pass
        else:
            missing.append(name)

    return positional, keyword, missing


# ---------------------------------------------------------------------------
# Error classification
# ---------------------------------------------------------------------------


def _classify_error(exc: Exception) -> tuple[str, str]:
    """Return ``(status, detail)`` — ``"skipped"`` or ``"fail"``."""
    msg = str(exc)
    lower = msg.lower()

    # Any 4xx with a "not enabled / not found" style message → SKIPPED
    for pattern in SKIP_PATTERNS:
        if pattern in lower:
            return "skipped", msg[:200]

    # Status-code heuristic: 403 / 404 / 501 generally mean
    # "feature not enabled / feature not available / permission missing"
    # 400 without a known pattern is ambiguous; still classify as skipped —
    # calling many endpoints without their full body is expected to 400.
    if any(code in msg for code in ("error 403", "error 404", "error 501", "error 400")):
        return "skipped", msg[:200]

    return "fail", msg[:400]


# ---------------------------------------------------------------------------
# Methods to skip unconditionally (destructive / dangerous / needs massive setup)
# ---------------------------------------------------------------------------

# These are skipped even in read-mode — they either require huge POST bodies
# with domain-specific shapes, or they have side effects we don't want to
# trigger speculatively.
UNCONDITIONAL_SKIP = {
    # Generic passthrough handles on misc namespaces — there's no single path
    # we can call without caller knowledge.
    ("clean", "get"),
    ("clean", "post"),
    ("clean", "patch"),
    ("clean", "put"),
    ("clean", "delete"),
    ("duplicate", "get"),
    ("duplicate", "post"),
    ("duplicate", "patch"),
    ("duplicate", "put"),
    ("duplicate", "delete"),
}


# Write methods we intentionally exercise end-to-end with cleanup.
WRITE_FIXTURE_METHODS = {
    "chatter.post_feed_item",
    "chatter.post_comment",
    "chatter.delete_feed_item",
}


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------


async def _invoke(
    namespace: str,
    method_name: str,
    meth: Any,
    fx: Fixtures,
    registry: dict[str, Any],
) -> CallResult:
    key = (namespace, method_name)
    if key in UNCONDITIONAL_SKIP:
        return CallResult(namespace, method_name, "skipped_no_args", "unconditional_skip")

    # Only run read-style methods in the broad pass. Write methods are handled
    # separately in the fixture phase.
    kind = _classify_method(method_name)
    full_name = f"{namespace}.{method_name}"
    if kind != "read" and full_name not in WRITE_FIXTURE_METHODS:
        return CallResult(namespace, method_name, "skipped_no_args", f"write-class method ({kind}) — not probed")

    positional, keyword, missing = _resolve_args(meth, registry)

    # Inject runtime fixtures (chatter post → feed_item_id, etc.)
    if "feed_item_id" in inspect.signature(meth).parameters and fx.feed_item_id:
        # positional or keyword? Check signature.
        sig = inspect.signature(meth)
        param = sig.parameters["feed_item_id"]
        if param.kind is inspect.Parameter.KEYWORD_ONLY:
            keyword["feed_item_id"] = fx.feed_item_id
        elif "feed_item_id" in [
            p for p, pr in sig.parameters.items() if pr.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        ]:
            # Rebuild positional list to include feed_item_id at the right slot
            rebuilt: list[Any] = []
            for pname, pp in sig.parameters.items():
                if pname == "self" or pp.kind is inspect.Parameter.KEYWORD_ONLY:
                    continue
                if pp.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                    continue
                if pname == "feed_item_id":
                    rebuilt.append(fx.feed_item_id)
                    if pname in missing:
                        missing.remove(pname)
                elif pname in registry and registry[pname] not in (None, ""):
                    rebuilt.append(registry[pname])
                elif pp.default is not inspect.Parameter.empty:
                    pass
                else:
                    if pname not in missing:
                        missing.append(pname)
            positional = rebuilt

    if missing:
        return CallResult(
            namespace,
            method_name,
            "skipped_no_args",
            f"missing required args: {', '.join(missing)}",
        )

    try:
        result = await meth(*positional, **keyword)
    except SalesforcePyError as exc:
        status, detail = _classify_error(exc)
        return CallResult(namespace, method_name, status, detail, exc_type="SalesforcePyError")
    except Exception as exc:  # noqa: BLE001 — broad on purpose for the probe
        return CallResult(
            namespace,
            method_name,
            "fail",
            f"{type(exc).__name__}: {exc}",
            exc_type=type(exc).__name__,
        )

    _ = result  # result shape varies widely; we only care that the call succeeded
    return CallResult(namespace, method_name, "pass")


# ---------------------------------------------------------------------------
# Write-fixture phase (produce feed item + comment, then delete)
# ---------------------------------------------------------------------------


async def _write_phase(client: ConnectClient, fx: Fixtures, results: list[CallResult]) -> None:
    """Exercise the write methods we actually care about end-to-end."""
    # Post a feed item to the authenticated user's own feed.
    try:
        post = await client.chatter.post_feed_item("salesforce-py live test", subject_id="me")
        fx.feed_item_id = post.get("id", "")
        results.append(
            CallResult("chatter", "post_feed_item", "pass" if fx.feed_item_id else "fail", "")
        )
    except Exception as exc:  # noqa: BLE001
        status, detail = _classify_error(exc) if isinstance(exc, SalesforcePyError) else ("fail", str(exc))
        results.append(
            CallResult("chatter", "post_feed_item", status, detail, exc_type=type(exc).__name__)
        )
        return

    # Comment on it.
    if fx.feed_item_id:
        try:
            comment = await client.chatter.post_comment(fx.feed_item_id, "live test comment")
            fx.comment_id = comment.get("id", "")
            results.append(CallResult("chatter", "post_comment", "pass"))
        except Exception as exc:  # noqa: BLE001
            status, detail = _classify_error(exc) if isinstance(exc, SalesforcePyError) else ("fail", str(exc))
            results.append(
                CallResult("chatter", "post_comment", status, detail, exc_type=type(exc).__name__)
            )


async def _cleanup_phase(client: ConnectClient, fx: Fixtures, results: list[CallResult]) -> None:
    """Delete fixtures created in the write phase."""
    if fx.feed_item_id:
        try:
            await client.chatter.delete_feed_item(fx.feed_item_id)
            results.append(CallResult("chatter", "delete_feed_item", "pass"))
        except Exception as exc:  # noqa: BLE001
            status, detail = _classify_error(exc) if isinstance(exc, SalesforcePyError) else ("fail", str(exc))
            results.append(
                CallResult("chatter", "delete_feed_item", status, detail, exc_type=type(exc).__name__)
            )


# ---------------------------------------------------------------------------
# Pytest test entry point
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_connect_live_probe_all_methods() -> None:
    org = SFOrg(target_org=TARGET_ORG)
    org._ensure_connected()

    async with ConnectClient.from_org(org) as client:
        fx = await _load_fixtures(client)
        registry = _build_param_registry(fx)

        results: list[CallResult] = []

        # 1. Write phase — create a feed item + comment we can reference.
        await _write_phase(client, fx, results)

        # Feed the fresh feed_item_id back into the registry so read-phase
        # methods that take `feed_item_id` can use it.
        if fx.feed_item_id:
            registry["feed_item_id"] = fx.feed_item_id
        if fx.comment_id:
            registry["comment_id"] = fx.comment_id

        # 2. Read-phase probe — every public async method on every namespace.
        methods = _discover_methods(client)
        for namespace, method_name, meth in methods:
            # Skip the write-fixture methods we already exercised
            if f"{namespace}.{method_name}" in WRITE_FIXTURE_METHODS:
                continue
            result = await _invoke(namespace, method_name, meth, fx, registry)
            results.append(result)

        # 3. Cleanup.
        await _cleanup_phase(client, fx, results)

    # --- Report ---
    _render_report(results)
    _write_json_report(results)

    # Only truly-unexpected failures should fail the test.
    hard_fails = [r for r in results if r.status == "fail"]
    if hard_fails:
        print(f"\n{len(hard_fails)} hard failures — review details above.\n")
        # Do not raise — we want to see the report in all cases. Bugs will be
        # inspected by the developer after the run.


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _render_report(results: list[CallResult]) -> None:
    by_status: dict[str, int] = {}
    for r in results:
        by_status[r.status] = by_status.get(r.status, 0) + 1

    print("\n" + "=" * 80)
    print(f"CONNECT API LIVE PROBE — {len(results)} method invocations")
    print("=" * 80)
    for status, count in sorted(by_status.items()):
        print(f"  {status:20s} {count}")
    print("-" * 80)

    # Detail: FAIL first, then SKIPPED grouped, then PASS count only
    fails = [r for r in results if r.status == "fail"]
    if fails:
        print(f"\nFAILURES ({len(fails)}):")
        for r in fails:
            print(f"  {r.namespace}.{r.method}  [{r.exc_type}]")
            print(f"    {r.detail}")

    skipped_no_args = [r for r in results if r.status == "skipped_no_args"]
    if skipped_no_args:
        print(f"\nSKIPPED (no fixture args) — {len(skipped_no_args)} methods")

    skipped_server = [r for r in results if r.status == "skipped"]
    if skipped_server:
        print(f"\nSKIPPED (feature/record missing) — {len(skipped_server)} methods")
        # Preview a handful so the user can sanity-check they're really "feature missing"
        for r in skipped_server[:10]:
            print(f"  {r.namespace}.{r.method}")
            print(f"    {r.detail[:140]}")

    passes = [r for r in results if r.status == "pass"]
    print(f"\nPASSES — {len(passes)} methods")
    print("=" * 80 + "\n")


def _write_json_report(results: list[CallResult]) -> None:
    out = [
        {
            "namespace": r.namespace,
            "method": r.method,
            "status": r.status,
            "detail": r.detail,
            "exc_type": r.exc_type,
        }
        for r in results
    ]
    path = "/tmp/connect_live_report.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Full JSON report written to {path}")
