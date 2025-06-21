#!/usr/bin/env python
"""
Command to create a meter in OpenMeter.

This script creates a meter in OpenMeter with the configured settings.

Example usage:
    python -m billing_services.commands.create_meter
"""

import argparse
import asyncio
import sys

from billing_services.core.config import settings
from billing_services.utils import logutils
from billing_services.utils.exceptions import ExternalServiceException
from billing_services.clients.metering.openmeter_metering_client import OpenMeterMeteringClient

logger = logutils.get_logger(__name__)


async def create_meter() -> bool:
    """
    Create a meter in OpenMeter with the configured settings.

    Returns:
        True if the meter was successfully created, False otherwise.
    """
    try:
        # Create the metering client
        metering_client = OpenMeterMeteringClient.from_default()

        # Create the meter
        result = await metering_client.create_meter()

        if result:
            logger.info(f"Successfully created meter {settings.OPENMETER.METER_SLUG}")
        else:
            logger.error(f"Failed to create meter {settings.OPENMETER.METER_SLUG}")

        return result
    except Exception as e:
        logger.error(f"Error creating meter: {e}")
        raise ExternalServiceException(f"Failed to create meter: {e}")


def main() -> None:
    """
    Main entry point for the command.
    """
    parser = argparse.ArgumentParser(description="Create a meter in OpenMeter")

    try:
        # Set up logging
        logutils.setup.setup_logging()

        # Create the meter
        success = asyncio.run(create_meter())

        if not success:
            sys.exit(1)

        logger.info("Successfully created meter")
    except Exception as e:
        logger.error(f"Error creating meter: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
