"""Support — data category groups, embedded service, field service, knowledge.

Covers the ``/services/data/vXX.X/support/`` endpoints:

- ``/support/dataCategoryGroups`` — Data category groups visible to the user.
- ``/support/dataCategoryGroups/{group}/dataCategories/{category}`` — Data
  category detail and child categories.
- ``/support/embeddedservice/configuration/{serviceName}`` — Embedded Service
  configuration metadata.
- ``/support/fieldservice/Flow`` — Field Service flow metadata.
- ``/support/fieldservice/ServiceReportTemplate`` — Service report templates.
- ``/support/knowledgeArticles/{articleId|articleUrlName}`` — Knowledge
  article detail.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class SupportOperations(RestBaseOperations):
    """Wrapper for ``/support/...`` resources."""

    # ------------------------------------------------------------------
    # Data category groups
    # ------------------------------------------------------------------

    async def get_data_category_groups(
        self, *, sobject: str | None = None, top_categories_only: bool | None = None
    ) -> dict[str, Any]:
        """Return data category groups visible to the current user."""
        return await self._get(
            "support/dataCategoryGroups",
            params={"sObjectName": sobject, "topCategoriesOnly": top_categories_only},
        )

    async def get_data_category(
        self, group: str, category: str
    ) -> dict[str, Any]:
        """Return a data category and its child categories."""
        return await self._get(
            f"support/dataCategoryGroups/{group}/dataCategories/{category}"
        )

    # ------------------------------------------------------------------
    # Embedded Service
    # ------------------------------------------------------------------

    async def get_embedded_service_configuration(
        self, service_name: str
    ) -> dict[str, Any]:
        """Return metadata for an Embedded Service deployment."""
        return await self._get(
            f"support/embeddedservice/configuration/{service_name}"
        )

    # ------------------------------------------------------------------
    # Field Service
    # ------------------------------------------------------------------

    async def get_field_service_flow(
        self, *, developer_names: list[str] | None = None
    ) -> dict[str, Any]:
        """Return metadata for one or more Field Service flows.

        Args:
            developer_names: Optional list of flow developer names to narrow
                the response.
        """
        return await self._get(
            "support/fieldservice/Flow",
            params={
                "developerNames": ",".join(developer_names)
                if developer_names
                else None
            },
        )

    async def get_field_service_report_templates(
        self, *, developer_names: list[str] | None = None
    ) -> dict[str, Any]:
        """Return metadata for Field Service service report templates."""
        return await self._get(
            "support/fieldservice/ServiceReportTemplate",
            params={
                "developerNames": ",".join(developer_names)
                if developer_names
                else None
            },
        )

    # ------------------------------------------------------------------
    # Knowledge articles
    # ------------------------------------------------------------------

    async def get_knowledge_article(
        self, article_id_or_url_name: str
    ) -> dict[str, Any]:
        """Return online Knowledge article fields accessible to the user.

        Args:
            article_id_or_url_name: Article ID (``kaXXX...``) or URL name.
        """
        return await self._get(
            f"support/knowledgeArticles/{article_id_or_url_name}"
        )
