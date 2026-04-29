"""Client-credentials token helper for the Salesforce Models REST API.

The Models API is token-driven but has a dedicated bootstrap flow:

    POST {my_domain}/services/oauth2/token
        grant_type=client_credentials
        client_id=<consumer_key>
        client_secret=<consumer_secret>

The response includes an ``access_token`` (a Salesforce-issued JWT) plus
an ``api_instance_url`` — the geo-appropriate host for subsequent Models
API requests.

This helper performs that one call and returns a :class:`TokenResponse`
you can hand to :class:`~salesforce_py.models.ModelsClient`. It does not
cache or refresh the token; callers own that lifecycle.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import Any

import httpx

from salesforce_py._retry import DEFAULT_TIMEOUT, retry_async_http_call
from salesforce_py.exceptions import AuthError, SalesforcePyError


@dataclass(frozen=True, slots=True)
class TokenResponse:
    """Parsed response from the ``/services/oauth2/token`` endpoint.

    Attributes:
        access_token: Bearer JWT for use with the Models API.
        instance_url: Org instance URL returned by the token endpoint.
        api_instance_url: Region-specific Models API host (e.g.
            ``https://api.salesforce.com``). Use this as the ``base_url``
            of :class:`~salesforce_py.models.ModelsClient` when present.
        token_type: Always ``"Bearer"``.
        issued_at: Unix millisecond timestamp (string) when the token was
            issued — use ``int(token.issued_at)`` to parse.
        scope: Space-separated list of granted scopes.
        signature: Salesforce-signed digest over the token payload.
        raw: The complete JSON body, in case the server returns additional
            fields not captured above.
    """

    access_token: str
    instance_url: str
    api_instance_url: str | None
    token_type: str
    issued_at: str
    scope: str
    signature: str | None
    raw: dict[str, Any]

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> TokenResponse:
        return cls(
            access_token=body["access_token"],
            instance_url=body["instance_url"],
            api_instance_url=body.get("api_instance_url"),
            token_type=body.get("token_type", "Bearer"),
            issued_at=body.get("issued_at", ""),
            scope=body.get("scope", ""),
            signature=body.get("signature"),
            raw=body,
        )


async def fetch_token(
    my_domain: str,
    consumer_key: str,
    consumer_secret: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
) -> TokenResponse:
    """Mint a client-credentials JWT for the Salesforce Models API.

    Args:
        my_domain: Current My Domain URL, e.g. ``"https://mycompany.my.salesforce.com"``.
            The helper normalises trailing slashes and an http(s) scheme is required.
        consumer_key: External Client App OAuth consumer key.
        consumer_secret: External Client App OAuth consumer secret.
        timeout: HTTP timeout in seconds for the token request.

    Returns:
        :class:`TokenResponse` with the access token and related metadata.

    Raises:
        AuthError: If Salesforce returns 400/401 (invalid credentials, wrong
            domain, or the app is missing required scopes).
        SalesforcePyError: On any other transport or non-JSON failure.
    """
    url = f"{my_domain.rstrip('/')}/services/oauth2/token"
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await retry_async_http_call(
            lambda: client.post(
                url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": consumer_key,
                    "client_secret": consumer_secret,
                },
            )
        )

    if response.status_code in (400, 401):
        body = ""
        with contextlib.suppress(Exception):
            body = response.text[:500]
        raise AuthError(
            f"Models API token request failed with {response.status_code}. "
            f"Verify the My Domain URL, consumer key/secret, and that the app has "
            f"the 'sfap_api einstein_gpt_api api' scopes. Body: {body}"
        )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        body = ""
        with contextlib.suppress(Exception):
            body = response.text[:500]
        raise SalesforcePyError(
            f"Models API token request failed {response.status_code}: {body}"
        ) from exc

    try:
        payload = response.json()
    except Exception as exc:
        raise SalesforcePyError(
            f"Models API token endpoint returned non-JSON: {response.text[:500]}"
        ) from exc

    return TokenResponse.from_json(payload)
