"""Wrapper utilities for the pybreaker-based circuit breaker."""

from __future__ import annotations

import logging
from datetime import timedelta
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar

import aiobreaker
from aiobreaker import CircuitBreakerError

from billing_services.utils.exceptions import ExternalServiceException

T = TypeVar('T')

logger = logging.getLogger(__name__)

# Keep a registry of circuit breakers by service name
_circuit_breakers: Dict[str, aiobreaker.CircuitBreaker] = {}


def get_circuit_breaker(service_name: str) -> aiobreaker.CircuitBreaker:
    """Return a circuit breaker for the given service name."""
    if service_name not in _circuit_breakers:
        # Configure the circuit breaker with appropriate timeout settings
        # - fail_max: Maximum number of failures before opening the circuit
        # - timeout_duration: Time to wait before attempting to reset the circuit (in seconds)
        _circuit_breakers[service_name] = aiobreaker.CircuitBreaker(
            name=service_name,
            fail_max=3,
            timeout_duration=timedelta(seconds=30),  # 30 seconds before attempting to reset
        )
    return _circuit_breakers[service_name]


def with_circuit_breaker(service_name: str, fallback_value: Optional[Any] = None):
    """Decorate a synchronous function with a circuit breaker."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        breaker = get_circuit_breaker(service_name)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return breaker.call(func, *args, **kwargs)
            except CircuitBreakerError:
                logger.warning('Circuit breaker for %s is open, failing fast', service_name)
                if fallback_value is not None:
                    return fallback_value
                raise ExternalServiceException(
                    detail=f'Service {service_name} is currently unavailable',
                    service_name=service_name,
                )

        return wrapper

    return decorator
