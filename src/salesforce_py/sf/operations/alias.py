"""SF CLI alias command wrappers."""

from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFAliasOperations(SFBaseOperations):
    """Wraps ``sf alias`` commands for managing local SF CLI aliases.

    Aliases are global to the local machine and not org-specific, so all
    methods set ``include_target_org=False`` and ``include_api_version=False``.
    """

    def list_aliases(self) -> list[dict[str, Any]]:
        """List all aliases currently set on the local computer.

        Returns:
            List of dicts, each containing ``alias`` and ``value`` keys.
        """
        result = self._run(
            ["alias", "list"],
            include_target_org=False,
            include_api_version=False,
        )
        if isinstance(result, list):
            return result
        return result.get("aliases", [])

    def set_alias(self, aliases: dict[str, str]) -> dict[str, Any]:
        """Set one or more aliases on the local computer.

        Args:
            aliases: Mapping of alias name to value, e.g.
                ``{"my-scratch-org": "test-abc@example.com"}``.

        Returns:
            Result dict confirming the aliases that were set.
        """
        if not aliases:
            raise ValueError("At least one alias must be provided.")

        # SF CLI accepts: sf alias set key=value key2=value2
        alias_args = [f"{name}={value}" for name, value in aliases.items()]
        args = ["alias", "set"] + alias_args

        return self._run_capturing(
            args,
            label=f"Setting alias{'es' if len(aliases) > 1 else ''} {', '.join(aliases)}",
            include_target_org=False,
            include_api_version=False,
        )

    def unset_alias(
        self,
        aliases: list[str] | None = None,
        all_aliases: bool = False,
        no_prompt: bool = False,
    ) -> dict[str, Any]:
        """Unset one or more aliases on the local computer.

        Either ``aliases`` or ``all_aliases=True`` must be provided.

        Args:
            aliases: List of alias names to unset.
            all_aliases: Unset all currently set aliases.
            no_prompt: Skip confirmation when unsetting all aliases.

        Returns:
            Result dict confirming the aliases that were unset.

        Raises:
            ValueError: If neither ``aliases`` nor ``all_aliases`` is provided.
        """
        if not aliases and not all_aliases:
            raise ValueError("Provide alias names to unset or set all_aliases=True.")

        args = ["alias", "unset"]

        if all_aliases:
            args.append("--all")
            if no_prompt:
                args.append("--no-prompt")
        else:
            # aliases is guaranteed non-None here (validated above)
            args += aliases or []

        if all_aliases:
            label = "Unsetting all aliases"
        else:
            plural = "es" if len(aliases or []) > 1 else ""
            label = f"Unsetting alias{plural} {', '.join(aliases or [])}"

        return self._run_capturing(
            args,
            label=label,
            include_target_org=False,
            include_api_version=False,
        )
