"""Custom exception classes for the AI Service.

This module defines custom exception classes for different error types in the AI Service.
These exceptions are designed to be caught and handled appropriately by the service handlers
and middleware to provide consistent error responses to clients.
"""
from typing import Any, Dict, List, Optional


class BaseServiceException(Exception):
    """Base exception class for all service exceptions.

    All custom exceptions should inherit from this class to ensure consistent
    error handling and response formatting.
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, str]] = None,
        error_code: Optional[str] = None,
    ):
        """Initialize the exception.

        Args:
            status_code: HTTP status code to return
            detail: Human-readable error message
            headers: Optional HTTP headers to include in the response
            error_code: Optional error code for machine-readable error identification
        """
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        self.error_code = error_code



class ResourceNotFoundException(BaseServiceException):
    """Exception raised when a requested resource is not found."""

    def __init__(
        self,
        detail: str,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize the resource not found exception.

        Args:
            detail: Human-readable error message
            headers: Optional HTTP headers to include in the response
        """
        super().__init__(
            status_code=404, detail=detail, headers=headers, error_code='RESOURCE_NOT_FOUND'
        )


class ExternalServiceException(BaseServiceException):
    """Exception raised when an external service call fails."""

    def __init__(
        self,
        detail: str,
        service_name: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize the external service exception.

        Args:
            detail: Human-readable error message
            service_name: Name of the external service that failed
            headers: Optional HTTP headers to include in the response
        """
        super().__init__(
            status_code=502, detail=detail, headers=headers, error_code='EXTERNAL_SERVICE_ERROR'
        )
        self.service_name = service_name
