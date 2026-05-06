"""Helper for the property-list shape used by Manufacturing sample management."""

from __future__ import annotations

from typing import Any


def _to_property_list(fields: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert ``{key: value}`` to ``[{"field": k, "value": v}, ...]``.

    Salesforce's sample-management endpoint encodes flat objects as a list of
    field/value pairs at every nesting level. This helper performs that single
    transform; recursion is the caller's responsibility.

    Args:
        fields: Flat mapping of API field names to values.

    Returns:
        List of ``{"field": k, "value": v}`` dicts in the input's iteration order.
    """
    return [{"field": k, "value": v} for k, v in fields.items()]
