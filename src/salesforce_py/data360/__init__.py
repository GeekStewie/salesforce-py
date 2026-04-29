"""Salesforce Data 360 Connect REST API client.

Async wrapper around the ``/services/data/vXX.X/ssot/`` family of endpoints —
the REST surface for Data 360 (formerly Data Cloud / CDP).

Install the ``data360`` extra to unlock this module::

    pip install "salesforce-py[data360]"
    # or with uv:
    uv add "salesforce-py[data360]"
"""

try:
    import httpx as _httpx  # noqa: F401
except ImportError as exc:
    raise ImportError(
        "The 'data360' extra is required to use salesforce_py.data360.\n"
        "Install it with:  uv add 'salesforce-py[data360]'\n"
        "                  pip install 'salesforce-py[data360]'"
    ) from exc

from salesforce_py.data360.client import Data360Client

__all__ = ["Data360Client"]
