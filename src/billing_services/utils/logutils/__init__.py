"""
Logging package for the application.

This package provides utilities for configuring and using logutils
in a consistent way throughout the application.

It re-exports the standard logutils module for backward compatibility.
"""

# Import the standard logutils module first to avoid circular imports
import logging

# Re-export the standard logutils module for backward compatibility
# This allows code that imports from src.billing_services.core.logutils to continue working
__all__ = [
    'logging',
    'CustomFormatter',
    'create_default_formatter',
    'get_log_level',
    'create_console_handler',
    'configure_root_logger',
    'setup_logging',
    'get_logger',
]

from billing_services.utils.logutils.config import configure_root_logger, create_console_handler, get_log_level

# Now import the rest of the modules
from billing_services.utils.logutils.formatters import CustomFormatter, create_default_formatter
from billing_services.utils.logutils.setup import get_logger, setup_logging

# Set up logutils when the package is imported
setup_logging()
