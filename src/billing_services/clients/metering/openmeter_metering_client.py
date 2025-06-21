from typing import Any, Dict, List, Optional
from uuid import UUID

from azure.core.exceptions import HttpResponseError
from openmeter.aio import Client as AsyncClient

from billing_services.core.config import settings
from billing_services.models.entitlement import Entitlement
from billing_services.models.subject import Subject
from billing_services.models.usage import TokenQuotaResponse, UsageEvent
from billing_services.clients.metering.abstract_metering_client import AbstractMeteringClient
from billing_services.utils import logutils
from billing_services.utils.exceptions import ExternalServiceException
from billing_services.utils.resilient import with_resilient_execution
from billing_services.utils.openmeter_error_handler import handle_openmeter_errors

logger = logutils.get_logger(__name__)


class OpenMeterMeteringClient(AbstractMeteringClient):
    """
    OpenMeter implementation of the AbstractMeteringClient.
    """

    def __init__(self, client: AsyncClient):
        """
        Initialize the OpenMeterClient.

        Args:
            client: The asynchronous OpenMeter client.
        """
        self.client = client

    @staticmethod
    def create_client() -> AsyncClient:
        """
        Create OpenMeter async client.

        Returns:
            An instance of AsyncClient.
        """
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {settings.OPENMETER.API_KEY}'
        }

        async_client = AsyncClient(
            endpoint=settings.OPENMETER.API_URL,
            headers=headers,
        )

        return async_client

    @classmethod
    def from_default(cls) -> 'OpenMeterMeteringClient':
        """
        Create an instance of OpenMeterMeteringClient using default settings.

        Returns:
            An instance of OpenMeterMeteringClient.
        """
        client = cls.create_client()
        return cls(client)

    @with_resilient_execution(service_name='OpenMeter')
    async def record_usage(self, subject_id: str, usage_event: UsageEvent) -> bool:
        """
        Record usage for a subject using OpenMeter.

        Args:
            subject_id: The ID of the subject.
            usage_event: The usage event data.

        Returns:
            True if the usage was successfully recorded, False otherwise.
        """
        # OpenMeter doesn't have a direct record_usage method, so we use ingest_events
        # with a properly formatted event
        import uuid

        from cloudevents.conversion import to_dict
        from cloudevents.http import CloudEvent

        event = CloudEvent(
            attributes={
                'id': str(uuid.uuid4()),
                'type': settings.OPENMETER.TOKEN_EVENT_TYPE,
                'source': settings.OPENMETER.SOURCE,
                'subject': subject_id,
            },
            data=usage_event.to_dict(),
        )

        async def _record_usage():
            await self.client.ingest_events(to_dict(event))
            return True

        return await handle_openmeter_errors(_record_usage)

    @with_resilient_execution(service_name='OpenMeter')
    async def get_usage(self, subject_id: str) -> TokenQuotaResponse:
        """
        Get usage for a subject using OpenMeter.

        Args:
            subject_id: The ID of the subject.

        Returns:
            The usage data for the subject as a TokenQuotaResponse object.
        """
        async def _get_usage():
            try:
                # This is a placeholder. OpenMeter might have a different API for getting usage.
                # Adjust according to the actual OpenMeter API.
                response = await self.client.get_usage(subject_id)

                # Convert the response to a TokenQuotaResponse object
                return TokenQuotaResponse(
                    sufficient=response.get('sufficient', False),
                    token_limit=response.get('token_limit', 0),
                    consumed_tokens=response.get('consumed_tokens', 0),
                    remaining_tokens=response.get('remaining_tokens', 0),
                )
            except AttributeError:
                # The OpenMeter client library might not have a get_usage method
                logger.warning(
                    'get_usage method not found in OpenMeter client, returning default TokenQuotaResponse'
                )
                return TokenQuotaResponse(
                    sufficient=True,
                    token_limit=1000,
                    consumed_tokens=0,
                    remaining_tokens=1000,
                )

        return await handle_openmeter_errors(_get_usage)

    @with_resilient_execution(service_name='OpenMeter')
    async def upsert_subject(self, subjects: List[Dict[str, Any]]) -> None:
        """
        Create or update subjects using OpenMeter.

        Args:
            subjects: List of subject data to create or update.
        """
        async def _upsert_subject():
            await self.client.upsert_subject(subjects)

        await handle_openmeter_errors(_upsert_subject)

    @with_resilient_execution(service_name='OpenMeter')
    async def delete_subject(self, subject_id: str) -> None:
        """
        Delete a subject using OpenMeter.

        Args:
            subject_id: The ID of the subject to delete.
        """
        async def _delete_subject():
            await self.client.delete_subject(subject_id)

        await handle_openmeter_errors(_delete_subject)

    @with_resilient_execution(service_name='OpenMeter')
    async def list_subjects(self) -> List[Subject]:
        """
        List all subjects using OpenMeter.

        Returns:
            A list of all subjects as Subject objects.
        """
        async def _list_subjects():
            response = await self.client.list_subjects()

            # Convert the response to a list of Subject objects
            subjects = []
            for item in response:
                try:
                    subject = Subject(
                        id=UUID(item.get('key')),
                        email=item.get('displayName'),
                        display_name=item.get('displayName'),
                    )
                    subjects.append(subject)
                except ValueError as e:
                    logger.warning(
                        f'Error converting subject key to UUID: {e}. Skipping subject with key: {item.get("key")}'
                    )
                    continue

            return subjects

        return await handle_openmeter_errors(_list_subjects)

    @with_resilient_execution(service_name='OpenMeter')
    async def ingest_events(self, events: Dict[str, Any]) -> bool:
        """
        Ingest events into OpenMeter.

        Args:
            events: The events to ingest.

        Returns:
            True if the events were successfully ingested, False otherwise.
        """
        async def _ingest_events():
            await self.client.ingest_events(events)
            return True

        return await handle_openmeter_errors(_ingest_events)

    @with_resilient_execution(service_name='OpenMeter')
    async def list_entitlements(self, subject: Optional[List[str]] = None) -> List[Entitlement]:
        """
        List entitlements using OpenMeter, optionally filtered by subject.

        Args:
            subject: Optional list of subject IDs to filter by.

        Returns:
            A list of Entitlement objects.
        """
        async def _list_entitlements():
            try:
                response = await self.client.list_entitlements(subject=subject)
                return [Entitlement.from_dict(item) for item in response]
            except AttributeError:
                # The OpenMeter client library might not have a list_entitlements method
                logger.warning(
                    'list_entitlements method not found in OpenMeter client, returning empty list'
                )
                return []

        return await handle_openmeter_errors(_list_entitlements)

    @with_resilient_execution(service_name='OpenMeter')
    async def list_features(self) -> List[str]:
        """
        List all features available in OpenMeter.

        Returns:
            A list of feature keys.
        """
        async def _list_features():
            response = await self.client.list_features()
            return [item['key'] for item in response['items']]

        return await handle_openmeter_errors(_list_features)

    @with_resilient_execution(service_name='OpenMeter')
    async def create_feature(self, feature_key: str) -> None:
        """
        Create a new feature in OpenMeter.

        Args:
            feature_key: The key of the feature to create.
        """
        async def _create_feature():
            try:
                # Create a properly formatted object with the feature key and name
                feature_data = {
                    "key": feature_key,
                    "name": feature_key  # Using the feature_key as the name as well
                }
                await self.client.create_feature(feature_data)
                logger.info(f'Feature {feature_key} created successfully.')
            except Exception as e:
                # Check if the error is a "Conflict" error (409), which means the feature already exists
                if "Conflict" in str(e) and "already exists" in str(e):
                    logger.info(f'Feature {feature_key} already exists, skipping creation.')
                    return  # Return without raising the exception
                raise

        await handle_openmeter_errors(_create_feature)

    @with_resilient_execution(service_name='OpenMeter')
    async def create_meter(self) -> bool:
        """
        Create a meter in OpenMeter with the configured settings.

        Returns:
            True if the meter was successfully created, False otherwise.
        """
        async def _create_meter():
            try:
                # Create the meter configuration using the settings
                meter_config = {
                    "slug": settings.OPENMETER.METER_SLUG,
                    "description": settings.OPENMETER.METER_DESCRIPTION,
                    "eventType": settings.OPENMETER.METER_EVENT_TYPE,
                    "aggregation": settings.OPENMETER.METER_AGGREGATION,
                    "valueProperty": f'$.{settings.OPENMETER.METER_VALUE_PROPERTY}',
                    "groupBy": {key: f'$.{key}' for key in settings.OPENMETER.METER_GROUP_BY},
                    "windowSize": settings.OPENMETER.METER_WINDOW_SIZE
                }

                # Call the create_meter method of the OpenMeter client
                await self.client.create_meter(meter_config)
                logger.info(f'Meter {settings.OPENMETER.METER_SLUG} created successfully.')
                return True
            except HttpResponseError as e:
                if e.status_code == 200:
                    logger.info(f'Meter {settings.OPENMETER.METER_SLUG} has been created.')
                    return True
                raise

        return await handle_openmeter_errors(_create_meter)
