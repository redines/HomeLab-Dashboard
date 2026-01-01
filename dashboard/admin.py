from django.contrib import admin
from .models import Service, HealthCheck, GrafanaPanel


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'status', 'service_type', 'api_type', 'provider', 'last_checked', 'response_time']
    list_filter = ['status', 'service_type', 'api_type', 'provider']
    search_fields = ['name', 'url', 'description']
    readonly_fields = ['created_at', 'updated_at', 'last_checked', 'status_changed_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'url', 'status', 'service_type', 'provider', 'description', 'icon', 'tags')
        }),
        ('Health & Monitoring', {
            'fields': ('last_checked', 'status_changed_at', 'response_time', 'uptime_percentage')
        }),
        ('API Integration', {
            'fields': ('api_type', 'api_url', 'api_username', 'api_password', 'api_key'),
            'classes': ('collapse',),
        }),
        ('Traefik Configuration', {
            'fields': ('traefik_router_name', 'traefik_service_name'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
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


@admin.register(GrafanaPanel)
class GrafanaPanelAdmin(admin.ModelAdmin):
    list_display = ['title', 'service', 'grafana_url', 'panel_id', 'theme', 'refresh', 'is_active', 'display_order']
    list_filter = ['is_active', 'theme', 'refresh', 'service']
    search_fields = ['title', 'description', 'dashboard_uid']
    list_editable = ['is_active', 'display_order']
    readonly_fields = ['created_at', 'updated_at', 'get_embed_url', 'get_dashboard_url']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'service', 'is_active', 'display_order')
        }),
        ('Grafana Configuration', {
            'fields': ('grafana_url', 'dashboard_uid', 'panel_id', 'api_key'),
            'description': 'Configure connection to your Grafana instance. Find the dashboard UID in the URL when viewing a dashboard in Grafana.'
        }),
        ('Display Settings', {
            'fields': ('width', 'height', 'theme', 'refresh'),
            'description': 'Control how the panel appears in the dashboard.'
        }),
        ('Time Range', {
            'fields': ('from_time', 'to_time'),
            'description': 'Set the time range for the panel data. Examples: now-6h, now-24h, now-7d, now-30d'
        }),
        ('URLs (Read-only)', {
            'fields': ('get_embed_url', 'get_dashboard_url'),
            'classes': ('collapse',),
            'description': 'Generated URLs for embedding and linking to Grafana.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_embed_url(self, obj):
        """Display the generated embed URL."""
        if obj.id:
            return obj.get_embed_url()
        return "Save the panel first to generate URL"
    get_embed_url.short_description = "Embed URL"
    
    def get_dashboard_url(self, obj):
        """Display the dashboard URL."""
        if obj.id:
            return obj.get_dashboard_url()
        return "Save the panel first to generate URL"
    get_dashboard_url.short_description = "Dashboard URL"

