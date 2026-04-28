"""SF CLI code-analyzer command wrappers."""

from pathlib import Path
from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFCodeAnalyzerOperations(SFBaseOperations):
    """Wraps ``sf code-analyzer`` commands for static code analysis.

    These commands operate on local project files; no org connection is
    required, so all methods set ``include_target_org=False``.
    """

    def config(
        self,
        rule_selector: list[str] | None = None,
        workspace: list[str] | None = None,
        target: list[str] | None = None,
        config_file: Path | None = None,
        output_file: Path | None = None,
        include_unmodified_rules: bool = False,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """Output the current state of Code Analyzer configuration.

        Args:
            rule_selector: One or more rule selectors (engine name, severity,
                tag, rule name, or combined expressions). Defaults to ``all``.
            workspace: Folders, files, or glob patterns that make up the
                workspace. Repeat to add multiple paths.
            target: Subset of files within the workspace to target. Repeat
                to add multiple paths.
            config_file: Path to a custom ``code-analyzer.yml`` configuration
                file. Defaults to ``./code-analyzer.yml`` when present.
            output_file: Write the configuration state to this YAML file
                instead of (or in addition to) the terminal.
            include_unmodified_rules: Include rules with default (unmodified)
                values in the output, not just overridden rules.
            timeout: Subprocess timeout in seconds.

        Returns:
            Parsed configuration state dict.
        """
        args = ["code-analyzer", "config"]

        for selector in rule_selector or []:
            args += ["--rule-selector", selector]

        for ws in workspace or []:
            args += ["--workspace", ws]

        for tgt in target or []:
            args += ["--target", tgt]

        if config_file:
            args += ["--config-file", str(config_file)]

        if output_file:
            args += ["--output-file", str(output_file)]

        if include_unmodified_rules:
            args.append("--include-unmodified-rules")

        return self._run_capturing(
            args,
            label="Fetching code-analyzer config",
            timeout=timeout,
            include_target_org=False,
        )

    def rules(
        self,
        rule_selector: list[str] | None = None,
        workspace: list[str] | None = None,
        target: list[str] | None = None,
        config_file: Path | None = None,
        output_file: list[Path] | None = None,
        view: str | None = None,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """List the rules available to analyze code.

        Args:
            rule_selector: One or more rule selectors. Defaults to
                ``Recommended``.
            workspace: Workspace folders, files, or glob patterns.
            target: Subset of workspace files to target.
            config_file: Path to a custom ``code-analyzer.yml`` file.
            output_file: One or more file paths to write the rules to.
                Extension determines format: ``.json`` or ``.csv``.
            view: Terminal display format: ``table`` or ``detail``.
            timeout: Subprocess timeout in seconds.

        Returns:
            Parsed rules list dict.
        """
        args = ["code-analyzer", "rules"]

        for selector in rule_selector or []:
            args += ["--rule-selector", selector]

        for ws in workspace or []:
            args += ["--workspace", ws]

        for tgt in target or []:
            args += ["--target", tgt]

        if config_file:
            args += ["--config-file", str(config_file)]

        for out in output_file or []:
            args += ["--output-file", str(out)]

        if view:
            args += ["--view", view]

        return self._run_capturing(
            args,
            label="Listing code-analyzer rules",
            timeout=timeout,
            include_target_org=False,
        )

    def run(
        self,
        rule_selector: list[str] | None = None,
        workspace: list[str] | None = None,
        target: list[str] | None = None,
        config_file: Path | None = None,
        output_file: list[Path] | None = None,
        view: str | None = None,
        severity_threshold: str | int | None = None,
        no_suppressions: bool = False,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Analyze code with a selection of rules.

        Args:
            rule_selector: One or more rule selectors (engine, severity, tag,
                rule name, or combinations). Defaults to ``Recommended``.
            workspace: Workspace root(s). Defaults to the current folder.
            target: Subset of workspace files to analyze. Defaults to the
                entire workspace.
            config_file: Path to a custom ``code-analyzer.yml`` file.
            output_file: One or more output file paths. Extension determines
                format: ``.csv``, ``.html``/``.htm``, ``.json``,
                ``.sarif``/``.sarif.json``, or ``.xml``.
            view: Terminal display format: ``table`` or ``detail``.
            severity_threshold: Severity level at or above which violations
                cause a non-zero exit code. Accepts ``2``/``"High"``,
                ``3``/``"Moderate"``, etc.
            no_suppressions: Ignore all inline suppression markers and report
                all violations.
            timeout: Subprocess timeout in seconds.

        Returns:
            Analysis result dict containing violation summaries.
        """
        args = ["code-analyzer", "run"]

        for selector in rule_selector or []:
            args += ["--rule-selector", selector]

        for ws in workspace or []:
            args += ["--workspace", ws]

        for tgt in target or []:
            args += ["--target", tgt]

        if config_file:
            args += ["--config-file", str(config_file)]

        for out in output_file or []:
            args += ["--output-file", str(out)]

        if view:
            args += ["--view", view]

        if severity_threshold is not None:
            args += ["--severity-threshold", str(severity_threshold)]

        if no_suppressions:
            args.append("--no-suppressions")

        return self._run_capturing(
            args,
            label="Running code-analyzer",
            timeout=timeout,
            include_target_org=False,
        )
