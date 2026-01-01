from django.db import models
from django.utils import timezone
from .utils.encryption import EncryptedCharField, EncryptedTextField
import logging

logger = logging.getLogger(__name__)


class Service(models.Model):
    """Model to store discovered services from Traefik or other sources."""
    
    SERVICE_STATUS_CHOICES = [
        ('up', 'Up'),
        ('down', 'Down'),
        ('unknown', 'Unknown'),
    ]
    
    SERVICE_TYPE_CHOICES = [
        ('docker', 'Docker'),
        ('kubernetes', 'Kubernetes'),
        ('vm', 'Virtual Machine'),
        ('bare_metal', 'Bare Metal'),
        ('external', 'External Service'),
        ('other', 'Other'),
    ]
    
    API_TYPE_CHOICES = [
        ('qbittorrent', 'qBittorrent'),
        ('sonarr', 'Sonarr'),
        ('radarr', 'Radarr'),
        ('custom', 'Custom'),
    ]
    
    PROVIDER_CHOICES = [
        ('traefik', 'Traefik'),
        ('local', 'Local'),
        ('external', 'External'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    url = models.URLField(max_length=500)
    status = models.CharField(max_length=20, choices=SERVICE_STATUS_CHOICES, default='unknown')
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES, default='docker')
    provider = models.CharField(max_length=100, default='traefik', choices=PROVIDER_CHOICES)
    is_manual = models.BooleanField(default=False, help_text='Whether service was added manually or auto-discovered')
    
    # Health and uptime information
    last_checked = models.DateTimeField(null=True, blank=True)
    status_changed_at = models.DateTimeField(null=True, blank=True, help_text='When the status last changed')
    uptime_percentage = models.FloatField(null=True, blank=True)
    response_time = models.IntegerField(null=True, blank=True, help_text='Response time in milliseconds')
    
    # Metadata
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text='Icon class or emoji')
    tags = models.CharField(max_length=500, blank=True, help_text='Comma-separated tags')
    
    # Traefik specific
    traefik_router_name = models.CharField(max_length=255, blank=True)
    traefik_service_name = models.CharField(max_length=255, blank=True)
    
    # API integration
    api_url = models.URLField(max_length=500, blank=True, help_text='API endpoint URL for this service')
    api_key = EncryptedTextField(blank=True, help_text='API key or token for authentication')
    api_username = EncryptedCharField(max_length=255, blank=True, help_text='API username for authentication')
    api_password = EncryptedCharField(max_length=255, blank=True, help_text='API password for authentication')
    api_type = models.CharField(max_length=50, blank=True, choices=API_TYPE_CHOICES, help_text='Type of API integration')
    api_detected = models.BooleanField(default=False, help_text='Whether API was automatically detected')
    api_endpoint = models.CharField(max_length=255, blank=True, help_text='Detected API endpoint path')
    api_last_detected = models.DateTimeField(null=True, blank=True, help_text='When API was last detected/verified')
    api_detection_attempts = models.IntegerField(default=0, help_text='Number of failed API detection attempts')
    api_next_check = models.DateTimeField(null=True, blank=True, help_text='When to retry API detection next')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    def check_health(self):
        """Check the health status of the service."""
        import requests
        from datetime import datetime
        import urllib3
        
        # Suppress only the single InsecureRequestWarning from urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        old_status = self.status
        
        def is_service_up(status_code):
            """
            Determine if service is up based on status code.
            Many services return 3xx, 401, or 403 when up but requiring auth/redirect.
            """
            # 2xx - Success
            if 200 <= status_code < 300:
                return True
            # 3xx - Redirect (service is responding)
            if 300 <= status_code < 400:
                return True
            # 401 - Unauthorized (service is up, needs auth)
            if status_code == 401:
                return True
            # 403 - Forbidden (service is up, access denied - common for dashboards)
            if status_code == 403:
                return True
            # 405 - Method Not Allowed (service is up, just doesn't like GET)
            if status_code == 405:
                return True
            # Everything else (404, 5xx) is considered down
            return False
        
        try:
            start_time = datetime.now()
            logger.info(f"Checking health for {self.name} at {self.url}")
            
            # Set a reasonable timeout and allow redirects
            response = requests.get(
                self.url, 
                timeout=5, 
                allow_redirects=True, 
                verify=True,  # Use SSL verification for valid certificates
                headers={'User-Agent': 'HomeLab-Dashboard/1.0'}
            )
            end_time = datetime.now()
            
            self.response_time = int((end_time - start_time).total_seconds() * 1000)
            
            if is_service_up(response.status_code):
                self.status = 'up'
                logger.info(f"✓ {self.name}: UP (status={response.status_code}, time={self.response_time}ms)")
            else:
                self.status = 'down'
                logger.warning(f"✗ {self.name}: DOWN (status={response.status_code})")
                
        except requests.exceptions.SSLError as e:
            # SSL error - might be self-signed cert, try without verification
            logger.warning(f"SSL error for {self.name}, retrying without verification: {e}")
            try:
                start_time = datetime.now()
                response = requests.get(
                    self.url, 
                    timeout=5, 
                    allow_redirects=True, 
                    verify=False,
                    headers={'User-Agent': 'HomeLab-Dashboard/1.0'}
                )
                end_time = datetime.now()
                
                self.response_time = int((end_time - start_time).total_seconds() * 1000)
                
                if is_service_up(response.status_code):
                    self.status = 'up'
                    logger.info(f"✓ {self.name}: UP (no SSL verify, status={response.status_code}, time={self.response_time}ms)")
                else:
                    self.status = 'down'
                    logger.warning(f"✗ {self.name}: DOWN (status={response.status_code})")
            except Exception as e2:
                logger.error(f"✗ {self.name}: FAILED even without SSL verification - {type(e2).__name__}: {e2}")
                self.status = 'down'
                self.response_time = None
                
        except requests.exceptions.Timeout as e:
            logger.error(f"✗ {self.name}: TIMEOUT after 5s - {self.url}")
            self.status = 'down'
            self.response_time = None
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"✗ {self.name}: CONNECTION ERROR - {type(e).__name__}: {str(e)[:100]}")
            
            # If HTTPS failed, try HTTP as fallback
            if self.url.startswith('https://'):
                http_url = self.url.replace('https://', 'http://', 1)
                logger.info(f"↻ {self.name}: Trying HTTP fallback - {http_url}")
                try:
                    start_time = datetime.now()
                    response = requests.get(
                        http_url,
                        timeout=5,
                        allow_redirects=True,
                        verify=False,
                        headers={'User-Agent': 'HomeLab-Dashboard/1.0'}
                    )
                    end_time = datetime.now()
                    
                    self.response_time = int((end_time - start_time).total_seconds() * 1000)
                    
                    if is_service_up(response.status_code):
                        self.status = 'up'
                        self.url = http_url  # Update to HTTP
                        logger.info(f"✓ {self.name}: UP via HTTP fallback (status={response.status_code}, time={self.response_time}ms)")
                        logger.info(f"📝 Updated {self.name} URL from HTTPS to HTTP")
                    else:
                        self.status = 'down'
                        self.response_time = None
                        logger.warning(f"✗ {self.name}: DOWN on both HTTPS and HTTP")
                except Exception as e2:
                    logger.error(f"✗ {self.name}: HTTP fallback also failed - {type(e2).__name__}")
                    self.status = 'down'
                    self.response_time = None
            else:
                self.status = 'down'
                self.response_time = None
            
        except Exception as e:
            logger.error(f"✗ {self.name}: UNEXPECTED ERROR - {type(e).__name__}: {str(e)[:100]}")
            self.status = 'down'
            self.response_time = None
        
        # Track status changes
        if old_status != self.status:
            self.status_changed_at = timezone.now()
            logger.info(f"Status changed for {self.name}: {old_status} → {self.status}")
        
        self.last_checked = timezone.now()
        self.save()
        
        return self.status


class HealthCheck(models.Model):
    """Model to track historical health checks."""
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='health_checks')
    status = models.CharField(max_length=20)
    response_time = models.IntegerField(null=True, blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"{self.service.name} - {self.status} at {self.checked_at}"


class GrafanaPanel(models.Model):
    """Model to store Grafana panel/dashboard configurations for embedding."""
    
    REFRESH_CHOICES = [
        ('5s', '5 seconds'),
        ('10s', '10 seconds'),
        ('30s', '30 seconds'),
        ('1m', '1 minute'),
        ('5m', '5 minutes'),
        ('15m', '15 minutes'),
        ('30m', '30 minutes'),
        ('1h', '1 hour'),
        ('2h', '2 hours'),
        ('1d', '1 day'),
    ]
    
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
    ]
    
    # Basic configuration
    title = models.CharField(max_length=255, help_text='Display title for the panel')
    description = models.TextField(blank=True, help_text='Optional description of what this panel shows')
    
    # Grafana connection details
    grafana_url = models.URLField(max_length=500, help_text='Base URL of your Grafana instance (e.g., https://grafana.example.com)')
    dashboard_uid = models.CharField(max_length=255, help_text='Dashboard UID from Grafana (found in dashboard URL)')
    panel_id = models.IntegerField(help_text='Panel ID to embed (found in panel share link)')
    
    # Optional: Link to specific service
    service = models.ForeignKey(
        Service, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='grafana_panels',
        help_text='Optionally link this panel to a specific service'
    )
    
    # Display settings
    width = models.IntegerField(default=450, help_text='Width in pixels for the embedded panel')
    height = models.IntegerField(default=200, help_text='Height in pixels for the embedded panel')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='dark', help_text='Grafana panel theme')
    refresh = models.CharField(max_length=10, choices=REFRESH_CHOICES, default='1m', help_text='Auto-refresh interval')
    
    # Time range settings
    from_time = models.CharField(max_length=50, default='now-6h', help_text='Start time (e.g., now-6h, now-24h, now-7d)')
    to_time = models.CharField(max_length=50, default='now', help_text='End time (usually "now")')
    
    # Display control
    is_active = models.BooleanField(default=True, help_text='Show this panel on the dashboard')
    display_order = models.IntegerField(default=0, help_text='Order in which panels are displayed (lower numbers first)')
    
    # Optional authentication
    api_key = EncryptedTextField(blank=True, help_text='Grafana API key if authentication is required')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'title']
        verbose_name = 'Grafana Panel'
        verbose_name_plural = 'Grafana Panels'
    
    def __str__(self):
        return self.title
    
    def get_embed_url(self):
        """Generate the iframe embed URL for this Grafana panel."""
        # Base URL format: {grafana_url}/d-solo/{dashboard_uid}
        base_url = self.grafana_url.rstrip('/')
        embed_url = f"{base_url}/d-solo/{self.dashboard_uid}"
        
        # Add parameters
        params = [
            f"orgId=1",
            f"panelId={self.panel_id}",
            f"theme={self.theme}",
            f"from={self.from_time}",
            f"to={self.to_time}",
            f"refresh={self.refresh}",
        ]
        
        return f"{embed_url}?{'&'.join(params)}"
    
    def get_dashboard_url(self):
        """Get the full dashboard URL (not embedded) for reference."""
        base_url = self.grafana_url.rstrip('/')
        return f"{base_url}/d/{self.dashboard_uid}"
