"""SF CLI logic command wrappers."""

from pathlib import Path
from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFLogicOperations(SFBaseOperations):
    """Wraps ``sf logic`` commands for running Apex and Flow tests together.

    These commands are a Beta Service as of the current SF CLI release.
    They provide a unified interface for running both Apex and Flow tests in
    a single invocation, unlike the separate ``sf apex run test`` and
    ``sf flow run test`` commands.
    """

    def run_test(
        self,
        tests: list[str] | None = None,
        class_names: list[str] | None = None,
        suite_names: list[str] | None = None,
        test_category: list[str] | None = None,
        test_level: str | None = None,
        code_coverage: bool = False,
        detailed_coverage: bool = False,
        synchronous: bool = False,
        wait: int | None = None,
        result_format: str | None = None,
        output_dir: Path | None = None,
        concise: bool = False,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Invoke tests for Apex and Flows in an org.

        Runs asynchronously by default, returning a test run ID immediately.
        Use :meth:`get_test` with that ID to fetch results. Pass
        ``synchronous=True`` to block until tests complete.

        ``tests``, ``class_names``, and ``suite_names`` are mutually
        exclusive — only one may be provided per call.

        For Flow tests in ``tests``, use the format
        ``FlowTesting.<flow-test-name>`` (e.g.
        ``"FlowTesting.Modify_Account_Desc.Modify_Account_Desc_TestAccountDescription"``).

        Args:
            tests: Specific Apex or Flow test names to run. Mutually
                exclusive with ``class_names`` and ``suite_names``.
            class_names: Apex test class names to run. Mutually exclusive
                with ``suite_names`` and ``tests``.
            suite_names: Apex test suite names to run. Mutually exclusive
                with ``class_names`` and ``tests``.
            test_category: Categories of tests to run — ``Apex``, ``Flow``,
                or both. Repeat to include multiple categories.
            test_level: Execution scope — ``RunLocalTests``,
                ``RunAllTestsInOrg``, or ``RunSpecifiedTests``. Defaults to
                ``RunLocalTests``.
            code_coverage: Retrieve code coverage results.
            detailed_coverage: Display detailed code coverage per test
                (human format only).
            synchronous: Run tests synchronously; blocks until complete or
                ``timeout`` is reached.
            wait: Streaming client socket timeout in minutes.
            result_format: Output format — ``human``, ``tap``, ``junit``,
                or ``json``. Defaults to ``human``.
            output_dir: Directory in which to store test run files.
            concise: Display only failed results (human format only).
            timeout: Subprocess timeout in seconds (default 600).

        Returns:
            Test run result dict, or a dict containing the async test run ID
            when running asynchronously.
        """
        args = ["logic", "run", "test"]

        if tests:
            for test in tests:
                args += ["--tests", test]

        if class_names:
            for name in class_names:
                args += ["--class-names", name]

        if suite_names:
            for name in suite_names:
                args += ["--suite-names", name]

        if test_category:
            for category in test_category:
                args += ["--test-category", category]

        if test_level:
            args += ["--test-level", test_level]

        if code_coverage:
            args.append("--code-coverage")

        if detailed_coverage:
            args.append("--detailed-coverage")

        if synchronous:
            args.append("--synchronous")

        if wait is not None:
            args += ["--wait", str(wait)]

        if result_format:
            args += ["--result-format", result_format]

        if output_dir:
            args += ["--output-dir", str(output_dir)]

        if concise:
            args.append("--concise")

        return self._run_capturing(
            args,
            label="Running logic tests",
            timeout=timeout,
        )

    def get_test(
        self,
        test_run_id: str,
        code_coverage: bool = False,
        detailed_coverage: bool = False,
        result_format: str | None = None,
        output_dir: Path | None = None,
        concise: bool = False,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """Get the results of a logic test run.

        Use the test run ID returned by :meth:`run_test` to fetch results
        from an asynchronous run.

        Args:
            test_run_id: ID of the test run.
            code_coverage: Retrieve code coverage results. Use with
                ``result_format`` to include coverage in output.
            detailed_coverage: Display detailed code coverage per test
                (human format only).
            result_format: Output format — ``human``, ``tap``, ``junit``,
                or ``json``. Defaults to ``human``.
            output_dir: Directory in which to store test result files.
            concise: Display only failed results (human format only).
            timeout: Subprocess timeout in seconds (default 120).

        Returns:
            Test result dict.
        """
        args = ["logic", "get", "test", "--test-run-id", test_run_id]

        if code_coverage:
            args.append("--code-coverage")

        if detailed_coverage:
            args.append("--detailed-coverage")

        if result_format:
            args += ["--result-format", result_format]

        if output_dir:
            args += ["--output-dir", str(output_dir)]

        if concise:
            args.append("--concise")

        return self._run_capturing(
            args,
            label=f"Getting logic test results for run {test_run_id}",
            timeout=timeout,
        )
