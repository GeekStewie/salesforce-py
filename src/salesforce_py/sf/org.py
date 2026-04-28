"""Salesforce org connection and auth management via SF CLI."""

import json
import logging
import os
import subprocess
from typing import Any

from salesforce_py.exceptions import CLIError, SalesforcePyError

_log = logging.getLogger(__name__)

# Environment variables applied to every SF CLI invocation.
# These mirror the container/CI configuration used in Heroku deployments.
_SF_ENV_DEFAULTS: dict[str, str] = {
    "SF_AUTOUPDATE_DISABLE": "true",
    "SF_CONTAINER_MODE": "true",
    "SF_DISABLE_DNS_CHECK": "true",
    "SF_DISABLE_SOURCE_MEMBER_POLLING": "true",
    "SF_DISABLE_SOURCE_MOBILITY": "true",
    "SF_DISABLE_TELEMETRY": "true",
    "SF_ENV": "true",
    "SF_HIDE_RELEASE_NOTES": "true",
    "SF_HIDE_RELEASE_NOTES_FOOTER": "true",
    "SF_ORG_METADATA_REST_DEPLOY": "true",
    "SF_SKIP_NEW_VERSION_CHECK": "true",
}


class SFOrg:
    """Represents a Salesforce org connection managed by the SF CLI auth store.

    Reads credentials lazily from ``sf org display`` on first use.
    Designed to be extended later to accept a CumulusCI OrgConfig directly.

    Args:
        target_org: SF CLI alias or username. None resolves the default alias.
        lazy_connect: When True (default) defer ``sf org display`` until first use.
    """

    def __init__(
        self,
        target_org: str | None = None,
        lazy_connect: bool = True,
    ) -> None:
        """Initialise SFOrg.

        Args:
            target_org: SF CLI alias or username. None resolves the default alias.
            lazy_connect: When True (default) defer ``sf org display`` until first use.
        """
        self.target_org: str | None = target_org
        self.instance_url: str = ""
        self.access_token: str = ""
        self.username: str = ""
        self.org_id: str = ""
        self.alias: str = ""
        self.is_scratch: bool = False
        self.expiry_date: str | None = None
        self._connected: bool = False

        if not lazy_connect:
            self.connect()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def connect(self) -> bool:
        """Connect to the org by calling ``sf org display``.

        Returns:
            True if connection succeeded, False otherwise.
        """
        if self._connected:
            return True

        try:
            result = self._run_raw(
                self._build_sf_cmd(["org", "display"]),
                timeout=30,
            )
            info = result.get("result", result)
            self.instance_url = info.get("instanceUrl", "")
            self.access_token = info.get("accessToken", "")
            self.username = info.get("username", "")
            self.org_id = info.get("id", "")
            self.alias = info.get("alias", self.target_org or "")
            self.is_scratch = bool(info.get("isScratch", False))
            self.expiry_date = info.get("expirationDate")
            self._connected = True
            return True
        except SalesforcePyError as exc:
            _log.error(f"Failed to connect to org: {exc}")
            return False

    def is_connected(self) -> bool:
        """Return True if org credentials have been loaded."""
        return self._connected

    def display(self) -> dict[str, Any]:
        """Return org display info from SF CLI.

        Returns:
            Dict containing org connection details.
        """
        self._ensure_connected()
        return self._run_raw(self._build_sf_cmd(["org", "display"]))

    def env(self) -> dict[str, str]:
        """Return an isolated environment dict for subprocess calls.

        Combines the current process environment with the SF CLI defaults
        and org-specific credentials. Never mutates ``os.environ``.

        Returns:
            Environment dict suitable for passing to ``subprocess.run``.
        """
        base = os.environ.copy()
        base.update(_SF_ENV_DEFAULTS)

        # If credentials are loaded, inject them so callers don't need to
        # re-authenticate inside subprocess invocations.
        if self._connected:
            if self.access_token:
                base["SF_ACCESS_TOKEN"] = self.access_token
            if self.instance_url:
                base["SF_INSTANCE_URL"] = self.instance_url

        return base

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_connected(self) -> None:
        """Connect lazily on first use."""
        if not self._connected:
            self.connect()

    def _build_sf_cmd(self, args: list[str]) -> list[str]:
        """Prepend 'sf' and append target-org + --json flags.

        Args:
            args: SF CLI sub-command parts, e.g. ['org', 'display'].

        Returns:
            Full command list ready for subprocess.
        """
        cmd = ["sf"] + args + ["--json"]
        if self.target_org:
            cmd += ["--target-org", self.target_org]
        return cmd

    def _run_raw(self, cmd: list[str], timeout: int = 120) -> dict[str, Any]:
        """Execute an SF CLI command and return the parsed JSON result.

        Args:
            cmd: Full command list.
            timeout: Subprocess timeout in seconds.

        Returns:
            Parsed JSON dict (``result`` key unwrapped if present).

        Raises:
            SalesforcePyError: On non-zero exit or JSON parse failure.
        """
        env = self.env()
        try:
            proc = subprocess.run(
                " ".join(cmd),
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            raise SalesforcePyError(
                f"SF CLI command timed out after {timeout}s: {{'cmd': '{' '.join(cmd)}'}}"
            ) from exc

        raw_output = proc.stdout.strip()
        stderr_output = proc.stderr.strip()

        if proc.returncode != 0:
            # SF CLI often writes JSON even on failure — try to surface message
            detail = raw_output or stderr_output
            try:
                payload = json.loads(detail)
                detail = payload.get("message") or payload.get("result") or detail
            except (json.JSONDecodeError, AttributeError):
                pass
            raise CLIError(
                returncode=proc.returncode,
                stdout=raw_output,
                stderr=stderr_output,
            )

        if stderr_output:
            _log.warning(f"SF CLI stderr: {stderr_output[:500]}")

        if not raw_output:
            return {}

        try:
            payload = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise SalesforcePyError(
                f"SF CLI returned non-JSON output: {{'cmd': '{' '.join(cmd)}', 'output': '{raw_output[:500]}'}}"
            ) from exc

        # Surface any warnings embedded in the payload
        for warning in payload.get("warnings", []):
            _log.warning(f"SF CLI: {warning}")

        return payload

    def __repr__(self) -> str:
        """Return debug representation."""
        return f"SFOrg(target_org={self.target_org!r}, connected={self._connected})"
