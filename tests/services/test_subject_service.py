"""
Integration tests for the SubjectService.
"""

import uuid
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

import pytest
from azure.core.exceptions import ResourceNotFoundError

from billing_services.services.subject_service import SubjectService
from billing_services.clients.metering.abstract_metering_client import AbstractMeteringClient


class MockMeteringClient(AbstractMeteringClient):
    """Mock implementation of AbstractMeteringClient for testing."""

    def __init__(self):
        self.subjects = {}
        self.entitlements = {}
        self.upsert_subject_mock = Mock()
        self.delete_subject_mock = Mock()
        self.list_subjects_mock = Mock()
        self.list_entitlements_mock = Mock()

    def record_usage(self, subject_id: str, usage_event: Any) -> bool:
        """Mock implementation of record_usage."""
        return True

    def get_usage(self, subject_id: str) -> Any:
        """Mock implementation of get_usage."""
        return None

    def upsert_subject(self, subjects: List[Dict[str, Any]]) -> None:
        """Mock implementation of upsert_subject."""
        self.upsert_subject_mock(subjects)
        for subject in subjects:
            self.subjects[subject['key']] = subject

    def delete_subject(self, subject_id: str) -> None:
        """Mock implementation of delete_subject."""
        self.delete_subject_mock(subject_id)
        if subject_id not in self.subjects:
            raise ResourceNotFoundError(f'Subject {subject_id} not found')
        del self.subjects[subject_id]

    def list_subjects(self) -> List[Dict[str, Any]]:
        """Mock implementation of list_subjects."""
        self.list_subjects_mock()
        return [
            {'key': key, 'displayName': value.get('displayName')}
            for key, value in self.subjects.items()
        ]

    def list_entitlements(self, subject: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Mock implementation of list_entitlements."""
        self.list_entitlements_mock(subject)
        if not subject:
            return list(self.entitlements.values())

        result = []
        for subj_id in subject:
            if subj_id in self.entitlements:
                result.append(self.entitlements[subj_id])

        if not result and subject:
            raise ResourceNotFoundError(f'No entitlements found for subjects {subject}')

        return result

    def ingest_events(self, events: Dict[str, Any]) -> bool:
        """Mock implementation of ingest_events."""
        return True

    def add_entitlement(self, subject_id: str, entitlement: Dict[str, Any]) -> None:
        """Helper method to add an entitlement for testing."""
        self.entitlements[subject_id] = entitlement


@pytest.mark.asyncio
async def test_create_subject():
    """Test that create_subject works correctly."""
    # Create a mock metering client
    mock_client = MockMeteringClient()

    # Create a subject service with the mock client
    user_id = uuid.uuid4()
    user_email = 'test@example.com'
    service = SubjectService(mock_client)

    # Create a subject
    await service.create_subject(user_id=user_id, user_email=user_email)

    # Verify the mock was called with the correct arguments
    mock_client.upsert_subject_mock.assert_called_once()
    call_args = mock_client.upsert_subject_mock.call_args[0][0]
    assert len(call_args) == 1
    assert call_args[0]['key'] == str(user_id)
    assert call_args[0]['displayName'] == user_email


@pytest.mark.asyncio
async def test_create_subject_with_parameters():
    """Test that create_subject works correctly with parameters."""
    # Create a mock metering client
    mock_client = MockMeteringClient()

    # Create test data
    user_id = uuid.uuid4()
    user_email = 'test@example.com'

    # Create a subject service with the mock client
    service = SubjectService(mock_client)

    # Create a subject
    await service.create_subject(subject_id=user_id, user_email=user_email)

    # Verify the mock was called with the correct arguments
    mock_client.upsert_subject_mock.assert_called_once()
    call_args = mock_client.upsert_subject_mock.call_args[0][0]
    assert len(call_args) == 1
    assert call_args[0]['key'] == str(user_id)
    assert call_args[0]['displayName'] == user_email


@pytest.mark.asyncio
async def test_create_subject_no_user_id():
    """Test that create_subject handles missing user ID correctly."""
    # Create a mock metering client
    mock_client = MockMeteringClient()

    # Create a subject service with the mock client
    service = SubjectService(mock_client)

    # Create a subject without user ID
    await service.create_subject()

    # Verify the mock was not called
    mock_client.upsert_subject_mock.assert_not_called()


@pytest.mark.asyncio
async def test_delete_subject():
    """Test that delete_subject works correctly."""
    # Create a mock metering client
    mock_client = MockMeteringClient()

    # Create a subject service with the mock client
    user_id = uuid.uuid4()
    service = SubjectService(mock_client)

    # Add a subject to the mock client
    mock_client.upsert_subject([{'key': str(user_id), 'displayName': 'test@example.com'}])

    # Delete the subject
    await service.delete_subject(user_id=user_id)

    # Verify the mock was called with the correct arguments
    mock_client.delete_subject_mock.assert_called_once_with(str(user_id))


@pytest.mark.asyncio
async def test_delete_subject_not_found():
    """Test that delete_subject handles not found correctly."""
    # Create a mock metering client
    mock_client = MockMeteringClient()

    # Create a subject service with the mock client
    user_id = uuid.uuid4()
    service = SubjectService(mock_client)

    # Delete a subject that doesn't exist
    from billing_services.utils.exceptions import ExternalServiceException

    with pytest.raises(ExternalServiceException):
        await service.delete_subject(user_id=user_id)

    # Verify the mock was called with the correct arguments
    mock_client.delete_subject_mock.assert_called_once_with(str(user_id))


@pytest.mark.asyncio
async def test_list_subjects_without_entitlement():
    """Test that list_subjects_without_entitlement works correctly."""
    # Create a mock metering client
    mock_client = MockMeteringClient()

    # Create a subject service with the mock client
    service = SubjectService(mock_client)

    # Add subjects to the mock client
    subject1_id = uuid.uuid4()
    subject2_id = uuid.uuid4()
    subject3_id = uuid.uuid4()

    mock_client.upsert_subject(
        [
            {'key': str(subject1_id), 'displayName': 'test1@example.com'},
            {'key': str(subject2_id), 'displayName': 'test2@example.com'},
            {'key': str(subject3_id), 'displayName': 'test3@example.com'},
        ]
    )

    # Add an entitlement for subject2
    mock_client.add_entitlement(str(subject2_id), {'id': 'ent1', 'subject': str(subject2_id)})

    # List subjects without entitlement
    subjects = await service.list_subjects_without_entitlement()

    # Verify the result
    assert len(subjects) == 2
    assert subject1_id in subjects
    assert subject3_id in subjects
    assert subject2_id not in subjects

    # Verify the mocks were called
    mock_client.list_subjects_mock.assert_called_once()
    assert mock_client.list_entitlements_mock.call_count == 3


def test_create_subject_sync():
    """Test that create_subject_sync works correctly."""
    # Create a mock metering client
    mock_client = MockMeteringClient()

    # Create a subject service with the mock client
    user_id = uuid.uuid4()
    user_email = 'test@example.com'
    service = SubjectService(mock_client)

    # Create a subject
    service.create_subject_sync(user_id=user_id, user_email=user_email)

    # Verify the mock was called with the correct arguments
    mock_client.upsert_subject_mock.assert_called_once()
    call_args = mock_client.upsert_subject_mock.call_args[0][0]
    assert len(call_args) == 1
    assert call_args[0]['key'] == str(user_id)
    assert call_args[0]['displayName'] == user_email


def test_delete_subject_sync():
    """Test that delete_subject_sync works correctly."""
    # Create a mock metering client
    mock_client = MockMeteringClient()

    # Create a subject service with the mock client
    user_id = uuid.uuid4()
    service = SubjectService(mock_client)

    # Add a subject to the mock client
    mock_client.upsert_subject([{'key': str(user_id), 'displayName': 'test@example.com'}])

    # Delete the subject
    service.delete_subject_sync(user_id=user_id)

    # Verify the mock was called with the correct arguments
    mock_client.delete_subject_mock.assert_called_once_with(str(user_id))


def test_list_subjects_without_entitlement_sync():
    """Test that list_subjects_without_entitlement_sync works correctly."""
    # Create a mock metering client
    mock_client = MockMeteringClient()

    # Create a subject service with the mock client
    service = SubjectService(mock_client)

    # Add subjects to the mock client
    subject1_id = uuid.uuid4()
    subject2_id = uuid.uuid4()
    subject3_id = uuid.uuid4()

    mock_client.upsert_subject(
        [
            {'key': str(subject1_id), 'displayName': 'test1@example.com'},
            {'key': str(subject2_id), 'displayName': 'test2@example.com'},
            {'key': str(subject3_id), 'displayName': 'test3@example.com'},
        ]
    )

    # Add an entitlement for subject2
    mock_client.add_entitlement(str(subject2_id), {'id': 'ent1', 'subject': str(subject2_id)})

    # List subjects without entitlement
    subjects = service.list_subjects_without_entitlement_sync()

    # Verify the result
    assert len(subjects) == 2
    assert subject1_id in subjects
    assert subject3_id in subjects
    assert subject2_id not in subjects

    # Verify the mocks were called
    mock_client.list_subjects_mock.assert_called_once()
    assert mock_client.list_entitlements_mock.call_count == 3


@pytest.mark.asyncio
async def test_list_subjects():
    """Test that list_subjects works correctly."""
    # Create a mock metering client
    mock_client = MockMeteringClient()

    # Create a subject service with the mock client
    service = SubjectService(mock_client)

    # Add subjects to the mock client
    subject1_id = uuid.uuid4()
    subject2_id = uuid.uuid4()
    subject3_id = uuid.uuid4()

    mock_client.upsert_subject(
        [
            {'key': str(subject1_id), 'displayName': 'test1@example.com'},
            {'key': str(subject2_id), 'displayName': 'test2@example.com'},
            {'key': str(subject3_id), 'displayName': 'test3@example.com'},
        ]
    )

    # List subjects
    subjects = await service.list_subjects()

    # Verify the result
    assert len(subjects) == 3
    subject_keys = [subject['key'] for subject in subjects]
    assert str(subject1_id) in subject_keys
    assert str(subject2_id) in subject_keys
    assert str(subject3_id) in subject_keys

    # Verify the mock was called
    mock_client.list_subjects_mock.assert_called_once()


def test_list_subjects_sync():
    """Test that list_subjects_sync works correctly."""
    # Create a mock metering client
    mock_client = MockMeteringClient()

    # Create a subject service with the mock client
    service = SubjectService(mock_client)

    # Add subjects to the mock client
    subject1_id = uuid.uuid4()
    subject2_id = uuid.uuid4()
    subject3_id = uuid.uuid4()

    mock_client.upsert_subject(
        [
            {'key': str(subject1_id), 'displayName': 'test1@example.com'},
            {'key': str(subject2_id), 'displayName': 'test2@example.com'},
            {'key': str(subject3_id), 'displayName': 'test3@example.com'},
        ]
    )

    # List subjects
    subjects = service.list_subjects_sync()

    # Verify the result
    assert len(subjects) == 3
    subject_keys = [subject['key'] for subject in subjects]
    assert str(subject1_id) in subject_keys
    assert str(subject2_id) in subject_keys
    assert str(subject3_id) in subject_keys

    # Verify the mock was called
    mock_client.list_subjects_mock.assert_called_once()
