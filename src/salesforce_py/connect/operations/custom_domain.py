"""Custom Domain Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CustomDomainOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/custom-domain/...`` endpoints.

    A custom domain is a domain you own (e.g. ``https://www.example.com``)
    that serves content from Experience Cloud sites or Salesforce Sites.
    """

    async def list_domains(self) -> dict[str, Any]:
        """Get a list of custom domains for the org (v60.0+).

        Returns:
            Custom Domain Collection dict.
        """
        return await self._get("custom-domain/domains")

    async def get_domain(self, domain_id: str) -> dict[str, Any]:
        """Get information about a custom domain (v60.0+).

        Args:
            domain_id: Custom domain ID.

        Returns:
            Custom Domain Detail dict.
        """
        return await self._get(f"custom-domain/domains/{domain_id}")

    async def get_domain_id(self, domain_name: str) -> dict[str, Any]:
        """Get the ID for a custom domain by name (v63.0+).

        Args:
            domain_name: Domain name, e.g. ``www.example.com``.

        Returns:
            Custom Domain ID dict.
        """
        return await self._get(f"custom-domain/domains/{domain_name}/domainId")

    async def get_expected_cname(self, domain_name: str) -> dict[str, Any]:
        """Get the CNAME record used to verify domain ownership (v63.0+).

        Args:
            domain_name: Domain name.

        Returns:
            Custom Domain CNAME for Domain Verification dict.
        """
        return await self._get(f"custom-domain/domains/{domain_name}/expected-cname")

    async def get_expected_cdn_cname(self, domain_name: str) -> dict[str, Any]:
        """Get the CNAME record required for the Salesforce CDN (v63.0+).

        Args:
            domain_name: Domain name.

        Returns:
            Custom Domain CNAME for the Salesforce CDN dict.
        """
        return await self._get(f"custom-domain/domains/{domain_name}/expected-cdn-validation-cname")

    async def list_custom_urls(self, domain_id: str) -> dict[str, Any]:
        """Get custom URLs for a custom domain (v62.0+).

        Args:
            domain_id: Custom domain ID.

        Returns:
            Custom Domain Custom URL Collection dict.
        """
        return await self._get(f"custom-domain/domains/{domain_id}/custom-urls")

    async def get_custom_url(self, domain_id: str, custom_url_id: str) -> dict[str, Any]:
        """Get information about a custom URL (v62.0+).

        Args:
            domain_id: Custom domain ID.
            custom_url_id: Custom URL ID.

        Returns:
            Custom URL Detail dict.
        """
        return await self._get(f"custom-domain/domains/{domain_id}/custom-urls/{custom_url_id}")

    async def get_pending_configuration(self, domain_id: str) -> dict[str, Any]:
        """Get pending configuration options for a custom domain (v66.0+).

        Args:
            domain_id: Custom domain ID.

        Returns:
            Custom Domain Pending Configuration Detail dict.
        """
        return await self._get(f"custom-domain/domains/{domain_id}/pending-configuration")

    async def list_site_custom_urls(self, store_or_site_id: str) -> dict[str, Any]:
        """Get custom URLs for a custom domain on a site or store (v63.0+).

        Args:
            store_or_site_id: Site or store ID.

        Returns:
            Custom Domain Custom URL Collection dict.
        """
        store_or_site_id = self._ensure_18(store_or_site_id)
        return await self._get(f"custom-domain/domains/sites/{store_or_site_id}/custom-urls")
