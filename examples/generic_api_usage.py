"""
Example: Using the Generic API Client

This file demonstrates how to use the GenericAPIClient to interact
with any service in your homelab without writing service-specific code.
"""

from dashboard.models import Service
from dashboard.generic_api_client import GenericAPIClient


# Example 1: Username/Password Authentication (Portainer, qBittorrent, Gitea, etc.)
def example_username_password():
    """Use username/password authentication."""
    
    # Get service from database
    service = Service.objects.get(name='Portainer')
    
    # Create generic client
    client = GenericAPIClient(
        base_url=service.api_url,
        username=service.api_username,
        password=service.api_password
    )
    
    # Make requests - authentication is automatic
    status = client.get('/api/status')
    print(f"Portainer version: {status['Version']}")
    
    # POST request
    endpoints = client.get('/api/endpoints')
    print(f"Found {len(endpoints)} endpoints")


# Example 2: API Key Authentication (Sonarr, Radarr, Prowlarr, etc.)
def example_api_key():
    """Use API key authentication."""
    
    # Get service from database
    service = Service.objects.get(name='Sonarr')
    
    # Create client with API key
    client = GenericAPIClient(
        base_url=service.api_url,
        api_key=service.api_key
    )
    
    # Make requests - API key is automatically added to headers
    status = client.get('/api/v3/system/status')
    print(f"Sonarr version: {status['version']}")
    
    # Get calendar
    calendar = client.get('/api/v3/calendar')
    print(f"Found {len(calendar)} upcoming episodes")


# Example 3: Custom Authentication Endpoint
def example_custom_auth():
    """Use custom authentication endpoint for non-standard services."""
    
    client = GenericAPIClient(
        base_url='https://custom-service.local',
        username='admin',
        password='password',
        auth_endpoint='/custom/login'  # Override default
    )
    
    data = client.get('/api/data')
    print(data)


# Example 4: Different HTTP Methods
def example_http_methods():
    """Demonstrate different HTTP methods."""
    
    service = Service.objects.get(name='Gitea')
    client = GenericAPIClient(
        base_url=service.api_url,
        username=service.api_username,
        password=service.api_password
    )
    
    # GET
    repos = client.get('/api/v1/user/repos')
    
    # POST - create new repository
    new_repo = client.post('/api/v1/user/repos', data={
        'name': 'test-repo',
        'description': 'Test repository',
        'private': True
    })
    
    # PUT - update repository
    client.put(f'/api/v1/repos/{new_repo["owner"]["login"]}/{new_repo["name"]}', data={
        'description': 'Updated description'
    })
    
    # DELETE - delete repository
    client.delete(f'/api/v1/repos/{new_repo["owner"]["login"]}/{new_repo["name"]}')


# Example 5: Query Parameters
def example_query_params():
    """Use query parameters in requests."""
    
    service = Service.objects.get(name='qBittorrent')
    client = GenericAPIClient(
        base_url=service.api_url,
        username=service.api_username,
        password=service.api_password
    )
    
    # GET with query parameters
    torrents = client.get('/api/v2/torrents/info', params={
        'filter': 'downloading',
        'category': 'movies',
        'sort': 'progress',
        'reverse': 'true'
    })
    
    print(f"Found {len(torrents)} downloading torrents in movies category")


# Example 6: Error Handling
def example_error_handling():
    """Handle API errors gracefully."""
    
    try:
        service = Service.objects.get(name='Portainer')
        client = GenericAPIClient(
            base_url=service.api_url,
            username='wrong_user',
            password='wrong_pass'
        )
        
        # This will fail with authentication error
        client.get('/api/status')
        
    except Exception as e:
        print(f"Error occurred: {e}")
        # Check logs for detailed error information


# Example 7: Using the API Proxy (from JavaScript/frontend)
def example_api_proxy_usage():
    """
    Example of using the generic API proxy from JavaScript.
    
    This code would run in your frontend JavaScript:
    
    // GET request
    fetch('/api/services/1/proxy/?path=/api/status')
        .then(r => r.json())
        .then(data => console.log(data.data));
    
    // POST request
    fetch('/api/services/1/proxy/?path=/api/create', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name: 'test'})
    })
        .then(r => r.json())
        .then(data => console.log(data.data));
    
    // With query parameters
    fetch('/api/services/1/proxy/?path=/api/torrents&filter=downloading')
        .then(r => r.json())
        .then(data => console.log(data.data));
    """
    pass


# Example 8: Loop Through All API-Enabled Services
def example_all_services():
    """Query all services with API support."""
    
    # Get all services with API detected
    api_services = Service.objects.filter(api_detected=True)
    
    for service in api_services:
        print(f"\n{service.name} ({service.api_type}):")
        
        try:
            # Create client based on auth method
            if service.api_key:
                client = GenericAPIClient(
                    base_url=service.api_url,
                    api_key=service.api_key
                )
            elif service.api_username and service.api_password:
                client = GenericAPIClient(
                    base_url=service.api_url,
                    username=service.api_username,
                    password=service.api_password
                )
            else:
                print("  No credentials configured")
                continue
            
            # Try to get status (common endpoint)
            for path in ['/api/status', '/api/system/status', '/api/v1/status', '/api/v3/system/status']:
                try:
                    status = client.get(path)
                    print(f"  Status: {status}")
                    break
                except:
                    continue
                    
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == '__main__':
    # Run examples
    print("Generic API Client Examples\n")
    print("=" * 50)
    
    # Uncomment to run specific examples:
    # example_username_password()
    # example_api_key()
    # example_http_methods()
    # example_query_params()
    # example_all_services()
    
    print("\nSee the code for more examples!")
