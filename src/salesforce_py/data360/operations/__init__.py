"""Data 360 Connect REST API operation classes."""

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

__all__ = [
    "ActivationTargetsOperations",
    "ActivationsOperations",
    "CalculatedInsightsOperations",
    "ConnectionsOperations",
    "ConnectorsOperations",
    "DataActionTargetsOperations",
    "DataActionsOperations",
    "DataCleanRoomOperations",
    "DataGraphsOperations",
    "DataKitsOperations",
    "DataLakeObjectsOperations",
    "DataModelObjectsOperations",
    "DataSpacesOperations",
    "DataStreamsOperations",
    "DataTransformsOperations",
    "DocumentAIOperations",
    "IdentityResolutionsOperations",
    "InsightsOperations",
    "MachineLearningOperations",
    "MetadataOperations",
    "PrivateNetworkRoutesOperations",
    "ProfileOperations",
    "QueryOperations",
    "SearchIndexOperations",
    "SegmentsOperations",
    "UniversalIdLookupOperations",
]
