from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Subject(BaseModel):
    """
    Model representing a subject (user) in the system.
    """

    id: UUID
    email: Optional[str] = None
    display_name: Optional[str] = None

    def to_dict(self):
        """
        Convert the subject to a dictionary format suitable for external APIs.
        """
        return {'key': str(self.id), 'displayName': self.email or self.display_name or str(self.id)}
