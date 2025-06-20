"""
TokenQuotaServiceProvider: Factory for creating token quota services.
"""

from uuid import UUID

from fastapi import Request
from openmeter import Client
from openmeter.aio import Client as AsyncClient

from src.core.config import settings
from src.domain.services.entitlement_service import EntitlementService
from src.domain.services.metering_service import MeteringService
from src.domain.services.subject_service import SubjectService
from src.external.entitlements.openmeter_entitlement_client import OpenMeterEntitlementClient
from src.external.metering.openmeter_client import OpenMeterClient


class DomainServiceFactory:
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
    def get_subject_service(request: Request = None):
        """
        Get a SubjectService instance.

        Args:
            request: Optional FastAPI request object.

        Returns:
            A SubjectService instance.
        """
        sync_client, async_client = DomainServiceFactory.create_clients()
        metering_client = OpenMeterClient(sync_client, async_client)
        return SubjectService(metering_client, request)

    @staticmethod
    def get_entitlement_service(request: Request = None):
        """
        Get an EntitlementService instance.

        Args:
            request: Optional FastAPI request object.

        Returns:
            An EntitlementService instance.
        """
        sync_client, async_client = DomainServiceFactory.create_clients()
        entitlement_client = OpenMeterEntitlementClient(sync_client, async_client)
        return EntitlementService(entitlement_client, request or DomainServiceFactory._test_request)

    @staticmethod
    def get_metering_service(request: Request):
        """
        Get a MeteringService instance.

        Args:
            request: Optional FastAPI request object.

        Returns:
            A MeteringService instance.
        """

        sync_client, async_client = DomainServiceFactory.create_clients()
        metering_client = OpenMeterClient(sync_client, async_client)
        return MeteringService(metering_client, request)

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
