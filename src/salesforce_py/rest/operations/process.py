"""Process — approvals and workflow rules.

Covers:

- ``/services/data/vXX.X/process/approvals`` — Submit, approve, and reject
  approval requests.
- ``/services/data/vXX.X/process/rules`` — Retrieve active workflow rules
  and trigger them.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class ProcessOperations(RestBaseOperations):
    """Wrapper for ``/process/approvals`` and ``/process/rules``."""

    # ------------------------------------------------------------------
    # Approvals
    # ------------------------------------------------------------------

    async def list_approvals(self) -> dict[str, Any]:
        """Return all approval processes configured in the org."""
        return await self._get("process/approvals")

    async def submit_approvals(self, requests: list[dict[str, Any]]) -> dict[str, Any]:
        """Submit one or more approval requests.

        Each request dict typically carries ``actionType`` (``Submit``,
        ``Approve``, ``Reject``), ``contextId``, ``comments``,
        ``nextApproverIds``, and optionally ``processDefinitionNameOrId``.
        """
        return await self._post("process/approvals", json={"requests": requests})

    # ------------------------------------------------------------------
    # Workflow rules
    # ------------------------------------------------------------------

    async def list_rules(self) -> dict[str, Any]:
        """Return all active workflow rules in the org."""
        return await self._get("process/rules")

    async def list_rules_for_object(self, object_name: str) -> dict[str, Any]:
        """Return active workflow rules for a specific sObject."""
        return await self._get(f"process/rules/{object_name}")

    async def get_rule(self, object_name: str, rule_id: str) -> dict[str, Any]:
        """Return detailed metadata for a single workflow rule."""
        return await self._get(f"process/rules/{object_name}/{rule_id}")

    async def trigger_rules(self, context_ids: list[str]) -> dict[str, Any]:
        """Trigger all active workflow rules for the specified record IDs."""
        return await self._post("process/rules", json={"contextIds": context_ids})
