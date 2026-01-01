from django.core.management.base import BaseCommand
from dashboard.utils.traefik_service import sync_traefik_services


class Command(BaseCommand):
    help = 'Sync services from Traefik API'

    def handle(self, *args, **options):
        self.stdout.write('Syncing services from Traefik...')
        
        try:
            count = sync_traefik_services()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully synced {count} services')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error syncing services: {e}')
            )
