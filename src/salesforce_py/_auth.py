"""Shared auth helpers for environment-driven client construction.

Each async API client supports a ``from_env`` factory that resolves
credentials in this order:

1. **Client-credentials OAuth** — if ``SF_{PREFIX}_CLIENT_ID`` and
   ``SF_{PREFIX}_CLIENT_SECRET`` are both set, plus ``SF_INSTANCE_URL``
   (or ``SF_{PREFIX}_INSTANCE_URL``) for the My Domain URL, a
   ``client_credentials`` token is minted via
   :func:`fetch_org_token` and returned.

2. **SF CLI session** — if a ``target_org`` alias/username is supplied
   (and no client credentials are set), credentials are read from the
   SF CLI auth store via :class:`~salesforce_py.sf.org.SFOrg`.

3. **Failure** — if neither path resolves, :class:`~salesforce_py.exceptions.SalesforcePyError`
   is raised with a clear message explaining what is missing.

Environment variable prefixes per client:

    ============  =====================  ======================  ====================
    Client        CLIENT_ID              CLIENT_SECRET           INSTANCE_URL
    ============  =====================  ======================  ====================
    Connect       SF_CONNECT_CLIENT_ID   SF_CONNECT_CLIENT_SECRET  SF_CONNECT_INSTANCE_URL (or SF_INSTANCE_URL)
    Data 360      SF_DATA360_CLIENT_ID   SF_DATA360_CLIENT_SECRET  SF_DATA360_INSTANCE_URL (or SF_INSTANCE_URL)
    Models        SF_MODELS_CLIENT_ID    SF_MODELS_CLIENT_SECRET   SF_MODELS_INSTANCE_URL (or SF_INSTANCE_URL)
    ============  =====================  ======================  ====================

Note: The Models API requires ``sfap_api einstein_gpt_api api`` scopes on the
External Client App — a standard SF CLI session token does **not** carry
those scopes. ``ModelsClient.from_env`` therefore requires client credentials
and does not fall back to the SF CLI.
"""

from __future__ import annotations

import contextlib
import os
from typing import TYPE_CHECKING

import httpx

from salesforce_py._retry import DEFAULT_TIMEOUT, retry_async_http_call
from salesforce_py.exceptions import AuthError, SalesforcePyError

if TYPE_CHECKING:
    pass


def resolve_client_creds(prefix: str) -> tuple[str, str] | None:
    """Return ``(client_id, client_secret)`` from ``SF_{prefix}_CLIENT_ID/SECRET``.

    Args:
        prefix: Upper-case prefix, e.g. ``"CONNECT"``, ``"DATA360"``, ``"MODELS"``.

    Returns:
        ``(client_id, client_secret)`` if both env vars are non-empty, else ``None``.
    """
    client_id = os.environ.get(f"SF_{prefix}_CLIENT_ID", "").strip()
    client_secret = os.environ.get(f"SF_{prefix}_CLIENT_SECRET", "").strip()
    if client_id and client_secret:
        return client_id, client_secret
    return None


def resolve_instance_url(prefix: str) -> str:
    """Return the instance URL from ``SF_{prefix}_INSTANCE_URL`` or ``SF_INSTANCE_URL``.

    Args:
        prefix: Upper-case prefix, e.g. ``"CONNECT"``, ``"DATA360"``, ``"MODELS"``.

    Returns:
        The instance URL string (may be empty if neither var is set).
    """
    return (
        os.environ.get(f"SF_{prefix}_INSTANCE_URL", "").strip()
        or os.environ.get("SF_INSTANCE_URL", "").strip()
    )


async def fetch_org_token(
    my_domain: str,
    client_id: str,
    client_secret: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
) -> tuple[str, str]:
    """Mint a ``client_credentials`` bearer token for Connect / Data 360.

    Unlike the Models ``fetch_token`` helper (which also returns
    ``api_instance_url``), this simpler helper only needs the ``api`` scope
    and returns ``(access_token, instance_url)``.

    Args:
        my_domain: Salesforce My Domain URL, e.g. ``"https://myorg.my.salesforce.com"``.
        client_id: External Client App OAuth consumer key.
        client_secret: External Client App OAuth consumer secret.
        timeout: HTTP timeout for the token request.

    Returns:
        ``(access_token, instance_url)`` tuple.

    Raises:
        AuthError: On ``400``/``401`` — wrong credentials or missing scopes.
        SalesforcePyError: On any other transport failure.
    """
    url = f"{my_domain.rstrip('/')}/services/oauth2/token"
    async with httpx.AsyncClient(timeout=timeout) as http:
        response = await retry_async_http_call(
            lambda: http.post(
                url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )
        )

    if response.status_code in (400, 401):
        body = ""
        with contextlib.suppress(Exception):
            body = response.text[:500]
        raise AuthError(
            f"OAuth token request failed with {response.status_code}. "
            f"Check the My Domain URL, client ID/secret, and that the app has "
            f"the required scopes. Body: {body}"
        )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        body = ""
        with contextlib.suppress(Exception):
            body = response.text[:500]
        raise SalesforcePyError(
            f"OAuth token request failed {response.status_code}: {body}"
        ) from exc

    try:
        payload = response.json()
    except Exception as exc:
        raise SalesforcePyError(
            f"OAuth token endpoint returned non-JSON: {response.text[:500]}"
        ) from exc

    return payload["access_token"], payload["instance_url"]
