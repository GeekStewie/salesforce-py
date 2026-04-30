"""Tabs, Theme, Recently Viewed Items.

Covers:

- ``/services/data/vXX.X/tabs`` — Returns a list of all tabs available to the
  current user.
- ``/services/data/vXX.X/theme`` — Returns the list of icons and colors used
  by themes in the Salesforce application.
- ``/services/data/vXX.X/recent`` — Gets the most recently accessed items
  viewed or referenced by the current user.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class TabsOperations(RestBaseOperations):
    """Wrapper for ``/tabs``."""

    async def list_tabs(self) -> list[dict[str, Any]]:
        """Return all tabs — including Lightning page tabs — available to the user."""
        response = await self._get("tabs")
        if isinstance(response, list):
            return response
        return response.get("tabs", [])  # type: ignore[return-value]


class ThemeOperations(RestBaseOperations):
    """Wrapper for ``/theme``."""

    async def get_theme(self) -> dict[str, Any]:
        """Return theme icons and colors for the Salesforce application."""
        return await self._get("theme")


class RecentOperations(RestBaseOperations):
    """Wrapper for ``/recent``."""

    async def get_recent_items(self, *, limit: int | None = None) -> list[dict[str, Any]]:
        """Return the recently accessed items for the current user."""
        response = await self._get("recent", params={"limit": limit})
        if isinstance(response, list):
            return response
        return response.get("recentItems", [])  # type: ignore[return-value]
