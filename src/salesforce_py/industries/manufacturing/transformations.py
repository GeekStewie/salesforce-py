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
