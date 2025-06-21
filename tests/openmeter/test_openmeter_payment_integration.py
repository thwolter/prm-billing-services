"""
Integration tests for the OpenMeter payment client and service.
"""

import uuid
from datetime import datetime

import pytest

from billing_services.core.config import settings
from billing_services.services.payment_service import PaymentService
from billing_services.clients.payment.openmeter_payment_client import OpenMeterPaymentClient


@pytest.mark.integration
def test_openmeter_payment_client_initialization():
    """
    Integration test to verify initialization of the OpenMeter payment client.

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter payment client and
    verifies that it can be created without errors.
    """
    api_key = settings.OPENMETER.API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        sync_client, async_client = OpenMeterPaymentClient.create_clients()
        payment_client = OpenMeterPaymentClient(sync_client, async_client)
        assert payment_client is not None
    except Exception as exc:
        pytest.fail(f'OpenMeter payment client initialization failed: {exc}')


@pytest.mark.integration
@pytest.mark.asyncio
async def test_payment_service_process_payment():
    """
    Integration test to verify that the payment service can process payments.

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter payment client and
    payment service, processes a payment, and verifies that the payment was processed
    successfully.
    """
    api_key = settings.OPENMETER.API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        # Initialize the payment client and service
        sync_client, async_client = OpenMeterPaymentClient.create_clients()
        payment_client = OpenMeterPaymentClient(sync_client, async_client)
        payment_service = PaymentService(payment_client)

        # Process a payment
        subscription_id = uuid.uuid4()
        amount = 100.0
        currency = 'USD'
        payment_method = 'credit_card'
        metadata = {'test': 'integration', 'timestamp': datetime.now().isoformat()}

        payment = await payment_service.process_payment(
            subscription_id=subscription_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            metadata=metadata,
        )

        # Verify the payment was processed successfully
        assert payment is not None
        assert payment.subscription_id == subscription_id
        assert payment.amount == amount
        assert payment.currency == currency
        assert payment.payment_method == payment_method
        assert payment.status == 'processed'
        assert payment.metadata == metadata

        # Get the payment by ID
        retrieved_payment = await payment_service.get_payment(payment.id)
        assert retrieved_payment is not None
        assert retrieved_payment.id == payment.id
        assert retrieved_payment.subscription_id == subscription_id

        # Get payments for the subscription
        payments = await payment_service.get_payments_for_subscription(subscription_id)
        assert len(payments) >= 1
        assert any(p.id == payment.id for p in payments)

    except Exception as exc:
        pytest.fail(f'Payment service integration test failed: {exc}')


@pytest.mark.integration
@pytest.mark.asyncio
async def test_payment_service_refund_payment():
    """
    Integration test to verify that the payment service can refund payments.

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter payment client and
    payment service, processes a payment, refunds it, and verifies that the refund was
    processed successfully.
    """
    api_key = settings.OPENMETER.API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        # Initialize the payment client and service
        sync_client, async_client = OpenMeterPaymentClient.create_clients()
        payment_client = OpenMeterPaymentClient(sync_client, async_client)
        payment_service = PaymentService(payment_client)

        # Process a payment
        subscription_id = uuid.uuid4()
        amount = 200.0
        currency = 'USD'
        payment_method = 'credit_card'
        metadata = {'test': 'refund_integration', 'timestamp': datetime.now().isoformat()}

        payment = await payment_service.process_payment(
            subscription_id=subscription_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            metadata=metadata,
        )

        # Verify the payment was processed successfully
        assert payment is not None
        assert payment.status == 'processed'

        # Refund the payment
        refunded_payment = await payment_service.refund_payment(payment.id)
        assert refunded_payment is not None
        assert refunded_payment.id == payment.id
        assert refunded_payment.status == 'refunded'

        # Get the payment by ID to verify the refund
        retrieved_payment = await payment_service.get_payment(payment.id)
        assert retrieved_payment is not None
        assert retrieved_payment.id == payment.id
        assert retrieved_payment.status == 'refunded'

    except Exception as exc:
        pytest.fail(f'Payment refund integration test failed: {exc}')


@pytest.mark.integration
@pytest.mark.asyncio
async def test_payment_service_partial_refund():
    """
    Integration test to verify that the payment service can process partial refunds.

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter payment client and
    payment service, processes a payment, partially refunds it, and verifies that the
    partial refund was processed successfully.
    """
    api_key = settings.OPENMETER.API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        # Initialize the payment client and service
        sync_client, async_client = OpenMeterPaymentClient.create_clients()
        payment_client = OpenMeterPaymentClient(sync_client, async_client)
        payment_service = PaymentService(payment_client)

        # Process a payment
        subscription_id = uuid.uuid4()
        amount = 300.0
        currency = 'USD'
        payment_method = 'credit_card'
        metadata = {'test': 'partial_refund_integration', 'timestamp': datetime.now().isoformat()}

        payment = await payment_service.process_payment(
            subscription_id=subscription_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            metadata=metadata,
        )

        # Verify the payment was processed successfully
        assert payment is not None
        assert payment.status == 'processed'

        # Partially refund the payment
        refund_amount = 150.0
        refunded_payment = await payment_service.refund_payment(payment.id, refund_amount)
        assert refunded_payment is not None
        assert refunded_payment.id == payment.id
        assert refunded_payment.status == 'partially_refunded'
        assert refunded_payment.metadata.get('refunded_amount') == refund_amount

        # Get the payment by ID to verify the partial refund
        retrieved_payment = await payment_service.get_payment(payment.id)
        assert retrieved_payment is not None
        assert retrieved_payment.id == payment.id
        assert retrieved_payment.status == 'partially_refunded'
        assert retrieved_payment.metadata.get('refunded_amount') == refund_amount

    except Exception as exc:
        pytest.fail(f'Payment partial refund integration test failed: {exc}')


@pytest.mark.integration
@pytest.mark.asyncio
async def test_payment_service_update_status():
    """
    Integration test to verify that the payment service can update payment status.

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter payment client and
    payment service, processes a payment, updates its status, and verifies that the
    status was updated successfully.
    """
    api_key = settings.OPENMETER.API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        # Initialize the payment client and service
        sync_client, async_client = OpenMeterPaymentClient.create_clients()
        payment_client = OpenMeterPaymentClient(sync_client, async_client)
        payment_service = PaymentService(payment_client)

        # Process a payment
        subscription_id = uuid.uuid4()
        amount = 400.0
        currency = 'USD'
        payment_method = 'credit_card'
        metadata = {'test': 'update_status_integration', 'timestamp': datetime.now().isoformat()}

        payment = await payment_service.process_payment(
            subscription_id=subscription_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            metadata=metadata,
        )

        # Verify the payment was processed successfully
        assert payment is not None
        assert payment.status == 'processed'

        # Update the payment status
        new_status = 'failed'
        updated_payment = await payment_service.update_payment_status(payment.id, new_status)
        assert updated_payment is not None
        assert updated_payment.id == payment.id
        assert updated_payment.status == new_status

        # Get the payment by ID to verify the status update
        retrieved_payment = await payment_service.get_payment(payment.id)
        assert retrieved_payment is not None
        assert retrieved_payment.id == payment.id
        assert retrieved_payment.status == new_status

    except Exception as exc:
        pytest.fail(f'Payment status update integration test failed: {exc}')
