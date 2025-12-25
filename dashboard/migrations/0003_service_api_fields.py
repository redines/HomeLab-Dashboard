# Generated manually for API integration fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_service_status_changed_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='api_url',
            field=models.URLField(blank=True, help_text='API endpoint URL for this service', max_length=500),
        ),
        migrations.AddField(
            model_name='service',
            name='api_key',
            field=models.CharField(blank=True, help_text='API key or token for authentication', max_length=500),
        ),
        migrations.AddField(
            model_name='service',
            name='api_username',
            field=models.CharField(blank=True, help_text='API username for authentication', max_length=255),
        ),
        migrations.AddField(
            model_name='service',
            name='api_password',
            field=models.CharField(blank=True, help_text='API password for authentication', max_length=255),
        ),
        migrations.AddField(
            model_name='service',
            name='api_type',
            field=models.CharField(blank=True, choices=[('qbittorrent', 'qBittorrent'), ('sonarr', 'Sonarr'), ('radarr', 'Radarr'), ('custom', 'Custom')], help_text='Type of API integration', max_length=50),
        ),
    ]
