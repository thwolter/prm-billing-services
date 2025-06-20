"""Tests for the BaseService class."""

from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel, Field
from riskgpt.models.schemas import ResponseInfo

from src.services.base_service import BaseService


@pytest.mark.ignore
class TestQueryModel(BaseModel):
    """Test query model."""

    query: str


@pytest.mark.ignore
class TestResultModel(BaseModel):
    """Test result model."""

    success: bool
    result: str = ''
    error: str = ''
    response_info: ResponseInfo = Field(default_factory=ResponseInfo)


class TestService(BaseService):
    """Test service implementation."""

    chain_fn = None
    route_path = '/test'
    QueryModel = TestQueryModel
    ResultModel = TestResultModel


@pytest.mark.asyncio
async def test_base_service_execute_query_success():
    """Test that execute_query works correctly with successful chain function."""
    # Create a mock chain function that returns a successful result
    mock_chain_fn = AsyncMock(
        return_value=TestResultModel(
            success=True,
            result='test result',
            response_info=ResponseInfo(
                consumed_tokens=100,
                total_cost=0.02,
                prompt_name='test_prompt',
                model_name='test_model',
            ),
        )
    )

    # Create a test service with the mock chain function
    service = TestService()
    service.__class__.chain_fn = mock_chain_fn

    # Execute a query
    query = TestQueryModel(query='test query')
    result = await service.execute_query(query)

    # Verify the result
    assert result.success is True
    assert result.result == 'test result'
    mock_chain_fn.assert_called_once_with(query)


@pytest.mark.asyncio
async def test_base_service_execute_query_failure():
    """Test that execute_query handles failures correctly."""
    # Create a mock chain function that raises an exception
    mock_chain_fn = AsyncMock(side_effect=Exception('test error'))

    # Create a test service with the mock chain function
    service = TestService()
    service.__class__.chain_fn = mock_chain_fn

    # Execute a query - should return a fallback response
    query = TestQueryModel(query='test query')
    result = await service.execute_query(query)

    # Verify the result
    assert result.success is False
    assert 'temporarily unavailable' in result.error
    mock_chain_fn.assert_called_once_with(query)


@pytest.mark.asyncio
async def test_base_service_execute_query_circuit_open():
    """Test that execute_query handles open circuit correctly."""
    # Create a mock chain function
    mock_chain_fn = AsyncMock(
        return_value=TestResultModel(
            success=True,
            result='test result',
            response_info=ResponseInfo(
                consumed_tokens=100,
                total_cost=0.02,
                prompt_name='test_prompt',
                model_name='test_model',
            ),
        )
    )

    # Create a test service with the mock chain function
    service = TestService()
    service.__class__.chain_fn = mock_chain_fn

    # Open the circuit for the service
    from src.utils.circuit_breaker import get_circuit_breaker

    cb = get_circuit_breaker('TestService')
    cb.open()

    # Execute a query - should return a fallback response without calling the chain function
    query = TestQueryModel(query='test query')
    result = await service.execute_query(query)

    # Verify the result
    assert result.success is False
    assert 'currently unavailable' in result.error
    mock_chain_fn.assert_not_called()


@pytest.mark.asyncio
async def test_base_service_execute_query_no_chain_fn():
    """Test that execute_query raises RuntimeError when chain_fn is not set."""
    # Create a test service without a chain function
    service = TestService()
    service.__class__.chain_fn = None

    # Execute a query - should raise RuntimeError
    query = TestQueryModel(query='test query')
    with pytest.raises(RuntimeError, match='riskgpt is not installed'):
        await service.execute_query(query)
