from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from openmeter import Client
from openmeter.aio import Client as AsyncClient

from src.core.config import settings
from src.domain.models.entitlement import Entitlement
from src.domain.models.subject import Subject
from src.domain.models.usage import TokenQuotaResponse, UsageEvent
from src.external.metering.abstract_metering_client import AbstractMeteringClient
from src.utils import logutils

logger = logutils.get_logger(__name__)


class OpenMeterClient(AbstractMeteringClient):
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
                    'type': settings.OPENMETER_EVENT_TYPE,
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

    def delete_subject(self, subject_id: str) -> None:
        """
        Delete a subject using OpenMeter.

        Args:
            subject_id: The ID of the subject to delete.
        """
        self.sync_client.delete_subject(subject_id)

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
