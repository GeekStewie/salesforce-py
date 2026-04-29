"""User-facing entry point for the Bulk API 2.0 client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from salesforce_py._auth import fetch_org_token, resolve_client_creds, resolve_instance_url
from salesforce_py._defaults import DEFAULT_API_VERSION as _DEFAULT_API_VERSION
from salesforce_py._retry import DEFAULT_TIMEOUT
from salesforce_py.bulk._session import BulkSession
from salesforce_py.bulk.operations.ingest import IngestOperations
from salesforce_py.bulk.operations.query import QueryOperations
from salesforce_py.exceptions import SalesforcePyError

if TYPE_CHECKING:
    from salesforce_py.sf.org import SFOrg


class BulkClient:
    """Async client for the Salesforce Bulk API 2.0.

    Binds to one org's credentials and exposes grouped operation
    namespaces mirroring the ``/services/data/vXX.X/jobs/`` URL hierarchy:

    - :attr:`ingest` — CSV upload jobs (insert/update/upsert/delete/hardDelete).
    - :attr:`query` — SOQL query jobs, with automatic ``ORDER BY``
      stripping + DuckDB-powered client-side re-sort.

    Intended to be used as an async context manager::

        async with BulkClient(instance_url, access_token) as client:
            job = await client.ingest.create_job(
                object_name="Account", operation="insert"
            )

    Can also be used without a context manager — call :meth:`open` and
    :meth:`close` manually in that case.

    Args:
        instance_url: Org instance URL, e.g. ``"https://myorg.my.salesforce.com"``.
        access_token: OAuth bearer token for the org.
        api_version: Salesforce API version string. Defaults to
            :data:`salesforce_py.DEFAULT_API_VERSION`.
        timeout: Default HTTP request timeout in seconds.
        http2: Negotiate HTTP/2 when the server supports it (falls back to
            HTTP/1.1). Defaults to ``True``.
    """

    def __init__(
        self,
        instance_url: str,
        access_token: str,
        api_version: str = _DEFAULT_API_VERSION,
        timeout: float = DEFAULT_TIMEOUT,
        http2: bool = True,
    ) -> None:
        self._session = BulkSession(
            instance_url=instance_url,
            access_token=access_token,
            api_version=api_version,
            timeout=timeout,
            http2=http2,
        )
        self.ingest = IngestOperations(self._session)
        self.query = QueryOperations(self._session)

    # ------------------------------------------------------------------
    # Alternate constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_org(
        cls,
        org: SFOrg,
        api_version: str = _DEFAULT_API_VERSION,
        timeout: float = DEFAULT_TIMEOUT,
        http2: bool = True,
    ) -> BulkClient:
        """Create a :class:`BulkClient` from a connected :class:`~salesforce_py.sf.org.SFOrg`.

        Calls :meth:`~salesforce_py.sf.org.SFOrg._ensure_connected` to
        trigger lazy auth resolution, then forwards ``instance_url`` and
        ``access_token`` directly.

        Args:
            org: An :class:`~salesforce_py.sf.org.SFOrg` instance.
            api_version: Salesforce API version string.
            timeout: Default HTTP request timeout in seconds.
            http2: Negotiate HTTP/2 when the server supports it.

        Returns:
            A new :class:`BulkClient` bound to the org's credentials.
        """
        org._ensure_connected()
        return cls(
            instance_url=org.instance_url,
            access_token=org.access_token,
            api_version=api_version,
            timeout=timeout,
            http2=http2,
        )

    @classmethod
    async def from_env(
        cls,
        target_org: str | None = None,
        api_version: str = _DEFAULT_API_VERSION,
        timeout: float = DEFAULT_TIMEOUT,
        http2: bool = True,
    ) -> BulkClient:
        """Create a :class:`BulkClient` from environment variables or an SF CLI org.

        Resolution order:

        1. **Client credentials** — if ``SF_BULK_CLIENT_ID`` and
           ``SF_BULK_CLIENT_SECRET`` are both set, a ``client_credentials``
           OAuth token is minted. The My Domain URL is read from
           ``SF_BULK_INSTANCE_URL``, falling back to ``SF_INSTANCE_URL``.
        2. **SF CLI session** — if ``target_org`` is provided (and env creds
           are absent), credentials are read from the SF CLI auth store.
        3. Raises :class:`~salesforce_py.exceptions.SalesforcePyError` if
           neither path succeeds.

        Args:
            target_org: SF CLI alias or username. Used when env creds are absent.
            api_version: Salesforce API version string.
            timeout: Default HTTP request timeout in seconds.
            http2: Negotiate HTTP/2 when the server supports it.

        Returns:
            A new :class:`BulkClient` ready for use.

        Raises:
            SalesforcePyError: If credentials cannot be resolved.
            AuthError: If the OAuth token request fails.
        """
        creds = resolve_client_creds("BULK")
        if creds:
            instance_url = resolve_instance_url("BULK")
            if not instance_url:
                raise SalesforcePyError(
                    "SF_BULK_CLIENT_ID and SF_BULK_CLIENT_SECRET are set but no "
                    "instance URL was found. Set SF_BULK_INSTANCE_URL or SF_INSTANCE_URL."
                )
            access_token, resolved_url = await fetch_org_token(
                instance_url, creds[0], creds[1], timeout=timeout
            )
            return cls(
                instance_url=resolved_url,
                access_token=access_token,
                api_version=api_version,
                timeout=timeout,
                http2=http2,
            )

        if target_org is not None:
            from salesforce_py.sf.org import SFOrg

            org = SFOrg(target_org=target_org)
            return cls.from_org(org, api_version=api_version, timeout=timeout, http2=http2)

        raise SalesforcePyError(
            "Cannot resolve BulkClient credentials. Either set "
            "SF_BULK_CLIENT_ID + SF_BULK_CLIENT_SECRET + SF_BULK_INSTANCE_URL, "
            "or pass a target_org alias to from_env()."
        )

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> BulkClient:
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
        return f"BulkClient(instance_url={self._session._instance_url!r})"
