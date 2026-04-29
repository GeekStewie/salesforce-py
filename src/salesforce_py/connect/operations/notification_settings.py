"""Notification Settings Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class NotificationSettingsOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/notifications/settings/`` and
    ``/connect/notifications/app-settings/`` endpoints.

    Provides access to per-type delivery-channel toggles (desktop,
    email, mobile, slack) and per-app enablement for notification types.
    """

    # ------------------------------------------------------------------
    # Org-wide notification settings
    # ------------------------------------------------------------------

    async def list_org_settings(self) -> dict[str, Any]:
        """Get notification settings for the org.

        Returns:
            Notification Settings Collection dict.
        """
        return await self._get("notifications/settings/organization")

    async def get_org_setting(
        self,
        notification_type_or_id: str,
    ) -> dict[str, Any]:
        """Get a single notification setting for the org.

        Args:
            notification_type_or_id: Notification type API name or ID.

        Returns:
            Notification Setting dict.
        """
        return await self._get(f"notifications/settings/organization/{notification_type_or_id}")

    async def set_org_setting(
        self,
        notification_type_or_id: str,
        *,
        desktop_enabled: bool | None = None,
        email_enabled: bool | None = None,
        mobile_enabled: bool | None = None,
        slack_enabled: bool | None = None,
    ) -> dict[str, Any]:
        """Set delivery-channel toggles for a notification type.

        Args:
            notification_type_or_id: Notification type API name or ID.
            desktop_enabled: Enable desktop delivery.
            email_enabled: Enable email delivery.
            mobile_enabled: Enable mobile delivery.
            slack_enabled: Enable Slack delivery (reserved; v52.0+).

        Returns:
            Notification Setting dict.
        """
        body: dict[str, Any] = {}
        if desktop_enabled is not None:
            body["desktopEnabled"] = desktop_enabled
        if email_enabled is not None:
            body["emailEnabled"] = email_enabled
        if mobile_enabled is not None:
            body["mobileEnabled"] = mobile_enabled
        if slack_enabled is not None:
            body["slackEnabled"] = slack_enabled
        return await self._post(
            f"notifications/settings/organization/{notification_type_or_id}",
            json=body,
        )

    async def reset_org_setting(
        self,
        notification_type_or_id: str,
    ) -> dict[str, Any]:
        """Reset a notification setting to its default.

        Args:
            notification_type_or_id: Notification type API name or ID.

        Returns:
            Empty dict on success.
        """
        return await self._delete(f"notifications/settings/organization/{notification_type_or_id}")

    # ------------------------------------------------------------------
    # Notification app settings
    # ------------------------------------------------------------------

    async def list_app_settings(
        self,
        *,
        application_id: str | None = None,
    ) -> dict[str, Any]:
        """Get notification app settings for the org.

        Args:
            application_id: Connected app or external client app ID. If
                omitted, the session's app context is used.

        Returns:
            Notification App Settings Collection dict.
        """
        params: dict[str, Any] = {}
        if application_id is not None:
            params["applicationId"] = self._ensure_18(application_id)
        return await self._get("notifications/app-settings/organization", params=params)

    async def get_app_setting(
        self,
        notification_type_or_id: str,
        *,
        application_id: str | None = None,
    ) -> dict[str, Any]:
        """Get a single notification app setting.

        Args:
            notification_type_or_id: Notification type API name or ID.
            application_id: Connected app or external client app ID.

        Returns:
            Notification App Settings Collection dict.
        """
        params: dict[str, Any] = {}
        if application_id is not None:
            params["applicationId"] = self._ensure_18(application_id)
        return await self._get(
            f"notifications/app-settings/organization/{notification_type_or_id}",
            params=params,
        )

    async def set_app_setting(
        self,
        notification_type_or_id: str,
        *,
        enabled: bool | None = None,
        application_id: str | None = None,
    ) -> dict[str, Any]:
        """Set a notification app setting.

        Args:
            notification_type_or_id: Notification type API name or ID.
            enabled: Whether to enable delivery of the type for the app.
            application_id: Connected app or external client app ID.

        Returns:
            Notification App Setting dict.
        """
        body: dict[str, Any] = {}
        if enabled is not None:
            body["enabled"] = enabled
        if application_id is not None:
            body["applicationId"] = self._ensure_18(application_id)
        return await self._post(
            f"notifications/app-settings/organization/{notification_type_or_id}",
            json=body,
        )

    async def reset_app_setting(
        self,
        notification_type_or_id: str,
        *,
        application_id: str | None = None,
    ) -> dict[str, Any]:
        """Reset a notification app setting to its default.

        Args:
            notification_type_or_id: Notification type API name or ID.
            application_id: Connected app or external client app ID.

        Returns:
            Empty dict on success.
        """
        params: dict[str, Any] = {}
        if application_id is not None:
            params["applicationId"] = self._ensure_18(application_id)
        return await self._delete(
            f"notifications/app-settings/organization/{notification_type_or_id}",
            params=params,
        )
