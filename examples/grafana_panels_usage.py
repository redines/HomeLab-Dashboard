"""
Example: Working with Grafana Panels programmatically

This example shows how to create, query, and manage Grafana panels
through Django's ORM and API endpoints.
"""

from dashboard.models import GrafanaPanel, Service


# ============================================
# Creating Grafana Panels
# ============================================

def create_system_monitoring_panels():
    """Create a set of system monitoring panels."""
    
    # Create CPU usage panel
    cpu_panel = GrafanaPanel.objects.create(
        title="CPU Usage",
        description="Real-time CPU utilization across all cores",
        grafana_url="https://grafana.homelab.local",
        dashboard_uid="system-metrics",
        panel_id=2,
        width=450,
        height=200,
        theme="dark",
        refresh="10s",
        from_time="now-1h",
        to_time="now",
        is_active=True,
        display_order=1
    )
    
    # Create Memory usage panel
    memory_panel = GrafanaPanel.objects.create(
        title="Memory Usage",
        description="RAM consumption and available memory",
        grafana_url="https://grafana.homelab.local",
        dashboard_uid="system-metrics",
        panel_id=4,
        width=450,
        height=200,
        theme="dark",
        refresh="30s",
        from_time="now-6h",
        to_time="now",
        is_active=True,
        display_order=2
    )
    
    # Create Disk I/O panel
    disk_panel = GrafanaPanel.objects.create(
        title="Disk I/O",
        description="Read/write operations per second",
        grafana_url="https://grafana.homelab.local",
        dashboard_uid="system-metrics",
        panel_id=6,
        width=450,
        height=250,
        theme="dark",
        refresh="1m",
        from_time="now-6h",
        to_time="now",
        is_active=True,
        display_order=3
    )
    
    # Create Network traffic panel
    network_panel = GrafanaPanel.objects.create(
        title="Network Traffic",
        description="Inbound and outbound network traffic",
        grafana_url="https://grafana.homelab.local",
        dashboard_uid="network-stats",
        panel_id=1,
        width=450,
        height=250,
        theme="dark",
        refresh="5s",
        from_time="now-15m",
        to_time="now",
        is_active=True,
        display_order=4
    )
    
    print(f"Created {GrafanaPanel.objects.count()} panels")
    return [cpu_panel, memory_panel, disk_panel, network_panel]


# ============================================
# Linking Panels to Services
# ============================================

def link_panel_to_service(panel_title, service_name):
    """Link a Grafana panel to a specific service."""
    try:
        panel = GrafanaPanel.objects.get(title=panel_title)
        service = Service.objects.get(name=service_name)
        
        panel.service = service
        panel.save()
        
        print(f"Linked '{panel_title}' to service '{service_name}'")
        return True
    except (GrafanaPanel.DoesNotExist, Service.DoesNotExist) as e:
        print(f"Error: {e}")
        return False


# Example usage
def setup_service_specific_panels():
    """Create panels for specific services."""
    
    # Get Docker host service
    try:
        docker_host = Service.objects.get(name="Docker Host")
        
        # Create Docker-specific monitoring panel
        docker_panel = GrafanaPanel.objects.create(
            title="Docker Container Stats",
            description="CPU and memory usage of all containers",
            grafana_url="https://grafana.homelab.local",
            dashboard_uid="docker-monitoring",
            panel_id=10,
            service=docker_host,  # Link directly
            theme="dark",
            refresh="10s",
            from_time="now-1h",
            to_time="now",
            is_active=True,
            display_order=5
        )
        print(f"Created panel linked to {docker_host.name}")
        
    except Service.DoesNotExist:
        print("Docker Host service not found")


# ============================================
# Querying Panels
# ============================================

def get_active_panels():
    """Get all active panels ordered by display order."""
    panels = GrafanaPanel.objects.filter(is_active=True).order_by('display_order')
    
    for panel in panels:
        print(f"{panel.display_order}. {panel.title}")
        print(f"   URL: {panel.get_embed_url()}")
        print(f"   Refresh: {panel.get_refresh_display()}")
        if panel.service:
            print(f"   Service: {panel.service.name}")
        print()
    
    return panels


def get_panels_for_service(service_name):
    """Get all panels linked to a specific service."""
    try:
        service = Service.objects.get(name=service_name)
        panels = GrafanaPanel.objects.filter(service=service, is_active=True)
        
        print(f"Panels for {service_name}:")
        for panel in panels:
            print(f"  - {panel.title}")
        
        return panels
    except Service.DoesNotExist:
        print(f"Service '{service_name}' not found")
        return []


# ============================================
# Updating Panels
# ============================================

def update_panel_time_range(panel_title, from_time, to_time):
    """Update the time range for a panel."""
    try:
        panel = GrafanaPanel.objects.get(title=panel_title)
        panel.from_time = from_time
        panel.to_time = to_time
        panel.save()
        
        print(f"Updated '{panel_title}' time range: {from_time} to {to_time}")
        return True
    except GrafanaPanel.DoesNotExist:
        print(f"Panel '{panel_title}' not found")
        return False


def update_refresh_rate(panel_title, refresh_interval):
    """Update the refresh rate for a panel."""
    try:
        panel = GrafanaPanel.objects.get(title=panel_title)
        panel.refresh = refresh_interval
        panel.save()
        
        print(f"Updated '{panel_title}' refresh rate to {refresh_interval}")
        return True
    except GrafanaPanel.DoesNotExist:
        print(f"Panel '{panel_title}' not found")
        return False


def toggle_panel_status(panel_title):
    """Toggle a panel's active status."""
    try:
        panel = GrafanaPanel.objects.get(title=panel_title)
        panel.is_active = not panel.is_active
        panel.save()
        
        status = "activated" if panel.is_active else "deactivated"
        print(f"{status.capitalize()} panel: {panel_title}")
        return True
    except GrafanaPanel.DoesNotExist:
        print(f"Panel '{panel_title}' not found")
        return False


# ============================================
# Bulk Operations
# ============================================

def deactivate_all_panels():
    """Deactivate all panels."""
    count = GrafanaPanel.objects.filter(is_active=True).update(is_active=False)
    print(f"Deactivated {count} panels")
    return count


def activate_all_panels():
    """Activate all panels."""
    count = GrafanaPanel.objects.filter(is_active=False).update(is_active=True)
    print(f"Activated {count} panels")
    return count


def update_all_time_ranges(from_time, to_time):
    """Update time range for all panels."""
    count = GrafanaPanel.objects.update(from_time=from_time, to_time=to_time)
    print(f"Updated time range for {count} panels")
    return count


def change_theme_for_all(theme='dark'):
    """Change theme for all panels."""
    count = GrafanaPanel.objects.update(theme=theme)
    print(f"Updated theme to '{theme}' for {count} panels")
    return count


# ============================================
# API Integration Examples
# ============================================

def fetch_panels_via_api():
    """Example of fetching panels via the API endpoint."""
    import requests
    
    response = requests.get('http://localhost:8000/api/grafana/panels/')
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total']} panels")
        
        for panel in data['panels']:
            print(f"\n{panel['title']}")
            print(f"  Embed URL: {panel['embed_url']}")
            print(f"  Theme: {panel['theme']}")
            if 'service' in panel:
                print(f"  Service: {panel['service']['name']} ({panel['service']['status']})")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        return None


# ============================================
# Statistics and Reports
# ============================================

def get_panel_statistics():
    """Get statistics about configured panels."""
    total = GrafanaPanel.objects.count()
    active = GrafanaPanel.objects.filter(is_active=True).count()
    inactive = total - active
    linked = GrafanaPanel.objects.filter(service__isnull=False).count()
    
    print("Panel Statistics:")
    print(f"  Total Panels: {total}")
    print(f"  Active: {active}")
    print(f"  Inactive: {inactive}")
    print(f"  Linked to Services: {linked}")
    print(f"  Standalone: {total - linked}")
    
    # Group by theme
    by_theme = {}
    for panel in GrafanaPanel.objects.all():
        by_theme[panel.theme] = by_theme.get(panel.theme, 0) + 1
    
    print("\nBy Theme:")
    for theme, count in by_theme.items():
        print(f"  {theme}: {count}")
    
    return {
        'total': total,
        'active': active,
        'inactive': inactive,
        'linked': linked,
        'by_theme': by_theme
    }


# ============================================
# Example: Complete Setup Script
# ============================================

def setup_complete_monitoring():
    """
    Complete setup script for monitoring panels.
    Run this to set up a full monitoring dashboard.
    """
    print("Setting up monitoring panels...")
    
    # Create standard system panels
    panels = create_system_monitoring_panels()
    print(f"✓ Created {len(panels)} system monitoring panels")
    
    # Link to services if they exist
    if Service.objects.filter(name="Docker Host").exists():
        setup_service_specific_panels()
        print("✓ Created service-specific panels")
    
    # Display statistics
    print("\n" + "="*50)
    get_panel_statistics()
    print("="*50)
    
    print("\n✅ Setup complete!")
    print("Visit /grafana/ to view your panels")


# ============================================
# Run Examples
# ============================================

if __name__ == "__main__":
    # Uncomment the function you want to run:
    
    # Setup complete monitoring
    # setup_complete_monitoring()
    
    # Get all active panels
    # get_active_panels()
    
    # Update a panel's time range
    # update_panel_time_range("CPU Usage", "now-24h", "now")
    
    # Get statistics
    # get_panel_statistics()
    
    # Fetch via API
    # fetch_panels_via_api()
    
    pass
