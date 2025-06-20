"""
End-to-end tests for OpenMeter service integrations.
These tests verify that the CustomerService, MeteringService, and EntitlementService
can interact with the actual OpenMeter API.
"""

import asyncio
import uuid

import pytest
from fastapi import Request

from src.core.config import settings
from src.domain.models.entitlement import EntitlementCreate
from src.domain.services.subject_service import SubjectService
from src.external.metering.openmeter_client import OpenMeterClient
from src.utils.exceptions import ExternalServiceException


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.usefixtures('e2e_environment')
async def test_subject_service_create_delete(openmeter_clients):
    """
    Test that SubjectService can create and delete customers in OpenMeter.
    """
    sync_client, async_client = openmeter_clients
    test_id = uuid.uuid4()
    test_email = f'test-{test_id}@example.com'

    # Create a request with a test user
    req = Request(
        scope={
            'type': 'http',
            'method': 'POST',
            'path': '/test',
            'headers': [(b'accept', b'application/json')],
            'state': {
                'token': 'test_token',
                'user_id': test_id,
                'user_email': test_email,
            },
        }
    )

    metering_client = OpenMeterClient(sync_client, async_client)
    service = SubjectService(metering_client, req)

    # Create the subject
    await service.create_subject()

    # Delete the subject
    await service.delete_subject()

    # Verify deletion by attempting to delete again, which should raise an exception
    with pytest.raises(ExternalServiceException):
        await service.delete_subject()


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.usefixtures('e2e_environment')
async def test_entitlement_service_set_get(subject_service, entitlement_service, test_user_id):
    """
    Test that EntitlementService can set and get entitlements in OpenMeter.
    """
    # Await the async generator fixture to get the service instance
    feature = settings.OPENMETER_FEATURE_KEY

    # Set an entitlement
    limit = EntitlementCreate(feature='ai_tokens', max_limit=1000, period='MONTH')
    await entitlement_service.set_entitlement(limit)

    # Get the entitlement status
    status = await entitlement_service.get_token_entitlement_status(feature)
    assert status is True, 'User should have access after setting entitlement'

    # Get the entitlement value
    value = await entitlement_service.get_entitlement_value(feature)
    assert value.has_access is True, 'User should have access'
    assert value.balance == 1000, 'Balance should be 1000'

    # Test has_access alias
    has_access = await entitlement_service.has_access(feature)
    assert has_access is True, 'has_access should return True'


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.usefixtures('e2e_environment')
async def test_metering_consume_tokens(
    subject_service, entitlement_service, bare_metering_service, test_user_id
):
    """
    Test that MeteringService can consume tokens directly.
    """

    feature = settings.OPENMETER_FEATURE_KEY

    # Set an entitlement
    limit = EntitlementCreate(feature=feature, max_limit=1000, period='MONTH')
    await entitlement_service.set_entitlement(limit)

    # Consume tokens directly
    tokens = 300

    await bare_metering_service.consume_tokens_for_user(test_user_id, tokens)

    # Wait for OpenMeter to update the balance (polling with timeout)
    expected_balance = 1000 - tokens
    value = await entitlement_service.get_entitlement_value(feature)
    for _ in range(10):  # Try for up to ~5 seconds
        if value.balance == expected_balance:
            break
        await asyncio.sleep(0.5)
        value = await entitlement_service.get_entitlement_value(feature)
    else:
        assert value.balance == expected_balance, f'Balance should be {expected_balance}'
