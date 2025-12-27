from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Service, HealthCheck, GrafanaPanel
from .utils.traefik_service import sync_traefik_services
from .utils.generic_api_client import GenericAPIClient
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
    
    # Get active Grafana panels (limit to first 4 for dashboard preview)
    grafana_panels = GrafanaPanel.objects.filter(is_active=True).order_by('display_order', 'title')[:4]
    
    # Trigger async health check in background thread
    health_check_thread = threading.Thread(target=check_all_services_health, daemon=True)
    health_check_thread.start()
    
    context = {
        'services': services,
        'total_services': services.count(),
        'up_services': services.filter(status='up').count(),
        'down_services': services.filter(status='down').count(),
        'api_services': services.filter(api_detected=True).count(),
        'grafana_panels': grafana_panels,
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
    """API endpoint to refresh services from Traefik (auto-detected) or just check health."""
    from .utils.traefik_service import is_traefik_configured, check_traefik_availability
    
    try:
        synced_count = 0
        traefik_available = False
        traefik_configured = is_traefik_configured()
        
        # Automatically attempt Traefik sync if available
        if traefik_configured:
            if check_traefik_availability():
                synced_count = sync_traefik_services()
                traefik_available = True
            else:
                logger.info("Traefik is configured but not available, using manual mode")
        else:
            logger.debug("Traefik is not configured, using manual service management")
        
        # Check health for all services
        services = Service.objects.all()
        checked_count = 0
        for service in services:
            try:
                service.check_health()
                checked_count += 1
            except Exception as e:
                logger.error(f"Error checking health for {service.name}: {e}")
        
        response_data = {
            'success': True,
            'synced_services': synced_count,
            'health_checks': checked_count,
            'traefik_configured': traefik_configured,
            'traefik_available': traefik_available,
            'timestamp': timezone.now().isoformat(),
        }
        
        # Add informative message based on Traefik status
        if traefik_configured and not traefik_available:
            response_data['info'] = 'Traefik is configured but not responding. Health checks performed. Using manual service management.'
        elif not traefik_configured:
            response_data['info'] = 'Using manual service management. Add services with the "➕ Add Service" button.'
        
        return JsonResponse(response_data)
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
    from .utils.api_detector import APIDetector
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


@require_http_methods(["POST"])
def create_service(request):
    """Create a new manual service."""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        name = data.get('name', '').strip()
        url = data.get('url', '').strip()
        
        if not name:
            return JsonResponse({
                'success': False,
                'error': 'Service name is required'
            }, status=400)
        
        if not url:
            return JsonResponse({
                'success': False,
                'error': 'Service URL is required'
            }, status=400)
        
        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        url = url.rstrip('/')
        
        # Check if service with this name already exists
        if Service.objects.filter(name=name).exists():
            return JsonResponse({
                'success': False,
                'error': f'A service with the name "{name}" already exists'
            }, status=400)
        
        # Create the service
        service = Service.objects.create(
            name=name,
            url=url,
            description=data.get('description', '').strip(),
            icon=data.get('icon', '').strip(),
            service_type=data.get('service_type', 'other'),
            provider=data.get('provider', 'local'),
            is_manual=True,
            status='unknown',
            tags=data.get('tags', '').strip(),
        )
        
        # Check health immediately
        service.check_health()
        
        logger.info(f"Created manual service: {service.name}")
        
        return JsonResponse({
            'success': True,
            'message': 'Service created successfully',
            'service': {
                'id': service.id,
                'name': service.name,
                'url': service.url,
                'status': service.status,
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error creating service: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def update_service(request, service_id):
    """Update an existing manual service."""
    try:
        service = get_object_or_404(Service, id=service_id)
        
        # Only allow editing manual services
        if not service.is_manual:
            return JsonResponse({
                'success': False,
                'error': 'Only manually created services can be edited'
            }, status=403)
        
        data = json.loads(request.body)
        
        # Update fields if provided
        if 'name' in data:
            name = data['name'].strip()
            if name:
                # Check if name is taken by another service
                if Service.objects.exclude(id=service_id).filter(name=name).exists():
                    return JsonResponse({
                        'success': False,
                        'error': f'A service with the name "{name}" already exists'
                    }, status=400)
                service.name = name
        
        if 'url' in data:
            url = data['url'].strip()
            if url:
                if not url.startswith(('http://', 'https://')):
                    url = f"https://{url}"
                service.url = url.rstrip('/')
        
        if 'description' in data:
            service.description = data['description'].strip()
        
        if 'icon' in data:
            service.icon = data['icon'].strip()
        
        if 'service_type' in data:
            service.service_type = data['service_type']
        
        if 'provider' in data:
            service.provider = data['provider']
        
        if 'tags' in data:
            service.tags = data['tags'].strip()
        
        service.save()
        
        # Re-check health
        service.check_health()
        
        logger.info(f"Updated manual service: {service.name}")
        
        return JsonResponse({
            'success': True,
            'message': 'Service updated successfully',
            'service': {
                'id': service.id,
                'name': service.name,
                'url': service.url,
                'status': service.status,
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error updating service {service_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST", "DELETE"])
def delete_service(request, service_id):
    """Delete a manual service."""
    try:
        service = get_object_or_404(Service, id=service_id)
        
        # Only allow deleting manual services
        if not service.is_manual:
            return JsonResponse({
                'success': False,
                'error': 'Only manually created services can be deleted'
            }, status=403)
        
        service_name = service.name
        service.delete()
        
        logger.info(f"Deleted manual service: {service_name}")
        
        return JsonResponse({
            'success': True,
            'message': f'Service "{service_name}" deleted successfully'
        })
    
    except Exception as e:
        logger.error(f"Error deleting service {service_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================
# Grafana Panel Views
# ============================================

@require_http_methods(["GET"])
def api_grafana_panels(request):
    """API endpoint to get all active Grafana panels as JSON."""
    panels = GrafanaPanel.objects.filter(is_active=True).order_by('display_order', 'title')
    
    panels_data = []
    for panel in panels:
        panel_data = {
            'id': panel.id,
            'title': panel.title,
            'description': panel.description,
            'embed_url': panel.get_embed_url(),
            'dashboard_url': panel.get_dashboard_url(),
            'width': panel.width,
            'height': panel.height,
            'theme': panel.theme,
            'refresh': panel.refresh,
        }
        
        # Add service info if linked
        if panel.service:
            panel_data['service'] = {
                'id': panel.service.id,
                'name': panel.service.name,
                'status': panel.service.status,
            }
        
        panels_data.append(panel_data)
    
    return JsonResponse({
        'success': True,
        'panels': panels_data,
        'total': len(panels_data)
    })


def grafana_panels_view(request):
    """View to display all active Grafana panels."""
    panels = GrafanaPanel.objects.filter(is_active=True).order_by('display_order', 'title')
    
    context = {
        'panels': panels,
        'total_panels': panels.count(),
    }
    
    return render(request, 'dashboard/grafana_panels.html', context)


def grafana_panel_detail(request, panel_id):
    """View to display a single Grafana panel in fullscreen."""
    panel = get_object_or_404(GrafanaPanel, id=panel_id)
    
    context = {
        'panel': panel,
    }
    
    return render(request, 'dashboard/grafana_panel_detail.html', context)

