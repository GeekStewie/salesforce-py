"""Salesforce Payments operations.

Covers both ``/commerce/payments/...`` and ``/payments/...`` endpoints. Uses a
session rooted at ``/services/data/vXX.X/`` (no ``connect/`` prefix) — the
client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class PaymentsOperations(ConnectBaseOperations):
    """Wrapper for ``/commerce/payments/...`` and ``/payments/...`` endpoints."""

    # ------------------------------------------------------------------
    # /commerce/payments — authorizations, captures, reversals, sale, etc.
    # ------------------------------------------------------------------

    async def authorize(
        self,
        body: dict[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Authorize a payment (v49.0+)."""
        return await self._post(
            "commerce/payments/authorizations",
            json=body,
            headers=_idempotency_header(idempotency_key),
        )

    async def capture(
        self,
        authorization_id: str,
        body: dict[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Capture an authorized payment (v48.0+)."""
        authorization_id = self._ensure_18(authorization_id)
        return await self._post(
            f"commerce/payments/authorizations/{authorization_id}/captures",
            json=body,
            headers=_idempotency_header(idempotency_key),
        )

    async def reverse_authorization(
        self,
        authorization_id: str,
        body: dict[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Reverse an authorized payment (v51.0+)."""
        authorization_id = self._ensure_18(authorization_id)
        return await self._post(
            f"commerce/payments/authorizations/{authorization_id}/reversals",
            json=body,
            headers=_idempotency_header(idempotency_key),
        )

    async def post_authorization(
        self,
        body: dict[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Confirm readiness to capture a pre-authorized transaction (v54.0+)."""
        return await self._post(
            "commerce/payments/postAuths",
            json=body,
            headers=_idempotency_header(idempotency_key),
        )

    async def refund(
        self,
        payment_id: str,
        body: dict[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a refund for a payment (v48.0+)."""
        payment_id = self._ensure_18(payment_id)
        return await self._post(
            f"commerce/payments/payments/{payment_id}/refunds",
            json=body,
            headers=_idempotency_header(idempotency_key),
        )

    async def sale(
        self,
        body: dict[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Make a payment sale without a prior authorization (v54.0+)."""
        return await self._post(
            "commerce/payments/sales",
            json=body,
            headers=_idempotency_header(idempotency_key),
        )

    async def tokenize_payment_method(self, body: dict[str, Any]) -> dict[str, Any]:
        """Tokenize a payment method via the payment gateway (v51.0+)."""
        return await self._post("commerce/payments/payment-methods", json=body)

    # ------------------------------------------------------------------
    # /payments — payment intents
    # ------------------------------------------------------------------

    async def create_payment_intent(self, body: dict[str, Any]) -> dict[str, Any]:
        """Initiate a payment via a payment intent (v57.0+)."""
        return await self._post("payments/payment-intents", json=body)

    async def get_payment_intent_timeline(self, payment_intent_id: str) -> dict[str, Any]:
        """Retrieve the payment activity timeline for a payment intent (v60.0+)."""
        payment_intent_id = self._ensure_18(payment_intent_id)
        return await self._get(f"payments/payment-intents/{payment_intent_id}/timeline")

    # ------------------------------------------------------------------
    # /payments — payment method sets
    # ------------------------------------------------------------------

    async def get_payment_method_set(self, payment_method_set_id: str) -> dict[str, Any]:
        """Retrieve a payment method set by ID (v58.0+)."""
        payment_method_set_id = self._ensure_18(payment_method_set_id)
        return await self._get(f"payments/payment-method-sets/{payment_method_set_id}")

    async def get_payment_method_set_by_developer_name(self, developer_name: str) -> dict[str, Any]:
        """Retrieve a payment method set by developer name (v58.0+)."""
        return await self._get(
            "payments/payment-method-sets",
            params={"developerName": developer_name},
        )

    # ------------------------------------------------------------------
    # /payments — Apple Pay domains
    # ------------------------------------------------------------------

    def _apple_pay_base(self, merchant_account_id: str) -> str:
        return (
            f"payments/merchant-accounts/{self._ensure_18(merchant_account_id)}/apple-pay-domains"
        )

    async def register_apple_pay_domain(
        self, merchant_account_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Register an Apple Pay domain with the payment gateway."""
        return await self._post(self._apple_pay_base(merchant_account_id), json=body)

    async def list_apple_pay_domains(self, merchant_account_id: str) -> dict[str, Any]:
        """Retrieve a list of Apple Pay domains."""
        return await self._get(self._apple_pay_base(merchant_account_id))

    async def delete_apple_pay_domain(
        self, merchant_account_id: str, apple_pay_domain_id: str
    ) -> dict[str, Any]:
        """Delete an Apple Pay domain."""
        apple_pay_domain_id = self._ensure_18(apple_pay_domain_id)
        return await self._delete(
            f"{self._apple_pay_base(merchant_account_id)}/{apple_pay_domain_id}"
        )

    # ------------------------------------------------------------------
    # /payments — saved payment methods
    # ------------------------------------------------------------------

    def _saved_pm_base(self, merchant_account_id: str) -> str:
        return (
            f"payments/merchant-accounts/{self._ensure_18(merchant_account_id)}"
            "/saved-payment-methods"
        )

    async def list_saved_payment_methods(
        self,
        merchant_account_id: str,
        *,
        effective_account_id: str,
        page_size: int | None = None,
        page_token: str | None = None,
        sort_order: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve all saved payment methods for a merchant / contact (v58.0+)."""
        params: dict[str, Any] = {"effectiveAccountId": self._ensure_18(effective_account_id)}
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token is not None:
            params["pageToken"] = page_token
        if sort_order is not None:
            params["sortOrder"] = sort_order
        return await self._get(self._saved_pm_base(merchant_account_id), params=params)

    async def create_saved_payment_method(
        self, merchant_account_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a saved payment method for a merchant account (v58.0+)."""
        return await self._post(self._saved_pm_base(merchant_account_id), json=body)

    async def create_saved_payment_method_for_id(
        self,
        merchant_account_id: str,
        saved_payment_method_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a saved payment method associated with a given ID (v60.0+)."""
        saved_payment_method_id = self._ensure_18(saved_payment_method_id)
        return await self._post(
            f"{self._saved_pm_base(merchant_account_id)}/{saved_payment_method_id}",
            json=body,
        )

    async def update_saved_payment_method(
        self,
        merchant_account_id: str,
        saved_payment_method_id: str,
        body: dict[str, Any],
        *,
        effective_account_id: str,
    ) -> dict[str, Any]:
        """Update a saved payment method (v59.0+)."""
        saved_payment_method_id = self._ensure_18(saved_payment_method_id)
        return await self._patch(
            f"{self._saved_pm_base(merchant_account_id)}/{saved_payment_method_id}",
            json=body,
            params={"effectiveAccountId": self._ensure_18(effective_account_id)},
        )

    async def delete_saved_payment_method(
        self,
        merchant_account_id: str,
        saved_payment_method_id: str,
        *,
        effective_account_id: str,
    ) -> dict[str, Any]:
        """Delete a saved payment method (v58.0+)."""
        saved_payment_method_id = self._ensure_18(saved_payment_method_id)
        return await self._delete(
            f"{self._saved_pm_base(merchant_account_id)}/{saved_payment_method_id}",
            params={"effectiveAccountId": self._ensure_18(effective_account_id)},
        )

    # ------------------------------------------------------------------
    # /payments — save payment method token
    # ------------------------------------------------------------------

    def _save_token_path(self, merchant_account_id: str) -> str:
        return f"{self._saved_pm_base(merchant_account_id)}/saveToken"

    async def create_save_payment_method_token(
        self, merchant_account_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Create saved payment method token details from the gateway (v60.0+)."""
        return await self._post(self._save_token_path(merchant_account_id), json=body)

    async def update_save_payment_method_token(
        self,
        merchant_account_id: str,
        body: dict[str, Any],
        *,
        effective_account_id: str,
    ) -> dict[str, Any]:
        """Update saved payment method token details (v60.0+)."""
        return await self._patch(
            self._save_token_path(merchant_account_id),
            json=body,
            params={"effectiveAccountId": self._ensure_18(effective_account_id)},
        )

    async def delete_save_payment_method_token(
        self,
        merchant_account_id: str,
        *,
        effective_account_id: str,
    ) -> dict[str, Any]:
        """Delete saved payment method token details (v60.0+)."""
        return await self._delete(
            self._save_token_path(merchant_account_id),
            params={"effectiveAccountId": self._ensure_18(effective_account_id)},
        )

    # ------------------------------------------------------------------
    # /payments — payment links
    # ------------------------------------------------------------------

    async def get_payment_link_details(self, payment_link_id: str) -> dict[str, Any]:
        """Retrieve payment link details (v58.0+)."""
        payment_link_id = self._ensure_18(payment_link_id)
        return await self._get(f"payments/payment-link-configs/{payment_link_id}")

    async def create_payment_link_order(
        self, payment_link_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Create an order for a payment link (v58.0+)."""
        payment_link_id = self._ensure_18(payment_link_id)
        return await self._post(f"payments/link-to-order/{payment_link_id}", json=body)


def _idempotency_header(key: str | None) -> dict[str, str] | None:
    if key is None:
        return None
    return {"sfdc-Payments-Idempotency-Key": key}
