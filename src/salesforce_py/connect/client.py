"""User-facing entry point for the Connect API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from salesforce_py._auth import fetch_org_token, resolve_client_creds, resolve_instance_url
from salesforce_py._retry import DEFAULT_TIMEOUT
from salesforce_py.connect._session import _DEFAULT_API_VERSION, ConnectSession
from salesforce_py.exceptions import SalesforcePyError

if TYPE_CHECKING:
    from salesforce_py.sf.org import SFOrg
from salesforce_py.connect.operations.action_links import ActionLinksOperations
from salesforce_py.connect.operations.activity_reminders import (
    ActivityRemindersOperations,
)
from salesforce_py.connect.operations.agentforce_data_libraries import (
    AgentforceDataLibrariesOperations,
)
from salesforce_py.connect.operations.announcements import AnnouncementsOperations
from salesforce_py.connect.operations.bot_version_activation import (
    BotVersionActivationOperations,
)
from salesforce_py.connect.operations.chatter import ChatterOperations
from salesforce_py.connect.operations.clean import CleanOperations
from salesforce_py.connect.operations.cms import (
    CMSManagedContentOperations,
    CMSWorkspacesOperations,
)
from salesforce_py.connect.operations.cms_content_search import (
    CMSContentSearchOperations,
)
from salesforce_py.connect.operations.comments import CommentsOperations
from salesforce_py.connect.operations.commerce_addresses import (
    CommerceAddressesOperations,
)
from salesforce_py.connect.operations.commerce_cart import CommerceCartOperations
from salesforce_py.connect.operations.commerce_checkout import (
    CommerceCheckoutOperations,
)
from salesforce_py.connect.operations.commerce_context import (
    CommerceContextOperations,
)
from salesforce_py.connect.operations.commerce_einstein_webstore import (
    CommerceEinsteinWebstoreOperations,
)
from salesforce_py.connect.operations.commerce_my_profile import (
    CommerceMyProfileOperations,
)
from salesforce_py.connect.operations.commerce_order_summaries import (
    CommerceOrderSummariesOperations,
)
from salesforce_py.connect.operations.commerce_pricing import (
    CommercePricingOperations,
)
from salesforce_py.connect.operations.commerce_products import (
    CommerceProductsOperations,
)
from salesforce_py.connect.operations.commerce_taxes import (
    CommerceTaxesOperations,
)
from salesforce_py.connect.operations.commerce_wishlists import (
    CommerceWishlistsOperations,
)
from salesforce_py.connect.operations.communities import CommunitiesOperations
from salesforce_py.connect.operations.content_hub import (
    FilesConnectRepositoryOperations,
)
from salesforce_py.connect.operations.conversation_application import (
    ConversationApplicationOperations,
)
from salesforce_py.connect.operations.conversations import ConversationsOperations
from salesforce_py.connect.operations.core import ConnectCoreOperations
from salesforce_py.connect.operations.custom_domain import CustomDomainOperations
from salesforce_py.connect.operations.data_integration import (
    DataIntegrationOperations,
)
from salesforce_py.connect.operations.duplicate import DuplicateOperations
from salesforce_py.connect.operations.einstein_recommendations import (
    EinsteinRecommendationsOperations,
)
from salesforce_py.connect.operations.email_merge_fields import (
    EmailMergeFieldsOperations,
)
from salesforce_py.connect.operations.feeds import FeedsOperations
from salesforce_py.connect.operations.files import FilesOperations
from salesforce_py.connect.operations.flow_approval import FlowApprovalOperations
from salesforce_py.connect.operations.groups import GroupsOperations
from salesforce_py.connect.operations.knowledge import (
    KnowledgeArticleViewStatOperations,
)
from salesforce_py.connect.operations.managed_topics import ManagedTopicsOperations
from salesforce_py.industries.manufacturing import (
    SalesAgreementsOperations,
    SampleManagementOperations,
    TransformationsOperations,
    WarrantyOperations,
)
from salesforce_py.connect.operations.microsites import MicrositesOperations
from salesforce_py.connect.operations.motifs import MotifsOperations
from salesforce_py.connect.operations.named_credentials import (
    NamedCredentialsOperations,
)
from salesforce_py.connect.operations.navigation_menu import (
    NavigationMenuOperations,
)
from salesforce_py.connect.operations.network_data_category import (
    NetworkDataCategoryOperations,
)
from salesforce_py.connect.operations.next_best_action import (
    NextBestActionOperations,
)
from salesforce_py.connect.operations.notification_settings import (
    NotificationSettingsOperations,
)
from salesforce_py.connect.operations.notifications import NotificationsOperations
from salesforce_py.connect.operations.omnichannel_inventory import (
    OmnichannelInventoryOperations,
)
from salesforce_py.connect.operations.orchestration import OrchestrationOperations
from salesforce_py.connect.operations.order_management import (
    OrderManagementOperations,
)
from salesforce_py.connect.operations.payments import PaymentsOperations
from salesforce_py.connect.operations.personalization_audiences import (
    PersonalizationAudiencesOperations,
)
from salesforce_py.connect.operations.personalization_engagement_signals import (
    PersonalizationEngagementSignalsOperations,
)
from salesforce_py.connect.operations.personalization_experiments import (
    PersonalizationExperimentsOperations,
)
from salesforce_py.connect.operations.personalization_recommenders import (
    PersonalizationRecommendersOperations,
)
from salesforce_py.connect.operations.prompt_templates import (
    PromptTemplatesOperations,
)
from salesforce_py.connect.operations.push_notifications import (
    PushNotificationsOperations,
)
from salesforce_py.connect.operations.quick_text import QuickTextOperations
from salesforce_py.connect.operations.quip import QuipOperations
from salesforce_py.connect.operations.search import SearchOperations
from salesforce_py.connect.operations.sites_knowledge import (
    SitesKnowledgeOperations,
)
from salesforce_py.connect.operations.sites_moderation import (
    SitesModerationOperations,
)
from salesforce_py.connect.operations.topics import (
    LikesOperations,
    MentionsOperations,
    SubscriptionsOperations,
    TopicsOperations,
)
from salesforce_py.connect.operations.topics_on_records import (
    TopicsOnRecordsOperations,
)
from salesforce_py.connect.operations.users import (
    UserProfilesOperations,
    UsersOperations,
)


class _ManufacturingNamespace:
    """Container exposing manufacturing-cloud Connect API operations.

    Grouped semantically; ``warranty.supplier_claim`` hits
    ``/connect/warranty/``, not ``/connect/manufacturing/``, despite living
    under this accessor.
    """

    def __init__(self, session: ConnectSession) -> None:
        self.sales_agreements = SalesAgreementsOperations(session)
        self.sample_management = SampleManagementOperations(session)
        self.transformations = TransformationsOperations(session)
        self.warranty = WarrantyOperations(session)


class ConnectClient:
    """Async client for the Salesforce Connect REST API.

    Binds to one org's credentials and exposes grouped operation namespaces
    mirroring the ``/services/data/vXX.X/connect/`` URL hierarchy.

    Intended to be used as an async context manager::

        async with ConnectClient(instance_url, access_token) as client:
            feed = await client.chatter.get_feed_items()

    Can also be used without a context manager — call :meth:`open` and
    :meth:`close` manually in that case.

    Args:
        instance_url: Org instance URL, e.g. ``"https://myorg.my.salesforce.com"``.
        access_token: OAuth bearer token for the org.
        api_version: Salesforce API version string. Defaults to
            :data:`salesforce_py.DEFAULT_API_VERSION`.
        timeout: Default HTTP request timeout in seconds.
        http2: Negotiate HTTP/2 when the server supports it (falls back to HTTP/1.1).
            Defaults to ``True`` — some Salesforce edges are HTTP/2-enabled and
            benefit from multiplexing; others transparently fall back.
    """

    def __init__(
        self,
        instance_url: str,
        access_token: str,
        api_version: str = _DEFAULT_API_VERSION,
        timeout: float = DEFAULT_TIMEOUT,
        http2: bool = True,
    ) -> None:
        self._session = ConnectSession(
            instance_url=instance_url,
            access_token=access_token,
            api_version=api_version,
            timeout=timeout,
            http2=http2,
        )
        self._einstein_session = ConnectSession(
            instance_url=instance_url,
            access_token=access_token,
            api_version=api_version,
            timeout=timeout,
            base_path="einstein",
            http2=http2,
        )
        self._data_session = ConnectSession(
            instance_url=instance_url,
            access_token=access_token,
            api_version=api_version,
            timeout=timeout,
            base_path="",
            http2=http2,
        )
        # Chatter-root endpoints (``/chatter/...``) are served at
        # ``/services/data/vXX.X/chatter/...`` — NOT under ``/connect/chatter/...``.
        # Operation classes that emit org-scope Chatter paths therefore receive
        # the data-session too, and ``ConnectBaseOperations._route`` dispatches
        # paths starting with ``chatter/`` to the data session while keeping
        # everything else (``communities/X/...``, etc.) on the connect session.
        ds = self._data_session
        self.core = ConnectCoreOperations(self._session)
        self.action_links = ActionLinksOperations(self._session)
        self.activity_reminders = ActivityRemindersOperations(self._session)
        self.agentforce_data_libraries = AgentforceDataLibrariesOperations(self._einstein_session)
        self.announcements = AnnouncementsOperations(self._session, ds)
        self.bot_version_activation = BotVersionActivationOperations(self._session)
        self.chatter = ChatterOperations(self._session, ds)
        self.clean = CleanOperations(self._data_session)
        self.cms_content = CMSManagedContentOperations(self._session)
        self.cms_content_search = CMSContentSearchOperations(self._session)
        self.cms_workspaces = CMSWorkspacesOperations(self._session)
        self.comments = CommentsOperations(self._session, ds)
        self.commerce_addresses = CommerceAddressesOperations(self._data_session)
        self.commerce_cart = CommerceCartOperations(self._data_session)
        self.commerce_checkout = CommerceCheckoutOperations(self._data_session)
        self.commerce_context = CommerceContextOperations(self._data_session)
        self.commerce_einstein_webstore = CommerceEinsteinWebstoreOperations(self._data_session)
        self.commerce_my_profile = CommerceMyProfileOperations(self._data_session)
        self.commerce_order_summaries = CommerceOrderSummariesOperations(self._data_session)
        self.commerce_pricing = CommercePricingOperations(self._data_session)
        self.commerce_products = CommerceProductsOperations(self._data_session)
        self.commerce_taxes = CommerceTaxesOperations(self._data_session)
        self.commerce_wishlists = CommerceWishlistsOperations(self._data_session)
        self.communities = CommunitiesOperations(self._session)
        self.content_hub = FilesConnectRepositoryOperations(self._session)
        self.conversation_application = ConversationApplicationOperations(self._session)
        self.conversations = ConversationsOperations(self._session)
        self.custom_domain = CustomDomainOperations(self._session)
        self.data_integration = DataIntegrationOperations(self._data_session)
        self.duplicate = DuplicateOperations(self._data_session)
        self.einstein_recommendations = EinsteinRecommendationsOperations(self._session)
        self.email_merge_fields = EmailMergeFieldsOperations(self._data_session)
        self.feeds = FeedsOperations(self._session, ds)
        self.files = FilesOperations(self._session, ds)
        self.flow_approval = FlowApprovalOperations(self._session)
        self.groups = GroupsOperations(self._session, ds)
        self.knowledge_article_view_stat = KnowledgeArticleViewStatOperations(self._session)
        self.likes = LikesOperations(self._session, ds)
        self.managed_topics = ManagedTopicsOperations(self._session)
        self.mentions = MentionsOperations(self._session, ds)
        self.microsites = MicrositesOperations(self._data_session)
        self.motifs = MotifsOperations(self._session)
        self.named_credentials = NamedCredentialsOperations(self._data_session)
        self.navigation_menu = NavigationMenuOperations(self._session)
        self.network_data_category = NetworkDataCategoryOperations(self._session)
        self.next_best_action = NextBestActionOperations(self._session)
        self.notification_settings = NotificationSettingsOperations(self._session)
        self.notifications = NotificationsOperations(self._session)
        self.omnichannel_inventory = OmnichannelInventoryOperations(self._data_session)
        self.orchestration = OrchestrationOperations(self._session)
        self.order_management = OrderManagementOperations(self._data_session)
        self.payments = PaymentsOperations(self._data_session)
        self.personalization_audiences = PersonalizationAudiencesOperations(self._session)
        self.personalization_engagement_signals = PersonalizationEngagementSignalsOperations(
            self._data_session
        )
        self.personalization_experiments = PersonalizationExperimentsOperations(self._data_session)
        self.personalization_recommenders = PersonalizationRecommendersOperations(
            self._data_session
        )
        self.prompt_templates = PromptTemplatesOperations(self._einstein_session)
        self.push_notifications = PushNotificationsOperations(self._session)
        self.quick_text = QuickTextOperations(self._session)
        self.quip = QuipOperations(self._session)
        self.search = SearchOperations(self._session)
        self.sites_knowledge = SitesKnowledgeOperations(self._session)
        self.sites_moderation = SitesModerationOperations(self._session, ds)
        self.subscriptions = SubscriptionsOperations(self._session, ds)
        self.topics = TopicsOperations(self._session, ds)
        self.topics_on_records = TopicsOnRecordsOperations(self._session)
        self.user_profiles = UserProfilesOperations(self._session)
        self.users = UsersOperations(self._session, ds)
        self.manufacturing = _ManufacturingNamespace(self._session)

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
    ) -> ConnectClient:
        """Create a :class:`ConnectClient` from a connected :class:`~salesforce_py.sf.org.SFOrg`.

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
            A new :class:`ConnectClient` bound to the org's credentials.

        Example::

            from salesforce_py.sf import SFOrgTask
            from salesforce_py.connect import ConnectClient

            task = SFOrgTask("my-org-alias")
            async with ConnectClient.from_org(task._org) as client:
                feed = await client.chatter.get_feed_items()
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
    ) -> ConnectClient:
        """Create a :class:`ConnectClient` from environment variables or an SF CLI org.

        Resolution order:

        1. **Client credentials** — if ``SF_CONNECT_CLIENT_ID`` and
           ``SF_CONNECT_CLIENT_SECRET`` are both set, a ``client_credentials``
           OAuth token is minted. The My Domain URL is read from
           ``SF_CONNECT_INSTANCE_URL``, falling back to ``SF_INSTANCE_URL``.
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
            A new :class:`ConnectClient` ready for use.

        Raises:
            SalesforcePyError: If credentials cannot be resolved.
            AuthError: If the OAuth token request fails.

        Example::

            import asyncio
            from salesforce_py.connect import ConnectClient

            # With SF_CONNECT_CLIENT_ID / SF_CONNECT_CLIENT_SECRET / SF_CONNECT_INSTANCE_URL:
            async def main():
                async with await ConnectClient.from_env() as client:
                    feed = await client.chatter.get_feed_items()

            # Or fall back to SF CLI:
            async def main():
                async with await ConnectClient.from_env("my-org-alias") as client:
                    feed = await client.chatter.get_feed_items()
        """
        creds = resolve_client_creds("CONNECT")
        if creds:
            instance_url = resolve_instance_url("CONNECT")
            if not instance_url:
                raise SalesforcePyError(
                    "SF_CONNECT_CLIENT_ID and SF_CONNECT_CLIENT_SECRET are set but no "
                    "instance URL was found. Set SF_CONNECT_INSTANCE_URL or SF_INSTANCE_URL."
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
            "Cannot resolve ConnectClient credentials. Either set "
            "SF_CONNECT_CLIENT_ID + SF_CONNECT_CLIENT_SECRET + SF_CONNECT_INSTANCE_URL, "
            "or pass a target_org alias to from_env()."
        )

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> ConnectClient:
        await self.open()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def open(self) -> None:
        """Open the underlying HTTP sessions."""
        await self._session.open()
        await self._einstein_session.open()
        await self._data_session.open()

    async def close(self) -> None:
        """Close the underlying HTTP sessions."""
        await self._session.close()
        await self._einstein_session.close()
        await self._data_session.close()

    def __repr__(self) -> str:
        return f"ConnectClient(instance_url={self._session._instance_url!r})"
