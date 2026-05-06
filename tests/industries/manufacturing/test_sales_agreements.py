"""Unit tests for SalesAgreementsOperations."""

from __future__ import annotations

import pytest

from salesforce_py.exceptions import AuthError, SalesforcePyError

from ._helpers import _client, _mock_response


class TestSalesAgreementsCreate:
    async def test_posts_to_correct_path(self):
        c = await _client(_mock_response(200, {"id": "0SAxxxx"}))
        await c.manufacturing.sales_agreements.create(source_object_id="0kFTxxx")
        path = c._session.post.call_args.args[0]
        assert path == "manufacturing/sales-agreements"

    async def test_minimal_body_contains_source_object_id_only(self):
        c = await _client(_mock_response(200, {"id": "0SAxxxx"}))
        await c.manufacturing.sales_agreements.create(source_object_id="0kFTxxx")
        body = c._session.post.call_args.kwargs["json"]
        assert body == {"sourceObjectId": "0kFTxxx"}

    async def test_default_values_included_when_provided(self):
        c = await _client(_mock_response(200, {"id": "0SAxxxx"}))
        defaults = {
            "salesAgreement": {"StartDate": "2026-01-01", "ScheduleFrequency": "Monthly"},
            "salesAgreementProduct": {"Name": "test", "InitialPlannedQuantity": "1"},
        }
        await c.manufacturing.sales_agreements.create(
            source_object_id="0kFTxxx",
            sales_agreement_default_values=defaults,
        )
        body = c._session.post.call_args.kwargs["json"]
        assert body == {
            "sourceObjectId": "0kFTxxx",
            "salesAgreementDefaultValues": defaults,
        }

    async def test_body_escape_hatch_overrides_named_kwargs(self):
        c = await _client(_mock_response(200, {"id": "0SAxxxx"}))
        literal = {"sourceObjectId": "OVERRIDE", "extra": "kept"}
        await c.manufacturing.sales_agreements.create(
            source_object_id="ignored", body=literal
        )
        assert c._session.post.call_args.kwargs["json"] == literal

    async def test_returns_parsed_json(self):
        c = await _client(_mock_response(200, {"id": "0SAxxxx", "ok": True}))
        result = await c.manufacturing.sales_agreements.create(source_object_id="0kFTxxx")
        assert result == {"id": "0SAxxxx", "ok": True}

    async def test_401_raises_auth_error(self):
        c = await _client(_mock_response(401))
        with pytest.raises(AuthError):
            await c.manufacturing.sales_agreements.create(source_object_id="0kFTxxx")

    async def test_400_raises_salesforce_py_error(self):
        c = await _client(_mock_response(400, {"errorCode": "INVALID"}))
        with pytest.raises(SalesforcePyError):
            await c.manufacturing.sales_agreements.create(source_object_id="0kFTxxx")

    async def test_raises_when_no_source_id_and_no_body(self):
        c = await _client(_mock_response(200, {"id": "x"}))
        with pytest.raises(ValueError, match="source_object_id is required"):
            await c.manufacturing.sales_agreements.create()
