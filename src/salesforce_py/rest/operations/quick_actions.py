"""Quick Actions — global quick actions directory.

Covers:

- ``/services/data/vXX.X/quickActions`` — Global quick actions, their types,
  and custom fields / objects that appear in the Chatter feed.

(sObject-scoped quick actions live under ``/sobjects/{sObject}/quickActions``
and are handled by :class:`SObjectsOperations.sobject_quick_actions` /
:meth:`SObjectsOperations.invoke_sobject_quick_action`.)
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class QuickActionsOperations(RestBaseOperations):
    """Wrapper for ``/quickActions`` (global)."""

    async def list_actions(self) -> list[dict[str, Any]]:
        """Return all global quick actions and their types."""
        response = await self._get("quickActions")
        if isinstance(response, list):
            return response
        return response.get("quickActions", [])  # type: ignore[return-value]

    async def get_action(self, action_name: str) -> dict[str, Any]:
        """Return a single quick action by developer name."""
        return await self._get(f"quickActions/{action_name}")

    async def describe_action(self, action_name: str) -> dict[str, Any]:
        """Return detailed metadata for a quick action."""
        return await self._get(f"quickActions/{action_name}/describe")

    async def get_default_values(
        self, action_name: str, *, context_id: str | None = None
    ) -> dict[str, Any]:
        """Return the default values that a quick action pre-populates."""
        path = f"quickActions/{action_name}/defaultValues"
        if context_id:
            path = f"{path}/{context_id}"
        return await self._get(path)

    async def invoke_action(
        self,
        action_name: str,
        *,
        context_id: str | None = None,
        record: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Invoke a global quick action."""
        payload: dict[str, Any] = {}
        if context_id is not None:
            payload["contextId"] = context_id
        if record is not None:
            payload["record"] = record
        return await self._post(
            f"quickActions/{action_name}", json=payload or None
        )
