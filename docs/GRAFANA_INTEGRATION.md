# Grafana Integration Guide

## Overview

The HomeLab Dashboard now supports embedding Grafana panels to display real-time resource monitoring data from your servers and services. This integration allows you to visualize metrics like CPU usage, memory consumption, disk I/O, network traffic, and more directly within your dashboard.

## Features

- **Embed Grafana Panels**: Display any Grafana panel directly in your dashboard
- **Flexible Configuration**: Customize panel size, theme, refresh rate, and time range
- **Service Linking**: Optionally link panels to specific services for context
- **Multiple Views**: 
  - Dashboard preview (first 4 panels)
  - Full panels page with all active panels
  - Individual fullscreen panel view
- **Auto-refresh**: Panels automatically refresh based on configured intervals
- **Responsive Design**: Panels adapt to different screen sizes

## Prerequisites

1. **Grafana Instance**: You need a running Grafana instance (local or remote)
2. **Dashboard Access**: Access to create and view Grafana dashboards
3. **Panel IDs**: Know how to find dashboard UIDs and panel IDs in Grafana

## Setup Instructions

### 1. Find Your Dashboard UID

The Dashboard UID is found in your Grafana dashboard URL:

```
https://grafana.example.com/d/abc123xyz/my-dashboard
                                  ^^^^^^^^^
                            This is the Dashboard UID
```

### 2. Find Your Panel ID

To get a panel ID:

1. In Grafana, click on a panel title
2. Select "Share" → "Link"
3. Check the "Direct link rendered image" option
4. Look for `panelId=` in the URL

Example URL:
```
https://grafana.example.com/render/d-solo/abc123xyz/my-dashboard?panelId=2
                                                                         ^
                                                                    Panel ID
```

### 3. Add Panel via Django Admin

1. Go to your Django admin panel: `/admin/`
2. Navigate to **Dashboard** → **Grafana Panels**
3. Click **"Add Grafana Panel"**
4. Fill in the required fields:

#### Required Fields

- **Title**: Display name for the panel (e.g., "CPU Usage")
- **Grafana URL**: Base URL of your Grafana instance (e.g., `https://grafana.example.com`)
- **Dashboard UID**: The UID from step 1 (e.g., `abc123xyz`)
- **Panel ID**: The numeric ID from step 2 (e.g., `2`)

#### Optional Fields

- **Description**: Brief explanation of what the panel shows
- **Service**: Link to a specific service in your dashboard
- **Width**: Panel width in pixels (default: 450)
- **Height**: Panel height in pixels (default: 200)
- **Theme**: Light or Dark (default: Dark)
- **Refresh**: Auto-refresh interval (default: 1 minute)
- **From Time**: Start of time range (default: `now-6h`)
- **To Time**: End of time range (default: `now`)
- **Display Order**: Order panels appear (lower numbers first)
- **Is Active**: Whether to display this panel

## Configuration Examples

### Example 1: CPU Usage Panel

```
Title: Server CPU Usage
Description: Real-time CPU utilization across all cores
Grafana URL: https://grafana.homelab.local
Dashboard UID: system-metrics
Panel ID: 2
Width: 450
Height: 200
Theme: Dark
Refresh: 10s
From Time: now-1h
To Time: now
Is Active: Yes
Display Order: 1
```

### Example 2: Memory Usage Panel

```
Title: Memory Consumption
Description: RAM usage and available memory
Grafana URL: https://grafana.homelab.local
Dashboard UID: system-metrics
Panel ID: 4
Width: 450
Height: 200
Theme: Dark
Refresh: 30s
From Time: now-6h
To Time: now
Is Active: Yes
Display Order: 2
```

### Example 3: Network Traffic Panel

```
Title: Network I/O
Description: Inbound and outbound network traffic
Grafana URL: https://grafana.homelab.local
Dashboard UID: network-stats
Panel ID: 1
Width: 450
Height: 250
Theme: Dark
Refresh: 5s
From Time: now-15m
To Time: now
Is Active: Yes
Display Order: 3
```

## Time Range Syntax

Common time range values:

- `now-5m` - Last 5 minutes
- `now-15m` - Last 15 minutes
- `now-30m` - Last 30 minutes
- `now-1h` - Last 1 hour
- `now-3h` - Last 3 hours
- `now-6h` - Last 6 hours
- `now-12h` - Last 12 hours
- `now-24h` - Last 24 hours
- `now-2d` - Last 2 days
- `now-7d` - Last 7 days
- `now-30d` - Last 30 days
- `now-90d` - Last 90 days

## Refresh Intervals

Available refresh intervals:

- `5s` - 5 seconds
- `10s` - 10 seconds
- `30s` - 30 seconds
- `1m` - 1 minute
- `5m` - 5 minutes
- `15m` - 15 minutes
- `30m` - 30 minutes
- `1h` - 1 hour
- `2h` - 2 hours
- `1d` - 1 day

## Accessing Grafana Panels

### Main Dashboard
The main dashboard (`/`) shows up to 4 Grafana panels in a "Resource Monitoring" section (if any panels are configured and active).

### All Panels Page
Visit `/grafana/` to see all active Grafana panels in a grid layout.

### Individual Panel View
Click the fullscreen icon on any panel to view it in fullscreen mode.

### API Endpoint
Access panel data via JSON: `/api/grafana/panels/`

## Authentication

### Anonymous Access
If your Grafana instance allows anonymous access, panels will work without authentication.

### API Key Authentication
If authentication is required:

1. In Grafana, create a Service Account or API Key with "Viewer" permissions
2. In the Django admin, add the API key to the panel's "API Key" field
3. The key will be encrypted and used for authenticated requests

## Troubleshooting

### Panel Not Displaying

**Check these common issues:**

1. **CORS Configuration**: Ensure Grafana allows iframe embedding
   - Edit `grafana.ini`:
     ```ini
     [security]
     allow_embedding = true
     cookie_samesite = none
     ```

2. **URL Format**: Verify the Grafana URL doesn't have trailing slashes
   - ✅ Correct: `https://grafana.example.com`
   - ❌ Wrong: `https://grafana.example.com/`

3. **Dashboard/Panel IDs**: Double-check the Dashboard UID and Panel ID
   - Use the "Share" function in Grafana to verify

4. **Network Access**: Ensure the dashboard server can reach Grafana
   - Test with: `curl https://grafana.example.com`

5. **Authentication**: If using authentication, verify the API key is valid
   - Test in Grafana API documentation

### Panels Loading Slowly

- Reduce the time range (e.g., change from `now-24h` to `now-6h`)
- Increase the refresh interval
- Optimize Grafana queries in the source dashboard
- Check network latency between servers

### Panel Shows "Dashboard not found"

- Verify the Dashboard UID is correct
- Ensure the dashboard is not deleted in Grafana
- Check dashboard permissions in Grafana

## Advanced: Setting Up Grafana Stack

If you haven't set up Grafana yet, here's a quick guide:

### Docker Compose Example

```yaml
version: '3'
services:
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ALLOW_EMBEDDING=true
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer
    volumes:
      - grafana-storage:/var/lib/grafana
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-storage:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    restart: unless-stopped

volumes:
  grafana-storage:
  prometheus-storage:
```

### Basic Prometheus Configuration

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

### After Setup

1. Access Grafana at `http://localhost:3000`
2. Default credentials: admin/admin
3. Add Prometheus as a data source
4. Import dashboards (e.g., Node Exporter Full - ID: 1860)
5. Create panels and get their IDs for embedding

## Best Practices

1. **Organize Panels**: Use display_order to arrange panels logically
2. **Meaningful Titles**: Use clear, descriptive titles
3. **Appropriate Refresh**: Don't refresh too frequently (causes load)
4. **Time Ranges**: Match time ranges to the data granularity
5. **Service Linking**: Link panels to relevant services for context
6. **Performance**: Monitor dashboard load times and adjust accordingly

## API Usage

### Get All Panels (JSON)

```bash
curl http://localhost:8000/api/grafana/panels/
```

Response:
```json
{
  "success": true,
  "panels": [
    {
      "id": 1,
      "title": "CPU Usage",
      "description": "Real-time CPU utilization",
      "embed_url": "https://grafana.example.com/d-solo/...",
      "dashboard_url": "https://grafana.example.com/d/...",
      "width": 450,
      "height": 200,
      "theme": "dark",
      "refresh": "1m",
      "service": {
        "id": 5,
        "name": "Docker Host",
        "status": "up"
      }
    }
  ],
  "total": 1
}
```

## Support & Resources

- **Grafana Documentation**: https://grafana.com/docs/
- **Grafana Dashboard Library**: https://grafana.com/grafana/dashboards/
- **Prometheus Documentation**: https://prometheus.io/docs/
- **Node Exporter Metrics**: https://github.com/prometheus/node_exporter

## Future Enhancements

Planned features for future releases:

- [ ] Variable support for dashboard parameters
- [ ] Alert status indicators
- [ ] Panel annotations
- [ ] Custom themes
- [ ] Panel grouping/categories
- [ ] Export/import panel configurations
- [ ] Panel snapshots
- [ ] Historical data comparison

---

**Note**: Make sure to run database migrations after setting up Grafana integration:

```bash
python manage.py migrate
```
