"""SF CLI community command wrappers."""

from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFCommunityOperations(SFBaseOperations):
    """Wraps ``sf community`` commands for Experience Cloud site management."""

    def create(
        self,
        name: str,
        template_name: str,
        url_path_prefix: str | None = None,
        description: str | None = None,
        template_params: dict[str, str] | None = None,
        timeout: int = 660,
    ) -> dict[str, Any]:
        """Create an Experience Cloud site using a template.

        Site creation is an async job; the result contains a ``jobId`` that
        can be used to poll ``BackgroundOperation`` for status. The job
        times out after 10 minutes if not completed.

        Args:
            name: Name of the site to create.
            template_name: Template to use (e.g. ``Customer Service``,
                ``Partner Central``, ``Build Your Own (LWR)``). Run
                :meth:`list_templates` to see available templates.
            url_path_prefix: URL path appended to the org domain, e.g.
                ``customers`` produces
                ``https://MyDomain.my.site.com/customers``.
            description: Description shown in Digital Experiences - All Sites.
            template_params: Additional template parameters passed as
                positional ``key=value`` arguments (e.g.
                ``{"templateParams.AuthenticationType": "UNAUTHENTICATED"}``).
            timeout: Subprocess timeout in seconds (default 660 — slightly
                above the 10-minute async job limit).

        Returns:
            Result dict containing ``jobId`` for the async creation job.
        """
        args = [
            "community",
            "create",
            "--name",
            name,
            "--template-name",
            template_name,
        ]

        if url_path_prefix:
            args += ["--url-path-prefix", url_path_prefix]

        if description:
            args += ["--description", description]

        # Template params are passed as positional key=value arguments
        if template_params:
            for key, value in template_params.items():
                args.append(f"{key}={value}")

        return self._run_capturing(
            args,
            label=f"Creating Experience Cloud site '{name}'",
            timeout=timeout,
        )

    def list_templates(self) -> list[dict[str, Any]]:
        """Retrieve the list of Experience Cloud templates available in the org.

        Returns:
            List of template summary dicts.
        """
        result = self._run_capturing(
            ["community", "list", "template"],
            label="Listing Experience Cloud templates",
        )
        if isinstance(result, list):
            return result
        return result.get("templates", [])

    def publish(self, name: str, timeout: int = 960) -> dict[str, Any]:
        """Publish an Experience Builder site to make it live.

        Each publish updates the live site with the latest changes. The first
        publish makes the site URL live and enables login access. The job
        times out after 15 minutes if not completed.

        Args:
            name: Name of the Experience Builder site to publish.
            timeout: Subprocess timeout in seconds (default 960 — slightly
                above the 15-minute async job limit).

        Returns:
            Result dict containing ``jobId`` for the async publish job.
        """
        return self._run_capturing(
            ["community", "publish", "--name", name],
            label=f"Publishing Experience Cloud site '{name}'",
            timeout=timeout,
        )
