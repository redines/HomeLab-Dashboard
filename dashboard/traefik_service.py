"""
Traefik API integration service.
Handles communication with Traefik API to discover services and routers.
"""

import requests
from requests.auth import HTTPBasicAuth
from typing import List, Dict, Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class TraefikService:
    """Service to interact with Traefik API."""
    
    def __init__(self):
        self.api_url = settings.TRAEFIK_API_URL
        self.username = settings.TRAEFIK_API_USERNAME
        self.password = settings.TRAEFIK_API_PASSWORD
        self.auth = None
        
        if self.username and self.password:
            self.auth = HTTPBasicAuth(self.username, self.password)
    
    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """Make a request to Traefik API."""
        try:
            url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error making request to Traefik API: {e}")
            return None
    
    def get_routers(self) -> List[Dict]:
        """Get all HTTP routers from Traefik."""
        data = self._make_request('http/routers')
        if data:
            return data if isinstance(data, list) else []
        return []
    
    def get_services(self) -> List[Dict]:
        """Get all HTTP services from Traefik."""
        data = self._make_request('http/services')
        if data:
            return data if isinstance(data, list) else []
        return []
    
    def discover_services(self) -> List[Dict]:
        """
        Discover all services from Traefik.
        Returns a list of service dictionaries with name, url, and metadata.
        """
        routers = self.get_routers()
        discovered_services = []
        
        for router in routers:
            try:
                # Extract router information
                router_name = router.get('name', '')
                router_rule = router.get('rule', '')
                router_status = router.get('status', 'unknown')
                service_name = router.get('service', '')
                
                # Skip internal Traefik services
                if '@internal' in router_name or '@internal' in service_name:
                    continue
                
                # Parse the rule to extract the host/domain
                url = self._extract_url_from_rule(router_rule)
                
                if url:
                    service_info = {
                        'name': self._clean_service_name(router_name),
                        'url': url,
                        'status': 'up' if router_status == 'enabled' else 'unknown',
                        'service_type': 'docker',
                        'provider': 'traefik',
                        'traefik_router_name': router_name,
                        'traefik_service_name': service_name,
                        'tags': self._extract_tags(router),
                    }
                    discovered_services.append(service_info)
            except Exception as e:
                logger.error(f"Error processing router {router.get('name', 'unknown')}: {e}")
        
        return discovered_services
    
    def _extract_url_from_rule(self, rule: str) -> Optional[str]:
        """
        Extract URL from Traefik rule.
        Example rules:
        - Host(`example.com`)
        - Host(`example.com`) && PathPrefix(`/api`)
        - (Host(`example.com`) || Host(`www.example.com`))
        """
        if not rule:
            return None
        
        # Simple extraction for Host() rules
        import re
        
        # Match Host(`domain`) or Host("domain")
        host_pattern = r'Host\([`"]([^`"]+)[`"]\)'
        matches = re.findall(host_pattern, rule)
        
        if matches:
            # Use the first host found
            host = matches[0]
            
            # Check if there's a PathPrefix
            path_pattern = r'PathPrefix\([`"]([^`"]+)[`"]\)'
            path_matches = re.findall(path_pattern, rule)
            
            # Determine protocol (assume HTTPS if available, fallback to HTTP)
            protocol = 'https' if self._has_tls(rule) else 'http'
            
            path = path_matches[0] if path_matches else ''
            return f"{protocol}://{host}{path}"
        
        return None
    
    def _has_tls(self, rule: str) -> bool:
        """Check if the rule or router has TLS enabled."""
        # This is a simple heuristic; in practice, you'd check the router's TLS configuration
        return 'tls' in rule.lower() or 'https' in rule.lower()
    
    def _clean_service_name(self, name: str) -> str:
        """Clean service name for display."""
        # Remove provider suffix (e.g., @docker, @kubernetes)
        name = name.split('@')[0]
        
        # Remove common prefixes/suffixes
        name = name.replace('-', ' ').replace('_', ' ')
        
        # Capitalize words
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name
    
    def _extract_tags(self, router: Dict) -> str:
        """Extract tags from router metadata."""
        tags = []
        
        # Extract provider
        provider = router.get('provider', '')
        if provider:
            tags.append(provider)
        
        # Extract from name
        name = router.get('name', '')
        if 'docker' in name.lower():
            tags.append('docker')
        
        return ','.join(tags)
    
    def test_connection(self) -> bool:
        """Test connection to Traefik API."""
        try:
            response = self._make_request('overview')
            return response is not None
        except Exception as e:
            logger.error(f"Failed to connect to Traefik API: {e}")
            return False


def sync_traefik_services():
    """
    Synchronize services from Traefik API to the database.
    This function can be called periodically or manually.
    """
    from dashboard.models import Service
    from django.utils import timezone
    
    traefik = TraefikService()
    
    # Test connection first
    if not traefik.test_connection():
        logger.warning("Cannot connect to Traefik API. Skipping sync.")
        return 0
    
    discovered = traefik.discover_services()
    synced_count = 0
    
    for service_data in discovered:
        try:
            # Check if service exists and if status is changing
            existing_service = Service.objects.filter(
                traefik_router_name=service_data['traefik_router_name']
            ).first()
            
            status_changed = False
            if existing_service and existing_service.status != service_data['status']:
                status_changed = True
                logger.info(
                    f"Status changed for {service_data['name']}: "
                    f"{existing_service.status} -> {service_data['status']}"
                )
            
            # Prepare defaults
            defaults = {
                'name': service_data['name'],
                'url': service_data['url'],
                'status': service_data['status'],
                'service_type': service_data['service_type'],
                'provider': service_data['provider'],
                'traefik_service_name': service_data['traefik_service_name'],
                'tags': service_data['tags'],
                'last_checked': timezone.now(),
            }
            
            # Update status_changed_at only if status changed or it's a new service
            if not existing_service or status_changed:
                defaults['status_changed_at'] = timezone.now()
            
            service, created = Service.objects.update_or_create(
                traefik_router_name=service_data['traefik_router_name'],
                defaults=defaults
            )
            synced_count += 1
            
            if created:
                logger.info(f"Created new service: {service.name}")
            else:
                logger.info(f"Updated service: {service.name}")
        except Exception as e:
            logger.error(f"Error syncing service {service_data.get('name')}: {e}")
    
    return synced_count
