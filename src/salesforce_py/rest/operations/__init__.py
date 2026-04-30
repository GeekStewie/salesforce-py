"""REST API operation classes."""

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

__all__ = [
    "ActionsOperations",
    "AnalyticsOperations",
    "AppMenuOperations",
    "AssetManagementOperations",
    "ChatterOperations",
    "CommerceOperations",
    "CompositeOperations",
    "ConnectOperations",
    "ConsentOperations",
    "ConsumerGoodsOperations",
    "ContactTracingOperations",
    "DedupeOperations",
    "EclairOperations",
    "FinancialServicesOperations",
    "FoldersOperations",
    "HealthCloudOperations",
    "JobsOperations",
    "JsonxformOperations",
    "KnowledgeManagementOperations",
    "LicensingOperations",
    "LightningUsageOperations",
    "LimitsOperations",
    "LocalizedValueOperations",
    "ManufacturingOperations",
    "MetadataOperations",
    "PaymentsOperations",
    "ProcessOperations",
    "QueryOperations",
    "QuickActionsOperations",
    "RecentOperations",
    "SchedulingOperations",
    "SearchOperations",
    "SObjectsOperations",
    "SmartDataDiscoveryOperations",
    "StreamingChannelPushOperations",
    "SupportOperations",
    "TabsOperations",
    "ThemeOperations",
    "ToolingOperations",
    "UIAPIOperations",
    "VersionsOperations",
    "WaveOperations",
]
