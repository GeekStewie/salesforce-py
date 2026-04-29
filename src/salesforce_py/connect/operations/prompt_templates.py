"""Prompt Templates Connect API operations.

Uses a session rooted at ``/services/data/vXX.X/einstein/`` — the client
supplies a dedicated ``_einstein_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class PromptTemplatesOperations(ConnectBaseOperations):
    """Wrapper for ``/einstein/prompt-templates/...`` endpoints (v60.0+)."""

    async def list_prompt_templates(
        self,
        *,
        fields: list[str] | None = None,
        is_active: bool | None = None,
        offset: int | None = None,
        page_limit: int | None = None,
        query: str | None = None,
        related_entity: str | None = None,
        sort_by: str | None = None,
        template_type: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of prompt templates based on specified filters (v62.0+).

        Args:
            fields: Comma-separated list of prompt template record fields to
                return (e.g. ``["createdDate"]``). If unspecified, all fields.
            is_active: Return active prompt templates only. Default ``false``.
            offset: Pagination — number of rows to skip. Default ``0``.
            page_limit: Pagination — max records per page. Default ``50``.
            query: User-entered search string.
            related_entity: Related entity to filter by (e.g. ``"Contact"``).
            sort_by: Field to sort records by (e.g. ``"createdDate"``).
            template_type: Prompt template type to filter by (e.g.
                ``"einstein_gpt__salesEmail"``).

        Returns:
            Einstein Prompt Record Collection dict.
        """
        params: dict[str, Any] = {}
        if fields is not None:
            params["fields"] = ",".join(fields)
        if is_active is not None:
            params["isActive"] = str(is_active).lower()
        if offset is not None:
            params["offset"] = offset
        if page_limit is not None:
            params["pageLimit"] = page_limit
        if query is not None:
            params["query"] = query
        if related_entity is not None:
            params["relatedEntity"] = related_entity
        if sort_by is not None:
            params["sortBy"] = sort_by
        if template_type is not None:
            params["type"] = template_type
        return await self._get("prompt-templates", params=params)

    async def generate(
        self,
        prompt_template_dev_name: str,
        *,
        input_params: dict[str, Any],
        additional_config: dict[str, Any],
        is_preview: bool = False,
        citation_mode: str | None = None,
        output_language: str | None = None,
        tags: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate a response based on a prompt template (v60.0+).

        Args:
            prompt_template_dev_name: Developer name or ID of the prompt
                template record.
            input_params: Parameters/values to resolve the template. Usually
                shaped as ``{"valueMap": {"Input:Name": {"value": ...}, ...}}``.
            additional_config: LLM provider configuration (required),
                e.g. ``{"applicationName": "PromptTemplateGenerationsInvocable"}``.
            is_preview: Resolve the template only (``True``) or resolve and
                generate an LLM response (``False``). Default ``False``.
            citation_mode: Citation mode — ``"post_generation"`` or ``"off"``
                (v62.0+).
            output_language: Language code for the LLM response (v61.0+).
            tags: Optional wrapped-value tag map (v62.0+).

        Returns:
            Einstein Prompt Template Generations response dict.
        """
        payload: dict[str, Any] = {
            "isPreview": is_preview,
            "inputParams": input_params,
            "additionalConfig": additional_config,
        }
        if citation_mode is not None:
            payload["citationMode"] = citation_mode
        if output_language is not None:
            payload["outputLanguage"] = output_language
        if tags is not None:
            payload["tags"] = tags
        return await self._post(
            f"prompt-templates/{prompt_template_dev_name}/generations",
            json=payload,
        )
