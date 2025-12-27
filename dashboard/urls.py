from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
    path('api/services/', views.api_services, name='api_services'),
    path('api/services/create/', views.create_service, name='create_service'),
    path('api/services/refresh/', views.refresh_services, name='refresh_services'),
    path('api/services/<int:service_id>/health/', views.check_service_health, name='check_health'),
    path('api/services/<int:service_id>/update/', views.update_service, name='update_service'),
    path('api/services/<int:service_id>/delete/', views.delete_service, name='delete_service'),
    path('api/services/<int:service_id>/credentials/', views.update_service_credentials, name='update_credentials'),
    path('api/services/<int:service_id>/detect-api/', views.detect_service_api, name='detect_service_api'),
    path('api/services/<int:service_id>/api-docs/', views.service_api_docs, name='service_api_docs'),
    path('api/services/<int:service_id>/proxy/', views.generic_api_proxy, name='generic_api_proxy'),
    
    # Grafana panels
    path('grafana/', views.grafana_panels_view, name='grafana_panels'),
    path('grafana/<int:panel_id>/', views.grafana_panel_detail, name='grafana_panel_detail'),
    path('api/grafana/panels/', views.api_grafana_panels, name='api_grafana_panels'),
]
