"""App Menu — Lightning / mobile navigation menu.

Covers:

- ``/services/data/vXX.X/appMenu`` — App menu types.
- ``/services/data/vXX.X/appMenu/AppSwitcher`` — Items from the Salesforce
  app dropdown menu.
- ``/services/data/vXX.X/appMenu/Salesforce1`` — Items from the Salesforce
  mobile app navigation menu.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class AppMenuOperations(RestBaseOperations):
    """Wrapper for ``/appMenu`` resources."""

    async def get_types(self) -> dict[str, Any]:
        """Return the list of app menu types available in the org."""
        return await self._get("appMenu")

    async def get_app_switcher(self) -> dict[str, Any]:
        """Return app switcher items from the Salesforce dropdown menu."""
        return await self._get("appMenu/AppSwitcher")

    async def get_salesforce_mobile(self) -> dict[str, Any]:
        """Return navigation menu items for the Salesforce mobile app."""
        return await self._get("appMenu/Salesforce1")
