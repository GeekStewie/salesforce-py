"""SF CLI lightning command wrappers."""

from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFLightningOperations(SFBaseOperations):
    """Wraps ``sf lightning dev`` commands for local Lightning development.

    All three commands launch long-running local development servers that
    stream output until interrupted. ``dev_app`` and ``dev_site`` have no
    ``--json`` flag in the CLI, so ``include_json=False`` is used for those.
    The default timeout is set high (3600 s) since servers run until the
    caller terminates them.
    """

    def dev_app(
        self,
        name: str | None = None,
        device_type: str | None = None,
        device_id: str | None = None,
        timeout: int = 3600,
    ) -> dict[str, Any]:
        """Preview a Lightning Experience app locally in real-time.

        Launches a local dev server with hot-reload support. Changes to LWC
        HTML, CSS, and non-API-breaking JavaScript are reflected immediately
        without deploying. Run interactively; the server streams output until
        stopped.

        If run without ``name`` or ``device_type``, the CLI prompts
        interactively for a device and then an app.

        Args:
            name: Name of the Lightning Experience app to preview.
            device_type: Preview device type — ``desktop``, ``ios``, or
                ``android``.
            device_id: ID of the mobile device to use when ``device_type``
                is ``ios`` or ``android``. Defaults to the first available
                device.
            timeout: Subprocess timeout in seconds (default 3600).

        Returns:
            Raw stdout under the ``output`` key (no JSON envelope).
        """
        args = ["lightning", "dev", "app"]

        if name:
            args += ["--name", name]

        if device_type:
            args += ["--device-type", device_type]

        if device_id:
            args += ["--device-id", device_id]

        return self._run_capturing(
            args,
            label="Starting Lightning app local dev server",
            timeout=timeout,
            include_json=False,
        )

    def dev_component(
        self,
        name: str | None = None,
        client_select: bool = False,
        timeout: int = 3600,
    ) -> dict[str, Any]:
        """Preview LWC components in isolation.

        Launches an isolated development environment with hot module
        replacement (HMR). Changes to component HTML, CSS, and
        non-API-breaking JavaScript are reflected immediately.

        If run without ``name``, the CLI prompts interactively for a
        component unless ``client_select=True``.

        Args:
            name: Name of the component to preview.
            client_select: Launch preview without selecting a component
                server-side (selection happens in the browser).
            timeout: Subprocess timeout in seconds (default 3600).

        Returns:
            Result dict from the SF CLI JSON envelope, or raw stdout when
            no JSON is returned.
        """
        args = ["lightning", "dev", "component"]

        if name:
            args += ["--name", name]

        if client_select:
            args.append("--client-select")

        return self._run_capturing(
            args,
            label="Starting Lightning component local dev server",
            timeout=timeout,
        )

    def dev_site(
        self,
        name: str | None = None,
        timeout: int = 3600,
    ) -> dict[str, Any]:
        """Preview an Experience Builder site locally in real-time.

        Launches a local dev server with hot-reload support. Changes to LWC
        HTML, CSS, and non-API-breaking JavaScript are reflected immediately
        without deploying or republishing the site.

        If run without ``name``, the CLI prompts interactively for a site.

        Args:
            name: Name of the Experience Builder site to preview. Must match
                a site name in the current org.
            timeout: Subprocess timeout in seconds (default 3600).

        Returns:
            Raw stdout under the ``output`` key (no JSON envelope).
        """
        args = ["lightning", "dev", "site"]

        if name:
            args += ["--name", name]

        return self._run_capturing(
            args,
            label="Starting Lightning site local dev server",
            timeout=timeout,
            include_json=False,
        )
