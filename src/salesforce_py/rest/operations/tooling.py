"""Tooling API — ``/services/data/vXX.X/tooling`` pass-through helpers.

The full Tooling API surface is documented in the Tooling API Developer
Guide. Rather than re-implementing every endpoint, this wrapper exposes
verbs that route to ``/tooling/{subpath}``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class ToolingOperations(RestBaseOperations):
    """Pass-through wrapper for ``/tooling``."""

    # ------------------------------------------------------------------
    # Directory + high-level helpers
    # ------------------------------------------------------------------

    async def list_resources(self) -> dict[str, Any]:
        """Return the list of Tooling API resources available for this version."""
        return await self._get("tooling")

    async def query(self, soql: str) -> dict[str, Any]:
        """Execute a SOQL query against Tooling-API-visible entities."""
        return await self._get("tooling/query", params={"q": soql})

    async def query_more(self, next_records_url: str) -> dict[str, Any]:
        """Fetch the next page of a Tooling API query result."""
        locator = next_records_url
        prefix = f"/services/data/v{self._session._api_version}/"
        if locator.startswith(prefix):
            locator = locator[len(prefix) :]
        return await self._get(locator.lstrip("/"))

    async def describe_global(self) -> dict[str, Any]:
        """Return the Tooling-API describe global payload."""
        return await self._get("tooling/sobjects")

    async def describe_sobject(self, object_name: str) -> dict[str, Any]:
        """Describe a single Tooling API sObject."""
        return await self._get(f"tooling/sobjects/{object_name}/describe")

    async def execute_anonymous(self, anonymous_body: str) -> dict[str, Any]:
        """Run Apex anonymously via ``/tooling/executeAnonymous``."""
        return await self._get(
            "tooling/executeAnonymous", params={"anonymousBody": anonymous_body}
        )

    async def run_tests_asynchronous(
        self, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Submit Apex tests for asynchronous execution."""
        return await self._post("tooling/runTestsAsynchronous", json=body)

    async def run_tests_synchronous(self, body: dict[str, Any]) -> dict[str, Any]:
        """Run Apex tests synchronously."""
        return await self._post("tooling/runTestsSynchronous", json=body)

    # ------------------------------------------------------------------
    # Generic passthrough
    # ------------------------------------------------------------------

    async def get(
        self, subpath: str, *, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Issue a GET against ``/tooling/{subpath}``."""
        return await self._get(f"tooling/{subpath.lstrip('/')}", params=params)

    async def post(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a POST against ``/tooling/{subpath}``."""
        return await self._post(
            f"tooling/{subpath.lstrip('/')}", json=json, params=params
        )

    async def patch(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a PATCH against ``/tooling/{subpath}``."""
        return await self._patch(
            f"tooling/{subpath.lstrip('/')}", json=json, params=params
        )

    async def put(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a PUT against ``/tooling/{subpath}``."""
        return await self._put(
            f"tooling/{subpath.lstrip('/')}", json=json, params=params
        )

    async def delete(
        self, subpath: str, *, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Issue a DELETE against ``/tooling/{subpath}``."""
        return await self._delete(
            f"tooling/{subpath.lstrip('/')}", params=params
        )
