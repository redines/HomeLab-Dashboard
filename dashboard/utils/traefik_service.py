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


def is_traefik_configured() -> bool:
    """Check if Traefik API URL is configured."""
    api_url = getattr(settings, 'TRAEFIK_API_URL', None)
    if not api_url:
        return False
    # Check if it's not the default placeholder value or empty
    if api_url in ['http://traefik:8080/api', '']:
        logger.debug("Traefik API URL is set to default/empty value")
        return False
    return True


def check_traefik_availability() -> bool:
    """Test if Traefik API is accessible and responding."""
    if not is_traefik_configured():
        logger.debug("Traefik is not configured, skipping availability check")
        return False
    
    try:
        api_url = settings.TRAEFIK_API_URL
        username = getattr(settings, 'TRAEFIK_API_USERNAME', '')
        password = getattr(settings, 'TRAEFIK_API_PASSWORD', '')
        
        auth = None
        if username and password:
            auth = HTTPBasicAuth(username, password)
        
        response = requests.get(f"{api_url.rstrip('/')}/version", auth=auth, timeout=5)
        response.raise_for_status()
        logger.info("✓ Traefik API is available and responding")
        return True
    except Exception as e:
        logger.info(f"Traefik API is not available: {e}")
        return False


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
    
    def get_router_details(self, router_name: str) -> Optional[Dict]:
        """Get detailed information about a specific router."""
        return self._make_request(f'http/routers/{router_name}')
    
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
                
                # Check if router has TLS configuration
                has_tls = router.get('tls') is not None
                
                # Parse the rule to extract the host/domain
                url = self._extract_url_from_rule(router_rule, has_tls)
                
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
    
    def _extract_url_from_rule(self, rule: str, has_tls: bool = False) -> Optional[str]:
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
            
            # Use HTTPS if TLS is configured, otherwise HTTP
            protocol = 'https' if has_tls else 'http'
            
            path = path_matches[0] if path_matches else ''
            return f"{protocol}://{host}{path}"
        
        return None
    
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


def sync_traefik_services(force_api_detection=False):
    """
    Synchronize services from Traefik API to the database.
    Automatically detects if Traefik is available and skips if not.
    
    Args:
        force_api_detection: If True, re-detect APIs even if already detected
        
    Returns:
        int: Number of services synced, or 0 if Traefik is not available
    """
    from dashboard.models import Service
    from dashboard.utils.api_detector import APIDetector
    from django.utils import timezone
    from datetime import timedelta
    
    # Automatically check if Traefik is available
    if not check_traefik_availability():
        logger.debug("Traefik is not available. Using manual service management mode.")
        return 0
    
    traefik = TraefikService()
    
    # Test connection first
    if not traefik.test_connection():
        logger.info("Cannot connect to Traefik API. Using manual service management mode.")
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
            
            # Detect API availability
            # Skip if already detected recently (within 7 days) unless forced or never detected
            should_detect = force_api_detection or not existing_service or not existing_service.api_detected
            
            # Check throttling: skip detection if checked 5+ times without success and not enough time passed
            if existing_service and existing_service.api_detection_attempts >= 5 and not force_api_detection:
                # If next_check time is set and we haven't reached it yet, skip detection
                if existing_service.api_next_check and timezone.now() < existing_service.api_next_check:
                    should_detect = False
                    logger.debug(
                        f"Skipping API detection for {service_data['name']} "
                        f"(checked {existing_service.api_detection_attempts} times, "
                        f"next check at {existing_service.api_next_check.strftime('%H:%M:%S')})"
                    )
                else:
                    # Time to retry - allow detection
                    logger.info(
                        f"Retrying API detection for {service_data['name']} "
                        f"(previous attempts: {existing_service.api_detection_attempts})"
                    )
            
            # Also re-detect if it's been more than 7 days since last detection
            if existing_service and existing_service.api_last_detected:
                days_since_detection = (timezone.now() - existing_service.api_last_detected).days
                if days_since_detection > 7:
                    should_detect = True
                    logger.info(f"Re-detecting API for {service_data['name']} (last detected {days_since_detection} days ago)")
            
            api_detected = False
            detected_api_type = None
            detected_endpoint = None
            
            # If service has manual credentials, mark as API available but skip probing
            if existing_service and existing_service.api_username:
                api_detected = True
                detected_api_type = existing_service.api_type or service_data['name'].lower().replace(' ', '')
                detected_endpoint = existing_service.api_endpoint
                logger.debug(f"Service {service_data['name']} has manual API configuration")
            elif should_detect:
                # Probe for API
                try:
                    has_api, api_type, api_endpoint = APIDetector.detect_api(
                        service_data['name'],
                        service_data['url'],
                        labels=None  # Could extract from Traefik if available
                    )
                    
                    if has_api:
                        api_detected = True
                        detected_api_type = api_type
                        detected_endpoint = api_endpoint
                        logger.info(f"🔍 API detected for {service_data['name']}: {api_type}")
                        # Reset detection attempts on success
                        if existing_service:
                            existing_service.api_detection_attempts = 0
                            existing_service.api_next_check = None
                    else:
                        # Increment failed attempts
                        if existing_service:
                            existing_service.api_detection_attempts = (existing_service.api_detection_attempts or 0) + 1
                            # After 5 failed attempts, throttle to check every 5 minutes
                            if existing_service.api_detection_attempts >= 5:
                                from datetime import timedelta
                                existing_service.api_next_check = timezone.now() + timedelta(minutes=5)
                                logger.info(
                                    f"⏱️  API not found for {service_data['name']} after "
                                    f"{existing_service.api_detection_attempts} attempts. "
                                    f"Next check at {existing_service.api_next_check.strftime('%H:%M:%S')}"
                                )
                except Exception as e:
                    logger.debug(f"API detection failed for {service_data['name']}: {e}")
                    # Also increment attempts on error
                    if existing_service:
                        existing_service.api_detection_attempts = (existing_service.api_detection_attempts or 0) + 1
                        if existing_service.api_detection_attempts >= 5:
                            from datetime import timedelta
                            existing_service.api_next_check = timezone.now() + timedelta(minutes=5)
            
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
            
            # Add API detection results
            defaults['api_detected'] = api_detected
            if api_detected:
                defaults['api_last_detected'] = timezone.now()
                defaults['api_detection_attempts'] = 0  # Reset on success
                defaults['api_next_check'] = None
                if detected_api_type:
                    defaults['api_type'] = detected_api_type
                if detected_endpoint:
                    defaults['api_endpoint'] = detected_endpoint
                # Auto-populate API URL if detected and not already set
                if not existing_service or not existing_service.api_url:
                    defaults['api_url'] = service_data['url']
            else:
                # Preserve attempt tracking
                if existing_service:
                    defaults['api_detection_attempts'] = existing_service.api_detection_attempts
                    defaults['api_next_check'] = existing_service.api_next_check
            
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
