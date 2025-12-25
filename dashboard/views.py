from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Service, HealthCheck
from .traefik_service import sync_traefik_services
from .generic_api_client import GenericAPIClient
from django.utils import timezone
import logging
import threading
import json

logger = logging.getLogger(__name__)


def check_all_services_health():
    """Background task to check health of all services."""
    services = Service.objects.all()
    for service in services:
        try:
            service.check_health()
        except Exception as e:
            logger.error(f"Error checking health for {service.name}: {e}")


def dashboard(request):
    """Main dashboard view."""
    services = Service.objects.all().order_by('name')
    
    # Trigger async health check in background thread
    health_check_thread = threading.Thread(target=check_all_services_health, daemon=True)
    health_check_thread.start()
    
    context = {
        'services': services,
        'total_services': services.count(),
        'up_services': services.filter(status='up').count(),
        'down_services': services.filter(status='down').count(),
        'api_services': services.filter(api_detected=True).count(),
        'last_updated': timezone.now(),
    }
    
    return render(request, 'dashboard/index.html', context)


@require_http_methods(["GET"])
def api_services(request):
    """API endpoint to get all services as JSON."""
    services = Service.objects.all().order_by('name')
    
    services_data = []
    for service in services:
        services_data.append({
            'id': service.id,
            'name': service.name,
            'url': service.url,
            'status': service.status,
            'service_type': service.service_type,
            'provider': service.provider,
            'description': service.description,
            'icon': service.icon,
            'tags': service.tags.split(',') if service.tags else [],
            'response_time': service.response_time,
            'last_checked': service.last_checked.isoformat() if service.last_checked else None,
            'uptime_percentage': service.uptime_percentage,
        })
    
    return JsonResponse({
        'services': services_data,
        'total': len(services_data),
        'timestamp': timezone.now().isoformat(),
    })


@require_http_methods(["POST"])
def refresh_services(request):
    """API endpoint to refresh services from Traefik."""
    try:
        synced_count = sync_traefik_services()
        
        # Check health for all services
        services = Service.objects.all()
        checked_count = 0
        for service in services:
            try:
                service.check_health()
                checked_count += 1
            except Exception as e:
                logger.error(f"Error checking health for {service.name}: {e}")
        
        return JsonResponse({
            'success': True,
            'synced_services': synced_count,
            'health_checks': checked_count,
            'timestamp': timezone.now().isoformat(),
        })
    except Exception as e:
        logger.error(f"Error refreshing services: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@require_http_methods(["POST"])
def check_service_health(request, service_id):
    """API endpoint to check health of a specific service."""
    try:
        service = Service.objects.get(id=service_id)
        status = service.check_health()
        
        return JsonResponse({
            'success': True,
            'service_id': service.id,
            'name': service.name,
            'status': status,
            'response_time': service.response_time,
            'last_checked': service.last_checked.isoformat() if service.last_checked else None,
        })
    except Service.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Service not found',
        }, status=404)
    except Exception as e:
        logger.error(f"Error checking health for service {service_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


def service_detail(request, service_id):
    """Service detail page with API integration."""
    service = get_object_or_404(Service, id=service_id)
    
    context = {
        'service': service,
        'has_api': bool(service.api_type and service.api_url),
        'has_credentials': bool((service.api_username and service.api_password) or service.api_key),
    }
    
    return render(request, 'dashboard/service_detail.html', context)


@require_http_methods(["POST"])
def update_service_credentials(request, service_id):
    """Update API credentials for a service."""
    service = get_object_or_404(Service, id=service_id)
    
    try:
        data = json.loads(request.body)
        
        # Update fields if provided
        if 'api_url' in data:
            api_url = data['api_url'].strip()
            # Validate and normalize URL
            if api_url:
                # Ensure URL has protocol
                if not api_url.startswith(('http://', 'https://')):
                    api_url = f"https://{api_url}"
                # Remove trailing slashes
                api_url = api_url.rstrip('/')
                service.api_url = api_url
                logger.info(f"Updated API URL for {service.name}: {api_url}")
        if 'api_type' in data:
            service.api_type = data['api_type']
        if 'api_username' in data:
            service.api_username = data['api_username']
        if 'api_password' in data:
            service.api_password = data['api_password']
        if 'api_key' in data:
            service.api_key = data['api_key']
        
        service.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Credentials updated successfully'
        })
    except Exception as e:
        logger.error(f"Error updating credentials for service {service_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def detect_service_api(request, service_id):
    """Force re-detection of API for a specific service."""
    from .api_detector import APIDetector
    from django.utils import timezone
    
    service = get_object_or_404(Service, id=service_id)
    
    try:
        # Check if API is already configured with credentials
        if service.api_detected and service.api_type and service.api_url:
            has_creds = bool((service.api_username and service.api_password) or service.api_key)
            if has_creds:
                logger.info(f"API already configured for {service.name}: type={service.api_type}")
                return JsonResponse({
                    'success': True,
                    'message': f'✅ API already configured: {service.api_type}. Credentials are set and ready to use.',
                    'api_type': service.api_type,
                    'api_endpoint': service.api_endpoint,
                    'api_url': service.api_url,
                    'already_configured': True,
                })
        
        logger.info(f"Starting API detection for {service.name} at {service.url}")
        
        # Detect API
        has_api, api_type, api_endpoint = APIDetector.detect_api(
            service.name,
            service.url,
            labels=None
        )
        
        logger.info(f"Detection result for {service.name}: has_api={has_api}, type={api_type}, endpoint={api_endpoint}")
        
        if has_api:
            service.api_detected = True
            service.api_type = api_type
            service.api_endpoint = api_endpoint
            service.api_last_detected = timezone.now()
            
            # Auto-populate API URL if not set
            if not service.api_url:
                # Ensure URL has protocol
                api_url = service.url
                if not api_url.startswith(('http://', 'https://')):
                    api_url = f"https://{api_url}"
                service.api_url = api_url.rstrip('/')
                logger.info(f"Auto-populated API URL for {service.name}: {service.api_url}")
            
            service.save()
            logger.info(f"Successfully saved API detection for {service.name}")
            
            return JsonResponse({
                'success': True,
                'message': f'✅ API detected: {api_type}',
                'api_type': api_type,
                'api_endpoint': api_endpoint,
                'api_url': service.api_url,
            })
        else:
            service.api_detected = False
            service.api_last_detected = timezone.now()
            service.save()
            
            logger.warning(f"No API detected for {service.name} at {service.url}")
            
            return JsonResponse({
                'success': False,
                'message': f'❌ No API detected. The service at {service.url} does not respond to common API endpoints. This might be because: 1) The service has no API, 2) The API requires authentication to probe, or 3) The service is not accessible from this server.'
            })
    except Exception as e:
        logger.error(f"Error detecting API for service {service_id} ({service.name}): {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'Error during detection: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def service_api_docs(request, service_id):
    """Get API documentation for a service."""
    service = get_object_or_404(Service, id=service_id)
    
    if not service.api_detected:
        return JsonResponse({
            'success': False,
            'error': 'Service does not have API integration configured',
        }, status=400)
    
    # API documentation by service type
    api_docs = {
        'qbittorrent': {
            'name': 'qBittorrent',
            'official_docs': 'https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API',
            'endpoints': [
                {
                    'category': 'Authentication',
                    'endpoints': [
                        {
                            'name': 'Login',
                            'method': 'POST',
                            'path': '/api/v2/auth/login',
                            'description': 'Login to qBittorrent (handled automatically by proxy)',
                        },
                        {
                            'name': 'Logout',
                            'method': 'POST',
                            'path': '/api/v2/auth/logout',
                            'description': 'Logout from qBittorrent',
                        },
                    ]
                },
                {
                    'category': 'Application',
                    'endpoints': [
                        {
                            'name': 'Get Application Version',
                            'method': 'GET',
                            'path': '/api/v2/app/version',
                            'description': 'Get qBittorrent version',
                        },
                        {
                            'name': 'Get Application Preferences',
                            'method': 'GET',
                            'path': '/api/v2/app/preferences',
                            'description': 'Get application preferences',
                        },
                        {
                            'name': 'Set Application Preferences',
                            'method': 'POST',
                            'path': '/api/v2/app/setPreferences',
                            'description': 'Set application preferences',
                        },
                    ]
                },
                {
                    'category': 'Transfer Info',
                    'endpoints': [
                        {
                            'name': 'Get Transfer Info',
                            'method': 'GET',
                            'path': '/api/v2/transfer/info',
                            'description': 'Get global transfer info (speeds, totals, etc.)',
                        },
                        {
                            'name': 'Get Speed Limits',
                            'method': 'GET',
                            'path': '/api/v2/transfer/speedLimitsMode',
                            'description': 'Get current speed limits mode',
                        },
                        {
                            'name': 'Set Download Limit',
                            'method': 'POST',
                            'path': '/api/v2/transfer/setDownloadLimit',
                            'description': 'Set global download limit (bytes/sec, 0 = unlimited)',
                        },
                        {
                            'name': 'Set Upload Limit',
                            'method': 'POST',
                            'path': '/api/v2/transfer/setUploadLimit',
                            'description': 'Set global upload limit (bytes/sec, 0 = unlimited)',
                        },
                    ]
                },
                {
                    'category': 'Torrent Management',
                    'endpoints': [
                        {
                            'name': 'Get Torrent List',
                            'method': 'GET',
                            'path': '/api/v2/torrents/info',
                            'description': 'Get list of torrents. Supports filters: all, downloading, seeding, completed, paused, active, inactive, resumed, stalled, stalled_uploading, stalled_downloading',
                        },
                        {
                            'name': 'Get Torrent Properties',
                            'method': 'GET',
                            'path': '/api/v2/torrents/properties',
                            'description': 'Get torrent properties by hash',
                        },
                        {
                            'name': 'Add New Torrent',
                            'method': 'POST',
                            'path': '/api/v2/torrents/add',
                            'description': 'Add new torrent via URL or magnet link',
                        },
                        {
                            'name': 'Pause Torrent',
                            'method': 'POST',
                            'path': '/api/v2/torrents/pause',
                            'description': 'Pause torrent(s). Requires hash parameter',
                        },
                        {
                            'name': 'Resume Torrent',
                            'method': 'POST',
                            'path': '/api/v2/torrents/resume',
                            'description': 'Resume torrent(s). Requires hash parameter',
                        },
                        {
                            'name': 'Delete Torrent',
                            'method': 'POST',
                            'path': '/api/v2/torrents/delete',
                            'description': 'Delete torrent(s). Requires hash and deleteFiles parameters',
                        },
                    ]
                },
                {
                    'category': 'Categories & Tags',
                    'endpoints': [
                        {
                            'name': 'Get Categories',
                            'method': 'GET',
                            'path': '/api/v2/torrents/categories',
                            'description': 'Get all categories',
                        },
                        {
                            'name': 'Create Category',
                            'method': 'POST',
                            'path': '/api/v2/torrents/createCategory',
                            'description': 'Create new category',
                        },
                        {
                            'name': 'Get Tags',
                            'method': 'GET',
                            'path': '/api/v2/torrents/tags',
                            'description': 'Get all tags',
                        },
                    ]
                },
            ]
        },
        'sonarr': {
            'name': 'Sonarr',
            'official_docs': 'https://wiki.servarr.com/sonarr/api',
            'endpoints': [
                {
                    'category': 'Series',
                    'endpoints': [
                        {
                            'name': 'Get All Series',
                            'method': 'GET',
                            'path': '/api/v3/series',
                            'description': 'Get all series in your library',
                        },
                        {
                            'name': 'Get Series by ID',
                            'method': 'GET',
                            'path': '/api/v3/series/{id}',
                            'description': 'Get specific series by ID',
                        },
                        {
                            'name': 'Add Series',
                            'method': 'POST',
                            'path': '/api/v3/series',
                            'description': 'Add a new series',
                        },
                    ]
                },
                {
                    'category': 'Episodes',
                    'endpoints': [
                        {
                            'name': 'Get Episodes',
                            'method': 'GET',
                            'path': '/api/v3/episode',
                            'description': 'Get episodes, optionally filtered by series ID',
                        },
                    ]
                },
                {
                    'category': 'Queue',
                    'endpoints': [
                        {
                            'name': 'Get Queue',
                            'method': 'GET',
                            'path': '/api/v3/queue',
                            'description': 'Get currently downloading/processing items',
                        },
                    ]
                },
                {
                    'category': 'System',
                    'endpoints': [
                        {
                            'name': 'Get System Status',
                            'method': 'GET',
                            'path': '/api/v3/system/status',
                            'description': 'Get system status information',
                        },
                    ]
                },
            ]
        },
        'radarr': {
            'name': 'Radarr',
            'official_docs': 'https://wiki.servarr.com/radarr/api',
            'endpoints': [
                {
                    'category': 'Movies',
                    'endpoints': [
                        {
                            'name': 'Get All Movies',
                            'method': 'GET',
                            'path': '/api/v3/movie',
                            'description': 'Get all movies in your library',
                        },
                        {
                            'name': 'Get Movie by ID',
                            'method': 'GET',
                            'path': '/api/v3/movie/{id}',
                            'description': 'Get specific movie by ID',
                        },
                        {
                            'name': 'Add Movie',
                            'method': 'POST',
                            'path': '/api/v3/movie',
                            'description': 'Add a new movie',
                        },
                    ]
                },
                {
                    'category': 'Queue',
                    'endpoints': [
                        {
                            'name': 'Get Queue',
                            'method': 'GET',
                            'path': '/api/v3/queue',
                            'description': 'Get currently downloading/processing items',
                        },
                    ]
                },
                {
                    'category': 'System',
                    'endpoints': [
                        {
                            'name': 'Get System Status',
                            'method': 'GET',
                            'path': '/api/v3/system/status',
                            'description': 'Get system status information',
                        },
                    ]
                },
            ]
        },
    }
    
    service_api_type = service.api_type or 'unknown'
    docs = api_docs.get(service_api_type, None)
    
    if docs:
        return JsonResponse({
            'success': True,
            'service': service.name,
            'api_type': service_api_type,
            'api_url': service.api_url,
            'proxy_url': f'/api/services/{service.id}/proxy/',
            'official_docs': docs['official_docs'],
            'documentation': docs,
        })
    else:
        # Generic documentation for unsupported API types
        return JsonResponse({
            'success': True,
            'service': service.name,
            'api_type': service_api_type,
            'api_url': service.api_url,
            'proxy_url': f'/api/services/{service.id}/proxy/',
            'message': 'This service has API support but specific documentation is not available. Please refer to the official API documentation for this service.',
            'documentation': None,
        })


@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE", "PATCH"])
def generic_api_proxy(request, service_id):
    """Generic proxy for any service API requests."""
    service = get_object_or_404(Service, id=service_id)
    
    # Check if service has API URL configured
    if not service.api_url:
        return JsonResponse({
            'success': False,
            'error': 'API URL not configured. Please configure API credentials in the service detail page.',
        }, status=400)
    
    # Check if service has authentication configured
    has_auth = bool(service.api_username and service.api_password) or bool(service.api_key)
    if not has_auth:
        return JsonResponse({
            'success': False,
            'error': 'API credentials not configured. Please add username/password or API key in the service detail page.',
        }, status=400)
    
    # Get the target path from query parameter
    target_path = request.GET.get('path', '')
    if not target_path:
        return JsonResponse({
            'success': False,
            'error': 'Missing "path" query parameter. Example: ?path=/api/v1/status',
        }, status=400)
    
    try:
        # Validate and log the API URL
        logger.info(f"API Proxy request for {service.name}: base_url={service.api_url}, path={target_path}")
        
        # Create generic API client
        client_kwargs = {
            'base_url': service.api_url,
        }
        
        # Add authentication if configured
        if service.api_username and service.api_password:
            client_kwargs['username'] = service.api_username
            client_kwargs['password'] = service.api_password
        elif service.api_key:
            client_kwargs['api_key'] = service.api_key
        
        try:
            client = GenericAPIClient(**client_kwargs)
        except ValueError as e:
            logger.error(f"Invalid API URL for {service.name}: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Invalid API URL configuration: {str(e)}. Please check the API URL in service settings.',
            }, status=400)
        
        # Prepare request data
        data = None
        if request.body:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                data = request.body.decode('utf-8')
        
        # Forward query parameters (excluding 'path')
        params = {k: v for k, v in request.GET.items() if k != 'path'}
        
        # Make the API request based on HTTP method
        response_data = client.request(
            method=request.method,
            endpoint=target_path,
            data=data,
            params=params if params else None
        )
        
        return JsonResponse({
            'success': True,
            'data': response_data
        })
    
    except Exception as e:
        logger.error(f"Error in generic API proxy for {service.name}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
