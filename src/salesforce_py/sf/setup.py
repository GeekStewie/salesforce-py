"""SF CLI installation and prerequisite checks."""

import logging
import re
import shutil
import subprocess
from typing import Any

_VERSION_RE = re.compile(r"^\d+(\.\d+)*$")

from salesforce_py.exceptions import SalesforcePyError

_log = logging.getLogger(__name__)

_SF_NPM_PACKAGE = "@salesforce/cli"
_NODE_BREW_FORMULA = "node"
# Official Homebrew install script — see https://brew.sh
_HOMEBREW_INSTALL_URL = "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"


class SFCLISetup:
    """Check for and install SF CLI prerequisites.

    Detection uses :func:`shutil.which` so the PATH must include the relevant
    directories (e.g. ``/opt/homebrew/bin`` on Apple Silicon).

    Typical usage::

        setup = SFCLISetup()
        if not setup.is_sf_installed():
            setup.ensure_sf_installed()
    """

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def is_sf_installed(self) -> bool:
        """Return True if the ``sf`` CLI is available on PATH.

        Returns:
            True when ``sf`` resolves to an executable.
        """
        return shutil.which("sf") is not None

    def is_node_installed(self) -> bool:
        """Return True if Node.js is available on PATH.

        Returns:
            True when ``node`` resolves to an executable.
        """
        return shutil.which("node") is not None

    def is_homebrew_installed(self) -> bool:
        """Return True if Homebrew is available on PATH.

        Returns:
            True when ``brew`` resolves to an executable.
        """
        return shutil.which("brew") is not None

    def get_sf_version(self) -> str | None:
        """Return the installed SF CLI version string, or None if not found.

        Returns:
            Version string such as ``"@salesforce/cli/2.x.x darwin-arm64 node-v20.x.x"``
            or None when SF CLI is not installed.
        """
        if not self.is_sf_installed():
            return None
        try:
            result = subprocess.run(
                "sf --version",
                shell=True,
                capture_output=True,
                text=True,
                timeout=15,
            )
            return result.stdout.strip() or None
        except (subprocess.TimeoutExpired, OSError):
            return None

    def get_node_version(self) -> str | None:
        """Return the installed Node.js version string, or None if not found.

        Returns:
            Version string such as ``"v20.11.0"`` or None when Node.js is
            not installed.
        """
        if not self.is_node_installed():
            return None
        try:
            result = subprocess.run(
                "node --version",
                shell=True,
                capture_output=True,
                text=True,
                timeout=15,
            )
            return result.stdout.strip() or None
        except (subprocess.TimeoutExpired, OSError):
            return None

    # ------------------------------------------------------------------
    # Installation
    # ------------------------------------------------------------------

    def install_homebrew(self, timeout: int = 300) -> None:
        """Install Homebrew via the official install script.

        This command is interactive — it will prompt for your macOS/Linux
        password and display its own progress output.  Do not capture stdout
        or stderr so the user can see and respond to the prompts.

        Args:
            timeout: Maximum seconds to wait for the install to complete
                (default 300 — 5 minutes).

        Raises:
            SalesforcePyError: When the install script exits with a non-zero code.
        """
        if self.is_homebrew_installed():
            _log.info("Homebrew is already installed")
            return

        _log.info("Installing Homebrew...")
        try:
            proc = subprocess.run(
                f'/bin/bash -c "$(curl -fsSL {_HOMEBREW_INSTALL_URL})"',
                shell=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise SalesforcePyError(f"Homebrew installation timed out after {timeout}s") from exc

        if proc.returncode != 0:
            raise SalesforcePyError(
                f"Homebrew installation failed: {{'exit_code': {proc.returncode}}}"
            )
        _log.info("Homebrew installed")

    def install_node(self, timeout: int = 300) -> None:
        """Install the LTS version of Node.js via Homebrew.

        Args:
            timeout: Maximum seconds to wait (default 300 — 5 minutes).

        Raises:
            CLINotFoundError: When Homebrew is not installed.
            SalesforcePyError: When ``brew install node`` exits with a non-zero code.
        """
        if self.is_node_installed():
            version = self.get_node_version()
            _log.info(f"Node.js is already installed ({version})")
            return

        if not self.is_homebrew_installed():
            raise SalesforcePyError(
                "Homebrew is required to install Node.js but was not found on PATH: "
                "{'hint': 'Run install_homebrew() first, or install Node.js manually from https://nodejs.org'}"
            )

        _log.info(f"Installing Node.js via Homebrew (brew install {_NODE_BREW_FORMULA})...")
        try:
            proc = subprocess.run(
                f"brew install {_NODE_BREW_FORMULA}",
                shell=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise SalesforcePyError(f"Node.js installation timed out after {timeout}s") from exc

        if proc.returncode != 0:
            raise SalesforcePyError(
                f"Node.js installation via Homebrew failed: {{'exit_code': {proc.returncode}}}"
            )
        _log.info("Node.js installed")

    def install_sf(
        self,
        version: str | None = None,
        timeout: int = 120,
    ) -> None:
        """Install or pin SF CLI globally via npm.

        Runs ``npm install @salesforce/cli[@<version>] --global``.  Does not
        use ``sudo`` — if you receive a permissions error on macOS/Linux, see
        the npm docs on fixing npm permissions.

        Args:
            version: Specific version to install, e.g. ``"2.0.1"``.  When
                None (default), the latest release is installed.  Pass a
                version to pin to an older release or to downgrade; pass None
                again to return to the current release.
            timeout: Maximum seconds to wait (default 120).

        Raises:
            SalesforcePyError: When Node.js/npm is not installed, the version
                string is invalid, or the npm install command exits with a
                non-zero code.
        """
        if version is not None and not _VERSION_RE.match(version):
            raise SalesforcePyError(
                "Invalid SF CLI version string: "
                f"{{'version': '{version}', 'hint': \"Expected format: '2.0.1'\"}}"
            )

        if self.is_sf_installed() and version is None:
            installed = self.get_sf_version()
            _log.info(f"SF CLI is already installed ({installed})")
            return

        if not self.is_node_installed():
            raise SalesforcePyError(
                "Node.js is required to install SF CLI but was not found on PATH: "
                "{'hint': 'Run install_node() first'}"
            )

        package = f"{_SF_NPM_PACKAGE}@{version}" if version else _SF_NPM_PACKAGE
        cmd = f"npm install {package} --global"
        label = f"version {version}" if version else "latest"
        _log.info(f"Installing SF CLI {label} ({cmd})...")
        try:
            proc = subprocess.run(
                cmd,
                shell=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise SalesforcePyError(f"SF CLI installation timed out after {timeout}s") from exc

        if proc.returncode != 0:
            raise SalesforcePyError(
                "SF CLI installation via npm failed: "
                f"{{'exit_code': {proc.returncode}, 'cmd': '{cmd}'}}"
            )
        _log.info(f"SF CLI {label} installed")

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def ensure_sf_installed(
        self,
        version: str | None = None,
        install_homebrew_if_missing: bool = True,
    ) -> None:
        """Ensure SF CLI is installed, installing prerequisites as needed.

        Checks SF CLI → Node.js → Homebrew in order and installs anything
        that is missing.

        Args:
            version: Specific SF CLI version to install, e.g. ``"2.0.1"``.
                When None (default), the latest release is installed.
            install_homebrew_if_missing: When True (default), attempt to
                install Homebrew if it is not found.  Set to False if you
                want the method to raise instead of triggering the
                interactive Homebrew installer.

        Raises:
            SalesforcePyError: When a prerequisite cannot be installed.
        """
        if self.is_sf_installed() and version is None:
            installed = self.get_sf_version()
            _log.info(f"SF CLI is installed ({installed})")
            return

        _log.warning("SF CLI not found — checking prerequisites...")

        if not self.is_node_installed():
            _log.warning("Node.js not found")

            if not self.is_homebrew_installed():
                if install_homebrew_if_missing:
                    self.install_homebrew()
                else:
                    raise SalesforcePyError(
                        "Homebrew is not installed and install_homebrew_if_missing=False: "
                        "{'hint': 'Install Homebrew from https://brew.sh or Node.js from https://nodejs.org'}"
                    )

            self.install_node()

        self.install_sf(version=version)

    # ------------------------------------------------------------------
    # Status summary
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        """Return a dict summarising the installation status of all tools.

        Returns:
            Dict with keys ``sf``, ``node``, ``homebrew`` — each a sub-dict
            with ``installed: bool`` and ``version: str | None``.
        """
        return {
            "sf": {
                "installed": self.is_sf_installed(),
                "version": self.get_sf_version(),
            },
            "node": {
                "installed": self.is_node_installed(),
                "version": self.get_node_version(),
            },
            "homebrew": {
                "installed": self.is_homebrew_installed(),
                "version": None,
            },
        }
