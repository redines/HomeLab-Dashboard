from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Service, HealthCheck
from .traefik_service import sync_traefik_services
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def dashboard(request):
    """Main dashboard view."""
    services = Service.objects.all().order_by('name')
    
    context = {
        'services': services,
        'total_services': services.count(),
        'up_services': services.filter(status='up').count(),
        'down_services': services.filter(status='down').count(),
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
