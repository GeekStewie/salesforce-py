"""Tests for salesforce_py.bulk._limits — constants + validators."""

from __future__ import annotations

import pytest

from salesforce_py.bulk._limits import (
    MAX_UPLOAD_BYTES_BASE64,
    MAX_UPLOAD_BYTES_RAW,
    validate_column_delimiter,
    validate_line_ending,
    validate_operation,
    validate_query_operation,
    validate_upload_size,
)


class TestConstants:
    def test_base64_ceiling_is_150mb(self):
        assert MAX_UPLOAD_BYTES_BASE64 == 150 * 1024 * 1024

    def test_raw_ceiling_is_100mb(self):
        assert MAX_UPLOAD_BYTES_RAW == 100 * 1024 * 1024


class TestValidators:
    @pytest.mark.parametrize(
        "op", ["insert", "update", "upsert", "delete", "hardDelete"]
    )
    def test_valid_ingest_ops(self, op):
        assert validate_operation(op) == op

    def test_invalid_ingest_op_raises(self):
        with pytest.raises(ValueError, match="Invalid ingest operation"):
            validate_operation("query")

    def test_valid_query_ops(self):
        assert validate_query_operation("query") == "query"
        assert validate_query_operation("queryAll") == "queryAll"

    def test_invalid_query_op_raises(self):
        with pytest.raises(ValueError, match="Invalid query operation"):
            validate_query_operation("insert")

    @pytest.mark.parametrize(
        "delim", ["BACKQUOTE", "CARET", "COMMA", "PIPE", "SEMICOLON", "TAB"]
    )
    def test_valid_column_delimiter(self, delim):
        assert validate_column_delimiter(delim) == delim

    def test_invalid_column_delimiter_raises(self):
        with pytest.raises(ValueError, match="Invalid columnDelimiter"):
            validate_column_delimiter("COLON")

    def test_valid_line_endings(self):
        assert validate_line_ending("LF") == "LF"
        assert validate_line_ending("CRLF") == "CRLF"

    def test_invalid_line_ending_raises(self):
        with pytest.raises(ValueError, match="Invalid lineEnding"):
            validate_line_ending("CR")


class TestValidateUploadSize:
    def test_small_payload_passes(self):
        validate_upload_size(b"a,b\n1,2\n")

    def test_payload_at_limit_passes(self):
        validate_upload_size(b"x" * MAX_UPLOAD_BYTES_RAW)

    def test_payload_above_limit_raises(self):
        with pytest.raises(ValueError, match="raw ceiling"):
            validate_upload_size(b"x" * (MAX_UPLOAD_BYTES_RAW + 1))
