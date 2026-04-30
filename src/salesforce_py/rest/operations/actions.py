"""Invocable Actions — standard and custom invocable actions.

Covers:

- ``/services/data/vXX.X/actions/standard`` — Standard actions (Post to
  Chatter, Send Email, etc.).
- ``/services/data/vXX.X/actions/custom`` — Custom invocable actions defined
  in the org.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class ActionsOperations(RestBaseOperations):
    """Wrapper for ``/actions/standard`` and ``/actions/custom``."""

    # ------------------------------------------------------------------
    # Directory
    # ------------------------------------------------------------------

    async def list_actions(self) -> dict[str, Any]:
        """Return available action categories (``standard``, ``custom``)."""
        return await self._get("actions")

    # ------------------------------------------------------------------
    # Standard actions
    # ------------------------------------------------------------------

    async def list_standard_actions(self) -> dict[str, Any]:
        """List the standard invocable actions available in the org."""
        return await self._get("actions/standard")

    async def describe_standard_action(self, action_name: str) -> dict[str, Any]:
        """Return metadata for a standard invocable action."""
        return await self._get(f"actions/standard/{action_name}")

    async def invoke_standard_action(
        self, action_name: str, inputs: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Invoke a standard invocable action.

        Args:
            action_name: Action API name, e.g. ``chatterPost``, ``emailSimple``.
            inputs: List of input dicts — one per invocation.
        """
        return await self._post(
            f"actions/standard/{action_name}", json={"inputs": inputs}
        )

    # ------------------------------------------------------------------
    # Custom actions
    # ------------------------------------------------------------------

    async def list_custom_actions(self) -> dict[str, Any]:
        """List the custom invocable actions defined in the org."""
        return await self._get("actions/custom")

    async def list_custom_action_types(self, action_type: str) -> dict[str, Any]:
        """List custom actions of a specific type (``apex``, ``flow``, ``emailAlert``, etc.)."""
        return await self._get(f"actions/custom/{action_type}")

    async def describe_custom_action(
        self, action_type: str, action_name: str
    ) -> dict[str, Any]:
        """Return metadata for a custom invocable action."""
        return await self._get(f"actions/custom/{action_type}/{action_name}")

    async def invoke_custom_action(
        self,
        action_type: str,
        action_name: str,
        inputs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Invoke a custom invocable action."""
        return await self._post(
            f"actions/custom/{action_type}/{action_name}",
            json={"inputs": inputs},
        )
