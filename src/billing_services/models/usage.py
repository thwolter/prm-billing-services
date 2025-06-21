from typing import Optional

from pydantic import BaseModel


class ConsumedTokensInfo(BaseModel):
    """
    Model representing information about consumed tokens.
    """

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    total_cost: float
    prompt_name: str
    model_name: str


class TokenQuotaResponse(BaseModel):
    """
    Model representing a token quota response.
    """

    sufficient: bool
    token_limit: int
    consumed_tokens: int
    remaining_tokens: int


class UsageEvent(BaseModel):
    """
    Model representing a usage event to be recorded.
    """

    tokens: int
    model: Optional[str] = None
    prompt: Optional[str] = None

    def to_dict(self) -> dict:
        """
        Convert the usage event to a dictionary format suitable for.clients.APIs.
        """
        return {
            'tokens': self.tokens,
            'model': self.model or 'unknown_model',
            'prompt': self.prompt or 'unknown_prompt',
        }
