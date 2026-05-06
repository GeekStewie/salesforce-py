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
