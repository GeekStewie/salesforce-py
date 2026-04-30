"""sObjects — describe, CRUD, relationships, layouts, list views, blobs.

Covers all endpoints under ``/services/data/vXX.X/sobjects/``:

- ``/sobjects`` — Describe global (and org encoding / max batch size).
- ``/sobjects/{sObject}`` — Basic information about a specific object, or
  create (POST) a new record for that object.
- ``/sobjects/{sObject}/describe`` — Full metadata for a specific object.
- ``/sobjects/{sObject}/describe/approvalLayouts`` — Approval layouts.
- ``/sobjects/{sObject}/describe/compactLayouts`` — Compact layouts.
- ``/sobjects/{sObject}/describe/layouts`` (+ ``/Global/describe/layouts``)
  — Page layouts.
- ``/sobjects/{sObject}/describe/namedLayouts/{layoutName}`` — Named layouts.
- ``/sobjects/{sObject}/{id}`` — CRUD on a record by ID.
- ``/sobjects/{sObject}/{id}/{relationship}`` — Relationship traversal.
- ``/sobjects/{sObject}/{id}/{blobField}`` — Blob field download.
- ``/sobjects/{sObject}/{id}/richTextImageFields/{fieldName}/{contentReferenceId}``
  — Rich text image download.
- ``/sobjects/{sObject}/{fieldName}/{fieldValue}`` — Upsert by external ID.
- ``/sobjects/{sObject}/deleted`` / ``/updated`` — Change feeds.
- ``/sobjects/{sObject}/listviews`` — List views and list view execution.
- ``/sobjects/{sObject}/quickActions`` — sObject quick actions.
- ``/sobjects/relevantItems`` — Current user's relevant items.
- ``/sobjects/PlatformAction`` — Actions in the UI for a user/context/record.
- ``/sobjects/{sObject}/eventSchema`` — Platform event schemas by event name.
- ``/sobjects/Event/{id}/fromThisEventOnwards`` — Recurring event series delete.
- ``/sobjects/User/{userId}/password`` — User password ops.
- ``/sobjects/SelfServiceUser/{selfServiceUserId}/password`` — Self-service
  user password ops.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class SObjectsOperations(RestBaseOperations):
    """Wrapper for every ``/sobjects/...`` resource documented in the REST API."""

    # ------------------------------------------------------------------
    # Describe
    # ------------------------------------------------------------------

    async def describe_global(self) -> dict[str, Any]:
        """Return the Describe Global payload for the org.

        Includes the list of sObjects the user can access, the org's default
        encoding, and the maximum batch size permitted in queries.
        """
        return await self._get("sobjects")

    async def describe_object_basic(self, object_name: str) -> dict[str, Any]:
        """Return basic metadata for an sObject (labels, URLs, recent items)."""
        return await self._get(f"sobjects/{object_name}")

    async def describe_object(self, object_name: str) -> dict[str, Any]:
        """Return the full describe payload for an sObject (fields, child relationships, etc.)."""
        return await self._get(f"sobjects/{object_name}/describe")

    async def describe_approval_layouts(
        self, object_name: str, *, approval_process_name: str | None = None
    ) -> dict[str, Any]:
        """Return the approval layouts for an sObject."""
        path = f"sobjects/{object_name}/describe/approvalLayouts"
        if approval_process_name:
            path = f"{path}/{approval_process_name}"
        return await self._get(path)

    async def describe_compact_layouts(
        self, object_name: str, *, record_type_id: str | None = None
    ) -> dict[str, Any]:
        """Return the compact layouts for an sObject."""
        path = f"sobjects/{object_name}/describe/compactLayouts"
        if record_type_id:
            path = f"{path}/{record_type_id}"
        return await self._get(path)

    async def describe_layouts(
        self, object_name: str, *, record_type_id: str | None = None
    ) -> dict[str, Any]:
        """Return page layouts for an sObject (or a specific record type)."""
        path = f"sobjects/{object_name}/describe/layouts"
        if record_type_id:
            path = f"{path}/{record_type_id}"
        return await self._get(path)

    async def describe_global_layouts(self) -> dict[str, Any]:
        """Return page layouts from ``/sobjects/Global/describe/layouts``."""
        return await self._get("sobjects/Global/describe/layouts")

    async def describe_named_layout(
        self, object_name: str, layout_name: str
    ) -> dict[str, Any]:
        """Return an alternate named layout for an sObject."""
        return await self._get(f"sobjects/{object_name}/describe/namedLayouts/{layout_name}")

    async def compact_layouts(self, object_list: list[str]) -> dict[str, Any]:
        """Return compact layouts for multiple objects at once.

        Maps to ``/services/data/vXX.X/compactLayouts?q=objectList``.
        """
        return await self._get("compactLayouts", params={"q": ",".join(object_list)})

    # ------------------------------------------------------------------
    # Record CRUD
    # ------------------------------------------------------------------

    async def create(
        self, object_name: str, record: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a new record.

        Args:
            object_name: API name of the target sObject.
            record: Field/value dict matching the target schema.

        Returns:
            Dict with ``id`` and ``success`` keys.
        """
        return await self._post(f"sobjects/{object_name}", json=record)

    async def get(
        self, object_name: str, record_id: str, *, fields: list[str] | None = None
    ) -> dict[str, Any]:
        """Retrieve a record by ID, optionally filtering fields."""
        params = {"fields": ",".join(fields)} if fields else None
        return await self._get(f"sobjects/{object_name}/{record_id}", params=params)

    async def update(
        self, object_name: str, record_id: str, record: dict[str, Any]
    ) -> dict[str, Any]:
        """Patch a record by ID."""
        return await self._patch(f"sobjects/{object_name}/{record_id}", json=record)

    async def delete(self, object_name: str, record_id: str) -> dict[str, Any]:
        """Delete a record by ID."""
        return await self._delete(f"sobjects/{object_name}/{record_id}")

    async def upsert(
        self,
        object_name: str,
        external_id_field: str,
        external_id: str,
        record: dict[str, Any],
    ) -> dict[str, Any]:
        """Upsert a record by external ID.

        Maps to ``PATCH /sobjects/{sObject}/{fieldName}/{fieldValue}``.
        Creates a new record when *external_id* is not yet assigned,
        otherwise updates the existing record.
        """
        return await self._patch(
            f"sobjects/{object_name}/{external_id_field}/{external_id}",
            json=record,
        )

    async def get_by_external_id(
        self,
        object_name: str,
        external_id_field: str,
        external_id: str,
        *,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Retrieve a record by its external ID field value."""
        params = {"fields": ",".join(fields)} if fields else None
        return await self._get(
            f"sobjects/{object_name}/{external_id_field}/{external_id}",
            params=params,
        )

    async def delete_by_external_id(
        self,
        object_name: str,
        external_id_field: str,
        external_id: str,
    ) -> dict[str, Any]:
        """Delete a record by its external ID field value."""
        return await self._delete(
            f"sobjects/{object_name}/{external_id_field}/{external_id}",
        )

    # ------------------------------------------------------------------
    # Relationships / blobs / rich text images
    # ------------------------------------------------------------------

    async def get_relationship(
        self,
        object_name: str,
        record_id: str,
        relationship_name: str,
        *,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Traverse a parent/child relationship from a record.

        Maps to ``GET /sobjects/{sObject}/{id}/{relationshipName}``.
        """
        params = {"fields": ",".join(fields)} if fields else None
        return await self._get(
            f"sobjects/{object_name}/{record_id}/{relationship_name}",
            params=params,
        )

    async def update_relationship(
        self,
        object_name: str,
        record_id: str,
        relationship_name: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Update the record associated with a lookup/master-detail field."""
        return await self._patch(
            f"sobjects/{object_name}/{record_id}/{relationship_name}",
            json=body,
        )

    async def delete_relationship(
        self, object_name: str, record_id: str, relationship_name: str
    ) -> dict[str, Any]:
        """Delete the record associated with a lookup/master-detail field."""
        return await self._delete(
            f"sobjects/{object_name}/{record_id}/{relationship_name}"
        )

    async def get_blob(
        self, object_name: str, record_id: str, blob_field: str
    ) -> bytes:
        """Download a blob field (Attachment body, ContentVersion version data, etc.)."""
        return await self._get_bytes(
            f"sobjects/{object_name}/{record_id}/{blob_field}"
        )

    async def get_rich_text_image(
        self,
        object_name: str,
        record_id: str,
        field_name: str,
        content_reference_id: str,
    ) -> bytes:
        """Download an image embedded in a rich text area field."""
        return await self._get_bytes(
            f"sobjects/{object_name}/{record_id}"
            f"/richTextImageFields/{field_name}/{content_reference_id}"
        )

    # ------------------------------------------------------------------
    # Change feeds
    # ------------------------------------------------------------------

    async def get_deleted(
        self, object_name: str, *, start: str, end: str
    ) -> dict[str, Any]:
        """Return records of a given type deleted between *start* and *end*.

        Args:
            object_name: API name of the sObject.
            start: ISO-8601 datetime (e.g. ``2026-01-01T00:00:00Z``).
            end: ISO-8601 datetime.
        """
        return await self._get(
            f"sobjects/{object_name}/deleted",
            params={"start": start, "end": end},
        )

    async def get_updated(
        self, object_name: str, *, start: str, end: str
    ) -> dict[str, Any]:
        """Return IDs of records of a given type updated between *start* and *end*."""
        return await self._get(
            f"sobjects/{object_name}/updated",
            params={"start": start, "end": end},
        )

    # ------------------------------------------------------------------
    # List views
    # ------------------------------------------------------------------

    async def list_views(
        self, object_name: str, *, list_view_id: str | None = None
    ) -> dict[str, Any]:
        """Return list views for an object, or a single list view by ID."""
        path = f"sobjects/{object_name}/listviews"
        if list_view_id:
            path = f"{path}/{list_view_id}"
        return await self._get(path)

    async def list_view_results(
        self,
        object_name: str,
        list_view_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        q: str | None = None,
    ) -> dict[str, Any]:
        """Run the SOQL behind a list view and return the rendered rows."""
        return await self._get(
            f"sobjects/{object_name}/listviews/{list_view_id}/results",
            params={"limit": limit, "offset": offset, "q": q},
        )

    async def describe_list_view(
        self, object_name: str, query_locator: str
    ) -> dict[str, Any]:
        """Return the detailed definition of a list view (columns + SOQL)."""
        return await self._get(
            f"sobjects/{object_name}/listviews/{query_locator}/describe"
        )

    async def recent_list_views(self, object_name: str) -> dict[str, Any]:
        """Return the recently used list views for an object."""
        return await self._get(f"sobjects/{object_name}/listviews/recent")

    # ------------------------------------------------------------------
    # Quick actions
    # ------------------------------------------------------------------

    async def sobject_quick_actions(
        self,
        object_name: str,
        *,
        action_name: str | None = None,
        describe: bool = False,
        default_values: bool = False,
    ) -> dict[str, Any]:
        """Access an sObject's quick actions.

        Args:
            object_name: Target sObject.
            action_name: Optional quick action developer name. When present,
                the URL narrows to that action.
            describe: When True, append ``/describe`` to return action metadata.
            default_values: When True, append ``/defaultValues`` to return
                the action's pre-populated field values.
        """
        path = f"sobjects/{object_name}/quickActions"
        if action_name:
            path = f"{path}/{action_name}"
            if describe:
                path = f"{path}/describe"
            if default_values:
                path = f"{path}/defaultValues"
        return await self._get(path)

    async def invoke_sobject_quick_action(
        self,
        object_name: str,
        action_name: str,
        context_id: str | None = None,
        record: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Invoke an sObject quick action.

        Args:
            object_name: Target sObject.
            action_name: Quick action developer name.
            context_id: Optional record ID supplying the action's context.
            record: Optional field/value overrides for the record the action
                creates.
        """
        payload: dict[str, Any] = {}
        if context_id is not None:
            payload["contextId"] = context_id
        if record is not None:
            payload["record"] = record
        return await self._post(
            f"sobjects/{object_name}/quickActions/{action_name}",
            json=payload or None,
        )

    # ------------------------------------------------------------------
    # Relevant items, platform actions, event schemas
    # ------------------------------------------------------------------

    async def get_relevant_items(self, **params: Any) -> dict[str, Any]:
        """Return the current user's most relevant items.

        Args:
            **params: Optional filters — ``sobjects``, ``mode``, ``limit``,
                ``lastUpdatedId``. See the REST API Developer Guide for the
                full list.
        """
        return await self._get("sobjects/relevantItems", params=params)

    async def get_platform_actions(self, **params: Any) -> dict[str, Any]:
        """Return standard / custom / productivity actions for the current UI context.

        Args:
            **params: Filters such as ``parentEntity``, ``recordId``,
                ``contextUserId``, ``context``, ``formFactor``, ``apiName``.
        """
        return await self._get("sobjects/PlatformAction", params=params)

    async def get_event_schema_by_name(self, event_name: str) -> dict[str, Any]:
        """Return the schema for a platform event by its developer name."""
        return await self._get(f"sobjects/{event_name}/eventSchema")

    async def get_event_schema_by_id(self, schema_id: str) -> dict[str, Any]:
        """Return a platform event schema by schema ID.

        Maps to ``/event/eventSchema/{schemaId}`` — available in REST API
        version 40.0 and later.
        """
        return await self._get(f"event/eventSchema/{schema_id}")

    # ------------------------------------------------------------------
    # Recurring event series
    # ------------------------------------------------------------------

    async def delete_event_from_this_onwards(self, event_id: str) -> dict[str, Any]:
        """Remove one or more ``IsRecurrence2`` events in a series.

        Maps to ``DELETE /sobjects/Event/{id}/fromThisEventOnwards``.
        """
        return await self._delete(f"sobjects/Event/{event_id}/fromThisEventOnwards")

    # ------------------------------------------------------------------
    # User password management
    # ------------------------------------------------------------------

    async def get_user_password_status(self, user_id: str) -> dict[str, Any]:
        """Return a user password's expiration status."""
        return await self._get(f"sobjects/User/{user_id}/password")

    async def set_user_password(
        self, user_id: str, new_password: str
    ) -> dict[str, Any]:
        """Set a user's password."""
        return await self._post(
            f"sobjects/User/{user_id}/password",
            json={"NewPassword": new_password},
        )

    async def reset_user_password(self, user_id: str) -> dict[str, Any]:
        """Initiate a user password reset."""
        return await self._delete(f"sobjects/User/{user_id}/password")

    async def get_self_service_user_password_status(
        self, self_service_user_id: str
    ) -> dict[str, Any]:
        """Return a self-service user password's expiration status."""
        return await self._get(
            f"sobjects/SelfServiceUser/{self_service_user_id}/password"
        )

    async def set_self_service_user_password(
        self, self_service_user_id: str, new_password: str
    ) -> dict[str, Any]:
        """Set a self-service user's password."""
        return await self._post(
            f"sobjects/SelfServiceUser/{self_service_user_id}/password",
            json={"NewPassword": new_password},
        )

    async def reset_self_service_user_password(
        self, self_service_user_id: str
    ) -> dict[str, Any]:
        """Initiate a self-service user password reset."""
        return await self._delete(
            f"sobjects/SelfServiceUser/{self_service_user_id}/password"
        )
