"""Feedback operations for the Salesforce Models REST API."""

from __future__ import annotations

from typing import Any

from salesforce_py.models.base import ModelsBaseOperations


class FeedbackOperations(ModelsBaseOperations):
    """Wrapper for ``/feedback``.

    Submit feedback for a previously generated response.
    """

    async def submit(self, body: dict[str, Any]) -> dict[str, Any]:
        """Submit feedback for generated text.

        The Models API ``/feedback`` endpoint accepts a free-form payload
        describing the generation being rated and the user's feedback
        (``id``, ``feedback``, ``feedbackText``, etc. — see the Models API
        reference). This method forwards the payload unchanged.

        Args:
            body: Feedback payload.

        Returns:
            Parsed JSON response from the feedback endpoint.
        """
        return await self._post("feedback", json=body)
