from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('api/services/', views.api_services, name='api_services'),
    path('api/services/refresh/', views.refresh_services, name='refresh_services'),
    path('api/services/<int:service_id>/health/', views.check_service_health, name='check_health'),
]
