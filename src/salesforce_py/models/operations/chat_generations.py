"""Chat generation operations for the Salesforce Models REST API."""

from __future__ import annotations

from typing import Any

from salesforce_py.models.base import ModelsBaseOperations


class ChatGenerationsOperations(ModelsBaseOperations):
    """Wrapper for ``/models/{modelName}/chat-generations``.

    Generate a response based on a list of chat messages.
    """

    async def generate(
        self,
        model_name: str,
        messages: list[dict[str, Any]],
        *,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate a chat completion from a conversation history.

        Args:
            model_name: API name of the model, e.g.
                ``"sfdc_ai__DefaultOpenAIGPT4OmniMini"``.
            messages: List of chat messages. Each message is a dict with
                ``role`` (``"system"`` / ``"user"`` / ``"assistant"``) and
                ``content`` keys, following the OpenAI-compatible chat shape.
            extra: Additional body properties merged into the request
                (``temperature``, ``max_tokens``, ``localization``, etc.).

        Returns:
            Parsed JSON response with ``generationDetails`` / ``parameters``.
        """
        body: dict[str, Any] = {"messages": messages}
        if extra:
            body.update(extra)
        return await self._post(f"models/{model_name}/chat-generations", json=body)

    async def generate_raw(self, model_name: str, body: dict[str, Any]) -> dict[str, Any]:
        """Send a fully-formed chat-generations request."""
        return await self._post(f"models/{model_name}/chat-generations", json=body)
