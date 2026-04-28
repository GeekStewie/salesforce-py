"""SF CLI project command wrappers."""

from pathlib import Path
from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFProjectOperations(SFBaseOperations):
    """Wraps ``sf project`` commands for deploying and retrieving metadata.

    Covers convert, delete, deploy (standard and pipeline), generate,
    list, reset tracking, and retrieve sub-command groups.
    """

    # ------------------------------------------------------------------
    # convert
    # ------------------------------------------------------------------

    def convert_mdapi(
        self,
        root_dir: Path,
        output_dir: Path | None = None,
        manifest: Path | None = None,
        metadata_dir: str | None = None,
        metadata: list[str] | None = None,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Convert Metadata API–formatted files into source format.

        Args:
            root_dir: Root directory of the Metadata API–formatted metadata.
            output_dir: Directory to write converted source files into.
                Defaults to the default package directory.
            manifest: Path to a ``package.xml`` manifest of types to convert.
                Mutually exclusive with ``metadata`` and ``metadata_dir``.
            metadata_dir: Root of a directory or ZIP file of metadata-format
                files to convert. Mutually exclusive with ``manifest`` and
                ``metadata``.
            metadata: Metadata component names to convert. Mutually exclusive
                with ``manifest`` and ``metadata_dir``.
            timeout: Subprocess timeout in seconds (default 300).

        Returns:
            Conversion result dict.
        """
        args = ["project", "convert", "mdapi", "--root-dir", str(root_dir)]
        if output_dir:
            args += ["--output-dir", str(output_dir)]
        if manifest:
            args += ["--manifest", str(manifest)]
        if metadata_dir:
            args += ["--metadata-dir", metadata_dir]
        if metadata:
            for m in metadata:
                args += ["--metadata", m]
        return self._run_capturing(
            args,
            label="Converting Metadata API format to source format",
            timeout=timeout,
            include_target_org=False,
        )

    def convert_source(
        self,
        root_dir: Path | None = None,
        output_dir: Path | None = None,
        package_name: str | None = None,
        manifest: Path | None = None,
        source_dir: list[str] | None = None,
        metadata: list[str] | None = None,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Convert source-formatted files into Metadata API format.

        Args:
            root_dir: Source directory to convert (other than the default
                package).
            output_dir: Output directory for converted metadata files.
            package_name: Package name to associate with the converted files.
            manifest: Path to a ``package.xml`` manifest of types to convert.
                Mutually exclusive with ``metadata`` and ``source_dir``.
            source_dir: Paths to local source files to convert. Mutually
                exclusive with ``manifest`` and ``metadata``.
            metadata: Metadata component names to convert. Mutually exclusive
                with ``manifest`` and ``source_dir``.
            timeout: Subprocess timeout in seconds (default 300).

        Returns:
            Conversion result dict.
        """
        args = ["project", "convert", "source"]
        if root_dir:
            args += ["--root-dir", str(root_dir)]
        if output_dir:
            args += ["--output-dir", str(output_dir)]
        if package_name:
            args += ["--package-name", package_name]
        if manifest:
            args += ["--manifest", str(manifest)]
        if source_dir:
            for d in source_dir:
                args += ["--source-dir", d]
        if metadata:
            for m in metadata:
                args += ["--metadata", m]
        return self._run_capturing(
            args,
            label="Converting source format to Metadata API format",
            timeout=timeout,
            include_target_org=False,
        )

    def convert_source_behavior(
        self,
        behavior: str,
        dry_run: bool = False,
        preserve_temp_dir: bool = False,
        target_org: str | None = None,
    ) -> dict[str, Any]:
        """Enable a source behavior and update the project to implement it.

        Updates the ``sourceBehaviorOption`` in ``sfdx-project.json`` and
        converts existing local source files to the new format. Run once per
        behavior change.

        Args:
            behavior: Behavior to enable. Valid values:
                ``decomposeCustomLabelsBeta2``, ``decomposeCustomLabelsBeta``,
                ``decomposePermissionSetBeta``,
                ``decomposePermissionSetBeta2``,
                ``decomposeSharingRulesBeta``, ``decomposeWorkflowBeta``,
                ``decomposeExternalServiceRegistrationBeta``.
            dry_run: Display what would change without writing any files.
            preserve_temp_dir: Keep the temporary metadata-format directory
                (useful for debugging).
            target_org: Username or alias of the target org (optional).

        Returns:
            Behavior conversion result dict.
        """
        args = ["project", "convert", "source-behavior", "--behavior", behavior]
        if dry_run:
            args.append("--dry-run")
        if preserve_temp_dir:
            args.append("--preserve-temp-dir")
        if target_org:
            args += ["--target-org", target_org]
        return self._run_capturing(
            args,
            label=f"Converting source behavior '{behavior}'",
            include_target_org=False,
        )

    # ------------------------------------------------------------------
    # delete
    # ------------------------------------------------------------------

    def delete_source(
        self,
        metadata: list[str] | None = None,
        source_dir: list[str] | None = None,
        no_prompt: bool = False,
        check_only: bool = False,
        wait: int | None = None,
        test_level: str | None = None,
        tests: list[str] | None = None,
        track_source: bool = False,
        force_overwrite: bool = False,
        verbose: bool = False,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Delete source from the project and from a non-source-tracked org.

        Use ``metadata`` or ``source_dir`` (not both). Use for orgs without
        source tracking; for source-tracked orgs, use :meth:`deploy_start`
        instead.

        Args:
            metadata: Metadata component names to delete (e.g.
                ``["ApexClass:MyClass"]``). Mutually exclusive with
                ``source_dir``.
            source_dir: Source file paths to delete. Mutually exclusive with
                ``metadata``.
            no_prompt: Skip the delete confirmation prompt.
            check_only: Validate the delete without executing it.
            wait: Minutes to wait for the command to finish (default 33).
            test_level: Apex test level — ``NoTestRun``,
                ``RunSpecifiedTests``, ``RunLocalTests``,
                ``RunAllTestsInOrg``, or ``RunRelevantTests``.
            tests: Apex tests to run when ``test_level`` is
                ``RunSpecifiedTests``.
            track_source: Update source tracking if the delete succeeds.
            force_overwrite: Ignore conflict warnings.
            verbose: Show verbose output.
            timeout: Subprocess timeout in seconds (default 600).

        Returns:
            Delete result dict.
        """
        args = ["project", "delete", "source"]
        if metadata:
            for m in metadata:
                args += ["--metadata", m]
        if source_dir:
            for d in source_dir:
                args += ["--source-dir", d]
        if no_prompt:
            args.append("--no-prompt")
        if check_only:
            args.append("--check-only")
        if wait is not None:
            args += ["--wait", str(wait)]
        if test_level:
            args += ["--test-level", test_level]
        if tests:
            for t in tests:
                args += ["--tests", t]
        if track_source:
            args.append("--track-source")
        if force_overwrite:
            args.append("--force-overwrite")
        if verbose:
            args.append("--verbose")
        return self._run_capturing(
            args,
            label="Deleting source from project and org",
            timeout=timeout,
        )

    def delete_tracking(self, no_prompt: bool = False) -> dict[str, Any]:
        """Delete all local source tracking information.

        WARNING: Deletes or overwrites all existing source tracking files.
        When you next run deploy preview, all files appear changed.

        Args:
            no_prompt: Skip the confirmation prompt.

        Returns:
            Result dict.
        """
        args = ["project", "delete", "tracking"]
        if no_prompt:
            args.append("--no-prompt")
        return self._run_capturing(args, label="Deleting source tracking")

    # ------------------------------------------------------------------
    # deploy (standard)
    # ------------------------------------------------------------------

    def deploy_start(
        self,
        source_dir: list[str] | None = None,
        metadata: list[str] | None = None,
        manifest: Path | None = None,
        metadata_dir: str | None = None,
        test_level: str | None = None,
        tests: list[str] | None = None,
        wait: int | None = None,
        async_: bool = False,
        dry_run: bool = False,
        ignore_conflicts: bool = False,
        ignore_errors: bool = False,
        ignore_warnings: bool = False,
        single_package: bool = False,
        purge_on_delete: bool = False,
        pre_destructive_changes: Path | None = None,
        post_destructive_changes: Path | None = None,
        concise: bool = False,
        verbose: bool = False,
        coverage_formatters: list[str] | None = None,
        junit: bool = False,
        results_dir: Path | None = None,
        timeout: int = 3600,
    ) -> dict[str, Any]:
        """Deploy metadata to the target org from your local project.

        Use one of ``source_dir``, ``metadata``, ``manifest``, or
        ``metadata_dir`` to specify what to deploy.

        Args:
            source_dir: Paths to local source files or directories.
            metadata: Metadata component names to deploy. Wildcards supported
                with quotes (e.g. ``"ApexClass:MyClass*"``).
            manifest: Full path to a ``package.xml`` manifest. Mutually
                exclusive with ``metadata`` and ``source_dir``.
            metadata_dir: Root of a directory or ZIP of metadata-format files.
            test_level: Apex test level — ``NoTestRun``,
                ``RunSpecifiedTests``, ``RunLocalTests``,
                ``RunAllTestsInOrg``, or ``RunRelevantTests``.
            tests: Apex tests to run when ``test_level`` is
                ``RunSpecifiedTests``.
            wait: Minutes to wait for completion (default 33).
            async_: Return immediately with a job ID.
            dry_run: Validate and run tests without saving to the org.
            ignore_conflicts: Deploy even if it overwrites org changes
                (source-tracked orgs only).
            ignore_errors: Ignore errors and don't roll back (never use on
                production).
            ignore_warnings: Treat warnings as success.
            single_package: Indicates the metadata ZIP is a single-package
                structure.
            purge_on_delete: Immediately delete destructive-changes
                components instead of sending to Recycle Bin.
            pre_destructive_changes: Path to ``destructiveChangesPre.xml``.
            post_destructive_changes: Path to ``destructiveChangesPost.xml``.
            concise: Show concise output.
            verbose: Show verbose output.
            coverage_formatters: Code coverage output formats (e.g.
                ``["lcov", "html"]``).
            junit: Output JUnit test results.
            results_dir: Directory for coverage and JUnit results.
            timeout: Subprocess timeout in seconds (default 3600).

        Returns:
            Deployment result dict.
        """
        args = ["project", "deploy", "start"]
        if source_dir:
            for d in source_dir:
                args += ["--source-dir", d]
        if metadata:
            for m in metadata:
                args += ["--metadata", m]
        if manifest:
            args += ["--manifest", str(manifest)]
        if metadata_dir:
            args += ["--metadata-dir", metadata_dir]
        if test_level:
            args += ["--test-level", test_level]
        if tests:
            for t in tests:
                args += ["--tests", t]
        if wait is not None:
            args += ["--wait", str(wait)]
        if async_:
            args.append("--async")
        if dry_run:
            args.append("--dry-run")
        if ignore_conflicts:
            args.append("--ignore-conflicts")
        if ignore_errors:
            args.append("--ignore-errors")
        if ignore_warnings:
            args.append("--ignore-warnings")
        if single_package:
            args.append("--single-package")
        if purge_on_delete:
            args.append("--purge-on-delete")
        if pre_destructive_changes:
            args += ["--pre-destructive-changes", str(pre_destructive_changes)]
        if post_destructive_changes:
            args += ["--post-destructive-changes", str(post_destructive_changes)]
        if concise:
            args.append("--concise")
        if verbose:
            args.append("--verbose")
        if coverage_formatters:
            for fmt in coverage_formatters:
                args += ["--coverage-formatters", fmt]
        if junit:
            args.append("--junit")
        if results_dir:
            args += ["--results-dir", str(results_dir)]
        return self._run_capturing(
            args,
            label="Deploying metadata",
            timeout=timeout,
        )

    def deploy_validate(
        self,
        source_dir: list[str] | None = None,
        metadata: list[str] | None = None,
        manifest: Path | None = None,
        metadata_dir: str | None = None,
        test_level: str | None = None,
        tests: list[str] | None = None,
        wait: int | None = None,
        async_: bool = False,
        ignore_warnings: bool = False,
        single_package: bool = False,
        purge_on_delete: bool = False,
        pre_destructive_changes: Path | None = None,
        post_destructive_changes: Path | None = None,
        concise: bool = False,
        verbose: bool = False,
        coverage_formatters: list[str] | None = None,
        junit: bool = False,
        results_dir: Path | None = None,
        timeout: int = 3600,
    ) -> dict[str, Any]:
        """Validate a deployment without executing it.

        Returns a job ID that you can pass to :meth:`deploy_quick` within 10
        days. Requires Apex tests to run (default ``RunLocalTests``).

        Note: For sandboxes use ``deploy_start(dry_run=True)`` instead.

        Args:
            source_dir: Paths to local source files or directories.
            metadata: Metadata component names to validate.
            manifest: Full path to a ``package.xml`` manifest.
            metadata_dir: Root of a directory or ZIP of metadata-format files.
            test_level: Apex test level — ``RunSpecifiedTests``,
                ``RunLocalTests`` (default), ``RunAllTestsInOrg``, or
                ``RunRelevantTests``.
            tests: Apex tests to run when ``test_level`` is
                ``RunSpecifiedTests``.
            wait: Minutes to wait for completion (default 33).
            async_: Return immediately with a job ID.
            ignore_warnings: Treat warnings as success.
            single_package: Indicates the metadata ZIP is a single-package
                structure.
            purge_on_delete: Immediately delete destructive-changes
                components.
            pre_destructive_changes: Path to ``destructiveChangesPre.xml``.
            post_destructive_changes: Path to ``destructiveChangesPost.xml``.
            concise: Show concise output.
            verbose: Show verbose output.
            coverage_formatters: Code coverage output formats.
            junit: Output JUnit test results.
            results_dir: Directory for coverage and JUnit results.
            timeout: Subprocess timeout in seconds (default 3600).

        Returns:
            Validation result dict containing a job ID.
        """
        args = ["project", "deploy", "validate"]
        if source_dir:
            for d in source_dir:
                args += ["--source-dir", d]
        if metadata:
            for m in metadata:
                args += ["--metadata", m]
        if manifest:
            args += ["--manifest", str(manifest)]
        if metadata_dir:
            args += ["--metadata-dir", metadata_dir]
        if test_level:
            args += ["--test-level", test_level]
        if tests:
            for t in tests:
                args += ["--tests", t]
        if wait is not None:
            args += ["--wait", str(wait)]
        if async_:
            args.append("--async")
        if ignore_warnings:
            args.append("--ignore-warnings")
        if single_package:
            args.append("--single-package")
        if purge_on_delete:
            args.append("--purge-on-delete")
        if pre_destructive_changes:
            args += ["--pre-destructive-changes", str(pre_destructive_changes)]
        if post_destructive_changes:
            args += ["--post-destructive-changes", str(post_destructive_changes)]
        if concise:
            args.append("--concise")
        if verbose:
            args.append("--verbose")
        if coverage_formatters:
            for fmt in coverage_formatters:
                args += ["--coverage-formatters", fmt]
        if junit:
            args.append("--junit")
        if results_dir:
            args += ["--results-dir", str(results_dir)]
        return self._run_capturing(
            args,
            label="Validating deployment",
            timeout=timeout,
        )

    def deploy_quick(
        self,
        job_id: str | None = None,
        use_most_recent: bool = False,
        async_: bool = False,
        wait: int | None = None,
        concise: bool = False,
        verbose: bool = False,
        timeout: int = 3600,
    ) -> dict[str, Any]:
        """Quickly deploy a validated deployment.

        Use the job ID returned by :meth:`deploy_validate`. The job ID is
        valid for 10 days. Skips Apex tests since they ran during validation.

        Note: Use on production orgs only; for sandboxes use
        :meth:`deploy_start`.

        Args:
            job_id: Job ID of the validated deployment. Mutually exclusive
                with ``use_most_recent``.
            use_most_recent: Use the most recently validated deployment job ID
                (valid only if validated in the past 3 days).
            async_: Return immediately; monitor with :meth:`deploy_report`.
            wait: Minutes to wait for completion (default 33).
            concise: Show concise output.
            verbose: Show verbose output.
            timeout: Subprocess timeout in seconds (default 3600).

        Returns:
            Quick deploy result dict.
        """
        args = ["project", "deploy", "quick"]
        if job_id:
            args += ["--job-id", job_id]
        if use_most_recent:
            args.append("--use-most-recent")
        if async_:
            args.append("--async")
        if wait is not None:
            args += ["--wait", str(wait)]
        if concise:
            args.append("--concise")
        if verbose:
            args.append("--verbose")
        return self._run_capturing(
            args,
            label="Running quick deploy",
            timeout=timeout,
        )

    def deploy_cancel(
        self,
        job_id: str | None = None,
        use_most_recent: bool = False,
        async_: bool = False,
        wait: int | None = None,
    ) -> dict[str, Any]:
        """Cancel a deploy operation that hasn't yet completed.

        Args:
            job_id: Job ID of the deploy operation to cancel. Mutually
                exclusive with ``use_most_recent``.
            use_most_recent: Use the most recent deploy job ID (valid only
                if started in the past 3 days).
            async_: Return immediately; monitor with :meth:`deploy_report`.
            wait: Minutes to wait for the cancellation to complete.

        Returns:
            Cancellation result dict.
        """
        args = ["project", "deploy", "cancel"]
        if job_id:
            args += ["--job-id", job_id]
        if use_most_recent:
            args.append("--use-most-recent")
        if async_:
            args.append("--async")
        if wait is not None:
            args += ["--wait", str(wait)]
        return self._run_capturing(args, label="Cancelling deploy operation")

    def deploy_report(
        self,
        job_id: str | None = None,
        use_most_recent: bool = False,
        wait: int | None = None,
        coverage_formatters: list[str] | None = None,
        junit: bool = False,
        results_dir: Path | None = None,
    ) -> dict[str, Any]:
        """Check or poll for the status of a deploy operation.

        With ``wait``, polls every second until timeout. Without ``wait``,
        returns the current status immediately.

        Args:
            job_id: Job ID of the deploy operation.
            use_most_recent: Use the most recent deploy job ID.
            wait: Minutes to poll for status.
            coverage_formatters: Code coverage output formats.
            junit: Output JUnit test results.
            results_dir: Directory for coverage and JUnit results.

        Returns:
            Deploy status dict.
        """
        args = ["project", "deploy", "report"]
        if job_id:
            args += ["--job-id", job_id]
        if use_most_recent:
            args.append("--use-most-recent")
        if wait is not None:
            args += ["--wait", str(wait)]
        if coverage_formatters:
            for fmt in coverage_formatters:
                args += ["--coverage-formatters", fmt]
        if junit:
            args.append("--junit")
        if results_dir:
            args += ["--results-dir", str(results_dir)]
        return self._run_capturing(
            args,
            label="Checking deploy status",
            include_api_version=False,
        )

    def deploy_resume(
        self,
        job_id: str | None = None,
        use_most_recent: bool = False,
        wait: int | None = None,
        concise: bool = False,
        verbose: bool = False,
        coverage_formatters: list[str] | None = None,
        junit: bool = False,
        results_dir: Path | None = None,
        timeout: int = 3600,
    ) -> dict[str, Any]:
        """Resume watching a deploy operation and update source tracking.

        The underlying deploy continues whether or not you watch it. This
        command resumes watching and updates source tracking on completion.

        Args:
            job_id: Job ID of the deploy operation to resume watching.
            use_most_recent: Use the most recent deploy job ID.
            wait: Minutes to wait for the command to complete.
            concise: Show concise output.
            verbose: Show verbose output.
            coverage_formatters: Code coverage output formats.
            junit: Output JUnit test results.
            results_dir: Directory for coverage and JUnit results.
            timeout: Subprocess timeout in seconds (default 3600).

        Returns:
            Deploy result dict.
        """
        args = ["project", "deploy", "resume"]
        if job_id:
            args += ["--job-id", job_id]
        if use_most_recent:
            args.append("--use-most-recent")
        if wait is not None:
            args += ["--wait", str(wait)]
        if concise:
            args.append("--concise")
        if verbose:
            args.append("--verbose")
        if coverage_formatters:
            for fmt in coverage_formatters:
                args += ["--coverage-formatters", fmt]
        if junit:
            args.append("--junit")
        if results_dir:
            args += ["--results-dir", str(results_dir)]
        return self._run_capturing(
            args,
            label="Resuming deploy operation",
            timeout=timeout,
            include_api_version=False,
        )

    def deploy_preview(
        self,
        source_dir: list[str] | None = None,
        metadata: list[str] | None = None,
        manifest: Path | None = None,
        ignore_conflicts: bool = False,
        concise: bool = False,
    ) -> dict[str, Any]:
        """Preview a deployment without executing it.

        Shows what will deploy, potential conflicts, and ignored files.

        Args:
            source_dir: Paths to local source files or directories.
            metadata: Metadata component names to preview.
            manifest: Full path to a ``package.xml`` manifest.
            ignore_conflicts: Omit conflicts from the preview output.
            concise: Show only the files that will deploy; omit forceignored
                files.

        Returns:
            Preview result dict.
        """
        args = ["project", "deploy", "preview"]
        if source_dir:
            for d in source_dir:
                args += ["--source-dir", d]
        if metadata:
            for m in metadata:
                args += ["--metadata", m]
        if manifest:
            args += ["--manifest", str(manifest)]
        if ignore_conflicts:
            args.append("--ignore-conflicts")
        if concise:
            args.append("--concise")
        return self._run_capturing(args, label="Previewing deployment")

    # ------------------------------------------------------------------
    # deploy pipeline (Beta)
    # ------------------------------------------------------------------

    def deploy_pipeline_start(
        self,
        devops_center_project_name: str,
        branch_name: str,
        devops_center_username: str,
        bundle_version_name: str | None = None,
        deploy_all: bool = False,
        test_level: str | None = None,
        tests: str | None = None,
        async_: bool = False,
        wait: int | None = None,
        concise: bool = False,
        verbose: bool = False,
        timeout: int = 3600,
    ) -> dict[str, Any]:
        """Deploy changes from a branch to the pipeline stage's org (Beta).

        Requires that changes in the branch have been merged in source
        control before running.

        Args:
            devops_center_project_name: Name of the DevOps Center project.
            branch_name: Source control branch corresponding to the pipeline
                stage.
            devops_center_username: Username or alias of the DevOps Center
                org.
            bundle_version_name: Bundle version (required when deploying to
                the first stage after the bundling stage).
            deploy_all: Deploy all metadata in the branch, not just changes.
            test_level: Apex test level — ``NoTestRun``,
                ``RunSpecifiedTests``, ``RunLocalTests``, or
                ``RunAllTestsInOrg``.
            tests: Comma-separated Apex test names when ``test_level`` is
                ``RunSpecifiedTests``.
            async_: Return immediately with a job ID.
            wait: Minutes to wait for completion (default 33).
            concise: Show concise output.
            verbose: Show verbose output.
            timeout: Subprocess timeout in seconds (default 3600).

        Returns:
            Pipeline deploy result dict.
        """
        args = [
            "project",
            "deploy",
            "pipeline",
            "start",
            "--devops-center-project-name",
            devops_center_project_name,
            "--branch-name",
            branch_name,
            "--devops-center-username",
            devops_center_username,
        ]
        if bundle_version_name:
            args += ["--bundle-version-name", bundle_version_name]
        if deploy_all:
            args.append("--deploy-all")
        if test_level:
            args += ["--test-level", test_level]
        if tests:
            args += ["--tests", tests]
        if async_:
            args.append("--async")
        if wait is not None:
            args += ["--wait", str(wait)]
        if concise:
            args.append("--concise")
        if verbose:
            args.append("--verbose")
        return self._run_capturing(
            args,
            label=f"Starting pipeline deploy for '{devops_center_project_name}'",
            timeout=timeout,
            include_target_org=False,
        )

    def deploy_pipeline_validate(
        self,
        devops_center_project_name: str,
        branch_name: str,
        devops_center_username: str,
        bundle_version_name: str | None = None,
        deploy_all: bool = False,
        test_level: str | None = None,
        tests: str | None = None,
        async_: bool = False,
        wait: int | None = None,
        concise: bool = False,
        verbose: bool = False,
        timeout: int = 3600,
    ) -> dict[str, Any]:
        """Validate a pipeline deployment without executing it (Beta).

        Returns a job ID for use with :meth:`deploy_pipeline_quick`.

        Args:
            devops_center_project_name: Name of the DevOps Center project.
            branch_name: Source control branch corresponding to the pipeline
                stage.
            devops_center_username: Username or alias of the DevOps Center
                org.
            bundle_version_name: Bundle version name.
            deploy_all: Validate all metadata in the branch.
            test_level: Apex test level.
            tests: Comma-separated Apex test names.
            async_: Return immediately with a job ID.
            wait: Minutes to wait for completion (default 33).
            concise: Show concise output.
            verbose: Show verbose output.
            timeout: Subprocess timeout in seconds (default 3600).

        Returns:
            Validation result dict containing a job ID.
        """
        args = [
            "project",
            "deploy",
            "pipeline",
            "validate",
            "--devops-center-project-name",
            devops_center_project_name,
            "--branch-name",
            branch_name,
            "--devops-center-username",
            devops_center_username,
        ]
        if bundle_version_name:
            args += ["--bundle-version-name", bundle_version_name]
        if deploy_all:
            args.append("--deploy-all")
        if test_level:
            args += ["--test-level", test_level]
        if tests:
            args += ["--tests", tests]
        if async_:
            args.append("--async")
        if wait is not None:
            args += ["--wait", str(wait)]
        if concise:
            args.append("--concise")
        if verbose:
            args.append("--verbose")
        return self._run_capturing(
            args,
            label=f"Validating pipeline deploy for '{devops_center_project_name}'",
            timeout=timeout,
            include_target_org=False,
        )

    def deploy_pipeline_quick(
        self,
        devops_center_username: str,
        job_id: str | None = None,
        use_most_recent: bool = False,
        async_: bool = False,
        wait: int | None = None,
        concise: bool = False,
        verbose: bool = False,
        timeout: int = 3600,
    ) -> dict[str, Any]:
        """Quickly deploy a validated pipeline deployment (Beta).

        Args:
            devops_center_username: Username or alias of the DevOps Center
                org.
            job_id: Job ID of the validated pipeline deployment.
            use_most_recent: Use the most recently validated deployment.
            async_: Return immediately; monitor with
                :meth:`deploy_pipeline_report`.
            wait: Minutes to wait for completion (default 33).
            concise: Show concise output.
            verbose: Show verbose output.
            timeout: Subprocess timeout in seconds (default 3600).

        Returns:
            Quick deploy result dict.
        """
        args = [
            "project",
            "deploy",
            "pipeline",
            "quick",
            "--devops-center-username",
            devops_center_username,
        ]
        if job_id:
            args += ["--job-id", job_id]
        if use_most_recent:
            args.append("--use-most-recent")
        if async_:
            args.append("--async")
        if wait is not None:
            args += ["--wait", str(wait)]
        if concise:
            args.append("--concise")
        if verbose:
            args.append("--verbose")
        return self._run_capturing(
            args,
            label="Running pipeline quick deploy",
            timeout=timeout,
            include_target_org=False,
        )

    def deploy_pipeline_report(
        self,
        devops_center_username: str,
        job_id: str | None = None,
        use_most_recent: bool = False,
    ) -> dict[str, Any]:
        """Check the status of a pipeline deploy operation (Beta).

        Args:
            devops_center_username: Username or alias of the DevOps Center
                org.
            job_id: Job ID of the pipeline deployment.
            use_most_recent: Use the most recent deploy job ID.

        Returns:
            Pipeline deploy status dict.
        """
        args = [
            "project",
            "deploy",
            "pipeline",
            "report",
            "--devops-center-username",
            devops_center_username,
        ]
        if job_id:
            args += ["--job-id", job_id]
        if use_most_recent:
            args.append("--use-most-recent")
        return self._run_capturing(
            args,
            label="Checking pipeline deploy status",
            include_target_org=False,
            include_api_version=False,
        )

    def deploy_pipeline_resume(
        self,
        devops_center_username: str,
        job_id: str | None = None,
        use_most_recent: bool = False,
        wait: int | None = None,
        concise: bool = False,
        verbose: bool = False,
        timeout: int = 3600,
    ) -> dict[str, Any]:
        """Resume watching a pipeline deploy operation (Beta).

        Args:
            devops_center_username: Username or alias of the DevOps Center
                org.
            job_id: Job ID of the pipeline deploy operation.
            use_most_recent: Use the most recent deploy job ID.
            wait: Minutes to wait for completion (default 33).
            concise: Show concise output.
            verbose: Show verbose output.
            timeout: Subprocess timeout in seconds (default 3600).

        Returns:
            Pipeline deploy result dict.
        """
        args = [
            "project",
            "deploy",
            "pipeline",
            "resume",
            "--devops-center-username",
            devops_center_username,
        ]
        if job_id:
            args += ["--job-id", job_id]
        if use_most_recent:
            args.append("--use-most-recent")
        if wait is not None:
            args += ["--wait", str(wait)]
        if concise:
            args.append("--concise")
        if verbose:
            args.append("--verbose")
        return self._run_capturing(
            args,
            label="Resuming pipeline deploy",
            timeout=timeout,
            include_target_org=False,
            include_api_version=False,
        )

    # ------------------------------------------------------------------
    # generate
    # ------------------------------------------------------------------

    def generate_manifest(
        self,
        metadata: list[str] | None = None,
        source_dir: list[str] | None = None,
        name: str | None = None,
        manifest_type: str | None = None,
        include_packages: list[str] | None = None,
        excluded_metadata: list[str] | None = None,
        from_org: str | None = None,
        output_dir: Path | None = None,
    ) -> dict[str, Any]:
        """Create a project manifest listing components to deploy or retrieve.

        Use ``metadata`` or ``source_dir`` to specify components (not both).
        Use ``from_org`` to build a manifest from live org metadata.

        Args:
            metadata: Metadata component names to include (e.g.
                ``["ApexClass", "CustomObject:MyObj__c"]``).
            source_dir: Paths to local source files to include.
            name: Custom manifest filename (e.g. ``myPackage.xml``). Mutually
                exclusive with ``manifest_type``.
            manifest_type: Predefined manifest type — ``package``
                (``package.xml``), ``pre``
                (``destructiveChangesPre.xml``), ``post``
                (``destructiveChangesPost.xml``), or ``destroy``
                (``destructiveChanges.xml``). Mutually exclusive with
                ``name``.
            include_packages: Package types whose metadata to include —
                ``managed``, ``unlocked``, or both. Unmanaged packages are
                always included.
            excluded_metadata: Metadata type names to exclude when building
                from an org.
            from_org: Username or alias of an org to build the manifest from.
            output_dir: Directory to save the created manifest.

        Returns:
            Manifest generation result dict.
        """
        args = ["project", "generate", "manifest"]
        if metadata:
            for m in metadata:
                args += ["--metadata", m]
        if source_dir:
            for d in source_dir:
                args += ["--source-dir", d]
        if name:
            args += ["--name", name]
        if manifest_type:
            args += ["--type", manifest_type]
        if include_packages:
            for pkg in include_packages:
                args += ["--include-packages", pkg]
        if excluded_metadata:
            for ex in excluded_metadata:
                args += ["--excluded-metadata", ex]
        if from_org:
            args += ["--from-org", from_org]
        if output_dir:
            args += ["--output-dir", str(output_dir)]
        return self._run_capturing(
            args,
            label="Generating project manifest",
            include_target_org=False,
        )

    # ------------------------------------------------------------------
    # list
    # ------------------------------------------------------------------

    def list_ignored(self, source_dir: Path | None = None) -> list[dict[str, Any]]:
        """Check project package directories for forceignored files.

        Args:
            source_dir: File or directory to check. Checks all package
                directories when not specified.

        Returns:
            List of ignored file dicts.
        """
        args = ["project", "list", "ignored"]
        if source_dir:
            args += ["--source-dir", str(source_dir)]
        result = self._run_capturing(
            args,
            label="Listing ignored files",
            include_target_org=False,
            include_api_version=False,
        )
        if isinstance(result, list):
            return result
        return result.get("result", [])

    # ------------------------------------------------------------------
    # reset tracking
    # ------------------------------------------------------------------

    def reset_tracking(
        self,
        revision: int | None = None,
        no_prompt: bool = False,
    ) -> dict[str, Any]:
        """Reset local and remote source tracking.

        WARNING: Deletes or overwrites all existing source tracking files.
        After this command, the next deploy preview will return no results
        even if conflicts exist.

        Args:
            revision: SourceMember revision counter number to reset to.
            no_prompt: Skip the confirmation prompt.

        Returns:
            Result dict.
        """
        args = ["project", "reset", "tracking"]
        if revision is not None:
            args += ["--revision", str(revision)]
        if no_prompt:
            args.append("--no-prompt")
        return self._run_capturing(args, label="Resetting source tracking")

    # ------------------------------------------------------------------
    # retrieve
    # ------------------------------------------------------------------

    def retrieve_start(
        self,
        source_dir: list[str] | None = None,
        metadata: list[str] | None = None,
        manifest: Path | None = None,
        package_name: list[str] | None = None,
        output_dir: Path | None = None,
        target_metadata_dir: Path | None = None,
        wait: int | None = None,
        ignore_conflicts: bool = False,
        single_package: bool = False,
        unzip: bool = False,
        zip_file_name: str | None = None,
        timeout: int = 3600,
    ) -> dict[str, Any]:
        """Retrieve metadata from the target org to your local project.

        Use one of ``source_dir``, ``metadata``, ``manifest``, or
        ``package_name`` to specify what to retrieve. Use
        ``target_metadata_dir`` to retrieve in metadata format (ZIP).

        Args:
            source_dir: Paths to local source files to retrieve.
            metadata: Metadata component names to retrieve. Wildcards
                supported with quotes (e.g. ``"ApexClass:MyClass*"``).
            manifest: Path to a ``package.xml`` manifest.
            package_name: Package names to retrieve into child directories.
            output_dir: Root directory for retrieved source files.
            target_metadata_dir: Directory for metadata-format ZIP output.
            wait: Minutes to wait for completion (default 33).
            ignore_conflicts: Overwrite local files even if they conflict.
            single_package: ZIP file points to a single-package structure.
            unzip: Extract all files from the retrieved ZIP.
            zip_file_name: File name for the retrieved ZIP.
            timeout: Subprocess timeout in seconds (default 3600).

        Returns:
            Retrieval result dict.
        """
        args = ["project", "retrieve", "start"]
        if source_dir:
            for d in source_dir:
                args += ["--source-dir", d]
        if metadata:
            for m in metadata:
                args += ["--metadata", m]
        if manifest:
            args += ["--manifest", str(manifest)]
        if package_name:
            for pkg in package_name:
                args += ["--package-name", pkg]
        if output_dir:
            args += ["--output-dir", str(output_dir)]
        if target_metadata_dir:
            args += ["--target-metadata-dir", str(target_metadata_dir)]
        if wait is not None:
            args += ["--wait", str(wait)]
        if ignore_conflicts:
            args.append("--ignore-conflicts")
        if single_package:
            args.append("--single-package")
        if unzip:
            args.append("--unzip")
        if zip_file_name:
            args += ["--zip-file-name", zip_file_name]
        return self._run_capturing(
            args,
            label="Retrieving metadata",
            timeout=timeout,
        )

    def retrieve_preview(
        self,
        ignore_conflicts: bool = False,
        concise: bool = False,
    ) -> dict[str, Any]:
        """Preview a retrieval without executing it.

        Shows what will be retrieved, potential conflicts, and ignored files.

        Args:
            ignore_conflicts: Omit conflicts from the preview output.
            concise: Show only the files that will be retrieved; omit
                forceignored files.

        Returns:
            Preview result dict.
        """
        args = ["project", "retrieve", "preview"]
        if ignore_conflicts:
            args.append("--ignore-conflicts")
        if concise:
            args.append("--concise")
        return self._run_capturing(args, label="Previewing retrieval")
