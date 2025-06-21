"""
MeteringService: Manages token consumption and usage recording.
"""

from uuid import UUID

from billing_services.models import UsageEvent, ConsumedTokensInfo
from billing_services.clients.metering.abstract_metering_client import AbstractMeteringClient
from billing_services.utils import logutils

logger = logutils.get_logger(__name__)


class MeteringService:
    """
    Service for managing token consumption and usage recording.
    """

    def __init__(
        self, metering_client: AbstractMeteringClient):
        """
        Initialize the MeteringService.

        Args:
            metering_client: The metering client.
        """
        self.metering_client = metering_client


    async def consume_tokens(self, subject_id: UUID, token_info: ConsumedTokensInfo) -> bool:
        """
        Consumes tokens by creating and ingesting a CloudEvent.

        Creates an event with token consumption data including the number of tokens,
        model name, and prompt name from the response_info.

        Returns:
            bool: True if the event was successfully ingested.
        """
        usage_event = UsageEvent(
            tokens=token_info.consumed_tokens,
            model=token_info.model_name,
            prompt=token_info.prompt_name,
        )

        return self.metering_client.record_usage(str(subject_id), usage_event)
