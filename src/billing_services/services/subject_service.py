"""
SubjectService: Manages subject operations.
"""

from typing import List, Optional
from uuid import UUID

from azure.core.exceptions import ResourceNotFoundError

from billing_services.models import Subject
from billing_services.clients.metering.abstract_metering_client import AbstractMeteringClient
from billing_services.utils import logutils
from billing_services.utils.exceptions import ResourceNotFoundException
from billing_services.utils.resilient import with_resilient_execution

logger = logutils.get_logger(__name__)


class SubjectService:
    """
    Service for managing subjects.
    """

    def __init__(self, metering_client: AbstractMeteringClient):
        """
        Initialize the SubjectService.

        Args:
            metering_client: The metering client.
        """
        self.metering_client = metering_client


    @with_resilient_execution(service_name='SubjectService')
    async def create_subject(
        self, subject_id: UUID, user_email: Optional[str] = None
    ) -> None:
        """
        Create or update a subject.

        Args:
            subject_id: The ID of the subject.
            user_email: Optional user email.
        """

        subject = Subject(id=subject_id, email=user_email)
        await self.metering_client.upsert_subject_async([subject.to_dict()])

    @with_resilient_execution(service_name='SubjectService')
    async def delete_subject(self, subject_id: UUID) -> None:
        """
        Delete a subject.

        Args:
            subject_id: The ID of the subject to delete.

        Raises:
            ResourceNotFoundException: If the subject is not found.
        """
        if not subject_id:
            logger.error('Cannot delete subject: No subject ID provided')
            return

        try:
            await self.metering_client.delete_subject_async(str(subject_id))
        except ResourceNotFoundError as e:
            logger.error(f'Subject {subject_id} not found for deletion: {e}')
            raise ResourceNotFoundException(detail='Subject not found')

    @with_resilient_execution(service_name='SubjectService')
    async def list_subjects(self) -> List[Subject]:
        """
        List all subjects.

        Returns:
            A list of all subjects.
        """
        subjects = self.metering_client.list_subjects()
        logger.debug(f'Found {len(subjects)} subjects')
        return subjects

    @with_resilient_execution(service_name='SubjectService')
    async def list_subjects_without_entitlement(self) -> List[UUID]:
        """
        List all subjects without an entitlement.

        Returns:
            A list of UUIDs of subjects without entitlements.
        """

        # Get all subjects
        subjects = await self.list_subjects()

        # Filter subjects without entitlements
        subjects_without_entitlement = []
        for subject in subjects:
            try:
                # Check if subject has any entitlements
                entitlements = self.metering_client.list_entitlements(subject=[str(subject['key'])])
                if not entitlements:
                    subjects_without_entitlement.append(UUID(subject['key']))
            except ResourceNotFoundError:
                # If no entitlements found, add to the list
                subjects_without_entitlement.append(UUID(subject['key']))
        logger.debug(f'Found {len(subjects_without_entitlement)} subjects without entitlements')

        return subjects_without_entitlement
