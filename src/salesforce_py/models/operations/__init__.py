"""Operation classes for the Salesforce Models REST API."""

from salesforce_py.models.operations.chat_generations import ChatGenerationsOperations
from salesforce_py.models.operations.embeddings import EmbeddingsOperations
from salesforce_py.models.operations.feedback import FeedbackOperations
from salesforce_py.models.operations.generations import GenerationsOperations

__all__ = [
    "ChatGenerationsOperations",
    "EmbeddingsOperations",
    "FeedbackOperations",
    "GenerationsOperations",
]
