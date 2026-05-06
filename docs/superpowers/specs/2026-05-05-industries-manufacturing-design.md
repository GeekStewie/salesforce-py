# Industries library: Manufacturing Cloud Business APIs

Design for the first slice of `salesforce_py.industries` — Manufacturing Cloud
Business API support, exposed as new operation classes wired into the existing
`ConnectClient`.

## Goal

Add support for four Manufacturing Cloud Business API resources from the
*Spring '26 Manufacturing Cloud Developer Guide* (PDF pages 455–462):

| Resource              | Endpoint                                                              | Available |
|-----------------------|-----------------------------------------------------------------------|-----------|
| Sales Agreement       | `POST /connect/manufacturing/sales-agreements`                        | v51.0+    |
| Sample Management     | `POST /connect/manufacturing/sample-management/product-specifications`| v66.0+    |
| Transformations       | `POST /connect/manufacturing/transformations`                         | v55.0+    |
| Warranty → Supplier Claims | `POST /connect/warranty/supplier-claim`                          | v61.0+    |

These four are the "starter set." Future Manufacturing Cloud surfaces
(invocable actions, Tooling API objects, Apex namespace) are out of scope for
this iteration but the file layout is positioned to absorb them.

## Decisions (from brainstorming)

1. **Topology — extend existing clients, don't introduce a new top-level
   client.** All four endpoints sit under `/services/data/vXX.X/connect/`,
   which `ConnectClient` already covers. Adding a sibling `industries`
   *client* would duplicate session/auth machinery for no transport-level
   reason.
2. **Exposure — semantic grouping under `connect_client.manufacturing.*`.**
   Even though `warranty/supplier-claim` doesn't share the
   `/connect/manufacturing/` prefix, Salesforce documents it inside the
   Manufacturing Cloud guide and callers reason about it as part of the
   manufacturing surface. The operation class hard-codes the correct path.
3. **Inputs — raw dicts everywhere, with one ergonomic helper for sample
   management** (its property-list shape is repetitive across three nesting
   levels), plus a `body=` escape hatch on every method so power users can
   submit a literal payload.

## Architecture

### Source tree

```
src/salesforce_py/industries/
  __init__.py                          # empty (industries umbrella has no exports)
  manufacturing/
    __init__.py                        # re-exports the four operation classes
    README.md                          # mirrors connect/README.md style
    _properties.py                     # _to_property_list({...}) helper
    sales_agreements.py                # SalesAgreementsOperations
    sample_management.py               # SampleManagementOperations
    transformations.py                 # TransformationsOperations
    warranty.py                        # WarrantyOperations
```

`industries/` is purely an organizational layer in the source tree. There is
no `IndustriesClient`, no `industries` extra, no new env-var prefix. Future
industries (`industries/financial_services/`, etc.) will follow the same
pattern: implementation files live under `industries/<industry>/`, and they
get wired into whichever existing client (`ConnectClient`, `RestClient`,
…) matches each endpoint's URL.

### Wiring

In `src/salesforce_py/connect/client.py`:

```python
from salesforce_py.industries.manufacturing import (
    SalesAgreementsOperations,
    SampleManagementOperations,
    TransformationsOperations,
    WarrantyOperations,
)


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


# in ConnectClient.__init__, alongside the existing namespace assignments:
self.manufacturing = _ManufacturingNamespace(self._session)
```

`_ManufacturingNamespace` lives in `connect/client.py` (not in `industries/`)
because it's part of the `ConnectClient` public surface and only matters at
client-assembly time. The operation classes themselves are all the user-facing
API that lives in `industries/`.

### Operation classes

All four subclass the existing `ConnectBaseOperations`. They inherit:

- `_post`/`_get`/`_patch`/`_put`/`_delete` with the retry+timeout shape from
  `_retry.py` (one retry on transient 5xx/network/`429`, no retry on 4xx
  except 408/420/425/429).
- `_handle_status` mapping (401 → `AuthError`, other 4xx/5xx →
  `SalesforcePyError` with body excerpt).
- `_ensure_18` for 15→18-char ID normalisation (used selectively — see
  below).

Each method:

- Is keyword-only after `self` (the `*,` separator). Bodies have many fields
  and positional args invite mistakes.
- Returns the parsed JSON response (`dict[str, Any]`).
- Has a `body=` escape hatch: if supplied, posted verbatim, named kwargs
  ignored.
- Hard-codes its path as a module-level `_PATH` constant.

#### `SalesAgreementsOperations`

```python
async def create(
    self,
    *,
    source_object_id: str,
    sales_agreement_default_values: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a sales agreement from a quote, opportunity, or custom object."""
```

Path: `manufacturing/sales-agreements`. Body when `body=` is absent:
`{"sourceObjectId": ..., "salesAgreementDefaultValues": ...}` — the second
key is omitted when `None`.

#### `SampleManagementOperations`

```python
async def create(
    self,
    *,
    operation: str,                    # "Insert" | "Update" | "Version" | ...
    spec: dict[str, Any],              # flat field→value dict at the spec level
    versions: list[dict[str, Any]] | None = None,
    request_unique_id: str | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Insert / update / version a Product Requirement Specification."""
```

Path: `manufacturing/sample-management/product-specifications`.

`spec` is a flat dict like `{"Name": "Project Everest", "AccountId": "001...",
"Status": "Draft", "Alias__c": "..."}`. The internal helper
`_to_property_list(d) → [{"field": k, "value": v}, ...]` runs on the spec dict
itself, on each `versions[i]["fields"]`, and on each
`versions[i]["items"][j]["fields"]`.

Each entry of `versions` has the shape:

```python
{"fields": {"Name": "v1", "Version": "2", ...},
 "items": [{"fields": {"Name": "...", "Statement": "..."}}, ...]}
```

Wire payload after conversion exactly matches the JSON example on guide
page 457–458.

#### `TransformationsOperations`

```python
async def run(
    self,
    *,
    input_object_ids: list[str],
    input_object_name: str,            # MfgProgramCpntFrcstFact | ManufacturingProgram | Period | Quote | QuoteLineItem
    usage_type: str,                   # ConvertToSalesAgreement | CLMFieldMapping | EligibleProgramRebateType | MapJournalToMemberAggregate | TransformationMapping
    output_object_name: str,           # Opportunity | OpportunityLineItem | OpportunityLineItemSchedule
    output_object_default_values: dict[str, dict[str, Any]] | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run a configured transformation from program/forecast records to opportunities."""
```

Path: `manufacturing/transformations`. `output_object_default_values` is
already a `Map<String, Map<String, Any>>`-shaped dict and is passed straight
through.

#### `WarrantyOperations`

```python
async def supplier_claim(
    self,
    *,
    claim_ids: list[str],
    context_definition: str | None = None,
    context_mapping: str | None = None,
    conversion_type: str | None = None,
    supplier_recovery_products: list[dict[str, Any]] | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Clone warranty claim(s) into supplier recovery claim(s)."""
```

Path: `warranty/supplier-claim` (note: NOT under `manufacturing/`). Each
entry in `supplier_recovery_products` is a `{"product2Id": "...",
"salesContractLineId": "..."}` dict.

### ID normalisation

`ConnectBaseOperations._ensure_18` exists but most of these payloads carry
IDs inside arbitrary nested dicts (`outputObjectDefaultValues`, `properties`
lists, `supplierRecoveryProducts[].product2Id`). Auto-normalisation would
require schema-aware traversal that's brittle and offers no real benefit —
Salesforce accepts both 15- and 18-char forms. Callers who care can convert
via `salesforce_py.utils.convert_to_18_char` themselves.

## Data flow

### Request

1. Method is called with keyword arguments.
2. If `body=` is supplied, it's used verbatim.
3. Otherwise, the method assembles the request body from the named kwargs,
   omitting keys whose values are `None`. Sample management's helper runs
   here.
4. `await self._post(_PATH, json=body)` dispatches via the inherited
   transport, which applies retry + timeout from `_retry.py`.

### Response

1. `ConnectBaseOperations._post` calls `_handle_status`, which raises on
   4xx/5xx (mapping 401 → `AuthError`).
2. JSON body is parsed and returned to the caller.
3. No client-side post-processing — the four response shapes (Sales Agreement
   Output, Sample Management Output, Transformation Output, Warranty To
   Supplier Claims Output) are all returned as-is.

## Error handling

Inherited entirely from `ConnectBaseOperations`:

- `AuthError` on 401 (token invalid / expired).
- `SalesforcePyError` on other 4xx/5xx, with the first 500 chars of the
  response body attached.
- Transient errors (network, 5xx, 408/420/425/429) retried once after 20s
  by `retry_async_http_call` before surfacing.

No method-level error-handling logic. Validation of caller inputs is minimal
— keyword-only signatures already prevent positional mistakes; the API
itself rejects bad values with a clear 400.

## Testing

```
tests/industries/
  __init__.py
  manufacturing/
    __init__.py
    conftest.py                        # mock_connect_session fixture
    test_sales_agreements.py
    test_sample_management.py
    test_transformations.py
    test_warranty.py
    test_property_list.py              # unit tests for _to_property_list
```

`conftest.py` patches `ConnectSession`'s underlying `httpx.AsyncClient`,
following the pattern used by `tests/connect/`. Each per-class test file
asserts:

- Correct path is hit (`manufacturing/sales-agreements`,
  `manufacturing/sample-management/product-specifications`,
  `manufacturing/transformations`, `warranty/supplier-claim`).
- Correct HTTP verb (POST in every case).
- Correct JSON body shape, including the property-list transform for sample
  management.
- `body=` escape hatch is honored verbatim and named kwargs are ignored when
  it's supplied.
- One happy-path success (200 → parsed JSON returned).
- One failure case (401 → `AuthError`, plus one non-401 4xx →
  `SalesforcePyError`). The underlying status mapping is already exhaustively
  tested in `tests/connect/`, so we're just confirming the paths are wired.

`test_property_list.py` covers the helper directly: flat dict →
list-of-pairs; nested versions/items recursion; empty-dict edge case;
non-string values left intact.

No integration tests against a real org in this iteration. Manufacturing
Cloud licensing on the `sdonew` test org is unknown and all four endpoints
mutate state.

## Documentation

- New `src/salesforce_py/industries/manufacturing/README.md` — namespace
  map, one usage example per resource, link to the relevant PDF page numbers
  (455–462) in the Manufacturing Cloud Developer Guide. Mirrors
  `connect/README.md` style.
- One paragraph added to the project's `CLAUDE.md` under `## Architecture`
  describing the `industries/` package as a source-tree organizational layer
  that wires industry-specific operations into existing clients (no new
  client class, no new session, no new extra). Critical for future
  contributors and future Claude Code sessions to know.
- Top-level `README.md` updated only if it currently enumerates clients —
  to be checked during implementation.

## Public re-exports

`src/salesforce_py/industries/manufacturing/__init__.py`:

```python
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

`src/salesforce_py/industries/__init__.py` is empty. Nothing exposed at the
top-level `salesforce_py` namespace; users discover the API via
`connect_client.manufacturing.*`.

## Dependencies

No changes to `pyproject.toml`. These endpoints ride on the existing
`connect` extra (which already pulls in `httpx[http2]`).

## Out of scope for this iteration

- Manufacturing Cloud invocable actions (PDF pages 564–579).
- Manufacturing Cloud Tooling API objects (PDF pages 549–562) — likely
  added later as new operation classes wired into `RestClient.tooling`.
- Manufacturing Cloud metadata API types (PDF pages 484–547).
- The `ind_mfg_sample_mgmt_apex` Apex namespace (PDF pages 581+).
- Other industries (financial services, health, etc.) — `industries/` is
  positioned to absorb them but none are added now.
- Integration tests against a real Manufacturing Cloud org.
