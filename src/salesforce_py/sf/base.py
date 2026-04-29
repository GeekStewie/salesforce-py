"""Base class for all SF CLI operation wrappers."""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from salesforce_py._defaults import DEFAULT_API_VERSION
from salesforce_py.sf.org import SFOrg
from salesforce_py.exceptions import CLIError, SalesforcePyError

_log = logging.getLogger(__name__)


def _resolve_api_version() -> str:
    """Read the sourceApiVersion from sfdx-project.json in the working directory tree.

    Walks up from the current directory to find sfdx-project.json.

    Returns:
        API version string (e.g. ``"59.0"``) or None if not found.
    """
    current = Path.cwd()
    for directory in [current, *current.parents]:
        candidate = directory / "sfdx-project.json"
        if candidate.is_file():
            try:
                data = json.loads(candidate.read_text(encoding="utf-8"))
                version = data.get("sourceApiVersion")
                if version:
                    return str(version)
            except (json.JSONDecodeError, OSError):
                pass
            break  # Found file but couldn't read — don't keep searching
    return DEFAULT_API_VERSION


class SFBaseOperations:
    """Shared subprocess dispatch layer for all SF CLI operation classes.

    Every subclass receives an :class:`SFOrg` instance and delegates
    subprocess execution here.  All commands are run with:

    - ``--json`` for machine-readable output
    - ``--api-version`` when a ``sourceApiVersion`` is found in ``sfdx-project.json``
    - The org's isolated environment (SF_* vars, no ``os.environ`` mutation)
    - ``shell=True`` as required by the deployment environment

    Args:
        org: Authenticated :class:`SFOrg` instance.
    """

    def __init__(self, org: SFOrg) -> None:
        """Initialise with an SFOrg.

        Args:
            org: Authenticated SFOrg instance.
        """
        self._org = org
        self._api_version: str | None = _resolve_api_version()

    # ------------------------------------------------------------------
    # Protected helpers used by subclasses
    # ------------------------------------------------------------------

    def _build_cmd(
        self,
        args: list[str],
        *,
        include_target_org: bool = True,
        include_api_version: bool = True,
        include_json: bool = True,
    ) -> list[str]:
        """Build a full SF CLI command.

        Args:
            args: Sub-command parts, e.g. ``['apex', 'run', '--file', 'anon.apex']``.
            include_target_org: Append ``--target-org`` when the org has an alias.
            include_api_version: Append ``--api-version`` when available.
            include_json: Append ``--json`` for machine-readable output. Set to
                False for streaming commands (e.g. ``apex tail log``) that do not
                support the flag.

        Returns:
            Full command list including ``sf`` and optional flags.
        """
        cmd = ["sf"] + args

        if include_json:
            cmd.append("--json")

        if include_target_org and self._org.target_org:
            cmd += ["--target-org", self._org.target_org]

        if include_api_version and self._api_version:
            cmd += ["--api-version", self._api_version]

        return cmd

    def _run(
        self,
        args: list[str],
        *,
        timeout: int = 120,
        include_target_org: bool = True,
        include_api_version: bool = True,
        include_json: bool = True,
    ) -> dict[str, Any]:
        """Execute an SF CLI command and return the unwrapped result.

        Ensures the org is connected before running, then dispatches via
        ``subprocess.run`` with ``shell=True`` and the org's isolated env.

        Args:
            args: Sub-command parts passed to :meth:`_build_cmd`.
            timeout: Subprocess timeout in seconds (default 120).
            include_target_org: Forward to :meth:`_build_cmd`.
            include_api_version: Forward to :meth:`_build_cmd`.
            include_json: Forward to :meth:`_build_cmd`. Set False for commands
                that do not accept ``--json`` (e.g. ``apex tail log``).

        Returns:
            The ``result`` value from the SF CLI JSON envelope, or the full
            parsed dict when no ``result`` key is present.

        Raises:
            SalesforcePyError: On non-zero exit code or JSON parse failure.
        """
        self._org._ensure_connected()

        cmd = self._build_cmd(
            args,
            include_target_org=include_target_org,
            include_api_version=include_api_version,
            include_json=include_json,
        )
        cmd_str = " ".join(cmd)
        env = self._org.env()

        try:
            proc = subprocess.run(
                cmd_str,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            raise SalesforcePyError(
                f"SF CLI command timed out after {timeout}s: {{'cmd': '{cmd_str}'}}"
            ) from exc

        raw_output = proc.stdout.strip()
        stderr_output = proc.stderr.strip()

        if proc.returncode != 0:
            detail: str | dict = raw_output or stderr_output
            try:
                payload = json.loads(str(detail))
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

        # When --json was not passed, return the raw output as a text payload
        # so callers can still inspect stdout (e.g. apex tail log).
        if not include_json:
            return {"output": raw_output}

        try:
            payload = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise SalesforcePyError(
                f"SF CLI returned non-JSON output: {{'cmd': '{cmd_str}', 'output': '{raw_output[:500]}'}}"
            ) from exc

        for warning in payload.get("warnings", []):
            _log.warning(f"SF CLI: {warning}")

        # Unwrap the SF CLI envelope: {"status": 0, "result": {...}}
        return payload.get("result", payload)

    def _run_capturing(
        self,
        args: list[str],
        *,
        label: str = "Running",
        timeout: int = 120,
        include_target_org: bool = True,
        include_api_version: bool = True,
        include_json: bool = True,
    ) -> dict[str, Any]:
        """Execute an SF CLI command, printing progress to the terminal.

        Uses the logger to emit a start message and a completion (or
        failure) message.  Suitable for operations where callers want simple
        inline feedback without a full Rich live panel.

        Args:
            args: Sub-command parts.
            label: Human-readable label for progress output (e.g. ``"Deploying"``).
            timeout: Subprocess timeout in seconds.
            include_target_org: Forward to :meth:`_build_cmd`.
            include_api_version: Forward to :meth:`_build_cmd`.
            include_json: Forward to :meth:`_build_cmd`. Set False for commands
                that do not accept ``--json`` (e.g. ``apex tail log``).

        Returns:
            Unwrapped result dict from :meth:`_run`.

        Raises:
            SalesforcePyError: Propagated from :meth:`_run`.
        """
        org_label = self._org.target_org or "default org"
        _log.info(f"{label} [{org_label}]")
        try:
            result = self._run(
                args,
                timeout=timeout,
                include_target_org=include_target_org,
                include_api_version=include_api_version,
                include_json=include_json,
            )
            _log.info(f"{label} complete [{org_label}]")
            return result
        except SalesforcePyError:
            _log.error(f"{label} failed [{org_label}]")
            raise
