"""SF CLI operation wrappers."""

from salesforce_py.sf.operations.agent import SFAgentOperations
from salesforce_py.sf.operations.alias import SFAliasOperations
from salesforce_py.sf.operations.apex import SFApexOperations
from salesforce_py.sf.operations.api import SFApiOperations
from salesforce_py.sf.operations.cmdt import SFCmdtOperations
from salesforce_py.sf.operations.code_analyzer import SFCodeAnalyzerOperations
from salesforce_py.sf.operations.code_analyzer_manager import SFCodeAnalyzerManager
from salesforce_py.sf.operations.community import SFCommunityOperations
from salesforce_py.sf.operations.config import SFConfigOperations
from salesforce_py.sf.operations.data import SFDataOperations
from salesforce_py.sf.operations.dev import SFDevOperations
from salesforce_py.sf.operations.doctor import SFDoctorOperations
from salesforce_py.sf.operations.flow import SFFlowOperations
from salesforce_py.sf.operations.lightning import SFLightningOperations
from salesforce_py.sf.operations.logic import SFLogicOperations
from salesforce_py.sf.operations.org import SFOrgOperations
from salesforce_py.sf.operations.package import SFPackageOperations
from salesforce_py.sf.operations.plugins import SFPluginsOperations
from salesforce_py.sf.operations.plugins_manager import SFPluginsManagerOperations
from salesforce_py.sf.operations.project import SFProjectOperations
from salesforce_py.sf.operations.schema import SFSchemaOperations
from salesforce_py.sf.operations.sobject import SFSobjectOperations
from salesforce_py.sf.operations.template import SFTemplateOperations
from salesforce_py.sf.operations.ui_bundle import SFUiBundleOperations

__all__ = [
    "SFAgentOperations",
    "SFAliasOperations",
    "SFApexOperations",
    "SFCmdtOperations",
    "SFCodeAnalyzerOperations",
    "SFCodeAnalyzerManager",
    "SFCommunityOperations",
    "SFConfigOperations",
    "SFApiOperations",
    "SFDataOperations",
    "SFDevOperations",
    "SFDoctorOperations",
    "SFFlowOperations",
    "SFLightningOperations",
    "SFLogicOperations",
    "SFOrgOperations",
    "SFPackageOperations",
    "SFPluginsOperations",
    "SFPluginsManagerOperations",
    "SFProjectOperations",
    "SFSchemaOperations",
    "SFSobjectOperations",
    "SFTemplateOperations",
    "SFUiBundleOperations",
]
