# Quick Start: API Credentials

## Super Simple Setup ✨

Your HomeLab Dashboard automatically handles encryption for you!

### 1. Start the Application

```bash
./start.sh
```

That's it! The application automatically:
- Generates an encryption key on first run
- Saves it securely to `.encryption_key` file
- Uses it to encrypt all API credentials

### 2. Add Credentials

1. Open any service detail page
2. Click **"🔑 Edit Credentials"**
3. Fill in your API details
4. Click **"💾 Save Credentials"**

Your credentials are automatically encrypted! 🔒

## What Gets Encrypted?

- ✅ API Usernames
- ✅ API Passwords  
- ✅ API Keys/Tokens

## What Happens Behind the Scenes?

### First Run
```
Application starts → Checks for .encryption_key → Not found → 
Generates secure key → Saves to file → Ready to use!
```

### Subsequent Runs
```
Application starts → Checks for .encryption_key → Found → 
Loads key → Ready to use!
```

### Saving Credentials
```
User enters password → Application encrypts with key → 
Saves encrypted data to database → Nobody can read it directly!
```

### Loading Credentials
```
Application loads from database → Decrypts with key → 
Uses decrypted credentials for API calls → Works seamlessly!
```

## Important Files

- `.encryption_key` - Your encryption key (auto-generated, gitignored)
- `db.sqlite3` - Your database (contains encrypted credentials)

**Both are important** - back them up together!

## Backups

### Include These Files

```bash
# Simple backup
tar -czf homelab-backup.tar.gz db.sqlite3 .encryption_key

# Or use your preferred backup tool
```

### Docker Volumes

```yaml
volumes:
  - ./data:/app/data
  - ./.encryption_key:/app/.encryption_key  # Important!
```

## What If I Lose the Key?

**Don't worry!** 

1. Application generates a new key automatically
2. Old credentials become unreadable (but stay in database safely)
3. Simply re-enter your credentials through the web UI
4. Everything works again!

**Why this is okay:**
- Credentials are easy to re-enter (just a web form)
- No permanent data loss (service info is preserved)
- Still protects against database inspection
- Much simpler than manual key management

## Security Level

This implementation provides:

✅ **Database-level obscurity** - Credentials not readable in plain text  
✅ **Zero configuration** - Works out of the box  
✅ **Easy recovery** - Just re-enter credentials if needed  
✅ **Perfect for homelabs** - Great balance of security and usability  

Not suitable for:
❌ Highly sensitive enterprise data requiring HSM/KMS  
❌ Compliance requirements (SOC2, HIPAA, etc.)  
❌ Multi-tenant systems with strict isolation  

**For homelabs**: This is perfect! 🎯

## Advanced: Custom Key (Optional)

Want to use your own key? Set an environment variable:

```bash
# Generate a key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Set it
export FIELD_ENCRYPTION_KEY=your_key_here

# Or in .env file
echo "FIELD_ENCRYPTION_KEY=your_key_here" >> .env
```

The application will use your custom key instead of generating one.

## Questions?

See [ENCRYPTED_CREDENTIALS.md](ENCRYPTED_CREDENTIALS.md) for detailed documentation.
