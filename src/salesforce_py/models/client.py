"""User-facing entry point for the Salesforce Models REST API."""

from __future__ import annotations

from salesforce_py._retry import DEFAULT_TIMEOUT
from salesforce_py.models._session import _DEFAULT_BASE_URL, ModelsSession
from salesforce_py.models.operations.chat_generations import ChatGenerationsOperations
from salesforce_py.models.operations.embeddings import EmbeddingsOperations
from salesforce_py.models.operations.feedback import FeedbackOperations
from salesforce_py.models.operations.generations import GenerationsOperations


class ModelsClient:
    """Async client for the Salesforce Models REST API.

    Wraps the ``/einstein/platform/v1/`` endpoints served from
    ``https://api.salesforce.com`` (or the geo-routed host returned by the
    token endpoint). Exposes four grouped namespaces — one per capability:

    - :attr:`chat_generations` — ``/models/{modelName}/chat-generations``
    - :attr:`embeddings`       — ``/models/{modelName}/embeddings``
    - :attr:`generations`      — ``/models/{modelName}/generations``
    - :attr:`feedback`         — ``/feedback``

    Intended to be used as an async context manager::

        async with ModelsClient(access_token) as client:
            result = await client.generations.generate(
                "sfdc_ai__DefaultOpenAIGPT4OmniMini",
                "Tell me a story about a financial advisor.",
            )

    Can also be used without a context manager — call :meth:`open` and
    :meth:`close` manually in that case.

    Args:
        access_token: Bearer JWT minted from the ``/services/oauth2/token``
            endpoint with the ``sfap_api einstein_gpt_api api`` scopes. Use
            :func:`salesforce_py.models.fetch_token` to mint one.
        base_url: Override the API host. Defaults to
            ``https://api.salesforce.com/einstein/platform/v1/``. Pass the
            ``api_instance_url`` returned by the token endpoint when you
            want the geo-specific host.
        app_context: Value for the ``x-sfdc-app-context`` header (default
            ``"EinsteinGPT"``).
        client_feature_id: Value for the ``x-client-feature-id`` header
            (default ``"ai-platform-models-connected-app"``).
        timeout: Default HTTP request timeout in seconds.
        http2: Negotiate HTTP/2 when the server supports it (falls back to
            HTTP/1.1). Defaults to ``True``.
    """

    def __init__(
        self,
        access_token: str,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        app_context: str = "EinsteinGPT",
        client_feature_id: str = "ai-platform-models-connected-app",
        timeout: float = DEFAULT_TIMEOUT,
        http2: bool = True,
    ) -> None:
        self._session = ModelsSession(
            access_token=access_token,
            base_url=base_url,
            app_context=app_context,
            client_feature_id=client_feature_id,
            timeout=timeout,
            http2=http2,
        )
        self.chat_generations = ChatGenerationsOperations(self._session)
        self.embeddings = EmbeddingsOperations(self._session)
        self.feedback = FeedbackOperations(self._session)
        self.generations = GenerationsOperations(self._session)

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> ModelsClient:
        await self.open()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def open(self) -> None:
        """Open the underlying HTTP session."""
        await self._session.open()

    async def close(self) -> None:
        """Close the underlying HTTP session."""
        await self._session.close()

    def __repr__(self) -> str:
        return f"ModelsClient(base_url={self._session._base_url!r})"
