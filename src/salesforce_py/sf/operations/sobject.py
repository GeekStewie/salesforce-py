"""SF CLI sobject command wrappers."""

from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFSobjectOperations(SFBaseOperations):
    """Wraps ``sf sobject`` commands for SObject introspection."""

    def describe(
        self,
        sobject: str,
        use_tooling_api: bool = False,
    ) -> dict[str, Any]:
        """Display the metadata for a standard or custom object.

        Args:
            sobject: API name of the object (e.g. ``Account``,
                ``MyObject__c``, or a Tooling API object such as
                ``ApexCodeCoverage``).
            use_tooling_api: Use the Tooling API instead of the standard
                Metadata API.

        Returns:
            DescribeSObjectResult dict containing fields, childRelationships,
            recordTypeInfos, and all other describe properties.
        """
        args: list[str] = ["sobject", "describe", "--sobject", sobject]
        if use_tooling_api:
            args.append("--use-tooling-api")
        return self._run_capturing(
            args,
            label=f"Describing {sobject}",
        )

    def list_sobjects(self, category: str = "ALL") -> list[str]:
        """List all Salesforce objects of a specified category.

        Args:
            category: Object category to list — ``ALL``, ``custom``, or
                ``standard`` (case-insensitive; default ``ALL``).

        Returns:
            List of SObject API name strings.
        """
        result = self._run_capturing(
            ["sobject", "list", "--sobject", category],
            label=f"Listing {category} SObjects",
        )
        if isinstance(result, list):
            return result
        return result.get("result", [])

    def list_fields(self, sobject: str) -> list[dict[str, Any]]:
        """Return the field metadata for an SObject.

        Convenience wrapper around :meth:`describe` that extracts only the
        ``fields`` array from the DescribeSObjectResult.

        Args:
            sobject: API name of the object.

        Returns:
            List of Field dicts from the DescribeSObjectResult.
        """
        result = self.describe(sobject)
        fields = result.get("fields", [])
        if isinstance(fields, list):
            return fields
        return []
