"""
SubscriptionService: Manages subscriptions.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.domain.models import Subscription
from src.domain.services.payment_service import PaymentService
from src.utils import logutils

logger = logutils.get_logger(__name__)


class SubscriptionService:
    """
    Service for managing subscriptions.
    """

    def __init__(self, payment_service: Optional[PaymentService] = None):
        """
        Initialize the SubscriptionService.

        Args:
            payment_service: Optional payment service for processing subscription payments.
        """
        # This is a placeholder. In a real implementation, this would likely
        # use a database or external service to store and retrieve subscriptions.
        self.subscriptions = {}
        self.payment_service = payment_service

    async def create_subscription(
        self,
        subject_id: UUID,
        plan_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        auto_renew: bool = False,
        metadata: Optional[dict] = None,
        amount: Optional[float] = None,
        currency: str = 'USD',
        payment_method: str = 'credit_card',
    ) -> Subscription:
        """
        Create a new subscription.

        Args:
            subject_id: The ID of the subject (user).
            plan_id: The ID of the plan.
            start_date: The start date of the subscription. Defaults to now.
            end_date: The end date of the subscription.
            auto_renew: Whether the subscription should auto-renew.
            metadata: Additional metadata for the subscription.
            amount: The payment amount for the subscription. If None, no payment is processed.
            currency: The currency for the payment.
            payment_method: The payment method to use.

        Returns:
            The created subscription.
        """
        from uuid import uuid4

        subscription_id = uuid4()
        subscription = Subscription(
            id=subscription_id,
            subject_id=subject_id,
            plan_id=plan_id,
            status='active',
            start_date=start_date or datetime.now(),
            end_date=end_date,
            auto_renew=auto_renew,
            metadata=metadata or {},
        )

        # In a real implementation, this would save to a database
        self.subscriptions[str(subscription_id)] = subscription

        # Process payment if amount is provided and payment service is available
        if amount is not None and self.payment_service:
            try:
                payment_metadata = {
                    'subscription_id': str(subscription_id),
                    'plan_id': plan_id,
                    'subject_id': str(subject_id),
                    'type': 'subscription_creation',
                }

                # Merge with any existing metadata
                if metadata:
                    payment_metadata.update(metadata)

                await self.payment_service.process_payment(
                    subscription_id=subscription_id,
                    amount=amount,
                    currency=currency,
                    payment_method=payment_method,
                    metadata=payment_metadata,
                )

                logger.info(f'Payment processed for subscription {subscription_id}')
            except Exception as e:
                logger.error(f'Failed to process payment for subscription {subscription_id}: {e}')
                # In a real implementation, you might want to handle payment failures differently
                # For example, you might want to mark the subscription as pending or failed
                subscription.status = 'payment_failed'
                self.subscriptions[str(subscription_id)] = subscription

        return subscription

    async def get_subscription(self, subscription_id: UUID) -> Optional[Subscription]:
        """
        Get a subscription by ID.

        Args:
            subscription_id: The ID of the subscription.

        Returns:
            The subscription, or None if not found.
        """
        return self.subscriptions.get(str(subscription_id))

    async def get_subscriptions_for_subject(self, subject_id: UUID) -> List[Subscription]:
        """
        Get all subscriptions for a subject.

        Args:
            subject_id: The ID of the subject.

        Returns:
            A list of subscriptions for the subject.
        """
        return [
            subscription
            for subscription in self.subscriptions.values()
            if subscription.subject_id == subject_id
        ]

    async def update_subscription(
        self,
        subscription_id: UUID,
        status: Optional[str] = None,
        end_date: Optional[datetime] = None,
        auto_renew: Optional[bool] = None,
        metadata: Optional[dict] = None,
    ) -> Optional[Subscription]:
        """
        Update a subscription.

        Args:
            subscription_id: The ID of the subscription.
            status: The new status of the subscription.
            end_date: The new end date of the subscription.
            auto_renew: Whether the subscription should auto-renew.
            metadata: Additional metadata for the subscription.

        Returns:
            The updated subscription, or None if not found.
        """
        subscription = self.subscriptions.get(str(subscription_id))
        if not subscription:
            return None

        if status is not None:
            subscription.status = status
        if end_date is not None:
            subscription.end_date = end_date
        if auto_renew is not None:
            subscription.auto_renew = auto_renew
        if metadata is not None:
            subscription.metadata = metadata

        # In a real implementation, this would update in a database
        self.subscriptions[str(subscription_id)] = subscription
        return subscription

    async def cancel_subscription(
        self, subscription_id: UUID, refund: bool = False, refund_amount: Optional[float] = None
    ) -> Optional[Subscription]:
        """
        Cancel a subscription.

        Args:
            subscription_id: The ID of the subscription.
            refund: Whether to issue a refund for the subscription.
            refund_amount: The amount to refund. If None and refund is True, refunds the full amount.

        Returns:
            The cancelled subscription, or None if not found.
        """
        subscription = await self.update_subscription(subscription_id, status='cancelled')

        # Process refund if requested and payment service is available
        if refund and self.payment_service and subscription:
            try:
                # Get the most recent payment for this subscription
                payments = await self.payment_service.get_payments_for_subscription(subscription_id)
                if payments:
                    # Sort payments by date, most recent first
                    sorted_payments = sorted(payments, key=lambda p: p.payment_date, reverse=True)
                    latest_payment = sorted_payments[0]

                    # Process the refund
                    await self.payment_service.refund_payment(
                        payment_id=latest_payment.id, amount=refund_amount
                    )

                    logger.info(f'Refund processed for subscription {subscription_id}')
                else:
                    logger.warning(
                        f'No payments found for subscription {subscription_id} to refund'
                    )
            except Exception as e:
                logger.error(f'Failed to process refund for subscription {subscription_id}: {e}')
                # In a real implementation, you might want to handle refund failures differently

        return subscription
