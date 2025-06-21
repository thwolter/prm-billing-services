"""Configuration utilities for logutils."""

import logging
import sys
from typing import List, Optional

from billing_services.core.config import settings
from billing_services.utils.logutils.formatters import create_default_formatter


def get_log_level() -> int:
    """
    Get the log level from settings.

    Returns:
        The log level as an integer constant from the logutils module.
    """
    return getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)


def create_console_handler(stream=sys.stdout) -> logging.StreamHandler:
    """
    Create a console handler that writes to the specified stream.

    Args:
        stream: The stream to write to (default: sys.stdout).

    Returns:
        A configured StreamHandler instance.
    """
    return logging.StreamHandler(stream)


def configure_root_logger(
    level: Optional[int] = None,
    handlers: Optional[List[logging.Handler]] = None,
    formatter: Optional[logging.Formatter] = None,
) -> None:
    """
    Configure the root logutils with the specified level, handlers, and formatter.

    Args:
        level: The log level to use (default: from settings).
        handlers: The handlers to add to the root logutils (default: console handler).
        formatter: The formatter to use for all handlers (default: CustomFormatter).
    """
    if level is None:
        level = get_log_level()

    if handlers is None:
        handlers = [create_console_handler()]

    if formatter is None:
        formatter = create_default_formatter()

    # Configure basic logutils
    logging.basicConfig(level=level, handlers=handlers)

    # Apply the formatter to all handlers
    for handler in logging.root.handlers:
        handler.setFormatter(formatter)
