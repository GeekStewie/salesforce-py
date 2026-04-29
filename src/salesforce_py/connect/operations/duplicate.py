"""Duplicate (dedupe) Connect API operations.

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class DuplicateOperations(ConnectBaseOperations):
    """Wrapper for ``/dedupe/...`` endpoints (v42.0+)."""

    async def get_directory(self) -> dict[str, Any]:
        """Get a directory of duplicate resources.

        Returns:
            Duplicate Directory dict.
        """
        return await self._get("dedupe")

    async def list_job_definitions(self) -> dict[str, Any]:
        """Get duplicate job definitions.

        Returns:
            Duplicate Job Definition Collection dict.
        """
        return await self._get("dedupe/job-definitions")

    async def get_job_definition(self, job_definition_id: str) -> dict[str, Any]:
        """Get a duplicate job definition.

        Args:
            job_definition_id: Duplicate job definition ID.

        Returns:
            Duplicate Job Definition dict.
        """
        job_definition_id = self._ensure_18(job_definition_id)
        return await self._get(f"dedupe/job-definitions/{job_definition_id}")

    async def list_jobs(self) -> dict[str, Any]:
        """Get duplicate jobs.

        Returns:
            Duplicate Job Collection dict.
        """
        return await self._get("dedupe/jobs")

    async def run_job(self, job_definition_id: str) -> dict[str, Any]:
        """Run a duplicate job.

        Args:
            job_definition_id: Duplicate job definition ID.

        Returns:
            Duplicate Job dict.
        """
        job_definition_id = self._ensure_18(job_definition_id)
        return await self._post(
            "dedupe/jobs", json={"duplicateJobDefId": job_definition_id}
        )

    async def get_job(self, job_id: str) -> dict[str, Any]:
        """Get status of a duplicate job.

        Args:
            job_id: Duplicate job ID.

        Returns:
            Duplicate Job dict.
        """
        job_id = self._ensure_18(job_id)
        return await self._get(f"dedupe/jobs/{job_id}")

    async def cancel_job(self, job_id: str) -> dict[str, Any]:
        """Cancel a duplicate job.

        Only ``Canceled`` is a valid status value.

        Args:
            job_id: Duplicate job ID.

        Returns:
            Duplicate Job dict.
        """
        job_id = self._ensure_18(job_id)
        return await self._patch(
            f"dedupe/jobs/{job_id}", json={"status": "Canceled"}
        )

    async def delete_job_results(self, job_id: str) -> dict[str, Any]:
        """Delete duplicate job results.

        Args:
            job_id: Duplicate job ID.

        Returns:
            Empty dict on success.
        """
        job_id = self._ensure_18(job_id)
        return await self._delete(f"dedupe/jobs/{job_id}/results")
