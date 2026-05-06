"""Unit tests for SampleManagementOperations."""

from __future__ import annotations

import pytest

from salesforce_py.exceptions import AuthError

from ._helpers import _client, _mock_response


class TestSampleManagementCreate:
    async def test_posts_to_correct_path(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "x"}))
        await c.manufacturing.sample_management.create(
            operation="Insert",
            spec={"Name": "X"},
        )
        assert (
            c._session.post.call_args.args[0]
            == "manufacturing/sample-management/product-specifications"
        )

    async def test_spec_is_converted_to_property_list(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "x"}))
        await c.manufacturing.sample_management.create(
            operation="Insert",
            spec={"Name": "Project Everest", "AccountId": "001xx", "Status": "Draft"},
        )
        body = c._session.post.call_args.kwargs["json"]
        assert body["operation"] == "Insert"
        assert body["productRequirementSpecification"]["properties"] == [
            {"field": "Name", "value": "Project Everest"},
            {"field": "AccountId", "value": "001xx"},
            {"field": "Status", "value": "Draft"},
        ]

    async def test_versions_and_items_are_recursively_converted(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "x"}))
        await c.manufacturing.sample_management.create(
            operation="Insert",
            spec={"Name": "Spec"},
            versions=[
                {
                    "fields": {"Name": "v1", "Version": "2"},
                    "items": [
                        {"fields": {"Name": "i1", "Statement": "S"}},
                        {"fields": {"Name": "i2", "Statement": "T"}},
                    ],
                }
            ],
        )
        body = c._session.post.call_args.kwargs["json"]
        prs = body["productRequirementSpecification"]
        assert len(prs["productRequirementSpecificationVersions"]) == 1
        v0 = prs["productRequirementSpecificationVersions"][0]
        assert v0["properties"] == [
            {"field": "Name", "value": "v1"},
            {"field": "Version", "value": "2"},
        ]
        assert len(v0["productRequirementSpecificationItems"]) == 2
        assert v0["productRequirementSpecificationItems"][0]["properties"] == [
            {"field": "Name", "value": "i1"},
            {"field": "Statement", "value": "S"},
        ]

    async def test_request_unique_id_included_when_provided(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "abc"}))
        await c.manufacturing.sample_management.create(
            operation="Insert",
            spec={"Name": "X"},
            request_unique_id="abc",
        )
        body = c._session.post.call_args.kwargs["json"]
        assert body["requestUniqueId"] == "abc"

    async def test_request_unique_id_omitted_when_none(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "x"}))
        await c.manufacturing.sample_management.create(
            operation="Insert", spec={"Name": "X"}
        )
        body = c._session.post.call_args.kwargs["json"]
        assert "requestUniqueId" not in body

    async def test_versions_omitted_when_none(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "x"}))
        await c.manufacturing.sample_management.create(
            operation="Insert", spec={"Name": "X"}
        )
        body = c._session.post.call_args.kwargs["json"]
        assert (
            "productRequirementSpecificationVersions"
            not in body["productRequirementSpecification"]
        )

    async def test_items_omitted_when_version_has_no_items_key(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "x"}))
        await c.manufacturing.sample_management.create(
            operation="Update",
            spec={"Name": "X"},
            versions=[{"fields": {"Name": "v1"}}],
        )
        body = c._session.post.call_args.kwargs["json"]
        v0 = body["productRequirementSpecification"][
            "productRequirementSpecificationVersions"
        ][0]
        assert "productRequirementSpecificationItems" not in v0

    async def test_body_escape_hatch_overrides_named_kwargs(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "x"}))
        literal = {"operation": "OVERRIDE", "extra": "kept"}
        await c.manufacturing.sample_management.create(
            operation="Insert", spec={"Name": "X"}, body=literal
        )
        assert c._session.post.call_args.kwargs["json"] == literal

    async def test_401_raises_auth_error(self):
        c = await _client(_mock_response(401))
        with pytest.raises(AuthError):
            await c.manufacturing.sample_management.create(
                operation="Insert", spec={"Name": "X"}
            )

    async def test_raises_when_required_args_missing_and_no_body(self):
        c = await _client(_mock_response(200, {"requestUniqueId": "x"}))
        with pytest.raises(ValueError, match="operation and spec are required"):
            await c.manufacturing.sample_management.create()
