"""Experience Cloud Microsites Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class MicrositesOperations(ConnectBaseOperations):
    """Wrapper for ``/sites/{siteId}/marketing-integration/forms`` endpoints.

    Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
    prefix) — the client supplies a dedicated ``_data_session``.
    """

    async def save_form(
        self,
        site_id: str,
        form_name: str,
        member_identification_code: str,
        form_fields: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Save a marketing integration form (v53.0+).

        Args:
            site_id: Site ID (15 or 18 characters).
            form_name: Form name.
            member_identification_code: Marketing Cloud Engagement MID.
            form_fields: List of field dicts (each with ``name`` and
                ``type``).

        Returns:
            Form dict.
        """
        site_id = self._ensure_18(site_id)
        body = {
            "formName": form_name,
            "memberIdentificationCode": member_identification_code,
            "formFieldsList": {"formFields": form_fields},
        }
        return await self._post(f"sites/{site_id}/marketing-integration/forms", json=body)

    async def get_form(
        self,
        site_id: str,
        form_id: str,
    ) -> dict[str, Any]:
        """Get a marketing integration form.

        Args:
            site_id: Site ID (15 or 18 characters).
            form_id: Form ID.

        Returns:
            Form dict.
        """
        site_id = self._ensure_18(site_id)
        return await self._get(f"sites/{site_id}/marketing-integration/forms/{form_id}")

    async def submit_form(
        self,
        site_id: str,
        form_id: str,
        form_fields: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Submit a marketing integration form.

        Args:
            site_id: Site ID (15 or 18 characters).
            form_id: Form ID.
            form_fields: List of submitted field dicts (each with
                ``name`` and ``value``).

        Returns:
            Form Submission dict.
        """
        site_id = self._ensure_18(site_id)
        body = {"formFieldsList": {"formFields": form_fields}}
        return await self._post(
            f"sites/{site_id}/marketing-integration/forms/{form_id}/data",
            json=body,
        )
