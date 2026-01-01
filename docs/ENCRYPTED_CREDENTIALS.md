# Encrypted Credentials Setup

## Overview

API credentials (username, password, API keys) are automatically encrypted before being stored in the database using industry-standard encryption (Fernet from the `cryptography` library).

**✨ Zero Configuration Required**: The application automatically generates and manages the encryption key for you!

## How It Works (Automatic)

### First Run

When you first start the application:

1. **Auto-Generation**: Application checks for `.encryption_key` file
2. **Key Creation**: If not found, generates a secure encryption key automatically
3. **Secure Storage**: Saves key to `.encryption_key` file with restrictive permissions (600)
4. **Ready to Use**: You can immediately start adding encrypted credentials!

### Subsequent Runs

- Application loads the existing key from `.encryption_key`
- All credentials are encrypted/decrypted using this key
- No manual configuration needed

## Quick Start

1. **Start your application** (that's it!)
   ```bash
   ./scripts/start.sh
   ```

2. **Configure credentials** through the web interface:
   - Go to any service detail page
   - Click **"🔑 Edit Credentials"**
   - Enter your API credentials
   - Click **"💾 Save Credentials"**

Your credentials are automatically encrypted! 🔒

## Advanced: Manual Key Management (Optional)

If you need to use a specific encryption key (e.g., for production clusters or key rotation):

### Option 1: Environment Variable

```bash
# Generate a key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Set it
export FIELD_ENCRYPTION_KEY=your_custom_key_here
```

### Option 2: .env File

```bash
# Generate a key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Add to .env
echo "FIELD_ENCRYPTION_KEY=your_generated_key" >> .env
```

## Backup & Recovery

### Backing Up Your Key

**Important**: Back up the `.encryption_key` file if you want to preserve access to encrypted credentials.

```bash
# Backup the key
cp .encryption_key .encryption_key.backup

# Or include in your backup script
tar -czf homelab-backup.tar.gz db.sqlite3 .encryption_key
```

### If You Lose Your Key

- ❌ **Encrypted credentials cannot be recovered** (this is by design)
- ✅ **Application continues working** - generates a new key automatically
- ✅ **Simple solution** - Re-enter credentials through the web interface

This is acceptable because:
- Credentials can be re-entered easily via the web UI
- No data loss (just need to re-configure API access)
- Security is maintained (old encrypted data stays encrypted)

## Setup Instructions

### 1. Generate an Encryption Key

Run this command to generate a secure encryption key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

This will output something like:
```
Abc123XYZ789SecureKeyHere==
```

### 2. Add the Key to Your Environment

#### Development (.env file)

Create or edit `.env` file in the project root:

```bash
# Field encryption key for sensitive data (required in production)
FIELD_ENCRYPTION_KEY=your_generated_key_here
```

#### Production (Environment Variables)

Set the environment variable in your deployment:

**Docker Compose:**
```yaml
environment:
  - FIELD_ENCRYPTION_KEY=your_generated_key_here
```

**Docker Run:**
```bash
docker run -e FIELD_ENCRYPTION_KEY=your_generated_key_here ...
```

**System Environment:**
```bash
export FIELD_ENCRYPTION_KEY=your_generated_key_here
```

### 3. Restart the Application

After setting the key, restart your application:

```bash
# Development
./scripts/start.sh

# Docker
docker-compose restart
```

## How It Works

### Encryption Process

1. **User Input**: When you save API credentials through the web interface
2. **Encryption**: Credentials are encrypted using Fernet encryption before saving to database
3. **Storage**: Only encrypted data is stored in the database
4. **Decryption**: When loading credentials, they are automatically decrypted using your encryption key

### Security Features

- ✅ **Industry Standard**: Uses Fernet (symmetric encryption) from the `cryptography` library
- ✅ **Key Management**: Encryption key stored separately from database (in environment)
- ✅ **Transparent**: Automatic encryption/decryption - works seamlessly in your code
- ✅ **Secure by Default**: If credentials exist but decryption fails, returns empty string

### Fields That Are Encrypted

The following fields are encrypted:
- `api_username` - API username
- `api_password` - API password
- `api_key` - API key/token

The following fields are NOT encrypted (they're not sensitive):
- `api_url` - API endpoint URL
- `api_type` - Type of API integration

## Using the Web Interface

### Configure Credentials

1. Navigate to a service detail page
2. Click **"🔑 Edit Credentials"** button
3. Fill in the form:
   - **API Type**: Select service type (qBittorrent, Sonarr, etc.)
   - **API URL**: Full URL to the API endpoint
   - **Username**: Your API username
   - **Password**: Your API password
4. Click **"💾 Save Credentials"**

Your credentials are automatically encrypted before being saved!

### View Credentials

- Passwords are masked with `●●●●●●●●` in the display
- Only you can decrypt them using your encryption key
- The encrypted form cannot be reversed without the key

## Important Security Notes

### 🔒 Understanding the Security Model

**This implementation prioritizes ease of use while providing database-level obscurity:**

- ✅ **Credentials are NOT stored in plain text** in the database
- ✅ **Automatic key management** - no manual configuration required
- ✅ **Perfect for homelab environments** where ease of use is important
- ⚠️ **Key is stored on filesystem** - protect your server file access
- ℹ️ **If key is lost, credentials can be re-entered** through the web UI

**Trade-offs:**
- **Easier**: No manual key management needed
- **Acceptable**: Losing the key means re-entering credentials (not losing data)
- **Secure Enough**: Protects against casual database inspection
- **Not Enterprise-Grade**: For enterprise use, implement external key management (KMS, Vault, etc.)

### 📋 File Locations

- **Encryption Key**: `.encryption_key` (auto-generated, gitignored)
- **Encrypted Data**: `db.sqlite3` (credentials stored encrypted)
- **Backup Both**: Include both files in your backups to preserve access

### 🆘 Key Loss Scenarios

**Scenario 1: Deleted .encryption_key file**
- Application generates new key automatically
- Old credentials are unreadable (but harmless)
- Solution: Re-enter credentials via web UI

**Scenario 2: Backup/Restore without .encryption_key**
- Restored credentials are encrypted with old key
- Current application has different key
- Solution: Either restore `.encryption_key` from backup, or re-enter credentials

**Scenario 3: Docker container recreated**
- Use Docker volumes to persist `.encryption_key`
- Or set `FIELD_ENCRYPTION_KEY` environment variable
- Otherwise credentials need to be re-entered

## Docker Deployment

### Persisting the Encryption Key

**Option 1: Volume Mount (Recommended)**
```yaml
services:
  web:
    volumes:
      - ./data:/app/data
      - ./.encryption_key:/app/.encryption_key
```

**Option 2: Environment Variable**
```yaml
services:
  web:
    environment:
      - FIELD_ENCRYPTION_KEY=${FIELD_ENCRYPTION_KEY}
```

Then set in your `.env` file or generate a key once:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy the output to your .env file
```

### 🔒 Protecting Your Encryption Key

Your encryption key provides access to decrypt credentials:

- ✅ **DO**: Keep `.encryption_key` file with restrictive permissions (600)
- ✅ **DO**: Include in backups alongside your database
- ✅ **DO**: Use Docker volumes to persist the key
- ✅ **DO**: Consider environment variables for production
- ❌ **DON'T**: Commit the key to version control (already in .gitignore)
- ❌ **DON'T**: Share the key in plain text messages
- ℹ️ **NOTE**: If lost, credentials can be re-entered (no permanent data loss)

### 📋 Key Rotation (Advanced)

If you need to change your encryption key:

1. **Export existing credentials** (optional - for automatic migration)
2. **Generate new key** or set new `FIELD_ENCRYPTION_KEY`
3. **Delete or replace `.encryption_key` file**
4. **Re-enter credentials** through web UI

**Helper script for automated rotation** (optional):
```python
from dashboard.models import Service

# Get all services with credentials
services = Service.objects.exclude(api_username='').exclude(api_password='')

# Store temporarily
creds = [(s.id, s.api_username, s.api_password) for s in services]

# Now: Replace key, restart application

# Re-save with new key
for sid, username, password in creds:
    s = Service.objects.get(id=sid)
    s.api_username = username
    s.api_password = password
    s.save()
```

### 🆘 Lost Your Key?

**Good News**: Since credentials can be re-entered easily:

1. Application automatically generates a new key
2. Old encrypted data becomes unreadable (but stays in database safely)
3. Simply re-configure credentials through the web interface
4. No permanent data loss - just need to re-enter API credentials

## Troubleshooting

### Warning: "Generated new encryption key"

**Cause**: First run or `.encryption_key` file not found

**Solution**: This is normal! The application automatically created a key for you. No action needed.

### Error: "Could not save encryption key to file"

**Cause**: Permission issues or read-only filesystem

**Solution**: 
1. Check directory permissions: `chmod 755 /path/to/app`
2. Or set `FIELD_ENCRYPTION_KEY` environment variable manually
3. Check disk space

### Error: "Could not read encryption key file"

**Cause**: File corruption or permission issues

**Solution**: 
1. Delete `.encryption_key` - app will generate new one
2. Re-enter credentials through web UI
3. Or restore from backup if you have one

### Error: "Decryption failed"

**Cause**: Encryption key changed or data encrypted with different key

**Solution**: 
1. If you have backup of old `.encryption_key`, restore it
2. Otherwise, re-enter credentials through web UI
3. Old encrypted data is safe - just unreadable with current key

### Credentials Show as Empty After Server Migration

**Cause**: `.encryption_key` file not migrated with database

**Solution**:
1. Copy `.encryption_key` from old server to new server
2. Or re-enter credentials (they'll be encrypted with new key)

## For Developers

### Custom Encrypted Fields

The implementation uses custom Django fields in `dashboard/encryption.py`:

```python
from dashboard.utils.encryption import EncryptedCharField, EncryptedTextField

class MyModel(models.Model):
    secret = EncryptedCharField(max_length=255, blank=True)
    big_secret = EncryptedTextField(blank=True)
```

### Testing Encryption

```python
from dashboard.models import Service

# Create service with credentials
service = Service.objects.create(
    name="Test",
    url="http://example.com",
    api_username="admin",
    api_password="secret123"
)

# Check database - should see encrypted text
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT api_username, api_password FROM dashboard_service WHERE id = %s", [service.id])
row = cursor.fetchone()
print(row)  # Should show 'gAAAAA...' (encrypted)

# Load from database - should see decrypted text
service = Service.objects.get(id=service.id)
print(service.api_username)  # Should show 'admin' (decrypted)
```

## Migration Applied

The following migration was applied to enable encryption:
- `0004_encrypted_api_fields.py` - Converts `api_username`, `api_password`, and `api_key` to encrypted fields

Existing unencrypted data will be automatically encrypted on first save after migration.
