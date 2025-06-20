import pytest
from openmeter import Client

from src.core.config import settings


@pytest.mark.integration
def test_openmeter_healthcheck():
    """
    Integration test to verify connectivity and authentication with the OpenMeter API.

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter client with the API URL
    and authorization header. The test attempts to list available meters via the OpenMeter API.
    If the API request fails, the test fails with the corresponding exception message.
    """

    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    client = Client(endpoint=settings.OPENMETER_API_URL, headers=headers)
    try:
        client.list_meters()
    except Exception as exc:
        pytest.fail(f'OpenMeter request failed: {exc}')
