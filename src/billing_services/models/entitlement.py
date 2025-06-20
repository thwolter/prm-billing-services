from typing import Literal, Optional

from pydantic import BaseModel


class EntitlementCreate(BaseModel):
    """
    Model for creating a new entitlement.
    """

    feature: str
    max_limit: int
    period: Literal['DAY', 'WEEK', 'MONTH', 'YEAR']


class Entitlement(BaseModel):
    """
    Model representing an entitlement in the system.
    """

    feature_key: str
    has_access: bool
    balance: Optional[int] = None
    limit: Optional[int] = None
    usage: Optional[int] = None
    period: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Entitlement':
        """
        Create an Entitlement instance from a dictionary.
        """
        return cls(
            feature_key=data.get('featureKey', ''),
            has_access=data.get('hasAccess', False),
            balance=data.get('balance'),
            limit=data.get('limit'),
            usage=data.get('usage'),
            period=data.get('period'),
        )

    def to_dict(self) -> dict:
        """
        Convert the entitlement to a dictionary format suitable for external APIs.
        """
        return {
            'type': 'metered',
            'featureKey': self.feature_key,
            'issueAfterReset': self.limit,
            'usagePeriod': {'interval': self.period} if self.period else None,
        }
