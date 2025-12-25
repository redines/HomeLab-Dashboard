from django.contrib import admin
from .models import Service, HealthCheck


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'status', 'service_type', 'provider', 'last_checked', 'response_time']
    list_filter = ['status', 'service_type', 'provider']
    search_fields = ['name', 'url', 'description']
    readonly_fields = ['created_at', 'updated_at', 'last_checked']
    
    actions = ['check_health']
    
    def check_health(self, request, queryset):
        for service in queryset:
            service.check_health()
        self.message_user(request, f"Health check completed for {queryset.count()} services.")
    check_health.short_description = "Check health status"


@admin.register(HealthCheck)
class HealthCheckAdmin(admin.ModelAdmin):
    list_display = ['service', 'status', 'response_time', 'checked_at']
    list_filter = ['status', 'checked_at']
    search_fields = ['service__name']
    readonly_fields = ['checked_at']
