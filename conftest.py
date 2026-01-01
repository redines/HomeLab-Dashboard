"""Pytest configuration and fixtures for testing."""

import pytest
from django.conf import settings
from django.test import Client
from dashboard.models import Service, HealthCheck, GrafanaPanel
from django.utils import timezone
import os


# Configure Django settings for tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homelab_dashboard.settings')


@pytest.fixture(scope='session')
def django_db_setup():
    """Setup the test database."""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': False,
    }


@pytest.fixture
def api_client():
    """Fixture for Django test client."""
    return Client()


@pytest.fixture
def sample_service(db):
    """Create a sample service for testing."""
    return Service.objects.create(
        name='Test Service',
        url='https://test.local',
        status='up',
        service_type='docker',
        provider='traefik',
        is_manual=False,
        description='Test service for unit testing',
        icon='🧪',
        tags='test, sample'
    )


@pytest.fixture
def sample_services(db):
    """Create multiple sample services for testing."""
    services = []
    for i in range(5):
        service = Service.objects.create(
            name=f'Service {i}',
            url=f'https://service{i}.local',
            status='up' if i % 2 == 0 else 'down',
            service_type='docker',
            provider='traefik',
            is_manual=False,
            description=f'Test service {i}',
            icon='🔧',
            tags=f'test{i}'
        )
        services.append(service)
    return services


@pytest.fixture
def manual_service(db):
    """Create a manually added service for testing."""
    return Service.objects.create(
        name='Manual Service',
        url='https://manual.local',
        status='unknown',
        service_type='external',
        provider='local',
        is_manual=True,
        description='Manually added service',
    )


@pytest.fixture
def service_with_api(db):
    """Create a service with API integration for testing."""
    return Service.objects.create(
        name='API Service',
        url='https://api-service.local',
        status='up',
        service_type='docker',
        provider='traefik',
        api_url='https://api-service.local/api',
        api_key='test_api_key_123',
        api_username='testuser',
        api_password='testpass',
        api_type='qbittorrent',
        api_detected=True,
        api_endpoint='/api/v2',
        api_last_detected=timezone.now()
    )


@pytest.fixture
def health_check(db, sample_service):
    """Create a health check record for testing."""
    return HealthCheck.objects.create(
        service=sample_service,
        status='up',
        response_time=150,
        checked_at=timezone.now()
    )


@pytest.fixture
def grafana_panel(db):
    """Create a Grafana panel for testing."""
    return GrafanaPanel.objects.create(
        title='Test Panel',
        grafana_url='https://grafana.local',
        dashboard_uid='test-dashboard',
        panel_id='1',
        width=12,
        height=8,
        refresh='5m',
        display_order=1,
        is_active=True,
        theme='dark'
    )


@pytest.fixture
def mock_requests_success(monkeypatch):
    """Mock requests.get to return successful response."""
    class MockResponse:
        status_code = 200
        text = 'OK'
        
        def json(self):
            return {'status': 'ok'}
    
    def mock_get(*args, **kwargs):
        return MockResponse()
    
    monkeypatch.setattr('requests.get', mock_get)


@pytest.fixture
def mock_requests_failure(monkeypatch):
    """Mock requests.get to simulate connection failure."""
    import requests
    
    def mock_get(*args, **kwargs):
        raise requests.exceptions.ConnectionError('Connection failed')
    
    monkeypatch.setattr('requests.get', mock_get)


@pytest.fixture
def mock_requests_timeout(monkeypatch):
    """Mock requests.get to simulate timeout."""
    import requests
    
    def mock_get(*args, **kwargs):
        raise requests.exceptions.Timeout('Request timed out')
    
    monkeypatch.setattr('requests.get', mock_get)
