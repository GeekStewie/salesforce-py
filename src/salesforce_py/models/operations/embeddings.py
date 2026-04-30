"""Embeddings operations for the Salesforce Models REST API."""

from __future__ import annotations

from typing import Any

from salesforce_py.models.base import ModelsBaseOperations


class EmbeddingsOperations(ModelsBaseOperations):
    """Wrapper for ``/models/{modelName}/embeddings``.

    Create an embedding vector representing one or more input strings.
    """

    async def embed(
        self,
        model_name: str,
        input: str | list[str],
        *,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create embeddings for a string or list of strings.

        Args:
            model_name: API name of an embeddings-capable model, e.g.
                ``"sfdc_ai__DefaultOpenAITextEmbeddingAda_002"``.
            input: Single string or list of strings to embed. A scalar is
                wrapped into a one-element list — the Models API requires
                ``input`` to be an array even for a single text.
            extra: Additional body properties merged into the request.

        Returns:
            Parsed JSON response with ``embeddings``, ``usage``, etc.
        """
        payload_input = [input] if isinstance(input, str) else list(input)
        body: dict[str, Any] = {"input": payload_input}
        if extra:
            body.update(extra)
        return await self._post(f"models/{model_name}/embeddings", json=body)

    async def embed_raw(self, model_name: str, body: dict[str, Any]) -> dict[str, Any]:
        """Send a fully-formed embeddings request."""
        return await self._post(f"models/{model_name}/embeddings", json=body)
