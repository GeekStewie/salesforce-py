"""SF CLI package command wrappers."""

from pathlib import Path
from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFPackageOperations(SFBaseOperations):
    """Wraps ``sf package`` commands for unlocked and 2GP managed packages.

    Commands that operate against the Dev Hub use ``include_target_org=False``
    and pass ``--target-dev-hub`` explicitly when ``target_dev_hub`` is
    provided. Commands that install/uninstall into a target org use the
    standard ``include_target_org=True`` behaviour.
    """

    # ------------------------------------------------------------------
    # package (top-level)
    # ------------------------------------------------------------------

    def convert(
        self,
        package: str,
        installation_key: str | None = None,
        installation_key_bypass: bool = False,
        definition_file: Path | None = None,
        wait: int | None = None,
        seed_metadata: Path | None = None,
        patch_version: str | None = None,
        code_coverage: bool = False,
        target_dev_hub: str | None = None,
        verbose: bool = False,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Convert a first-generation managed package to a 2GP version.

        Selects the latest released major.minor 1GP version and converts it.
        Use ``patch_version`` to target a specific released patch version.

        Either ``installation_key`` or ``installation_key_bypass`` is
        required.

        Args:
            package: ID (starts with 033) of the 1GP managed package.
            installation_key: Installation key for key-protected package.
            installation_key_bypass: Bypass the installation key requirement.
            definition_file: Path to a definition file with features and
                preferences the package version depends on.
            wait: Minutes to wait for version creation (default 0 = async).
            seed_metadata: Directory of metadata to deploy before conversion.
            patch_version: Specific patch version (major.minor.patch) to
                convert.
            code_coverage: Calculate and store code coverage percentage.
            target_dev_hub: Dev Hub alias or username.
            verbose: Display verbose command output.
            timeout: Subprocess timeout in seconds (default 600).

        Returns:
            Package version creation result dict.
        """
        args = ["package", "convert", "--package", package]
        if installation_key:
            args += ["--installation-key", installation_key]
        if installation_key_bypass:
            args.append("--installation-key-bypass")
        if definition_file:
            args += ["--definition-file", str(definition_file)]
        if wait is not None:
            args += ["--wait", str(wait)]
        if seed_metadata:
            args += ["--seed-metadata", str(seed_metadata)]
        if patch_version:
            args += ["--patch-version", patch_version]
        if code_coverage:
            args.append("--code-coverage")
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        if verbose:
            args.append("--verbose")
        return self._run_capturing(
            args,
            label=f"Converting 1GP package {package}",
            timeout=timeout,
            include_target_org=False,
        )

    def create(
        self,
        name: str,
        package_type: str,
        path: str,
        description: str | None = None,
        no_namespace: bool = False,
        org_dependent: bool = False,
        error_notification_username: str | None = None,
        target_dev_hub: str | None = None,
    ) -> dict[str, Any]:
        """Create a package in the Dev Hub org.

        Args:
            name: Name of the package (unique within the namespace).
            package_type: ``Managed`` or ``Unlocked``.
            path: Path to the directory containing the package contents.
            description: Description of the package.
            no_namespace: Create with no namespace (unlocked only).
            org_dependent: Create an org-dependent unlocked package.
            error_notification_username: Dev Hub user to receive error
                notification emails.
            target_dev_hub: Dev Hub alias or username.

        Returns:
            Package creation result dict.
        """
        args = [
            "package",
            "create",
            "--name",
            name,
            "--package-type",
            package_type,
            "--path",
            path,
        ]
        if description:
            args += ["--description", description]
        if no_namespace:
            args.append("--no-namespace")
        if org_dependent:
            args.append("--org-dependent")
        if error_notification_username:
            args += ["--error-notification-username", error_notification_username]
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Creating package '{name}'",
            include_target_org=False,
        )

    def delete(
        self,
        package: str,
        no_prompt: bool = False,
        target_dev_hub: str | None = None,
    ) -> dict[str, Any]:
        """Delete a package (unlocked or 2GP managed).

        Delete all associated package versions before deleting the package.

        Args:
            package: ID (starts with 0Ho) or alias of the package.
            no_prompt: Skip confirmation prompt.
            target_dev_hub: Dev Hub alias or username.

        Returns:
            Deletion result dict.
        """
        args = ["package", "delete", "--package", package]
        if no_prompt:
            args.append("--no-prompt")
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Deleting package {package}",
            include_target_org=False,
        )

    def install(
        self,
        package: str,
        installation_key: str | None = None,
        wait: int | None = None,
        publish_wait: int | None = None,
        no_prompt: bool = False,
        apex_compile: str | None = None,
        security_type: str | None = None,
        upgrade_type: str | None = None,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Install or upgrade a package version in the target org.

        Args:
            package: ID (starts with 04t) or alias of the package version.
            installation_key: Key for key-protected packages.
            wait: Minutes to wait for installation status (default 0).
            publish_wait: Max minutes to wait for the subscriber package
                version ID to become available (default 0).
            no_prompt: Skip confirmation prompts.
            apex_compile: ``all`` or ``package`` (unlocked packages only).
            security_type: ``AllUsers`` or ``AdminsOnly`` (default
                ``AdminsOnly``).
            upgrade_type: ``DeprecateOnly``, ``Mixed``, or ``Delete``
                (unlocked upgrades only; default ``Mixed``).
            timeout: Subprocess timeout in seconds (default 600).

        Returns:
            Installation result dict.
        """
        args = ["package", "install", "--package", package]
        if installation_key:
            args += ["--installation-key", installation_key]
        if wait is not None:
            args += ["--wait", str(wait)]
        if publish_wait is not None:
            args += ["--publish-wait", str(publish_wait)]
        if no_prompt:
            args.append("--no-prompt")
        if apex_compile:
            args += ["--apex-compile", apex_compile]
        if security_type:
            args += ["--security-type", security_type]
        if upgrade_type:
            args += ["--upgrade-type", upgrade_type]
        return self._run_capturing(
            args,
            label=f"Installing package {package}",
            timeout=timeout,
        )

    def install_report(self, request_id: str) -> dict[str, Any]:
        """Retrieve the status of a package installation request.

        Args:
            request_id: ID of the install request (starts with 0Hf).

        Returns:
            Installation status dict.
        """
        return self._run_capturing(
            ["package", "install", "report", "--request-id", request_id],
            label=f"Checking install status for {request_id}",
        )

    def installed_list(self) -> list[dict[str, Any]]:
        """List the packages installed in the target org.

        Returns:
            List of installed package dicts.
        """
        result = self._run_capturing(
            ["package", "installed", "list"],
            label="Listing installed packages",
        )
        if isinstance(result, list):
            return result
        return result.get("result", [])

    def list_packages(
        self,
        verbose: bool = False,
        target_dev_hub: str | None = None,
    ) -> list[dict[str, Any]]:
        """List all packages in the Dev Hub org.

        Args:
            verbose: Display extended package details.
            target_dev_hub: Dev Hub alias or username.

        Returns:
            List of package dicts.
        """
        args = ["package", "list"]
        if verbose:
            args.append("--verbose")
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        result = self._run_capturing(
            args,
            label="Listing packages",
            include_target_org=False,
        )
        if isinstance(result, list):
            return result
        return result.get("result", [])

    def uninstall(
        self,
        package: str,
        wait: int | None = None,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Uninstall a second-generation package from the target org.

        Args:
            package: ID (starts with 04t) or alias of the package version.
            wait: Minutes to wait for uninstall status (default 0).
            timeout: Subprocess timeout in seconds (default 600).

        Returns:
            Uninstall result dict.
        """
        args = ["package", "uninstall", "--package", package]
        if wait is not None:
            args += ["--wait", str(wait)]
        return self._run_capturing(
            args,
            label=f"Uninstalling package {package}",
            timeout=timeout,
        )

    def uninstall_report(self, request_id: str) -> dict[str, Any]:
        """Retrieve the status of a package uninstall request.

        Args:
            request_id: ID of the uninstall request (starts with 06y).

        Returns:
            Uninstall status dict.
        """
        return self._run_capturing(
            ["package", "uninstall", "report", "--request-id", request_id],
            label=f"Checking uninstall status for {request_id}",
        )

    def update(
        self,
        package: str,
        name: str | None = None,
        description: str | None = None,
        error_notification_username: str | None = None,
        enable_app_analytics: bool = False,
        recommended_version_id: str | None = None,
        skip_ancestor_check: bool = False,
        target_dev_hub: str | None = None,
    ) -> dict[str, Any]:
        """Update package details in the Dev Hub org.

        Args:
            package: ID (starts with 0Ho) or alias of the package.
            name: New package name.
            description: New package description.
            error_notification_username: Dev Hub user for error notifications.
            enable_app_analytics: Enable AppExchange App Analytics data
                collection.
            recommended_version_id: ID of the recommended version for
                subscribers to install.
            skip_ancestor_check: Bypass ancestry check for recommended
                version.
            target_dev_hub: Dev Hub alias or username.

        Returns:
            Update result dict.
        """
        args = ["package", "update", "--package", package]
        if name:
            args += ["--name", name]
        if description:
            args += ["--description", description]
        if error_notification_username:
            args += ["--error-notification-username", error_notification_username]
        if enable_app_analytics:
            args.append("--enable-app-analytics")
        if recommended_version_id:
            args += ["--recommended-version-id", recommended_version_id]
        if skip_ancestor_check:
            args.append("--skip-ancestor-check")
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Updating package {package}",
            include_target_org=False,
        )

    # ------------------------------------------------------------------
    # push-upgrade
    # ------------------------------------------------------------------

    def push_upgrade_abort(
        self,
        push_request_id: str,
        target_dev_hub: str | None = None,
    ) -> dict[str, Any]:
        """Abort a scheduled package push upgrade.

        Only requests with status Created or Pending can be aborted.

        Args:
            push_request_id: ID of the push request (starts with 0DV).
            target_dev_hub: Dev Hub alias or username.

        Returns:
            Abort result dict.
        """
        args = [
            "package",
            "push-upgrade",
            "abort",
            "--push-request-id",
            push_request_id,
        ]
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Aborting push upgrade {push_request_id}",
            include_target_org=False,
        )

    def push_upgrade_list(
        self,
        package: str,
        scheduled_last_days: int | None = None,
        status: str | None = None,
        show_push_migrations_only: bool = False,
        target_dev_hub: str | None = None,
    ) -> list[dict[str, Any]]:
        """List the status of push upgrade requests for a package.

        Args:
            package: Package ID (starts with 033).
            scheduled_last_days: Filter to requests scheduled in the last N
                days.
            status: Filter by status — ``Created``, ``Cancelled``,
                ``Pending``, ``In Progress``, ``Failed``, or ``Succeeded``.
            show_push_migrations_only: Display only push migration requests.
            target_dev_hub: Dev Hub alias or username.

        Returns:
            List of push upgrade request dicts.
        """
        args = ["package", "push-upgrade", "list", "--package", package]
        if scheduled_last_days is not None:
            args += ["--scheduled-last-days", str(scheduled_last_days)]
        if status:
            args += ["--status", status]
        if show_push_migrations_only:
            args.append("--show-push-migrations-only")
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        result = self._run_capturing(
            args,
            label=f"Listing push upgrades for {package}",
            include_target_org=False,
        )
        if isinstance(result, list):
            return result
        return result.get("result", [])

    def push_upgrade_report(
        self,
        push_request_id: str,
        target_dev_hub: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve the status of a package push upgrade.

        Args:
            push_request_id: ID of the push request (starts with 0DV).
            target_dev_hub: Dev Hub alias or username.

        Returns:
            Push upgrade status dict.
        """
        args = [
            "package",
            "push-upgrade",
            "report",
            "--push-request-id",
            push_request_id,
        ]
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Reporting push upgrade {push_request_id}",
            include_target_org=False,
        )

    def push_upgrade_schedule(
        self,
        package: str,
        org_file: Path | None = None,
        org_list: str | None = None,
        start_time: str | None = None,
        migrate_to_2gp: bool = False,
        target_dev_hub: str | None = None,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Schedule a package push upgrade.

        Either ``org_file`` or ``org_list`` must be provided.

        Args:
            package: ID (starts with 04t) of the package version to upgrade
                subscribers to.
            org_file: CSV file listing subscriber org IDs (one per line).
            org_list: Comma-separated list of subscriber org IDs.
            start_time: UTC datetime when the upgrade should start, e.g.
                ``"2024-12-06T21:00:00"``. Schedules immediately if not
                set.
            migrate_to_2gp: Indicate this is a 1GP → 2GP migration push.
            target_dev_hub: Dev Hub alias or username.
            timeout: Subprocess timeout in seconds (default 300).

        Returns:
            Push upgrade schedule result dict.
        """
        args = ["package", "push-upgrade", "schedule", "--package", package]
        if org_file:
            args += ["--org-file", str(org_file)]
        if org_list:
            args += ["--org-list", org_list]
        if start_time:
            args += ["--start-time", start_time]
        if migrate_to_2gp:
            args.append("--migrate-to-2gp")
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Scheduling push upgrade for {package}",
            timeout=timeout,
            include_target_org=False,
        )

    # ------------------------------------------------------------------
    # package version
    # ------------------------------------------------------------------

    def version_create(
        self,
        package: str | None = None,
        path: str | None = None,
        installation_key: str | None = None,
        installation_key_bypass: bool = False,
        code_coverage: bool = False,
        skip_validation: bool = False,
        async_validation: bool = False,
        branch: str | None = None,
        definition_file: Path | None = None,
        tag: str | None = None,
        version_name: str | None = None,
        version_number: str | None = None,
        version_description: str | None = None,
        post_install_script: str | None = None,
        post_install_url: str | None = None,
        releasenotes_url: str | None = None,
        uninstall_script: str | None = None,
        skip_ancestor_check: bool = False,
        generate_pkg_zip: bool = False,
        language: str | None = None,
        wait: int | None = None,
        verbose: bool = False,
        target_dev_hub: str | None = None,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Create a package version in the Dev Hub org.

        Either ``package`` or ``path`` (or both) must be provided.
        Either ``installation_key`` or ``installation_key_bypass`` is
        required.

        Args:
            package: ID (starts with 0Ho) or alias of the package.
            path: Path to the directory containing the package contents.
            installation_key: Installation key for key-protected package.
            installation_key_bypass: Bypass installation key requirement.
            code_coverage: Calculate and store code coverage percentage.
            skip_validation: Skip validation (cannot promote unvalidated
                versions).
            async_validation: Return early before validation completes.
            branch: Source control branch name.
            definition_file: Path to a scratch org–like definition file.
            tag: Package version tag.
            version_name: Override the version name from sfdx-project.json.
            version_number: Override the version number
                (major.minor.patch.build).
            version_description: Override the version description.
            post_install_script: Apex class to run post-install (managed
                only).
            post_install_url: Post-install instructions URL.
            releasenotes_url: Release notes URL.
            uninstall_script: Apex class to run on uninstall (managed only).
            skip_ancestor_check: Bypass ancestry requirements.
            generate_pkg_zip: Generate a package ZIP for debugging.
            language: Language code for the package.
            wait: Minutes to wait for version creation (default 0).
            verbose: Display verbose output (useful in CI).
            target_dev_hub: Dev Hub alias or username.
            timeout: Subprocess timeout in seconds (default 600).

        Returns:
            Package version creation result dict.
        """
        args = ["package", "version", "create"]
        if package:
            args += ["--package", package]
        if path:
            args += ["--path", path]
        if installation_key:
            args += ["--installation-key", installation_key]
        if installation_key_bypass:
            args.append("--installation-key-bypass")
        if code_coverage:
            args.append("--code-coverage")
        if skip_validation:
            args.append("--skip-validation")
        if async_validation:
            args.append("--async-validation")
        if branch:
            args += ["--branch", branch]
        if definition_file:
            args += ["--definition-file", str(definition_file)]
        if tag:
            args += ["--tag", tag]
        if version_name:
            args += ["--version-name", version_name]
        if version_number:
            args += ["--version-number", version_number]
        if version_description:
            args += ["--version-description", version_description]
        if post_install_script:
            args += ["--post-install-script", post_install_script]
        if post_install_url:
            args += ["--post-install-url", post_install_url]
        if releasenotes_url:
            args += ["--releasenotes-url", releasenotes_url]
        if uninstall_script:
            args += ["--uninstall-script", uninstall_script]
        if skip_ancestor_check:
            args.append("--skip-ancestor-check")
        if generate_pkg_zip:
            args.append("--generate-pkg-zip")
        if language:
            args += ["--language", language]
        if wait is not None:
            args += ["--wait", str(wait)]
        if verbose:
            args.append("--verbose")
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Creating package version for {package or path}",
            timeout=timeout,
            include_target_org=False,
        )

    def version_create_list(
        self,
        created_last_days: int | None = None,
        status: str | None = None,
        show_conversions_only: bool = False,
        verbose: bool = False,
        target_dev_hub: str | None = None,
    ) -> list[dict[str, Any]]:
        """List package version creation requests in the Dev Hub org.

        Args:
            created_last_days: Filter to requests created in the last N days
                (0 = today).
            status: Filter by status — ``Queued``, ``InProgress``,
                ``Success``, or ``Error``.
            show_conversions_only: Show only converted package versions.
            verbose: Display additional details.
            target_dev_hub: Dev Hub alias or username.

        Returns:
            List of version creation request dicts.
        """
        args = ["package", "version", "create", "list"]
        if created_last_days is not None:
            args += ["--created-last-days", str(created_last_days)]
        if status:
            args += ["--status", status]
        if show_conversions_only:
            args.append("--show-conversions-only")
        if verbose:
            args.append("--verbose")
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        result = self._run_capturing(
            args,
            label="Listing package version create requests",
            include_target_org=False,
        )
        if isinstance(result, list):
            return result
        return result.get("result", [])

    def version_create_report(
        self,
        package_create_request_id: str,
        target_dev_hub: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve details about a package version creation request.

        Args:
            package_create_request_id: Request ID (starts with 08c).
            target_dev_hub: Dev Hub alias or username.

        Returns:
            Version creation request detail dict.
        """
        args = [
            "package",
            "version",
            "create",
            "report",
            "--package-create-request-id",
            package_create_request_id,
        ]
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Reporting on version create request {package_create_request_id}",
            include_target_org=False,
        )

    def version_delete(
        self,
        package: str,
        no_prompt: bool = False,
        target_dev_hub: str | None = None,
    ) -> dict[str, Any]:
        """Delete a package version.

        Only beta package versions can be deleted in 2GP managed packaging.

        Args:
            package: ID (starts with 04t) or alias of the package version.
            no_prompt: Skip confirmation prompt.
            target_dev_hub: Dev Hub alias or username.

        Returns:
            Deletion result dict.
        """
        args = ["package", "version", "delete", "--package", package]
        if no_prompt:
            args.append("--no-prompt")
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Deleting package version {package}",
            include_target_org=False,
        )

    def version_displayancestry(
        self,
        package: str,
        dot_code: bool = False,
        verbose: bool = False,
        target_dev_hub: str | None = None,
    ) -> dict[str, Any]:
        """Display the ancestry tree for a 2GP managed package version.

        Args:
            package: ID or alias of a package (starts with 0Ho) or package
                version (starts with 04t).
            dot_code: Output the ancestry tree in DOT code format.
            verbose: Include both the package version ID and version number
                in the tree.
            target_dev_hub: Dev Hub alias or username.

        Returns:
            Ancestry tree result dict.
        """
        args = ["package", "version", "displayancestry", "--package", package]
        if dot_code:
            args.append("--dot-code")
        if verbose:
            args.append("--verbose")
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Displaying ancestry for {package}",
            include_target_org=False,
        )

    def version_displaydependencies(
        self,
        package: str,
        edge_direction: str | None = None,
        verbose: bool = False,
        target_dev_hub: str | None = None,
    ) -> dict[str, Any]:
        """Display the dependency graph for an unlocked or 2GP package version.

        Args:
            package: ID or alias of a package version (starts with 04t) or
                version create request (starts with 08c).
            edge_direction: ``root-first`` or ``root-last`` (default
                ``root-first``).
            verbose: Include both the package version ID and version number
                in each node.
            target_dev_hub: Dev Hub alias or username.

        Returns:
            Dependency graph result dict.
        """
        args = ["package", "version", "displaydependencies", "--package", package]
        if edge_direction:
            args += ["--edge-direction", edge_direction]
        if verbose:
            args.append("--verbose")
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Displaying dependencies for {package}",
            include_target_org=False,
        )

    def version_list(
        self,
        packages: str | None = None,
        created_last_days: int | None = None,
        modified_last_days: int | None = None,
        released: bool = False,
        branch: str | None = None,
        order_by: str | None = None,
        concise: bool = False,
        show_conversions_only: bool = False,
        verbose: bool = False,
        target_dev_hub: str | None = None,
    ) -> list[dict[str, Any]]:
        """List all package versions in the Dev Hub org.

        Args:
            packages: Comma-delimited list of package aliases or 0Ho IDs
                to filter by.
            created_last_days: Filter to versions created in the last N days
                (0 = today).
            modified_last_days: Filter to versions modified in the last N
                days (0 = today).
            released: Show only released versions (IsReleased=true).
            branch: Filter by source control branch name.
            order_by: Package version field(s) to sort by (e.g.
                ``PatchVersion``).
            concise: Show limited version details.
            show_conversions_only: Show only converted package versions.
            verbose: Show extended version details.
            target_dev_hub: Dev Hub alias or username.

        Returns:
            List of package version dicts.
        """
        args = ["package", "version", "list"]
        if packages:
            args += ["--packages", packages]
        if created_last_days is not None:
            args += ["--created-last-days", str(created_last_days)]
        if modified_last_days is not None:
            args += ["--modified-last-days", str(modified_last_days)]
        if released:
            args.append("--released")
        if branch:
            args += ["--branch", branch]
        if order_by:
            args += ["--order-by", order_by]
        if concise:
            args.append("--concise")
        if show_conversions_only:
            args.append("--show-conversions-only")
        if verbose:
            args.append("--verbose")
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        result = self._run_capturing(
            args,
            label="Listing package versions",
            include_target_org=False,
        )
        if isinstance(result, list):
            return result
        return result.get("result", [])

    def version_promote(
        self,
        package: str,
        no_prompt: bool = False,
        target_dev_hub: str | None = None,
    ) -> dict[str, Any]:
        """Promote a package version to released.

        Args:
            package: ID (starts with 04t) or alias of the package version.
            no_prompt: Skip the confirmation prompt.
            target_dev_hub: Dev Hub alias or username.

        Returns:
            Promotion result dict.
        """
        args = ["package", "version", "promote", "--package", package]
        if no_prompt:
            args.append("--no-prompt")
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Promoting package version {package}",
            include_target_org=False,
        )

    def version_report(
        self,
        package: str,
        verbose: bool = False,
        target_dev_hub: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve details about a package version in the Dev Hub org.

        Args:
            package: ID (starts with 04t) or alias of the package version.
            verbose: Display extended package version details.
            target_dev_hub: Dev Hub alias or username.

        Returns:
            Package version detail dict.
        """
        args = ["package", "version", "report", "--package", package]
        if verbose:
            args.append("--verbose")
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Reporting on package version {package}",
            include_target_org=False,
        )

    def version_retrieve(
        self,
        package: str,
        output_dir: Path | None = None,
        target_dev_hub: str | None = None,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Retrieve package metadata for a specified package version.

        Available for 2GP managed package versions converted from 1GP, and
        for unlocked packages. The output directory must be empty.

        Args:
            package: Subscriber package version ID (starts with 04t).
            output_dir: Empty directory to download metadata into (default
                ``force-app``).
            target_dev_hub: Dev Hub alias or username.
            timeout: Subprocess timeout in seconds (default 300).

        Returns:
            Retrieval result dict.
        """
        args = ["package", "version", "retrieve", "--package", package]
        if output_dir:
            args += ["--output-dir", str(output_dir)]
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Retrieving package metadata for {package}",
            timeout=timeout,
            include_target_org=False,
        )

    def version_update(
        self,
        package: str,
        version_name: str | None = None,
        version_description: str | None = None,
        branch: str | None = None,
        tag: str | None = None,
        installation_key: str | None = None,
        target_dev_hub: str | None = None,
    ) -> dict[str, Any]:
        """Update a package version.

        Args:
            package: ID (starts with 04t) or alias of the package version.
            version_name: New version name.
            version_description: New version description.
            branch: New branch name.
            tag: New tag.
            installation_key: New installation key.
            target_dev_hub: Dev Hub alias or username.

        Returns:
            Update result dict.
        """
        args = ["package", "version", "update", "--package", package]
        if version_name:
            args += ["--version-name", version_name]
        if version_description:
            args += ["--version-description", version_description]
        if branch:
            args += ["--branch", branch]
        if tag:
            args += ["--tag", tag]
        if installation_key:
            args += ["--installation-key", installation_key]
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Updating package version {package}",
            include_target_org=False,
        )
