"""Operation namespaces exposed by :class:`~salesforce_py.bulk.BulkClient`."""

from salesforce_py.bulk.operations.ingest import IngestOperations
from salesforce_py.bulk.operations.query import QueryOperations

__all__ = ["IngestOperations", "QueryOperations"]
