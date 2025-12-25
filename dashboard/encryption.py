"""Custom encrypted fields for storing sensitive data."""

from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import os


def get_encryption_key():
    """Get or generate encryption key from settings."""
    key = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
    
    if not key:
        # Try to get from environment (fallback)
        key = os.environ.get('FIELD_ENCRYPTION_KEY')
    
    if not key:
        # This should not happen as settings.py handles key generation
        # But provide a fallback just in case
        from cryptography.fernet import Fernet
        key = Fernet.generate_key().decode()
        import warnings
        warnings.warn(
            "FIELD_ENCRYPTION_KEY not available from settings. Using temporary key. "
            "This should not happen in normal operation.",
            RuntimeWarning
        )
    
    # Ensure key is bytes
    if isinstance(key, str):
        key = key.encode()
    
    return key


class EncryptedTextField(models.TextField):
    """TextField that encrypts data before saving to database."""
    
    description = "Encrypted text field"
    
    def __init__(self, *args, **kwargs):
        # Remove max_length as TextField doesn't use it, but keep it for compatibility
        kwargs.pop('max_length', None)
        super().__init__(*args, **kwargs)
    
    def get_prep_value(self, value):
        """Encrypt the value before saving to database."""
        if value is None or value == '':
            return value
        
        # Don't encrypt if already encrypted (starts with 'gAAAAA' which is Fernet signature)
        if isinstance(value, str) and value.startswith('gAAAAA'):
            return value
        
        try:
            key = get_encryption_key()
            f = Fernet(key)
            
            # Ensure value is bytes
            if isinstance(value, str):
                value = value.encode('utf-8')
            
            encrypted = f.encrypt(value)
            return encrypted.decode('utf-8')
        except Exception as e:
            # If encryption fails, log and return None to avoid storing unencrypted data
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Encryption failed: {e}")
            raise
    
    def from_db_value(self, value, expression, connection):
        """Decrypt the value when loading from database."""
        return self.to_python(value)
    
    def to_python(self, value):
        """Decrypt the value."""
        if value is None or value == '':
            return value
        
        # If it's already a Python string and not encrypted, return it
        if isinstance(value, str) and not value.startswith('gAAAAA'):
            return value
        
        try:
            key = get_encryption_key()
            f = Fernet(key)
            
            # Ensure value is bytes
            if isinstance(value, str):
                value = value.encode('utf-8')
            
            decrypted = f.decrypt(value)
            return decrypted.decode('utf-8')
        except Exception as e:
            # If decryption fails, return empty string
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Decryption failed for value, returning empty string: {e}")
            return ''


class EncryptedCharField(models.CharField):
    """CharField that encrypts data before saving to database."""
    
    description = "Encrypted char field"
    
    def get_prep_value(self, value):
        """Encrypt the value before saving to database."""
        if value is None or value == '':
            return value
        
        # Don't encrypt if already encrypted
        if isinstance(value, str) and value.startswith('gAAAAA'):
            return value
        
        try:
            key = get_encryption_key()
            f = Fernet(key)
            
            # Ensure value is bytes
            if isinstance(value, str):
                value = value.encode('utf-8')
            
            encrypted = f.encrypt(value)
            return encrypted.decode('utf-8')
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Encryption failed: {e}")
            raise
    
    def from_db_value(self, value, expression, connection):
        """Decrypt the value when loading from database."""
        return self.to_python(value)
    
    def to_python(self, value):
        """Decrypt the value."""
        if value is None or value == '':
            return value
        
        # If it's already a Python string and not encrypted, return it
        if isinstance(value, str) and not value.startswith('gAAAAA'):
            return value
        
        try:
            key = get_encryption_key()
            f = Fernet(key)
            
            # Ensure value is bytes
            if isinstance(value, str):
                value = value.encode('utf-8')
            
            decrypted = f.decrypt(value)
            return decrypted.decode('utf-8')
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Decryption failed for value, returning empty string: {e}")
            return ''
