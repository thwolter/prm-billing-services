from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Payment(BaseModel):
    """
    Model representing a payment in the system.
    """

    id: UUID
    subscription_id: UUID
    amount: float
    currency: str
    status: str
    payment_date: datetime
    payment_method: str
    metadata: Optional[dict] = None

    def to_dict(self) -> dict:
        """
        Convert the payment to a dictionary format suitable for.clients.APIs.
        """
        return {
            'id': str(self.id),
            'subscriptionId': str(self.subscription_id),
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'paymentDate': self.payment_date.isoformat(),
            'paymentMethod': self.payment_method,
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Payment':
        """
        Create a Payment instance from a dictionary.
        """
        return cls(
            id=UUID(data['id']),
            subscription_id=UUID(data['subscriptionId']),
            amount=data['amount'],
            currency=data['currency'],
            status=data['status'],
            payment_date=datetime.fromisoformat(data['paymentDate']),
            payment_method=data['paymentMethod'],
            metadata=data.get('metadata'),
        )


class PaymentEvent(BaseModel):
    """
    Model representing a payment event to be recorded.
    """

    subscription_id: UUID
    amount: float
    currency: str
    payment_method: str
    metadata: Optional[dict] = None

    def to_dict(self) -> dict:
        """
        Convert the payment event to a dictionary format suitable for.clients.APIs.
        """
        return {
            'subscriptionId': str(self.subscription_id),
            'amount': self.amount,
            'currency': self.currency,
            'paymentMethod': self.payment_method,
            'metadata': self.metadata,
        }
