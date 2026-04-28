"""SF CLI config command wrappers."""

from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFConfigOperations(SFBaseOperations):
    """Wraps ``sf config`` commands for managing Salesforce CLI configuration.

    Config variables are machine-local (not org-specific), so all methods set
    ``include_target_org=False`` and ``include_api_version=False``.
    """

    def get(self, *variable_names: str, verbose: bool = False) -> list[dict[str, Any]]:
        """Get the value of one or more configuration variables.

        Args:
            *variable_names: One or more config variable names to retrieve
                (e.g. ``"target-org"``, ``"api-version"``).
            verbose: Display whether each variable is set locally or globally.

        Returns:
            List of dicts, each containing ``name``, ``value``, and optionally
            ``location`` when ``verbose=True``.
        """
        if not variable_names:
            raise ValueError("At least one configuration variable name is required.")

        args = ["config", "get"] + list(variable_names)
        if verbose:
            args.append("--verbose")

        result = self._run_capturing(
            args,
            label=f"Getting config {', '.join(variable_names)}",
            include_target_org=False,
            include_api_version=False,
        )
        if isinstance(result, list):
            return result
        return result.get("result", [result])

    def list_config(self) -> list[dict[str, Any]]:
        """List all configuration variables that have been previously set.

        Returns:
            List of dicts with ``name``, ``value``, and ``location``
            (``local``, ``global``, or environment variable).
        """
        result = self._run_capturing(
            ["config", "list"],
            label="Listing config variables",
            include_target_org=False,
            include_api_version=False,
        )
        if isinstance(result, list):
            return result
        return result.get("result", [])

    def set(
        self,
        variables: dict[str, str],
        global_config: bool = False,
    ) -> dict[str, Any]:
        """Set one or more configuration variables.

        Args:
            variables: Mapping of variable name to value, e.g.
                ``{"target-org": "my-scratch-org", "api-version": "59.0"}``.
            global_config: Set variables globally so they apply across all
                Salesforce DX projects. Without this flag, variables are set
                locally for the current project only.

        Returns:
            Result dict confirming the variables that were set.

        Raises:
            ValueError: If no variables are provided.
        """
        if not variables:
            raise ValueError("At least one configuration variable must be provided.")

        args = ["config", "set"]
        if global_config:
            args.append("--global")

        # Multiple variables require key=value format
        if len(variables) > 1:
            for name, value in variables.items():
                args.append(f"{name}={value}")
        else:
            name, value = next(iter(variables.items()))
            args += [name, value]

        return self._run_capturing(
            args,
            label=f"Setting config {', '.join(variables)}",
            include_target_org=False,
            include_api_version=False,
        )

    def unset(
        self,
        *variable_names: str,
        global_config: bool = False,
    ) -> dict[str, Any]:
        """Unset one or more configuration variables.

        Args:
            *variable_names: One or more config variable names to unset.
            global_config: Unset the variables globally instead of locally.

        Returns:
            Result dict confirming the variables that were unset.

        Raises:
            ValueError: If no variable names are provided.
        """
        if not variable_names:
            raise ValueError("At least one configuration variable name is required.")

        args = ["config", "unset"] + list(variable_names)
        if global_config:
            args.append("--global")

        return self._run_capturing(
            args,
            label=f"Unsetting config {', '.join(variable_names)}",
            include_target_org=False,
            include_api_version=False,
        )
