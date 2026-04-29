"""Activity Reminders Connect API operations (v39.0+)."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class ActivityRemindersOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/reminders/...`` endpoints."""

    async def list_activity_reminders(
        self,
        *,
        max_record_count: int | None = None,
        number_of_days: int | None = None,
        activity_type: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of upcoming activity reminders in Salesforce Classic.

        Args:
            max_record_count: Number of returned reminders. Max 2,000, default 100.
            number_of_days: Returns reminders due within the next N days. Default 7, max 365.
            activity_type: Filter by activity type — ``"All"``, ``"Event"``, or ``"Task"``.

        Returns:
            Activity Reminders Resources dict.
        """
        params: dict[str, Any] = {}
        if max_record_count is not None:
            params["maxRecordCount"] = max_record_count
        if number_of_days is not None:
            params["numberOfDays"] = number_of_days
        if activity_type is not None:
            params["type"] = activity_type
        return await self._get("reminders/activities", params=params)

    async def get_activity_reminder(self, activity_id: str) -> dict[str, Any]:
        """Get information about an activity reminder in Salesforce Classic.

        Args:
            activity_id: Activity (Event/Task) ID.

        Returns:
            Activity Reminder dict.
        """
        activity_id = self._ensure_18(activity_id)
        return await self._get(f"reminders/{activity_id}")

    async def update_activity_reminder(
        self,
        activity_id: str,
        *,
        is_reminder_displayed: bool,
        reminder_date_time: str | None = None,
    ) -> dict[str, Any]:
        """Update an activity reminder (PATCH).

        Args:
            activity_id: Activity ID.
            is_reminder_displayed: Whether the reminder has been displayed.
            reminder_date_time: ISO 8601 reminder display date/time.

        Returns:
            Activity Reminder dict.
        """
        activity_id = self._ensure_18(activity_id)
        payload: dict[str, Any] = {"isReminderDisplayed": is_reminder_displayed}
        if reminder_date_time is not None:
            payload["reminderDateTime"] = reminder_date_time
        return await self._patch(f"reminders/{activity_id}", json=payload)

    async def replace_activity_reminder(
        self,
        activity_id: str,
        *,
        reminder_date_time: str | None = None,
    ) -> dict[str, Any]:
        """Replace an activity reminder (PUT).

        Args:
            activity_id: Activity ID.
            reminder_date_time: ISO 8601 reminder display date/time.

        Returns:
            Activity Reminder dict.
        """
        activity_id = self._ensure_18(activity_id)
        payload: dict[str, Any] = {}
        if reminder_date_time is not None:
            payload["reminderDateTime"] = reminder_date_time
        return await self._put(f"reminders/{activity_id}", json=payload)

    async def delete_activity_reminder(self, activity_id: str) -> dict[str, Any]:
        """Delete an activity reminder.

        Args:
            activity_id: Activity ID.

        Returns:
            Empty dict on success.
        """
        activity_id = self._ensure_18(activity_id)
        return await self._delete(f"reminders/{activity_id}")
