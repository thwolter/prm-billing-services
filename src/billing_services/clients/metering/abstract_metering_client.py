from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from billing_services.models.entitlement import Entitlement
from billing_services.models.subject import Subject
from billing_services.models.usage import TokenQuotaResponse, UsageEvent


class AbstractMeteringClient(ABC):
    """
    Abstract base class defining the interface for metering clients.
    This abstraction allows for easy swapping of metering providers.
    """

    @abstractmethod
    async def record_usage(self, subject_id: str, usage_event: UsageEvent) -> bool:
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
    async def get_usage(self, subject_id: str) -> TokenQuotaResponse:
        """
        Get usage for a subject.

        Args:
            subject_id: The ID of the subject.

        Returns:
            The usage data for the subject as a TokenQuotaResponse object.
        """
        pass

    @abstractmethod
    async def upsert_subject(self, subjects: List[Dict[str, Any]]) -> None:
        """
        Create or update subjects.

        Args:
            subjects: List of subject data to create or update.
        """
        pass

    @abstractmethod
    async def delete_subject(self, subject_id: str) -> None:
        """
        Delete a subject.

        Args:
            subject_id: The ID of the subject to delete.
        """
        pass

    @abstractmethod
    async def list_subjects(self) -> List[Subject]:
        """
        List all subjects.

        Returns:
            A list of all subjects as Subject objects.
        """
        pass

    @abstractmethod
    async def ingest_events(self, events: Dict[str, Any]) -> bool:
        """
        Ingest events into the metering system.

        Args:
            events: The events to ingest.

        Returns:
            True if the events were successfully ingested, False otherwise.
        """
        pass

    @abstractmethod
    async def list_entitlements(self, subject: Optional[List[str]] = None) -> List[Entitlement]:
        """
        List entitlements, optionally filtered by subject.

        Args:
            subject: Optional list of subject IDs to filter by.

        Returns:
            A list of Entitlement objects.
        """
        pass

    @abstractmethod
    async def list_features(self) -> List[str]:
        """
        List all features available in the metering system.

        Returns:
            A list of feature keys.
        """
        pass

    @abstractmethod
    async def create_feature(self, feature_key: str) -> None:
        """
        Create a new feature in the metering system.

        Args:
            feature_key: The key of the feature to create.
        """
        pass

    @abstractmethod
    async def create_meter(self) -> bool:
        """
        Create a meter in the metering system with the configured settings.

        Returns:
            True if the meter was successfully created, False otherwise.
        """
        pass
