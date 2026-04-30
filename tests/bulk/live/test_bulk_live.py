"""Live end-to-end exercise of the Bulk API 2.0 client against the ``sdonew`` org.

Run with:

    LIVE_BULK_TESTS=1 uv run pytest tests/bulk/live/test_bulk_live.py -v -s

Unlike the Connect / REST probes (which are introspection-driven and fire
every method with plausible args), Bulk API 2.0 has a small, lifecycle-ordered
surface that benefits from hand-written sequencing. This file exercises:

* **Extract** — submit a SOQL query for Accounts and Contacts via bulk query,
  poll to ``JobComplete``, download all pages, reapply ORDER BY client-side,
  and list parallel result locators.
* **Ingest (insert)** — create a handful of marker Accounts via bulk insert
  and read back the success CSV.
* **Ingest (update)** — update those Accounts' Description field.
* **Ingest (delete)** — delete the marker Accounts, cleaning up all state.
* **Admin** — ``get_all_jobs`` for both ingest and query sides.

Every step prints a short status line so ``-s`` gives a human-readable trace.
The test cleans up every record it creates, even on failure, via a ``finally``
block that runs a dedicated bulk-delete pass keyed on the marker prefix.
"""

from __future__ import annotations

import asyncio
import io
import os
import time
from csv import DictReader
from typing import Any

import pytest

from salesforce_py.bulk import BulkClient
from salesforce_py.rest import RestClient
from salesforce_py.sf.org import SFOrg

TARGET_ORG = "sdonew"

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("LIVE_BULK_TESTS") != "1",
        reason="Set LIVE_BULK_TESTS=1 to run live Bulk API tests",
    ),
]


# Unique marker embedded in every record we create so we can find + delete
# stragglers from aborted runs.
MARKER_PREFIX = "salesforce-py-bulk-live"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _unique_suffix() -> str:
    return str(int(time.time()))


async def _poll_job(
    client: BulkClient,
    job_id: str,
    *,
    kind: str,  # "ingest" | "query"
    poll_interval: float = 3.0,
    timeout: float = 600.0,
) -> dict[str, Any]:
    """Poll ingest/query job until terminal state. Returns final job info."""
    ops = client.ingest if kind == "ingest" else client.query
    elapsed = 0.0
    while True:
        info = await ops.get_job(job_id)
        state = info.get("state")
        if state == "JobComplete":
            return info
        if state in ("Failed", "Aborted"):
            raise AssertionError(
                f"{kind} job {job_id} ended in {state!r}: {info.get('errorMessage', '')}"
            )
        if elapsed >= timeout:
            raise AssertionError(
                f"{kind} job {job_id} did not complete within {timeout:g}s "
                f"(last state: {state!r})"
            )
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval


def _csv_rows(payload: bytes) -> list[dict[str, str]]:
    text = payload.decode("utf-8", errors="replace")
    return list(DictReader(io.StringIO(text)))


# ---------------------------------------------------------------------------
# Phases
# ---------------------------------------------------------------------------


async def _phase_extract(client: BulkClient) -> None:
    """Extract Account + Contact data via bulk query end-to-end."""
    print("\n[1/4] EXTRACT — bulk query Account + Contact")

    # Account — exercise the end-to-end run_query convenience.
    soql = "SELECT Id, Name FROM Account ORDER BY Name LIMIT 50"
    print(f"  submitting: {soql}")
    combined = await client.query.run_query(
        soql, poll_interval=3.0, poll_timeout=600.0, auto_delete=True
    )
    rows = _csv_rows(combined)
    print(f"  Account rows returned (post client-side ORDER BY): {len(rows)}")
    assert rows, "expected at least one Account in the org"
    # Verify ORDER BY Name was reapplied client-side
    names = [r["Name"] for r in rows]
    assert names == sorted(names, key=str), "ORDER BY Name not reapplied"

    # Contact — exercise the lifecycle step-by-step so we can touch each method.
    print("  Contact — create_job / get_job poll / get_results pagination")
    job = await client.query.create_job(
        soql="SELECT Id, FirstName, LastName, Email FROM Contact LIMIT 25"
    )
    job_id = job["id"]
    print(f"  job id: {job_id}")
    final = await _poll_job(client, job_id, kind="query")
    assert final["state"] == "JobComplete"

    # Single-page fetch
    page, locator, count = await client.query.get_results(job_id)
    print(f"  first page: {count} records, locator={locator!r}")
    rows = _csv_rows(page)
    assert rows, "expected at least one Contact"

    # Parallel locators (API 58+)
    try:
        locators = await client.query.get_parallel_results(job_id)
        print(f"  parallel locators available: {len(locators)}")
    except Exception as exc:  # noqa: BLE001
        # Not all orgs / API versions support this — log, don't fail.
        print(f"  parallel locators unavailable: {type(exc).__name__}: {exc}")

    await client.query.delete_job(job_id)
    print("  Contact query job deleted")


async def _phase_insert(client: BulkClient) -> list[str]:
    """Bulk-insert three marker Accounts. Return their IDs."""
    print("\n[2/4] INGEST (insert) — 3 marker Accounts")
    suffix = _unique_suffix()
    csv = (
        "Name,Description\n"
        f"{MARKER_PREFIX}-{suffix}-1,row 1 from salesforce-py live test\n"
        f"{MARKER_PREFIX}-{suffix}-2,row 2 from salesforce-py live test\n"
        f"{MARKER_PREFIX}-{suffix}-3,row 3 from salesforce-py live test\n"
    ).encode()

    job = await client.ingest.create_job(object_name="Account", operation="insert")
    job_id = job["id"]
    print(f"  job id: {job_id}, contentUrl: {job['contentUrl']}")

    await client.ingest.upload_data(job_id, csv_data=csv, content_url=job["contentUrl"])
    await client.ingest.upload_complete(job_id)
    print("  upload complete; polling")
    final = await _poll_job(client, job_id, kind="ingest")
    print(
        f"  state={final['state']}, processed={final.get('numberRecordsProcessed')},"
        f" failed={final.get('numberRecordsFailed')}"
    )
    assert final.get("numberRecordsFailed", 0) == 0, "insert failures"

    successes = _csv_rows(await client.ingest.get_successful_results(job_id))
    # Look for Id column case-insensitively — Salesforce returns "sf__Id"
    ids: list[str] = []
    for row in successes:
        rid = row.get("sf__Id") or row.get("Id") or ""
        if rid:
            ids.append(rid)
    assert len(ids) == 3, f"expected 3 inserted IDs, got {ids}"
    print(f"  inserted IDs: {ids}")

    # Failed + unprocessed should be empty but fetchable
    failed = await client.ingest.get_failed_results(job_id)
    unprocessed = await client.ingest.get_unprocessed_results(job_id)
    print(f"  failed CSV bytes: {len(failed)}, unprocessed CSV bytes: {len(unprocessed)}")

    await client.ingest.delete_job(job_id)
    print("  insert job deleted")
    return ids


async def _phase_update(client: BulkClient, account_ids: list[str]) -> None:
    """Bulk-update the marker Accounts."""
    print(f"\n[3/4] INGEST (update) — {len(account_ids)} Accounts")
    lines = ["Id,Description"]
    for aid in account_ids:
        lines.append(f"{aid},updated by salesforce-py live test")
    csv = ("\n".join(lines) + "\n").encode()

    job = await client.ingest.create_job(object_name="Account", operation="update")
    job_id = job["id"]
    await client.ingest.upload_data(job_id, csv_data=csv, content_url=job["contentUrl"])
    await client.ingest.upload_complete(job_id)
    final = await _poll_job(client, job_id, kind="ingest")
    print(
        f"  state={final['state']}, processed={final.get('numberRecordsProcessed')},"
        f" failed={final.get('numberRecordsFailed')}"
    )
    assert final.get("numberRecordsFailed", 0) == 0, "update failures"
    await client.ingest.delete_job(job_id)
    print("  update job deleted")


async def _phase_delete(client: BulkClient, account_ids: list[str]) -> None:
    """Bulk-delete the marker Accounts. Idempotent — skips if list is empty."""
    if not account_ids:
        print("\n[4/4] INGEST (delete) — no IDs to delete; skipping")
        return

    print(f"\n[4/4] INGEST (delete) — {len(account_ids)} Accounts")
    lines = ["Id"] + list(account_ids)
    csv = ("\n".join(lines) + "\n").encode()

    job = await client.ingest.create_job(object_name="Account", operation="delete")
    job_id = job["id"]
    await client.ingest.upload_data(job_id, csv_data=csv, content_url=job["contentUrl"])
    await client.ingest.upload_complete(job_id)
    final = await _poll_job(client, job_id, kind="ingest")
    failed_count = final.get("numberRecordsFailed", 0)
    print(
        f"  state={final['state']}, processed={final.get('numberRecordsProcessed')},"
        f" failed={failed_count}"
    )
    await client.ingest.delete_job(job_id)
    print("  delete job deleted")


async def _phase_admin(client: BulkClient) -> None:
    """Exercise the admin endpoints: get_all_jobs for both sides."""
    print("\n[5/5] ADMIN — get_all_jobs")
    ing = await client.ingest.get_all_jobs()
    qry = await client.query.get_all_jobs()
    print(f"  ingest jobs visible: {len(ing.get('records', []))}")
    print(f"  query jobs visible: {len(qry.get('records', []))}")


async def _sweep_stragglers(rest: RestClient, client: BulkClient) -> None:
    """Final safety net — find any marker Accounts left over and bulk-delete them."""
    res = await rest.query.query(
        f"SELECT Id FROM Account WHERE Name LIKE '{MARKER_PREFIX}-%'"
    )
    records = res.get("records") or []
    if not records:
        print("sweep: no marker accounts remain")
        return
    ids = [r["Id"] for r in records]
    print(f"sweep: cleaning up {len(ids)} residual marker Accounts")
    await _phase_delete(client, ids)


# ---------------------------------------------------------------------------
# Test entry point
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_bulk_live_full_lifecycle() -> None:
    org = SFOrg(target_org=TARGET_ORG)
    org._ensure_connected()

    created_ids: list[str] = []
    async with BulkClient.from_org(org) as client, RestClient.from_org(org) as rest:
        try:
            await _phase_extract(client)
            created_ids = await _phase_insert(client)
            await _phase_update(client, created_ids)
            await _phase_delete(client, created_ids)
            created_ids = []  # deleted cleanly
            await _phase_admin(client)
        finally:
            # If anything failed mid-test, sweep any residual markers so the
            # org never accumulates test data.
            if created_ids:
                print(f"\nFINALLY: deleting {len(created_ids)} leftover IDs")
                try:
                    await _phase_delete(client, created_ids)
                except Exception as exc:  # noqa: BLE001
                    print(f"  finally-delete failed: {type(exc).__name__}: {exc}")
            try:
                await _sweep_stragglers(rest, client)
            except Exception as exc:  # noqa: BLE001
                print(f"  sweep failed: {type(exc).__name__}: {exc}")

    print("\nBULK LIVE — all phases passed")
