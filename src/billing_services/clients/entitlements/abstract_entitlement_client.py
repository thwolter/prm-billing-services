from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.models.entitlement import Entitlement


class AbstractEntitlementClient(ABC):
    """
    Abstract base class defining the interface for entitlement clients.
    This abstraction allows for easy swapping of entitlement providers.
    """

    @abstractmethod
    def create_entitlement(self, subject_id: str, entitlement: Entitlement) -> None:
        """
        Create an entitlement for a subject.

        Args:
            subject_id: The ID of the subject.
            entitlement: The entitlement data as an Entitlement object.
        """
        pass

    @abstractmethod
    def get_entitlement_value(self, subject_id: str, feature_key: str) -> Entitlement:
        """
        Get the entitlement value for a subject and feature.

        Args:
            subject_id: The ID of the subject.
            feature_key: The feature key to check.

        Returns:
            The entitlement value as an Entitlement object.
        """
        pass

    @abstractmethod
    def list_entitlements(self, subject: Optional[List[str]] = None) -> List[Entitlement]:
        """
        List entitlements, optionally filtered by subject.

        Args:
            subject: Optional list of subject IDs to filter by.

        Returns:
            A list of Entitlement objects.
        """
        pass

    @abstractmethod
    def delete_entitlement(self, subject_id: str, feature_key: str) -> None:
        """
        Delete an entitlement for a subject and feature.

        Args:
            subject_id: The ID of the subject.
            feature_key: The feature key to delete.
        """
        pass
