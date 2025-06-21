"""
EntitlementService: Manages entitlements.
"""

from uuid import UUID

from azure.core.exceptions import ResourceNotFoundError

from billing_services.models import Entitlement, EntitlementCreate
from billing_services.clients.entitlements.abstract_entitlement_client import AbstractEntitlementClient
from billing_services.core.config import settings
from billing_services.utils import logutils
from billing_services.utils.exceptions import ResourceNotFoundException
from billing_services.utils.resilient import with_resilient_execution

logger = logutils.get_logger(__name__)


class EntitlementService:
    """
    Service for managing entitlements.
    """

    def __init__(
        self,
        entitlement_client: AbstractEntitlementClient,
    ):
        """
        Initialize the EntitlementService.

        Args:
            entitlement_client: The entitlement client.
        """
        self.entitlement_client = entitlement_client

    @with_resilient_execution(service_name='EntitlementService')
    async def set_entitlement(self, subject_id: UUID, limit: EntitlementCreate) -> None:
        """
        Set an entitlement for a subject.

        Args:
            subject_id: The ID of the subject.
            limit: The entitlement details.
        """

        entitlement = Entitlement(
            feature_key=limit.feature,
            has_access=True,
            limit=limit.max_limit,
            period=limit.period,
        )

        self.entitlement_client.create_entitlement(str(subject_id), entitlement)

    @with_resilient_execution(service_name='EntitlementService')
    async def get_token_entitlement_status(self, subject_id: UUID, feature_key: str) -> bool:
        """
        Check if a subject has access to a feature.

        Args:
            subject_id: The ID of the subject.
            feature_key: The feature key to check.

        Returns:
            True if the subject has access, False otherwise.

        Raises:
            ResourceNotFoundException: If the subject or feature is not found.
        """

        try:
            entitlement = self.entitlement_client.get_entitlement_value(
                str(subject_id), feature_key
            )
            return entitlement.has_access
        except ResourceNotFoundError as e:
            logger.error(f'Subject {subject_id}, feature {feature_key}: {e}')

            # Check if this is the feature from settings
            if feature_key == settings.OPENMETER.FEATURE_KEY:
                error_msg = (
                    f"Feature '{feature_key}' not found. "
                    f"Run 'python -m billing_services.commands.ensure_entitlement_features' "
                    f"to create the feature."
                )
                raise ResourceNotFoundException(detail=error_msg)
            else:
                raise ResourceNotFoundException(detail='Subject or feature not found')

    async def has_access(self, subject_id: UUID, feature_key: str) -> bool:
        """
        Alias for get_token_entitlement_status for backward compatibility.

        Args:
            subject_id: The ID of the subject.
            feature_key: The feature key to check.

        Returns:
            True if the subject has access, False otherwise.
        """
        return await self.get_token_entitlement_status(subject_id, feature_key)

    @with_resilient_execution(service_name='EntitlementService')
    async def get_entitlement_value(self, subject_id: UUID, feature_key: str) -> Entitlement:
        """
        Get the entitlement value for a subject.

        Args:
            subject_id: The ID of the subject.
            feature_key: The feature key to check.

        Returns:
            The entitlement value.

        Raises:
            ResourceNotFoundException: If the subject or feature is not found.
        """
        try:
            return self.entitlement_client.get_entitlement_value(str(subject_id), feature_key)
        except ResourceNotFoundError as e:
            logger.error(f'Subject {subject_id}, feature {feature_key}: {e}')

            # Check if this is the feature from settings
            if feature_key == settings.OPENMETER.FEATURE_KEY:
                error_msg = (
                    f"Feature '{feature_key}' not found. "
                    f"Run 'python -m billing_services.commands.ensure_entitlement_features' "
                    f"to create the feature."
                )
                raise ResourceNotFoundException(detail=error_msg)
            else:
                raise ResourceNotFoundException(detail='Subject or feature not found')
