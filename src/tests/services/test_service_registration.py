from fastapi.routing import APIRoute

from src.main import app
from src.services import discover_services


def test_services_registered():
    service_paths = {f'/api{svc.route_path}' for svc in discover_services()}
    registered = {route.path for route in app.router.routes if isinstance(route, APIRoute)}
    for path in service_paths:
        assert path in registered
