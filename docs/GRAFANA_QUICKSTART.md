# Grafana Panels - Quick Setup Guide

## 🎯 Quick Start (5 minutes)

### Step 1: Get Panel Information from Grafana

```
Dashboard URL: https://grafana.example.com/d/abc123xyz/my-dashboard
                                            ^^^^^^^^^
                                        Dashboard UID

Panel Share Link: ...?panelId=2
                              ^
                          Panel ID
```

### Step 2: Add Panel in Django Admin

1. Go to `/admin/dashboard/grafanapanel/add/`
2. Fill in:
   - Title: "CPU Usage" *(what to display)*
   - Grafana URL: `https://grafana.example.com` *(no trailing slash)*
   - Dashboard UID: `abc123xyz`
   - Panel ID: `2`
3. Click "Save"

### Step 3: View Your Panel

- Main Dashboard: `/` (shows first 4 panels)
- All Panels: `/grafana/`
- API: `/api/grafana/panels/`

---

## 📋 Common Settings

### Time Ranges
```
now-15m    (last 15 minutes)
now-1h     (last hour)
now-6h     (last 6 hours)
now-24h    (last day)
now-7d     (last week)
```

### Refresh Rates
```
10s   (real-time monitoring)
1m    (general use)
5m    (slow-changing data)
```

### Panel Sizes
```
CPU/Memory:  450x200
Network:     450x250
Dashboard:   450x300
Fullscreen:  Use fullscreen button
```

---

## 🔧 Grafana Configuration

### Enable Embedding
Edit `grafana.ini`:
```ini
[security]
allow_embedding = true
cookie_samesite = none
```

Restart Grafana:
```bash
docker-compose restart grafana
```

### Anonymous Access (Optional)
```ini
[auth.anonymous]
enabled = true
org_role = Viewer
```

---

## 🐛 Troubleshooting

### Panel not showing?
✅ Check Grafana allows embedding (see above)  
✅ Verify Dashboard UID and Panel ID  
✅ Remove trailing slash from Grafana URL  
✅ Test network access to Grafana  

### "Dashboard not found"?
✅ Confirm dashboard exists in Grafana  
✅ Check dashboard permissions  
✅ Verify UID is correct (not the name)  

### Slow loading?
✅ Reduce time range (e.g., 6h instead of 24h)  
✅ Increase refresh interval  
✅ Optimize Grafana queries  

---

## 📊 Example Panel Configurations

### System Resources Panel Set

**CPU Usage**
```
Title: CPU Usage
Dashboard UID: system-metrics
Panel ID: 2
Time: now-1h → now
Refresh: 10s
```

**Memory Usage**
```
Title: Memory Usage
Dashboard UID: system-metrics
Panel ID: 4
Time: now-1h → now
Refresh: 10s
```

**Disk I/O**
```
Title: Disk I/O
Dashboard UID: system-metrics
Panel ID: 6
Time: now-6h → now
Refresh: 30s
```

**Network Traffic**
```
Title: Network Traffic
Dashboard UID: system-metrics
Panel ID: 8
Time: now-15m → now
Refresh: 5s
```

---

## 🔐 With Authentication

If Grafana requires authentication:

1. Create API Key in Grafana:
   - Configuration → API Keys → Add API Key
   - Role: Viewer
   - Copy the key

2. In Django Admin:
   - Open the panel
   - Paste key in "API Key" field
   - Save

---

## 🚀 Full Grafana Stack Setup

Quick Docker Compose:

```yaml
version: '3'
services:
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ALLOW_EMBEDDING=true
    volumes:
      - grafana-storage:/var/lib/grafana

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"

volumes:
  grafana-storage:
```

Start with: `docker-compose up -d`

---

## 📚 More Help

- Full guide: `docs/GRAFANA_INTEGRATION.md`
- Grafana docs: https://grafana.com/docs/
- Dashboard library: https://grafana.com/grafana/dashboards/

---

**Ready to go! 🎉**

Add your first panel at: `/admin/dashboard/grafanapanel/add/`
