"""Unit tests for TransformationsOperations."""

from __future__ import annotations

import pytest

from salesforce_py.exceptions import AuthError

from ._helpers import _client, _mock_response


class TestTransformationsRun:
    async def test_posts_to_correct_path(self):
        c = await _client(_mock_response(200, {"jobId": "0sx"}))
        await c.manufacturing.transformations.run(
            input_object_ids=["0sTxxx"],
            input_object_name="MfgProgramCpntFrcstFact",
            usage_type="TransformationMapping",
            output_object_name="Opportunity",
        )
        assert c._session.post.call_args.args[0] == "manufacturing/transformations"

    async def test_required_fields_present_in_body(self):
        c = await _client(_mock_response(200, {"jobId": "0sx"}))
        await c.manufacturing.transformations.run(
            input_object_ids=["0sTxxx", "0sTyyy"],
            input_object_name="MfgProgramCpntFrcstFact",
            usage_type="TransformationMapping",
            output_object_name="Opportunity",
        )
        body = c._session.post.call_args.kwargs["json"]
        assert body == {
            "inputObjectIds": ["0sTxxx", "0sTyyy"],
            "inputObjectName": "MfgProgramCpntFrcstFact",
            "usageType": "TransformationMapping",
            "outputObjectName": "Opportunity",
        }

    async def test_default_values_included_when_provided(self):
        c = await _client(_mock_response(200, {"jobId": "0sx"}))
        defaults = {
            "Opportunity": {"StageName": "Prospecting", "Probability": "20"},
            "OpportunityLineItem": {"TotalPrice": 1234, "CurrencyIsoCode": "USD"},
        }
        await c.manufacturing.transformations.run(
            input_object_ids=["0sTxxx"],
            input_object_name="MfgProgramCpntFrcstFact",
            usage_type="TransformationMapping",
            output_object_name="Opportunity",
            output_object_default_values=defaults,
        )
        body = c._session.post.call_args.kwargs["json"]
        assert body["outputObjectDefaultValues"] == defaults

    async def test_default_values_omitted_when_none(self):
        c = await _client(_mock_response(200, {"jobId": "0sx"}))
        await c.manufacturing.transformations.run(
            input_object_ids=["0sTxxx"],
            input_object_name="MfgProgramCpntFrcstFact",
            usage_type="TransformationMapping",
            output_object_name="Opportunity",
        )
        assert "outputObjectDefaultValues" not in c._session.post.call_args.kwargs["json"]

    async def test_body_escape_hatch_overrides_named_kwargs(self):
        c = await _client(_mock_response(200, {"jobId": "0sx"}))
        literal = {"inputObjectIds": ["OVERRIDE"], "extra": "kept"}
        await c.manufacturing.transformations.run(
            input_object_ids=["ignored"],
            input_object_name="X",
            usage_type="Y",
            output_object_name="Z",
            body=literal,
        )
        assert c._session.post.call_args.kwargs["json"] == literal

    async def test_401_raises_auth_error(self):
        c = await _client(_mock_response(401))
        with pytest.raises(AuthError):
            await c.manufacturing.transformations.run(
                input_object_ids=["0sTxxx"],
                input_object_name="MfgProgramCpntFrcstFact",
                usage_type="TransformationMapping",
                output_object_name="Opportunity",
            )

    async def test_raises_when_required_args_missing_and_no_body(self):
        c = await _client(_mock_response(200, {"jobId": "0sx"}))
        with pytest.raises(ValueError, match="input_object_ids, input_object_name"):
            await c.manufacturing.transformations.run()
