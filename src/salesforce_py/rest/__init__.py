"""Salesforce REST API client.

Async wrapper around the ``/services/data/vXX.X/`` REST API surface —
SOQL / SOSL queries, sObject CRUD, composite / batch / graph / tree,
quick actions, invocable actions, tooling, UI API, analytics, process /
approvals, and the rest.

Install the ``rest`` extra to unlock this module::

    pip install "salesforce-py[rest]"
    # or with uv:
    uv add "salesforce-py[rest]"
"""

try:
    import httpx as _httpx  # noqa: F401
except ImportError as exc:
    raise ImportError(
        "The 'rest' extra is required to use salesforce_py.rest.\n"
        "Install it with:  uv add 'salesforce-py[rest]'\n"
        "                  pip install 'salesforce-py[rest]'"
    ) from exc

from salesforce_py.rest.client import RestClient

__all__ = ["RestClient"]
