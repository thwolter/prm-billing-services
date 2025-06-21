"""
End-to-end tests for OpenMeter service integrations.
These tests verify that the CustomerService, MeteringService, and EntitlementService
can interact with the actual OpenMeter API.
"""

import asyncio
import uuid

import pytest

from billing_services.clients.entitlements.openmeter_entitlement_client import OpenMeterEntitlementClient
from billing_services.services import EntitlementService
from billing_services.utils.exceptions import ExternalServiceException
from billing_services.core.config import settings
from billing_services.models.entitlement import EntitlementCreate
from billing_services.services.subject_service import SubjectService
from billing_services.clients.metering.openmeter_metering_client import OpenMeterMeteringClient


@pytest.mark.asyncio
async def test_subject_service_create_delete():
    """
    Test that SubjectService can create and delete customers in OpenMeter.

    This test accesses the locally installed OpenMeter instance directly without mocking.
    The local OpenMeter instance should be running at the URL specified in the .env file.
    """
    test_id = uuid.uuid4()
    test_email = f'test-{test_id}@example.com'

    metering_client = OpenMeterMeteringClient.from_default()
    service = SubjectService(metering_client)

    # Create the subject
    await service.create_subject(subject_id=test_id, user_email=test_email)

    # Delete the subject
    await service.delete_subject(subject_id=test_id)

    # Verify deletion by attempting to delete again, which should raise an exception
    with pytest.raises(ExternalServiceException):
        await service.delete_subject(subject_id=test_id)


@pytest.mark.asyncio
async def test_entitlement_service_set_get():
    """
    Test that EntitlementService can set and get entitlements in OpenMeter.

    This test accesses the locally installed OpenMeter instance directly without mocking.
    The local OpenMeter instance should be running at the URL specified in the .env file.
    """
    entitlement_client = OpenMeterEntitlementClient.from_default()

    # Create a test user ID
    test_user_id = uuid.uuid4()

    # Create a subject first
    metering_client = OpenMeterMeteringClient.from_default()
    subject_service = SubjectService(metering_client)
    test_email = f'test-{test_user_id}@example.com'
    await subject_service.create_subject(subject_id=test_user_id, user_email=test_email)

    # Create the entitlement service
    entitlement_service = EntitlementService(entitlement_client)

    feature = settings.OPENMETER_FEATURE_KEY

    # Set an entitlement
    limit = EntitlementCreate(feature=settings.OPENMETER_FEATURE_KEY, max_limit=1000, period='MONTH')
    await entitlement_service.set_entitlement(test_user_id, limit)

    # Get the entitlement status
    status = await entitlement_service.get_token_entitlement_status(test_user_id, feature)
    assert status is True, 'User should have access after setting entitlement'

    # Get the entitlement value
    value = await entitlement_service.get_entitlement_value(test_user_id, feature)
    assert value.has_access is True, 'User should have access'
    assert value.balance == 1000, 'Balance should be 1000'

    # Test has_access alias
    has_access = await entitlement_service.has_access(test_user_id, feature)
    assert has_access is True, 'has_access should return True'

    # Clean up
    await subject_service.delete_subject(subject_id=test_user_id)


@pytest.mark.asyncio
async def test_metering_consume_tokens():
    """
    Test that MeteringService can consume tokens directly.

    This test accesses the locally installed OpenMeter instance directly without mocking.
    The local OpenMeter instance should be running at the URL specified in the .env file.
    """
    # Create OpenMeter clients directly
    from billing_services.clients.entitlements.openmeter_entitlement_client import OpenMeterEntitlementClient
    from billing_services.services.entitlement_service import EntitlementService
    from billing_services.services.metering_service import MeteringService
    from billing_services.models.usage import ConsumedTokensInfo

    # Create a test user ID
    test_user_id = uuid.uuid4()

    # Create a subject first
    metering_sync_client, metering_async_client = OpenMeterMeteringClient.create_clients()
    metering_client = OpenMeterMeteringClient(metering_sync_client, metering_async_client)
    subject_service = SubjectService(metering_client)
    test_email = f'test-{test_user_id}@example.com'
    await subject_service.create_subject(subject_id=test_user_id, user_email=test_email)

    # Create the entitlement service
    entitlement_sync_client, entitlement_async_client = OpenMeterEntitlementClient.create_clients()
    entitlement_client = OpenMeterEntitlementClient(entitlement_sync_client, entitlement_async_client)
    entitlement_service = EntitlementService(entitlement_client)

    # Create the metering service
    metering_service = MeteringService(metering_client)

    feature = settings.OPENMETER_FEATURE_KEY

    # Set an entitlement
    limit = EntitlementCreate(feature=feature, max_limit=1000, period='MONTH')
    await entitlement_service.set_entitlement(test_user_id, limit)

    # Consume tokens directly
    tokens = 300
    token_info = ConsumedTokensInfo(
        consumed_tokens=tokens,
        model_name="test-model",
        prompt_name="test-prompt"
    )

    await metering_service.consume_tokens(test_user_id, token_info)

    # Wait for OpenMeter to update the balance (polling with timeout)
    expected_balance = 1000 - tokens
    value = await entitlement_service.get_entitlement_value(test_user_id, feature)
    for _ in range(10):  # Try for up to ~5 seconds
        if value.balance == expected_balance:
            break
        await asyncio.sleep(0.5)
        value = await entitlement_service.get_entitlement_value(test_user_id, feature)
    else:
        assert value.balance == expected_balance, f'Balance should be {expected_balance}'

    # Clean up
    await subject_service.delete_subject(subject_id=test_user_id)
