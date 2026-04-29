"""Quick Text Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class QuickTextOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/quicktextbody`` endpoint.

    Retrieves a rendered quick-text body, substituting merge fields based
    on the supplied contextual record IDs.
    """

    async def get_quick_text_body(
        self,
        quick_text_id: str,
        what_id: str,
        who_id: str,
        *,
        channel: str | None = None,
        launch_source: str | None = None,
        quick_text_context: str | None = None,
        quick_text_message: str | None = None,
    ) -> dict[str, Any]:
        """Get the rendered body of a quick text template.

        Args:
            quick_text_id: ID of the quick text (15 or 18 characters).
            what_id: ID of a nonhuman object (e.g. account, case).
            who_id: ID of a human object (e.g. lead, contact).
            channel: Channel in which the quick text was created
                (``Email``, ``Event``, ``Generic``, ``Internal``,
                ``Knowledge``, ``Live Agent``, ``Messaging``, ``Phone``,
                ``Portal``, ``Social``, ``Task``).
            launch_source: How the user started the quick text
                (``Floater``, ``Keyboard shortcut``, ``Macro``, ``Toolbar``).
            quick_text_context: Context of the quick text
                (``Preview`` or ``Runtime``).
            quick_text_message: Content of the original text template
                before the quick text is merged into it.

        Returns:
            Quick Text Preview Body or Quick Text Runtime Body dict.
        """
        params: dict[str, Any] = {
            "quickTextId": self._ensure_18(quick_text_id),
            "whatId": self._ensure_18(what_id),
            "whoId": self._ensure_18(who_id),
        }
        if channel is not None:
            params["channel"] = channel
        if launch_source is not None:
            params["launchSource"] = launch_source
        if quick_text_context is not None:
            params["quickTextContext"] = quick_text_context
        if quick_text_message is not None:
            params["quickTextMessage"] = quick_text_message
        return await self._get("quicktextbody", params=params)
