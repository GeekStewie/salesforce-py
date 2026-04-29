"""Connect API operation classes."""

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

__all__ = [
    "ActionLinksOperations",
    "ActivityRemindersOperations",
    "AgentforceDataLibrariesOperations",
    "AnnouncementsOperations",
    "BotVersionActivationOperations",
    "CMSContentSearchOperations",
    "CMSManagedContentOperations",
    "CMSWorkspacesOperations",
    "ChatterOperations",
    "CleanOperations",
    "CommentsOperations",
    "CommerceAddressesOperations",
    "CommerceCartOperations",
    "CommerceCheckoutOperations",
    "CommerceContextOperations",
    "CommerceEinsteinWebstoreOperations",
    "CommerceMyProfileOperations",
    "CommerceOrderSummariesOperations",
    "CommercePricingOperations",
    "CommerceProductsOperations",
    "CommerceTaxesOperations",
    "CommerceWishlistsOperations",
    "CommunitiesOperations",
    "ConnectCoreOperations",
    "ConversationApplicationOperations",
    "ConversationsOperations",
    "CustomDomainOperations",
    "DataIntegrationOperations",
    "DuplicateOperations",
    "EinsteinRecommendationsOperations",
    "EmailMergeFieldsOperations",
    "FeedsOperations",
    "FilesConnectRepositoryOperations",
    "FilesOperations",
    "FlowApprovalOperations",
    "GroupsOperations",
    "KnowledgeArticleViewStatOperations",
    "LikesOperations",
    "ManagedTopicsOperations",
    "MentionsOperations",
    "MicrositesOperations",
    "MotifsOperations",
    "NamedCredentialsOperations",
    "NavigationMenuOperations",
    "NetworkDataCategoryOperations",
    "NextBestActionOperations",
    "NotificationSettingsOperations",
    "NotificationsOperations",
    "OmnichannelInventoryOperations",
    "OrchestrationOperations",
    "OrderManagementOperations",
    "PaymentsOperations",
    "PersonalizationAudiencesOperations",
    "PersonalizationEngagementSignalsOperations",
    "PersonalizationExperimentsOperations",
    "PersonalizationRecommendersOperations",
    "PromptTemplatesOperations",
    "PushNotificationsOperations",
    "QuickTextOperations",
    "QuipOperations",
    "SearchOperations",
    "SitesKnowledgeOperations",
    "SitesModerationOperations",
    "SubscriptionsOperations",
    "TopicsOnRecordsOperations",
    "TopicsOperations",
    "UserProfilesOperations",
    "UsersOperations",
]
