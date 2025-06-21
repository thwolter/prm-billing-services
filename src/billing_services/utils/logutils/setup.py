"""Setup functions for logutils."""

import logging

from billing_services.utils.logutils.config import configure_root_logger


def setup_logging() -> None:
    """
    Set up logutils for the application.

    This function configures the root logutils with the default settings.
    It should be called once at application startup.
    """
    configure_root_logger()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logutils with the specified name.

    This is a convenience function that ensures the logutils system
    is set up before returning a logutils.

    Args:
        name: The name of the logutils.

    Returns:
        A configured logutils instance.
    """
    return logging.getLogger(name)
