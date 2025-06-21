#!/usr/bin/env python
"""
Command to meter tokens for a subject.

This script meters tokens for a subject using the OpenMeter metering client.

Example usage:
    python -m billing_services.commands.meter_tokens --subject customer-1 --tokens 10 --model gpt-4 --prompt "Hello, world!"
"""

import argparse
import sys
from typing import Optional

from billing_services.core.config import settings
from billing_services.utils import logutils
from billing_services.utils.exceptions import ExternalServiceException
from billing_services.clients.metering.openmeter_metering_client import OpenMeterMeteringClient

logger = logutils.get_logger(__name__)


def meter_tokens(subject_id: str, tokens: int, model: str, prompt: str) -> bool:
    """
    Meter tokens for a subject.

    Args:
        subject_id: The ID of the subject.
        tokens: The number of tokens to meter.
        model: The model used.
        prompt: The prompt used.

    Returns:
        True if the tokens were successfully metered, False otherwise.
    """
    try:
        # Create the metering client
        metering_sync_client, metering_async_client = OpenMeterMeteringClient.create_clients()
        metering_client = OpenMeterMeteringClient(metering_sync_client, metering_async_client)

        # Meter tokens
        result = metering_client.meter_tokens(subject_id, tokens, model, prompt)
        
        if result:
            logger.info(f"Successfully metered {tokens} tokens for subject {subject_id}")
        else:
            logger.error(f"Failed to meter {tokens} tokens for subject {subject_id}")
        
        return result
    except Exception as e:
        logger.error(f"Error metering tokens for subject {subject_id}: {e}")
        raise ExternalServiceException(f"Failed to meter tokens for subject {subject_id}: {e}")


def main() -> None:
    """
    Main entry point for the command.
    """
    parser = argparse.ArgumentParser(description="Meter tokens for a subject")
    parser.add_argument(
        "--subject",
        required=True,
        help="Subject ID to meter tokens for",
    )
    parser.add_argument(
        "--tokens",
        type=int,
        required=True,
        help="Number of tokens to meter",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Model used",
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Prompt used",
    )

    args = parser.parse_args()

    try:
        # Set up logging
        logutils.setup.setup_logging()

        # Meter tokens
        success = meter_tokens(args.subject, args.tokens, args.model, args.prompt)
        
        if not success:
            sys.exit(1)
            
        logger.info("Successfully metered tokens")
    except Exception as e:
        logger.error(f"Error metering tokens: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()