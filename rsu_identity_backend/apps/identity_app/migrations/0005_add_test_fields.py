# 3. Migration nécessaire
# CRÉER: apps/identity_app/migrations/0005_add_test_fields.py

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('identity_app', '0004_update_geographic_data'),
    ]

    operations = [
        # Ajouter department à GeographicData
        migrations.AddField(
            model_name='geographicdata',
            name='department',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Département'),
        ),
        
        # Ajouter champs démographiques à Household
        migrations.AddField(
            model_name='household',
            name='head_person',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='headed_household_alt', to='identity_app.personidentity', verbose_name='Chef de Ménage (Référence alternative)'),
        ),
        migrations.AddField(
            model_name='household',
            name='members_under_15',
            field=models.PositiveIntegerField(default=0, verbose_name='Membres < 15 ans'),
        ),
        migrations.AddField(
            model_name='household',
            name='members_15_64',
            field=models.PositiveIntegerField(default=0, verbose_name='Membres 15-64 ans'),
        ),
        migrations.AddField(
            model_name='household',
            name='members_over_64',
            field=models.PositiveIntegerField(default=0, verbose_name='Membres > 64 ans'),
        ),
    ]