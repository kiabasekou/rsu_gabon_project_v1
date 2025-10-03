from django.db import migrations, models
import django.core.validators

class Migration(migrations.Migration):
    dependencies = [
        ('identity_app', '0013_add_employment_fields'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='personidentity',
            name='phone_number_alt',
            field=models.CharField(
                max_length=20,
                blank=True,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        regex=r'^\+241[0-9]{8}$',
                        message='Format: +241XXXXXXXX'
                    )
                ],
                verbose_name='Téléphone Alternatif',
                help_text='Numéro secondaire (optionnel)'
            ),
        ),
    ]