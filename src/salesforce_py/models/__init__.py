"""Salesforce Models REST API client.

Async wrapper around the ``/einstein/platform/v1/`` family of endpoints —
the REST surface for the Salesforce Models API (Einstein generative AI
platform). Covers the four documented capabilities:

- ``/models/{modelName}/chat-generations``
- ``/models/{modelName}/embeddings``
- ``/models/{modelName}/generations``
- ``/feedback``

Install the ``models`` extra to unlock this module::

    pip install "salesforce-py[models]"
    # or with uv:
    uv add "salesforce-py[models]"
"""

try:
    import httpx as _httpx  # noqa: F401
except ImportError as exc:
    raise ImportError(
        "The 'models' extra is required to use salesforce_py.models.\n"
        "Install it with:  uv add 'salesforce-py[models]'\n"
        "                  pip install 'salesforce-py[models]'"
    ) from exc

from salesforce_py.models.client import ModelsClient
from salesforce_py.models.supported_models import SUPPORTED_MODELS
from salesforce_py.models.token import TokenResponse, fetch_token

__all__ = ["ModelsClient", "SUPPORTED_MODELS", "TokenResponse", "fetch_token"]
