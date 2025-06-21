"""
Centralized error handling for OpenMeter API calls.
"""

from typing import Any, Callable, Coroutine, TypeVar

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from billing_services.utils import logutils
from billing_services.utils.exceptions import ResourceNotFoundException, ExternalServiceException

T = TypeVar('T')
logger = logutils.get_logger(__name__)


async def handle_openmeter_errors(
    func: Callable[..., Coroutine[Any, Any, T]], *args: Any, **kwargs: Any
) -> T:
    """
    Handle OpenMeter API errors in a centralized way.

    Args:
        func: The async function to execute.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The result of the function call.

    Raises:
        ResourceNotFoundException: If the resource is not found.
        ExternalServiceException: For other OpenMeter API errors.
    """
    try:
        return await func(*args, **kwargs)
    except ResourceNotFoundError as e:
        logger.error(f'OpenMeter resource not found: {e}')
        raise ResourceNotFoundException(detail='Resource not found in OpenMeter')
    except HttpResponseError as e:
        logger.error(f'OpenMeter API error: {e}')
        raise ExternalServiceException(
            detail=f'OpenMeter API error: {str(e)}', service_name='OpenMeter'
        )
    except Exception as e:
        logger.error(f'Unexpected error in OpenMeter API call: {e}')
        raise ExternalServiceException(
            detail=f'Unexpected error in OpenMeter API call: {str(e)}', service_name='OpenMeter'
        )
