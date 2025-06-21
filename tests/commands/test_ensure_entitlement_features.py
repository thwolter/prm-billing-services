"""
Tests for the ensure_entitlement_features command.
"""

import pytest
from uuid import uuid4

from billing_services.commands.ensure_entitlement_features import ensure_features
from billing_services.clients.metering.openmeter_metering_client import OpenMeterMeteringClient
from billing_services.core.config import settings


@pytest.mark.integration
def test_ensure_features_creates_feature_if_not_exists():
    """
    Test that ensure_features creates a feature if it doesn't exist.
    """
    test_feature_key = f"test_feature_{uuid4().hex}"
    client = OpenMeterMeteringClient.from_default()

    # Ensure the feature exists
    ensure_features([test_feature_key])

    # Verify that the feature exists by checking if it's in the list of features
    features = client.list_features()
    assert test_feature_key in features


@pytest.mark.integration
def test_ensure_features_uses_settings_feature_key_by_default():
    """
    Test that ensure_features uses the feature key from settings by default.
    """
    client = OpenMeterMeteringClient.from_default()

    # Ensure the feature exists
    ensure_features()

    # Verify that the feature exists by checking if it's in the list of features
    features = client.list_features()
    assert settings.OPENMETER_FEATURE_KEY in features


@pytest.mark.integration
def test_ensure_features_does_not_recreate_existing_feature():
    """
    Test that ensure_features does not recreate a feature if it already exists.
    """
    test_feature_key = f"test_feature_{uuid4().hex}"
    client = OpenMeterMeteringClient.from_default()

    client.create_feature(test_feature_key)

    # Verify the feature was created
    features_before = client.list_features()
    assert test_feature_key in features_before

    # Ensure the feature exists (this should not recreate it)
    ensure_features([test_feature_key])

    # Verify that the feature still exists
    features_after = client.list_features()
    assert test_feature_key in features_after
