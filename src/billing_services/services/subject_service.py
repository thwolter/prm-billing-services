"""
SubjectService: Manages subject operations.
"""

from typing import List, Optional
from uuid import UUID

from azure.core.exceptions import ResourceNotFoundError
from fastapi import Request

from src.domain.models import Subject
from src.external.metering.abstract_metering_client import AbstractMeteringClient
from src.utils import logutils
from src.utils.exceptions import ResourceNotFoundException
from src.utils.resilient import with_resilient_execution

logger = logutils.get_logger(__name__)


class SubjectService:
    """
    Service for managing subjects.
    """

    def __init__(self, metering_client: AbstractMeteringClient, request: Optional[Request] = None):
        """
        Initialize the SubjectService.

        Args:
            metering_client: The metering client.
            request: Optional FastAPI request object.
        """
        self.metering_client = metering_client
        self.request = request

        if request:
            self.user_id = request.state.user_id
            self.user_email = getattr(request.state, 'user_email', None)
        else:
            self.user_id = None
            self.user_email = None

    @with_resilient_execution(service_name='MeteringService')
    async def create_subject(
        self, user_id: Optional[UUID] = None, user_email: Optional[str] = None
    ) -> None:
        """
        Create or update a subject.

        Args:
            user_id: Optional user ID. If not provided, uses the ID from the request.
            user_email: Optional user email. If not provided, use the email from the request.
        """

        user_id = user_id or self.user_id
        user_email = user_email or self.user_email

        if not user_id:
            logger.error('Cannot create subject: No user ID provided')
            return

        subject = Subject(id=user_id, email=user_email)
        self.metering_client.upsert_subject([subject.to_dict()])

    def create_subject_sync(
        self, user_id: Optional[UUID] = None, user_email: Optional[str] = None
    ) -> None:
        """
        Synchronous version of create_subject.

        Args:
            user_id: Optional user ID. If not provided, uses the ID from the request.
            user_email: Optional user email. If not provided, use the email from the request.
        """
        import asyncio

        # Run the async method in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists in current thread, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.create_subject(user_id, user_email))

    @with_resilient_execution(service_name='MeteringService')
    async def delete_subject(self, user_id: Optional[UUID] = None) -> None:
        """
        Delete a subject.

        Args:
            user_id: Optional user ID. If not provided, uses the ID from the request.

        Raises:
            ResourceNotFoundException: If the user is not found.
        """

        user_id = user_id or self.user_id

        if not user_id:
            logger.error('Cannot delete subject: No user ID provided')
            return

        try:
            self.metering_client.delete_subject(str(user_id))
        except ResourceNotFoundError as e:
            logger.error(f'User {user_id} not found for deletion: {e}')
            raise ResourceNotFoundException(detail='User not found')

    def delete_subject_sync(self, user_id: Optional[UUID] = None) -> None:
        """
        Synchronous version of delete_subject.

        Args:
            user_id: Optional user ID. If not provided, uses the ID from the request.

        Raises:
            ResourceNotFoundException: If the user is not found.
        """
        import asyncio

        # Run the async method in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists in current thread, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.delete_subject(user_id))

    @with_resilient_execution(service_name='MeteringService')
    async def list_subjects(self) -> List[Subject]:
        """
        List all subjects.

        Returns:
            A list of all subjects.
        """
        subjects = self.metering_client.list_subjects()
        logger.debug(f'Found {len(subjects)} subjects')
        return subjects

    def list_subjects_sync(self) -> List[Subject]:
        """
        Synchronous version of list_subjects.

        Returns:
            A list of all subjects.
        """
        import asyncio

        # Run the async method in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists in current thread, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.list_subjects())

    @with_resilient_execution(service_name='MeteringService')
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

    def list_subjects_without_entitlement_sync(self) -> List[UUID]:
        """
        Synchronous version of list_subjects_without_entitlement.

        Returns:
            A list of UUIDs of subjects without entitlements.
        """
        import asyncio

        # Run the async method in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists in the current thread, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.list_subjects_without_entitlement())
