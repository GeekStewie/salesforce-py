"""SF CLI org command wrappers."""

from pathlib import Path
from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFOrgOperations(SFBaseOperations):
    """Wraps ``sf org`` commands for org lifecycle and user management.

    Covers assign, create, delete, display, enable/disable tracking,
    generate, get, list, login, logout, open, refresh, and resume
    sub-command groups.

    Note: login commands are thin wrappers over the SF CLI auth store.
    For programmatic org connections, prefer :class:`SFOrg` directly.
    """

    # ------------------------------------------------------------------
    # assign
    # ------------------------------------------------------------------

    def assign_permset(
        self,
        names: list[str],
        on_behalf_of: list[str] | None = None,
    ) -> dict[str, Any]:
        """Assign one or more permission sets to org users.

        Args:
            names: Permission set API names to assign.
            on_behalf_of: Usernames or aliases to assign the permission sets
                to. Defaults to the org's admin user.

        Returns:
            Assignment result dict.
        """
        args = ["org", "assign", "permset"]
        for name in names:
            args += ["--name", name]
        if on_behalf_of:
            for user in on_behalf_of:
                args += ["--on-behalf-of", user]
        return self._run_capturing(args, label="Assigning permission sets")

    def assign_permsetlicense(
        self,
        names: list[str],
        on_behalf_of: list[str] | None = None,
    ) -> dict[str, Any]:
        """Assign one or more permission set licenses to org users.

        Args:
            names: Permission set license names to assign.
            on_behalf_of: Usernames or aliases to assign the licenses to.
                Defaults to the org's admin user.

        Returns:
            Assignment result dict.
        """
        args = ["org", "assign", "permsetlicense"]
        for name in names:
            args += ["--name", name]
        if on_behalf_of:
            for user in on_behalf_of:
                args += ["--on-behalf-of", user]
        return self._run_capturing(args, label="Assigning permission set licenses")

    # ------------------------------------------------------------------
    # create
    # ------------------------------------------------------------------

    def create_agent_user(
        self,
        base_username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> dict[str, Any]:
        """Create the default Salesforce user used to run an agent.

        Creates a user with the "Einstein Agent User" profile and required
        Agentforce permission sets. The user has no password and cannot log
        in directly.

        Args:
            base_username: Base username pattern (email format). A GUID is
                appended to ensure global uniqueness. Auto-generated if not
                specified.
            first_name: First name for the agent user (default ``Agent``).
            last_name: Last name for the agent user (default ``User``).

        Returns:
            Agent user creation result dict.
        """
        args = ["org", "create", "agent-user"]
        if base_username:
            args += ["--base-username", base_username]
        if first_name:
            args += ["--first-name", first_name]
        if last_name:
            args += ["--last-name", last_name]
        return self._run_capturing(args, label="Creating agent user")

    def create_sandbox(
        self,
        name: str | None = None,
        definition_file: Path | None = None,
        license_type: str | None = None,
        alias: str | None = None,
        set_default: bool = False,
        wait: int | None = None,
        poll_interval: int | None = None,
        async_: bool = False,
        no_prompt: bool = False,
        no_track_source: bool = False,
        source_sandbox_name: str | None = None,
        source_id: str | None = None,
        timeout: int = 3600,
    ) -> dict[str, Any]:
        """Create a sandbox org.

        Specify a definition file or use ``name`` + ``license_type``. To
        clone an existing sandbox, use ``source_sandbox_name`` or
        ``source_id``.

        Args:
            name: Unique alphanumeric sandbox name (10 chars max).
            definition_file: Path to a sandbox definition file.
            license_type: License type — ``Developer``, ``Developer_Pro``,
                ``Partial``, or ``Full``.
            alias: Alias for the sandbox org.
            set_default: Set the sandbox as your default org.
            wait: Minutes to wait for creation (default 30).
            poll_interval: Seconds between status polls (default 30).
            async_: Return immediately with a job ID; don't wait.
            no_prompt: Skip confirmation prompts.
            no_track_source: Disable source tracking in the sandbox.
            source_sandbox_name: Name of an existing sandbox to clone.
            source_id: SandboxInfo ID of an existing sandbox to clone.
            timeout: Subprocess timeout in seconds (default 3600).

        Returns:
            Sandbox creation result dict.
        """
        args = ["org", "create", "sandbox"]
        if definition_file:
            args += ["--definition-file", str(definition_file)]
        if name:
            args += ["--name", name]
        if license_type:
            args += ["--license-type", license_type]
        if alias:
            args += ["--alias", alias]
        if set_default:
            args.append("--set-default")
        if wait is not None:
            args += ["--wait", str(wait)]
        if poll_interval is not None:
            args += ["--poll-interval", str(poll_interval)]
        if async_:
            args.append("--async")
        if no_prompt:
            args.append("--no-prompt")
        if no_track_source:
            args.append("--no-track-source")
        if source_sandbox_name:
            args += ["--source-sandbox-name", source_sandbox_name]
        if source_id:
            args += ["--source-id", source_id]
        return self._run_capturing(
            args,
            label=f"Creating sandbox {name or '(from definition file)'}",
            timeout=timeout,
            include_api_version=False,
        )

    def create_scratch(
        self,
        definition_file: Path | None = None,
        edition: str | None = None,
        alias: str | None = None,
        target_dev_hub: str | None = None,
        duration_days: int = 7,
        set_default: bool = False,
        no_namespace: bool = False,
        no_ancestors: bool = False,
        snapshot: str | None = None,
        source_org: str | None = None,
        username: str | None = None,
        description: str | None = None,
        org_name: str | None = None,
        release: str | None = None,
        admin_email: str | None = None,
        async_: bool = False,
        wait: int | None = None,
        client_id: str | None = None,
        track_source: bool = True,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Create a scratch org.

        Specify a definition file, an ``edition``, a ``snapshot``, or a
        ``source_org`` (org shape). ``edition``, ``snapshot``, and
        ``source_org`` are mutually exclusive.

        Args:
            definition_file: Path to a scratch org definition file.
            edition: Salesforce edition — ``developer``, ``enterprise``,
                ``group``, ``professional``, ``partner-developer``,
                ``partner-enterprise``, ``partner-group``, or
                ``partner-professional``.
            alias: Alias for the scratch org.
            target_dev_hub: Dev Hub alias or username. Uses the configured
                default when not specified.
            duration_days: Days before the org expires (default 7).
            set_default: Set the scratch org as your default org.
            no_namespace: Create without a namespace.
            no_ancestors: Exclude 2GP ancestors.
            snapshot: Snapshot name to create the scratch org from.
            source_org: 15-character ID of the org shape to base this org on.
            username: Admin username for the scratch org.
            description: Description stored in the Dev Hub.
            org_name: Org name (e.g. "Acme Company").
            release: ``preview`` or ``previous`` relative to the Dev Hub.
            admin_email: Email address for the admin user.
            async_: Return immediately with a job ID; don't wait.
            wait: Minutes to wait for creation (default 5).
            client_id: Consumer key of the Dev Hub connected app.
            track_source: Enable source tracking (default ``True``).
            timeout: Subprocess timeout in seconds (default 600).

        Returns:
            Scratch org creation result dict.
        """
        args = ["org", "create", "scratch"]
        if definition_file:
            args += ["--definition-file", str(definition_file)]
        if edition:
            args += ["--edition", edition]
        if alias:
            args += ["--alias", alias]
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        args += ["--duration-days", str(duration_days)]
        if set_default:
            args.append("--set-default")
        if no_namespace:
            args.append("--no-namespace")
        if no_ancestors:
            args.append("--no-ancestors")
        if snapshot:
            args += ["--snapshot", snapshot]
        if source_org:
            args += ["--source-org", source_org]
        if username:
            args += ["--username", username]
        if description:
            args += ["--description", description]
        if org_name:
            args += ["--name", org_name]
        if release:
            args += ["--release", release]
        if admin_email:
            args += ["--admin-email", admin_email]
        if async_:
            args.append("--async")
        if wait is not None:
            args += ["--wait", str(wait)]
        if client_id:
            args += ["--client-id", client_id]
        if not track_source:
            args.append("--no-track-source")
        return self._run_capturing(
            args,
            label=f"Creating scratch org {alias or '(auto-named)'}",
            timeout=timeout,
            include_target_org=False,
        )

    def create_shape(self) -> dict[str, Any]:
        """Create a scratch org configuration (shape) from the target org.

        The shape mimics the source org's baseline setup (features, limits,
        edition, Metadata API settings) without extraneous data or metadata.

        Returns:
            Shape creation result dict.
        """
        return self._run_capturing(
            ["org", "create", "shape"],
            label="Creating org shape",
        )

    def create_snapshot(
        self,
        source_org: str,
        name: str,
        target_dev_hub: str | None = None,
        description: str | None = None,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Create a snapshot of a scratch org.

        A snapshot is a point-in-time copy of a scratch org, referenced by
        its unique name in a scratch org definition file.

        Args:
            source_org: ID or locally authenticated username/alias of the
                scratch org to snapshot.
            name: Unique name for the snapshot.
            target_dev_hub: Dev Hub alias or username. Uses the configured
                default when not specified.
            description: Description of the snapshot contents.
            timeout: Subprocess timeout in seconds (default 600).

        Returns:
            Snapshot creation result dict.
        """
        args = [
            "org",
            "create",
            "snapshot",
            "--source-org",
            source_org,
            "--name",
            name,
        ]
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        if description:
            args += ["--description", description]
        return self._run_capturing(
            args,
            label=f"Creating snapshot '{name}'",
            timeout=timeout,
            include_target_org=False,
        )

    def create_user(
        self,
        set_alias: str | None = None,
        definition_file: Path | None = None,
        set_unique_username: bool = False,
        field_values: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Create a user for a scratch org.

        Args:
            set_alias: Alias for the new user.
            definition_file: Path to a user definition JSON file.
            set_unique_username: Append the org ID to the username to ensure
                global uniqueness.
            field_values: Extra User sObject field values as positional
                ``key=value`` arguments (e.g.
                ``{"profileName": "Chatter Free User"}``).

        Returns:
            User creation result dict.
        """
        args = ["org", "create", "user"]
        if set_alias:
            args += ["--set-alias", set_alias]
        if definition_file:
            args += ["--definition-file", str(definition_file)]
        if set_unique_username:
            args.append("--set-unique-username")
        if field_values:
            for key, value in field_values.items():
                args.append(f"{key}={value}")
        return self._run_capturing(args, label="Creating org user")

    # ------------------------------------------------------------------
    # delete
    # ------------------------------------------------------------------

    def delete_sandbox(
        self,
        no_prompt: bool = False,
    ) -> dict[str, Any]:
        """Delete a sandbox org.

        Marks the org for deletion in the production org and removes all
        local references. The target org must be the sandbox itself.

        Args:
            no_prompt: Skip the deletion confirmation prompt.

        Returns:
            Deletion result dict.
        """
        args = ["org", "delete", "sandbox"]
        if no_prompt:
            args.append("--no-prompt")
        return self._run_capturing(
            args,
            label="Deleting sandbox",
            include_api_version=False,
        )

    def delete_scratch(
        self,
        no_prompt: bool = False,
    ) -> dict[str, Any]:
        """Delete a scratch org.

        Marks the org for deletion in the Dev Hub and removes all local
        references.

        Args:
            no_prompt: Skip the deletion confirmation prompt.

        Returns:
            Deletion result dict.
        """
        args = ["org", "delete", "scratch"]
        if no_prompt:
            args.append("--no-prompt")
        return self._run_capturing(
            args,
            label="Deleting scratch org",
            include_api_version=False,
        )

    def delete_shape(
        self,
        no_prompt: bool = False,
    ) -> dict[str, Any]:
        """Delete all org shapes for the target org.

        Args:
            no_prompt: Skip the deletion confirmation prompt.

        Returns:
            Deletion result dict.
        """
        args = ["org", "delete", "shape"]
        if no_prompt:
            args.append("--no-prompt")
        return self._run_capturing(args, label="Deleting org shapes")

    def delete_snapshot(
        self,
        snapshot: str,
        target_dev_hub: str | None = None,
        no_prompt: bool = False,
    ) -> dict[str, Any]:
        """Delete a scratch org snapshot.

        Args:
            snapshot: Name or ID of the snapshot to delete.
            target_dev_hub: Dev Hub alias or username. Uses the configured
                default when not specified.
            no_prompt: Skip the deletion confirmation prompt.

        Returns:
            Deletion result dict.
        """
        args = ["org", "delete", "snapshot", "--snapshot", snapshot]
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        if no_prompt:
            args.append("--no-prompt")
        return self._run_capturing(
            args,
            label=f"Deleting snapshot '{snapshot}'",
            include_target_org=False,
        )

    # ------------------------------------------------------------------
    # tracking
    # ------------------------------------------------------------------

    def disable_tracking(self) -> dict[str, Any]:
        """Prevent Salesforce CLI from tracking source changes for the org.

        Affects only the local environment; has no direct effect on the org.

        Returns:
            Result dict.
        """
        return self._run_capturing(
            ["org", "disable", "tracking"],
            label="Disabling source tracking",
            include_api_version=False,
        )

    def enable_tracking(self) -> dict[str, Any]:
        """Allow Salesforce CLI to track source changes for the org.

        Affects only the local environment; has no direct effect on the org.
        Raises an error if the org type doesn't support source tracking.

        Returns:
            Result dict.
        """
        return self._run_capturing(
            ["org", "enable", "tracking"],
            label="Enabling source tracking",
            include_api_version=False,
        )

    # ------------------------------------------------------------------
    # display
    # ------------------------------------------------------------------

    def display(self, verbose: bool = False) -> dict[str, Any]:
        """Display information about the target org.

        Output includes access token, client ID, connection status, org ID,
        instance URL, username, and alias. Use ``verbose=True`` to include
        the sfdxAuthUrl (contains a refresh token — do not share).

        Args:
            verbose: Include the ``sfdxAuthUrl`` property (web flow only).

        Returns:
            Org info dict.
        """
        args = ["org", "display"]
        if verbose:
            args.append("--verbose")
        return self._run_capturing(args, label="Displaying org info")

    def display_user(self) -> dict[str, Any]:
        """Display information about the target org's Salesforce user.

        Output includes profile name, org ID, access token, instance URL,
        login URL, and alias if set.

        Returns:
            User info dict.
        """
        return self._run_capturing(["org", "display", "user"], label="Displaying user info")

    # ------------------------------------------------------------------
    # generate
    # ------------------------------------------------------------------

    def generate_password(
        self,
        on_behalf_of: list[str] | None = None,
        length: int | None = None,
        complexity: int | None = None,
    ) -> dict[str, Any]:
        """Generate a random password for scratch org users.

        By default generates a password for the org's admin user. Use
        ``on_behalf_of`` for additional users created with
        :meth:`create_user`.

        Args:
            on_behalf_of: Usernames or aliases to generate passwords for.
                Users must have been created with :meth:`create_user`.
            length: Password length (20–100, default 20).
            complexity: Password strength 0–5, where 5 uses all character
                classes (default 5).

        Returns:
            Password result dict.
        """
        args = ["org", "generate", "password"]
        if on_behalf_of:
            for user in on_behalf_of:
                args += ["--on-behalf-of", user]
        if length is not None:
            args += ["--length", str(length)]
        if complexity is not None:
            args += ["--complexity", str(complexity)]
        return self._run_capturing(args, label="Generating org password")

    # ------------------------------------------------------------------
    # get
    # ------------------------------------------------------------------

    def get_snapshot(
        self,
        snapshot: str,
        target_dev_hub: str | None = None,
    ) -> dict[str, Any]:
        """Get details about a scratch org snapshot.

        Args:
            snapshot: Name or ID of the snapshot to retrieve.
            target_dev_hub: Dev Hub alias or username. Uses the configured
                default when not specified.

        Returns:
            Snapshot detail dict.
        """
        args = ["org", "get", "snapshot", "--snapshot", snapshot]
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        return self._run_capturing(
            args,
            label=f"Getting snapshot '{snapshot}'",
            include_target_org=False,
        )

    # ------------------------------------------------------------------
    # list
    # ------------------------------------------------------------------

    def list_orgs(
        self,
        verbose: bool = False,
        all_: bool = False,
        clean: bool = False,
        no_prompt: bool = False,
        skip_connection_status: bool = False,
    ) -> list[dict[str, Any]]:
        """List all orgs you've created or authenticated to.

        Args:
            verbose: Show more information per org.
            all_: Include expired, deleted, and unknown-status scratch orgs.
            clean: Remove local auth info for non-active scratch orgs.
            no_prompt: Skip confirmation prompts.
            skip_connection_status: Skip live connection status checks for
                non-scratch orgs (faster).

        Returns:
            Combined list of non-scratch and scratch org dicts.
        """
        args = ["org", "list"]
        if verbose:
            args.append("--verbose")
        if all_:
            args.append("--all")
        if clean:
            args.append("--clean")
        if no_prompt:
            args.append("--no-prompt")
        if skip_connection_status:
            args.append("--skip-connection-status")
        result = self._run(
            args,
            include_target_org=False,
            include_api_version=False,
        )
        if isinstance(result, list):
            return result
        non_scratch = result.get("nonScratchOrgs", [])
        scratch = result.get("scratchOrgs", [])
        return non_scratch + scratch

    def list_auth(self) -> list[dict[str, Any]]:
        """List local authorization information about all orgs.

        Uses cached local data — does not connect to verify org status.
        For live status, use :meth:`list_orgs`.

        Returns:
            List of auth info dicts.
        """
        result = self._run(
            ["org", "list", "auth"],
            include_target_org=False,
            include_api_version=False,
        )
        if isinstance(result, list):
            return result
        return result.get("result", [])

    def list_limits(self) -> list[dict[str, Any]]:
        """Display information about limits in the target org.

        Returns both the maximum allocation and remaining allocation for
        each limit.

        Returns:
            List of limit dicts.
        """
        result = self._run_capturing(["org", "list", "limits"], label="Listing org limits")
        if isinstance(result, list):
            return result
        return result.get("result", [])

    def list_metadata(
        self,
        metadata_type: str,
        folder: str | None = None,
        output_file: Path | None = None,
    ) -> list[dict[str, Any]]:
        """List metadata components and properties of a specified type.

        Args:
            metadata_type: Metadata type to list (case-sensitive), e.g.
                ``CustomObject``, ``Layout``, ``Dashboard``.
            folder: Folder name for folder-based types (e.g.
                ``Dashboard``, ``Document``, ``EmailTemplate``,
                ``Report``).
            output_file: Path to write results to instead of stdout.

        Returns:
            List of metadata component dicts.
        """
        args = ["org", "list", "metadata", "--metadata-type", metadata_type]
        if folder:
            args += ["--folder", folder]
        if output_file:
            args += ["--output-file", str(output_file)]
        result = self._run_capturing(
            args,
            label=f"Listing {metadata_type} metadata",
        )
        if isinstance(result, list):
            return result
        return result.get("result", [])

    def list_metadata_types(
        self,
        output_file: Path | None = None,
    ) -> list[dict[str, Any]]:
        """Display details about the metadata types enabled in the target org.

        Args:
            output_file: Path to write results to instead of stdout.

        Returns:
            List of metadata type description dicts.
        """
        args = ["org", "list", "metadata-types"]
        if output_file:
            args += ["--output-file", str(output_file)]
        result = self._run_capturing(args, label="Listing metadata types")
        if isinstance(result, list):
            return result
        return result.get("result", [])

    def list_shape(self) -> list[dict[str, Any]]:
        """List all org shapes you've created.

        Returns:
            List of org shape dicts.
        """
        result = self._run(
            ["org", "list", "shape"],
            include_target_org=False,
            include_api_version=False,
        )
        if isinstance(result, list):
            return result
        return result.get("result", [])

    def list_snapshot(
        self,
        target_dev_hub: str | None = None,
    ) -> list[dict[str, Any]]:
        """List scratch org snapshots in the Dev Hub.

        Args:
            target_dev_hub: Dev Hub alias or username. Uses the configured
                default when not specified.

        Returns:
            List of snapshot dicts.
        """
        args = ["org", "list", "snapshot"]
        if target_dev_hub:
            args += ["--target-dev-hub", target_dev_hub]
        result = self._run(args, include_target_org=False)
        if isinstance(result, list):
            return result
        return result.get("result", [])

    def list_sobject_record_counts(
        self,
        sobjects: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Display approximate record counts for standard or custom objects.

        These counts match the Storage Usage page in Setup. They're
        approximate because they're calculated asynchronously.

        Args:
            sobjects: API names of objects to count. Returns all available
                counts when not specified.

        Returns:
            List of record count dicts.
        """
        args = ["org", "list", "sobject", "record-counts"]
        if sobjects:
            for sobject in sobjects:
                args += ["--sobject", sobject]
        result = self._run_capturing(args, label="Listing sobject record counts")
        if isinstance(result, list):
            return result
        return result.get("result", [])

    def list_users(self) -> list[dict[str, Any]]:
        """List all locally-authenticated users of the target org.

        For scratch orgs, includes users created with :meth:`create_user`.
        The original admin user is marked with "(A)".

        Returns:
            List of user summary dicts.
        """
        result = self._run_capturing(["org", "list", "users"], label="Listing org users")
        if isinstance(result, list):
            return result
        return result.get("result", [])

    # ------------------------------------------------------------------
    # login
    # ------------------------------------------------------------------

    def login_access_token(
        self,
        instance_url: str,
        alias: str | None = None,
        set_default: bool = False,
        set_default_dev_hub: bool = False,
        no_prompt: bool = False,
    ) -> dict[str, Any]:
        """Authorize an org using an existing Salesforce access token.

        Set the ``SF_ACCESS_TOKEN`` environment variable before calling
        when running non-interactively (also pass ``no_prompt=True``).

        Args:
            instance_url: URL of the org instance, e.g.
                ``https://mycompany.my.salesforce.com``.
            alias: Alias for the org.
            set_default: Set as the default org.
            set_default_dev_hub: Set as the default Dev Hub.
            no_prompt: Skip the overwrite confirmation prompt.

        Returns:
            Auth result dict.
        """
        args = ["org", "login", "access-token", "--instance-url", instance_url]
        if alias:
            args += ["--alias", alias]
        if set_default:
            args.append("--set-default")
        if set_default_dev_hub:
            args.append("--set-default-dev-hub")
        if no_prompt:
            args.append("--no-prompt")
        return self._run_capturing(
            args,
            label=f"Logging in via access token to {instance_url}",
            include_target_org=False,
            include_api_version=False,
        )

    def login_jwt(
        self,
        username: str,
        jwt_key_file: Path,
        client_id: str,
        instance_url: str | None = None,
        alias: str | None = None,
        set_default: bool = False,
        set_default_dev_hub: bool = False,
    ) -> dict[str, Any]:
        """Log in to a Salesforce org using a JWT.

        Use for CI/CD environments where browser-based login is unavailable.

        Args:
            username: Username of the user logging in.
            jwt_key_file: Path to the private key file.
            client_id: OAuth client ID (consumer key) of the connected app.
            instance_url: Org instance URL. Defaults to
                ``https://login.salesforce.com``.
            alias: Alias for the org.
            set_default: Set as the default org.
            set_default_dev_hub: Set as the default Dev Hub.

        Returns:
            Auth result dict.
        """
        args = [
            "org",
            "login",
            "jwt",
            "--username",
            username,
            "--jwt-key-file",
            str(jwt_key_file),
            "--client-id",
            client_id,
        ]
        if instance_url:
            args += ["--instance-url", instance_url]
        if alias:
            args += ["--alias", alias]
        if set_default:
            args.append("--set-default")
        if set_default_dev_hub:
            args.append("--set-default-dev-hub")
        return self._run_capturing(
            args,
            label=f"Logging in via JWT as {username}",
            include_target_org=False,
            include_api_version=False,
        )

    def login_sfdx_url(
        self,
        sfdx_url_file: Path,
        alias: str | None = None,
        set_default: bool = False,
        set_default_dev_hub: bool = False,
    ) -> dict[str, Any]:
        """Authorize an org using an SFDX authorization URL file.

        The file can be a JSON file (output of ``sf org display --verbose
        --json``), a JSON file with a top-level ``sfdxAuthUrl`` property,
        or a plain text file containing just the URL.

        Args:
            sfdx_url_file: Path to the file containing the SFDX auth URL.
            alias: Alias for the org.
            set_default: Set as the default org.
            set_default_dev_hub: Set as the default Dev Hub.

        Returns:
            Auth result dict.
        """
        args = ["org", "login", "sfdx-url", "--sfdx-url-file", str(sfdx_url_file)]
        if alias:
            args += ["--alias", alias]
        if set_default:
            args.append("--set-default")
        if set_default_dev_hub:
            args.append("--set-default-dev-hub")
        return self._run_capturing(
            args,
            label=f"Logging in via SFDX URL from {sfdx_url_file.name}",
            include_target_org=False,
            include_api_version=False,
        )

    def login_web(
        self,
        instance_url: str | None = None,
        alias: str | None = None,
        set_default: bool = False,
        set_default_dev_hub: bool = False,
        browser: str | None = None,
        client_id: str | None = None,
        client_app: str | None = None,
        username: str | None = None,
        scopes: str | None = None,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Log in to a Salesforce org using the web server flow.

        Opens a browser for credential entry. Use ``client_app`` +
        ``username`` to link a connected app to an already-authenticated
        user.

        Args:
            instance_url: Org instance URL. Defaults to
                ``https://login.salesforce.com``.
            alias: Alias for the org.
            set_default: Set as the default org.
            set_default_dev_hub: Set as the default Dev Hub.
            browser: Browser to open — ``chrome``, ``edge``, or
                ``firefox``. Defaults to the system browser.
            client_id: OAuth client ID of a custom connected app.
            client_app: Name for the link between the connected app and
                the user. Must be used with ``username``.
            username: Already-authenticated user to link to the connected
                app. Must be used with ``client_app``.
            scopes: OAuth scopes to request, space-separated
                (e.g. ``"sfap_api chatbot_api"``).
            timeout: Subprocess timeout in seconds (default 300).

        Returns:
            Auth result dict.
        """
        args = ["org", "login", "web"]
        if instance_url:
            args += ["--instance-url", instance_url]
        if alias:
            args += ["--alias", alias]
        if set_default:
            args.append("--set-default")
        if set_default_dev_hub:
            args.append("--set-default-dev-hub")
        if browser:
            args += ["--browser", browser]
        if client_id:
            args += ["--client-id", client_id]
        if client_app:
            args += ["--client-app", client_app]
        if username:
            args += ["--username", username]
        if scopes:
            args += ["--scopes", scopes]
        return self._run_capturing(
            args,
            label="Logging in via web flow",
            timeout=timeout,
            include_target_org=False,
            include_api_version=False,
        )

    # ------------------------------------------------------------------
    # logout
    # ------------------------------------------------------------------

    def logout(
        self,
        all_: bool = False,
        no_prompt: bool = False,
        client_app: str | None = None,
    ) -> dict[str, Any]:
        """Log out of the target org (or all orgs).

        Without ``all_=True``, logs out of the org configured as
        ``target_org`` on this instance. Use ``all_=True`` to log out of
        all authenticated orgs (prompts for confirmation unless
        ``no_prompt=True``).

        Args:
            all_: Include all authenticated orgs in the logout.
            no_prompt: Skip the confirmation prompt (requires ``all_`` or a
                ``target_org`` to be set).
            client_app: Name of a connected app link to log out of (created
                with :meth:`login_web` using ``--client-app``).

        Returns:
            Logout result dict.
        """
        args = ["org", "logout"]
        if all_:
            args.append("--all")
        if no_prompt:
            args.append("--no-prompt")
        if client_app:
            args += ["--client-app", client_app]
        return self._run_capturing(
            args,
            label="Logging out of org",
            include_api_version=False,
        )

    # ------------------------------------------------------------------
    # open
    # ------------------------------------------------------------------

    def open_org(
        self,
        path: str | None = None,
        url_only: bool = False,
        browser: str | None = None,
        private: bool = False,
        source_file: Path | None = None,
    ) -> dict[str, Any]:
        """Open the target org in a browser.

        Args:
            path: URL path to open, e.g. ``lightning`` or
                ``/apex/MyPage``.
            url_only: Return the URL without opening a browser.
            browser: Browser to use — ``chrome``, ``edge``, or
                ``firefox``. Defaults to the system browser.
            private: Open in a private (incognito) window.
            source_file: Local ApexPage, FlexiPage, Flow, or Agent
                metadata to open in its associated Builder.

        Returns:
            Dict containing ``url`` and related open metadata.
        """
        args = ["org", "open"]
        if path:
            args += ["--path", path]
        if url_only:
            args.append("--url-only")
        if browser:
            args += ["--browser", browser]
        if private:
            args.append("--private")
        if source_file:
            args += ["--source-file", str(source_file)]
        return self._run_capturing(args, label="Opening org")

    def open_agent(
        self,
        api_name: str,
        url_only: bool = False,
        browser: str | None = None,
        private: bool = False,
    ) -> dict[str, Any]:
        """Open an agent in the org's Agent Builder UI.

        Args:
            api_name: API (developer) name of the agent to open.
            url_only: Return the URL without opening a browser.
            browser: Browser to use — ``chrome``, ``edge``, or
                ``firefox``. Defaults to the system browser.
            private: Open in a private (incognito) window.

        Returns:
            Dict containing the Agent Builder URL.
        """
        args = ["org", "open", "agent", "--api-name", api_name]
        if url_only:
            args.append("--url-only")
        if browser:
            args += ["--browser", browser]
        if private:
            args.append("--private")
        return self._run_capturing(args, label=f"Opening agent '{api_name}'")

    def open_authoring_bundle(
        self,
        url_only: bool = False,
        browser: str | None = None,
        private: bool = False,
    ) -> dict[str, Any]:
        """Open Agentforce Studio showing the list of agents in the org.

        Args:
            url_only: Return the URL without opening a browser.
            browser: Browser to use — ``chrome``, ``edge``, or
                ``firefox``. Defaults to the system browser.
            private: Open in a private (incognito) window.

        Returns:
            Dict containing the Agentforce Studio URL.
        """
        args = ["org", "open", "authoring-bundle"]
        if url_only:
            args.append("--url-only")
        if browser:
            args += ["--browser", browser]
        if private:
            args.append("--private")
        return self._run_capturing(args, label="Opening Agentforce Studio")

    # ------------------------------------------------------------------
    # refresh / resume
    # ------------------------------------------------------------------

    def refresh_sandbox(
        self,
        name: str | None = None,
        definition_file: Path | None = None,
        wait: int | None = None,
        poll_interval: int | None = None,
        async_: bool = False,
        no_prompt: bool = False,
        no_auto_activate: bool = False,
        source_sandbox_name: str | None = None,
        source_id: str | None = None,
        timeout: int = 3600,
    ) -> dict[str, Any]:
        """Refresh a sandbox org.

        Copies metadata (and optionally data) from the source production
        org to the sandbox. Optionally change its configuration by
        specifying a definition file.

        Args:
            name: Name of the existing sandbox to refresh.
            definition_file: Path to a sandbox definition file to override
                the sandbox configuration during refresh.
            wait: Minutes to poll for refresh status (default 30).
            poll_interval: Seconds between status polls (default 30).
            async_: Return immediately with a job ID; don't wait.
            no_prompt: Skip confirmation prompts.
            no_auto_activate: Disable auto-activation after refresh.
            source_sandbox_name: Name of the new source sandbox for the
                refresh. Mutually exclusive with ``source_id``.
            source_id: ID of the new source sandbox for the refresh.
                Mutually exclusive with ``source_sandbox_name``.
            timeout: Subprocess timeout in seconds (default 3600).

        Returns:
            Sandbox refresh result dict.
        """
        args = ["org", "refresh", "sandbox"]
        if name:
            args += ["--name", name]
        if definition_file:
            args += ["--definition-file", str(definition_file)]
        if wait is not None:
            args += ["--wait", str(wait)]
        if poll_interval is not None:
            args += ["--poll-interval", str(poll_interval)]
        if async_:
            args.append("--async")
        if no_prompt:
            args.append("--no-prompt")
        if no_auto_activate:
            args.append("--no-auto-activate")
        if source_sandbox_name:
            args += ["--source-sandbox-name", source_sandbox_name]
        if source_id:
            args += ["--source-id", source_id]
        return self._run_capturing(
            args,
            label=f"Refreshing sandbox {name or '(from definition file)'}",
            timeout=timeout,
            include_api_version=False,
        )

    def resume_sandbox(
        self,
        name: str | None = None,
        job_id: str | None = None,
        use_most_recent: bool = False,
        wait: int | None = None,
    ) -> dict[str, Any]:
        """Check the status of a sandbox creation and log in when ready.

        Use the job ID from an ``--async`` :meth:`create_sandbox` call, or
        ``use_most_recent=True`` for the most recent creation.

        Args:
            name: Name of the sandbox org.
            job_id: Job ID of the incomplete sandbox creation.
            use_most_recent: Use the most recent sandbox create request.
            wait: Minutes to wait for the sandbox to be ready.

        Returns:
            Sandbox status or completion result dict.
        """
        args = ["org", "resume", "sandbox"]
        if name:
            args += ["--name", name]
        if job_id:
            args += ["--job-id", job_id]
        if use_most_recent:
            args.append("--use-most-recent")
        if wait is not None:
            args += ["--wait", str(wait)]
        return self._run_capturing(
            args,
            label="Resuming sandbox creation",
            include_api_version=False,
        )

    def resume_scratch(
        self,
        job_id: str | None = None,
        use_most_recent: bool = False,
        wait: int | None = None,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Resume the creation of an incomplete scratch org.

        Use the job ID from an ``--async`` :meth:`create_scratch` call, or
        ``use_most_recent=True`` for the most recent creation.

        Args:
            job_id: Job ID of the incomplete scratch org creation.
            use_most_recent: Use the most recent incomplete scratch org.
            wait: Minutes to wait for the scratch org to be ready.
            timeout: Subprocess timeout in seconds (default 600).

        Returns:
            Scratch org status or completion result dict.
        """
        args = ["org", "resume", "scratch"]
        if job_id:
            args += ["--job-id", job_id]
        if use_most_recent:
            args.append("--use-most-recent")
        if wait is not None:
            args += ["--wait", str(wait)]
        return self._run_capturing(
            args,
            label="Resuming scratch org creation",
            timeout=timeout,
            include_target_org=False,
            include_api_version=False,
        )
