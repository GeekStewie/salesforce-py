"""DuckDB helpers for Bulk API 2.0 query results.

Bulk API 2.0 returns query results as CSV, paginated via the
``Sforce-Locator`` header. When the submitted SOQL originally had an
``ORDER BY`` clause, the client strips the clause before submission (to
keep PK chunking enabled), then concatenates the paginated CSV pages and
re-sorts the combined dataset locally via DuckDB.

DuckDB is imported lazily so the ``bulk`` extra can be installed without
it when callers only need ingest operations.
"""

from __future__ import annotations

import contextlib
import os
import tempfile

from salesforce_py.bulk._soql import OrderByClause

_DELIMITER_CHARS: dict[str, str] = {
    "BACKQUOTE": "`",
    "CARET": "^",
    "COMMA": ",",
    "PIPE": "|",
    "SEMICOLON": ";",
    "TAB": "\t",
}

_LINE_ENDING_CHARS: dict[str, str] = {
    "LF": "\n",
    "CRLF": "\r\n",
}


def _load_duckdb():
    """Import ``duckdb`` lazily, raising a helpful message if missing."""
    try:
        import duckdb  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "Sorting Bulk API 2.0 query results by ORDER BY requires the "
            "'duckdb' package. Install it with:\n"
            "  uv add 'salesforce-py[bulk]'\n"
            "  pip install 'salesforce-py[bulk]'"
        ) from exc
    return duckdb


def concatenate_csv_pages(
    pages: list[bytes],
    *,
    line_ending: str = "LF",
) -> bytes:
    """Join paginated Bulk query CSV pages into a single CSV payload.

    Each page returned by ``/jobs/query/{id}/results`` includes the CSV
    header row. The header is preserved from the first non-empty page
    and stripped from subsequent pages so the combined payload is valid
    CSV.

    Args:
        pages: Raw CSV byte payloads, in page order.
        line_ending: The ``lineEnding`` the job was created with — used
            to locate the header terminator. ``"LF"`` or ``"CRLF"``.

    Returns:
        The concatenated CSV bytes. Empty if all pages are empty.
    """
    sep = _LINE_ENDING_CHARS[line_ending].encode("utf-8")
    non_empty = [page for page in pages if page]
    if not non_empty:
        return b""
    if len(non_empty) == 1:
        return non_empty[0]

    first = non_empty[0]
    header_end = first.find(sep)
    if header_end == -1:
        return sep.join(non_empty)

    combined = bytearray(first)
    for page in non_empty[1:]:
        body_start = page.find(sep)
        if body_start == -1:
            continue
        body = page[body_start + len(sep) :]
        if not body:
            continue
        if not combined.endswith(sep):
            combined.extend(sep)
        combined.extend(body)
    return bytes(combined)


def apply_order_by(
    csv_data: bytes,
    order_by: OrderByClause,
    *,
    column_delimiter: str = "COMMA",
    line_ending: str = "LF",
) -> bytes:
    """Re-sort *csv_data* locally using *order_by* via DuckDB.

    Loads the CSV into DuckDB via a tempfile, applies ``ORDER BY``, and
    writes the sorted payload back out with the original delimiter and
    line ending.

    Args:
        csv_data: Raw CSV bytes — typically the output of
            :func:`concatenate_csv_pages`.
        order_by: The clause that was stripped from the submitted SOQL.
        column_delimiter: Matches the query job's ``columnDelimiter``.
        line_ending: Matches the query job's ``lineEnding``.

    Returns:
        Sorted CSV bytes. Returns *csv_data* unchanged when empty or
        when ``order_by.columns`` is empty.
    """
    if not csv_data or not order_by.columns:
        return csv_data

    duckdb = _load_duckdb()
    delimiter = _DELIMITER_CHARS[column_delimiter]
    newline = _LINE_ENDING_CHARS[line_ending]

    input_path = _write_tempfile(csv_data, suffix=".csv")
    output_path = _reserve_tempfile(suffix=".csv")

    try:
        con = duckdb.connect(":memory:")
        try:
            con.execute(
                "CREATE TEMP TABLE bulk_results AS "
                "SELECT * FROM read_csv_auto(?, header=True, delim=?, all_varchar=True)",
                [input_path, delimiter],
            )

            order_clauses: list[str] = []
            for expression, direction, nulls in order_by.columns:
                clause = f'"{expression}" {direction}'
                if nulls:
                    clause += f" NULLS {nulls}"
                order_clauses.append(clause)
            order_sql = ", ".join(order_clauses)

            # DuckDB's COPY TO requires literal options — parameterise the
            # path but embed the delimiter in the SQL. Delimiter is from a
            # validated whitelist (_DELIMITER_CHARS), so no injection risk.
            con.execute(
                f"COPY (SELECT * FROM bulk_results ORDER BY {order_sql}) "  # nosec B608
                f"TO ? (HEADER, DELIMITER '{delimiter}')",
                [output_path],
            )
        finally:
            con.close()

        with open(output_path, "rb") as handle:
            sorted_bytes = handle.read()
    finally:
        _cleanup(input_path)
        _cleanup(output_path)

    if newline != "\n":
        sorted_bytes = sorted_bytes.replace(b"\n", newline.encode("utf-8"))

    return sorted_bytes


# ---------------------------------------------------------------------------
# Tempfile helpers — DuckDB's CSV reader/writer prefers real file paths.
# ---------------------------------------------------------------------------


def _write_tempfile(data: bytes, *, suffix: str) -> str:
    fd, path = tempfile.mkstemp(suffix=suffix, prefix="salesforce_py_bulk_")
    try:
        with open(fd, "wb") as handle:
            handle.write(data)
    except Exception:
        _cleanup(path)
        raise
    return path


def _reserve_tempfile(*, suffix: str) -> str:
    fd, path = tempfile.mkstemp(suffix=suffix, prefix="salesforce_py_bulk_")
    os.close(fd)
    return path


def _cleanup(path: str) -> None:
    with contextlib.suppress(OSError):
        os.unlink(path)
