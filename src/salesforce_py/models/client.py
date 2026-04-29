"""User-facing entry point for the Salesforce Models REST API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from salesforce_py._auth import resolve_client_creds, resolve_instance_url
from salesforce_py._retry import DEFAULT_TIMEOUT
from salesforce_py.exceptions import SalesforcePyError
from salesforce_py.models._session import _DEFAULT_BASE_URL, ModelsSession
from salesforce_py.models.token import fetch_token

if TYPE_CHECKING:
    from salesforce_py.sf.org import SFOrg
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
    # Alternate constructors
    # ------------------------------------------------------------------

    @classmethod
    async def from_org(
        cls,
        org: SFOrg,
        consumer_key: str,
        consumer_secret: str,
        *,
        app_context: str = "EinsteinGPT",
        client_feature_id: str = "ai-platform-models-connected-app",
        timeout: float = DEFAULT_TIMEOUT,
        http2: bool = True,
    ) -> ModelsClient:
        """Create a :class:`ModelsClient` via an :class:`~salesforce_py.sf.org.SFOrg`.

        Calls :meth:`~salesforce_py.sf.org.SFOrg._ensure_connected` to
        resolve the org's ``instance_url`` (used as ``my_domain``), then
        calls :func:`~salesforce_py.models.fetch_token` with the supplied
        consumer credentials.

        Args:
            org: An :class:`~salesforce_py.sf.org.SFOrg` instance (from
                :class:`~salesforce_py.sf.SFOrgTask` or standalone).
            consumer_key: External Client App OAuth consumer key.
            consumer_secret: External Client App OAuth consumer secret.
            app_context: Value for the ``x-sfdc-app-context`` header.
            client_feature_id: Value for the ``x-client-feature-id`` header.
            timeout: Default HTTP request timeout in seconds.
            http2: Negotiate HTTP/2 when the server supports it.

        Returns:
            A new :class:`ModelsClient` bound to the freshly minted token.

        Raises:
            AuthError: If the token request fails (wrong credentials or missing
                scopes).
            SalesforcePyError: On any other transport failure.

        Example::

            from salesforce_py.sf import SFOrgTask
            from salesforce_py.models import ModelsClient

            task = SFOrgTask("my-org-alias")
            async with await ModelsClient.from_org(
                task._org,
                consumer_key="...",
                consumer_secret="...",
            ) as client:
                reply = await client.chat_generations.generate(model, messages)
        """
        org._ensure_connected()
        token = await fetch_token(
            my_domain=org.instance_url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            timeout=timeout,
        )
        base_url = (
            f"{token.api_instance_url}/einstein/platform/v1/"
            if token.api_instance_url
            else _DEFAULT_BASE_URL
        )
        return cls(
            token.access_token,
            base_url=base_url,
            app_context=app_context,
            client_feature_id=client_feature_id,
            timeout=timeout,
            http2=http2,
        )

    @classmethod
    async def from_env(
        cls,
        *,
        app_context: str = "EinsteinGPT",
        client_feature_id: str = "ai-platform-models-connected-app",
        timeout: float = DEFAULT_TIMEOUT,
        http2: bool = True,
    ) -> ModelsClient:
        """Create a :class:`ModelsClient` from environment variables.

        Reads ``SF_MODELS_CLIENT_ID`` and ``SF_MODELS_CLIENT_SECRET`` and
        mints a ``client_credentials`` token via :func:`~salesforce_py.models.fetch_token`.
        The My Domain URL is read from ``SF_MODELS_INSTANCE_URL``, falling
        back to ``SF_INSTANCE_URL``.

        .. note::
            The Models API requires ``sfap_api einstein_gpt_api api`` scopes on the
            External Client App. A standard SF CLI session token does **not** carry
            those scopes, so there is no SF CLI fallback for this client — client
            credentials are always required.

        Args:
            app_context: Value for the ``x-sfdc-app-context`` header.
            client_feature_id: Value for the ``x-client-feature-id`` header.
            timeout: Default HTTP request timeout in seconds.
            http2: Negotiate HTTP/2 when the server supports it.

        Returns:
            A new :class:`ModelsClient` bound to the freshly minted token.

        Raises:
            SalesforcePyError: If ``SF_MODELS_CLIENT_ID``, ``SF_MODELS_CLIENT_SECRET``,
                or the instance URL env var are missing.
            AuthError: If the token request fails (wrong credentials or missing scopes).

        Example::

            import asyncio
            from salesforce_py.models import ModelsClient

            # Set SF_MODELS_CLIENT_ID, SF_MODELS_CLIENT_SECRET, SF_MODELS_INSTANCE_URL
            async def main():
                async with await ModelsClient.from_env() as client:
                    reply = await client.chat_generations.generate(model, messages)
        """
        creds = resolve_client_creds("MODELS")
        if not creds:
            raise SalesforcePyError(
                "SF_MODELS_CLIENT_ID and SF_MODELS_CLIENT_SECRET must both be set to use "
                "ModelsClient.from_env(). The Models API requires an External Client App "
                "with the 'sfap_api einstein_gpt_api api' scopes — SF CLI session tokens "
                "are not supported."
            )

        instance_url = resolve_instance_url("MODELS")
        if not instance_url:
            raise SalesforcePyError(
                "SF_MODELS_CLIENT_ID and SF_MODELS_CLIENT_SECRET are set but no instance "
                "URL was found. Set SF_MODELS_INSTANCE_URL or SF_INSTANCE_URL."
            )

        token = await fetch_token(
            my_domain=instance_url,
            consumer_key=creds[0],
            consumer_secret=creds[1],
            timeout=timeout,
        )
        base_url = (
            f"{token.api_instance_url}/einstein/platform/v1/"
            if token.api_instance_url
            else _DEFAULT_BASE_URL
        )
        return cls(
            token.access_token,
            base_url=base_url,
            app_context=app_context,
            client_feature_id=client_feature_id,
            timeout=timeout,
            http2=http2,
        )

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
