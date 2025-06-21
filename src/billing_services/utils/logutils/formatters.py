"""Formatters for logutils messages."""

import logging


class CustomFormatter(logging.Formatter):
    """
    Custom formatter that pads log level names for better readability.

    This formatter ensures that all log level names have consistent width
    in the log output, making it easier to read and parse logs visually.
    """

    def format(self, record):
        """
        Format the log record by padding the level name.

        Args:
            record: The log record to format.

        Returns:
            The formatted log message.
        """
        levelname = record.levelname
        if levelname == 'INFO':
            levelname = 'INFO:    '
        elif levelname == 'DEBUG':
            levelname = 'DEBUG:   '
        elif levelname == 'WARNING':
            levelname = 'WARNING: '
        elif levelname == 'ERROR':
            levelname = 'ERROR:   '
        elif levelname == 'CRITICAL':
            levelname = 'CRITICAL:'
        record.levelname = levelname
        return super().format(record)


def create_default_formatter():
    """
    Create the default formatter used by the application.

    Returns:
        A CustomFormatter instance with the default format string.
    """
    return CustomFormatter('%(levelname)s [%(name)s] %(message)s')
