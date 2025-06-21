"""
ServiceFactory: Factory for creating service instances based on configured vendors.
"""

from uuid import UUID

from fastapi import Request
from openmeter import Client
from openmeter.aio import Client as AsyncClient

from billing_services.core.config import settings
from billing_services.services.entitlement_service import EntitlementService
from billing_services.services.metering_service import MeteringService
from billing_services.services.subject_service import SubjectService
from billing_services.clients.entitlements.openmeter_entitlement_client import OpenMeterEntitlementClient
from billing_services.clients.metering.openmeter_metering_client import OpenMeterMeteringClient


class ServiceFactory:
    """
    Provider for service instances based on configured vendors.
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
            'Authorization': f'Bearer {settings.OPENMETER.API_KEY}',
        }

        sync_client = Client(
            endpoint=settings.OPENMETER.API_URL,
            headers=headers,
        )

        async_client = AsyncClient(
            endpoint=settings.OPENMETER.API_URL,
            headers=headers,
        )

        return sync_client, async_client

    @staticmethod
    def get_metering_client():
        """
        Get a metering client based on the configured vendor.

        Returns:
            An implementation of AbstractMeteringClient.
        """
        if settings.METERING_VENDOR.lower() == 'openmeter':
            sync_client, async_client = ServiceFactory.create_clients()
            return OpenMeterMeteringClient(sync_client, async_client)
        # Add support for other vendors here
        # elif settings.METERING_VENDOR.lower() == 'other_vendor':
        #     return OtherVendorMeteringClient()
        else:
            raise ValueError(f"Unsupported metering vendor: {settings.METERING_VENDOR}")

    @staticmethod
    def get_entitlement_client():
        """
        Get an entitlement client based on the configured vendor.

        Returns:
            An implementation of AbstractEntitlementClient.
        """
        if settings.ENTITLEMENT_VENDOR.lower() == 'openmeter':
            sync_client, async_client = ServiceFactory.create_clients()
            return OpenMeterEntitlementClient(sync_client, async_client)
        # Add support for other vendors here
        # elif settings.ENTITLEMENT_VENDOR.lower() == 'other_vendor':
        #     return OtherVendorEntitlementClient()
        else:
            raise ValueError(f"Unsupported entitlement vendor: {settings.ENTITLEMENT_VENDOR}")

    @staticmethod
    def get_subject_service():
        """
        Get a SubjectService instance.

        Returns:
            A SubjectService instance.
        """
        metering_client = ServiceFactory.get_metering_client()
        return SubjectService(metering_client)

    @staticmethod
    def get_entitlement_service():
        """
        Get an EntitlementService instance.

        Returns:
            An EntitlementService instance.
        """
        entitlement_client = ServiceFactory.get_entitlement_client()
        return EntitlementService(entitlement_client)

    @staticmethod
    def get_metering_service():
        """
        Get a MeteringService instance.

        Returns:
            A MeteringService instance.
        """
        metering_client = ServiceFactory.get_metering_client()
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
