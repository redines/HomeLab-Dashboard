"""Generic API client with comprehensive logging and auto-detection of authentication methods."""

import requests
import logging
import warnings
from typing import Dict, Optional, Any, List, Tuple
import json

logger = logging.getLogger(__name__)

# Suppress InsecureRequestWarning for self-signed certificates
from urllib3.exceptions import InsecureRequestWarning
warnings.filterwarnings('ignore', category=InsecureRequestWarning)


class GenericAPIClient:
    """Generic API client with auto-detection of authentication methods."""
    
    def __init__(self, base_url: str, username: Optional[str] = None, 
                 password: Optional[str] = None, api_key: Optional[str] = None,
                 auth_endpoint: Optional[str] = None):
        """
        Initialize generic API client.
        
        Args:
            base_url: Base URL of the API (e.g., https://portainer.local)
            username: Username for authentication
            password: Password for authentication
            api_key: API key for token-based authentication
            auth_endpoint: Authentication endpoint (if different from /api/auth)
        """
        # Validate and normalize URL
        if not base_url:
            raise ValueError("base_url cannot be empty")
        
        # Ensure URL has a protocol
        if not base_url.startswith(('http://', 'https://')):
            logger.warning(f"URL missing protocol, adding https://: {base_url}")
            base_url = f"https://{base_url}"
        
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.api_key = api_key
        self.auth_endpoint = auth_endpoint
        self.session = requests.Session()
        self.session.verify = False  # Allow self-signed certificates
        self._token = None
        self._auth_method = None  # Store successful auth method
        
        logger.info(f"Initialized API client for {self.base_url}")
        if username:
            logger.debug(f"Using username/password authentication with user: {username}")
        if api_key:
            logger.debug(f"Using API key authentication")
    
    def _try_find_auth_endpoint(self) -> List[str]:
        """Try to find the authentication endpoint by checking common paths and API docs."""
        candidates = []
        
        # If user specified an endpoint, try it first and only it
        if self.auth_endpoint:
            return [self.auth_endpoint]
        
        # Common authentication endpoints (ordered by popularity)
        common_endpoints = [
            '/api/v2/auth/login',  # qBittorrent, some v2 APIs
            '/api/auth',            # Portainer, many modern APIs
            '/api/login',           # Common alternative
            '/auth/login',          # Another common pattern
            '/login',               # Simple services
            '/api/v1/auth',         # Versioned API
            '/api/v1/login',
            '/auth',
        ]
        
        candidates.extend(common_endpoints)
        
        # Only try to find API documentation if we have very few candidates
        # This reduces 404 spam during auto-detection
        if len(candidates) < 3:
            doc_endpoints = ['/api/docs', '/api.json', '/swagger.json']  # Reduced list
            for doc_path in doc_endpoints:
                try:
                    # Suppress connection warnings for doc discovery
                    response = self.session.get(f"{self.base_url}{doc_path}", timeout=2)
                    if response.status_code == 200:
                        logger.debug(f"Found API documentation at {doc_path}")
                        try:
                            doc_data = response.json()
                            # Try to extract auth endpoint from OpenAPI/Swagger docs
                            if 'paths' in doc_data:
                                for path, methods in doc_data.get('paths', {}).items():
                                    if any(keyword in path.lower() for keyword in ['auth', 'login']):
                                        logger.info(f"Found auth endpoint in API docs: {path}")
                                        candidates.insert(0, path)  # Prioritize documented endpoints
                        except:
                            pass
                except:
                    pass  # Silently ignore 404s during discovery
        
        return candidates
    
    def _detect_auth_method_from_response(self, response: requests.Response) -> Optional[str]:
        """Analyze error response to detect expected authentication method."""
        hints = []
        
        # Check response headers for hints
        content_type = response.headers.get('Content-Type', '').lower()
        www_auth = response.headers.get('WWW-Authenticate', '')
        
        if www_auth:
            hints.append(f"WWW-Authenticate header suggests: {www_auth}")
            if 'bearer' in www_auth.lower():
                return "Expected Bearer token authentication"
            elif 'basic' in www_auth.lower():
                return "Expected HTTP Basic authentication"
        
        # Analyze response body for hints
        try:
            if 'application/json' in content_type:
                data = response.json()
                error_msg = str(data.get('error', data.get('message', ''))).lower()
                
                if 'form' in error_msg or 'application/x-www-form-urlencoded' in error_msg:
                    hints.append("Response suggests form data (application/x-www-form-urlencoded)")
                elif 'json' in error_msg:
                    hints.append("Response suggests JSON body")
                elif 'bearer' in error_msg or 'token' in error_msg:
                    hints.append("Response suggests Bearer token")
                elif 'api key' in error_msg or 'api_key' in error_msg:
                    hints.append("Response suggests API key authentication")
                
                # Log full error for analysis
                logger.debug(f"API error response: {data}")
        except:
            pass
        
        return '; '.join(hints) if hints else None
    
    def authenticate(self) -> bool:
        """Authenticate with the API using auto-detected method."""
        if self.api_key:
            # Token-based authentication
            self._token = self.api_key
            self.session.headers.update({'X-API-Key': self.api_key})
            logger.info("✓ Using API key for authentication")
            self._auth_method = 'api_key'
            return True
        
        if not self.username or not self.password:
            logger.error("✗ No credentials provided for authentication")
            return False
        
        # Try to find authentication endpoint
        auth_endpoints = self._try_find_auth_endpoint()
        logger.debug(f"Will try authentication endpoints: {auth_endpoints}")
        
        # Try different authentication methods
        auth_methods = [
            ('json', 'JSON body'),
            ('form', 'Form data (application/x-www-form-urlencoded)'),
            ('basic', 'HTTP Basic authentication'),
        ]
        
        for endpoint in auth_endpoints:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"Attempting authentication at {url}")
            
            for method_type, method_name in auth_methods:
                if self._try_authenticate_with_method(url, method_type, method_name):
                    logger.info(f"✓ Successfully authenticated using {method_name}")
                    self._auth_method = method_type
                    return True
        
        logger.error("✗ All authentication attempts failed")
        return False
    
    def _try_authenticate_with_method(self, url: str, method_type: str, method_name: str) -> bool:
        """Try to authenticate using a specific method."""
        try:
            auth_data = {
                'username': self.username,
                'password': self.password
            }
            
            logger.debug(f"Trying {method_name}")
            
            # Choose authentication method
            if method_type == 'json':
                response = self.session.post(url, json=auth_data, timeout=5)
            elif method_type == 'form':
                response = self.session.post(url, data=auth_data, timeout=5)
            elif method_type == 'basic':
                response = self.session.post(url, auth=(self.username, self.password), timeout=5)
            else:
                return False
            
            logger.debug(f"Response status: {response.status_code}, Content-Type: {response.headers.get('Content-Type', 'unknown')}")
            
            if response.status_code == 200:
                # Success! Now determine how to use the credentials
                content_type = response.headers.get('Content-Type', '').lower()
                
                # Check for plain text response (qBittorrent style)
                if 'text/plain' in content_type or 'text/html' in content_type:
                    if 'ok' in response.text.lower().strip():
                        logger.debug("Plain text 'Ok.' response - cookie-based authentication")
                        return True
                
                # Try to parse JSON response
                try:
                    data = response.json()
                    # Look for common token field names
                    token = data.get('jwt') or data.get('token') or data.get('access_token') or data.get('auth_token')
                    if token:
                        self._token = token
                        self.session.headers.update({'Authorization': f'Bearer {token}'})
                        logger.debug(f"Extracted token from '{list(data.keys())}' fields")
                        return True
                    else:
                        logger.debug(f"JSON response with keys: {list(data.keys())}, checking for cookies")
                except ValueError:
                    logger.debug("Non-JSON response, checking for cookies")
                
                # Check if cookies were set (session-based auth)
                if self.session.cookies:
                    logger.debug(f"Session cookies set: {list(self.session.cookies.keys())}")
                    return True
                
                logger.debug("200 response but no token or cookies found")
                return False
            
            elif response.status_code == 401:
                hint = self._detect_auth_method_from_response(response)
                if hint:
                    logger.debug(f"401 Unauthorized - {hint}")
                else:
                    logger.debug(f"401 Unauthorized - Invalid credentials or wrong auth method")
                return False
            
            elif response.status_code == 404:
                logger.debug(f"404 Not Found - Endpoint doesn't exist")
                return False
            
            elif response.status_code == 400:
                hint = self._detect_auth_method_from_response(response)
                if hint:
                    logger.debug(f"400 Bad Request - {hint}")
                else:
                    logger.debug(f"400 Bad Request - Wrong request format")
                return False
            
            elif response.status_code == 405:
                logger.debug(f"405 Method Not Allowed - Wrong HTTP method")
                return False
            
            else:
                logger.debug(f"Unexpected status code: {response.status_code}")
                hint = self._detect_auth_method_from_response(response)
                if hint:
                    logger.debug(f"Hint: {hint}")
                return False
                
        except requests.exceptions.Timeout:
            logger.debug(f"Timeout - endpoint didn't respond in time")
            return False
        except requests.exceptions.ConnectionError:
            logger.debug(f"Connection error - endpoint unreachable")
            return False
        except Exception as e:
            logger.debug(f"Exception: {type(e).__name__}: {e}")
            return False
    
    def request(self, method: str, endpoint: str, **kwargs) -> Optional[Any]:
        """
        Make authenticated request to API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (e.g., /api/users)
            **kwargs: Additional arguments for requests (data, json, params, etc.)
            
        Returns:
            Response data or None on error
        """
        # Ensure we're authenticated
        if not self._token and not self.session.cookies:
            logger.debug("Not authenticated, attempting authentication")
            if not self.authenticate():
                logger.error("Failed to authenticate before making request")
                return None
        
        # Ensure endpoint starts with / for proper URL construction
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
            logger.debug(f"Added leading slash to endpoint: {endpoint}")
        
        url = f"{self.base_url}{endpoint}"
        logger.info(f"Making {method} request to {url}")
        
        # Log request details (sanitized)
        if 'json' in kwargs:
            logger.debug(f"Request JSON body: {json.dumps(kwargs['json'], indent=2)}")
        if 'data' in kwargs:
            logger.debug(f"Request data: {kwargs['data']}")
        if 'params' in kwargs:
            logger.debug(f"Request params: {kwargs['params']}")
        
        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            
            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Log response body (limited)
            if response.text:
                logger.debug(f"Response body (first 500 chars): {response.text[:500]}")
            
            # Handle authentication errors
            if response.status_code == 401:
                logger.warning("Got 401 Unauthorized, attempting re-authentication")
                if self.authenticate():
                    logger.debug(f"Retrying {method} request after re-authentication")
                    response = self.session.request(method, url, timeout=10, **kwargs)
                    logger.info(f"Retry response status: {response.status_code}")
                else:
                    logger.error("Re-authentication failed")
                    return None
            
            response.raise_for_status()
            
            # Parse response
            if not response.text:
                logger.debug("Empty response body (success)")
                return True
            
            try:
                data = response.json()
                logger.debug(f"Successfully parsed JSON response with keys: {list(data.keys()) if isinstance(data, dict) else 'array'}")
                return data
            except ValueError:
                logger.debug("Response is not JSON, returning text")
                return response.text
                
        except requests.exceptions.Timeout:
            logger.error(f"✗ Request timeout: {url} did not respond within 10 seconds")
            raise Exception(f"Request timeout: The API at {url} did not respond within 10 seconds")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"✗ Connection error for {url}: {e}")
            raise Exception(f"Connection error: Cannot connect to {url}. Error: {str(e)}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ HTTP error {response.status_code} for {url}: {response.text[:300]}")
            raise Exception(f"HTTP error {response.status_code}: {response.text[:300]}")
        except requests.exceptions.SSLError as e:
            logger.error(f"✗ SSL error for {url}: {e}")
            raise Exception(f"SSL certificate error for {url}: {str(e)}")
        except Exception as e:
            logger.error(f"✗ Unexpected error for {url}: {type(e).__name__}: {e}")
            raise
    
    def get(self, endpoint: str, **kwargs) -> Optional[Any]:
        """Make GET request."""
        return self.request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Optional[Any]:
        """Make POST request."""
        return self.request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> Optional[Any]:
        """Make PUT request."""
        return self.request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Optional[Any]:
        """Make DELETE request."""
        return self.request('DELETE', endpoint, **kwargs)
