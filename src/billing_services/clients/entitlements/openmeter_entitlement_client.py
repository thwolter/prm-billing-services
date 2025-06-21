from typing import List, Optional, Tuple

from openmeter import Client
from openmeter.aio import Client as AsyncClient

from billing_services.core.config import settings
from billing_services.models.entitlement import Entitlement
from billing_services.clients.entitlements.abstract_entitlement_client import AbstractEntitlementClient
from billing_services.utils import logutils

logger = logutils.get_logger(__name__)


class OpenMeterEntitlementClient(AbstractEntitlementClient):
    """
    OpenMeter implementation of the AbstractEntitlementClient.
    """

    def __init__(self, sync_client: Client, async_client: AsyncClient):
        """
        Initialize the OpenMeterEntitlementClient.

        Args:
            sync_client: The synchronous OpenMeter client.
            async_client: The asynchronous OpenMeter client.
        """
        self.sync_client = sync_client
        self.async_client = async_client

    @staticmethod
    def create_clients() -> Tuple[Client, AsyncClient]:
        """
        Create OpenMeter clients.

        Returns:
            A tuple of (sync_client, async_client).
        """
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {settings.OPENMETER_API_KEY}'
        }

        sync_client = Client(
            endpoint=settings.OPENMETER_API_URL,
            headers=headers,
        )

        async_client = AsyncClient(
            endpoint=settings.OPENMETER_API_URL,
            headers=headers,
        )

        return sync_client, async_client

    @classmethod
    def from_default(cls) -> 'OpenMeterEntitlementClient':
        """
        Create an OpenMeterEntitlementClient using default settings.

        Returns:
            An instance of OpenMeterEntitlementClient.
        """
        sync_client, async_client = cls.create_clients()
        return cls(sync_client, async_client)

    def create_entitlement(self, subject_id: str, entitlement: Entitlement) -> None:
        """
        Create an entitlement for a subject using OpenMeter.

        Args:
            subject_id: The ID of the subject.
            entitlement: The entitlement data as an Entitlement object.
        """
        self.sync_client.create_entitlement(subject_id, entitlement.to_dict())

    def get_entitlement_value(self, subject_id: str, feature_key: str) -> Entitlement:
        """
        Get the entitlement value for a subject and feature using OpenMeter.

        Args:
            subject_id: The ID of the subject.
            feature_key: The feature key to check.

        Returns:
            The entitlement value as an Entitlement object.
        """
        response = self.sync_client.get_entitlement_value(subject_id, feature_key)
        return Entitlement.from_dict(response)

    def list_entitlements(self, subject: Optional[List[str]] = None) -> List[Entitlement]:
        """
        List entitlements using OpenMeter, optionally filtered by subject.

        Args:
            subject: Optional list of subject IDs to filter by.

        Returns:
            A list of Entitlement objects.
        """
        response = self.sync_client.list_entitlements(subject=subject)
        return [Entitlement.from_dict(item) for item in response]

    def delete_entitlement(self, subject_id: str, feature_key: str) -> None:
        """
        Delete an entitlement for a subject and feature using OpenMeter.

        Args:
            subject_id: The ID of the subject.
            feature_key: The feature key to delete.
        """
        self.sync_client.delete_entitlement(subject_id, feature_key)
