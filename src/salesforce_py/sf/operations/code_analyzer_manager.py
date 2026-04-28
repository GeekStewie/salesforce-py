"""SF CLI Code Analyzer plugin installation and configuration helpers."""

import logging
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

try:
    from ruamel.yaml import YAML as _YAML

    _RUAMEL_AVAILABLE = True
except ImportError:
    _RUAMEL_AVAILABLE = False


def _require_ruamel() -> None:
    if not _RUAMEL_AVAILABLE:
        raise ImportError(
            "ruamel.yaml is required for SFCodeAnalyzerManager. "
            "Install it with: pip install 'salesforce-py[code-analyzer]'"
        )

from salesforce_py.exceptions import SalesforcePyError

_log = logging.getLogger(__name__)

_CODE_ANALYZER_PLUGIN = "code-analyzer"
_VERSION_RE = re.compile(r"^[A-Za-z0-9._-]+$")

# All engines recognised by Code Analyzer v5.
_VALID_ENGINES: frozenset[str] = frozenset(
    {"eslint", "retire-js", "regex", "flow", "pmd", "cpd", "sfge"}
)

# Default config file names checked automatically by the CLI.
_DEFAULT_CONFIG_NAMES: tuple[str, ...] = ("code-analyzer.yml", "code-analyzer.yaml")


def _yaml() -> "Any":
    """Return a ruamel YAML instance configured for round-trip editing."""
    _require_ruamel()
    y = _YAML()
    y.default_flow_style = False
    y.preserve_quotes = True
    return y


def _load_config(path: Path) -> dict[str, Any]:
    """Load a YAML config file, returning an empty dict when the file is absent.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed dict (or empty dict).
    """
    if not path.exists():
        return {}
    y = _yaml()
    data = y.load(path)
    return data if isinstance(data, dict) else {}


def _save_config(path: Path, data: dict[str, Any]) -> None:
    """Write *data* to *path* as YAML, creating parent directories as needed.

    Args:
        path: Destination file path.
        data: Configuration dict to serialise.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    y = _yaml()
    with path.open("w", encoding="utf-8") as fh:
        y.dump(data, fh)


class SFCodeAnalyzerManager:
    """Manage the SF CLI Code Analyzer plugin installation and configuration.

    This class is standalone — it does not require an org connection and does
    not extend :class:`SFBaseOperations`.  Instantiate it independently::

        manager = SFCodeAnalyzerManager()
        if not manager.is_installed():
            manager.install()
        manager.write_config(
            disabled_engines=["flow", "pmd", "cpd", "sfge"],
            log_folder="/tmp/ca-logs",
            ignores_files=["**/node_modules/", "**/*.test.js"],
        )
    """

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def is_installed(self) -> bool:
        """Return True if the Code Analyzer plugin is installed in SF CLI.

        Checks for the ``sf code-analyzer`` sub-command by running
        ``sf code-analyzer --help``.

        Returns:
            True when the plugin is available.
        """
        if shutil.which("sf") is None:
            return False
        try:
            result = subprocess.run(
                "sf code-analyzer --help",
                shell=True,
                capture_output=True,
                text=True,
                timeout=15,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            return False

    def get_installed_version(self) -> str | None:
        """Return the installed Code Analyzer version string, or None.

        Parses the output of ``sf plugins --core`` to find the version entry
        for the ``code-analyzer`` plugin.

        Returns:
            Version string such as ``"5.2.2"`` or None when not installed.
        """
        try:
            result = subprocess.run(
                "sf plugins --core",
                shell=True,
                capture_output=True,
                text=True,
                timeout=15,
            )
            for line in result.stdout.splitlines():
                if "code-analyzer" in line:
                    # Typical format: "code-analyzer 5.2.2 (5.2.2)"
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        return parts[1]
        except (subprocess.TimeoutExpired, OSError):
            pass
        return None

    # ------------------------------------------------------------------
    # Plugin lifecycle
    # ------------------------------------------------------------------

    def install(
        self,
        version: str | None = None,
        timeout: int = 300,
    ) -> None:
        """Install the Code Analyzer plugin into SF CLI.

        Runs ``sf plugins install code-analyzer[@<version>]``.  Calling this
        on an already-installed plugin updates it to the specified (or latest)
        version.

        Args:
            version: Specific release to install, e.g. ``"5.2.2"``.  When
                None (default), the latest release is installed.
            timeout: Subprocess timeout in seconds (default 300).

        Raises:
            SalesforcePyError: When SF CLI is not found, the version string is
                invalid, or the install command fails.
        """
        if shutil.which("sf") is None:
            raise SalesforcePyError(
                "SF CLI not found on PATH: {'hint': 'Install SF CLI first'}"
            )

        if version is not None and not _VERSION_RE.match(version):
            raise SalesforcePyError(
                f"Invalid Code Analyzer version string: {{'version': '{version}'}}"
            )

        package = (
            f"{_CODE_ANALYZER_PLUGIN}@{version}" if version else _CODE_ANALYZER_PLUGIN
        )
        label = f"version {version}" if version else "latest"
        _log.info(f"Installing Code Analyzer plugin ({label})...")
        try:
            proc = subprocess.run(
                f"sf plugins install {package}",
                shell=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise SalesforcePyError(
                f"Code Analyzer install timed out after {timeout}s"
            ) from exc

        if proc.returncode != 0:
            raise SalesforcePyError(
                f"Code Analyzer plugin installation failed: {{'exit_code': {proc.returncode}, 'package': '{package}'}}"
            )
        _log.info(f"Code Analyzer plugin {label} installed")

    def update(
        self,
        version: str | None = None,
        timeout: int = 300,
    ) -> None:
        """Update the Code Analyzer plugin to the latest (or a specific) release.

        Equivalent to re-running :meth:`install`; the SF CLI ``plugins install``
        command acts as an update when the plugin is already installed.

        Args:
            version: Specific version to update to.  None updates to the
                latest release.
            timeout: Subprocess timeout in seconds (default 300).
        """
        self.install(version=version, timeout=timeout)

    def uninstall(self, timeout: int = 60) -> None:
        """Uninstall the Code Analyzer plugin from SF CLI.

        Runs ``sf plugins uninstall code-analyzer``.

        Args:
            timeout: Subprocess timeout in seconds (default 60).

        Raises:
            SalesforcePyError: When SF CLI is not found or the uninstall fails.
        """
        if shutil.which("sf") is None:
            raise SalesforcePyError("SF CLI not found on PATH")

        if not self.is_installed():
            _log.warning(
                "Code Analyzer plugin is not installed — nothing to uninstall"
            )
            return

        _log.info("Uninstalling Code Analyzer plugin...")
        try:
            proc = subprocess.run(
                f"sf plugins uninstall {_CODE_ANALYZER_PLUGIN}",
                shell=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise SalesforcePyError(
                f"Code Analyzer uninstall timed out after {timeout}s"
            ) from exc

        if proc.returncode != 0:
            raise SalesforcePyError(
                f"Code Analyzer plugin uninstall failed: {{'exit_code': {proc.returncode}}}"
            )
        _log.info("Code Analyzer plugin uninstalled")

    # ------------------------------------------------------------------
    # Configuration — helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_engines(engines: list[str]) -> None:
        """Raise SalesforcePyError when any engine name is not recognised.

        Args:
            engines: Engine names to validate.

        Raises:
            SalesforcePyError: When unknown names are present.
        """
        unknown = [e for e in engines if e not in _VALID_ENGINES]
        if unknown:
            raise SalesforcePyError(
                f"Unknown Code Analyzer engine(s): {{'unknown': {unknown}, 'valid': {sorted(_VALID_ENGINES)}}}"
            )

    # ------------------------------------------------------------------
    # Configuration — read
    # ------------------------------------------------------------------

    def read_config(
        self,
        config_path: str | Path | None = None,
    ) -> dict[str, Any]:
        """Read and return the parsed contents of a ``code-analyzer.yml`` file.

        Args:
            config_path: Path to the config file.  When None, the method
                looks for ``code-analyzer.yml`` then ``code-analyzer.yaml``
                in the current directory.

        Returns:
            Parsed configuration dict, or an empty dict when no file is found.
        """
        if config_path is not None:
            return _load_config(Path(config_path))

        for name in _DEFAULT_CONFIG_NAMES:
            candidate = Path.cwd() / name
            if candidate.exists():
                return _load_config(candidate)
        return {}

    # ------------------------------------------------------------------
    # Configuration — write
    # ------------------------------------------------------------------

    def write_config(
        self,
        output_path: str | Path | None = None,
        *,
        overwrite: bool = False,
        # Top-level fields
        config_root: str | None = None,
        log_folder: str | None = None,
        log_level: int | str | None = None,
        # Engine toggles
        disabled_engines: list[str] | None = None,
        # ignores
        ignores_files: list[str] | None = None,
        # Rule overrides: {engine: {rule: {severity, tags, disabled}}}
        rules: dict[str, dict[str, dict[str, Any]]] | None = None,
        # Engine config: {engine: {property: value}}
        engines: dict[str, dict[str, Any]] | None = None,
    ) -> Path:
        """Write a ``code-analyzer.yml`` configuration file.

        Creates a new file from the provided parameters.  Use
        :meth:`update_config` to merge changes into an existing file.

        Top-level fields (``config_root``, ``log_folder``, ``log_level``)
        correspond directly to the Code Analyzer top-level configuration
        reference.

        Args:
            output_path: Destination path (default: ``code-analyzer.yml`` in
                the current directory).
            overwrite: When False (default), raise if the file already exists.
            config_root: Absolute folder path to which other relative paths
                in the config are resolved.
            log_folder: Folder for Code Analyzer log files.
            log_level: Log verbosity — ``1``/``"Error"``, ``2``/``"Warn"``,
                ``3``/``"Info"``, ``4``/``"Debug"`` (default), ``5``/``"Fine"``.
            disabled_engines: Engine names to set ``disable_engine: true``.
                Valid names: ``eslint``, ``retire-js``, ``regex``, ``flow``,
                ``pmd``, ``cpd``, ``sfge``.
            ignores_files: Glob patterns for files to exclude from scanning,
                e.g. ``["**/node_modules/", "**/*.test.js"]``.
            rules: Rule override dict in the form
                ``{engine: {rule_name: {severity, tags, disabled}}}``.
                Example::

                    {
                        "eslint": {"sort-vars": {"severity": "Info", "tags": ["Recommended"]}},
                        "regex": {"NoTrailingWhiteSpace": {"disabled": True}},
                    }

            engines: Engine-specific configuration in the form
                ``{engine: {property: value}}``.  May include ``disable_engine``
                and any engine-specific properties (e.g. ``eslint_config_file``,
                ``custom_rules``).

        Returns:
            Resolved path to the written file.

        Raises:
            SalesforcePyError: When an unknown engine name is supplied or the file
                already exists and ``overwrite=False``.
        """
        target = Path(output_path or "code-analyzer.yml").resolve()

        if target.exists() and not overwrite:
            raise SalesforcePyError(
                f"Config file already exists: {{'path': '{target}', 'hint': 'Pass overwrite=True to replace it'}}"
            )

        if disabled_engines:
            self._validate_engines(disabled_engines)
        if engines:
            self._validate_engines(list(engines.keys()))

        data: dict[str, Any] = {}

        if config_root is not None:
            data["config_root"] = config_root
        if log_folder is not None:
            data["log_folder"] = log_folder
        if log_level is not None:
            data["log_level"] = log_level

        if ignores_files:
            data["ignores"] = {"files": list(ignores_files)}

        if rules:
            data["rules"] = rules

        # Merge disabled_engines into engines block
        merged_engines: dict[str, Any] = dict(engines or {})
        for engine in disabled_engines or []:
            merged_engines.setdefault(engine, {})["disable_engine"] = True

        if merged_engines:
            data["engines"] = merged_engines

        _save_config(target, data)
        _log.info(f"Written {target}")
        return target

    # ------------------------------------------------------------------
    # Configuration — update
    # ------------------------------------------------------------------

    def update_config(
        self,
        config_path: str | Path | None = None,
        *,
        config_root: str | None = None,
        log_folder: str | None = None,
        log_level: int | str | None = None,
        disabled_engines: list[str] | None = None,
        enabled_engines: list[str] | None = None,
        ignores_files_add: list[str] | None = None,
        ignores_files_remove: list[str] | None = None,
        rules: dict[str, dict[str, dict[str, Any]]] | None = None,
        engines: dict[str, dict[str, Any]] | None = None,
    ) -> Path:
        """Merge changes into an existing ``code-analyzer.yml`` file.

        Reads the existing file, applies the requested changes, then writes it
        back.  Creates the file if it does not yet exist.

        The merge strategy is shallow for top-level keys (existing values are
        replaced) and deep for ``rules`` and ``engines`` (nested keys are
        merged, not replaced).  File globs in ``ignores.files`` are handled
        with explicit add/remove lists.

        Args:
            config_path: Path to the config file.  When None, looks for
                ``code-analyzer.yml`` in the current directory.
            config_root: Replaces the ``config_root`` field when supplied.
            log_folder: Replaces the ``log_folder`` field when supplied.
            log_level: Replaces the ``log_level`` field when supplied.
            disabled_engines: Engine names to set ``disable_engine: true``.
            enabled_engines: Engine names to remove ``disable_engine: true``
                from, effectively re-enabling them.
            ignores_files_add: Glob patterns to add to ``ignores.files``.
            ignores_files_remove: Glob patterns to remove from
                ``ignores.files``.
            rules: Rule overrides to deep-merge into the ``rules`` section.
            engines: Engine config to deep-merge into the ``engines`` section.

        Returns:
            Resolved path of the written file.

        Raises:
            SalesforcePyError: When unknown engine names are supplied.
        """
        if disabled_engines:
            self._validate_engines(disabled_engines)
        if enabled_engines:
            self._validate_engines(enabled_engines)
        if engines:
            self._validate_engines(list(engines.keys()))

        target = Path(config_path or "code-analyzer.yml").resolve()
        data = _load_config(target)

        if config_root is not None:
            data["config_root"] = config_root
        if log_folder is not None:
            data["log_folder"] = log_folder
        if log_level is not None:
            data["log_level"] = log_level

        # ignores.files
        current_files: list[str] = []
        if isinstance(data.get("ignores"), dict):
            current_files = list(data["ignores"].get("files") or [])
        for pattern in ignores_files_add or []:
            if pattern not in current_files:
                current_files.append(pattern)
        for pattern in ignores_files_remove or []:
            current_files = [f for f in current_files if f != pattern]
        if (
            current_files
            or ignores_files_add is not None
            or ignores_files_remove is not None
        ):
            data.setdefault("ignores", {})
            if isinstance(data["ignores"], dict):
                data["ignores"]["files"] = current_files

        # rules — deep merge
        if rules:
            _raw_rules = data.get("rules") or {}
            existing_rules: dict[str, Any] = (
                _raw_rules if isinstance(_raw_rules, dict) else {}
            )
            for engine, rule_map in rules.items():
                engine_rules = existing_rules.setdefault(engine, {})
                if not isinstance(engine_rules, dict):
                    engine_rules = {}
                    existing_rules[engine] = engine_rules
                for rule_name, overrides in rule_map.items():
                    rule_entry = engine_rules.setdefault(rule_name, {})
                    if not isinstance(rule_entry, dict):
                        rule_entry = {}
                        engine_rules[rule_name] = rule_entry
                    rule_entry.update(overrides)
            data["rules"] = existing_rules

        # engines — deep merge then apply disable/enable toggles
        _raw_engines = data.get("engines") or {}
        merged_engines: dict[str, Any] = (
            _raw_engines if isinstance(_raw_engines, dict) else {}
        )

        if engines:
            for engine, props in engines.items():
                eng_entry = merged_engines.setdefault(engine, {})
                if not isinstance(eng_entry, dict):
                    eng_entry = {}
                    merged_engines[engine] = eng_entry
                eng_entry.update(props)

        for engine in disabled_engines or []:
            merged_engines.setdefault(engine, {})["disable_engine"] = True

        for engine in enabled_engines or []:
            if engine in merged_engines and isinstance(merged_engines[engine], dict):
                merged_engines[engine].pop("disable_engine", None)
                if not merged_engines[engine]:
                    del merged_engines[engine]

        if merged_engines:
            data["engines"] = merged_engines
        elif "engines" in data:
            del data["engines"]

        _save_config(target, data)
        _log.info(f"Updated {target}")
        return target

    # ------------------------------------------------------------------
    # Configuration — delete
    # ------------------------------------------------------------------

    def delete_config(
        self,
        config_path: str | Path | None = None,
        *,
        no_prompt: bool = False,
    ) -> bool:
        """Delete a ``code-analyzer.yml`` configuration file.

        Args:
            config_path: Path to the config file.  When None, looks for
                ``code-analyzer.yml`` then ``code-analyzer.yaml`` in the
                current directory.
            no_prompt: When True, skip the existence check and silently
                return False if the file is not found (useful in automation).

        Returns:
            True when the file was deleted, False when it was not found.

        Raises:
            SalesforcePyError: When the file cannot be deleted.
        """
        if config_path is not None:
            target: Path | None = Path(config_path).resolve()
        else:
            target = None
            for name in _DEFAULT_CONFIG_NAMES:
                candidate = Path.cwd() / name
                if candidate.exists():
                    target = candidate
                    break

        if target is None or not target.exists():
            if not no_prompt:
                _log.warning(
                    "No Code Analyzer config file found — nothing to delete"
                )
            return False

        try:
            target.unlink()
        except OSError as exc:
            raise SalesforcePyError(
                f"Failed to delete Code Analyzer config file: {{'path': '{target}', 'error': '{exc}'}}"
            ) from exc

        _log.info(f"Deleted {target}")
        return True

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        """Return a dict summarising the Code Analyzer plugin installation.

        Returns:
            Dict with keys ``installed: bool`` and ``version: str | None``.
        """
        return {
            "installed": self.is_installed(),
            "version": self.get_installed_version(),
        }
