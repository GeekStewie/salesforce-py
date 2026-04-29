"""Push Notifications Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class PushNotificationsOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/notifications/push`` endpoint.

    Sends a mobile push notification to client apps on users' devices.
    This resource is only accessible when the session is established
    with a client app that is developed in the same org or installed in
    the same package as the recipient's client app.
    """

    async def send_push(
        self,
        app_name: str,
        user_ids: list[str],
        payload: str,
        *,
        namespace: str | None = None,
    ) -> dict[str, Any]:
        """Send a push notification.

        Args:
            app_name: API name of the client app that the push
                notification is sent to.
            user_ids: Recipient user IDs (15 or 18 characters).
            payload: Push notification payload in JSON-format string
                (e.g. ``"{'aps':{'alert':'test','badge':0}}"``).
            namespace: Namespace of the client app. Required if the
                receiving app has a namespace set.

        Returns:
            Push Notification Result dict.
        """
        body: dict[str, Any] = {
            "appName": app_name,
            "userIds": self._ensure_18_list(user_ids),
            "payload": payload,
        }
        if namespace is not None:
            body["namespace"] = namespace
        return await self._post("notifications/push", json=body)
