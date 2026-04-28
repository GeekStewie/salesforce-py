"""SF CLI agent command wrappers."""

from pathlib import Path
from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFAgentOperations(SFBaseOperations):
    """Wraps ``sf agent`` commands for Agentforce lifecycle management.

    Covers agent activation/deactivation, spec/bundle generation, authoring
    bundle publishing and validation, programmatic preview sessions, and test
    creation/execution.

    Note: ``sf agent preview`` (interactive terminal UI) is intentionally not
    wrapped here — use :meth:`preview_start` / :meth:`preview_send` /
    :meth:`preview_end` for programmatic access instead.
    """

    # ------------------------------------------------------------------
    # Activation / deactivation
    # ------------------------------------------------------------------

    def activate(
        self,
        api_name: str | None = None,
        version: int | None = None,
    ) -> dict[str, Any]:
        """Activate an agent in the target org.

        Args:
            api_name: API name of the agent to activate. If omitted and the
                command is non-interactive (``--json`` mode), the latest version
                is activated automatically.
            version: Version number to activate (e.g. ``4`` for ``v4``).

        Returns:
            Activation result dict.
        """
        args = ["agent", "activate"]
        if api_name:
            args += ["--api-name", api_name]
        if version is not None:
            args += ["--version", str(version)]

        return self._run_capturing(
            args,
            label=f"Activating agent {api_name or '(default)'}",
        )

    def deactivate(self, api_name: str | None = None) -> dict[str, Any]:
        """Deactivate an agent in the target org.

        Args:
            api_name: API name of the agent to deactivate. If omitted, the
                command selects automatically in ``--json`` mode.

        Returns:
            Deactivation result dict.
        """
        args = ["agent", "deactivate"]
        if api_name:
            args += ["--api-name", api_name]

        return self._run_capturing(
            args,
            label=f"Deactivating agent {api_name or '(default)'}",
        )

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(
        self,
        name: str | None = None,
        api_name: str | None = None,
        spec: Path | None = None,
        preview: bool = False,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Create an agent in the org from a local agent spec file.

        Args:
            name: Human-readable name (label) for the agent.
            api_name: API name for the agent; derived from ``name`` if omitted.
            spec: Path to an agent spec YAML file.
            preview: Review the agent definition without saving to the org.
            timeout: Subprocess timeout in seconds.

        Returns:
            Agent creation result dict.
        """
        args = ["agent", "create"]
        if name:
            args += ["--name", name]
        if api_name:
            args += ["--api-name", api_name]
        if spec:
            args += ["--spec", str(spec)]
        if preview:
            args.append("--preview")

        return self._run_capturing(
            args,
            label=f"Creating agent {name or api_name or '(prompted)'}",
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Generate sub-commands
    # ------------------------------------------------------------------

    def generate_agent_spec(
        self,
        agent_type: str | None = None,
        role: str | None = None,
        company_name: str | None = None,
        company_description: str | None = None,
        company_website: str | None = None,
        max_topics: int | None = None,
        agent_user: str | None = None,
        enrich_logs: bool | None = None,
        tone: str | None = None,
        spec: Path | None = None,
        output_file: Path | None = None,
        prompt_template: str | None = None,
        grounding_context: str | None = None,
        force_overwrite: bool = False,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Generate an agent spec YAML file.

        Args:
            agent_type: Agent type: ``customer`` or ``internal``.
            role: Role description for the agent.
            company_name: Name of the company.
            company_description: Description of the company.
            company_website: Website URL of the company.
            max_topics: Maximum number of topics to generate (default 5).
            agent_user: Username in the org to assign to the agent.
            enrich_logs: Add agent conversation data to event logs (``true``/``false``).
            tone: Conversational tone: ``formal``, ``casual``, or ``neutral``.
            spec: Existing agent spec YAML file to use as input for iteration.
            output_file: Path for the generated YAML file.
            prompt_template: API name of a custom prompt template.
            grounding_context: Context information for the custom prompt template.
            force_overwrite: Overwrite an existing spec file without confirmation.
            timeout: Subprocess timeout in seconds.

        Returns:
            Generation result dict.
        """
        args = ["agent", "generate", "agent-spec"]

        if agent_type:
            args += ["--type", agent_type]
        if role:
            args += ["--role", role]
        if company_name:
            args += ["--company-name", company_name]
        if company_description:
            args += ["--company-description", company_description]
        if company_website:
            args += ["--company-website", company_website]
        if max_topics is not None:
            args += ["--max-topics", str(max_topics)]
        if agent_user:
            args += ["--agent-user", agent_user]
        if enrich_logs is not None:
            args += ["--enrich-logs", "true" if enrich_logs else "false"]
        if tone:
            args += ["--tone", tone]
        if spec:
            args += ["--spec", str(spec)]
        if output_file:
            args += ["--output-file", str(output_file)]
        if prompt_template:
            args += ["--prompt-template", prompt_template]
        if grounding_context:
            args += ["--grounding-context", grounding_context]
        if force_overwrite:
            args.append("--force-overwrite")

        return self._run_capturing(
            args,
            label="Generating agent spec",
            timeout=timeout,
        )

    def generate_authoring_bundle(
        self,
        name: str | None = None,
        api_name: str | None = None,
        spec: Path | None = None,
        no_spec: bool = False,
        output_dir: Path | None = None,
        force_overwrite: bool = False,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Generate an authoring bundle from an agent spec YAML file.

        Args:
            name: Label for the authoring bundle.
            api_name: API name for the bundle; derived from ``name`` if omitted.
            spec: Path to the agent spec YAML file.
            no_spec: Generate a default boilerplate bundle without a spec file.
            output_dir: Directory where bundle files are generated.
            force_overwrite: Overwrite an existing bundle with the same API name.
            timeout: Subprocess timeout in seconds.

        Returns:
            Generation result dict.
        """
        args = ["agent", "generate", "authoring-bundle"]

        if name:
            args += ["--name", name]
        if api_name:
            args += ["--api-name", api_name]
        if spec:
            args += ["--spec", str(spec)]
        if no_spec:
            args.append("--no-spec")
        if output_dir:
            args += ["--output-dir", str(output_dir)]
        if force_overwrite:
            args.append("--force-overwrite")

        return self._run_capturing(
            args,
            label=f"Generating authoring bundle {name or '(prompted)'}",
            timeout=timeout,
        )

    def generate_template(
        self,
        agent_file: Path,
        agent_version: int,
        source_org: str,
        output_dir: Path | None = None,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Generate an agent template from an existing DX project agent.

        Args:
            agent_file: Path to the Bot metadata file (e.g.
                ``force-app/main/default/bots/My_Agent/My_Agent.bot-meta.xml``).
            agent_version: Version number of the agent (BotVersion).
            source_org: Alias or username of the namespaced scratch org that
                contains the agent.
            output_dir: Directory where the BotTemplate and GenAiPlannerBundle
                files are saved.
            timeout: Subprocess timeout in seconds.

        Returns:
            Template generation result dict.
        """
        args = [
            "agent",
            "generate",
            "template",
            "--agent-file",
            str(agent_file),
            "--agent-version",
            str(agent_version),
            "--source-org",
            source_org,
        ]
        if output_dir:
            args += ["--output-dir", str(output_dir)]

        # generate template uses --source-org, not --target-org
        return self._run_capturing(
            args,
            label=f"Generating agent template from {agent_file.name}",
            timeout=timeout,
            include_target_org=False,
        )

    def generate_test_spec(
        self,
        output_file: Path | None = None,
        from_definition: Path | None = None,
        force_overwrite: bool = False,
    ) -> dict[str, Any]:
        """Generate an agent test spec YAML file.

        Args:
            output_file: Path for the generated test spec YAML file.
            from_definition: Path to an existing AiEvaluationDefinition metadata
                XML file to convert.
            force_overwrite: Overwrite an existing test spec file without
                confirmation.

        Returns:
            Generation result dict.
        """
        args = ["agent", "generate", "test-spec"]

        if output_file:
            args += ["--output-file", str(output_file)]
        if from_definition:
            args += ["--from-definition", str(from_definition)]
        if force_overwrite:
            args.append("--force-overwrite")

        return self._run_capturing(
            args,
            label="Generating agent test spec",
            include_target_org=False,
        )

    # ------------------------------------------------------------------
    # Authoring bundle: publish and validate
    # ------------------------------------------------------------------

    def publish_authoring_bundle(
        self,
        api_name: str | None = None,
        skip_retrieve: bool = False,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Publish an authoring bundle to the org.

        Args:
            api_name: API name of the authoring bundle to publish. If omitted,
                the command selects automatically in ``--json`` mode.
            skip_retrieve: Skip retrieving updated metadata back to the DX project.
            timeout: Subprocess timeout in seconds.

        Returns:
            Publish result dict.
        """
        args = ["agent", "publish", "authoring-bundle"]
        if api_name:
            args += ["--api-name", api_name]
        if skip_retrieve:
            args.append("--skip-retrieve")

        return self._run_capturing(
            args,
            label=f"Publishing authoring bundle {api_name or '(prompted)'}",
            timeout=timeout,
        )

    def validate_authoring_bundle(
        self,
        api_name: str | None = None,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """Validate that an authoring bundle's Agent Script file compiles.

        Args:
            api_name: API name of the authoring bundle to validate. If omitted,
                the command selects automatically in ``--json`` mode.
            timeout: Subprocess timeout in seconds.

        Returns:
            Validation result dict. On failure, contains a list of compilation
            errors with location information.
        """
        args = ["agent", "validate", "authoring-bundle"]
        if api_name:
            args += ["--api-name", api_name]

        return self._run_capturing(
            args,
            label=f"Validating authoring bundle {api_name or '(prompted)'}",
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Programmatic preview sessions
    # ------------------------------------------------------------------

    def preview_start(
        self,
        api_name: str | None = None,
        authoring_bundle: str | None = None,
        use_live_actions: bool = False,
        simulate_actions: bool = False,
    ) -> dict[str, Any]:
        """Start a programmatic agent preview session.

        Either ``api_name`` (published agent) or ``authoring_bundle`` must be
        provided.  For authoring bundles, exactly one of ``use_live_actions``
        or ``simulate_actions`` must be set.

        Args:
            api_name: API name of an activated published agent.
            authoring_bundle: API name of a local authoring bundle.
            use_live_actions: Execute real Apex/Flow actions in the org.
            simulate_actions: Use AI to simulate action execution.

        Returns:
            Dict containing the ``sessionId`` for subsequent calls.
        """
        args = ["agent", "preview", "start"]
        if api_name:
            args += ["--api-name", api_name]
        if authoring_bundle:
            args += ["--authoring-bundle", authoring_bundle]
        if use_live_actions:
            args.append("--use-live-actions")
        if simulate_actions:
            args.append("--simulate-actions")

        return self._run_capturing(
            args,
            label=f"Starting agent preview session for {api_name or authoring_bundle}",
        )

    def preview_send(
        self,
        utterance: str,
        api_name: str | None = None,
        authoring_bundle: str | None = None,
        session_id: str | None = None,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """Send a message to an active agent preview session.

        Args:
            utterance: Natural language statement, question, or command to send.
            api_name: API name of the published agent.
            authoring_bundle: API name of the local authoring bundle.
            session_id: Session ID from :meth:`preview_start`. Required when
                the agent has more than one active session.
            timeout: Subprocess timeout in seconds.

        Returns:
            Dict containing the agent's response.
        """
        args = ["agent", "preview", "send", "--utterance", utterance]
        if api_name:
            args += ["--api-name", api_name]
        if authoring_bundle:
            args += ["--authoring-bundle", authoring_bundle]
        if session_id:
            args += ["--session-id", session_id]

        return self._run_capturing(
            args,
            label="Sending utterance to agent",
            timeout=timeout,
        )

    def preview_end(
        self,
        api_name: str | None = None,
        authoring_bundle: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """End an active programmatic agent preview session.

        Args:
            api_name: API name of the published agent.
            authoring_bundle: API name of the local authoring bundle.
            session_id: Session ID from :meth:`preview_start`. Required when
                the agent has more than one active session.

        Returns:
            Dict containing the trace file location.
        """
        args = ["agent", "preview", "end"]
        if api_name:
            args += ["--api-name", api_name]
        if authoring_bundle:
            args += ["--authoring-bundle", authoring_bundle]
        if session_id:
            args += ["--session-id", session_id]

        return self._run_capturing(
            args,
            label=f"Ending agent preview session {session_id or ''}",
        )

    def preview_sessions(self) -> list[dict[str, Any]]:
        """List all cached programmatic agent preview sessions.

        Returns:
            List of session summary dicts, each containing ``sessionId``,
            agent API name, and status.
        """
        result = self._run(
            ["agent", "preview", "sessions"],
            include_target_org=False,
        )
        if isinstance(result, list):
            return result
        return result.get("sessions", [])

    # ------------------------------------------------------------------
    # Test management
    # ------------------------------------------------------------------

    def test_create(
        self,
        spec: Path | None = None,
        api_name: str | None = None,
        preview: bool = False,
        force_overwrite: bool = False,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """Create an agent test in the org from a test spec YAML file.

        Args:
            spec: Path to the test spec YAML file.
            api_name: API name for the new test in the org.
            preview: Preview the AiEvaluationDefinition metadata without
                deploying to the org.
            force_overwrite: Overwrite an existing test with the same API name
                without confirmation.
            timeout: Subprocess timeout in seconds.

        Returns:
            Test creation result dict including the metadata file path.
        """
        args = ["agent", "test", "create"]
        if spec:
            args += ["--spec", str(spec)]
        if api_name:
            args += ["--api-name", api_name]
        if preview:
            args.append("--preview")
        if force_overwrite:
            args.append("--force-overwrite")

        return self._run_capturing(
            args,
            label=f"Creating agent test {api_name or '(prompted)'}",
            timeout=timeout,
        )

    def test_list(self) -> list[dict[str, Any]]:
        """List all available agent tests in the target org.

        Returns:
            List of test summary dicts with name, ID, and creation date.
        """
        result = self._run_capturing(
            ["agent", "test", "list"],
            label="Listing agent tests",
        )
        if isinstance(result, list):
            return result
        return result.get("tests", [])

    def test_run(
        self,
        api_name: str | None = None,
        wait: int | None = None,
        result_format: str = "json",
        output_dir: Path | None = None,
        verbose: bool = False,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Start an agent test run in the org.

        Args:
            api_name: API name of the AiEvaluationDefinition to run.
            wait: Minutes to wait for completion before returning. When omitted,
                the command returns immediately with a job ID.
            result_format: Output format: ``json``, ``human``, ``junit``,
                or ``tap``. Defaults to ``json`` for programmatic use.
            output_dir: Directory to write results into.
            verbose: Include detailed generated data (invoked actions, touched
                objects) in the results — useful for building JSONPath expressions.
            timeout: Subprocess timeout in seconds.

        Returns:
            Test run result dict, or a dict containing a ``jobId`` when the
            test has not yet completed.
        """
        args = ["agent", "test", "run"]
        if api_name:
            args += ["--api-name", api_name]
        if wait is not None:
            args += ["--wait", str(wait)]
        args += ["--result-format", result_format]
        if output_dir:
            args += ["--output-dir", str(output_dir)]
        if verbose:
            args.append("--verbose")

        return self._run_capturing(
            args,
            label=f"Running agent test {api_name or '(all)'}",
            timeout=timeout,
        )

    def test_results(
        self,
        job_id: str,
        result_format: str = "json",
        output_dir: Path | None = None,
        verbose: bool = False,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """Get the results of a completed agent test run.

        Args:
            job_id: Job ID of the completed test run.
            result_format: Output format: ``json``, ``human``, ``junit``,
                or ``tap``.
            output_dir: Directory to write results into.
            verbose: Include detailed generated data in the output.
            timeout: Subprocess timeout in seconds.

        Returns:
            Test results dict.
        """
        args = [
            "agent",
            "test",
            "results",
            "--job-id",
            job_id,
            "--result-format",
            result_format,
        ]
        if output_dir:
            args += ["--output-dir", str(output_dir)]
        if verbose:
            args.append("--verbose")

        return self._run_capturing(
            args,
            label=f"Fetching test results for job {job_id}",
            timeout=timeout,
        )

    def test_resume(
        self,
        job_id: str | None = None,
        use_most_recent: bool = False,
        wait: int | None = None,
        result_format: str = "json",
        output_dir: Path | None = None,
        verbose: bool = False,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Resume a previously started agent test run.

        Either ``job_id`` or ``use_most_recent`` must be provided.

        Args:
            job_id: Job ID of the original test run.
            use_most_recent: Resume the most recently started test run.
            wait: Minutes to wait for the test to complete.
            result_format: Output format: ``json``, ``human``, ``junit``,
                or ``tap``.
            output_dir: Directory to write results into.
            verbose: Include detailed generated data in the output.
            timeout: Subprocess timeout in seconds.

        Returns:
            Test results dict.
        """
        args = ["agent", "test", "resume"]
        if job_id:
            args += ["--job-id", job_id]
        if use_most_recent:
            args.append("--use-most-recent")
        if wait is not None:
            args += ["--wait", str(wait)]
        args += ["--result-format", result_format]
        if output_dir:
            args += ["--output-dir", str(output_dir)]
        if verbose:
            args.append("--verbose")

        return self._run_capturing(
            args,
            label=f"Resuming agent test {job_id or '(most recent)'}",
            timeout=timeout,
        )
