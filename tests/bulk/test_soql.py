"""Tests for salesforce_py.bulk._soql — SOQL prep and validation."""

from __future__ import annotations

import pytest

from salesforce_py.bulk._soql import prepare_query, validate_soql


class TestValidateSoql:
    @pytest.mark.parametrize(
        "bad_query, keyword",
        [
            ("SELECT Id FROM Account GROUP BY Name", "GROUP BY"),
            ("SELECT Id FROM Account LIMIT 10 OFFSET 5", "OFFSET"),
            ("SELECT TYPEOF Owner WHEN User THEN Id END FROM Task", "TYPEOF"),
            ("SELECT COUNT(Id) FROM Account", "COUNT"),
            ("SELECT SUM(Amount) FROM Opportunity", "SUM"),
        ],
    )
    def test_rejects_unsupported_construct(self, bad_query, keyword):
        with pytest.raises(ValueError, match=keyword):
            validate_soql(bad_query)

    def test_accepts_plain_soql(self):
        validate_soql("SELECT Id, Name FROM Account WHERE IsDeleted = false")


class TestPrepareQuery:
    def test_query_without_order_by_is_unchanged(self):
        prepared = prepare_query("SELECT Id FROM Account")
        assert prepared.soql == "SELECT Id FROM Account"
        assert prepared.order_by is None

    def test_strips_basic_order_by(self):
        prepared = prepare_query("SELECT Id FROM Account ORDER BY CreatedDate")
        assert prepared.soql == "SELECT Id FROM Account"
        assert prepared.order_by is not None
        assert prepared.order_by.columns == (("CreatedDate", "ASC", None),)

    def test_preserves_limit_after_order_by(self):
        prepared = prepare_query("SELECT Id FROM Account ORDER BY Name DESC LIMIT 100")
        assert prepared.soql == "SELECT Id FROM Account LIMIT 100"
        assert prepared.order_by.columns == (("Name", "DESC", None),)

    def test_parses_multi_column_order_by(self):
        prepared = prepare_query(
            "SELECT Id FROM Contact ORDER BY LastName ASC, CreatedDate DESC NULLS LAST"
        )
        assert prepared.soql == "SELECT Id FROM Contact"
        assert prepared.order_by.columns == (
            ("LastName", "ASC", None),
            ("CreatedDate", "DESC", "LAST"),
        )

    def test_parses_nulls_first(self):
        prepared = prepare_query("SELECT Id FROM Lead ORDER BY Score ASC NULLS FIRST")
        assert prepared.order_by.columns == (("Score", "ASC", "FIRST"),)

    def test_handles_function_with_commas_in_order_key(self):
        prepared = prepare_query(
            "SELECT Id FROM Account "
            "ORDER BY DISTANCE(Location__c, GEOLOCATION(37.7, -122.4), 'mi')"
        )
        assert prepared.soql == "SELECT Id FROM Account"
        # Single sort key even though the function has inner commas.
        assert len(prepared.order_by.columns) == 1
        expression, direction, nulls = prepared.order_by.columns[0]
        assert "DISTANCE" in expression
        assert direction == "ASC"
        assert nulls is None

    def test_rejects_unsupported_construct_before_stripping(self):
        with pytest.raises(ValueError, match="GROUP BY"):
            prepare_query("SELECT Id FROM Account GROUP BY Name ORDER BY Name")
