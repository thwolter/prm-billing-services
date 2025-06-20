from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.domain.models.subject import Subject
from src.domain.models.usage import TokenQuotaResponse, UsageEvent


class AbstractMeteringClient(ABC):
    """
    Abstract base class defining the interface for metering clients.
    This abstraction allows for easy swapping of metering providers.
    """

    @abstractmethod
    def record_usage(self, subject_id: str, usage_event: UsageEvent) -> bool:
        """
        Record usage for a subject.

        Args:
            subject_id: The ID of the subject.
            usage_event: The usage event data.

        Returns:
            True if the usage was successfully recorded, False otherwise.
        """
        pass

    @abstractmethod
    def get_usage(self, subject_id: str) -> TokenQuotaResponse:
        """
        Get usage for a subject.

        Args:
            subject_id: The ID of the subject.

        Returns:
            The usage data for the subject as a TokenQuotaResponse object.
        """
        pass

    @abstractmethod
    def upsert_subject(self, subjects: List[Dict[str, Any]]) -> None:
        """
        Create or update subjects.

        Args:
            subjects: List of subject data to create or update.
        """
        pass

    @abstractmethod
    def delete_subject(self, subject_id: str) -> None:
        """
        Delete a subject.

        Args:
            subject_id: The ID of the subject to delete.
        """
        pass

    @abstractmethod
    def list_subjects(self) -> List[Subject]:
        """
        List all subjects.

        Returns:
            A list of all subjects as Subject objects.
        """
        pass

    @abstractmethod
    def ingest_events(self, events: Dict[str, Any]) -> bool:
        """
        Ingest events into the metering system.

        Args:
            events: The events to ingest.

        Returns:
            True if the events were successfully ingested, False otherwise.
        """
        pass
