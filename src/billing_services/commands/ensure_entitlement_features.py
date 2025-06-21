#!/usr/bin/env python
"""
Command to ensure that entitlement features exist in the system.

This script checks if the feature specified in the settings exists,
and if not, creates it. This should be run when:
- The parameter in Settings is changed (i.e., feature might now be necessary), or
- Manually triggered (e.g., admin action, migration script).

Example usage:
    python -m billing_services.commands.ensure_entitlement_features
"""

import argparse
import sys
from typing import List, Optional

from billing_services.core.config import settings
from billing_services.utils import logutils
from billing_services.utils.exceptions import ExternalServiceException
from billing_services.clients.metering.openmeter_metering_client import OpenMeterMeteringClient

logger = logutils.get_logger(__name__)


def feature_exists(feature_key: str) -> bool:
    """
    Check if a feature exists in the system.

    Args:
        feature_key: The feature key to check.

    Returns:
        True if the feature exists, False otherwise.
    """
    try:
        # Create the metering client
        metering_sync_client, metering_async_client = OpenMeterMeteringClient.create_clients()
        metering_client = OpenMeterMeteringClient(metering_sync_client, metering_async_client)

        # List all features and check if the feature_key exists
        features = metering_client.list_features()

        # Check if the feature_key is in the list of features
        return feature_key in features
    except Exception as e:
        logger.error(f"Error checking if feature {feature_key} exists: {e}")
        raise ExternalServiceException(f"Failed to check feature existence for {feature_key}: {e}")


def create_feature(feature_key: str) -> None:
    """
    Create a feature in the system.

    Args:
        feature_key: The feature key to create.
    """
    try:
        # Create the metering client
        metering_sync_client, metering_async_client = OpenMeterMeteringClient.create_clients()
        metering_client = OpenMeterMeteringClient(metering_sync_client, metering_async_client)

        # Create the feature using the OpenMeterMeteringClient
        metering_client.create_feature(feature_key)
        logger.info(f"Created feature {feature_key}")
    except Exception as e:
        logger.error(f"Error creating feature {feature_key}: {e}")
        raise


def ensure_features(feature_keys: Optional[List[str]] = None) -> None:
    """
    Ensure that the specified features exist in the system.

    Args:
        feature_keys: Optional list of feature keys to ensure. If not provided,
                     uses the feature key from settings.
    """

    # If no feature keys are provided, use the one from settings
    if not feature_keys:
        feature_keys = [settings.OPENMETER.FEATURE_KEY]

    # Filter out empty or None feature keys
    feature_keys = [key for key in feature_keys if key]

    if not feature_keys:
        logger.warning("No feature keys provided or found in settings. Nothing to ensure.")
        return

    # Ensure each feature exists
    for feature_key in feature_keys:
        try:
            if not feature_exists(feature_key):
                logger.info(f"Feature {feature_key} does not exist, creating it...")
                create_feature(feature_key)
            else:
                logger.info(f"Feature {feature_key} already exists")
        except Exception as e:
            logger.error(f"Error ensuring feature {feature_key}: {e}")
            raise


def main() -> None:
    """
    Main entry point for the command.
    """
    parser = argparse.ArgumentParser(description="Ensure entitlement features exist")
    parser.add_argument(
        "--features",
        nargs="+",
        help="List of feature keys to ensure (default: use the one from settings)",
    )

    args = parser.parse_args()

    try:
        # Set up logging
        logutils.setup.setup_logging()

        # Ensure features
        ensure_features(args.features)
        logger.info("Successfully ensured all features exist")
    except Exception as e:
        logger.error(f"Error ensuring features: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
