import json
from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=['.env', '../.env'], env_ignore_empty=True, extra='ignore'
    )


    # Vendor configuration
    METERING_VENDOR: str = 'openmeter'
    ENTITLEMENT_VENDOR: str = 'openmeter'
    PAYMENT_VENDOR: str = 'openmeter'

    # OpenMeter configuration
    OPENMETER_API_KEY: str
    OPENMETER_API_URL: str = 'https://openmeter.cloud'
    OPENMETER_SOURCE: str = 'prm-ai-service'
    OPENMETER_TIMEOUT: float = 1.0
    OPENMETER_FEATURE_KEY: str = 'ai_tokens'
    OPENMETER_EVENT_TYPE: str = 'tokens'

    @classmethod
    def from_env(cls):
        return cls()


settings = Settings()
