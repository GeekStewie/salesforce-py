"""Orchestrator that composes all SF CLI operation classes behind a single entry point."""

from salesforce_py.sf.operations.agent import SFAgentOperations
from salesforce_py.sf.operations.alias import SFAliasOperations
from salesforce_py.sf.operations.apex import SFApexOperations
from salesforce_py.sf.operations.cmdt import SFCmdtOperations
from salesforce_py.sf.operations.code_analyzer import SFCodeAnalyzerOperations
from salesforce_py.sf.operations.community import SFCommunityOperations
from salesforce_py.sf.operations.config import SFConfigOperations
from salesforce_py.sf.operations.api import SFApiOperations
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
from salesforce_py.sf.org import SFOrg


class SFOrgTask:
    """High-level entry point for SF CLI operations.

    Instantiate once per org and access grouped operations as attributes.
    The underlying :class:`SFOrg` connects lazily on first use.

    Example::

        task = SFOrgTask("my-scratch-org")
        records = task.data.query("SELECT Id, Name FROM Account LIMIT 10")
        task.project.deploy(source_dir=Path("force-app"))

    Args:
        target_org: SF CLI alias or username. None resolves the default alias.
        lazy_connect: Defer org credential resolution until first operation.
    """

    def __init__(
        self,
        target_org: str | None = None,
        lazy_connect: bool = True,
    ) -> None:
        """Initialise the orchestrator and all operation sub-classes.

        Args:
            target_org: SF CLI alias or username. None resolves the default alias.
            lazy_connect: Defer org credential resolution until first operation.
        """
        self._org = SFOrg(target_org=target_org, lazy_connect=lazy_connect)

        self.agent = SFAgentOperations(self._org)
        self.alias = SFAliasOperations(self._org)
        self.apex = SFApexOperations(self._org)
        self.cmdt = SFCmdtOperations(self._org)
        self.code_analyzer = SFCodeAnalyzerOperations(self._org)
        self.community = SFCommunityOperations(self._org)
        self.config = SFConfigOperations(self._org)
        self.api = SFApiOperations(self._org)
        self.data = SFDataOperations(self._org)
        self.dev = SFDevOperations(self._org)
        self.doctor = SFDoctorOperations(self._org)
        self.flow = SFFlowOperations(self._org)
        self.lightning = SFLightningOperations(self._org)
        self.logic = SFLogicOperations(self._org)
        self.org = SFOrgOperations(self._org)
        self.package = SFPackageOperations(self._org)
        self.plugins = SFPluginsOperations(self._org)
        self.plugins_manager = SFPluginsManagerOperations(self._org)
        self.project = SFProjectOperations(self._org)
        self.schema = SFSchemaOperations(self._org)
        self.sobject = SFSobjectOperations(self._org)
        self.template = SFTemplateOperations(self._org)
        self.ui_bundle = SFUiBundleOperations(self._org)

    def connect(self) -> bool:
        """Explicitly connect to the org (normally done lazily).

        Returns:
            True if connection succeeded.
        """
        return self._org.connect()

    def is_connected(self) -> bool:
        """Return True if org credentials have been loaded."""
        return self._org.is_connected()

    def __repr__(self) -> str:
        """Return debug representation."""
        return f"SFOrgTask(target_org={self._org.target_org!r})"
