"""Salesforce ID utility functions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
_DATA_FILE = Path(__file__).parent / "data" / "object_prefixes.json"
_PREFIX_MAP: dict[str, dict[str, str]] | None = None


def _load_prefix_map() -> dict[str, dict[str, str]]:
    global _PREFIX_MAP
    if _PREFIX_MAP is None:
        _PREFIX_MAP = json.loads(_DATA_FILE.read_text(encoding="utf-8"))
    return _PREFIX_MAP


def convert_to_18_char(sf_id: str) -> str:
    """Convert a 15-character Salesforce ID to its 18-character equivalent.

    Args:
        sf_id: A 15- or 18-character Salesforce ID.

    Returns:
        The 18-character form of the ID.

    Raises:
        ValueError: If ``sf_id`` is not 15 or 18 characters long.
    """
    if len(sf_id) == 18:
        return sf_id
    if len(sf_id) != 15:
        raise ValueError("Salesforce ID must be 15 or 18 characters long.")

    def _checksum_char(segment: str) -> str:
        position = sum(2**i for i, c in enumerate(segment) if c.isupper())
        return _CHARS[position]

    suffix = "".join(_checksum_char(sf_id[i : i + 5]) for i in range(0, 15, 5))
    return sf_id + suffix


def get_object_type(sf_id: str) -> dict[str, Any]:
    """Look up the Salesforce object type for a given ID.

    Extracts the 3-character key prefix from the ID and returns the matching
    object metadata from the bundled prefix reference data.

    Args:
        sf_id: A 15- or 18-character Salesforce ID.

    Returns:
        Dict with ``label`` and ``name`` keys identifying the object type.

    Raises:
        ValueError: If ``sf_id`` is not 15 or 18 characters long, or if the
            prefix is not recognised.
    """
    if len(sf_id) not in (15, 18):
        raise ValueError("Salesforce ID must be 15 or 18 characters long.")

    prefix = sf_id[:3]
    prefix_map = _load_prefix_map()

    if prefix in prefix_map:
        return prefix_map[prefix]

    # Knowledge Article prefixes use a wildcard pattern: kA# / ka# where # is any char
    wildcard_key = prefix[:2] + "#"
    if wildcard_key in prefix_map:
        return prefix_map[wildcard_key]

    raise ValueError(f"Unknown Salesforce ID prefix: {prefix!r}")
