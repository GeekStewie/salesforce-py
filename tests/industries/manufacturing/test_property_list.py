"""Unit tests for the property-list helper used by sample management."""

from __future__ import annotations

from salesforce_py.industries.manufacturing._properties import _to_property_list


class TestToPropertyList:
    def test_flat_dict_is_converted_to_field_value_pairs(self):
        result = _to_property_list({"Name": "Acme", "Status": "Draft"})
        assert result == [
            {"field": "Name", "value": "Acme"},
            {"field": "Status", "value": "Draft"},
        ]

    def test_empty_dict_yields_empty_list(self):
        assert _to_property_list({}) == []

    def test_non_string_values_are_preserved(self):
        result = _to_property_list({"Count": 42, "Active": True, "Ratio": 1.5})
        assert result == [
            {"field": "Count", "value": 42},
            {"field": "Active", "value": True},
            {"field": "Ratio", "value": 1.5},
        ]

    def test_iteration_order_matches_input(self):
        # dict preserves insertion order in Python 3.7+
        result = _to_property_list({"z": 1, "a": 2, "m": 3})
        assert [pair["field"] for pair in result] == ["z", "a", "m"]
