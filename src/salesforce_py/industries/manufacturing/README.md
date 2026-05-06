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
