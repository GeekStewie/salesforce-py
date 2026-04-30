"""Miscellaneous REST API resources — one-endpoint / small-surface wrappers.

Groups together the small-surface resources that don't warrant their own
module. Each class binds to a single top-level path and exposes generic
``get`` / ``post`` / ``patch`` / ``put`` / ``delete`` verbs for the sub-paths
documented in the REST API Developer Guide.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


def _make_passthrough(namespace: str):  # noqa: ANN202 - returns a generated class
    """Build a subclass of :class:`RestBaseOperations` bound to ``/{namespace}``."""

    class _Passthrough(RestBaseOperations):
        async def get(
            self, subpath: str = "", *, params: dict[str, Any] | None = None
        ) -> dict[str, Any]:
            """Issue a GET against ``/{base}/{subpath}``."""
            path = namespace if not subpath else f"{namespace}/{subpath.lstrip('/')}"
            return await self._get(path, params=params)

        async def post(
            self,
            subpath: str = "",
            *,
            json: dict[str, Any] | None = None,
            params: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            """Issue a POST against ``/{base}/{subpath}``."""
            path = namespace if not subpath else f"{namespace}/{subpath.lstrip('/')}"
            return await self._post(path, json=json, params=params)

        async def patch(
            self,
            subpath: str = "",
            *,
            json: dict[str, Any] | None = None,
            params: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            """Issue a PATCH against ``/{base}/{subpath}``."""
            path = namespace if not subpath else f"{namespace}/{subpath.lstrip('/')}"
            return await self._patch(path, json=json, params=params)

        async def put(
            self,
            subpath: str = "",
            *,
            json: dict[str, Any] | None = None,
            params: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            """Issue a PUT against ``/{base}/{subpath}``."""
            path = namespace if not subpath else f"{namespace}/{subpath.lstrip('/')}"
            return await self._put(path, json=json, params=params)

        async def delete(
            self, subpath: str = "", *, params: dict[str, Any] | None = None
        ) -> dict[str, Any]:
            """Issue a DELETE against ``/{base}/{subpath}``."""
            path = namespace if not subpath else f"{namespace}/{subpath.lstrip('/')}"
            return await self._delete(path, params=params)

    _Passthrough.__doc__ = f"Pass-through wrapper for ``/{namespace}`` resources."
    return _Passthrough


# Small-surface REST resources that map 1:1 to a top-level path.
#
# Each of these wrappers exposes generic verbs; the specific sub-paths are
# documented in the Salesforce REST API Developer Guide under the linked
# resource name.
AssetManagementOperations = _make_passthrough("asset-management")
ChatterOperations = _make_passthrough("chatter")
CommerceOperations = _make_passthrough("commerce")
ConnectOperations = _make_passthrough("connect")
ConsentOperations = _make_passthrough("consent")
ContactTracingOperations = _make_passthrough("contact-tracing")
DedupeOperations = _make_passthrough("dedupe")
KnowledgeManagementOperations = _make_passthrough("knowledgeManagement")
PaymentsOperations = _make_passthrough("payments")
SchedulingOperations = _make_passthrough("scheduling")
JobsOperations = _make_passthrough("jobs")
LicensingOperations = _make_passthrough("licensing")
LocalizedValueOperations = _make_passthrough("localizedvalue")

# Connect-industry verticals (documented as ``/connect/<vertical>``).
FinancialServicesOperations = _make_passthrough("connect/financialservices")
HealthCloudOperations = _make_passthrough("connect/health/care-services")
ManufacturingOperations = _make_passthrough("connect/manufacturing")


__all__ = [
    "AssetManagementOperations",
    "ChatterOperations",
    "CommerceOperations",
    "ConnectOperations",
    "ConsentOperations",
    "ContactTracingOperations",
    "DedupeOperations",
    "FinancialServicesOperations",
    "HealthCloudOperations",
    "JobsOperations",
    "KnowledgeManagementOperations",
    "LicensingOperations",
    "LocalizedValueOperations",
    "ManufacturingOperations",
    "PaymentsOperations",
    "SchedulingOperations",
]
