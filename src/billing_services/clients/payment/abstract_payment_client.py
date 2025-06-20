from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.models.payment import Payment, PaymentEvent


class AbstractPaymentClient(ABC):
    """
    Abstract base class defining the interface for payment clients.
    This abstraction allows for easy swapping of payment providers.
    """

    @abstractmethod
    def process_payment(self, payment_event: PaymentEvent) -> Payment:
        """
        Process a payment.

        Args:
            payment_event: The payment event data.

        Returns:
            The processed payment.
        """
        pass

    @abstractmethod
    def get_payment(self, payment_id: UUID) -> Optional[Payment]:
        """
        Get a payment by ID.

        Args:
            payment_id: The ID of the payment.

        Returns:
            The payment, or None if not found.
        """
        pass

    @abstractmethod
    def get_payments_for_subscription(self, subscription_id: UUID) -> List[Payment]:
        """
        Get all payments for a subscription.

        Args:
            subscription_id: The ID of the subscription.

        Returns:
            A list of payments for the subscription.
        """
        pass

    @abstractmethod
    def refund_payment(self, payment_id: UUID, amount: Optional[float] = None) -> Payment:
        """
        Refund a payment.

        Args:
            payment_id: The ID of the payment to refund.
            amount: The amount to refund. If None, refunds the full amount.

        Returns:
            The updated payment.
        """
        pass

    @abstractmethod
    def update_payment_status(self, payment_id: UUID, status: str) -> Payment:
        """
        Update the status of a payment.

        Args:
            payment_id: The ID of the payment.
            status: The new status of the payment.

        Returns:
            The updated payment.
        """
        pass
