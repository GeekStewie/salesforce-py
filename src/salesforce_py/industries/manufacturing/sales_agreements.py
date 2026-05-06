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
