"""SOQL helpers for the Bulk API 2.0 client.

Bulk API 2.0 disables PK chunking when a query contains ``ORDER BY`` or
``LIMIT``, which hurts throughput and can trip query timeouts on large
result sets. The client strips ``ORDER BY`` before submission, captures
the clause, and reapplies it locally via DuckDB once the results are
downloaded.

Several other SOQL constructs are outright unsupported by Bulk API 2.0
and are rejected client-side with a clear message rather than producing
an opaque ``InvalidJob`` server-side error.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = ["OrderByClause", "PreparedQuery", "prepare_query", "validate_soql"]


# ---------------------------------------------------------------------------
# Unsupported clauses — see "SOQL Considerations" in the Bulk API 2.0 guide
# ---------------------------------------------------------------------------

_UNSUPPORTED_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bGROUP\s+BY\b", re.IGNORECASE), "GROUP BY"),
    (re.compile(r"\bOFFSET\b", re.IGNORECASE), "OFFSET"),
    (re.compile(r"\bTYPEOF\b", re.IGNORECASE), "TYPEOF"),
    (re.compile(r"\bCOUNT\s*\(", re.IGNORECASE), "COUNT() aggregate"),
    (re.compile(r"\bSUM\s*\(", re.IGNORECASE), "SUM() aggregate"),
    (re.compile(r"\bAVG\s*\(", re.IGNORECASE), "AVG() aggregate"),
    (re.compile(r"\bMIN\s*\(", re.IGNORECASE), "MIN() aggregate"),
    (re.compile(r"\bMAX\s*\(", re.IGNORECASE), "MAX() aggregate"),
)


# ORDER BY ... [LIMIT n] [OFFSET n] — captured lazily so we can peel it off
# the tail of the statement and put the bits after it back in place.
_ORDER_BY_RE = re.compile(
    r"""
    \bORDER\s+BY\b          # ORDER BY keyword
    (?P<clause>.*?)         # the ordering expression (non-greedy)
    (?=                     # stop at:
        \bLIMIT\b           #   LIMIT
      | \bOFFSET\b          #   OFFSET
      | \bFOR\s+(?:VIEW|REFERENCE|UPDATE)\b
      | \bUPDATE\s+TRACKING\b
      | \bUPDATE\s+VIEWSTAT\b
      | \Z                  #   or end of string
    )
    """,
    re.IGNORECASE | re.VERBOSE | re.DOTALL,
)


@dataclass(frozen=True)
class OrderByClause:
    """A captured ``ORDER BY`` clause, parsed into (expression, direction, nulls)
    triples so DuckDB can reapply the sort client-side.

    ``raw`` preserves the original text for debugging; ``columns`` is the
    list of sort keys. Each key is a tuple of ``(expression, direction,
    nulls)``. ``direction`` is ``"ASC"`` or ``"DESC"``. ``nulls`` is
    ``"FIRST"``, ``"LAST"``, or ``None`` (server default).
    """

    raw: str
    columns: tuple[tuple[str, str, str | None], ...]


@dataclass(frozen=True)
class PreparedQuery:
    """Output of :func:`prepare_query`.

    Attributes:
        soql: The query to actually send to Bulk API 2.0 — ``ORDER BY``
            stripped when present.
        order_by: The captured ``ORDER BY`` clause, or ``None`` if the
            original query had none.
    """

    soql: str
    order_by: OrderByClause | None


def _parse_order_by(clause_body: str) -> tuple[tuple[str, str, str | None], ...]:
    """Split a raw ``ORDER BY`` body into ``(expr, direction, nulls)`` tuples.

    Top-level commas separate keys; commas inside parentheses (e.g.
    ``DISTANCE(Location__c, GEOLOCATION(...), 'mi')``) don't split keys.
    """
    keys: list[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(clause_body):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            keys.append(clause_body[start:i].strip())
            start = i + 1
    tail = clause_body[start:].strip()
    if tail:
        keys.append(tail)

    parsed: list[tuple[str, str, str | None]] = []
    for key in keys:
        tokens = key.split()
        direction = "ASC"
        nulls: str | None = None

        # Walk the tail looking for NULLS FIRST/LAST and ASC/DESC.
        while tokens and tokens[-1].upper() in {"FIRST", "LAST"}:
            if len(tokens) >= 2 and tokens[-2].upper() == "NULLS":
                nulls = tokens[-1].upper()
                tokens = tokens[:-2]
            else:
                break
        if tokens and tokens[-1].upper() in {"ASC", "DESC"}:
            direction = tokens[-1].upper()
            tokens = tokens[:-1]

        expression = " ".join(tokens).strip()
        if expression:
            parsed.append((expression, direction, nulls))

    return tuple(parsed)


def validate_soql(soql: str) -> None:
    """Raise ``ValueError`` when *soql* uses a construct Bulk API 2.0 rejects.

    Bulk API 2.0 does not support ``GROUP BY``, ``OFFSET``, ``TYPEOF``, or
    aggregate functions. It also does not support parent-to-child
    relationship subqueries, but detecting those reliably would require a
    full parser — we surface the server error instead.
    """
    for pattern, name in _UNSUPPORTED_PATTERNS:
        if pattern.search(soql):
            raise ValueError(
                f"Bulk API 2.0 does not support SOQL with {name}. "
                f"Rewrite the query or use the REST /query endpoint instead."
            )


def prepare_query(soql: str) -> PreparedQuery:
    """Strip any ``ORDER BY`` clause from *soql* and capture it for local re-sort.

    Bulk API 2.0 disables PK chunking when a SOQL query contains
    ``ORDER BY`` — which can push large queries into timeouts. This
    helper removes the clause before submission and returns it separately
    so the caller can sort the CSV results client-side via DuckDB.

    Also runs :func:`validate_soql` to surface unsupported constructs
    with a clear error.
    """
    validate_soql(soql)

    # Match ``ORDER BY ...`` up to the next LIMIT/OFFSET/FOR/UPDATE-TRACKING
    # clause (if any). Whatever follows the ORDER BY survives so ``LIMIT``
    # is preserved in the submitted query.
    match = _ORDER_BY_RE.search(soql)
    if match is None:
        return PreparedQuery(soql=soql.strip(), order_by=None)

    raw_clause_body = match.group("clause").strip().rstrip(",")
    stripped = (soql[: match.start()] + soql[match.end() :]).strip()
    # Collapse the double-space left where the clause used to be.
    stripped = re.sub(r"\s+", " ", stripped)

    return PreparedQuery(
        soql=stripped,
        order_by=OrderByClause(
            raw=raw_clause_body,
            columns=_parse_order_by(raw_clause_body),
        ),
    )
