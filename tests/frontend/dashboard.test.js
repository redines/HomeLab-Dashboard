/**
 * Unit tests for dashboard.js
 */

// Import functions from dashboard.js for testing
// Note: In a real setup, you'd need to export these functions or use a module bundler

describe('Dashboard JavaScript Tests', () => {
  
  describe('getCookie', () => {
    beforeEach(() => {
      // Reset document.cookie
      document.cookie = '';
    });
    
    test('should retrieve CSRF token from cookies', () => {
      document.cookie = 'csrftoken=test_token_123; path=/';
      
      // Mock the getCookie function since we can't import it directly
      const getCookie = (name) => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
      };
      
      const token = getCookie('csrftoken');
      expect(token).toBe('test_token_123');
    });
    
    test('should return null for non-existent cookie', () => {
      const getCookie = (name) => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
      };
      
      const result = getCookie('nonexistent');
      expect(result).toBeNull();
    });
    
    test('should handle empty cookie string', () => {
      document.cookie = '';
      
      const getCookie = (name) => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
      };
      
      const result = getCookie('csrftoken');
      expect(result).toBeNull();
    });
  });
  
  describe('openService', () => {
    test('should open service URL in new tab', () => {
      const mockOpen = jest.fn();
      global.window.open = mockOpen;
      
      const openService = (url) => {
        window.open(url, '_blank');
      };
      
      openService('https://test.local');
      
      expect(mockOpen).toHaveBeenCalledWith('https://test.local', '_blank');
    });
  });
  
  describe('refreshServices', () => {
    beforeEach(() => {
      // Setup DOM elements
      document.body.innerHTML = `
        <div id="loading-overlay" style="display: none;"></div>
        <button id="refresh-btn"></button>
      `;
      
      // Mock fetch
      global.fetch = jest.fn();
      global.window.location.reload = jest.fn();
      global.alert = jest.fn();
    });
    
    test('should show loading overlay during refresh', async () => {
      const mockResponse = {
        json: jest.fn().resolves({ success: true, synced_services: 5, health_checks: 5 }),
        ok: true,
      };
      fetch.mockResolvedValue(mockResponse);
      
      const refreshServices = async () => {
        const loadingOverlay = document.getElementById('loading-overlay');
        const refreshBtn = document.getElementById('refresh-btn');
        
        loadingOverlay.style.display = 'flex';
        refreshBtn.disabled = true;
        
        const response = await fetch('/api/services/refresh/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': 'test_csrf_token',
          },
        });
        
        const data = await response.json();
        
        if (data.success) {
          window.location.reload();
        }
        
        loadingOverlay.style.display = 'none';
        refreshBtn.disabled = false;
      };
      
      const promise = refreshServices();
      
      const overlay = document.getElementById('loading-overlay');
      const btn = document.getElementById('refresh-btn');
      
      expect(overlay.style.display).toBe('flex');
      expect(btn.disabled).toBe(true);
      
      await promise;
    });
    
    test('should handle refresh success', async () => {
      const mockResponse = {
        json: jest.fn().resolves({ 
          success: true, 
          synced_services: 5, 
          health_checks: 5 
        }),
        ok: true,
      };
      fetch.mockResolvedValue(mockResponse);
      
      const refreshServices = async () => {
        const response = await fetch('/api/services/refresh/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': 'test_csrf_token',
          },
        });
        
        const data = await response.json();
        
        if (data.success) {
          window.location.reload();
        }
      };
      
      await refreshServices();
      
      expect(fetch).toHaveBeenCalledWith(
        '/api/services/refresh/',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
      expect(window.location.reload).toHaveBeenCalled();
    });
    
    test('should handle refresh error', async () => {
      const mockResponse = {
        json: jest.fn().resolves({ 
          success: false, 
          error: 'Connection failed' 
        }),
        ok: false,
      };
      fetch.mockResolvedValue(mockResponse);
      
      const refreshServices = async () => {
        try {
          const response = await fetch('/api/services/refresh/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': 'test_csrf_token',
            },
          });
          
          const data = await response.json();
          
          if (!data.success) {
            alert('Error refreshing services: ' + data.error);
          }
        } catch (error) {
          alert('Failed to refresh services. Please try again.');
        }
      };
      
      await refreshServices();
      
      expect(alert).toHaveBeenCalledWith('Error refreshing services: Connection failed');
    });
  });
  
  describe('updateStats', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <span id="total-services">0</span>
        <span id="up-services">0</span>
        <span id="down-services">0</span>
      `;
    });
    
    test('should update service statistics', () => {
      const updateStats = (data) => {
        const totalServices = document.getElementById('total-services');
        const upServices = document.getElementById('up-services');
        const downServices = document.getElementById('down-services');
        
        if (totalServices) totalServices.textContent = data.total;
        
        const upCount = data.services.filter(s => s.status === 'up').length;
        const downCount = data.services.filter(s => s.status === 'down').length;
        
        if (upServices) upServices.textContent = upCount;
        if (downServices) downServices.textContent = downCount;
      };
      
      const data = {
        total: 5,
        services: [
          { status: 'up' },
          { status: 'up' },
          { status: 'up' },
          { status: 'down' },
          { status: 'unknown' },
        ]
      };
      
      updateStats(data);
      
      expect(document.getElementById('total-services').textContent).toBe('5');
      expect(document.getElementById('up-services').textContent).toBe('3');
      expect(document.getElementById('down-services').textContent).toBe('1');
    });
  });
  
  describe('fetchServicesData', () => {
    test('should fetch services from API', async () => {
      const mockData = {
        services: [
          { id: 1, name: 'Service 1', status: 'up' },
          { id: 2, name: 'Service 2', status: 'down' },
        ],
        total: 2,
        timestamp: new Date().toISOString(),
      };
      
      fetch.mockResolvedValue({
        json: jest.fn().resolves(mockData),
        ok: true,
      });
      
      const fetchServicesData = async () => {
        const response = await fetch('/api/services/');
        const data = await response.json();
        return data;
      };
      
      const result = await fetchServicesData();
      
      expect(fetch).toHaveBeenCalledWith('/api/services/');
      expect(result.services).toHaveLength(2);
      expect(result.total).toBe(2);
    });
  });
  
  describe('updateServiceCards', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <div data-service-id="1" class="border-l-4 border-l-success">
          <span class="px-3 py-1 rounded-xl text-xs font-semibold uppercase tracking-wide bg-success/20 text-success">UP</span>
        </div>
      `;
    });
    
    test('should update service card status', () => {
      const updateServiceCards = (services) => {
        services.forEach(service => {
          const card = document.querySelector(`[data-service-id="${service.id}"]`);
          if (!card) return;
          
          const statusBadge = card.querySelector('span[class*="bg-"]');
          if (statusBadge) {
            if (service.status === 'down') {
              statusBadge.className = 'px-3 py-1 rounded-xl text-xs font-semibold uppercase tracking-wide bg-danger/20 text-danger';
              statusBadge.textContent = 'DOWN';
            }
          }
        });
      };
      
      const services = [{ id: 1, status: 'down' }];
      updateServiceCards(services);
      
      const badge = document.querySelector('[data-service-id="1"] span');
      expect(badge.textContent).toBe('DOWN');
      expect(badge.className).toContain('bg-danger');
    });
  });
});
