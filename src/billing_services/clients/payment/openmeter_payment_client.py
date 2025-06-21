from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from cloudevents.conversion import to_dict
from cloudevents.http import CloudEvent
from openmeter import Client
from openmeter.aio import Client as AsyncClient

from billing_services.core.config import settings
from billing_services.models.payment import Payment, PaymentEvent
from billing_services.clients.payment.abstract_payment_client import AbstractPaymentClient
from billing_services.utils import logutils

logger = logutils.get_logger(__name__)


class OpenMeterPaymentClient(AbstractPaymentClient):
    """
    OpenMeter implementation of the AbstractPaymentClient.
    """

    def __init__(self, sync_client: Client, async_client: AsyncClient):
        """
        Initialize the OpenMeterPaymentClient.

        Args:
            sync_client: The synchronous OpenMeter client.
            async_client: The asynchronous OpenMeter client.
        """
        self.sync_client = sync_client
        self.async_client = async_client
        # In-memory storage for payments (in a real implementation, this would be a database)
        self.payments = {}

    @staticmethod
    def create_clients() -> Tuple[Client, AsyncClient]:
        """
        Create OpenMeter clients.

        Returns:
            A tuple of (sync_client, async_client).
        """
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {settings.OPENMETER.API_KEY}',
        }

        sync_client = Client(
            endpoint=settings.OPENMETER.API_URL,
            headers=headers,
        )

        async_client = AsyncClient(
            endpoint=settings.OPENMETER.API_URL,
            headers=headers,
        )

        return sync_client, async_client

    def process_payment(self, payment_event: PaymentEvent) -> Payment:
        """
        Process a payment using OpenMeter.

        Args:
            payment_event: The payment event data.

        Returns:
            The processed payment.
        """
        try:
            # Create a unique ID for the payment
            payment_id = uuid4()

            # Create a CloudEvent for the payment
            event = CloudEvent(
                attributes={
                    'id': str(payment_id),
                    'type': 'payment.processed',
                    'source': settings.OPENMETER.SOURCE,
                    'subject': str(payment_event.subscription_id),
                },
                data=payment_event.to_dict(),
            )

            # Ingest the event into OpenMeter
            self.sync_client.ingest_events(to_dict(event))

            # Create a Payment object
            payment = Payment(
                id=payment_id,
                subscription_id=payment_event.subscription_id,
                amount=payment_event.amount,
                currency=payment_event.currency,
                status='processed',
                payment_date=datetime.now(),
                payment_method=payment_event.payment_method,
                metadata=payment_event.metadata,
            )

            # Store the payment (in a real implementation, this would be in a database)
            self.payments[str(payment_id)] = payment

            return payment
        except Exception as e:
            logger.error(f'Error processing payment: {e}')
            raise

    def get_payment(self, payment_id: UUID) -> Optional[Payment]:
        """
        Get a payment by ID.

        Args:
            payment_id: The ID of the payment.

        Returns:
            The payment, or None if not found.
        """
        return self.payments.get(str(payment_id))

    def get_payments_for_subscription(self, subscription_id: UUID) -> List[Payment]:
        """
        Get all payments for a subscription.

        Args:
            subscription_id: The ID of the subscription.

        Returns:
            A list of payments for the subscription.
        """
        return [
            payment
            for payment in self.payments.values()
            if payment.subscription_id == subscription_id
        ]

    def refund_payment(self, payment_id: UUID, amount: Optional[float] = None) -> Payment:
        """
        Refund a payment.

        Args:
            payment_id: The ID of the payment to refund.
            amount: The amount to refund. If None, refunds the full amount.

        Returns:
            The updated payment.
        """
        payment = self.get_payment(payment_id)
        if not payment:
            raise ValueError(f'Payment with ID {payment_id} not found')

        # Create a CloudEvent for the refund
        refund_amount = amount if amount is not None else payment.amount
        event = CloudEvent(
            attributes={
                'id': str(uuid4()),
                'type': 'payment.refunded',
                'source': settings.OPENMETER.SOURCE,
                'subject': str(payment.subscription_id),
            },
            data={
                'paymentId': str(payment_id),
                'amount': refund_amount,
                'currency': payment.currency,
            },
        )

        # Ingest the event into OpenMeter
        self.sync_client.ingest_events(to_dict(event))

        # Update the payment status
        payment.status = 'refunded'
        if amount is not None and amount < payment.amount:
            payment.status = 'partially_refunded'
            payment.metadata = payment.metadata or {}
            payment.metadata['refunded_amount'] = amount

        # Store the updated payment
        self.payments[str(payment_id)] = payment

        return payment

    def update_payment_status(self, payment_id: UUID, status: str) -> Payment:
        """
        Update the status of a payment.

        Args:
            payment_id: The ID of the payment.
            status: The new status of the payment.

        Returns:
            The updated payment.
        """
        payment = self.get_payment(payment_id)
        if not payment:
            raise ValueError(f'Payment with ID {payment_id} not found')

        # Create a CloudEvent for the status update
        event = CloudEvent(
            attributes={
                'id': str(uuid4()),
                'type': 'payment.status_updated',
                'source': settings.OPENMETER.SOURCE,
                'subject': str(payment.subscription_id),
            },
            data={
                'paymentId': str(payment_id),
                'oldStatus': payment.status,
                'newStatus': status,
            },
        )

        # Ingest the event into OpenMeter
        self.sync_client.ingest_events(to_dict(event))

        # Update the payment status
        payment.status = status

        # Store the updated payment
        self.payments[str(payment_id)] = payment

        return payment
