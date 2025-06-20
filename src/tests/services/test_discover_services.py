from unittest import mock

import pytest

from src.services import discover_services
from src.services.base_service import BaseService
from src.utils import logutils

logutils.logging.basicConfig(level=logutils.logging.DEBUG)


class TestDiscoverServices:
    """Tests for the discover_services function."""

    def test_discover_services_normal(self):
        """Test that discover_services finds service classes in normal conditions."""
        # Call the function
        services = discover_services()

        # Verify that services were found
        assert len(services) > 0, 'No services were discovered'

        # Verify that all discovered services have a route_path attribute
        for service in services:
            assert hasattr(service, 'route_path'), (
                f'Service {service.__name__} has no route_path attribute'
            )
            assert service.route_path, f'Service {service.__name__} has empty route_path'

    def test_discover_services_attributes(self):
        """Test that discovered services have the required attributes."""
        services = discover_services()

        # Verify that all services have the required attributes
        for service in services:
            assert hasattr(service, 'route_path'), (
                f'Service {service.__name__} has no route_path attribute'
            )
            assert hasattr(service, 'chain_fn'), (
                f'Service {service.__name__} has no chain_fn attribute'
            )
            assert hasattr(service, 'QueryModel'), (
                f'Service {service.__name__} has no QueryModel attribute'
            )
            assert hasattr(service, 'ResultModel'), (
                f'Service {service.__name__} has no ResultModel attribute'
            )

    def test_discover_services_inheritance(self):
        """Test that discovered services inherit from BaseService."""
        services = discover_services()

        # Verify that all services inherit from BaseService
        for service in services:
            assert issubclass(service, BaseService), (
                f'Service {service.__name__} does not inherit from BaseService'
            )

    @mock.patch('pkgutil.walk_packages')
    def test_discover_services_no_modules(self, mock_walk_packages):
        """Test that discover_services handles the case where no modules are found."""
        # Mock pkgutil.walk_packages to return an empty list
        mock_walk_packages.return_value = []

        # Call the function
        services = discover_services()

        # Verify that no services were found
        assert len(services) == 0, 'Services were discovered when none should be'

    @mock.patch('importlib.import_module')
    def test_discover_services_import_error(self, mock_import_module):
        """Test that discover_services handles ImportError."""
        # Mock importlib.import_module to raise ImportError
        mock_import_module.side_effect = ImportError('Test import error')

        # Call the function - it should not raise an exception
        services = discover_services()

        # Verify that no services were found
        assert len(services) == 0, 'Services were discovered when an import error occurred'

    @mock.patch('pkgutil.walk_packages')
    def test_discover_services_exception(self, mock_walk_packages):
        """Test that discover_services handles general exceptions."""
        # Mock pkgutil.walk_packages to raise an exception
        mock_walk_packages.side_effect = Exception('Test exception')

        # Call the function - it should not raise an exception
        services = discover_services()

        # Verify that no services were found
        assert len(services) == 0, 'Services were discovered when an exception occurred'

    @mock.patch('src.services.importlib.import_module')
    def test_discover_services_module_import_error(self, mock_import_module):
        """Test that discover_services handles ImportError when importing a module."""
        # First call to import_module('src') should succeed
        # Subsequent calls should fail with ImportError
        src_module = mock.MagicMock()
        src_module.__path__ = ['mock_path']

        def side_effect(name):
            if name == 'src':
                return src_module
            raise ImportError(f'Test import error for {name}')

        mock_import_module.side_effect = side_effect

        # Mock pkgutil.walk_packages to return a module name
        with mock.patch(
            'src.services.pkgutil.walk_packages', return_value=[(None, 'src.services', False)]
        ):
            # Call the function
            services = discover_services()

            # Verify that no services were found
            assert len(services) == 0, (
                'Services were discovered when a module import error occurred'
            )

    def test_discover_services_specific_services(self):
        """Test that discover_services finds specific known services."""
        services = discover_services()

        # Get the names of all discovered services
        service_names = [service.__name__ for service in services]

        # Verify that specific known services are discovered
        expected_services = [
            'RiskDefinitionCheckService',
            'RiskIdentificationService',
            'RiskDriverService',
            'RiskAssessmentService',
            'RiskMitigationService',
            'CreateCategoriesService',
        ]

        for expected_service in expected_services:
            assert expected_service in service_names, (
                f'Expected service {expected_service} was not discovered'
            )


if __name__ == '__main__':
    pytest.main(['-v', 'test_discover_services.py'])
