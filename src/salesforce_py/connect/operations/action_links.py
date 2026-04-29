"""Action Links Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class ActionLinksOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/action-link*`` endpoints.

    Covers action link group definitions, action link groups, action links,
    and action link diagnostic information. All methods are async.

    Community-scoped variants of each resource are supported via the optional
    ``community_id`` keyword argument.
    """

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _alg_def_path(action_link_group_id: str, community_id: str | None) -> str:
        base = f"action-link-group-definitions/{action_link_group_id}"
        return f"communities/{community_id}/{base}" if community_id else base

    @staticmethod
    def _alg_path(action_link_group_id: str, community_id: str | None) -> str:
        base = f"action-link-groups/{action_link_group_id}"
        return f"communities/{community_id}/{base}" if community_id else base

    @staticmethod
    def _al_path(action_link_id: str, community_id: str | None) -> str:
        base = f"action-links/{action_link_id}"
        return f"communities/{community_id}/{base}" if community_id else base

    # ------------------------------------------------------------------
    # Action Link Group Definitions  /connect/action-link-group-definitions
    # ------------------------------------------------------------------

    async def create_action_link_group_definition(
        self,
        definition: dict[str, Any],
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Create an action link group definition.

        All action links must belong to a group. Create the group definition
        first, then associate it with a feed element via the ``associatedActions``
        capability.

        Args:
            definition: Action Link Group Definition Input payload dict.
            community_id: Optional community ID to scope the request.

        Returns:
            Action Link Group Definition response dict.
        """
        path = (
            f"communities/{community_id}/action-link-group-definitions"
            if community_id
            else "action-link-group-definitions"
        )
        return await self._post(path, json=definition)

    async def get_action_link_group_definition(
        self,
        action_link_group_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get an action link group definition.

        The calling client must be the same app that created the definition,
        and the user must be the creator or have View All Data permission.

        Args:
            action_link_group_id: ID of the action link group definition
                (15 or 18 characters).
            community_id: Optional community ID to scope the request.

        Returns:
            Action Link Group Definition response dict.
        """
        action_link_group_id = self._ensure_18(action_link_group_id)
        return await self._get(self._alg_def_path(action_link_group_id, community_id))

    async def delete_action_link_group_definition(
        self,
        action_link_group_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Delete an action link group definition.

        Removes all references to the definition from feed elements.

        Args:
            action_link_group_id: ID of the action link group definition
                (15 or 18 characters).
            community_id: Optional community ID to scope the request.

        Returns:
            Empty dict on success (204 No Content).
        """
        action_link_group_id = self._ensure_18(action_link_group_id)
        return await self._delete(self._alg_def_path(action_link_group_id, community_id))

    # ------------------------------------------------------------------
    # Action Link Groups  /connect/action-link-groups
    # ------------------------------------------------------------------

    async def get_action_link_group(
        self,
        action_link_group_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get an action link group including context-user state.

        Unlike definitions, groups are accessible by any client.

        Args:
            action_link_group_id: ID of the action link group (15 or 18 characters).
            community_id: Optional community ID to scope the request.

        Returns:
            Action link group dict including per-user visibility state.
        """
        action_link_group_id = self._ensure_18(action_link_group_id)
        return await self._get(self._alg_path(action_link_group_id, community_id))

    # ------------------------------------------------------------------
    # Action Links  /connect/action-links
    # ------------------------------------------------------------------

    async def get_action_link(
        self,
        action_link_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get information about an action link.

        Args:
            action_link_id: ID of the action link (15 or 18 characters).
            community_id: Optional community ID to scope the request.

        Returns:
            Platform Action response dict.
        """
        action_link_id = self._ensure_18(action_link_id)
        return await self._get(self._al_path(action_link_id, community_id))

    async def update_action_link_status(
        self,
        action_link_id: str,
        status: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Update the status of an action link.

        To trigger the API call for ``Api`` and ``ApiAsync`` action links, set
        *status* to ``"PendingStatus"``. For ``Download`` and ``Ui`` links,
        set it to ``"SuccessfulStatus"`` or ``"FailedStatus"`` once your
        application has handled the outcome.

        Valid values: ``"NewStatus"``, ``"PendingStatus"``,
        ``"SuccessfulStatus"``, ``"FailedStatus"``.

        Args:
            action_link_id: ID of the action link (15 or 18 characters).
            status: New status value.
            community_id: Optional community ID to scope the request.

        Returns:
            Updated Platform Action response dict.
        """
        action_link_id = self._ensure_18(action_link_id)
        return await self._patch(
            self._al_path(action_link_id, community_id),
            json={"status": status},
        )

    # ------------------------------------------------------------------
    # Action Link Diagnostic Info  /connect/action-links/{id}/diagnostic-info
    # ------------------------------------------------------------------

    async def get_action_link_diagnostic_info(
        self,
        action_link_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get diagnostic information returned when an action link executes.

        Only available to users who can access the action link.

        Args:
            action_link_id: ID of the action link (15 or 18 characters).
            community_id: Optional community ID to scope the request.

        Returns:
            Action Link Diagnostic response dict.
        """
        action_link_id = self._ensure_18(action_link_id)
        base = self._al_path(action_link_id, community_id)
        return await self._get(f"{base}/diagnostic-info")
