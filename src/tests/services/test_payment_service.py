"""Tests for the PaymentService class."""

import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.domain.models.payment import Payment, PaymentEvent
from src.domain.services.payment_service import PaymentService
from src.external.payment.abstract_payment_client import AbstractPaymentClient


class MockPaymentClient(AbstractPaymentClient):
    """Mock implementation of AbstractPaymentClient for testing."""

    def __init__(self):
        self.payments = {}
        self.process_payment_mock = MagicMock()
        self.get_payment_mock = MagicMock()
        self.get_payments_for_subscription_mock = MagicMock()
        self.refund_payment_mock = MagicMock()
        self.update_payment_status_mock = MagicMock()

    def process_payment(self, payment_event: PaymentEvent) -> Payment:
        """Mock implementation of process_payment."""
        self.process_payment_mock(payment_event)
        payment_id = uuid.uuid4()
        payment = Payment(
            id=payment_id,
            subscription_id=payment_event.subscription_id,
            amount=payment_event.amount,
            currency=payment_event.currency,
            status='processed',
            payment_date=datetime.now(),
            payment_method=payment_event.payment_method,
            metadata=payment_event.metadata,
        )
        self.payments[str(payment_id)] = payment
        return payment

    def get_payment(self, payment_id: uuid.UUID) -> Payment:
        """Mock implementation of get_payment."""
        self.get_payment_mock(payment_id)
        return self.payments.get(str(payment_id))

    def get_payments_for_subscription(self, subscription_id: uuid.UUID) -> list[Payment]:
        """Mock implementation of get_payments_for_subscription."""
        self.get_payments_for_subscription_mock(subscription_id)
        return [
            payment
            for payment in self.payments.values()
            if payment.subscription_id == subscription_id
        ]

    def refund_payment(self, payment_id: uuid.UUID, amount=None) -> Payment:
        """Mock implementation of refund_payment."""
        self.refund_payment_mock(payment_id, amount)
        payment = self.get_payment(payment_id)
        if not payment:
            raise ValueError(f'Payment with ID {payment_id} not found')
        payment.status = 'refunded'
        if amount is not None and amount < payment.amount:
            payment.status = 'partially_refunded'
            payment.metadata = payment.metadata or {}
            payment.metadata['refunded_amount'] = amount
        self.payments[str(payment_id)] = payment
        return payment

    def update_payment_status(self, payment_id: uuid.UUID, status: str) -> Payment:
        """Mock implementation of update_payment_status."""
        self.update_payment_status_mock(payment_id, status)
        payment = self.get_payment(payment_id)
        if not payment:
            raise ValueError(f'Payment with ID {payment_id} not found')
        payment.status = status
        self.payments[str(payment_id)] = payment
        return payment


@pytest.mark.asyncio
async def test_process_payment_success():
    """Test that process_payment works correctly."""
    # Create a mock payment client
    mock_client = MockPaymentClient()

    # Create a payment service with the mock client
    service = PaymentService(mock_client)

    # Process a payment
    subscription_id = uuid.uuid4()
    amount = 100.0
    currency = 'USD'
    payment_method = 'credit_card'
    metadata = {'test': 'data'}

    payment = await service.process_payment(
        subscription_id=subscription_id,
        amount=amount,
        currency=currency,
        payment_method=payment_method,
        metadata=metadata,
    )

    # Verify the result
    assert payment.subscription_id == subscription_id
    assert payment.amount == amount
    assert payment.currency == currency
    assert payment.payment_method == payment_method
    assert payment.metadata == metadata
    assert payment.status == 'processed'

    # Verify the mock was called with the correct arguments
    mock_client.process_payment_mock.assert_called_once()
    call_args = mock_client.process_payment_mock.call_args[0][0]
    assert call_args.subscription_id == subscription_id
    assert call_args.amount == amount
    assert call_args.currency == currency
    assert call_args.payment_method == payment_method
    assert call_args.metadata == metadata


@pytest.mark.asyncio
async def test_process_payment_error():
    """Test that process_payment handles errors correctly."""
    # Create a mock payment client that raises an exception
    mock_client = MockPaymentClient()
    mock_client.process_payment_mock.side_effect = Exception('Test error')

    # Create a payment service with the mock client
    service = PaymentService(mock_client)

    # Process a payment - should raise the exception
    subscription_id = uuid.uuid4()

    with pytest.raises(Exception, match='Test error'):
        await service.process_payment(
            subscription_id=subscription_id,
            amount=100.0,
            currency='USD',
            payment_method='credit_card',
        )


@pytest.mark.asyncio
async def test_get_payment_success():
    """Test that get_payment works correctly."""
    # Create a mock payment client
    mock_client = MockPaymentClient()

    # Create a payment service with the mock client
    service = PaymentService(mock_client)

    # Process a payment to create one in the mock client
    subscription_id = uuid.uuid4()
    payment = await service.process_payment(
        subscription_id=subscription_id,
        amount=100.0,
        currency='USD',
        payment_method='credit_card',
    )

    # Get the payment
    retrieved_payment = await service.get_payment(payment.id)

    # Verify the result
    assert retrieved_payment.id == payment.id
    assert retrieved_payment.subscription_id == subscription_id

    # Verify the mock was called with the correct arguments
    mock_client.get_payment_mock.assert_called_once_with(payment.id)


@pytest.mark.asyncio
async def test_get_payment_not_found():
    """Test that get_payment handles not found correctly."""
    # Create a mock payment client
    mock_client = MockPaymentClient()

    # Create a payment service with the mock client
    service = PaymentService(mock_client)

    # Get a payment that doesn't exist
    payment_id = uuid.uuid4()
    payment = await service.get_payment(payment_id)

    # Verify the result
    assert payment is None

    # Verify the mock was called with the correct arguments
    mock_client.get_payment_mock.assert_called_once_with(payment_id)


@pytest.mark.asyncio
async def test_get_payments_for_subscription():
    """Test that get_payments_for_subscription works correctly."""
    # Create a mock payment client
    mock_client = MockPaymentClient()

    # Create a payment service with the mock client
    service = PaymentService(mock_client)

    # Process payments for two different subscriptions
    subscription_id1 = uuid.uuid4()
    subscription_id2 = uuid.uuid4()

    payment1 = await service.process_payment(
        subscription_id=subscription_id1,
        amount=100.0,
        currency='USD',
        payment_method='credit_card',
    )

    payment2 = await service.process_payment(
        subscription_id=subscription_id1,
        amount=200.0,
        currency='USD',
        payment_method='credit_card',
    )

    payment3 = await service.process_payment(
        subscription_id=subscription_id2,
        amount=300.0,
        currency='USD',
        payment_method='credit_card',
    )

    # Get payments for subscription 1
    payments = await service.get_payments_for_subscription(subscription_id1)

    # Verify the result
    assert len(payments) == 2
    assert any(p.id == payment1.id for p in payments)
    assert any(p.id == payment2.id for p in payments)
    assert not any(p.id == payment3.id for p in payments)

    # Verify the mock was called with the correct arguments
    mock_client.get_payments_for_subscription_mock.assert_called_once_with(subscription_id1)


@pytest.mark.asyncio
async def test_refund_payment():
    """Test that refund_payment works correctly."""
    # Create a mock payment client
    mock_client = MockPaymentClient()

    # Create a payment service with the mock client
    service = PaymentService(mock_client)

    # Process a payment
    subscription_id = uuid.uuid4()
    payment = await service.process_payment(
        subscription_id=subscription_id,
        amount=100.0,
        currency='USD',
        payment_method='credit_card',
    )

    # Refund the payment
    refunded_payment = await service.refund_payment(payment.id)

    # Verify the result
    assert refunded_payment.id == payment.id
    assert refunded_payment.status == 'refunded'

    # Verify the mock was called with the correct arguments
    mock_client.refund_payment_mock.assert_called_once_with(payment.id, None)


@pytest.mark.asyncio
async def test_refund_payment_partial():
    """Test that refund_payment works correctly with partial refund."""
    # Create a mock payment client
    mock_client = MockPaymentClient()

    # Create a payment service with the mock client
    service = PaymentService(mock_client)

    # Process a payment
    subscription_id = uuid.uuid4()
    payment = await service.process_payment(
        subscription_id=subscription_id,
        amount=100.0,
        currency='USD',
        payment_method='credit_card',
    )

    # Refund part of the payment
    refund_amount = 50.0
    refunded_payment = await service.refund_payment(payment.id, refund_amount)

    # Verify the result
    assert refunded_payment.id == payment.id
    assert refunded_payment.status == 'partially_refunded'
    assert refunded_payment.metadata['refunded_amount'] == refund_amount

    # Verify the mock was called with the correct arguments
    mock_client.refund_payment_mock.assert_called_once_with(payment.id, refund_amount)


@pytest.mark.asyncio
async def test_refund_payment_not_found():
    """Test that refund_payment handles not found correctly."""
    # Create a mock payment client
    mock_client = MockPaymentClient()
    mock_client.refund_payment_mock.side_effect = ValueError('Payment not found')

    # Create a payment service with the mock client
    service = PaymentService(mock_client)

    # Refund a payment that doesn't exist
    payment_id = uuid.uuid4()

    with pytest.raises(ValueError, match='Payment not found'):
        await service.refund_payment(payment_id)

    # Verify the mock was called with the correct arguments
    mock_client.refund_payment_mock.assert_called_once_with(payment_id, None)


@pytest.mark.asyncio
async def test_update_payment_status():
    """Test that update_payment_status works correctly."""
    # Create a mock payment client
    mock_client = MockPaymentClient()

    # Create a payment service with the mock client
    service = PaymentService(mock_client)

    # Process a payment
    subscription_id = uuid.uuid4()
    payment = await service.process_payment(
        subscription_id=subscription_id,
        amount=100.0,
        currency='USD',
        payment_method='credit_card',
    )

    # Update the payment status
    new_status = 'failed'
    updated_payment = await service.update_payment_status(payment.id, new_status)

    # Verify the result
    assert updated_payment.id == payment.id
    assert updated_payment.status == new_status

    # Verify the mock was called with the correct arguments
    mock_client.update_payment_status_mock.assert_called_once_with(payment.id, new_status)


@pytest.mark.asyncio
async def test_update_payment_status_not_found():
    """Test that update_payment_status handles not found correctly."""
    # Create a mock payment client
    mock_client = MockPaymentClient()
    mock_client.update_payment_status_mock.side_effect = ValueError('Payment not found')

    # Create a payment service with the mock client
    service = PaymentService(mock_client)

    # Update a payment that doesn't exist
    payment_id = uuid.uuid4()

    with pytest.raises(ValueError, match='Payment not found'):
        await service.update_payment_status(payment_id, 'failed')

    # Verify the mock was called with the correct arguments
    mock_client.update_payment_status_mock.assert_called_once_with(payment_id, 'failed')
