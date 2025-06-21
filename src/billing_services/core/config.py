from typing import Optional, List, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenMeterSettings(BaseSettings):
    """OpenMeter-specific settings"""
    model_config = SettingsConfigDict(env_file=['.env', '../.env'], env_ignore_empty=True, extra='ignore', env_prefix="OPENMETER_")

    # API configuration
    API_KEY: Optional[str] = None
    API_URL: str = 'https://openmeter.cloud'
    SOURCE: str = 'source'
    TIMEOUT: float = 1.0

    # Meter configuration
    METER_SLUG: str = 'ai_tokens'
    METER_DESCRIPTION: str = 'LLM tokens'
    METER_EVENT_TYPE: str = 'tokens'
    METER_AGGREGATION: str = 'SUM'
    METER_VALUE_PROPERTY: str = 'tokens'
    METER_GROUP_BY: List[str] = ['model', 'prompt']
    METER_WINDOW_SIZE: str = 'DAY'

    # Feature configuration
    FEATURE_KEY: str = 'ai_tokens'

    # Event configuration
    TOKEN_EVENT_TYPE: str = 'tokens'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=['.env', '../.env'], env_ignore_empty=True, extra='ignore'
    )

    # General settings
    LOG_LEVEL: str = 'ERROR'

    # Vendor configuration
    # These settings determine which service provider to use for each functionality
    METERING_VENDOR: str = 'openmeter'
    ENTITLEMENT_VENDOR: str = 'openmeter'
    PAYMENT_VENDOR: str = 'openmeter'

    # Vendor-specific settings
    OPENMETER: OpenMeterSettings = Field(default_factory=OpenMeterSettings)

    # In the future, add other vendor settings here:
    # OTHER_VENDOR: OtherVendorSettings = Field(default_factory=OtherVendorSettings)


settings = Settings()
