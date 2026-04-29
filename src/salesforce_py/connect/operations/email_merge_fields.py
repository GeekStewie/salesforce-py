"""Email Merge Field Services Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class EmailMergeFieldsOperations(ConnectBaseOperations):
    """Wrapper for ``/email-merge-fields`` endpoint.

    Returns a list of merge fields for one or more objects. A merge
    field is a placeholder usable in email templates, mail-merge
    templates, custom links, and formulas.

    Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
    prefix), so the client supplies a dedicated session.
    """

    async def list_merge_fields(
        self,
        object_api_names: list[str],
    ) -> dict[str, Any]:
        """Get merge fields for a collection of objects.

        Args:
            object_api_names: API names of the objects being referenced.

        Returns:
            Email Merge Field dict.
        """
        params = {"objectApiNames": ",".join(object_api_names)}
        return await self._get("email-merge-fields", params=params)
