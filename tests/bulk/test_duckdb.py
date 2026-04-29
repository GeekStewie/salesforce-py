"""Tests for salesforce_py.bulk._duckdb — CSV concat + ORDER BY replay."""

from __future__ import annotations

from salesforce_py.bulk._duckdb import apply_order_by, concatenate_csv_pages
from salesforce_py.bulk._soql import OrderByClause


class TestConcatenateCsvPages:
    def test_empty_pages_returns_empty(self):
        assert concatenate_csv_pages([]) == b""
        assert concatenate_csv_pages([b"", b""]) == b""

    def test_single_page_passthrough(self):
        page = b"Id,Name\n001,Acme\n"
        assert concatenate_csv_pages([page]) == page

    def test_two_pages_strip_header_from_second(self):
        first = b"Id,Name\n001,Acme\n"
        second = b"Id,Name\n002,Beta\n"
        combined = concatenate_csv_pages([first, second])
        assert combined == b"Id,Name\n001,Acme\n002,Beta\n"

    def test_crlf_line_ending(self):
        first = b"Id,Name\r\n001,Acme\r\n"
        second = b"Id,Name\r\n002,Beta\r\n"
        combined = concatenate_csv_pages([first, second], line_ending="CRLF")
        assert combined == b"Id,Name\r\n001,Acme\r\n002,Beta\r\n"

    def test_page_with_only_header_is_ignored(self):
        first = b"Id,Name\n001,Acme\n"
        header_only = b"Id,Name\n"
        combined = concatenate_csv_pages([first, header_only])
        assert combined == b"Id,Name\n001,Acme\n"


class TestApplyOrderBy:
    def test_returns_empty_when_csv_is_empty(self):
        clause = OrderByClause(raw="Name", columns=(("Name", "ASC", None),))
        assert apply_order_by(b"", clause) == b""

    def test_returns_unchanged_when_no_sort_columns(self):
        clause = OrderByClause(raw="", columns=())
        data = b"Id,Name\n001,Acme\n"
        assert apply_order_by(data, clause) == data

    def test_ascending_sort(self):
        clause = OrderByClause(raw="Name", columns=(("Name", "ASC", None),))
        csv_in = b"Id,Name\n001,Charlie\n002,Alice\n003,Bob\n"
        result = apply_order_by(csv_in, clause)
        rows = result.strip().split(b"\n")
        assert rows[0] == b"Id,Name"
        assert rows[1].split(b",")[1] == b"Alice"
        assert rows[2].split(b",")[1] == b"Bob"
        assert rows[3].split(b",")[1] == b"Charlie"

    def test_descending_sort(self):
        clause = OrderByClause(raw="Name DESC", columns=(("Name", "DESC", None),))
        csv_in = b"Id,Name\n001,Alice\n002,Charlie\n003,Bob\n"
        result = apply_order_by(csv_in, clause)
        rows = result.strip().split(b"\n")
        assert rows[1].split(b",")[1] == b"Charlie"
        assert rows[3].split(b",")[1] == b"Alice"

    def test_multi_column_sort(self):
        clause = OrderByClause(
            raw="Grade ASC, Name ASC",
            columns=(("Grade", "ASC", None), ("Name", "ASC", None)),
        )
        csv_in = b"Id,Grade,Name\n1,B,Zed\n2,A,Carol\n3,A,Alice\n"
        result = apply_order_by(csv_in, clause)
        rows = result.strip().split(b"\n")
        assert rows[1] == b"3,A,Alice"
        assert rows[2] == b"2,A,Carol"
        assert rows[3] == b"1,B,Zed"

    def test_crlf_output(self):
        clause = OrderByClause(raw="Name", columns=(("Name", "ASC", None),))
        csv_in = b"Id,Name\r\n001,Bob\r\n002,Alice\r\n"
        result = apply_order_by(csv_in, clause, line_ending="CRLF")
        # Output should use CRLF line endings.
        assert b"\r\n" in result
        # Alice should now come before Bob.
        alice_idx = result.find(b"Alice")
        bob_idx = result.find(b"Bob")
        assert 0 < alice_idx < bob_idx
