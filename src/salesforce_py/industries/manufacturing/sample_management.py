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
                raise ValueError("operation and spec are required when body is not supplied")
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
