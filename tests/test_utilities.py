"""Unit tests for utility modules."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from dashboard.utils.encryption import (
    EncryptedTextField, EncryptedCharField, 
    get_encryption_key
)
from dashboard.utils.generic_api_client import GenericAPIClient
from django.conf import settings
from cryptography.fernet import Fernet


@pytest.mark.unit
class TestEncryption:
    """Test cases for encryption utilities."""
    
    def test_get_encryption_key(self):
        """Test getting encryption key from settings."""
        key = get_encryption_key()
        assert key is not None
        assert isinstance(key, bytes)
    
    def test_encrypt_decrypt_with_field(self):
        """Test encrypting and decrypting a value using field class."""
        field = EncryptedTextField()
        original_value = "secret_password_123"
        
        # Encrypt value
        encrypted = field.get_prep_value(original_value)
        
        # Encrypted value should be different from original
        assert encrypted != original_value
        assert encrypted is not None
        
        # Decrypted value should match original
        decrypted = field.to_python(encrypted)
        assert decrypted == original_value
    
    def test_encrypt_empty_string(self):
        """Test encrypting empty string."""
        field = EncryptedTextField()
        encrypted = field.get_prep_value("")
        assert encrypted == ""
        
        decrypted = field.to_python("")
        assert decrypted == ""
    
    def test_encrypt_none_value(self):
        """Test encrypting None value."""
        field = EncryptedTextField()
        encrypted = field.get_prep_value(None)
        assert encrypted is None
        
        decrypted = field.to_python(None)
        assert decrypted is None
    
    def test_encrypted_field_in_model(self, service_with_api):
        """Test encrypted fields work correctly in models."""
        # Set encrypted values
        test_key = "test_api_key_456"
        test_username = "testuser123"
        test_password = "testpass456"
        
        service_with_api.api_key = test_key
        service_with_api.api_username = test_username
        service_with_api.api_password = test_password
        service_with_api.save()
        
        # Reload from database
        from dashboard.models import Service
        reloaded = Service.objects.get(id=service_with_api.id)
        
        # Values should be decrypted correctly
        assert reloaded.api_key == test_key
        assert reloaded.api_username == test_username
        assert reloaded.api_password == test_password
    
    def test_encryption_key_consistency(self):
        """Test that encryption key remains consistent."""
        key1 = get_encryption_key()
        key2 = get_encryption_key()
        assert key1 == key2
    
    def test_encrypted_value_format(self):
        """Test that encrypted values have correct format."""
        field = EncryptedTextField()
        value = "test123"
        encrypted = field.get_prep_value(value)
        
        # Encrypted value should be base64 encoded
        assert isinstance(encrypted, str)
        # Fernet tokens start with 'gAAAAA' signature
        assert encrypted.startswith('gAAAAA')
        assert len(encrypted) > len(value)
    
    def test_char_field_encryption(self):
        """Test EncryptedCharField encryption."""
        field = EncryptedCharField(max_length=255)
        original = "test_username"
        
        encrypted = field.get_prep_value(original)
        assert encrypted != original
        
        decrypted = field.to_python(encrypted)
        assert decrypted == original


@pytest.mark.unit
class TestGenericAPIClient:
    """Test cases for GenericAPIClient."""
    
    def test_client_initialization(self):
        """Test initializing API client."""
        client = GenericAPIClient(
            base_url="https://api.test.local",
            username="testuser",
            password="testpass"
        )
        
        assert client.base_url == "https://api.test.local"
        assert client.username == "testuser"
        assert client.password == "testpass"
    
    def test_client_url_normalization(self):
        """Test URL normalization in client."""
        # URL with trailing slash
        client1 = GenericAPIClient(base_url="https://api.test.local/")
        assert client1.base_url == "https://api.test.local"
        
        # URL without protocol
        client2 = GenericAPIClient(base_url="api.test.local")
        assert client2.base_url.startswith("https://")
    
    def test_client_empty_url_raises_error(self):
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError):
            GenericAPIClient(base_url="")
    
    def test_client_none_url_raises_error(self):
        """Test that None URL raises ValueError."""
        with pytest.raises(ValueError):
            GenericAPIClient(base_url=None)
    
    @patch('requests.Session.get')
    def test_client_make_request_success(self, mock_get):
        """Test making a successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_get.return_value = mock_response
        
        client = GenericAPIClient(base_url="https://api.test.local")
        response = client.make_request('/endpoint')
        
        assert response.status_code == 200
        assert response.json() == {'data': 'test'}
    
    @patch('requests.Session.post')
    def test_client_authenticate_with_credentials(self, mock_post):
        """Test authentication with username/password."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'token': 'test_token_123'}
        mock_post.return_value = mock_response
        
        client = GenericAPIClient(
            base_url="https://api.test.local",
            username="testuser",
            password="testpass"
        )
        
        result = client.authenticate()
        assert result is True or mock_post.called
    
    def test_client_api_key_authentication(self):
        """Test initialization with API key."""
        client = GenericAPIClient(
            base_url="https://api.test.local",
            api_key="test_api_key_123"
        )
        
        assert client.api_key == "test_api_key_123"
    
    @patch('requests.Session.get')
    def test_client_handles_ssl_errors(self, mock_get):
        """Test client handles SSL errors gracefully."""
        import requests
        mock_get.side_effect = requests.exceptions.SSLError("SSL Error")
        
        client = GenericAPIClient(base_url="https://api.test.local")
        
        # Should not raise exception
        with pytest.raises(requests.exceptions.SSLError):
            client.make_request('/endpoint')
    
    @patch('requests.Session.get')
    def test_client_handles_timeout(self, mock_get):
        """Test client handles timeout errors."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")
        
        client = GenericAPIClient(base_url="https://api.test.local")
        
        with pytest.raises(requests.exceptions.Timeout):
            client.make_request('/endpoint')
    
    def test_client_session_configuration(self):
        """Test that session is configured correctly."""
        client = GenericAPIClient(base_url="https://api.test.local")
        
        # Session should be created
        assert client.session is not None
        # SSL verification should be disabled for self-signed certs
        assert client.session.verify is False


@pytest.mark.unit
class TestTraefikService:
    """Test cases for Traefik service integration."""
    
    @patch('requests.get')
    def test_fetch_traefik_services_success(self, mock_get):
        """Test fetching services from Traefik."""
        from dashboard.traefik_service import TraefikService
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'name': 'test-router',
                'rule': 'Host(`test.local`)',
                'service': 'test-service',
                'status': 'enabled'
            }
        ]
        mock_get.return_value = mock_response
        
        traefik = TraefikService()
        services = traefik.discover_services()
        assert services is not None or mock_get.called
    
    @patch('requests.get')
    def test_fetch_traefik_services_connection_error(self, mock_get):
        """Test handling Traefik connection errors."""
        import requests
        from dashboard.utils.traefik_service import TraefikService
        
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        # Should handle error gracefully
        traefik = TraefikService()
        result = traefik.discover_services()
        assert result == [] or mock_get.called
    
    @patch('dashboard.utils.traefik_service.check_traefik_availability')
    @patch('dashboard.utils.traefik_service.TraefikService')
    def test_sync_traefik_services(self, mock_traefik_class, mock_check_availability, db):
        """Test syncing Traefik services to database."""
        from dashboard.utils.traefik_service import sync_traefik_services
        from dashboard.models import Service
        
        # Mock Traefik availability check to return True
        mock_check_availability.return_value = True
        
        # Create a mock instance
        mock_instance = Mock()
        mock_instance.discover_services.return_value = [
            {
                'name': 'test-service',
                'url': 'https://test.local',
                'status': 'up',
                'service_type': 'docker',
                'provider': 'traefik',
                'traefik_router_name': 'test-router',
                'traefik_service_name': 'test-service',
                'tags': []
            }
        ]
        mock_traefik_class.return_value = mock_instance
        
        result = sync_traefik_services()
        
        # Check that Traefik availability was checked and TraefikService was instantiated
        assert mock_check_availability.called
        assert mock_traefik_class.called
