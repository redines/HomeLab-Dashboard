from django.apps import AppConfig
import threading
import time
import logging

logger = logging.getLogger(__name__)


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    
    def ready(self):
        """Run when Django app is ready."""
        # Only run in the main process (not in reloader)
        import sys
        if 'runserver' not in sys.argv:
            return
            
        # Avoid running twice in development (Django's autoreload spawns two processes)
        import os
        if os.environ.get('RUN_MAIN') != 'true':
            return
        
        # Import here to avoid AppRegistryNotReady error
        from dashboard.utils.traefik_service import sync_traefik_services
        from django.conf import settings
        
        # Start background sync thread
        sync_interval = getattr(settings, 'SERVICE_REFRESH_INTERVAL', 30)
        
        def periodic_sync():
            """Background thread to periodically sync services."""
            # Wait a bit before first sync to let Django fully initialize
            time.sleep(2)
            
            logger.info("Running initial service sync on startup...")
            try:
                count = sync_traefik_services()
                logger.info(f"Initial sync completed: {count} services synced")
            except Exception as e:
                logger.error(f"Error during initial sync: {e}")
            
            # Continue with periodic syncs
            while True:
                try:
                    time.sleep(sync_interval)
                    logger.info("Running periodic service sync...")
                    count = sync_traefik_services()
                    logger.info(f"Periodic sync completed: {count} services synced")
                except Exception as e:
                    logger.error(f"Error during periodic sync: {e}")
        
        # Start daemon thread (will stop when main process stops)
        sync_thread = threading.Thread(target=periodic_sync, daemon=True)
        sync_thread.start()
        logger.info(f"Started periodic service sync (every {sync_interval} seconds)")
