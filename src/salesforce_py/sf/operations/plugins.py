"""SF CLI plugins command wrappers."""

from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFPluginsOperations(SFBaseOperations):
    """Wraps ``sf plugins`` commands for finding and managing SF CLI plugins.

    Plugin management is machine-local and org-agnostic, so
    ``include_target_org=False`` and ``include_api_version=False`` are set
    throughout.
    """

    def discover(self) -> list[dict[str, Any]]:
        """See a list of third-party SF CLI plugins available to install.

        Returns:
            List of discoverable plugin dicts.
        """
        result = self._run_capturing(
            ["plugins", "discover"],
            label="Discovering SF CLI plugins",
            include_target_org=False,
            include_api_version=False,
        )
        if isinstance(result, list):
            return result
        return result.get("result", [])
