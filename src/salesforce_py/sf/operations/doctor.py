"""SF CLI doctor command wrappers."""

from pathlib import Path
from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFDoctorOperations(SFBaseOperations):
    """Wraps the ``sf doctor`` command for CLI environment diagnostics.

    Doctor is machine-local and org-agnostic, so ``include_target_org=False``
    and ``include_api_version=False`` are set throughout.
    """

    def run(
        self,
        command: str | None = None,
        plugin: str | None = None,
        output_dir: Path | None = None,
        create_issue: bool = False,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """Gather CLI configuration data and run diagnostic tests.

        Without parameters, displays a diagnostic overview and writes a
        detailed JSON diagnosis to the current directory (or ``output_dir``).
        Use ``command`` to run a specific command in debug mode and capture
        stdout/stderr to log files. Use ``plugin`` to scope diagnostics to a
        specific plugin.

        Args:
            command: Command to run in debug mode; results written to a log
                file (e.g. ``"force:org:list --all"``).
            plugin: Specific plugin on which to run diagnostics
                (e.g. ``"@salesforce/plugin-source"``).
            output_dir: Directory to save created files instead of the
                current working directory.
            create_issue: Create a new GitHub issue and attach diagnostic
                results.
            timeout: Subprocess timeout in seconds (default 120).

        Returns:
            Diagnostic result dict.
        """
        args = ["doctor"]

        if command:
            args += ["--command", command]

        if plugin:
            args += ["--plugin", plugin]

        if output_dir:
            args += ["--output-dir", str(output_dir)]

        if create_issue:
            args.append("--create-issue")

        return self._run_capturing(
            args,
            label="Running SF CLI doctor diagnostics",
            timeout=timeout,
            include_target_org=False,
            include_api_version=False,
        )
