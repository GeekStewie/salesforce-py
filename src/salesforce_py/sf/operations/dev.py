"""SF CLI dev command wrappers."""

from pathlib import Path
from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFDevOperations(SFBaseOperations):
    """Wraps ``sf dev`` commands for Salesforce CLI plugin development.

    All commands operate on local project files; none require an org
    connection, so ``include_target_org=False`` and
    ``include_api_version=False`` are set throughout.
    """

    def audit_messages(
        self,
        project_dir: Path | None = None,
        messages_dir: Path | None = None,
        source_dir: Path | None = None,
    ) -> dict[str, Any]:
        """Audit messages in a plugin's messages directory.

        Locates unused messages and missing messages referenced in source.

        Args:
            project_dir: Location of the project to audit. Defaults to ``.``.
            messages_dir: Directory containing message files. Defaults to
                ``messages``.
            source_dir: Directory containing plugin source. Defaults to
                ``src``.

        Returns:
            Audit result dict.
        """
        args = ["dev", "audit", "messages"]

        if project_dir:
            args += ["--project-dir", str(project_dir)]

        if messages_dir:
            args += ["--messages-dir", str(messages_dir)]

        if source_dir:
            args += ["--source-dir", str(source_dir)]

        return self._run_capturing(
            args,
            label="Auditing plugin messages",
            include_target_org=False,
            include_api_version=False,
        )

    def convert_messages(
        self,
        file_name: str,
        project_dir: Path | None = None,
    ) -> dict[str, Any]:
        """Convert a .json messages file into Markdown.

        Preserves the original ``.json`` file and creates a new ``.md`` file
        with standard headers. Review the Markdown file and delete the
        ``.json`` file manually once satisfied.

        Args:
            file_name: Filename to convert (e.g. ``my-command.json``).
            project_dir: Project directory. Defaults to ``.``.

        Returns:
            Conversion result dict.
        """
        args = ["dev", "convert", "messages", "--file-name", file_name]

        if project_dir:
            args += ["--project-dir", str(project_dir)]

        return self._run_capturing(
            args,
            label=f"Converting messages file {file_name}",
            include_target_org=False,
            include_api_version=False,
        )

    def convert_script(self, script: Path) -> dict[str, Any]:
        """Convert a script file from deprecated sfdx-style to sf-style commands.

        Creates a new file with ``-converted`` appended to the original name.
        This command is interactive and prompts for each replacement — run it
        from a terminal session, not an automated pipeline.

        Args:
            script: Path to the script file to convert.

        Returns:
            Raw stdout under the ``output`` key (no JSON envelope).
        """
        return self._run_capturing(
            ["dev", "convert", "script", "--script", str(script)],
            label=f"Converting script {script.name}",
            include_target_org=False,
            include_api_version=False,
            include_json=False,
        )

    def generate_command(
        self,
        name: str,
        force: bool = False,
        dry_run: bool = False,
        nuts: bool = True,
        unit: bool = True,
    ) -> dict[str, Any]:
        """Generate a new sf command inside the current plugin directory.

        Creates source files, message files, and test files. Must be run
        from within a plugin directory.

        Args:
            name: Command name using colon-separated parts
                (e.g. ``my:exciting:command``).
            force: Overwrite existing files.
            dry_run: Display changes without writing to disk.
            nuts: Generate a NUT test file (default ``True``).
            unit: Generate a unit test file (default ``True``).

        Returns:
            Raw stdout under the ``output`` key (no JSON envelope).
        """
        args = ["dev", "generate", "command", "--name", name]

        if force:
            args.append("--force")

        if dry_run:
            args.append("--dry-run")

        if not nuts:
            args.append("--no-nuts")

        if not unit:
            args.append("--no-unit")

        return self._run_capturing(
            args,
            label=f"Generating command {name}",
            include_target_org=False,
            include_api_version=False,
            include_json=False,
        )

    def generate_flag(self, dry_run: bool = False) -> dict[str, Any]:
        """Generate a flag for an existing command.

        Interactive command — discovers available commands and prompts for
        flag properties. Must be run from a terminal session.

        Args:
            dry_run: Print generated flag code instead of writing to the
                command file.

        Returns:
            Raw stdout under the ``output`` key (no JSON envelope).
        """
        args = ["dev", "generate", "flag"]

        if dry_run:
            args.append("--dry-run")

        return self._run_capturing(
            args,
            label="Generating command flag",
            include_target_org=False,
            include_api_version=False,
            include_json=False,
        )

    def generate_plugin(self, dry_run: bool = False) -> dict[str, Any]:
        """Generate a new sf plugin.

        Interactive command — prompts for plugin name, description, author,
        and coverage target, then clones the plugin template and runs
        ``yarn install``. Must be run from a terminal session.

        Args:
            dry_run: Display changes without writing to disk.

        Returns:
            Raw stdout under the ``output`` key (no JSON envelope).
        """
        args = ["dev", "generate", "plugin"]

        if dry_run:
            args.append("--dry-run")

        return self._run_capturing(
            args,
            label="Generating sf plugin",
            include_target_org=False,
            include_api_version=False,
            include_json=False,
        )
