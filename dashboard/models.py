from django.db import models
from django.utils import timezone


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
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    url = models.URLField(max_length=500)
    status = models.CharField(max_length=20, choices=SERVICE_STATUS_CHOICES, default='unknown')
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES, default='docker')
    provider = models.CharField(max_length=100, default='traefik')
    
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
        
        try:
            start_time = datetime.now()
            response = requests.get(self.url, timeout=5, allow_redirects=True)
            end_time = datetime.now()
            
            self.response_time = int((end_time - start_time).total_seconds() * 1000)
            
            if response.status_code < 400:
                self.status = 'up'
            else:
                self.status = 'down'
        except Exception:
            self.status = 'down'
            self.response_time = None
        
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
