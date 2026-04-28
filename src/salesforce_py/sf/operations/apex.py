"""SF CLI apex command wrappers."""

from pathlib import Path
from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFApexOperations(SFBaseOperations):
    """Wraps ``sf apex`` commands.

    Covers anonymous execution, test running, log retrieval and tailing.
    """

    # ------------------------------------------------------------------
    # Anonymous execution
    # ------------------------------------------------------------------

    def run(self, file_path: Path, timeout: int = 120) -> dict[str, Any]:
        """Execute anonymous Apex code from a local file.

        ``sf apex run`` only accepts ``--file``; inline code strings require
        interactive stdin which is not supported in subprocess mode.

        Args:
            file_path: Path to the ``.apex`` or ``.cls`` file to execute.
            timeout: Subprocess timeout in seconds.

        Returns:
            Result dict with ``success``, ``compiled``, ``compileProblem``,
            ``exceptionMessage``, ``exceptionStackTrace``, and ``logs``.
        """
        return self._run_capturing(
            ["apex", "run", "--file", str(file_path)],
            label=f"Running Apex file {file_path.name}",
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Test execution
    # ------------------------------------------------------------------

    def run_tests(
        self,
        class_names: list[str] | None = None,
        suite_names: list[str] | None = None,
        tests: list[str] | None = None,
        test_level: str | None = None,
        code_coverage: bool = False,
        detailed_coverage: bool = False,
        synchronous: bool = False,
        wait: int | None = None,
        poll_interval: int | None = None,
        result_format: str = "json",
        output_dir: Path | None = None,
        concise: bool = False,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Invoke Apex tests in the org.

        Specify tests via ``class_names``, ``suite_names``, or ``tests`` (mutually
        exclusive per SF CLI rules). Use ``test_level`` to run broader sets.

        Args:
            class_names: Apex test class names to run.
            suite_names: Apex test suite names to run.
            tests: Specific test methods in ``Class.method`` or ``ns.Class.method``
                notation; a class name without a method runs all its methods.
            test_level: One of ``RunLocalTests``, ``RunAllTestsInOrg``,
                ``RunSpecifiedTests``.
            code_coverage: Retrieve code coverage results.
            detailed_coverage: Display detailed code coverage per test method
                (requires ``code_coverage=True`` and human result format).
            synchronous: Run tests synchronously from a single class.
            wait: Minutes to wait for async tests to complete before returning.
            poll_interval: Seconds between polling retries.
            result_format: Output format: ``json``, ``human``, ``tap``,
                or ``junit``. Defaults to ``json`` for programmatic use.
            output_dir: Directory to write test result files into.
            concise: Show only failed test results (human format only).
            timeout: Subprocess timeout in seconds.

        Returns:
            Test result dict, or a dict containing a ``testRunId`` when the
            tests have not yet completed.
        """
        args = ["apex", "run", "test", "--result-format", result_format]

        if test_level:
            args += ["--test-level", test_level]

        if class_names:
            for name in class_names:
                args += ["--class-names", name]

        if suite_names:
            for name in suite_names:
                args += ["--suite-names", name]

        if tests:
            for test in tests:
                args += ["--tests", test]

        if code_coverage:
            args.append("--code-coverage")

        if detailed_coverage:
            args.append("--detailed-coverage")

        if synchronous:
            args.append("--synchronous")

        if wait is not None:
            args += ["--wait", str(wait)]

        if poll_interval is not None:
            args += ["--poll-interval", str(poll_interval)]

        if output_dir:
            args += ["--output-dir", str(output_dir)]

        if concise:
            args.append("--concise")

        return self._run_capturing(
            args,
            label="Running Apex tests",
            timeout=timeout,
        )

    def get_test_results(
        self,
        test_run_id: str,
        code_coverage: bool = False,
        detailed_coverage: bool = False,
        result_format: str = "json",
        output_dir: Path | None = None,
        concise: bool = False,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Display test results for a specific asynchronous test run.

        Args:
            test_run_id: ID of the test run (from ``run_tests``).
            code_coverage: Retrieve code coverage results.
            detailed_coverage: Display detailed coverage per test method.
            result_format: Output format: ``json``, ``human``, ``tap``,
                or ``junit``.
            output_dir: Directory to write result files into.
            concise: Show only failed test results (human format only).
            timeout: Subprocess timeout in seconds.

        Returns:
            Test result dict.
        """
        args = [
            "apex",
            "get",
            "test",
            "--test-run-id",
            test_run_id,
            "--result-format",
            result_format,
        ]

        if code_coverage:
            args.append("--code-coverage")

        if detailed_coverage:
            args.append("--detailed-coverage")

        if output_dir:
            args += ["--output-dir", str(output_dir)]

        if concise:
            args.append("--concise")

        return self._run_capturing(
            args,
            label=f"Fetching test results {test_run_id}",
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Log management
    # ------------------------------------------------------------------

    def list_logs(self) -> list[dict[str, Any]]:
        """Display a list of IDs and general information about debug logs.

        Returns:
            List of log summary dicts.
        """
        result = self._run(["apex", "list", "log"])
        if isinstance(result, list):
            return result
        return result.get("logs", [])

    def get_log(
        self,
        log_id: str | None = None,
        number: int | None = None,
        output_dir: Path | None = None,
    ) -> dict[str, Any]:
        """Fetch one or more debug logs from the org.

        Passing neither ``log_id`` nor ``number`` returns the most recent log.

        Args:
            log_id: ID of a specific log to fetch.
            number: Number of the most recent logs to fetch.
            output_dir: Directory to save the log files into.

        Returns:
            Result dict. When ``output_dir`` is given, contains file paths.
            Otherwise contains ``log`` with the raw log text for a single log,
            or ``logs`` for multiple.
        """
        args = ["apex", "get", "log"]

        if log_id:
            args += ["--log-id", log_id]

        if number is not None:
            args += ["--number", str(number)]

        if output_dir:
            args += ["--output-dir", str(output_dir)]

        return self._run_capturing(args, label="Fetching Apex log")

    def tail_log(
        self,
        debug_level: str | None = None,
        color: bool = False,
        skip_trace_flag: bool = False,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Activate debug logging and stream logs to the terminal.

        This command does not support ``--json`` and runs until interrupted or
        the timeout expires. The raw stdout is returned under the ``output`` key.

        Args:
            debug_level: Debug level to set on the DEVELOPER_LOG trace flag.
            color: Apply default colours to noteworthy log lines.
            skip_trace_flag: Skip trace flag setup; assumes one is already set.
            timeout: Subprocess timeout in seconds (default 600).

        Returns:
            Dict with ``output`` containing the captured log text.
        """
        args = ["apex", "tail", "log"]

        if debug_level:
            args += ["--debug-level", debug_level]

        if color:
            args.append("--color")

        if skip_trace_flag:
            args.append("--skip-trace-flag")

        return self._run_capturing(
            args,
            label="Tailing Apex logs",
            timeout=timeout,
            include_json=False,
        )
