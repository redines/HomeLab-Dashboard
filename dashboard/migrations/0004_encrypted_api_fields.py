# Migration to convert API fields to encrypted fields

from django.db import migrations
import dashboard.utils.encryption


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_service_api_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='api_key',
            field=dashboard.utils.encryption.EncryptedTextField(blank=True, help_text='API key or token for authentication'),
        ),
        migrations.AlterField(
            model_name='service',
            name='api_username',
            field=dashboard.utils.encryption.EncryptedCharField(blank=True, help_text='API username for authentication', max_length=255),
        ),
        migrations.AlterField(
            model_name='service',
            name='api_password',
            field=dashboard.utils.encryption.EncryptedCharField(blank=True, help_text='API password for authentication', max_length=255),
        ),
    ]
