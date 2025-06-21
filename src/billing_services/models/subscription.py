from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Subscription(BaseModel):
    """
    Model representing a subscription in the system.
    """

    id: UUID
    subject_id: UUID
    plan_id: str
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_renew: bool = False
    metadata: Optional[dict] = None

    def to_dict(self) -> dict:
        """
        Convert the subscription to a dictionary format suitable for.clients.APIs.
        """
        return {
            'id': str(self.id),
            'subjectId': str(self.subject_id),
            'planId': self.plan_id,
            'status': self.status,
            'startDate': self.start_date.isoformat(),
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'autoRenew': self.auto_renew,
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Subscription':
        """
        Create a Subscription instance from a dictionary.
        """
        return cls(
            id=UUID(data['id']),
            subject_id=UUID(data['subjectId']),
            plan_id=data['planId'],
            status=data['status'],
            start_date=datetime.fromisoformat(data['startDate']),
            end_date=datetime.fromisoformat(data['endDate']) if data.get('endDate') else None,
            auto_renew=data.get('autoRenew', False),
            metadata=data.get('metadata'),
        )
