"""User-facing entry point for the Data 360 Connect REST API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from salesforce_py._auth import fetch_org_token, resolve_client_creds, resolve_instance_url
from salesforce_py._retry import DEFAULT_TIMEOUT
from salesforce_py.data360._session import _DEFAULT_API_VERSION, Data360Session
from salesforce_py.exceptions import SalesforcePyError

if TYPE_CHECKING:
    from salesforce_py.sf.org import SFOrg
from salesforce_py.data360.operations.activation_targets import (
    ActivationTargetsOperations,
)
from salesforce_py.data360.operations.activations import ActivationsOperations
from salesforce_py.data360.operations.calculated_insights import (
    CalculatedInsightsOperations,
)
from salesforce_py.data360.operations.connections import ConnectionsOperations
from salesforce_py.data360.operations.connectors import ConnectorsOperations
from salesforce_py.data360.operations.data_action_targets import (
    DataActionTargetsOperations,
)
from salesforce_py.data360.operations.data_actions import DataActionsOperations
from salesforce_py.data360.operations.data_clean_room import DataCleanRoomOperations
from salesforce_py.data360.operations.data_graphs import DataGraphsOperations
from salesforce_py.data360.operations.data_kits import DataKitsOperations
from salesforce_py.data360.operations.data_lake_objects import (
    DataLakeObjectsOperations,
)
from salesforce_py.data360.operations.data_model_objects import (
    DataModelObjectsOperations,
)
from salesforce_py.data360.operations.data_spaces import DataSpacesOperations
from salesforce_py.data360.operations.data_streams import DataStreamsOperations
from salesforce_py.data360.operations.data_transforms import DataTransformsOperations
from salesforce_py.data360.operations.document_ai import DocumentAIOperations
from salesforce_py.data360.operations.identity_resolutions import (
    IdentityResolutionsOperations,
)
from salesforce_py.data360.operations.insights import InsightsOperations
from salesforce_py.data360.operations.machine_learning import (
    MachineLearningOperations,
)
from salesforce_py.data360.operations.metadata import MetadataOperations
from salesforce_py.data360.operations.private_network_routes import (
    PrivateNetworkRoutesOperations,
)
from salesforce_py.data360.operations.profile import ProfileOperations
from salesforce_py.data360.operations.query import QueryOperations
from salesforce_py.data360.operations.search_index import SearchIndexOperations
from salesforce_py.data360.operations.segments import SegmentsOperations
from salesforce_py.data360.operations.universal_id_lookup import (
    UniversalIdLookupOperations,
)


class Data360Client:
    """Async client for the Salesforce Data 360 Connect REST API.

    Binds to one Data 360 tenant's credentials and exposes grouped operation
    namespaces mirroring the ``/services/data/vXX.X/ssot/`` URL hierarchy.

    Intended to be used as an async context manager::

        async with Data360Client(instance_url, access_token) as client:
            segments = await client.segments.get_segments()

    Can also be used without a context manager — call :meth:`open` and
    :meth:`close` manually in that case.

    Args:
        instance_url: Data 360 instance URL, e.g.
            ``"https://datacloud-abc.my.salesforce.com"``.
        access_token: OAuth bearer token for the tenant.
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
        self._session = Data360Session(
            instance_url=instance_url,
            access_token=access_token,
            api_version=api_version,
            timeout=timeout,
            http2=http2,
        )
        self.activation_targets = ActivationTargetsOperations(self._session)
        self.activations = ActivationsOperations(self._session)
        self.calculated_insights = CalculatedInsightsOperations(self._session)
        self.connections = ConnectionsOperations(self._session)
        self.connectors = ConnectorsOperations(self._session)
        self.data_action_targets = DataActionTargetsOperations(self._session)
        self.data_actions = DataActionsOperations(self._session)
        self.data_clean_room = DataCleanRoomOperations(self._session)
        self.data_graphs = DataGraphsOperations(self._session)
        self.data_kits = DataKitsOperations(self._session)
        self.data_lake_objects = DataLakeObjectsOperations(self._session)
        self.data_model_objects = DataModelObjectsOperations(self._session)
        self.data_spaces = DataSpacesOperations(self._session)
        self.data_streams = DataStreamsOperations(self._session)
        self.data_transforms = DataTransformsOperations(self._session)
        self.document_ai = DocumentAIOperations(self._session)
        self.identity_resolutions = IdentityResolutionsOperations(self._session)
        self.insights = InsightsOperations(self._session)
        self.machine_learning = MachineLearningOperations(self._session)
        self.metadata = MetadataOperations(self._session)
        self.private_network_routes = PrivateNetworkRoutesOperations(self._session)
        self.profile = ProfileOperations(self._session)
        self.query = QueryOperations(self._session)
        self.search_index = SearchIndexOperations(self._session)
        self.segments = SegmentsOperations(self._session)
        self.universal_id_lookup = UniversalIdLookupOperations(self._session)

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
    ) -> Data360Client:
        """Create a :class:`Data360Client` from an already-connected :class:`~salesforce_py.sf.org.SFOrg`.

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
            A new :class:`Data360Client` bound to the org's credentials.

        Example::

            from salesforce_py.sf import SFOrgTask
            from salesforce_py.data360 import Data360Client

            task = SFOrgTask("my-org-alias")
            async with Data360Client.from_org(task._org) as client:
                segments = await client.segments.get_segments()
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
    ) -> Data360Client:
        """Create a :class:`Data360Client` from environment variables or an SF CLI org.

        Resolution order:

        1. **Client credentials** — if ``SF_DATA360_CLIENT_ID`` and
           ``SF_DATA360_CLIENT_SECRET`` are both set, a ``client_credentials``
           OAuth token is minted. The My Domain URL is read from
           ``SF_DATA360_INSTANCE_URL``, falling back to ``SF_INSTANCE_URL``.
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
            A new :class:`Data360Client` ready for use.

        Raises:
            SalesforcePyError: If credentials cannot be resolved.
            AuthError: If the OAuth token request fails.

        Example::

            import asyncio
            from salesforce_py.data360 import Data360Client

            # With env vars SF_DATA360_CLIENT_ID / SF_DATA360_CLIENT_SECRET / SF_DATA360_INSTANCE_URL:
            async def main():
                async with await Data360Client.from_env() as client:
                    segments = await client.segments.get_segments()

            # Or fall back to SF CLI:
            async def main():
                async with await Data360Client.from_env("my-org-alias") as client:
                    segments = await client.segments.get_segments()
        """
        creds = resolve_client_creds("DATA360")
        if creds:
            instance_url = resolve_instance_url("DATA360")
            if not instance_url:
                raise SalesforcePyError(
                    "SF_DATA360_CLIENT_ID and SF_DATA360_CLIENT_SECRET are set but no "
                    "instance URL was found. Set SF_DATA360_INSTANCE_URL or SF_INSTANCE_URL."
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
            "Cannot resolve Data360Client credentials. Either set "
            "SF_DATA360_CLIENT_ID + SF_DATA360_CLIENT_SECRET + SF_DATA360_INSTANCE_URL, "
            "or pass a target_org alias to from_env()."
        )

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> Data360Client:
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
        return f"Data360Client(instance_url={self._session._instance_url!r})"
