"""Wrappers for `sf project deploy` and `sf project retrieve` commands."""

from __future__ import annotations

import asyncio
from typing import Any

from salesforce_py.sf._runner import run


async def deploy(
    source_dir: str,
    *,
    target_org: str,
    wait: int = 33,
) -> dict[str, Any]:
    """Deploy source metadata to a Salesforce org.

    Equivalent to::

        sf project deploy start --source-dir <source_dir> \\
            --target-org <target_org> --wait <wait> --json

    Parameters
    ----------
    source_dir:
        Path to the directory containing the source to deploy.
    target_org:
        Alias or username of the target org.
    wait:
        Number of minutes to wait for the deploy to complete. Defaults to 33.

    Returns
    -------
    dict
        Parsed JSON deploy result.
    """
    return await run(
        [
            "project",
            "deploy",
            "start",
            "--source-dir",
            source_dir,
            "--target-org",
            target_org,
            "--wait",
            str(wait),
        ]
    )


async def retrieve(
    source_dir: str,
    *,
    target_org: str,
) -> dict[str, Any]:
    """Retrieve source metadata from a Salesforce org.

    Equivalent to::

        sf project retrieve start --source-dir <source_dir> \\
            --target-org <target_org> --json

    Parameters
    ----------
    source_dir:
        Path to the directory to retrieve metadata into.
    target_org:
        Alias or username of the target org.

    Returns
    -------
    dict
        Parsed JSON retrieve result.
    """
    return await run(
        [
            "project",
            "retrieve",
            "start",
            "--source-dir",
            source_dir,
            "--target-org",
            target_org,
        ]
    )


def deploy_sync(
    source_dir: str,
    *,
    target_org: str,
    wait: int = 33,
) -> dict[str, Any]:
    """Synchronous wrapper around :func:`deploy`."""
    return asyncio.run(deploy(source_dir, target_org=target_org, wait=wait))


def retrieve_sync(
    source_dir: str,
    *,
    target_org: str,
) -> dict[str, Any]:
    """Synchronous wrapper around :func:`retrieve`."""
    return asyncio.run(retrieve(source_dir, target_org=target_org))
