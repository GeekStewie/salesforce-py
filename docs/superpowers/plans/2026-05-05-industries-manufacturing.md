# Industries Library — Manufacturing Cloud Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new `salesforce_py.industries.manufacturing` package containing four operation classes (Sales Agreement, Sample Management, Transformations, Warranty→Supplier Claims), wired into the existing `ConnectClient` under a single `client.manufacturing.*` accessor.

**Architecture:** The new files live under `src/salesforce_py/industries/manufacturing/`. Each operation class subclasses the existing `ConnectBaseOperations` so it reuses session/retry/auth/error-mapping for free. `ConnectClient.__init__` instantiates a small `_ManufacturingNamespace` container that exposes the four operation classes as `c.manufacturing.sales_agreements`, `c.manufacturing.sample_management`, `c.manufacturing.transformations`, `c.manufacturing.warranty`. No new session, no new env-var prefix, no new pyproject extra.

**Tech Stack:** Python 3.12+, `httpx` (already a `connect` extra), `pytest` + `pytest-asyncio` in auto mode, `tenacity` (transitively via `_retry.py`). Tooling: `uv run pytest`, `uv run ruff check src/`, `uv run ruff format src/`, `uv run ty check src/`.

**Spec:** [docs/superpowers/specs/2026-05-05-industries-manufacturing-design.md](../specs/2026-05-05-industries-manufacturing-design.md)

---

## File Structure

### Files to create

| Path | Responsibility |
|------|----------------|
| `src/salesforce_py/industries/__init__.py` | Empty umbrella package marker |
| `src/salesforce_py/industries/manufacturing/__init__.py` | Re-export the four operation classes |
| `src/salesforce_py/industries/manufacturing/_properties.py` | `_to_property_list` helper (sample management) |
| `src/salesforce_py/industries/manufacturing/sales_agreements.py` | `SalesAgreementsOperations` |
| `src/salesforce_py/industries/manufacturing/sample_management.py` | `SampleManagementOperations` |
| `src/salesforce_py/industries/manufacturing/transformations.py` | `TransformationsOperations` |
| `src/salesforce_py/industries/manufacturing/warranty.py` | `WarrantyOperations` |
| `src/salesforce_py/industries/manufacturing/README.md` | Namespace map + usage examples |
| `tests/industries/__init__.py` | Empty test package marker |
| `tests/industries/manufacturing/__init__.py` | Empty test package marker |
| `tests/industries/manufacturing/_helpers.py` | Shared `_mock_response` + `_client` test helpers |
| `tests/industries/manufacturing/test_property_list.py` | Unit tests for `_to_property_list` |
| `tests/industries/manufacturing/test_sales_agreements.py` | Unit tests for `SalesAgreementsOperations` |
| `tests/industries/manufacturing/test_sample_management.py` | Unit tests for `SampleManagementOperations` |
| `tests/industries/manufacturing/test_transformations.py` | Unit tests for `TransformationsOperations` |
| `tests/industries/manufacturing/test_warranty.py` | Unit tests for `WarrantyOperations` |
| `tests/industries/manufacturing/test_namespace_wiring.py` | Integration test that goes via `client.manufacturing.*` |

### Files to modify

| Path | Modification |
|------|--------------|
| `src/salesforce_py/connect/client.py` | Add `_ManufacturingNamespace` class + wire into `ConnectClient.__init__` |
| `CLAUDE.md` | Add one paragraph under `## Architecture` describing the `industries/` layer |

---

## Task 1: Package scaffolding

**Files:**
- Create: `src/salesforce_py/industries/__init__.py`
- Create: `src/salesforce_py/industries/manufacturing/__init__.py` (placeholder — final exports added in later tasks)
- Create: `tests/industries/__init__.py`
- Create: `tests/industries/manufacturing/__init__.py`

This task creates the empty package skeleton so subsequent tasks can add files into existing packages. No tests yet — there's nothing to test.

- [ ] **Step 1: Create `src/salesforce_py/industries/__init__.py`**

```python
"""Industry-specific Salesforce API extensions.

Each industry sub-package contains operation classes that are wired into
existing top-level clients (``ConnectClient``, ``RestClient``, …). There is
no ``IndustriesClient`` — see the design spec for the rationale.
"""
```

- [ ] **Step 2: Create `src/salesforce_py/industries/manufacturing/__init__.py`** (placeholder; will be filled in Task 7)

```python
"""Manufacturing Cloud Business API operations.

Four resources are supported: sales agreements, sample management,
transformations, and warranty-to-supplier-claims. Wired into
:class:`salesforce_py.connect.ConnectClient` as ``client.manufacturing.*``.
"""

# Re-exports added in Task 7 once all four operation classes exist.
```

- [ ] **Step 3: Create `tests/industries/__init__.py`** (empty file)

```python
```

- [ ] **Step 4: Create `tests/industries/manufacturing/__init__.py`** (empty file)

```python
```

- [ ] **Step 5: Verify pytest collects the new (empty) test package**

Run: `uv run pytest tests/industries/ -v`

Expected: exits 0 with `no tests ran` (or similar). The collection itself confirms package discovery is working.

- [ ] **Step 6: Commit**

```bash
git add src/salesforce_py/industries/ tests/industries/
git commit -m "Scaffold salesforce_py.industries.manufacturing package"
```

---

## Task 2: `_to_property_list` helper

**Files:**
- Create: `src/salesforce_py/industries/manufacturing/_properties.py`
- Create: `tests/industries/manufacturing/test_property_list.py`

The Sample Management endpoint encodes flat dicts as `[{"field": k, "value": v}, ...]` lists at every nesting level. This helper does that single transform; recursion is handled by the caller (`SampleManagementOperations` in Task 4).

- [ ] **Step 1: Write the failing test** at `tests/industries/manufacturing/test_property_list.py`

```python
"""Unit tests for the property-list helper used by sample management."""

from __future__ import annotations

from salesforce_py.industries.manufacturing._properties import _to_property_list


class TestToPropertyList:
    def test_flat_dict_is_converted_to_field_value_pairs(self):
        result = _to_property_list({"Name": "Acme", "Status": "Draft"})
        assert result == [
            {"field": "Name", "value": "Acme"},
            {"field": "Status", "value": "Draft"},
        ]

    def test_empty_dict_yields_empty_list(self):
        assert _to_property_list({}) == []

    def test_non_string_values_are_preserved(self):
        result = _to_property_list({"Count": 42, "Active": True, "Ratio": 1.5})
        assert result == [
            {"field": "Count", "value": 42},
            {"field": "Active", "value": True},
            {"field": "Ratio", "value": 1.5},
        ]

    def test_iteration_order_matches_input(self):
        # dict preserves insertion order in Python 3.7+
        result = _to_property_list({"z": 1, "a": 2, "m": 3})
        assert [pair["field"] for pair in result] == ["z", "a", "m"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/industries/manufacturing/test_property_list.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'salesforce_py.industries.manufacturing._properties'`

- [ ] **Step 3: Write minimal implementation** at `src/salesforce_py/industries/manufacturing/_properties.py`

```python
"""Helper for the property-list shape used by Manufacturing sample management."""

from __future__ import annotations

from typing import Any


def _to_property_list(fields: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert ``{key: value}`` to ``[{"field": k, "value": v}, ...]``.

    Salesforce's sample-management endpoint encodes flat objects as a list of
    field/value pairs at every nesting level. This helper performs that single
    transform; recursion is the caller's responsibility.

    Args:
        fields: Flat mapping of API field names to values.

    Returns:
        List of ``{"field": k, "value": v}`` dicts in the input's iteration order.
    """
    return [{"field": k, "value": v} for k, v in fields.items()]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/industries/manufacturing/test_property_list.py -v`

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/salesforce_py/industries/manufacturing/_properties.py tests/industries/manufacturing/test_property_list.py
git commit -m "Add _to_property_list helper for manufacturing sample management"
```

---

## Task 3: Test helpers

**Files:**
- Create: `tests/industries/manufacturing/_helpers.py`

These helpers are imported by the test files in Tasks 4–8. They mirror the helpers used in `tests/connect/test_connect.py`. No standalone tests — they're exercised by every operation class test.

- [ ] **Step 1: Write the helpers** at `tests/industries/manufacturing/_helpers.py`

```python
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
```

- [ ] **Step 2: Verify the helper module imports cleanly**

Run: `uv run python -c "from tests.industries.manufacturing._helpers import _mock_response, _client; print('ok')"`

Expected: prints `ok` and exits 0.

- [ ] **Step 3: Commit**

```bash
git add tests/industries/manufacturing/_helpers.py
git commit -m "Add shared test helpers for industries.manufacturing"
```

---

## Task 4: `SalesAgreementsOperations`

**Files:**
- Create: `src/salesforce_py/industries/manufacturing/sales_agreements.py`
- Create: `tests/industries/manufacturing/test_sales_agreements.py`

POST `/connect/manufacturing/sales-agreements` (v51.0+). Body: `sourceObjectId` (required when `body=` not given), optional `salesAgreementDefaultValues`. Returns the parsed Sales Agreement Output JSON.

- [ ] **Step 1: Write the failing tests** at `tests/industries/manufacturing/test_sales_agreements.py`

```python
"""Unit tests for SalesAgreementsOperations."""

from __future__ import annotations

import pytest

from salesforce_py.exceptions import AuthError, SalesforcePyError

from ._helpers import _client, _mock_response


class TestSalesAgreementsCreate:
    async def test_posts_to_correct_path(self):
        c = await _client(_mock_response(200, {"id": "0SAxxxx"}))
        await c.manufacturing.sales_agreements.create(source_object_id="0kFTxxx")
        path = c._session.post.call_args.args[0]
        assert path == "manufacturing/sales-agreements"

    async def test_minimal_body_contains_source_object_id_only(self):
        c = await _client(_mock_response(200, {"id": "0SAxxxx"}))
        await c.manufacturing.sales_agreements.create(source_object_id="0kFTxxx")
        body = c._session.post.call_args.kwargs["json"]
        assert body == {"sourceObjectId": "0kFTxxx"}

    async def test_default_values_included_when_provided(self):
        c = await _client(_mock_response(200, {"id": "0SAxxxx"}))
        defaults = {
            "salesAgreement": {"StartDate": "2026-01-01", "ScheduleFrequency": "Monthly"},
            "salesAgreementProduct": {"Name": "test", "InitialPlannedQuantity": "1"},
        }
        await c.manufacturing.sales_agreements.create(
            source_object_id="0kFTxxx",
            sales_agreement_default_values=defaults,
        )
        body = c._session.post.call_args.kwargs["json"]
        assert body == {
            "sourceObjectId": "0kFTxxx",
            "salesAgreementDefaultValues": defaults,
        }

    async def test_body_escape_hatch_overrides_named_kwargs(self):
        c = await _client(_mock_response(200, {"id": "0SAxxxx"}))
        literal = {"sourceObjectId": "OVERRIDE", "extra": "kept"}
        await c.manufacturing.sales_agreements.create(
            source_object_id="ignored", body=literal
        )
        assert c._session.post.call_args.kwargs["json"] == literal

    async def test_returns_parsed_json(self):
        c = await _client(_mock_response(200, {"id": "0SAxxxx", "ok": True}))
        result = await c.manufacturing.sales_agreements.create(source_object_id="0kFTxxx")
        assert result == {"id": "0SAxxxx", "ok": True}

    async def test_401_raises_auth_error(self):
        c = await _client(_mock_response(401))
        with pytest.raises(AuthError):
            await c.manufacturing.sales_agreements.create(source_object_id="0kFTxxx")

    async def test_400_raises_salesforce_py_error(self):
        c = await _client(_mock_response(400, {"errorCode": "INVALID"}))
        with pytest.raises(SalesforcePyError):
            await c.manufacturing.sales_agreements.create(source_object_id="0kFTxxx")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/industries/manufacturing/test_sales_agreements.py -v`

Expected: collection errors or failures with `AttributeError: 'ConnectClient' object has no attribute 'manufacturing'` (because the namespace isn't wired yet — that happens in Task 8). At this point the implementation file doesn't exist, so we'll get an `ImportError` on the module the namespace would import.

This is expected. We write the implementation now and the tests will *still* fail until Task 8 wires the namespace. We'll come back to run them in Task 8.

- [ ] **Step 3: Write the implementation** at `src/salesforce_py/industries/manufacturing/sales_agreements.py`

```python
"""Manufacturing Cloud Sales Agreement Connect API."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations

_PATH = "manufacturing/sales-agreements"


class SalesAgreementsOperations(ConnectBaseOperations):
    """Operations for ``/connect/manufacturing/sales-agreements`` (v51.0+).

    See: Manufacturing Cloud Developer Guide (Spring '26), pp. 456–457.
    """

    async def create(
        self,
        *,
        source_object_id: str | None = None,
        sales_agreement_default_values: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a sales agreement from a quote, opportunity, or custom object.

        Pass ``body=`` to submit a literal payload; named kwargs are then
        ignored. Otherwise the body is assembled as
        ``{"sourceObjectId": ..., "salesAgreementDefaultValues": ...}``,
        omitting the second key when ``None``.

        Args:
            source_object_id: ID of the source quote/opportunity/custom-object.
                Required when ``body`` is not supplied.
            sales_agreement_default_values: Optional default values dict with
                ``salesAgreement`` and ``salesAgreementProduct`` sub-keys.
            body: Literal request body. Overrides the named kwargs when set.

        Returns:
            Parsed Sales Agreement Output JSON.
        """
        if body is None:
            if source_object_id is None:
                raise ValueError(
                    "source_object_id is required when body is not supplied"
                )
            body = {"sourceObjectId": source_object_id}
            if sales_agreement_default_values is not None:
                body["salesAgreementDefaultValues"] = sales_agreement_default_values
        return await self._post(_PATH, json=body)
```

- [ ] **Step 4: Add a `ValueError`-when-no-body-and-no-source-id test** at the end of `TestSalesAgreementsCreate` in the test file:

```python
    async def test_raises_when_no_source_id_and_no_body(self):
        c = await _client(_mock_response(200, {"id": "x"}))
        with pytest.raises(ValueError, match="source_object_id is required"):
            await c.manufacturing.sales_agreements.create()
```

- [ ] **Step 5: Skip the test run for now**

The tests can't pass until the namespace is wired in Task 8. Move on.

- [ ] **Step 6: Commit**

```bash
git add src/salesforce_py/industries/manufacturing/sales_agreements.py tests/industries/manufacturing/test_sales_agreements.py
git commit -m "Add SalesAgreementsOperations for manufacturing Connect API"
```

---

## Task 5: `SampleManagementOperations`

**Files:**
- Create: `src/salesforce_py/industries/manufacturing/sample_management.py`
- Create: `tests/industries/manufacturing/test_sample_management.py`

POST `/connect/manufacturing/sample-management/product-specifications` (v66.0+). Body has the recursive property-list shape — see PDF page 457–458.

- [ ] **Step 1: Write the failing tests** at `tests/industries/manufacturing/test_sample_management.py`

```python
"""Unit tests for SampleManagementOperations."""

from __future__ import annotations

import pytest

from salesforce_py.exceptions import AuthError

from ._helpers import _client, _mock_response


class TestSampleManagementCreate:
    async def test_posts_to_correct_path(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "x"}))
        await c.manufacturing.sample_management.create(
            operation="Insert",
            spec={"Name": "X"},
        )
        assert (
            c._session.post.call_args.args[0]
            == "manufacturing/sample-management/product-specifications"
        )

    async def test_spec_is_converted_to_property_list(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "x"}))
        await c.manufacturing.sample_management.create(
            operation="Insert",
            spec={"Name": "Project Everest", "AccountId": "001xx", "Status": "Draft"},
        )
        body = c._session.post.call_args.kwargs["json"]
        assert body["operation"] == "Insert"
        assert body["productRequirementSpecification"]["properties"] == [
            {"field": "Name", "value": "Project Everest"},
            {"field": "AccountId", "value": "001xx"},
            {"field": "Status", "value": "Draft"},
        ]

    async def test_versions_and_items_are_recursively_converted(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "x"}))
        await c.manufacturing.sample_management.create(
            operation="Insert",
            spec={"Name": "Spec"},
            versions=[
                {
                    "fields": {"Name": "v1", "Version": "2"},
                    "items": [
                        {"fields": {"Name": "i1", "Statement": "S"}},
                        {"fields": {"Name": "i2", "Statement": "T"}},
                    ],
                }
            ],
        )
        body = c._session.post.call_args.kwargs["json"]
        prs = body["productRequirementSpecification"]
        assert len(prs["productRequirementSpecificationVersions"]) == 1
        v0 = prs["productRequirementSpecificationVersions"][0]
        assert v0["properties"] == [
            {"field": "Name", "value": "v1"},
            {"field": "Version", "value": "2"},
        ]
        assert len(v0["productRequirementSpecificationItems"]) == 2
        assert v0["productRequirementSpecificationItems"][0]["properties"] == [
            {"field": "Name", "value": "i1"},
            {"field": "Statement", "value": "S"},
        ]

    async def test_request_unique_id_included_when_provided(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "abc"}))
        await c.manufacturing.sample_management.create(
            operation="Insert",
            spec={"Name": "X"},
            request_unique_id="abc",
        )
        body = c._session.post.call_args.kwargs["json"]
        assert body["requestUniqueId"] == "abc"

    async def test_request_unique_id_omitted_when_none(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "x"}))
        await c.manufacturing.sample_management.create(
            operation="Insert", spec={"Name": "X"}
        )
        body = c._session.post.call_args.kwargs["json"]
        assert "requestUniqueId" not in body

    async def test_versions_omitted_when_none(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "x"}))
        await c.manufacturing.sample_management.create(
            operation="Insert", spec={"Name": "X"}
        )
        body = c._session.post.call_args.kwargs["json"]
        assert (
            "productRequirementSpecificationVersions"
            not in body["productRequirementSpecification"]
        )

    async def test_items_omitted_when_version_has_no_items_key(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "x"}))
        await c.manufacturing.sample_management.create(
            operation="Update",
            spec={"Name": "X"},
            versions=[{"fields": {"Name": "v1"}}],
        )
        body = c._session.post.call_args.kwargs["json"]
        v0 = body["productRequirementSpecification"][
            "productRequirementSpecificationVersions"
        ][0]
        assert "productRequirementSpecificationItems" not in v0

    async def test_body_escape_hatch_overrides_named_kwargs(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "x"}))
        literal = {"operation": "OVERRIDE", "extra": "kept"}
        await c.manufacturing.sample_management.create(
            operation="Insert", spec={"Name": "X"}, body=literal
        )
        assert c._session.post.call_args.kwargs["json"] == literal

    async def test_401_raises_auth_error(self):
        c = await _client(_mock_response(401))
        with pytest.raises(AuthError):
            await c.manufacturing.sample_management.create(
                operation="Insert", spec={"Name": "X"}
            )
```

- [ ] **Step 2: Skip running tests** (will run in Task 8 once namespace is wired)

- [ ] **Step 3: Write the implementation** at `src/salesforce_py/industries/manufacturing/sample_management.py`

```python
"""Manufacturing Cloud Sample Management Connect API."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations
from salesforce_py.industries.manufacturing._properties import _to_property_list

_PATH = "manufacturing/sample-management/product-specifications"


class SampleManagementOperations(ConnectBaseOperations):
    """Operations for ``/connect/manufacturing/sample-management/product-specifications`` (v66.0+).

    See: Manufacturing Cloud Developer Guide (Spring '26), pp. 457–458.
    """

    async def create(
        self,
        *,
        operation: str | None = None,
        spec: dict[str, Any] | None = None,
        versions: list[dict[str, Any]] | None = None,
        request_unique_id: str | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Insert / update / version a Product Requirement Specification.

        Pass ``body=`` to submit a literal payload; named kwargs are ignored.
        Otherwise the request body is assembled by converting flat dicts
        (``spec``, ``versions[i]['fields']``, ``versions[i]['items'][j]['fields']``)
        into the field/value list shape Salesforce expects.

        Args:
            operation: ``"Insert"``, ``"Update"``, or ``"Version"``. Required
                when ``body`` is not supplied.
            spec: Flat ``{field: value}`` mapping for the top-level Product
                Requirement Specification. Required when ``body`` is not
                supplied.
            versions: Optional list of ``{"fields": {...}, "items":
                [{"fields": {...}}, ...]}`` dicts.
            request_unique_id: Optional client-side request ID echoed in the
                response — useful for tracing.
            body: Literal request body. Overrides the named kwargs when set.

        Returns:
            Parsed Sample Management Output JSON.
        """
        if body is None:
            if operation is None or spec is None:
                raise ValueError(
                    "operation and spec are required when body is not supplied"
                )
            spec_payload: dict[str, Any] = {"properties": _to_property_list(spec)}
            if versions is not None:
                spec_payload["productRequirementSpecificationVersions"] = [
                    _build_version(v) for v in versions
                ]
            body = {
                "operation": operation,
                "productRequirementSpecification": spec_payload,
            }
            if request_unique_id is not None:
                body["requestUniqueId"] = request_unique_id
        return await self._post(_PATH, json=body)


def _build_version(version: dict[str, Any]) -> dict[str, Any]:
    """Convert one version dict to the wire shape."""
    out: dict[str, Any] = {"properties": _to_property_list(version.get("fields", {}))}
    items = version.get("items")
    if items is not None:
        out["productRequirementSpecificationItems"] = [
            {"properties": _to_property_list(item.get("fields", {}))} for item in items
        ]
    return out
```

- [ ] **Step 4: Commit**

```bash
git add src/salesforce_py/industries/manufacturing/sample_management.py tests/industries/manufacturing/test_sample_management.py
git commit -m "Add SampleManagementOperations for manufacturing Connect API"
```

---

## Task 6: `TransformationsOperations`

**Files:**
- Create: `src/salesforce_py/industries/manufacturing/transformations.py`
- Create: `tests/industries/manufacturing/test_transformations.py`

POST `/connect/manufacturing/transformations` (v55.0+). Body fields: `inputObjectIds[]`, `inputObjectName`, `usageType`, `outputObjectName`, optional `outputObjectDefaultValues` (a `Map<String, Map<String, Any>>`-shaped dict).

- [ ] **Step 1: Write the failing tests** at `tests/industries/manufacturing/test_transformations.py`

```python
"""Unit tests for TransformationsOperations."""

from __future__ import annotations

import pytest

from salesforce_py.exceptions import AuthError

from ._helpers import _client, _mock_response


class TestTransformationsRun:
    async def test_posts_to_correct_path(self):
        c = await _client(_mock_response(200, {"jobId": "0sx"}))
        await c.manufacturing.transformations.run(
            input_object_ids=["0sTxxx"],
            input_object_name="MfgProgramCpntFrcstFact",
            usage_type="TransformationMapping",
            output_object_name="Opportunity",
        )
        assert c._session.post.call_args.args[0] == "manufacturing/transformations"

    async def test_required_fields_present_in_body(self):
        c = await _client(_mock_response(200, {"jobId": "0sx"}))
        await c.manufacturing.transformations.run(
            input_object_ids=["0sTxxx", "0sTyyy"],
            input_object_name="MfgProgramCpntFrcstFact",
            usage_type="TransformationMapping",
            output_object_name="Opportunity",
        )
        body = c._session.post.call_args.kwargs["json"]
        assert body == {
            "inputObjectIds": ["0sTxxx", "0sTyyy"],
            "inputObjectName": "MfgProgramCpntFrcstFact",
            "usageType": "TransformationMapping",
            "outputObjectName": "Opportunity",
        }

    async def test_default_values_included_when_provided(self):
        c = await _client(_mock_response(200, {"jobId": "0sx"}))
        defaults = {
            "Opportunity": {"StageName": "Prospecting", "Probability": "20"},
            "OpportunityLineItem": {"TotalPrice": 1234, "CurrencyIsoCode": "USD"},
        }
        await c.manufacturing.transformations.run(
            input_object_ids=["0sTxxx"],
            input_object_name="MfgProgramCpntFrcstFact",
            usage_type="TransformationMapping",
            output_object_name="Opportunity",
            output_object_default_values=defaults,
        )
        body = c._session.post.call_args.kwargs["json"]
        assert body["outputObjectDefaultValues"] == defaults

    async def test_default_values_omitted_when_none(self):
        c = await _client(_mock_response(200, {"jobId": "0sx"}))
        await c.manufacturing.transformations.run(
            input_object_ids=["0sTxxx"],
            input_object_name="MfgProgramCpntFrcstFact",
            usage_type="TransformationMapping",
            output_object_name="Opportunity",
        )
        assert "outputObjectDefaultValues" not in c._session.post.call_args.kwargs["json"]

    async def test_body_escape_hatch_overrides_named_kwargs(self):
        c = await _client(_mock_response(200, {"jobId": "0sx"}))
        literal = {"inputObjectIds": ["OVERRIDE"], "extra": "kept"}
        await c.manufacturing.transformations.run(
            input_object_ids=["ignored"],
            input_object_name="X",
            usage_type="Y",
            output_object_name="Z",
            body=literal,
        )
        assert c._session.post.call_args.kwargs["json"] == literal

    async def test_401_raises_auth_error(self):
        c = await _client(_mock_response(401))
        with pytest.raises(AuthError):
            await c.manufacturing.transformations.run(
                input_object_ids=["0sTxxx"],
                input_object_name="MfgProgramCpntFrcstFact",
                usage_type="TransformationMapping",
                output_object_name="Opportunity",
            )
```

- [ ] **Step 2: Skip running tests** (will run in Task 8)

- [ ] **Step 3: Write the implementation** at `src/salesforce_py/industries/manufacturing/transformations.py`

```python
"""Manufacturing Cloud Transformations Connect API."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations

_PATH = "manufacturing/transformations"


class TransformationsOperations(ConnectBaseOperations):
    """Operations for ``/connect/manufacturing/transformations`` (v55.0+).

    See: Manufacturing Cloud Developer Guide (Spring '26), pp. 459–461.
    """

    async def run(
        self,
        *,
        input_object_ids: list[str] | None = None,
        input_object_name: str | None = None,
        usage_type: str | None = None,
        output_object_name: str | None = None,
        output_object_default_values: dict[str, dict[str, Any]] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run a configured transformation from program/forecast records.

        Common scenarios: ``MfgProgramCpntFrcstFact`` → ``Opportunity``,
        ``ManufacturingProgram`` → ``Opportunity``,
        ``MfgProgramCpntFrcstFact`` → ``OpportunityLineItem``,
        ``Period`` → ``OpportunityLineItemSchedule``.

        Pass ``body=`` to submit a literal payload; named kwargs are ignored.

        Args:
            input_object_ids: List of source record IDs (all of the same
                ``input_object_name``). Required when ``body`` is not supplied.
            input_object_name: Source object API name (``MfgProgramCpntFrcstFact``,
                ``ManufacturingProgram``, ``Period``, ``Quote``, ``QuoteLineItem``).
                Required when ``body`` is not supplied.
            usage_type: ``ConvertToSalesAgreement`` | ``CLMFieldMapping`` |
                ``EligibleProgramRebateType`` | ``MapJournalToMemberAggregate`` |
                ``TransformationMapping``. Required when ``body`` is not supplied.
            output_object_name: Target object API name. Required when ``body``
                is not supplied.
            output_object_default_values: Optional default values, keyed by
                output object API name, e.g.
                ``{"Opportunity": {"StageName": "Prospecting"}}``.
            body: Literal request body. Overrides the named kwargs when set.

        Returns:
            Parsed Transformation Output JSON.
        """
        if body is None:
            if (
                input_object_ids is None
                or input_object_name is None
                or usage_type is None
                or output_object_name is None
            ):
                raise ValueError(
                    "input_object_ids, input_object_name, usage_type, and "
                    "output_object_name are all required when body is not supplied"
                )
            body = {
                "inputObjectIds": input_object_ids,
                "inputObjectName": input_object_name,
                "usageType": usage_type,
                "outputObjectName": output_object_name,
            }
            if output_object_default_values is not None:
                body["outputObjectDefaultValues"] = output_object_default_values
        return await self._post(_PATH, json=body)
```

- [ ] **Step 4: Commit**

```bash
git add src/salesforce_py/industries/manufacturing/transformations.py tests/industries/manufacturing/test_transformations.py
git commit -m "Add TransformationsOperations for manufacturing Connect API"
```

---

## Task 7: `WarrantyOperations`

**Files:**
- Create: `src/salesforce_py/industries/manufacturing/warranty.py`
- Create: `tests/industries/manufacturing/test_warranty.py`

POST `/connect/warranty/supplier-claim` (v61.0+). **Note the path**: this hits `/connect/warranty/...`, NOT `/connect/manufacturing/...`. The class still lives under `industries/manufacturing/` because Salesforce documents it inside the Manufacturing Cloud guide and callers reach it via `client.manufacturing.warranty`.

- [ ] **Step 1: Write the failing tests** at `tests/industries/manufacturing/test_warranty.py`

```python
"""Unit tests for WarrantyOperations."""

from __future__ import annotations

import pytest

from salesforce_py.exceptions import AuthError

from ._helpers import _client, _mock_response


class TestWarrantySupplierClaim:
    async def test_posts_to_warranty_path_not_manufacturing_path(self):
        c = await _client(_mock_response(200, {"id": "0Z..."}))
        await c.manufacturing.warranty.supplier_claim(claim_ids=["0ZkSxxx"])
        # Critical: path is /warranty/, not /manufacturing/warranty/
        assert c._session.post.call_args.args[0] == "warranty/supplier-claim"

    async def test_minimal_body_contains_claim_ids_only(self):
        c = await _client(_mock_response(200, {"id": "0Z..."}))
        await c.manufacturing.warranty.supplier_claim(claim_ids=["0ZkSxxx", "0ZkSyyy"])
        body = c._session.post.call_args.kwargs["json"]
        assert body == {"claimIds": ["0ZkSxxx", "0ZkSyyy"]}

    async def test_optional_context_fields_included_when_provided(self):
        c = await _client(_mock_response(200, {"id": "0Z..."}))
        await c.manufacturing.warranty.supplier_claim(
            claim_ids=["0ZkSxxx"],
            context_definition="ClaimDetails__stdctx",
            context_mapping="ClaimDetailsMapping",
            conversion_type="Supplier Recovery Claim",
        )
        body = c._session.post.call_args.kwargs["json"]
        assert body["contextDefinition"] == "ClaimDetails__stdctx"
        assert body["contextMapping"] == "ClaimDetailsMapping"
        assert body["conversionType"] == "Supplier Recovery Claim"

    async def test_supplier_recovery_products_passed_through(self):
        c = await _client(_mock_response(200, {"id": "0Z..."}))
        products = [
            {"product2Id": "01tSBxxx", "salesContractLineId": "0sLSBxxx"},
            {"product2Id": "01tSByyy"},
        ]
        await c.manufacturing.warranty.supplier_claim(
            claim_ids=["0ZkSxxx"],
            supplier_recovery_products=products,
        )
        body = c._session.post.call_args.kwargs["json"]
        assert body["supplierRecoveryProducts"] == products

    async def test_optional_fields_omitted_when_none(self):
        c = await _client(_mock_response(200, {"id": "0Z..."}))
        await c.manufacturing.warranty.supplier_claim(claim_ids=["0ZkSxxx"])
        body = c._session.post.call_args.kwargs["json"]
        for k in (
            "contextDefinition",
            "contextMapping",
            "conversionType",
            "supplierRecoveryProducts",
        ):
            assert k not in body

    async def test_body_escape_hatch_overrides_named_kwargs(self):
        c = await _client(_mock_response(200, {"id": "0Z..."}))
        literal = {"claimIds": ["OVERRIDE"], "extra": "kept"}
        await c.manufacturing.warranty.supplier_claim(
            claim_ids=["ignored"], body=literal
        )
        assert c._session.post.call_args.kwargs["json"] == literal

    async def test_401_raises_auth_error(self):
        c = await _client(_mock_response(401))
        with pytest.raises(AuthError):
            await c.manufacturing.warranty.supplier_claim(claim_ids=["0ZkSxxx"])
```

- [ ] **Step 2: Skip running tests** (will run in Task 8)

- [ ] **Step 3: Write the implementation** at `src/salesforce_py/industries/manufacturing/warranty.py`

```python
"""Warranty → Supplier Claims Connect API.

Note: this endpoint sits at ``/connect/warranty/supplier-claim``, not under
``/connect/manufacturing/``. Salesforce documents it inside the Manufacturing
Cloud guide (pp. 461–462), so the class lives in the manufacturing folder
and is exposed as ``client.manufacturing.warranty.supplier_claim(...)``,
even though the URL path is a sibling.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations

_PATH = "warranty/supplier-claim"


class WarrantyOperations(ConnectBaseOperations):
    """Operations for ``/connect/warranty/supplier-claim`` (v61.0+)."""

    async def supplier_claim(
        self,
        *,
        claim_ids: list[str] | None = None,
        context_definition: str | None = None,
        context_mapping: str | None = None,
        conversion_type: str | None = None,
        supplier_recovery_products: list[dict[str, Any]] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Clone warranty claim(s) into supplier recovery claim(s).

        Pass ``body=`` to submit a literal payload; named kwargs are ignored.

        Args:
            claim_ids: IDs of warranty Claim records to clone. Required when
                ``body`` is not supplied.
            context_definition: Developer name of the context definition
                describing the warranty claim structure.
            context_mapping: Name of the context mapping associated with the
                context definition.
            conversion_type: Type of conversion, e.g. ``"Supplier Recovery Claim"``.
            supplier_recovery_products: List of
                ``{"product2Id": ..., "salesContractLineId": ...}`` dicts.
            body: Literal request body. Overrides the named kwargs when set.

        Returns:
            Parsed Warranty To Supplier Claims Output JSON.
        """
        if body is None:
            if claim_ids is None:
                raise ValueError("claim_ids is required when body is not supplied")
            body = {"claimIds": claim_ids}
            if context_definition is not None:
                body["contextDefinition"] = context_definition
            if context_mapping is not None:
                body["contextMapping"] = context_mapping
            if conversion_type is not None:
                body["conversionType"] = conversion_type
            if supplier_recovery_products is not None:
                body["supplierRecoveryProducts"] = supplier_recovery_products
        return await self._post(_PATH, json=body)
```

- [ ] **Step 4: Commit**

```bash
git add src/salesforce_py/industries/manufacturing/warranty.py tests/industries/manufacturing/test_warranty.py
git commit -m "Add WarrantyOperations for manufacturing Connect API"
```

---

## Task 8: Wire `_ManufacturingNamespace` into `ConnectClient`

**Files:**
- Modify: `src/salesforce_py/industries/manufacturing/__init__.py`
- Modify: `src/salesforce_py/connect/client.py`
- Create: `tests/industries/manufacturing/test_namespace_wiring.py`

This task wires up the `c.manufacturing.*` accessor and unblocks Tasks 4–7's tests.

- [ ] **Step 1: Fill in the package re-exports** at `src/salesforce_py/industries/manufacturing/__init__.py`

```python
"""Manufacturing Cloud Business API operations.

Four resources are supported: sales agreements, sample management,
transformations, and warranty-to-supplier-claims. Wired into
:class:`salesforce_py.connect.ConnectClient` as ``client.manufacturing.*``.
"""

from salesforce_py.industries.manufacturing.sales_agreements import (
    SalesAgreementsOperations,
)
from salesforce_py.industries.manufacturing.sample_management import (
    SampleManagementOperations,
)
from salesforce_py.industries.manufacturing.transformations import (
    TransformationsOperations,
)
from salesforce_py.industries.manufacturing.warranty import WarrantyOperations

__all__ = [
    "SalesAgreementsOperations",
    "SampleManagementOperations",
    "TransformationsOperations",
    "WarrantyOperations",
]
```

- [ ] **Step 2: Write the namespace wiring test** at `tests/industries/manufacturing/test_namespace_wiring.py`

```python
"""Smoke tests for the c.manufacturing.* namespace on ConnectClient."""

from __future__ import annotations

from salesforce_py.connect.client import ConnectClient
from salesforce_py.industries.manufacturing import (
    SalesAgreementsOperations,
    SampleManagementOperations,
    TransformationsOperations,
    WarrantyOperations,
)

INSTANCE_URL = "https://test.my.salesforce.com"
ACCESS_TOKEN = "test_token_abc"


class TestManufacturingNamespace:
    def test_namespace_exposes_all_four_operation_classes(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        assert isinstance(c.manufacturing.sales_agreements, SalesAgreementsOperations)
        assert isinstance(c.manufacturing.sample_management, SampleManagementOperations)
        assert isinstance(c.manufacturing.transformations, TransformationsOperations)
        assert isinstance(c.manufacturing.warranty, WarrantyOperations)

    def test_all_operation_classes_share_the_connect_session(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        assert c.manufacturing.sales_agreements._session is c._session
        assert c.manufacturing.sample_management._session is c._session
        assert c.manufacturing.transformations._session is c._session
        assert c.manufacturing.warranty._session is c._session
```

- [ ] **Step 3: Run the wiring test to verify it fails**

Run: `uv run pytest tests/industries/manufacturing/test_namespace_wiring.py -v`

Expected: FAIL with `AttributeError: 'ConnectClient' object has no attribute 'manufacturing'`.

- [ ] **Step 4: Add the import to `src/salesforce_py/connect/client.py`**

Add this import alongside the existing operation imports near the top of the file (the import block runs from roughly line 14 to line 159). Place it alphabetically — between `KnowledgeArticleViewStatOperations` and `ManagedTopicsOperations` works well, since `from salesforce_py.industries.manufacturing import ...` comes before `from salesforce_py.connect.operations.managed_topics`:

```python
from salesforce_py.industries.manufacturing import (
    SalesAgreementsOperations,
    SampleManagementOperations,
    TransformationsOperations,
    WarrantyOperations,
)
```

- [ ] **Step 5: Add the namespace class** to `src/salesforce_py/connect/client.py`, immediately above the `class ConnectClient:` line:

```python
class _ManufacturingNamespace:
    """Container exposing manufacturing-cloud Connect API operations.

    Grouped semantically; ``warranty.supplier_claim`` hits
    ``/connect/warranty/``, not ``/connect/manufacturing/``, despite living
    under this accessor.
    """

    def __init__(self, session: ConnectSession) -> None:
        self.sales_agreements = SalesAgreementsOperations(session)
        self.sample_management = SampleManagementOperations(session)
        self.transformations = TransformationsOperations(session)
        self.warranty = WarrantyOperations(session)
```

- [ ] **Step 6: Wire the namespace into `ConnectClient.__init__`**

Add this line at the very end of the `__init__` body, after the last existing `self.users = ...` line (line 296):

```python
        self.manufacturing = _ManufacturingNamespace(self._session)
```

- [ ] **Step 7: Run the wiring test to verify it passes**

Run: `uv run pytest tests/industries/manufacturing/test_namespace_wiring.py -v`

Expected: 2 passed.

- [ ] **Step 8: Run all manufacturing tests to verify Tasks 4–7 now pass**

Run: `uv run pytest tests/industries/manufacturing/ -v`

Expected: all tests pass (4 from `test_property_list.py`, 8 from `test_sales_agreements.py`, 9 from `test_sample_management.py`, 6 from `test_transformations.py`, 7 from `test_warranty.py`, 2 from `test_namespace_wiring.py` — 36 total).

If any test fails, fix the underlying issue (most likely a typo in a path constant or a key name in an operation class) before committing.

- [ ] **Step 9: Run the full test suite to confirm nothing else broke**

Run: `uv run pytest`

Expected: all existing tests still pass plus the 36 new ones.

- [ ] **Step 10: Commit**

```bash
git add src/salesforce_py/industries/manufacturing/__init__.py src/salesforce_py/connect/client.py tests/industries/manufacturing/test_namespace_wiring.py
git commit -m "Wire manufacturing namespace into ConnectClient"
```

---

## Task 9: README

**Files:**
- Create: `src/salesforce_py/industries/manufacturing/README.md`

Mirrors `src/salesforce_py/connect/README.md` style — namespace map plus one usage example per resource.

- [ ] **Step 1: Write the README** at `src/salesforce_py/industries/manufacturing/README.md`

```markdown
# salesforce_py.industries.manufacturing

Manufacturing Cloud Business API operations, exposed through the existing
[`ConnectClient`](../../connect/README.md) as `client.manufacturing.*`.

| Operation namespace | Resource | Endpoint | Available since |
|--------------------|----------|----------|-----------------|
| `client.manufacturing.sales_agreements` | Sales Agreement | `POST /connect/manufacturing/sales-agreements` | v51.0 |
| `client.manufacturing.sample_management` | Sample Management | `POST /connect/manufacturing/sample-management/product-specifications` | v66.0 |
| `client.manufacturing.transformations` | Transformations | `POST /connect/manufacturing/transformations` | v55.0 |
| `client.manufacturing.warranty` | Warranty → Supplier Claims | `POST /connect/warranty/supplier-claim` | v61.0 |

> **Note**: `warranty.supplier_claim` is grouped under `manufacturing.*`
> because Salesforce documents it inside the Manufacturing Cloud guide,
> but its actual URL path is `/connect/warranty/...`, not
> `/connect/manufacturing/warranty/...`.

## Installation

No new extra. The existing `connect` extra covers these endpoints:

```bash
uv sync --extra dev --extra connect
```

## Usage

All examples assume an opened `ConnectClient`:

```python
import asyncio
from salesforce_py.connect import ConnectClient


async def main() -> None:
    async with ConnectClient(instance_url, access_token) as client:
        ...  # examples below

asyncio.run(main())
```

### Sales Agreement (POST)

```python
result = await client.manufacturing.sales_agreements.create(
    source_object_id="0kFT1000000000RMAQ",
    sales_agreement_default_values={
        "salesAgreement": {
            "StartDate": "2026-01-01",
            "ScheduleFrequency": "Monthly",
            "ScheduleCount": "10",
        },
        "salesAgreementProduct": {
            "PricebookEntry": "01uxx00000091jOAAQ",
            "Name": "test-sap1",
            "InitialPlannedQuantity": "1",
        },
    },
)
```

### Sample Management (POST)

```python
result = await client.manufacturing.sample_management.create(
    operation="Insert",
    spec={
        "Name": "Project Everest Core Requirements",
        "AccountId": "001xx000003GaGxAAK",
        "Status": "Draft",
        "Alias__c": "Requirements1136",
    },
    versions=[
        {
            "fields": {"Name": "Functional1136", "Version": "2"},
            "items": [
                {
                    "fields": {
                        "Name": "Functional1136",
                        "Statement": "The system shall display KPIs.",
                        "AcceptanceCriteria": "The system shall display KPIs.",
                        "Category": "Functional",
                    },
                },
            ],
        },
    ],
    request_unique_id="insert_op_req_1",
)
```

The flat `spec` dict is converted internally to the `[{"field": k, "value": v}, ...]`
shape Salesforce expects; same for each version's `fields` and each item's `fields`.

### Transformations (POST)

```python
result = await client.manufacturing.transformations.run(
    input_object_ids=[
        "0sTxx000000003FEAQ",
        "0sTxx000000004rEAA",
    ],
    input_object_name="MfgProgramCpntFrcstFact",
    usage_type="TransformationMapping",
    output_object_name="Opportunity",
    output_object_default_values={
        "Opportunity": {
            "Pricebook2Id": "PriceBookID",
            "StageName": "Prospecting",
            "Probability": "20",
            "Name": "SampleFactToOpp",
            "CloseDate": "2026-12-31",
        },
        "OpportunityLineItem": {"TotalPrice": 1234, "CurrencyIsoCode": "USD"},
        "OpportunityLineItemSchedule": {"Type": "Both"},
    },
)
```

### Warranty → Supplier Claims (POST)

```python
result = await client.manufacturing.warranty.supplier_claim(
    claim_ids=["0ZkSB00000002TF0AY"],
    context_definition="ClaimDetails__stdctx",
    context_mapping="ClaimDetailsMapping",
    conversion_type="Supplier Recovery Claim",
    supplier_recovery_products=[
        {
            "product2Id": "01tSB000000FXLlYAO",
            "salesContractLineId": "0sLSB00000001Ab2AI",
        },
    ],
)
```

## Escape hatch

Every method accepts a `body=` keyword that, when supplied, is posted
verbatim — named kwargs are ignored. Use this when you need to submit a
payload shape the helper doesn't yet support:

```python
await client.manufacturing.sample_management.create(
    body={"operation": "Insert", "productRequirementSpecification": {...}}
)
```

## Reference

- Manufacturing Cloud Developer Guide (Spring '26), pp. 455–462 — the
  authoritative source for request/response shapes and field validation
  rules.
- Connect REST API Developer Guide — architecture, authentication, rate
  limits.
```

- [ ] **Step 2: Commit**

```bash
git add src/salesforce_py/industries/manufacturing/README.md
git commit -m "Document salesforce_py.industries.manufacturing usage"
```

---

## Task 10: CLAUDE.md update

**Files:**
- Modify: `CLAUDE.md`

Add one paragraph describing the `industries/` package as an organizational layer that wires industry-specific operations into existing clients. This is critical orientation for future contributors and Claude Code sessions.

- [ ] **Step 1: Read the current `CLAUDE.md` to find the right insertion point**

Run: `uv run python -c "import pathlib; print(pathlib.Path('CLAUDE.md').read_text().count('### '))"`

This is just to confirm the file exists. Then open it and locate the line near the end of `## Architecture` that starts with `### Bulk API 2.0 client`.

- [ ] **Step 2: Insert a new sub-section** immediately before `## Exceptions` in `CLAUDE.md`. Use the `Edit` tool with this exact insertion:

```markdown
### Industry extensions (`salesforce_py/industries/`)

Industry-specific operation classes that wire into existing top-level clients
rather than introducing new ones. The `industries/` directory is purely a
source-tree organizational layer — there is no `IndustriesClient`, no new
session, no new pyproject extra, no new env-var prefix.

The first slice is `industries/manufacturing/`, which adds four operation
classes (`SalesAgreementsOperations`, `SampleManagementOperations`,
`TransformationsOperations`, `WarrantyOperations`) covering the four
Manufacturing Cloud Business API resources. They subclass the existing
`ConnectBaseOperations` and are wired into `ConnectClient.__init__` as a
small `_ManufacturingNamespace` container exposed as
`client.manufacturing.*`. The warranty operation hits
`/connect/warranty/supplier-claim` despite being grouped under
`manufacturing.*` — Salesforce documents it inside the Manufacturing Cloud
guide but its URL path is a sibling, not a child.

Future industries (`industries/financial_services/`, `industries/health/`,
…) follow the same pattern: implementation files live under
`industries/<industry>/`, and they get wired into whichever existing client
matches each endpoint's URL.
```

- [ ] **Step 3: Verify CLAUDE.md still parses cleanly** (visual inspection)

Run: `uv run python -c "import pathlib; t = pathlib.Path('CLAUDE.md').read_text(); assert '### Industry extensions' in t; assert '## Exceptions' in t; print('ok')"`

Expected: prints `ok`.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "Document industries/ package layer in CLAUDE.md"
```

---

## Task 11: Final verification (lint, format, type-check, full test run)

No new files. This task validates the work and catches anything the per-task TDD missed.

- [ ] **Step 1: Run ruff check**

Run: `uv run ruff check src/`

Expected: `All checks passed!`. If ruff reports issues, fix them inline (most likely unused imports or import-order nits) and re-run.

- [ ] **Step 2: Run ruff format**

Run: `uv run ruff format src/`

Expected: either `N files left unchanged` or a list of files reformatted. If files were reformatted, stage and commit them: `git add src/ && git commit -m "Apply ruff format to industries.manufacturing"`.

- [ ] **Step 3: Run ty type-check**

Run: `uv run ty check src/`

Expected: `Success: no issues found`. If ty reports type errors, fix the type annotations in the offending file and re-run. (Common issues: missing `| None` on optional kwargs, missing `from __future__ import annotations`.)

- [ ] **Step 4: Run the full test suite**

Run: `uv run pytest`

Expected: all tests pass — the existing suite plus 36 new tests under `tests/industries/manufacturing/`. Look specifically for the line `tests/industries/manufacturing/...` reporting all green.

- [ ] **Step 5: If any of steps 1–4 produced no extra commits, mark the plan complete**

Run: `git log --oneline -15`

Expected: 10 commits since the spec commit (one per task that added code, plus any format/lint fix-up commits).

---

## Self-review notes

Cross-checked against the spec:

- Sales Agreement endpoint, body shape, escape hatch — Task 4. ✓
- Sample Management endpoint, recursive property-list conversion, escape hatch — Tasks 2 + 5. ✓
- Transformations endpoint, body shape, escape hatch — Task 6. ✓
- Warranty endpoint at `/connect/warranty/`, escape hatch — Task 7. ✓
- `_ManufacturingNamespace` exposed as `client.manufacturing.*` — Task 8. ✓
- Tests under `tests/industries/manufacturing/` (one file per resource + property-list helper + namespace wiring) — Tasks 2, 4, 5, 6, 7, 8. ✓
- README under `industries/manufacturing/` — Task 9. ✓
- One paragraph added to `CLAUDE.md` — Task 10. ✓
- No new pyproject extra; no new env-var prefix; no new session — preserved across all tasks. ✓
- Public re-exports scoped to `industries.manufacturing.__init__` only; nothing exposed at the top-level `salesforce_py` namespace — Task 8. ✓
- No integration tests against a real org in this iteration — confirmed. ✓
