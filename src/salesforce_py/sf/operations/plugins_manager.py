"""SF CLI plugin installation and management wrappers."""

import re
from typing import Any

from salesforce_py.exceptions import SalesforcePyError
from salesforce_py.sf.base import SFBaseOperations

# Validated against: sf plugins install --help
_PLUGIN_VERSION_RE = re.compile(r"^[A-Za-z0-9._-]+$")

# CRM Analytics plugin — override if the package name changes.
_ANALYTICS_PLUGIN = "@salesforce/analytics"


class SFPluginsManagerOperations(SFBaseOperations):
    """Wraps ``sf plugins install`` and ``sf plugins reset`` commands.

    Plugin management is machine-local and org-agnostic, so
    ``include_target_org=False`` and ``include_api_version=False`` are set
    throughout.
    """

    # ------------------------------------------------------------------
    # Install
    # ------------------------------------------------------------------

    def install(
        self,
        plugin: str,
        version: str | None = None,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Install an SF CLI plugin from npm.

        Args:
            plugin: Long name of the plugin, e.g.
                ``"@salesforce/plugin-devops-center"``.
            version: Specific release tag to install, e.g. ``"1.2.27"``.
                When None (default), the latest release is installed.
            timeout: Subprocess timeout in seconds (default 300 — plugin
                installs can be slow on first run).

        Returns:
            Raw output dict (``{"output": ...}``).

        Raises:
            SalesforcePyError: When the version string contains invalid
                characters or the install command fails.
        """
        if version is not None and not _PLUGIN_VERSION_RE.match(version):
            raise SalesforcePyError(
                f"Invalid plugin version string: {version!r}",
            )

        package = f"{plugin}@{version}" if version else plugin
        return self._run_capturing(
            ["plugins", "install", package],
            label=f"Installing plugin '{package}'",
            timeout=timeout,
            include_target_org=False,
            include_api_version=False,
            include_json=False,
        )

    def install_analytics(
        self,
        version: str | None = None,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Install the Salesforce CRM Analytics SF CLI plugin.

        Convenience wrapper around :meth:`install` that pins the package to
        ``@salesforce/analytics``.

        Args:
            version: Specific release to install (default: latest).
            timeout: Subprocess timeout in seconds (default 300).

        Returns:
            Raw output dict (``{"output": ...}``).
        """
        return self.install(_ANALYTICS_PLUGIN, version=version, timeout=timeout)

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(
        self,
        reinstall: bool = False,
        hard: bool = False,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Uninstall all non-core SF CLI plugins.

        Removes third-party plugins, JIT plugins, and locally linked plugins,
        leaving only the core Salesforce CLI plugins as if the CLI was freshly
        installed.

        Args:
            reinstall: After uninstalling, reinstall all removed non-core
                plugins.  Equivalent to ``sf plugins reset --reinstall``.
            hard: Also remove all package manager files and directories
                (``node_modules``, ``package.json``, ``yarn.lock``,
                ``package-lock.json``) from the CLI's internal data directory.
                Equivalent to ``sf plugins reset --hard``.
            timeout: Subprocess timeout in seconds (default 300).

        Returns:
            Raw output dict (``{"output": ...}``).
        """
        args: list[str] = ["plugins", "reset"]
        if reinstall:
            args.append("--reinstall")
        if hard:
            args.append("--hard")
        label = "Resetting SF CLI plugins"
        if reinstall:
            label += " (reinstall)"
        if hard:
            label += " (hard)"
        return self._run_capturing(
            args,
            label=label,
            timeout=timeout,
            include_target_org=False,
            include_api_version=False,
            include_json=False,
        )
