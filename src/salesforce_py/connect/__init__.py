"""Salesforce Connect REST API client.

Wraps the ``/services/data/vXX.X/connect/`` family of endpoints
(Chatter, Files, Communities, etc.).

Install the ``connect`` extra to unlock this module::

    pip install "salesforce-py[connect]"
    # or with uv:
    uv add "salesforce-py[connect]"
"""

try:
    import httpx as _httpx  # noqa: F401
except ImportError as exc:
    raise ImportError(
        "The 'connect' extra is required to use salesforce_py.connect.\n"
        "Install it with:  uv add 'salesforce-py[connect]'\n"
        "                  pip install 'salesforce-py[connect]'"
    ) from exc

from salesforce_py.connect.client import ConnectClient

__all__ = ["ConnectClient"]
