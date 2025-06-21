"""Utilities for resilient service execution using a circuit breaker."""

from __future__ import annotations

import inspect
import logging
from functools import wraps
from typing import Any, Callable, Coroutine, Optional, TypeVar, Union

from aiobreaker import CircuitBreakerError

from billing_services.utils.circuit_breaker import get_circuit_breaker
from billing_services.utils.exceptions import ExternalServiceException

T = TypeVar('T')

logger = logging.getLogger(__name__)


def with_resilient_execution(
    service_name: Union[str, Callable[..., str]],
    create_default_response: Optional[Callable[..., Union[T, Coroutine[Any, Any, T]]]] = None,
) -> Callable[[Callable[..., Coroutine[Any, Any, T]]], Callable[..., Coroutine[Any, Any, T]]]:
    """Decorate an async function with circuit breaker and fallback handling."""

    def decorator(
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            # If service_name is a callable, call it with the instance (self) as the first argument
            if callable(service_name) and args:
                svc_name = service_name(args[0])
            else:
                svc_name = service_name if isinstance(service_name, str) else service_name(*args, **kwargs)

            breaker = get_circuit_breaker(svc_name)

            try:
                return await breaker.call_async(func, *args, **kwargs)
            except CircuitBreakerError:
                logger.warning('Circuit breaker for %s is open, failing fast', svc_name)
                if create_default_response:
                    result = create_default_response(*args, **kwargs)
                    if inspect.isawaitable(result):
                        result = await result
                    return result
                raise ExternalServiceException(
                    detail=f'Service {svc_name} is currently unavailable', service_name=svc_name
                )

            except Exception as error:  # pragma: no cover - unexpected error
                logger.warning('Service %s failed: %s', svc_name, error)

                if create_default_response:
                    try:
                        result = create_default_response(*args, **kwargs)
                        if inspect.isawaitable(result):
                            result = await result
                        return result
                    except Exception as fallback_error:
                        logger.error(f'Fallback for {svc_name} failed: {fallback_error}')
                        # If the fallback fails, raise the original error
                        raise ExternalServiceException(
                            detail=f'Service {svc_name} failed: {str(error)}',
                            service_name=svc_name,
                        )
                raise ExternalServiceException(
                    detail=f'Service {svc_name} failed: {error}', service_name=svc_name
                )

        return wrapper

    return decorator
