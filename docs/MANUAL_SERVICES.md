# Manual Service Management

The HomeLab Dashboard automatically detects if Traefik is available and seamlessly switches between auto-discovery and manual modes.

## Overview

The application automatically operates in one of these modes based on Traefik availability:

1. **Auto-Discovery Mode** - Traefik URL is configured and responding → services are automatically discovered
2. **Manual Mode** - Traefik URL is not configured or not responding → use manual service management
3. **Hybrid Mode** - Both auto-discovered and manual services coexist

**No configuration required!** The app automatically detects which mode to use.

## Configuration

### Automatic Mode Detection (Default)

By default, the application automatically detects if Traefik is available:

- **If `TRAEFIK_API_URL` is empty or not set** → Manual mode automatically activated
- **If `TRAEFIK_API_URL` is set but Traefik is not responding** → Gracefully falls back to manual mode
- **If `TRAEFIK_API_URL` is set and Traefik responds** → Auto-discovery mode activated

No manual enable/disable needed!

### Manual-Only Mode

To use manual-only mode, simply leave the Traefik URL empty in your `.env` file:

```bash
TRAEFIK_API_URL=
```

Or don't set it at all. The app will automatically use manual mode.

### Auto-Discovery Mode

To enable Traefik auto-discovery, just set the URL:

```bash
TRAEFIK_API_URL=http://traefik:8080/api
TRAEFIK_API_USERNAME=your_username  # Optional
TRAEFIK_API_PASSWORD=your_password  # Optional
```

The app will automatically detect if Traefik is responding and use it.

## Adding Services Manually

### Through the Web UI

1. Click the **"➕ Add Service"** button in the header (or press **'R'** to refresh services)
2. Fill in the service details:
   - **Service Name** (required) - e.g., "Plex", "Google", "GitHub"
   - **Service URL** (required) - Flexible format:
     - Domain: `plex.example.com`
     - IP with port: `192.168.1.100:8080`
     - Full URL: `https://service.com`
     - Protocol auto-added: `https://` is added automatically if not specified
     - **HTTP fallback**: If HTTPS fails, HTTP is tried automatically
   - **Description** (optional) - Brief description of the service
   - **Icon** (optional) - An emoji to represent the service (e.g., 🎬)
   - **Service Type** - Choose from:
     - Docker
     - Kubernetes
     - Virtual Machine
     - Bare Metal
     - External Service (for services outside your homelab)
     - Other
   - **Provider** - Choose from:
     - **Local** - Services running in your homelab
     - **External** - Internet services outside your homelab
   - **Tags** (optional) - Comma-separated tags (e.g., "media, streaming, movies")

3. Click **"Add Service"**
4. The service will be added and its health will be checked immediately

### Keyboard Shortcuts

- **Press 'R'** - Refresh all services (when not typing in a field)

### Service Types

- **External Service**: Use this for publicly accessible services like Google, GitHub, AWS Console, etc.
- **Docker/Kubernetes/VM/Bare Metal**: Use these for services running in your homelab

## Editing and Deleting Services

### Edit a Service

1. Click on a service card to view its details
2. If the service is manually added, you'll see **"✏️ Edit"** and **"🗑️ Delete"** buttons
3. Click **"✏️ Edit"** to modify the service details
4. Make your changes and click **"Update Service"**

### Delete a Service

1. Go to the service detail page
2. Click **"🗑️ Delete"**
3. Confirm the deletion

**Note**: Only manually added services can be edited or deleted. Services discovered from Traefik cannot be manually edited or deleted.

## Examples

### Adding a Homelab Service

```
Name: Plex Media Server
URL: plex.yourdomain.com  (https:// will be added automatically)
Description: Personal media streaming server
Icon: 🎬
Service Type: Docker
Provider: Local
Tags: media, streaming, entertainment
```

### Adding an External Service

```
Name: GitHub
URL: github.com  (https:// will be added automatically)
Description: Code repository and collaboration platform
Icon: 🐙
Service Type: External Service
Provider: External
Tags: development, git, code
```

### Adding a Local Network Service with IP and Port

```
Name: Home Assistant
URL: 192.168.1.100:8123  (https:// tried first, falls back to http:// if needed)
Description: Home automation hub
Icon: 🏠
Service Type: Docker
Provider: Local
Tags: automation, iot, smart-home
```

## Health Checks

All services (both manual and Traefik-discovered) are regularly checked for availability:

- **Up** (✅) - Service is responding (status codes: 2xx, 3xx, 401, 403, 405)
- **Down** (❌) - Service is not responding
- **Unknown** (⚠️) - Service has not been checked yet

The dashboard considers several HTTP status codes as "up":
- 200-299: Success
- 300-399: Redirects (service is responding)
- 401: Unauthorized (service is up, needs authentication)
- 403: Forbidden (service is up, access denied)
- 405: Method Not Allowed (service is up, doesn't accept GET)

### Smart Protocol Detection

When adding a service, the dashboard automatically handles protocol selection:

1. **Default**: `https://` is added if no protocol is specified
2. **HTTPS First**: Always tries HTTPS first (secure by default)
3. **HTTP Fallback**: If HTTPS fails with connection error, automatically tries HTTP
4. **Auto-Update**: If HTTP works, the service URL is updated to use HTTP
5. **Logging**: All protocol changes are logged for transparency

**Example:**
- You add: `192.168.1.100:8080`
- System tries: `https://192.168.1.100:8080`
- If it fails, tries: `http://192.168.1.100:8080`
- If HTTP works: URL updated to `http://192.168.1.100:8080`

## API Integration

Manual services support the same API integration features as Traefik-discovered services:

1. Navigate to the service detail page
2. Click **"🔑 Configure Credentials"**
3. Enter API credentials if the service has an API
4. Use the API dashboard to interact with the service

### API Detection Throttling

To reduce unnecessary network traffic and log spam, the dashboard implements smart API detection:

- Services are probed for API availability on first sync
- After **5 failed detection attempts**, probing is throttled
- Throttled services are rechecked every **5 minutes**
- Pressing "Refresh Services" respects throttling (use `--force` flag to override)
- Successfully detecting an API resets the counter

## Mixed Environment

You can use both Traefik auto-discovery and manual services simultaneously:

1. Leave `TRAEFIK_ENABLED=True`
2. Add manual services through the UI
3. Both types of services will appear in the dashboard
4. Manually added services will have a **"📝 Manually Added"** badge

## Troubleshooting

### Traefik Not Responding

If you see: "ℹ️ Traefik is configured but not responding. Health checks performed. Using manual service management."

This means:
- `TRAEFIK_API_URL` is set in your configuration
- But the dashboard cannot connect to the Traefik API
- **The app automatically uses manual mode**

Solutions:
1. Check that Traefik is running
2. Verify `TRAEFIK_API_URL` is correct
3. Check authentication credentials if required
4. Or simply leave `TRAEFIK_API_URL` empty to always use manual mode

### Service Shows as Down

If a service shows as "Down" but you know it's running:

1. Check the URL is correct
2. Verify network connectivity
3. Check if the service requires authentication
4. Look at the logs for detailed error messages
5. **Note**: The system automatically tries HTTP if HTTPS fails

### URL Format Issues

The dashboard is flexible with URL formats:
- ✅ `service.com` - Works! Protocol added automatically
- ✅ `192.168.1.100:8080` - Works! IP addresses with ports supported
- ✅ `http://service.local` - Works! Explicit protocol respected
- ✅ `https://service.com` - Works! HTTPS explicitly specified

## Recent Improvements (December 2025)

### Smart Protocol Detection
- Automatically adds `https://` if no protocol specified
- Falls back to `http://` if HTTPS connection fails
- Updates service URL automatically to working protocol
- Logs all protocol changes for transparency

### Flexible URL Input
- Accepts domain names, IP addresses, and ports
- No need to type `http://` or `https://`
- Works with local network addresses
- Validation happens on the backend

### API Detection Throttling
- Reduces network traffic for services without APIs
- After 5 failed attempts, waits 5 minutes before retrying
- Prevents log spam
- Manual refresh with `--force` flag bypasses throttling

### Provider Type Update
- Changed from "Manual" to "Local" for better clarity
- "Local" = services in your homelab
- "External" = services on the internet
- Automatic backward compatibility for existing services

### Keyboard Shortcuts
- Press 'R' to refresh all services
- Only works when not typing in input fields
- Provides quick access without mouse clicks

### Cannot Edit or Delete a Service

Only manually added services can be edited or deleted. Services discovered from Traefik are managed by Traefik and cannot be manually modified.

## Migration from Traefik-Only Setup
The app now automatically handles Traefik availability. If you're upgrading:

1. **No changes needed** - the app automatically detects Traefik
2. Remove old `TRAEFIK_ENABLED` variable if you have it (no longer needed)
3. Keep `TRAEFIK_API_URL` set if you use Traefik
4. Leave `TRAEFIK_API_URL` empty if you don't use Traefik

The app will automatically do the right thing!
4. Or keep existing Traefik-discovered services (they'll remain in the database)

## Database Migration

If upgrading from an older version, run:

```bash
python manage.py migrate
```

This will add the new `is_manual` field and update the provider choices.
