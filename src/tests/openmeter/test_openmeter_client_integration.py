"""
End-to-end tests for the OpenMeterClient.
These tests interact with a real OpenMeter service and do not use mocks.
"""

import uuid

import pytest
from cloudevents.conversion import to_dict
from cloudevents.http import CloudEvent

from src.core.config import settings
from src.domain.models.usage import UsageEvent
from src.external.metering.openmeter_client import OpenMeterClient


@pytest.mark.integration
def test_openmeter_client_initialization():
    """
    Integration test to verify initialization of the OpenMeter client.

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter client and
    verifies that it can be created without errors.
    """
    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        sync_client, async_client = OpenMeterClient.create_clients()
        client = OpenMeterClient(sync_client, async_client)
        assert client is not None
    except Exception as exc:
        pytest.fail(f'OpenMeter client initialization failed: {exc}')


@pytest.mark.integration
def test_openmeter_client_record_usage():
    """
    Integration test to verify that the OpenMeter client can record usage.

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter client, creates a subject,
    records usage for the subject, and verifies that the usage was recorded successfully.
    """
    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        # Initialize the client
        sync_client, async_client = OpenMeterClient.create_clients()
        client = OpenMeterClient(sync_client, async_client)

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

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter client, creates a subject,
    ingests an event for the subject, and verifies that the event was ingested successfully.
    """
    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        # Initialize the client
        sync_client, async_client = OpenMeterClient.create_clients()
        client = OpenMeterClient(sync_client, async_client)

        # Create a subject
        subject_id = str(uuid.uuid4())
        subject_email = f'test-{subject_id}@example.com'
        client.upsert_subject([{'key': subject_id, 'displayName': subject_email}])

        # Create a cloud event
        event = CloudEvent(
            attributes={
                'id': str(uuid.uuid4()),
                'type': settings.OPENMETER_EVENT_TYPE,
                'source': settings.OPENMETER_SOURCE,
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

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter client, creates multiple
    subjects, lists them, and verifies that the subjects were created and listed correctly.
    """
    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        # Initialize the client
        sync_client, async_client = OpenMeterClient.create_clients()
        client = OpenMeterClient(sync_client, async_client)

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
def test_openmeter_client_delete_subject():
    """
    Integration test to verify that the OpenMeter client can delete subjects.

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter client, creates a subject,
    deletes it, and verifies that the subject was deleted correctly.
    """
    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        # Initialize the client
        sync_client, async_client = OpenMeterClient.create_clients()
        client = OpenMeterClient(sync_client, async_client)

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
def test_openmeter_client_list_entitlements():
    """
    Integration test to verify that the OpenMeter client can list entitlements.

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter client and lists entitlements.
    """
    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        # Initialize the client
        sync_client, async_client = OpenMeterClient.create_clients()
        client = OpenMeterClient(sync_client, async_client)

        # List entitlements
        entitlements = client.list_entitlements()

        # Verify the entitlements were listed correctly
        assert entitlements is not None
        assert isinstance(entitlements, list)
    except Exception as exc:
        pytest.fail(f'OpenMeter client list_entitlements test failed: {exc}')


@pytest.mark.integration
def test_openmeter_client_get_usage():
    """
    Integration test to verify that the OpenMeter client can get usage.

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter client, creates a subject,
    records usage for the subject, gets the usage, and verifies that the usage was retrieved correctly.
    """
    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        # Initialize the client
        sync_client, async_client = OpenMeterClient.create_clients()
        client = OpenMeterClient(sync_client, async_client)

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
