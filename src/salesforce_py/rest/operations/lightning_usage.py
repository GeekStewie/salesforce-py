"""Lightning Usage / Exit / Toggle metrics.

Covers the Lightning Adoption metric sObject endpoints served under
``/services/data/vXX.X/sobjects/``:

- ``LightningExitByPageMetrics`` — Exit frequency from Lightning back to Classic.
- ``LightningToggleMetrics`` — Users who switched between Classic and Lightning.
- ``LightningUsageByAppTypeMetrics`` — Lightning Experience / Salesforce Mobile
  user totals (REST API 44.0+).
- ``LightningUsageByBrowserMetrics`` — Lightning usage grouped by browser.
- ``LightningUsageByFlexiPageMetrics`` — Custom pages viewed most in Lightning.
- ``LightningUsageByPageMetrics`` — Standard pages viewed most in Lightning.

All six are regular sObject-style endpoints; the helpers here just route
straight to them.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class LightningUsageOperations(RestBaseOperations):
    """Wrapper for the Lightning usage metric sObjects."""

    async def exit_by_page(self, **params: Any) -> dict[str, Any]:
        """Return frequency metrics for pages users switched to Classic from."""
        return await self._get("sobjects/LightningExitByPageMetrics", params=params)

    async def toggle(self, **params: Any) -> dict[str, Any]:
        """Return details about users toggling between Classic and Lightning."""
        return await self._get("sobjects/LightningToggleMetrics", params=params)

    async def usage_by_app_type(self, **params: Any) -> dict[str, Any]:
        """Return total LEX / Salesforce Mobile user counts (44.0+)."""
        return await self._get("sobjects/LightningUsageByAppTypeMetrics", params=params)

    async def usage_by_browser(self, **params: Any) -> dict[str, Any]:
        """Return Lightning usage grouped by browser."""
        return await self._get("sobjects/LightningUsageByBrowserMetrics", params=params)

    async def usage_by_flexipage(self, **params: Any) -> dict[str, Any]:
        """Return most-viewed custom pages in Lightning."""
        return await self._get("sobjects/LightningUsageByFlexiPageMetrics", params=params)

    async def usage_by_page(self, **params: Any) -> dict[str, Any]:
        """Return most-viewed standard pages in Lightning."""
        return await self._get("sobjects/LightningUsageByPageMetrics", params=params)
