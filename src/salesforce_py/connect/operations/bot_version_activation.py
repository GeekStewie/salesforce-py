"""Bot Version Activation Connect API operations (v50.0+)."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class BotVersionActivationOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/bot-versions/{botVersionId}/activation``."""

    async def get_activation(self, bot_version_id: str) -> dict[str, Any]:
        """Get the activation info of a bot version.

        Args:
            bot_version_id: Bot version ID.

        Returns:
            Bot Version Activation Info dict.
        """
        bot_version_id = self._ensure_18(bot_version_id)
        return await self._get(f"bot-versions/{bot_version_id}/activation")

    async def set_activation(
        self,
        bot_version_id: str,
        *,
        status: str,
        in_body: bool = True,
    ) -> dict[str, Any]:
        """Change activation status of a bot version.

        Args:
            bot_version_id: Bot version ID.
            status: Activation status — ``"Active"`` or ``"Inactive"``.
            in_body: If ``True`` (default), pass status in the request body;
                otherwise pass as a ``status`` query parameter.

        Returns:
            Bot Version Activation Info dict.
        """
        bot_version_id = self._ensure_18(bot_version_id)
        path = f"bot-versions/{bot_version_id}/activation"
        if in_body:
            return await self._post(path, json={"status": status})
        return await self._post(path, params={"status": status})
