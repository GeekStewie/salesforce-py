"""Manufacturing Cloud Business API operations.

Four resources are supported: sales agreements, sample management,
transformations, and warranty-to-supplier-claims. Wired into
:class:`salesforce_py.connect.ConnectClient` as ``client.manufacturing.*``.
"""

from salesforce_py.industries.manufacturing.sales_agreements import (
    SalesAgreementsOperations,
)
from salesforce_py.industries.manufacturing.sample_management import (
    SampleManagementOperations,
)
from salesforce_py.industries.manufacturing.transformations import (
    TransformationsOperations,
)
from salesforce_py.industries.manufacturing.warranty import WarrantyOperations

__all__ = [
    "SalesAgreementsOperations",
    "SampleManagementOperations",
    "TransformationsOperations",
    "WarrantyOperations",
]
