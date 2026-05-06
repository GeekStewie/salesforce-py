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

    async def test_raises_when_claim_ids_missing_and_no_body(self):
        c = await _client(_mock_response(200, {"id": "0Z..."}))
        with pytest.raises(ValueError, match="claim_ids is required"):
            await c.manufacturing.warranty.supplier_claim()
