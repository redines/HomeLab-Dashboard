"""
API Detection Service
Automatically detects if services have APIs available.
"""
import requests
import logging
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class APIDetector:
    """Detect API availability for services."""
    
    # Common API endpoint patterns to try (from generic to specific)
    COMMON_ENDPOINTS = [
        '/api',
        '/api/v1',
        '/api/v2',
        '/api/v3',
        '/api/v1/system/status',
        '/api/v2/app/version',
        '/api/v2/auth/login',
        '/api/v3/system/status',
        '/api/system/status',
        '/api/version',
        '/api/status',
        '/api/health',
        '/health',
        '/healthz',
        '/System/Info/Public',
        '/identity',
        '/docs',
        '/swagger',
        '/api-docs',
    ]
    
    @staticmethod
    def detect_api_from_labels(labels: Dict[str, str]) -> Optional[str]:
        """
        Detect API type from Traefik/Docker labels.
        
        Args:
            labels: Dictionary of labels from Traefik/Docker
            
        Returns:
            API type if detected from labels, None otherwise
        """
        if not labels:
            return None
            
        # Check for custom homelab labels
        if labels.get('homelab.api.enabled') == 'true':
            api_type = labels.get('homelab.api.type')
            if api_type:
                logger.info(f"✓ API type from labels: {api_type}")
                return api_type
        
        # Check for common Docker Compose project labels
        compose_service = labels.get('com.docker.compose.service')
        if compose_service:
            logger.info(f"✓ Service from compose label: {compose_service}")
            return compose_service.lower()
        
        return None
    
    @staticmethod
    def probe_api_endpoints(base_url: str, timeout: int = 3) -> Tuple[bool, Optional[str]]:
        """
        Probe service to detect API availability by trying common endpoints.
        
        Args:
            base_url: Base URL of the service
            timeout: Request timeout in seconds
            
        Returns:
            Tuple of (api_detected: bool, detected_endpoint: Optional[str])
        """
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        session = requests.Session()
        session.verify = False  # Allow self-signed certificates
        
        logger.info(f"Probing API endpoints for {base_url}")
        
        for endpoint in APIDetector.COMMON_ENDPOINTS:
            try:
                url = base_url.rstrip('/') + endpoint
                logger.debug(f"Trying endpoint: {url}")
                response = session.get(url, timeout=timeout, allow_redirects=False)
                
                logger.debug(f"  Response: status={response.status_code}, content-type={response.headers.get('Content-Type', 'N/A')}")
                
                # Check for successful response or authentication required
                if response.status_code in [200, 401, 403]:
                    # Check if response looks like JSON (API indicator)
                    content_type = response.headers.get('Content-Type', '')
                    if 'application/json' in content_type or response.status_code == 401:
                        logger.info(f"✓ API endpoint found: {url} (status={response.status_code})")
                        return True, endpoint
                    
                    # Some APIs return HTML for docs
                    if endpoint in ['/docs', '/swagger', '/api-docs']:
                        if 'text/html' in content_type:
                            logger.info(f"✓ API documentation found: {url}")
                            return True, endpoint
                            
            except requests.exceptions.Timeout:
                logger.debug(f"  Timeout for {endpoint}")
                continue
            except requests.exceptions.ConnectionError as e:
                logger.debug(f"  Connection error for {endpoint}: {e}")
                continue
            except requests.exceptions.RequestException as e:
                logger.debug(f"  Request error for {endpoint}: {e}")
                continue
        
        logger.info(f"No API endpoints found for {base_url}")
        return False, None
    
    @staticmethod
    def detect_api(service_name: str, service_url: str, labels: Optional[Dict[str, str]] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Comprehensive API detection combining labels and endpoint probing.
        
        Args:
            service_name: Name of the service
            service_url: Base URL of the service
            labels: Optional Traefik/Docker labels
            
        Returns:
            Tuple of (has_api: bool, api_type: Optional[str], api_endpoint: Optional[str])
        """
        detected_type = None
        detected_endpoint = None
        
        # Method 1: Check labels for API type (from Traefik/Docker)
        if labels:
            detected_type = APIDetector.detect_api_from_labels(labels)
        
        # Method 2: Probe endpoints to verify API availability
        has_api, endpoint = APIDetector.probe_api_endpoints(service_url)
        if has_api:
            detected_endpoint = endpoint
            # If we found an API but didn't get type from labels, mark as service name or 'custom'
            if not detected_type:
                # Use the service name as the type if it looks reasonable
                service_name_lower = service_name.lower().replace(' ', '')
                if len(service_name_lower) > 2:
                    detected_type = service_name_lower
                    logger.info(f"✓ API detected for {service_name}, using service name as type")
                else:
                    detected_type = 'custom'
                    logger.info(f"✓ Generic API detected for {service_name}")
            return True, detected_type, detected_endpoint
        
        # No API detected
        if detected_type:
            logger.warning(f"✗ {service_name}: Type detected from labels ({detected_type}) but endpoints unreachable")
        else:
            logger.debug(f"✗ No API detected for {service_name}")
        
        return False, detected_type, None
