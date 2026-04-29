"""Text generation operations for the Salesforce Models REST API."""

from __future__ import annotations

from typing import Any

from salesforce_py.models.base import ModelsBaseOperations


class GenerationsOperations(ModelsBaseOperations):
    """Wrapper for ``/models/{modelName}/generations``.

    Generate a response based on a single prompt.
    """

    async def generate(
        self,
        model_name: str,
        prompt: str,
        *,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate text from a prompt.

        Args:
            model_name: API name of the model, e.g.
                ``"sfdc_ai__DefaultOpenAIGPT4OmniMini"``. See
                :mod:`salesforce_py.models.supported_models` for constants.
            prompt: Prompt string passed to the model.
            extra: Additional body properties merged into the request —
                use this for model-specific parameters (``temperature``,
                ``max_tokens``, ``localization``, etc.) that are accepted
                by the Models API.

        Returns:
            Parsed JSON response with ``generation``, ``parameters``, etc.
        """
        body: dict[str, Any] = {"prompt": prompt}
        if extra:
            body.update(extra)
        return await self._post(f"models/{model_name}/generations", json=body)

    async def generate_raw(self, model_name: str, body: dict[str, Any]) -> dict[str, Any]:
        """Send a fully-formed generation request.

        Use this when you need to pass a payload that doesn't fit the
        ``prompt`` + ``extra`` shape of :meth:`generate`.
        """
        return await self._post(f"models/{model_name}/generations", json=body)
