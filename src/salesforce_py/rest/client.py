"""User-facing entry point for the Salesforce REST API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from salesforce_py._auth import fetch_org_token, resolve_client_creds, resolve_instance_url
from salesforce_py._defaults import DEFAULT_API_VERSION as _DEFAULT_API_VERSION
from salesforce_py._retry import DEFAULT_TIMEOUT
from salesforce_py.exceptions import SalesforcePyError
from salesforce_py.rest._session import RestSession
from salesforce_py.rest.operations.actions import ActionsOperations
from salesforce_py.rest.operations.analytics import (
    AnalyticsOperations,
    EclairOperations,
    FoldersOperations,
    JsonxformOperations,
    SmartDataDiscoveryOperations,
    WaveOperations,
)
from salesforce_py.rest.operations.app_menu import AppMenuOperations
from salesforce_py.rest.operations.composite import CompositeOperations
from salesforce_py.rest.operations.consumer_goods import ConsumerGoodsOperations
from salesforce_py.rest.operations.lightning_usage import LightningUsageOperations
from salesforce_py.rest.operations.limits import LimitsOperations
from salesforce_py.rest.operations.metadata import MetadataOperations
from salesforce_py.rest.operations.misc import (
    AssetManagementOperations,
    ChatterOperations,
    CommerceOperations,
    ConnectOperations,
    ConsentOperations,
    ContactTracingOperations,
    DedupeOperations,
    FinancialServicesOperations,
    HealthCloudOperations,
    JobsOperations,
    KnowledgeManagementOperations,
    LicensingOperations,
    LocalizedValueOperations,
    ManufacturingOperations,
    PaymentsOperations,
    SchedulingOperations,
)
from salesforce_py.rest.operations.process import ProcessOperations
from salesforce_py.rest.operations.query import QueryOperations
from salesforce_py.rest.operations.quick_actions import QuickActionsOperations
from salesforce_py.rest.operations.search import SearchOperations
from salesforce_py.rest.operations.sobjects import SObjectsOperations
from salesforce_py.rest.operations.streaming import StreamingChannelPushOperations
from salesforce_py.rest.operations.support import SupportOperations
from salesforce_py.rest.operations.tabs_theme_recent import (
    RecentOperations,
    TabsOperations,
    ThemeOperations,
)
from salesforce_py.rest.operations.tooling import ToolingOperations
from salesforce_py.rest.operations.ui_api import UIAPIOperations
from salesforce_py.rest.operations.versions import VersionsOperations

if TYPE_CHECKING:
    from salesforce_py.sf.org import SFOrg


class RestClient:
    """Async client for the Salesforce REST API.

    Binds to one org's credentials and exposes grouped operation namespaces
    mirroring the ``/services/data/vXX.X/`` URL hierarchy — SOQL / SOSL
    queries, every ``/sobjects/...`` resource, the composite / batch / graph
    / tree families, quick actions, invocable actions, tooling, UI API,
    analytics, process, support, and the rest.

    Intended to be used as an async context manager::

        async with RestClient(instance_url, access_token) as client:
            account = await client.sobjects.create(
                "Account", {"Name": "Acme Corp"}
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
        self._session = RestSession(
            instance_url=instance_url,
            access_token=access_token,
            api_version=api_version,
            timeout=timeout,
            http2=http2,
        )

        # Core data surfaces
        self.versions = VersionsOperations(self._session)
        self.limits = LimitsOperations(self._session)
        self.query = QueryOperations(self._session)
        self.search = SearchOperations(self._session)
        self.sobjects = SObjectsOperations(self._session)
        self.composite = CompositeOperations(self._session)
        self.quick_actions = QuickActionsOperations(self._session)
        self.actions = ActionsOperations(self._session)

        # UI / navigation / metrics
        self.tabs = TabsOperations(self._session)
        self.theme = ThemeOperations(self._session)
        self.recent = RecentOperations(self._session)
        self.app_menu = AppMenuOperations(self._session)
        self.lightning_usage = LightningUsageOperations(self._session)

        # Process and support
        self.process = ProcessOperations(self._session)
        self.support = SupportOperations(self._session)

        # Tooling, UI API, Metadata
        self.tooling = ToolingOperations(self._session)
        self.ui_api = UIAPIOperations(self._session)
        self.metadata = MetadataOperations(self._session)

        # Analytics family
        self.analytics = AnalyticsOperations(self._session)
        self.wave = WaveOperations(self._session)
        self.folders = FoldersOperations(self._session)
        self.smart_data_discovery = SmartDataDiscoveryOperations(self._session)
        self.eclair = EclairOperations(self._session)
        self.jsonxform = JsonxformOperations(self._session)

        # Streaming and platform
        self.streaming = StreamingChannelPushOperations(self._session)

        # Industry clouds served under /connect/<vertical>
        self.financial_services = FinancialServicesOperations(self._session)
        self.health_cloud = HealthCloudOperations(self._session)
        self.manufacturing = ManufacturingOperations(self._session)
        self.consumer_goods = ConsumerGoodsOperations(self._session)

        # Small-surface passthroughs (see operations/misc.py)
        self.asset_management = AssetManagementOperations(self._session)
        self.chatter = ChatterOperations(self._session)
        self.commerce = CommerceOperations(self._session)
        self.connect = ConnectOperations(self._session)
        self.consent = ConsentOperations(self._session)
        self.contact_tracing = ContactTracingOperations(self._session)
        self.dedupe = DedupeOperations(self._session)
        self.jobs = JobsOperations(self._session)
        self.knowledge_management = KnowledgeManagementOperations(self._session)
        self.licensing = LicensingOperations(self._session)
        self.localized_value = LocalizedValueOperations(self._session)
        self.payments = PaymentsOperations(self._session)
        self.scheduling = SchedulingOperations(self._session)

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
    ) -> RestClient:
        """Create a :class:`RestClient` from a connected :class:`~salesforce_py.sf.org.SFOrg`.

        Calls :meth:`~salesforce_py.sf.org.SFOrg._ensure_connected` to
        trigger lazy auth resolution, then forwards ``instance_url`` and
        ``access_token`` directly.

        Args:
            org: An :class:`~salesforce_py.sf.org.SFOrg` instance (from
                :class:`~salesforce_py.sf.SFOrgTask` or standalone).
            api_version: Salesforce API version string.
            timeout: Default HTTP request timeout in seconds.
            http2: Negotiate HTTP/2 when the server supports it.

        Returns:
            A new :class:`RestClient` bound to the org's credentials.

        Example::

            from salesforce_py.sf import SFOrgTask
            from salesforce_py.rest import RestClient

            task = SFOrgTask("my-org-alias")
            async with RestClient.from_org(task._org) as client:
                me = await client.sobjects.get("User", "005xx000001SvD8AAK")
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
    ) -> RestClient:
        """Create a :class:`RestClient` from environment variables or an SF CLI org.

        Resolution order:

        1. **Client credentials** — if ``SF_REST_CLIENT_ID`` and
           ``SF_REST_CLIENT_SECRET`` are both set, a ``client_credentials``
           OAuth token is minted. The My Domain URL is read from
           ``SF_REST_INSTANCE_URL``, falling back to ``SF_INSTANCE_URL``.
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
            A new :class:`RestClient` ready for use.

        Raises:
            SalesforcePyError: If credentials cannot be resolved.
            AuthError: If the OAuth token request fails.

        Example::

            import asyncio
            from salesforce_py.rest import RestClient

            # With SF_REST_CLIENT_ID / SF_REST_CLIENT_SECRET / SF_REST_INSTANCE_URL:
            async def main():
                async with await RestClient.from_env() as client:
                    limits = await client.limits.get_limits()

            # Or fall back to the SF CLI:
            async def main():
                async with await RestClient.from_env("my-org-alias") as client:
                    result = await client.query.query("SELECT Id FROM Account LIMIT 1")
        """
        creds = resolve_client_creds("REST")
        if creds:
            instance_url = resolve_instance_url("REST")
            if not instance_url:
                raise SalesforcePyError(
                    "SF_REST_CLIENT_ID and SF_REST_CLIENT_SECRET are set but no "
                    "instance URL was found. Set SF_REST_INSTANCE_URL or SF_INSTANCE_URL."
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
            "Cannot resolve RestClient credentials. Either set "
            "SF_REST_CLIENT_ID + SF_REST_CLIENT_SECRET + SF_REST_INSTANCE_URL, "
            "or pass a target_org alias to from_env()."
        )

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> RestClient:
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
        return f"RestClient(instance_url={self._session._instance_url!r})"
