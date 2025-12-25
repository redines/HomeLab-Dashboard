// Dashboard JavaScript

// CSRF Token helper
function getCookie(name) {
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
}

const csrftoken = getCookie('csrftoken');

// Open service in new tab
function openService(url) {
    window.open(url, '_blank');
}

// Refresh services
async function refreshServices() {
    const loadingOverlay = document.getElementById('loading-overlay');
    const refreshBtn = document.getElementById('refresh-btn');
    
    try {
        // Show loading
        loadingOverlay.style.display = 'flex';
        refreshBtn.disabled = true;
        
        // Call refresh API
        const response = await fetch('/api/services/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show info message if in manual mode or Traefik unavailable
            if (data.info) {
                console.log('ℹ️ ' + data.info);
                // Only show alert if no services were synced and user might be expecting Traefik
                if (data.synced_services === 0 && data.traefik_configured) {
                    alert('ℹ️ ' + data.info);
                }
            }
            
            // Reload page to show updated services
            window.location.reload();
        } else {
            alert('Error refreshing services: ' + data.error);
        }
    } catch (error) {
        console.error('Error refreshing services:', error);
        alert('Failed to refresh services. Please try again.');
    } finally {
        loadingOverlay.style.display = 'none';
        refreshBtn.disabled = false;
    }
}

// Auto-refresh services periodically
let autoRefreshInterval = null;

function startAutoRefresh(intervalSeconds = 300) {
    // Clear existing interval
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    // Set new interval (default 5 minutes)
    autoRefreshInterval = setInterval(async () => {
        console.log('Auto-refreshing services...');
        await fetchServicesData();
    }, intervalSeconds * 1000);
}

// Fetch services data without page reload
async function fetchServicesData() {
    try {
        const response = await fetch('/api/services/');
        const data = await response.json();
        
        // Update stats
        updateStats(data);
        
        // Update service cards
        updateServiceCards(data.services);
        
        // Update last updated time
        const lastUpdated = document.getElementById('last-updated');
        if (lastUpdated) {
            lastUpdated.textContent = new Date(data.timestamp).toLocaleString();
        }
    } catch (error) {
        console.error('Error fetching services:', error);
    }
}

// Update statistics
function updateStats(data) {
    const totalServices = document.getElementById('total-services');
    const upServices = document.getElementById('up-services');
    const downServices = document.getElementById('down-services');
    
    if (totalServices) totalServices.textContent = data.total;
    
    const upCount = data.services.filter(s => s.status === 'up').length;
    const downCount = data.services.filter(s => s.status === 'down').length;
    
    if (upServices) upServices.textContent = upCount;
    if (downServices) downServices.textContent = downCount;
}

// Update service cards in the grid
function updateServiceCards(services) {
    services.forEach(service => {
        const card = document.querySelector(`[data-service-id="${service.id}"]`);
        if (!card) return;
        
        // Update status badge
        const statusBadge = card.querySelector('span[class*="status-"]');
        if (statusBadge) {
            // Remove old status classes
            statusBadge.className = statusBadge.className.replace(/bg-\w+\/20/g, '').replace(/text-\w+/g, '');
            
            // Add new status classes
            if (service.status === 'up') {
                statusBadge.className = 'px-3 py-1 rounded-xl text-xs font-semibold uppercase tracking-wide bg-success/20 text-success';
            } else if (service.status === 'down') {
                statusBadge.className = 'px-3 py-1 rounded-xl text-xs font-semibold uppercase tracking-wide bg-danger/20 text-danger';
            } else {
                statusBadge.className = 'px-3 py-1 rounded-xl text-xs font-semibold uppercase tracking-wide bg-warning/20 text-warning';
            }
            statusBadge.textContent = service.status.toUpperCase();
        }
        
        // Update card border color
        card.className = card.className.replace(/border-l-\w+/g, '');
        if (service.status === 'up') {
            card.classList.add('border-l-success');
        } else if (service.status === 'down') {
            card.classList.add('border-l-danger');
        } else {
            card.classList.add('border-l-warning');
        }
        
        // Update response time if available
        if (service.response_time) {
            const responseTimeEl = card.querySelector('.meta-item:last-child .meta-value');
            if (responseTimeEl) {
                responseTimeEl.textContent = `${service.response_time}ms`;
            }
        }
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Attach refresh button event
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshServices);
    }
    
    // Add Service Modal
    const addServiceBtn = document.getElementById('add-service-btn');
    const addServiceModal = document.getElementById('add-service-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const cancelModalBtn = document.getElementById('cancel-modal-btn');
    const addServiceForm = document.getElementById('add-service-form');
    
    if (addServiceBtn && addServiceModal) {
        addServiceBtn.addEventListener('click', () => {
            addServiceModal.style.display = 'flex';
            document.getElementById('service-name').focus();
        });
    }
    
    if (closeModalBtn && addServiceModal) {
        closeModalBtn.addEventListener('click', () => {
            addServiceModal.style.display = 'none';
            addServiceForm.reset();
            document.getElementById('form-error').classList.add('hidden');
        });
    }
    
    if (cancelModalBtn && addServiceModal) {
        cancelModalBtn.addEventListener('click', () => {
            addServiceModal.style.display = 'none';
            addServiceForm.reset();
            document.getElementById('form-error').classList.add('hidden');
        });
    }
    
    // Close modal on outside click
    if (addServiceModal) {
        addServiceModal.addEventListener('click', (e) => {
            if (e.target === addServiceModal) {
                addServiceModal.style.display = 'none';
                addServiceForm.reset();
                document.getElementById('form-error').classList.add('hidden');
            }
        });
    }
    
    // Handle form submission
    if (addServiceForm) {
        addServiceForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formError = document.getElementById('form-error');
            formError.classList.add('hidden');
            
            const formData = {
                name: document.getElementById('service-name').value.trim(),
                url: document.getElementById('service-url').value.trim(),
                description: document.getElementById('service-description').value.trim(),
                icon: document.getElementById('service-icon').value.trim(),
                service_type: document.getElementById('service-type').value,
                provider: document.getElementById('service-provider').value,
                tags: document.getElementById('service-tags').value.trim(),
            };
            
            try {
                const response = await fetch('/api/services/create/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                    },
                    body: JSON.stringify(formData),
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Close modal and reload page
                    addServiceModal.style.display = 'none';
                    addServiceForm.reset();
                    window.location.reload();
                } else {
                    formError.textContent = data.error || 'Failed to create service';
                    formError.classList.remove('hidden');
                }
            } catch (error) {
                console.error('Error creating service:', error);
                formError.textContent = 'Network error. Please try again.';
                formError.classList.remove('hidden');
            }
        });
    }
    
    // Auto-fetch updated data after page load (wait 2 seconds for health checks to complete)
    setTimeout(async () => {
        await fetchServicesData();
    }, 2000);
    
    // Poll for updates every 10 seconds for the first minute after page load
    let pollCount = 0;
    const pollInterval = setInterval(async () => {
        await fetchServicesData();
        pollCount++;
        
        // Stop polling after 6 iterations (60 seconds)
        if (pollCount >= 6) {
            clearInterval(pollInterval);
            console.log('Initial polling complete');
        }
    }, 10000);
    
    // Start auto-refresh (every 5 minutes)
    // Uncomment to enable auto-refresh
    // startAutoRefresh(300);
    
    console.log('HomeLab Dashboard initialized');
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Press 'R' to refresh (but not when typing in input fields)
    if (e.key === 'r' || e.key === 'R') {
        // Check if user is typing in an input/textarea/select element
        const activeElement = document.activeElement;
        const isTyping = activeElement && (
            activeElement.tagName === 'INPUT' ||
            activeElement.tagName === 'TEXTAREA' ||
            activeElement.tagName === 'SELECT' ||
            activeElement.isContentEditable
        );
        
        // Only trigger refresh if not typing and no modifier keys
        if (!isTyping && !e.ctrlKey && !e.metaKey && !e.altKey) {
            e.preventDefault();
            refreshServices();
        }
    }
});
