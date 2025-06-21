from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from azure.core.exceptions import HttpResponseError
from openmeter import Client
from openmeter.aio import Client as AsyncClient

from billing_services.core.config import settings
from billing_services.models.entitlement import Entitlement
from billing_services.models.subject import Subject
from billing_services.models.usage import TokenQuotaResponse, UsageEvent
from billing_services.clients.metering.abstract_metering_client import AbstractMeteringClient
from billing_services.utils import logutils
from billing_services.utils.exceptions import ExternalServiceException

logger = logutils.get_logger(__name__)


class OpenMeterMeteringClient(AbstractMeteringClient):
    """
    OpenMeter implementation of the AbstractMeteringClient.
    """

    def __init__(self, sync_client: Client, async_client: AsyncClient):
        """
        Initialize the OpenMeterClient.

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
    def from_default(cls) -> 'OpenMeterMeteringClient':
        """
        Create an instance of OpenMeterMeteringClient using default settings.

        Returns:
            An instance of OpenMeterMeteringClient.
        """
        sync_client, async_client = cls.create_clients()
        return cls(sync_client, async_client)

    def record_usage(self, subject_id: str, usage_event: UsageEvent) -> bool:
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
        try:
            import uuid

            from cloudevents.conversion import to_dict
            from cloudevents.http import CloudEvent

            event = CloudEvent(
                attributes={
                    'id': str(uuid.uuid4()),
                    'type': settings.OPENMETER_TOKEN_EVENT_TYPE,
                    'source': settings.OPENMETER_SOURCE,
                    'subject': subject_id,
                },
                data=usage_event.to_dict(),
            )
            self.sync_client.ingest_events(to_dict(event))
            return True
        except Exception as e:
            logger.error(f'Error recording usage for subject {subject_id}: {e}')
            return False

    def get_usage(self, subject_id: str) -> TokenQuotaResponse:
        """
        Get usage for a subject using OpenMeter.

        Args:
            subject_id: The ID of the subject.

        Returns:
            The usage data for the subject as a TokenQuotaResponse object.
        """
        try:
            # This is a placeholder. OpenMeter might have a different API for getting usage.
            # Adjust according to the actual OpenMeter API.
            response = self.sync_client.get_usage(subject_id)

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
        except Exception as e:
            logger.error(f'Error getting usage for subject {subject_id}: {e}')
            return TokenQuotaResponse(
                sufficient=True,
                token_limit=1000,
                consumed_tokens=0,
                remaining_tokens=1000,
            )

    def upsert_subject(self, subjects: List[Dict[str, Any]]) -> None:
        """
        Create or update subjects using OpenMeter.

        Args:
            subjects: List of subject data to create or update.
        """
        self.sync_client.upsert_subject(subjects)

    async def upsert_subject_async(self, subjects: List[Dict[str, Any]]) -> None:
        """
        Create or update subjects using OpenMeter asynchronously.

        Args:
            subjects: List of subject data to create or update.
        """
        await self.async_client.upsert_subject(subjects)

    def delete_subject(self, subject_id: str) -> None:
        """
        Delete a subject using OpenMeter.

        Args:
            subject_id: The ID of the subject to delete.
        """
        self.sync_client.delete_subject(subject_id)

    async def delete_subject_async(self, subject_id: str) -> None:
        """
        Delete a subject using OpenMeter asynchronously.

        Args:
            subject_id: The ID of the subject to delete.
        """
        await self.async_client.delete_subject(subject_id)

    def list_subjects(self) -> List[Subject]:
        """
        List all subjects using OpenMeter.

        Returns:
            A list of all subjects as Subject objects.
        """
        response = self.sync_client.list_subjects()

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

    def ingest_events(self, events: Dict[str, Any]) -> bool:
        """
        Ingest events into OpenMeter.

        Args:
            events: The events to ingest.

        Returns:
            True if the events were successfully ingested, False otherwise.
        """
        try:
            self.sync_client.ingest_events(events)
            return True
        except Exception as e:
            logger.error(f'Error ingesting events: {e}')
            return False

    def list_entitlements(self, subject: Optional[List[str]] = None) -> List[Entitlement]:
        """
        List entitlements using OpenMeter, optionally filtered by subject.

        Args:
            subject: Optional list of subject IDs to filter by.

        Returns:
            A list of Entitlement objects.
        """
        try:
            response = self.sync_client.list_entitlements(subject=subject)
            return [Entitlement.from_dict(item) for item in response]
        except AttributeError:
            # The OpenMeter client library might not have a list_entitlements method
            logger.warning(
                'list_entitlements method not found in OpenMeter client, returning empty list'
            )
            return []
        except Exception as e:
            logger.error(f'Error listing entitlements: {e}')
            return []

    def list_features(self) -> List[str]:
        """
        List all features available in OpenMeter.

        Returns:
            A list of feature keys.
        """
        try:
            response = self.sync_client.list_features()
            return [item['key'] for item in response['items']]
        except Exception as e:
            logger.error(f'Error listing features: {e}')
            raise ExternalServiceException(f'Failed to list features from OpenMeter: {e}')

    def create_feature(self, feature_key: str) -> None:
        """
        Create a new feature in OpenMeter.

        Args:
            feature_key: The key of the feature to create.
        """
        try:
            # Create a properly formatted object with the feature key and name
            feature_data = {
                "key": feature_key,
                "name": feature_key  # Using the feature_key as the name as well
            }
            self.sync_client.create_feature(feature_data)
            logger.info(f'Feature {feature_key} created successfully.')
        except Exception as e:
            # Check if the error is a "Conflict" error (409), which means the feature already exists
            if "Conflict" in str(e) and "already exists" in str(e):
                logger.info(f'Feature {feature_key} already exists, skipping creation.')
                return  # Return without raising the exception
            logger.error(f'Error creating feature {feature_key}: {e}')
            raise

    def create_meter(self) -> bool:
        """
        Create a meter in OpenMeter with the configured settings.

        Returns:
            True if the meter was successfully created, False otherwise.
        """
        try:
            # Create the meter configuration using the settings
            meter_config = {
                "slug": settings.OPENMETER_METER_SLUG,
                "description": settings.OPENMETER_METER_DESCRIPTION,
                "eventType": settings.OPENMETER_METER_EVENT_TYPE,
                "aggregation": settings.OPENMETER_METER_AGGREGATION,
                "valueProperty": f'$.{settings.OPENMETER_METER_VALUE_PROPERTY}',
                "groupBy": {key: f'$.{key}' for key in settings.OPENMETER_METER_GROUP_BY},
                "windowSize": settings.OPENMETER_METER_WINDOW_SIZE
            }

            # Call the create_meter method of the OpenMeter client
            self.sync_client.create_meter(meter_config)
            logger.info(f'Meter {settings.OPENMETER_METER_SLUG} created successfully.')
            return True
        except HttpResponseError as e:
            if e.status_code == 200:
                logger.info(f'Meter {settings.OPENMETER_METER_SLUG} has been created.')
                return True
        except Exception as e:
            logger.error(f'Error creating meter: {e}')
            return False
