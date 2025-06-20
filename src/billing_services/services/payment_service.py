"""
PaymentService: Manages payments for subscriptions.
"""

from typing import List, Optional
from uuid import UUID

from src.domain.models.payment import Payment, PaymentEvent
from src.external.payment.abstract_payment_client import AbstractPaymentClient
from src.utils import logutils

logger = logutils.get_logger(__name__)


class PaymentService:
    """
    Service for managing payments for subscriptions.
    """

    def __init__(self, payment_client: AbstractPaymentClient):
        """
        Initialize the PaymentService.

        Args:
            payment_client: The payment client.
        """
        self.payment_client = payment_client

    async def process_payment(
        self,
        subscription_id: UUID,
        amount: float,
        currency: str,
        payment_method: str,
        metadata: Optional[dict] = None,
    ) -> Payment:
        """
        Process a payment for a subscription.

        Args:
            subscription_id: The ID of the subscription.
            amount: The payment amount.
            currency: The payment currency.
            payment_method: The payment method.
            metadata: Additional metadata for the payment.

        Returns:
            The processed payment.
        """
        try:
            payment_event = PaymentEvent(
                subscription_id=subscription_id,
                amount=amount,
                currency=currency,
                payment_method=payment_method,
                metadata=metadata,
            )
            return self.payment_client.process_payment(payment_event)
        except Exception as e:
            logger.error(f'Error processing payment for subscription {subscription_id}: {e}')
            raise

    async def get_payment(self, payment_id: UUID) -> Optional[Payment]:
        """
        Get a payment by ID.

        Args:
            payment_id: The ID of the payment.

        Returns:
            The payment, or None if not found.
        """
        try:
            return self.payment_client.get_payment(payment_id)
        except Exception as e:
            logger.error(f'Error getting payment {payment_id}: {e}')
            raise

    async def get_payments_for_subscription(self, subscription_id: UUID) -> List[Payment]:
        """
        Get all payments for a subscription.

        Args:
            subscription_id: The ID of the subscription.

        Returns:
            A list of payments for the subscription.
        """
        try:
            return self.payment_client.get_payments_for_subscription(subscription_id)
        except Exception as e:
            logger.error(f'Error getting payments for subscription {subscription_id}: {e}')
            raise

    async def refund_payment(self, payment_id: UUID, amount: Optional[float] = None) -> Payment:
        """
        Refund a payment.

        Args:
            payment_id: The ID of the payment to refund.
            amount: The amount to refund. If None, refunds the full amount.

        Returns:
            The updated payment.
        """
        try:
            return self.payment_client.refund_payment(payment_id, amount)
        except Exception as e:
            logger.error(f'Error refunding payment {payment_id}: {e}')
            raise

    async def update_payment_status(self, payment_id: UUID, status: str) -> Payment:
        """
        Update the status of a payment.

        Args:
            payment_id: The ID of the payment.
            status: The new status of the payment.

        Returns:
            The updated payment.
        """
        try:
            return self.payment_client.update_payment_status(payment_id, status)
        except Exception as e:
            logger.error(f'Error updating payment status for {payment_id}: {e}')
            raise
