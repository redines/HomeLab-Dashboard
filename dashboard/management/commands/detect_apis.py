"""
Management command to detect or re-detect APIs for services.
"""
from django.core.management.base import BaseCommand
from dashboard.utils.traefik_service import sync_traefik_services


class Command(BaseCommand):
    help = 'Detect or re-detect APIs for all services'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-detection even for services with already detected APIs',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        if force:
            self.stdout.write(self.style.WARNING('Forcing API re-detection for all services...'))
        else:
            self.stdout.write(self.style.SUCCESS('Detecting APIs for new services...'))
        
        try:
            count = sync_traefik_services(force_api_detection=force)
            
            if count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Successfully synced {count} services')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('No services were synced')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error: {str(e)}')
            )
            raise
