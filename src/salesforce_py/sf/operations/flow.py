"""SF CLI flow command wrappers."""

from pathlib import Path
from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFFlowOperations(SFBaseOperations):
    """Wraps ``sf flow`` commands for testing flows in an org."""

    def run_test(
        self,
        class_names: list[str] | None = None,
        tests: list[str] | None = None,
        test_level: str | None = None,
        code_coverage: bool = False,
        synchronous: bool = False,
        result_format: str | None = None,
        output_dir: Path | None = None,
        concise: bool = False,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Invoke flow tests in an org.

        Runs asynchronously by default, returning a test run ID immediately.
        Use ``synchronous=True`` to block until tests complete (subject to
        ``timeout``). Use :meth:`get_test` with the returned run ID to fetch
        results from an async run.

        ``class_names`` and ``tests`` are mutually exclusive.

        Args:
            class_names: Flow names whose tests to run. Cannot be used with
                ``tests``.
            tests: Specific flow test names to run (e.g.
                ``["Flow1.Test1", "Flow2.Test2"]``). Cannot be used with
                ``class_names``.
            test_level: Test execution scope. One of ``RunLocalTests``,
                ``RunAllTestsInOrg``, ``RunSpecifiedTests``. Defaults to
                ``RunLocalTests``.
            code_coverage: Retrieve code coverage results alongside test
                results.
            synchronous: Run tests synchronously; blocks until complete or
                ``timeout`` is reached.
            result_format: Output format — ``human``, ``tap``, ``junit``, or
                ``json``. Defaults to ``human``.
            output_dir: Directory in which to store test result files.
            concise: Display only failed results (human format only).
            timeout: Subprocess timeout in seconds (default 600).

        Returns:
            Test run result dict, or a dict containing the async test run ID
            when running asynchronously.
        """
        args = ["flow", "run", "test"]

        if class_names:
            for name in class_names:
                args += ["--class-names", name]

        if tests:
            for test in tests:
                args += ["--tests", test]

        if test_level:
            args += ["--test-level", test_level]

        if code_coverage:
            args.append("--code-coverage")

        if synchronous:
            args.append("--synchronous")

        if result_format:
            args += ["--result-format", result_format]

        if output_dir:
            args += ["--output-dir", str(output_dir)]

        if concise:
            args.append("--concise")

        return self._run_capturing(
            args,
            label="Running flow tests",
            timeout=timeout,
        )

    def get_test(
        self,
        test_run_id: str,
        code_coverage: bool = False,
        result_format: str | None = None,
        output_dir: Path | None = None,
        concise: bool = False,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """Display test results for a specific asynchronous flow test run.

        Args:
            test_run_id: ID of the test run, as returned by :meth:`run_test`.
            code_coverage: Retrieve code coverage results alongside test
                results. Use with ``result_format`` to include coverage in
                output.
            result_format: Output format — ``human``, ``tap``, ``junit``, or
                ``json``. Defaults to ``human``.
            output_dir: Directory in which to save test result files.
            concise: Display only failed results (human format only).
            timeout: Subprocess timeout in seconds (default 120).

        Returns:
            Test result dict.
        """
        args = ["flow", "get", "test", "--test-run-id", test_run_id]

        if code_coverage:
            args.append("--code-coverage")

        if result_format:
            args += ["--result-format", result_format]

        if output_dir:
            args += ["--output-dir", str(output_dir)]

        if concise:
            args.append("--concise")

        return self._run_capturing(
            args,
            label=f"Getting flow test results for run {test_run_id}",
            timeout=timeout,
        )
