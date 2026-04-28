"""SF CLI ui-bundle command wrappers."""

from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFUiBundleOperations(SFBaseOperations):
    """Wraps ``sf ui-bundle`` commands for local UI bundle development.

    UI bundles host non-native Salesforce UI frameworks (e.g. React) as
    first-class Salesforce Platform apps via the ``UiBundle`` metadata type.
    """

    def dev(
        self,
        name: str | None = None,
        url: str | None = None,
        port: int | None = None,
        open_browser: bool = False,
        timeout: int = 3600,
    ) -> dict[str, Any]:
        """Preview a UI bundle locally without deploying to an org.

        Starts a local development server and a proxy server that injects
        authentication headers so the bundle can make authenticated API calls
        to Salesforce.

        This is a long-running command (the server runs until interrupted).
        ``include_json=False`` is used because the command streams output
        rather than emitting a single JSON envelope.

        Args:
            name: Name of the UI bundle to preview.  If omitted, the command
                auto-discovers ``ui-bundle.json`` files; it prompts when
                multiple are found.
            url: URL where the developer server runs, e.g.
                ``"http://localhost:5173"``.  Overrides the value in
                ``ui-bundle.json``.
            port: Local port for the proxy server.
            open_browser: Automatically open the proxy server URL in the
                default browser when the dev server is ready.
            timeout: Subprocess timeout in seconds (default 3600 — 1 hour).

        Returns:
            Raw output dict (``{"output": ...}``).
        """
        args: list[str] = ["ui-bundle", "dev"]
        if name is not None:
            args += ["--name", name]
        if url is not None:
            args += ["--url", url]
        if port is not None:
            args += ["--port", str(port)]
        if open_browser:
            args.append("--open")
        return self._run_capturing(
            args,
            label="Starting UI bundle dev server",
            timeout=timeout,
            include_api_version=False,
            include_json=False,
        )
