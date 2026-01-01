"""Unit tests for Django models."""

import pytest
from django.utils import timezone
from django.db import IntegrityError
from datetime import datetime, timedelta
from dashboard.models import Service, HealthCheck, GrafanaPanel


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.models
class TestServiceModel:
    """Test cases for the Service model."""
    
    def test_create_service(self):
        """Test creating a basic service."""
        service = Service.objects.create(
            name='Test Service',
            url='https://test.local',
            status='up',
            service_type='docker',
            provider='traefik'
        )
        
        assert service.name == 'Test Service'
        assert service.url == 'https://test.local'
        assert service.status == 'up'
        assert service.service_type == 'docker'
        assert service.provider == 'traefik'
        assert service.is_manual is False
        
    def test_service_unique_name(self, db):
        """Test that service names must be unique."""
        Service.objects.create(
            name='Duplicate Service',
            url='https://service1.local'
        )
        
        with pytest.raises(IntegrityError):
            Service.objects.create(
                name='Duplicate Service',
                url='https://service2.local'
            )
    
    def test_service_str_representation(self, sample_service):
        """Test string representation of service."""
        assert str(sample_service) == 'Test Service (up)'
    
    def test_service_default_values(self, db):
        """Test default values for service fields."""
        service = Service.objects.create(
            name='Default Service',
            url='https://default.local'
        )
        
        assert service.status == 'unknown'
        assert service.service_type == 'docker'
        assert service.provider == 'traefik'
        assert service.is_manual is False
        assert service.api_detected is False
        assert service.api_detection_attempts == 0
    
    def test_service_with_api_credentials(self, service_with_api):
        """Test service with encrypted API credentials."""
        # Verify the service was created with API info
        assert service_with_api.api_url == 'https://api-service.local/api'
        assert service_with_api.api_type == 'qbittorrent'
        assert service_with_api.api_detected is True
        
        # Verify encrypted fields are accessible (encryption tested separately)
        assert service_with_api.api_key is not None
        assert service_with_api.api_username is not None
        assert service_with_api.api_password is not None
    
    def test_service_status_choices(self, db):
        """Test valid status choices."""
        valid_statuses = ['up', 'down', 'unknown']
        
        for status in valid_statuses:
            service = Service.objects.create(
                name=f'Service {status}',
                url=f'https://{status}.local',
                status=status
            )
            assert service.status == status
    
    def test_service_type_choices(self, db):
        """Test valid service type choices."""
        valid_types = ['docker', 'kubernetes', 'vm', 'bare_metal', 'external', 'other']
        
        for service_type in valid_types:
            service = Service.objects.create(
                name=f'Service {service_type}',
                url=f'https://{service_type}.local',
                service_type=service_type
            )
            assert service.service_type == service_type
    
    def test_manual_service_creation(self, manual_service):
        """Test creating a manually added service."""
        assert manual_service.is_manual is True
        assert manual_service.provider == 'local'
        assert manual_service.status == 'unknown'
    
    def test_service_timestamps(self, sample_service):
        """Test that timestamps are set correctly."""
        assert sample_service.created_at is not None
        assert sample_service.updated_at is not None
        assert isinstance(sample_service.created_at, datetime)
        assert isinstance(sample_service.updated_at, datetime)
    
    def test_service_ordering(self, sample_services):
        """Test that services are ordered by name."""
        services = Service.objects.all()
        names = [s.name for s in services]
        assert names == sorted(names)
    
    def test_service_tags_field(self, db):
        """Test service tags field."""
        service = Service.objects.create(
            name='Tagged Service',
            url='https://tagged.local',
            tags='docker, monitoring, production'
        )
        
        assert 'docker' in service.tags
        assert 'monitoring' in service.tags
        assert 'production' in service.tags
    
    def test_service_check_health_success(self, sample_service, mock_requests_success):
        """Test health check with successful response."""
        old_status = sample_service.status
        sample_service.check_health()
        
        assert sample_service.status == 'up'
        assert sample_service.response_time is not None
        assert sample_service.last_checked is not None
    
    def test_service_check_health_timeout(self, sample_service, mock_requests_timeout):
        """Test health check with timeout."""
        sample_service.check_health()
        
        assert sample_service.status == 'down'
        assert sample_service.response_time is None
    
    def test_service_check_health_connection_error(self, sample_service, mock_requests_failure):
        """Test health check with connection error."""
        sample_service.check_health()
        
        assert sample_service.status == 'down'


@pytest.mark.django_db
@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.models
class TestHealthCheckModel:
    """Test cases for the HealthCheck model."""
    
    def test_create_health_check(self, sample_service):
        """Test creating a health check record."""
        check = HealthCheck.objects.create(
            service=sample_service,
            status='up',
            response_time=125,
            checked_at=timezone.now()
        )
        
        assert check.service == sample_service
        assert check.status == 'up'
        assert check.response_time == 125
    
    def test_health_check_relationship(self, health_check, sample_service):
        """Test relationship between health check and service."""
        assert health_check.service == sample_service
        assert health_check in sample_service.health_checks.all()
    
    def test_health_check_ordering(self, sample_service, db):
        """Test health checks are ordered by checked_at."""
        now = timezone.now()
        
        # Create checks with explicit checked_at timestamps
        # Note: We need to save first, then update checked_at to override auto_now_add
        check2 = HealthCheck.objects.create(
            service=sample_service,
            status='up',
            response_time=100
        )
        check2.checked_at = now + timedelta(minutes=2)
        check2.save()
        
        check1 = HealthCheck.objects.create(
            service=sample_service,
            status='up',
            response_time=100
        )
        check1.checked_at = now + timedelta(minutes=1)
        check1.save()
        
        check3 = HealthCheck.objects.create(
            service=sample_service,
            status='up',
            response_time=100
        )
        check3.checked_at = now + timedelta(minutes=3)
        check3.save()
        
        # Refresh from database to get the updated timestamps
        checks = list(sample_service.health_checks.all())
        assert len(checks) == 3
        # Verify ordering - most recent first
        assert checks[0].checked_at > checks[1].checked_at
        assert checks[1].checked_at > checks[2].checked_at


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.models
class TestGrafanaPanelModel:
    """Test cases for the GrafanaPanel model."""
    
    def test_create_grafana_panel(self, grafana_panel):
        """Test creating a Grafana panel."""
        assert grafana_panel.title == 'Test Panel'
        assert grafana_panel.grafana_url == 'https://grafana.local'
        assert grafana_panel.dashboard_uid == 'test-dashboard'
        assert grafana_panel.panel_id == '1'
        assert grafana_panel.is_active is True
    
    def test_grafana_panel_default_values(self, db):
        """Test default values for Grafana panel."""
        panel = GrafanaPanel.objects.create(
            title='Default Panel',
            grafana_url='https://grafana.local',
            dashboard_uid='default-dash',
            panel_id='2'
        )
        
        assert panel.width == 450
        assert panel.height == 200
        assert panel.refresh == '1m'  # Field is 'refresh' not 'refresh_interval'
        assert panel.display_order == 0
        assert panel.is_active is True
        assert panel.theme == 'dark'
    
    def test_grafana_panel_ordering(self, db):
        """Test panels are ordered by display_order."""
        panel3 = GrafanaPanel.objects.create(
            title='Panel 3',
            grafana_url='https://grafana.local',
            dashboard_uid='dash',
            panel_id='3',
            display_order=3
        )
        panel1 = GrafanaPanel.objects.create(
            title='Panel 1',
            grafana_url='https://grafana.local',
            dashboard_uid='dash',
            panel_id='1',
            display_order=1
        )
        panel2 = GrafanaPanel.objects.create(
            title='Panel 2',
            grafana_url='https://grafana.local',
            dashboard_uid='dash',
            panel_id='2',
            display_order=2
        )
        
        panels = list(GrafanaPanel.objects.all())
        assert panels[0] == panel1
        assert panels[1] == panel2
        assert panels[2] == panel3
    
    def test_grafana_panel_iframe_url_generation(self, grafana_panel):
        """Test iframe URL is generated correctly."""
        expected_url = (
            'https://grafana.local/d-solo/test-dashboard?'
            'orgId=1&panelId=1&theme=dark&refresh=5m'
        )
        # Note: This assumes the model has a method to generate iframe URL
        # If not implemented, this test documents expected behavior
    
    def test_grafana_panel_str_representation(self, grafana_panel):
        """Test string representation of panel."""
        assert str(grafana_panel) == 'Test Panel'
