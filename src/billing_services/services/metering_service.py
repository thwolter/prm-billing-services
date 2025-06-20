"""
MeteringService: Manages token consumption and usage recording.
"""

from typing import Optional
from uuid import UUID

from riskgpt.models.schemas import BaseResponse, ResponseInfo

from src.domain.models import UsageEvent
from src.external.metering.abstract_metering_client import AbstractMeteringClient
from src.utils import logutils

logger = logutils.get_logger(__name__)


class MeteringService:
    """
    Service for managing token consumption and usage recording.
    """

    def __init__(
        self, metering_client: AbstractMeteringClient, request: Optional[BaseResponse] = None
    ):
        """
        Initialize the MeteringService.

        Args:
            metering_client: The metering client.
            request: The BaseResponse object containing response_info and user_id in state.
        """
        self.metering_client = metering_client
        self.request = request
        if request:
            self.response_info: ResponseInfo = request.state.response_info
            self.user_id = request.state.user_id

    async def consume_tokens(self) -> bool:
        """
        Consumes tokens by creating and ingesting a CloudEvent.

        Creates an event with token consumption data including the number of tokens,
        model name, and prompt name from the response_info.

        Returns:
            bool: True if the event was successfully ingested.
        """
        usage_event = UsageEvent(
            tokens=self.response_info.consumed_tokens,
            model=self.response_info.model_name,
            prompt=self.response_info.prompt_name,
        )

        return self.metering_client.record_usage(str(self.user_id), usage_event)

    async def consume_tokens_for_user(
        self,
        user_id: UUID,
        token: int,
        model_name: Optional[str] = None,
        prompt_name: Optional[str] = None,
    ) -> bool:
        """
        Consumes token for a specific user.

        Args:
            user_id (UUID): The ID of the user for whom tokens are being consumed.
            token (int): The number of tokens consumed.
            model_name (str): The name of the model used.
            prompt_name (str): The name of the prompt used.

        Returns:
            bool: True if the event was successfully ingested.
        """
        usage_event = UsageEvent(
            tokens=token,
            model=model_name,
            prompt=prompt_name,
        )

        return self.metering_client.record_usage(str(user_id), usage_event)
