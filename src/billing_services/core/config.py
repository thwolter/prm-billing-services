from typing import Optional, List

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # OpenMeter API configuration
    # These settings are used for connecting to the OpenMeter API
    OPENMETER_API_KEY: Optional[str] = None
    OPENMETER_API_URL: str = 'https://openmeter.cloud'
    OPENMETER_SOURCE: str = 'source'
    OPENMETER_TIMEOUT: float = 1.0

    # OpenMeter feature configuration
    # These settings define the feature used for entitlements
    OPENMETER_FEATURE_KEY: str = 'ai_tokens'  # The key used to identify the feature in OpenMeter

    # OpenMeter event configuration
    # These settings define how events are recorded in OpenMeter
    OPENMETER_TOKEN_EVENT_TYPE: str = 'tokens'  # The event type for token usage events

    # OpenMeter meter configuration
    # These settings define how the meter is configured in OpenMeter

    OPENMETER_METER_SLUG: str = 'ai_tokens'
    OPENMETER_METER_DESCRIPTION: str = 'LLM tokens'
    OPENMETER_METER_EVENT_TYPE: str = 'tokens'
    OPENMETER_METER_AGGREGATION: str = 'SUM'
    OPENMETER_METER_VALUE_PROPERTY: str = 'tokens'
    OPENMETER_METER_GROUP_BY: List[str] = ['model', 'prompt']
    OPENMETER_METER_WINDOW_SIZE: str = 'DAY'

settings = Settings()
