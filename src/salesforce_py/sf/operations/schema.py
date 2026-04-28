"""SF CLI schema command wrappers."""

from pathlib import Path
from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFSchemaOperations(SFBaseOperations):
    """Wraps ``sf schema generate`` commands for metadata source file generation.

    All ``generate field/platformevent/sobject`` commands are interactive and
    do not support ``--json``.  Only ``generate tab`` supports ``--json``.
    """

    def generate_field(
        self,
        label: str,
        object_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Generate metadata source files for a new custom field.

        Interactive command — prompts for additional field properties.

        Args:
            label: Human-readable label for the field.
            object_dir: Local path to the object's source directory (optional;
                the command prompts if omitted).

        Returns:
            Raw output dict (``{"output": ...}``).
        """
        args: list[str] = ["schema", "generate", "field", "--label", label]
        if object_dir is not None:
            args += ["--object", str(object_dir)]
        return self._run_capturing(
            args,
            label=f"Generating field '{label}'",
            include_target_org=False,
            include_api_version=False,
            include_json=False,
        )

    def generate_platformevent(self, label: str) -> dict[str, Any]:
        """Generate metadata source files for a new platform event.

        Interactive command — prompts for additional event properties.

        Args:
            label: Human-readable label for the platform event.

        Returns:
            Raw output dict (``{"output": ...}``).
        """
        return self._run_capturing(
            ["schema", "generate", "platformevent", "--label", label],
            label=f"Generating platform event '{label}'",
            include_target_org=False,
            include_api_version=False,
            include_json=False,
        )

    def generate_sobject(
        self,
        label: str,
        use_default_features: bool = False,
    ) -> dict[str, Any]:
        """Generate metadata source files for a new custom object.

        Interactive command — prompts for Name field and other properties
        unless ``use_default_features`` is set.

        Args:
            label: Human-readable label for the custom object.
            use_default_features: Enable all optional features without
                prompting (search, feeds, reports, history, activities,
                Bulk API, sharing, Streaming API).

        Returns:
            Raw output dict (``{"output": ...}``).
        """
        args: list[str] = ["schema", "generate", "sobject", "--label", label]
        if use_default_features:
            args.append("--use-default-features")
        return self._run_capturing(
            args,
            label=f"Generating custom object '{label}'",
            include_target_org=False,
            include_api_version=False,
            include_json=False,
        )

    def generate_tab(
        self,
        object_api_name: str,
        directory: str | Path,
        icon: int = 1,
    ) -> dict[str, Any]:
        """Generate metadata source files for a new custom tab.

        Args:
            object_api_name: API name of the custom object (must end in
                ``__c``, e.g. ``MyObject__c``).
            directory: Path to the ``tabs`` directory that will contain the
                generated source files.
            icon: Icon number 1–100 from the Lightning Design System custom
                icon set.

        Returns:
            Generation result dict.
        """
        return self._run_capturing(
            [
                "schema",
                "generate",
                "tab",
                "--object",
                object_api_name,
                "--directory",
                str(directory),
                "--icon",
                str(icon),
            ],
            label=f"Generating tab for '{object_api_name}'",
            include_target_org=False,
            include_api_version=False,
        )
