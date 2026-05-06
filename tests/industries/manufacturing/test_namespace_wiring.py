"""Smoke tests for the c.manufacturing.* namespace on ConnectClient."""

from __future__ import annotations

from salesforce_py.connect.client import ConnectClient
from salesforce_py.industries.manufacturing import (
    SalesAgreementsOperations,
    SampleManagementOperations,
    TransformationsOperations,
    WarrantyOperations,
)

INSTANCE_URL = "https://test.my.salesforce.com"
ACCESS_TOKEN = "test_token_abc"


class TestManufacturingNamespace:
    def test_namespace_exposes_all_four_operation_classes(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        assert isinstance(c.manufacturing.sales_agreements, SalesAgreementsOperations)
        assert isinstance(c.manufacturing.sample_management, SampleManagementOperations)
        assert isinstance(c.manufacturing.transformations, TransformationsOperations)
        assert isinstance(c.manufacturing.warranty, WarrantyOperations)

    def test_all_operation_classes_share_the_connect_session(self):
        c = ConnectClient(INSTANCE_URL, ACCESS_TOKEN)
        assert c.manufacturing.sales_agreements._session is c._session
        assert c.manufacturing.sample_management._session is c._session
        assert c.manufacturing.transformations._session is c._session
        assert c.manufacturing.warranty._session is c._session
