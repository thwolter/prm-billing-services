"""
End-to-end tests for the OpenMeterMeteringClient.
These tests interact with a real OpenMeter service and do not use mocks.
"""

import asyncio
import uuid

import pytest
from cloudevents.conversion import to_dict
from cloudevents.http import CloudEvent

from billing_services.core.config import settings
from billing_services.models.usage import UsageEvent
from billing_services.clients.metering.openmeter_metering_client import OpenMeterMeteringClient


@pytest.mark.integration
def test_openmeter_client_initialization():
    """
    Integration test to verify initialization of the OpenMeter client.

    This test initializes the OpenMeter client and verifies that it can be created without errors.
    """

    try:
        client = OpenMeterMeteringClient.from_default()
        assert client is not None
    except Exception as exc:
        pytest.fail(f'OpenMeter client initialization failed: {exc}')


@pytest.mark.integration
def test_openmeter_client_from_default():
    """
    Integration test to verify the from_default class method of the OpenMeter client.

    This test initializes the OpenMeter client using the from_default method and 
    verifies that it can be created without errors.
    """

    try:
        client = OpenMeterMeteringClient.from_default()
        assert client is not None
        assert isinstance(client, OpenMeterMeteringClient)
        assert client.sync_client is not None
        assert client.async_client is not None
    except Exception as exc:
        pytest.fail(f'OpenMeter client from_default initialization failed: {exc}')


@pytest.mark.integration
def test_openmeter_client_record_usage():
    """
    Integration test to verify that the OpenMeter client can record usage.

    This test initializes the OpenMeter client, creates a subject,
    records usage for the subject, and verifies that the usage was recorded successfully.
    """

    try:
        # Initialize the client
        client = OpenMeterMeteringClient.from_default()

        # Create a subject
        subject_id = str(uuid.uuid4())
        subject_email = f'test-{subject_id}@example.com'
        client.upsert_subject([{'key': subject_id, 'displayName': subject_email}])

        # Record usage
        usage_event = UsageEvent(tokens=100, model='test-model', prompt='test-prompt')
        result = client.record_usage(subject_id, usage_event)

        # Verify the usage was recorded successfully
        assert result is True

        # Clean up
        client.delete_subject(subject_id)
    except Exception as exc:
        pytest.fail(f'OpenMeter client record_usage test failed: {exc}')


@pytest.mark.integration
def test_openmeter_client_ingest_events():
    """
    Integration test to verify that the OpenMeter client can ingest events.

    This test initializes the OpenMeter client, creates a subject,
    ingests an event for the subject, and verifies that the event was ingested successfully.
    """

    try:
        # Initialize the client
        client = OpenMeterMeteringClient.from_default()

        # Create a subject
        subject_id = str(uuid.uuid4())
        subject_email = f'test-{subject_id}@example.com'
        client.upsert_subject([{'key': subject_id, 'displayName': subject_email}])

        # Create a cloud event
        event = CloudEvent(
            attributes={
                'id': str(uuid.uuid4()),
                'type': settings.OPENMETER.TOKEN_EVENT_TYPE,
                'source': settings.OPENMETER.SOURCE,
                'subject': subject_id,
            },
            data={'tokens': 100, 'model': 'test-model', 'prompt': 'test-prompt'},
        )

        # Ingest the event
        result = client.ingest_events(to_dict(event))

        # Verify the event was ingested successfully
        assert result is True

        # Clean up
        client.delete_subject(subject_id)
    except Exception as exc:
        pytest.fail(f'OpenMeter client ingest_events test failed: {exc}')


@pytest.mark.integration
def test_openmeter_client_upsert_and_list_subjects():
    """
    Integration test to verify that the OpenMeter client can upsert and list subjects.

    This test initializes the OpenMeter client, creates multiple subjects, 
    lists them, and verifies that the subjects were created and listed correctly.
    """

    try:
        # Initialize the client
        client = OpenMeterMeteringClient.from_default()

        # Create subjects
        subject1_id = str(uuid.uuid4())
        subject1_email = f'test-{subject1_id}@example.com'
        subject2_id = str(uuid.uuid4())
        subject2_email = f'test-{subject2_id}@example.com'

        client.upsert_subject(
            [
                {'key': subject1_id, 'displayName': subject1_email},
                {'key': subject2_id, 'displayName': subject2_email},
            ]
        )

        # List subjects
        subjects = client.list_subjects()

        # Verify the subjects were created and listed correctly
        assert subjects is not None
        assert isinstance(subjects, list)

        # Find our test subjects in the list
        subject1_found = False
        subject2_found = False

        for subject in subjects:
            if str(subject.id) == subject1_id:
                subject1_found = True
                assert subject.email == subject1_email or subject.display_name == subject1_email
            elif str(subject.id) == subject2_id:
                subject2_found = True
                assert subject.email == subject2_email or subject.display_name == subject2_email

        assert subject1_found, f'Subject {subject1_id} not found in the list'
        assert subject2_found, f'Subject {subject2_id} not found in the list'

        # Clean up
        client.delete_subject(subject1_id)
        client.delete_subject(subject2_id)
    except Exception as exc:
        pytest.fail(f'OpenMeter client upsert_and_list_subjects test failed: {exc}')


@pytest.mark.integration
@pytest.mark.asyncio
async def test_openmeter_client_upsert_subject_async():
    """
    Integration test to verify that the OpenMeter client can upsert subjects asynchronously.

    This test initializes the OpenMeter client, creates a subject asynchronously, 
    and verifies that the subject was created correctly.
    """

    try:
        # Initialize the client
        client = OpenMeterMeteringClient.from_default()

        # Create a subject asynchronously
        subject_id = str(uuid.uuid4())
        subject_email = f'test-{subject_id}@example.com'
        await client.upsert_subject_async([{'key': subject_id, 'displayName': subject_email}])

        # List subjects to verify the subject was created
        subjects = client.list_subjects()
        subject_found = any(str(subject.id) == subject_id for subject in subjects)
        assert subject_found, f'Subject {subject_id} not found after async upsert'

        # Clean up
        client.delete_subject(subject_id)
    except Exception as exc:
        pytest.fail(f'OpenMeter client upsert_subject_async test failed: {exc}')


@pytest.mark.integration
def test_openmeter_client_delete_subject():
    """
    Integration test to verify that the OpenMeter client can delete subjects.

    This test initializes the OpenMeter client, creates a subject,
    deletes it, and verifies that the subject was deleted correctly.
    """

    try:
        # Initialize the client
        client = OpenMeterMeteringClient.from_default()

        # Create a subject
        subject_id = str(uuid.uuid4())
        subject_email = f'test-{subject_id}@example.com'
        client.upsert_subject([{'key': subject_id, 'displayName': subject_email}])

        # List subjects to verify the subject was created
        subjects_before = client.list_subjects()
        subject_found_before = any(str(subject.id) == subject_id for subject in subjects_before)
        assert subject_found_before, f'Subject {subject_id} not found before deletion'

        # Delete the subject
        client.delete_subject(subject_id)

        # List subjects to verify the subject was deleted
        subjects_after = client.list_subjects()
        subject_found_after = any(str(subject.id) == subject_id for subject in subjects_after)
        assert not subject_found_after, f'Subject {subject_id} still found after deletion'
    except Exception as exc:
        pytest.fail(f'OpenMeter client delete_subject test failed: {exc}')


@pytest.mark.integration
@pytest.mark.asyncio
async def test_openmeter_client_delete_subject_async():
    """
    Integration test to verify that the OpenMeter client can delete subjects asynchronously.

    This test initializes the OpenMeter client, creates a subject,
    deletes it asynchronously, and verifies that the subject was deleted correctly.
    """

    try:
        # Initialize the client
        client = OpenMeterMeteringClient.from_default()

        # Create a subject
        subject_id = str(uuid.uuid4())
        subject_email = f'test-{subject_id}@example.com'
        client.upsert_subject([{'key': subject_id, 'displayName': subject_email}])

        # List subjects to verify the subject was created
        subjects_before = client.list_subjects()
        subject_found_before = any(str(subject.id) == subject_id for subject in subjects_before)
        assert subject_found_before, f'Subject {subject_id} not found before async deletion'

        # Delete the subject asynchronously
        await client.delete_subject_async(subject_id)

        # List subjects to verify the subject was deleted
        subjects_after = client.list_subjects()
        subject_found_after = any(str(subject.id) == subject_id for subject in subjects_after)
        assert not subject_found_after, f'Subject {subject_id} still found after async deletion'
    except Exception as exc:
        pytest.fail(f'OpenMeter client delete_subject_async test failed: {exc}')


@pytest.mark.integration
def test_openmeter_client_list_entitlements():
    """
    Integration test to verify that the OpenMeter client can list entitlements.

    This test initializes the OpenMeter client and lists entitlements.
    """

    try:
        # Initialize the client
        client = OpenMeterMeteringClient.from_default()

        # List entitlements
        entitlements = client.list_entitlements()

        # Verify the entitlements were listed correctly
        assert entitlements is not None
        assert isinstance(entitlements, list)
    except Exception as exc:
        pytest.fail(f'OpenMeter client list_entitlements test failed: {exc}')


@pytest.mark.integration
def test_openmeter_client_list_features():
    """
    Integration test to verify that the OpenMeter client can list features.

    This test initializes the OpenMeter client and lists features.
    """

    try:
        # Initialize the client
        client = OpenMeterMeteringClient.from_default()

        # List features
        features = client.list_features()

        # Verify the features were listed correctly
        assert features is not None
        assert isinstance(features, list)
    except Exception as exc:
        pytest.fail(f'OpenMeter client list_features test failed: {exc}')


@pytest.mark.integration
def test_openmeter_client_create_feature():
    """
    Integration test to verify that the OpenMeter client can create features.

    This test initializes the OpenMeter client, creates a feature,
    and verifies that the feature was created correctly.
    """

    try:
        client = OpenMeterMeteringClient.from_default()

        # Create a unique feature key
        feature_key = f'test-feature-{uuid.uuid4()}'

        # Create the feature
        client.create_feature(feature_key)

        # List features to verify the feature was created
        features = client.list_features()
        feature_found = feature_key in features
        assert feature_found, f'Feature {feature_key} not found after creation'

        # Test creating the same feature again (should not raise an exception)
        client.create_feature(feature_key)
    except Exception as exc:
        pytest.fail(f'OpenMeter client create_feature test failed: {exc}')


@pytest.mark.integration
def test_openmeter_client_create_meter():
    """
    Integration test to verify that the OpenMeter client can create meters.

    This test initializes the OpenMeter client, creates a meter,
    and verifies that the meter was created correctly.
    """

    # Initialize the client
    client = OpenMeterMeteringClient.from_default()

    try:
        client.sync_client.delete_meter(settings.OPENMETER.METER_SLUG)
    except Exception as exc:
        pytest.fail(f'OpenMeter client delete_meter test failed: {exc}')

    try:
        # Create the meter
        result = client.create_meter()

        # Verify the meter was created successfully
        assert result is True
    except Exception as exc:
        pytest.fail(f'OpenMeter client create_meter test failed: {exc}')


@pytest.mark.integration
def test_openmeter_client_get_usage():
    """
    Integration test to verify that the OpenMeter client can get usage.

    This test initializes the OpenMeter client, creates a subject,
    records usage for the subject, gets the usage, and verifies that the usage was retrieved correctly.
    """

    try:
        # Initialize the client
        sync_client, async_client = OpenMeterMeteringClient.create_clients()
        client = OpenMeterMeteringClient(sync_client, async_client)

        # Create a subject
        subject_id = str(uuid.uuid4())
        subject_email = f'test-{subject_id}@example.com'
        client.upsert_subject([{'key': subject_id, 'displayName': subject_email}])

        # Record usage
        usage_event = UsageEvent(tokens=100, model='test-model', prompt='test-prompt')
        client.record_usage(subject_id, usage_event)

        # Get usage
        usage = client.get_usage(subject_id)

        # Verify the usage was retrieved correctly
        assert usage is not None
        assert hasattr(usage, 'sufficient')
        assert hasattr(usage, 'token_limit')
        assert hasattr(usage, 'consumed_tokens')
        assert hasattr(usage, 'remaining_tokens')

        # Clean up
        client.delete_subject(subject_id)
    except Exception as exc:
        pytest.fail(f'OpenMeter client get_usage test failed: {exc}')
