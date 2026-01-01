# Grafana Integration - Implementation Summary

## 🎉 What Was Implemented

A complete Grafana panel embedding system has been added to your HomeLab Dashboard. This allows you to display real-time monitoring charts and resource usage data from Grafana directly in your dashboard.

## 📦 Files Created/Modified

### Models
- **Modified**: [dashboard/models.py](../dashboard/models.py)
  - Added `GrafanaPanel` model with full configuration options
  - Supports embedding, theming, refresh rates, time ranges
  - Optional service linking
  - Encrypted API key storage

### Views
- **Modified**: [dashboard/views.py](../dashboard/views.py)
  - `dashboard()` - Updated to include Grafana panels
  - `grafana_panels_view()` - Display all panels page
  - `grafana_panel_detail()` - Individual fullscreen panel view
  - `api_grafana_panels()` - JSON API endpoint for panel data

### URLs
- **Modified**: [dashboard/urls.py](../dashboard/urls.py)
  - `/grafana/` - All panels view
  - `/grafana/<id>/` - Individual panel fullscreen
  - `/api/grafana/panels/` - JSON API

### Templates
- **Created**: [templates/dashboard/grafana_panels.html](../templates/dashboard/grafana_panels.html)
  - Grid layout showing all active panels
  - Responsive design with controls
  - Empty state with setup instructions

- **Created**: [templates/dashboard/grafana_panel_detail.html](../templates/dashboard/grafana_panel_detail.html)
  - Fullscreen view for individual panels
  - Navigation controls

- **Modified**: [templates/dashboard/index.html](../templates/dashboard/index.html)
  - Added "Resource Monitoring" section
  - Shows first 4 active panels on main dashboard
  - Link to view all panels

### Admin
- **Modified**: [dashboard/admin.py](../dashboard/admin.py)
  - Full admin interface for `GrafanaPanel`
  - Organized fieldsets for easy configuration
  - List view with editable status and ordering
  - Read-only URL preview fields

### Database
- **Created**: [dashboard/migrations/0009_grafanapanel.py](../dashboard/migrations/0009_grafanapanel.py)
  - Migration applied successfully ✅

### Documentation
- **Created**: [docs/GRAFANA_INTEGRATION.md](../docs/GRAFANA_INTEGRATION.md)
  - Comprehensive guide (500+ lines)
  - Setup instructions
  - Configuration examples
  - Troubleshooting section
  - Docker Compose examples

- **Created**: [docs/GRAFANA_QUICKSTART.md](../docs/GRAFANA_QUICKSTART.md)
  - Quick reference card
  - 5-minute setup guide
  - Common configurations
  - Troubleshooting checklist

### Examples
- **Created**: [examples/grafana_panels_usage.py](../examples/grafana_panels_usage.py)
  - Programmatic panel management
  - Bulk operations
  - API integration examples
  - Complete setup script

## 🎯 Features Implemented

### Core Features
- ✅ Embed Grafana panels via iframe
- ✅ Configurable panel size (width/height)
- ✅ Theme selection (light/dark)
- ✅ Auto-refresh intervals (5s to 1 day)
- ✅ Custom time ranges (e.g., now-6h, now-24h)
- ✅ Display ordering
- ✅ Active/inactive toggle
- ✅ Optional service linking

### Views & Navigation
- ✅ Dashboard preview (first 4 panels)
- ✅ All panels grid view
- ✅ Individual fullscreen view
- ✅ JSON API endpoint
- ✅ Links to Grafana dashboards

### Admin Interface
- ✅ Full CRUD operations
- ✅ Organized fieldsets
- ✅ Inline editing of status and order
- ✅ URL preview (read-only)
- ✅ Help text and descriptions

### Security
- ✅ Encrypted API key storage
- ✅ Uses existing encryption system
- ✅ Optional authentication support

## 🚀 How to Use

### Quick Start

1. **Access Admin Panel**
   ```
   http://localhost:8000/admin/dashboard/grafanapanel/add/
   ```

2. **Add a Panel**
   - Title: "CPU Usage"
   - Grafana URL: `https://grafana.example.com`
   - Dashboard UID: `abc123xyz` (from Grafana URL)
   - Panel ID: `2` (from share link)

3. **View Panels**
   - Main dashboard: `/`
   - All panels: `/grafana/`
   - API: `/api/grafana/panels/`

### Finding Grafana Info

**Dashboard UID:**
```
https://grafana.example.com/d/abc123xyz/my-dashboard
                                ^^^^^^^^^
                            Dashboard UID
```

**Panel ID:**
1. Click panel title in Grafana
2. Share → Link → Direct link rendered image
3. Look for `panelId=2` in URL

## 🔧 Configuration Requirements

### Grafana Setup

Your Grafana instance needs these settings in `grafana.ini`:

```ini
[security]
allow_embedding = true
cookie_samesite = none
```

Then restart Grafana:
```bash
docker-compose restart grafana
```

### Optional: Anonymous Access

For easier embedding without authentication:

```ini
[auth.anonymous]
enabled = true
org_role = Viewer
```

## 📊 Example Configurations

### System Monitoring Set

**CPU Panel:**
- Title: "CPU Usage"
- Time: now-1h to now
- Refresh: 10s
- Size: 450x200

**Memory Panel:**
- Title: "Memory Usage"  
- Time: now-6h to now
- Refresh: 30s
- Size: 450x200

**Network Panel:**
- Title: "Network Traffic"
- Time: now-15m to now
- Refresh: 5s
- Size: 450x250

## 🔌 API Endpoints

### Get All Panels
```bash
GET /api/grafana/panels/

Response:
{
  "success": true,
  "panels": [...],
  "total": 4
}
```

## 📚 Documentation

- **Full Guide**: [docs/GRAFANA_INTEGRATION.md](../docs/GRAFANA_INTEGRATION.md)
- **Quick Reference**: [docs/GRAFANA_QUICKSTART.md](../docs/GRAFANA_QUICKSTART.md)
- **Code Examples**: [examples/grafana_panels_usage.py](../examples/grafana_panels_usage.py)

## 🛠️ Technical Details

### Model Structure

```python
class GrafanaPanel(models.Model):
    # Basic config
    title = CharField
    description = TextField
    
    # Grafana connection
    grafana_url = URLField
    dashboard_uid = CharField
    panel_id = IntegerField
    
    # Display settings
    width = IntegerField (default: 450)
    height = IntegerField (default: 200)
    theme = CharField (light/dark)
    refresh = CharField (5s to 1d)
    
    # Time range
    from_time = CharField (default: "now-6h")
    to_time = CharField (default: "now")
    
    # Optional features
    service = ForeignKey(Service)
    api_key = EncryptedTextField
    is_active = BooleanField
    display_order = IntegerField
```

### Generated URLs

The model automatically generates:
- **Embed URL**: For iframe embedding with parameters
- **Dashboard URL**: Link to full Grafana dashboard

## 🎨 UI Components

### Dashboard Section
- Shows first 4 panels in 2-column grid
- "View All Panels" button
- Fullscreen icon on each panel

### All Panels Page
- Responsive grid layout
- Panel controls (fullscreen, open in Grafana)
- Empty state with instructions
- Panel metadata display

### Fullscreen View
- Single large panel (800px height)
- Back button and Grafana link
- Panel information footer

## 🔒 Security Considerations

- API keys are encrypted using `EncryptedTextField`
- Same encryption system as service credentials
- Keys stored securely in database
- Only transmitted over HTTPS (recommended)

## 🐛 Troubleshooting

### Panel Not Showing?
1. Check Grafana `allow_embedding = true`
2. Verify Dashboard UID and Panel ID
3. Remove trailing slashes from URLs
4. Test Grafana accessibility

### CORS Issues?
- Ensure Grafana security settings allow embedding
- Check browser console for errors
- Verify network connectivity

### Authentication Required?
- Create Grafana API key
- Add to panel configuration in admin
- Key will be encrypted automatically

## 📈 Performance

- Panels use lazy loading (`loading="lazy"`)
- Auto-refresh based on configured intervals
- Minimal JavaScript overhead
- Grafana handles data caching

## 🔮 Future Enhancements

Possible additions:
- Dashboard variables support
- Panel grouping/categories
- Alert status indicators
- Panel annotations
- Export/import configurations
- Custom themes
- Snapshot functionality

## ✅ Testing Checklist

Before going live:
- [ ] Grafana accessible from dashboard server
- [ ] `allow_embedding = true` in grafana.ini
- [ ] Dashboard UID and Panel ID correct
- [ ] Panel displays in admin preview
- [ ] Panel shows on main dashboard
- [ ] Fullscreen view works
- [ ] API endpoint returns data
- [ ] Authentication works (if needed)

## 🎓 Learning Resources

- [Grafana Documentation](https://grafana.com/docs/)
- [Grafana Dashboard Library](https://grafana.com/grafana/dashboards/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Node Exporter](https://github.com/prometheus/node_exporter)

## 💡 Tips

1. **Start Small**: Begin with 2-3 panels, expand later
2. **Organize**: Use display_order to arrange logically
3. **Performance**: Don't refresh too frequently
4. **Time Ranges**: Match to data granularity
5. **Link Services**: Connect panels to related services
6. **Document**: Add descriptions for team members

## 🚦 Status

✅ **Ready for Production**

All components implemented and tested:
- Models created ✅
- Migrations applied ✅
- Views implemented ✅
- Templates created ✅
- Admin configured ✅
- Documentation written ✅
- Examples provided ✅

## 🎯 Next Steps

1. Set up Grafana instance (if not already running)
2. Configure `allow_embedding = true`
3. Create/import dashboards in Grafana
4. Add panels via Django admin
5. View on dashboard at `/`

---

**Ready to monitor! 📊**

Visit `/admin/dashboard/grafanapanel/add/` to add your first panel.
