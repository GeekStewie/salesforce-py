"""Named Credentials Connect API operations.

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class NamedCredentialsOperations(ConnectBaseOperations):
    """Wrapper for ``/named-credentials/...`` endpoints (v56.0+).

    Covers credentials, external credentials, named credentials, and
    external auth identity providers.
    """

    # ------------------------------------------------------------------
    # Credential  /named-credentials/credential
    # ------------------------------------------------------------------

    async def get_credential(
        self,
        *,
        external_credential: str,
        principal_type: str,
        principal_name: str | None = None,
    ) -> dict[str, Any]:
        """Get a credential (v56.0+).

        Args:
            external_credential: External credential developer name.
            principal_type: ``AwsStsPrincipal``, ``NamedPrincipal``, or
                ``PerUserPrincipal``.
            principal_name: Principal name (required when
                ``principal_type`` is ``NamedPrincipal``).

        Returns:
            Credential dict.
        """
        params: dict[str, Any] = {
            "externalCredential": external_credential,
            "principalType": principal_type,
        }
        if principal_name is not None:
            params["principalName"] = principal_name
        return await self._get("named-credentials/credential", params=params)

    async def create_credential(
        self, body: dict[str, Any], *, action: str | None = None
    ) -> dict[str, Any]:
        """Create a credential (v56.0+).

        Args:
            body: Credential Input payload (see Salesforce docs).
            action: Optional action, e.g. ``"Refresh"`` (v58.0+) to
                refresh an OAuth or AWS Roles Anywhere credential.

        Returns:
            Credential dict.
        """
        params: dict[str, Any] = {}
        if action is not None:
            params["action"] = action
        return await self._post(
            "named-credentials/credential", json=body, params=params
        )

    async def replace_credential(self, body: dict[str, Any]) -> dict[str, Any]:
        """Replace a credential (v56.0+).

        Args:
            body: Credential Input payload.

        Returns:
            Credential dict.
        """
        return await self._put("named-credentials/credential", json=body)

    async def update_credential(self, body: dict[str, Any]) -> dict[str, Any]:
        """Update a custom credential (v59.0+, custom protocols only).

        Args:
            body: Credential Input payload.

        Returns:
            Credential dict.
        """
        return await self._patch("named-credentials/credential", json=body)

    async def delete_credential(
        self,
        *,
        external_credential: str,
        principal_type: str,
        principal_name: str | None = None,
        authentication_parameters: list[str] | None = None,
    ) -> dict[str, Any]:
        """Delete a credential (v56.0+).

        Args:
            external_credential: External credential developer name.
            principal_type: ``AwsStsPrincipal``, ``NamedPrincipal``, or
                ``PerUserPrincipal``.
            principal_name: Principal name (required when
                ``principal_type`` is ``NamedPrincipal``).
            authentication_parameters: Custom-protocol credential names
                to delete (v59.0+). Omit to delete all.

        Returns:
            Empty dict on success.
        """
        params: dict[str, Any] = {
            "externalCredential": external_credential,
            "principalType": principal_type,
        }
        if principal_name is not None:
            params["principalName"] = principal_name
        if authentication_parameters is not None:
            params["authenticationParameters"] = ",".join(
                authentication_parameters
            )
        return await self._delete(
            "named-credentials/credential", params=params
        )

    async def get_oauth_url(self, body: dict[str, Any]) -> dict[str, Any]:
        """Get the URL for the OAuth token flow for an external credential.

        Despite being a POST, this resource retrieves information (v56.0+).

        Args:
            body: OAuth credential auth URL input payload.

        Returns:
            OAuth Credential Auth URL dict.
        """
        return await self._post(
            "named-credentials/credential/auth-url/o-auth", json=body
        )

    # ------------------------------------------------------------------
    # External credentials
    # ------------------------------------------------------------------

    async def list_external_credentials(self) -> dict[str, Any]:
        """Get external credentials the user can authenticate to (v56.0+).

        Returns:
            External Credential List dict.
        """
        return await self._get("named-credentials/external-credentials")

    async def create_external_credential(
        self, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Create an external credential (v58.0+).

        Args:
            body: External Credential Input payload.

        Returns:
            External Credential dict.
        """
        return await self._post(
            "named-credentials/external-credentials", json=body
        )

    async def get_external_credential(
        self, developer_name: str
    ) -> dict[str, Any]:
        """Get an external credential (v56.0+).

        Args:
            developer_name: External credential developer name.

        Returns:
            External Credential dict.
        """
        return await self._get(
            f"named-credentials/external-credentials/{developer_name}"
        )

    async def update_external_credential(
        self, developer_name: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an external credential (v58.0+).

        Args:
            developer_name: External credential developer name.
            body: External Credential Input payload.

        Returns:
            External Credential dict.
        """
        return await self._put(
            f"named-credentials/external-credentials/{developer_name}",
            json=body,
        )

    async def delete_external_credential(
        self, developer_name: str
    ) -> dict[str, Any]:
        """Delete an external credential (v58.0+).

        Args:
            developer_name: External credential developer name.

        Returns:
            Empty dict on success.
        """
        return await self._delete(
            f"named-credentials/external-credentials/{developer_name}"
        )

    # ------------------------------------------------------------------
    # Named credentials
    # ------------------------------------------------------------------

    async def list_named_credentials(self) -> dict[str, Any]:
        """Get a list of named credentials in the org (v58.0+).

        Returns:
            Named Credential List dict.
        """
        return await self._get("named-credentials/named-credential-setup")

    async def create_named_credential(
        self, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a named credential (v58.0+).

        Args:
            body: Named Credential Input payload.

        Returns:
            Named Credential dict.
        """
        return await self._post(
            "named-credentials/named-credential-setup", json=body
        )

    async def get_named_credential(self, developer_name: str) -> dict[str, Any]:
        """Get a named credential (v58.0+).

        Args:
            developer_name: Named credential developer name.

        Returns:
            Named Credential dict.
        """
        return await self._get(
            f"named-credentials/named-credential-setup/{developer_name}"
        )

    async def update_named_credential(
        self, developer_name: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a named credential (v58.0+).

        Args:
            developer_name: Named credential developer name.
            body: Named Credential Input payload.

        Returns:
            Named Credential dict.
        """
        return await self._put(
            f"named-credentials/named-credential-setup/{developer_name}",
            json=body,
        )

    async def delete_named_credential(
        self, developer_name: str
    ) -> dict[str, Any]:
        """Delete a named credential (v58.0+).

        Args:
            developer_name: Named credential developer name.

        Returns:
            Empty dict on success.
        """
        return await self._delete(
            f"named-credentials/named-credential-setup/{developer_name}"
        )

    # ------------------------------------------------------------------
    # External auth identity providers
    # ------------------------------------------------------------------

    async def list_external_auth_identity_providers(self) -> dict[str, Any]:
        """Get a list of external auth identity providers (v62.0+).

        Returns:
            External Auth Identity Provider List dict.
        """
        return await self._get(
            "named-credentials/external-auth-identity-providers"
        )

    async def create_external_auth_identity_provider(
        self, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Create an external auth identity provider (v62.0+).

        Args:
            body: External auth identity provider payload.

        Returns:
            External Auth Identity Provider dict.
        """
        return await self._post(
            "named-credentials/external-auth-identity-providers", json=body
        )

    async def get_external_auth_identity_provider(
        self, full_name: str
    ) -> dict[str, Any]:
        """Get an external auth identity provider (v62.0+).

        Args:
            full_name: Full name of the identity provider.

        Returns:
            External Auth Identity Provider dict.
        """
        return await self._get(
            f"named-credentials/external-auth-identity-providers/{full_name}"
        )

    async def update_external_auth_identity_provider(
        self, full_name: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an external auth identity provider (v62.0+).

        Args:
            full_name: Full name of the identity provider.
            body: External auth identity provider payload.

        Returns:
            External Auth Identity Provider dict.
        """
        return await self._put(
            f"named-credentials/external-auth-identity-providers/{full_name}",
            json=body,
        )

    async def delete_external_auth_identity_provider(
        self, full_name: str
    ) -> dict[str, Any]:
        """Delete an external auth identity provider (v62.0+).

        Args:
            full_name: Full name of the identity provider.

        Returns:
            Empty dict on success.
        """
        return await self._delete(
            f"named-credentials/external-auth-identity-providers/{full_name}"
        )

    # ------------------------------------------------------------------
    # External auth identity provider credentials
    # ------------------------------------------------------------------

    async def get_external_auth_identity_provider_credentials(
        self, full_name: str
    ) -> dict[str, Any]:
        """Get external auth identity provider credentials (v62.0+).

        Args:
            full_name: Full name of the identity provider.

        Returns:
            External Auth Identity Provider Credentials dict.
        """
        return await self._get(
            f"named-credentials/external-auth-identity-provider-credentials/{full_name}"
        )

    async def create_external_auth_identity_provider_credentials(
        self, full_name: str, credentials: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create external auth identity provider credentials (v62.0+).

        Args:
            full_name: Full name of the identity provider.
            credentials: List of ``{"credentialName": ...,
                "credentialValue": ...}`` entries.

        Returns:
            External Auth Identity Provider Credentials dict.
        """
        return await self._post(
            f"named-credentials/external-auth-identity-provider-credentials/{full_name}",
            json={"credentials": credentials},
        )

    async def replace_external_auth_identity_provider_credentials(
        self, full_name: str, credentials: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Replace external auth identity provider credentials (v62.0+).

        Args:
            full_name: Full name of the identity provider.
            credentials: List of ``{"credentialName": ...,
                "credentialValue": ...}`` entries.

        Returns:
            External Auth Identity Provider Credentials dict.
        """
        return await self._put(
            f"named-credentials/external-auth-identity-provider-credentials/{full_name}",
            json={"credentials": credentials},
        )
