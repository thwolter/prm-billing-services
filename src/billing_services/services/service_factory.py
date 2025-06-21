"""
TokenQuotaServiceProvider: Factory for creating token quota services.
"""

from uuid import UUID

from fastapi import Request
from openmeter import Client
from openmeter.aio import Client as AsyncClient

from src.billing_services.core.config import settings
from src.billing_services.services.entitlement_service import EntitlementService
from src.billing_services.services.metering_service import MeteringService
from src.billing_services.services.subject_service import SubjectService
from src.billing_services.clients.entitlements.openmeter_entitlement_client import OpenMeterEntitlementClient
from src.billing_services.clients.metering.openmeter_metering_client import OpenMeterMeteringClient


class.erviceFactory:
    """
    Provider for token quota services.
    """

    @staticmethod
    def create_clients(request: Request = None):
        """
        Create OpenMeter clients.

        Args:
            request: Optional FastAPI request object.

        Returns:
            A tuple of (sync_client, async_client).
        """
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {settings.OPENMETER_API_KEY}',
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

    @staticmethod
    def get_subject_service():
        """
        Get a SubjectService instance.

        Returns:
            A SubjectService instance.
        """
        sync_client, async_client =.erviceFactory.create_clients()
        metering_client = OpenMeterMeteringClient(sync_client, async_client)
        return SubjectService(metering_client)

    @staticmethod
    def get_entitlement_service():
        """
        Get an EntitlementService instance.

        Returns:
            An EntitlementService instance.
        """
        sync_client, async_client =.erviceFactory.create_clients()
        entitlement_client = OpenMeterEntitlementClient(sync_client, async_client)
        return EntitlementService(entitlement_client)

    @staticmethod
    def get_metering_service():
        """
        Get a MeteringService instance.

        Returns:
            A MeteringService instance.
        """

        sync_client, async_client =.erviceFactory.create_clients()
        metering_client = OpenMeterMeteringClient(sync_client, async_client)
        return MeteringService(metering_client)

    @classmethod
    def setup_for_testing(cls, test_user_id: UUID):
        """
        Set up the provider for testing with a test user ID.

        Args:
            test_user_id: The test user ID to use.
        """
        # Create a mock request with the test user ID
        cls._test_request = Request(
            scope={
                'type': 'http',
                'method': 'POST',
                'path': '/test',
                'headers': [(b'accept', b'application/json')],
                'state': {
                    'token': 'test_token',
                    'user_id': test_user_id,
                },
            }
        )
