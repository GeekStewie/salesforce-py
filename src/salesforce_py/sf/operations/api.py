"""SF CLI api command wrappers."""

import json
from pathlib import Path
from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFApiOperations(SFBaseOperations):
    """Wraps ``sf api request`` commands for raw REST and GraphQL API calls.

    REST responses are raw API payloads, not SF CLI JSON envelopes, so REST
    methods use ``include_json=False`` and return ``{"output": "<raw text>"}``.
    GraphQL supports ``--json`` and returns a parsed result dict.
    """

    # ------------------------------------------------------------------
    # REST API
    # ------------------------------------------------------------------

    def rest(
        self,
        url: str,
        method: str = "GET",
        body: str | dict[str, Any] | None = None,
        body_file: Path | None = None,
        headers: dict[str, str] | None = None,
        include: bool = False,
        stream_to_file: Path | None = None,
        request_file: Path | None = None,
        timeout: int = 60,
    ) -> dict[str, Any]:
        """Make an authenticated HTTP request using the Salesforce REST API.

        Args:
            url: REST API resource path (e.g. ``/services/data/v59.0/limits``).
            method: HTTP verb: ``GET``, ``POST``, ``PUT``, ``PATCH``, ``HEAD``,
                ``DELETE``, ``OPTIONS``, or ``TRACE``. Defaults to ``GET``.
            body: Request body as a string or dict (serialised to JSON). Mutually
                exclusive with ``body_file`` and ``request_file``.
            body_file: Path to a file whose contents are sent as the body.
                Mutually exclusive with ``body`` and ``request_file``.
            headers: HTTP headers as a ``{"Key": "Value"}`` dict.
            include: Include the HTTP response status and headers in the output.
            stream_to_file: Stream the response to this file path instead of
                stdout.
            request_file: JSON file containing the full request definition
                (url, method, header, body). Replaces all other request flags.
                Supports Postman collection schema.
            timeout: Subprocess timeout in seconds.

        Returns:
            ``{"output": "<raw response text>"}`` — the Salesforce REST API
            response body (not wrapped in an SF CLI JSON envelope).
        """
        args = ["api", "request", "rest", url, "--method", method.upper()]

        if body is not None:
            body_str = json.dumps(body) if isinstance(body, dict) else body
            args += ["--body", body_str]
        elif body_file is not None:
            # SF CLI uses @filename convention to read body from a file
            args += ["--body", f"@{body_file}"]

        if headers:
            for key, value in headers.items():
                args += ["--header", f"{key}: {value}"]

        if include:
            args.append("--include")

        if stream_to_file:
            args += ["--stream-to-file", str(stream_to_file)]

        if request_file:
            args += ["--file", str(request_file)]

        return self._run_capturing(
            args,
            label=f"{method.upper()} {url}",
            timeout=timeout,
            include_json=False,
        )

    def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        include: bool = False,
        stream_to_file: Path | None = None,
        timeout: int = 60,
    ) -> dict[str, Any]:
        """Perform a GET request against the Salesforce REST API.

        Args:
            url: REST API resource path.
            headers: Optional HTTP headers.
            include: Include HTTP response status and headers in output.
            stream_to_file: Stream response to this file.
            timeout: Subprocess timeout in seconds.

        Returns:
            ``{"output": "<raw response text>"}``.
        """
        return self.rest(
            url,
            method="GET",
            headers=headers,
            include=include,
            stream_to_file=stream_to_file,
            timeout=timeout,
        )

    def post(
        self,
        url: str,
        body: str | dict[str, Any] | None = None,
        body_file: Path | None = None,
        headers: dict[str, str] | None = None,
        include: bool = False,
        timeout: int = 60,
    ) -> dict[str, Any]:
        """Perform a POST request against the Salesforce REST API.

        Args:
            url: REST API resource path.
            body: Request body as a string or dict.
            body_file: Path to a file to use as the request body.
            headers: Optional HTTP headers.
            include: Include HTTP response status and headers in output.
            timeout: Subprocess timeout in seconds.

        Returns:
            ``{"output": "<raw response text>"}``.
        """
        return self.rest(
            url,
            method="POST",
            body=body,
            body_file=body_file,
            headers=headers,
            include=include,
            timeout=timeout,
        )

    def patch(
        self,
        url: str,
        body: str | dict[str, Any] | None = None,
        body_file: Path | None = None,
        headers: dict[str, str] | None = None,
        include: bool = False,
        timeout: int = 60,
    ) -> dict[str, Any]:
        """Perform a PATCH request against the Salesforce REST API.

        Args:
            url: REST API resource path.
            body: Request body as a string or dict.
            body_file: Path to a file to use as the request body.
            headers: Optional HTTP headers.
            include: Include HTTP response status and headers in output.
            timeout: Subprocess timeout in seconds.

        Returns:
            ``{"output": "<raw response text>"}``.
        """
        return self.rest(
            url,
            method="PATCH",
            body=body,
            body_file=body_file,
            headers=headers,
            include=include,
            timeout=timeout,
        )

    def delete(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        include: bool = False,
        timeout: int = 60,
    ) -> dict[str, Any]:
        """Perform a DELETE request against the Salesforce REST API.

        Args:
            url: REST API resource path.
            headers: Optional HTTP headers.
            include: Include HTTP response status and headers in output.
            timeout: Subprocess timeout in seconds.

        Returns:
            ``{"output": "<raw response text>"}``.
        """
        return self.rest(
            url,
            method="DELETE",
            headers=headers,
            include=include,
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # GraphQL API
    # ------------------------------------------------------------------

    def graphql(
        self,
        body: str | Path,
        include: bool = False,
        stream_to_file: Path | None = None,
        timeout: int = 60,
    ) -> dict[str, Any]:
        """Execute a GraphQL statement against the Salesforce GraphQL API.

        Args:
            body: GraphQL statement as a string, or a :class:`Path` to a file
                containing the statement.
            include: Include HTTP response status and headers in output.
            stream_to_file: Stream the response to this file.
            timeout: Subprocess timeout in seconds.

        Returns:
            Parsed result dict from the GraphQL response.
        """
        body_arg = str(body) if isinstance(body, Path) else body
        args = ["api", "request", "graphql", "--body", body_arg]

        if include:
            args.append("--include")

        if stream_to_file:
            args += ["--stream-to-file", str(stream_to_file)]

        return self._run_capturing(
            args,
            label="Executing GraphQL request",
            timeout=timeout,
        )
