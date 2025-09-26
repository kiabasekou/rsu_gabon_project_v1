# =============================================================================
# FICHIER: apps/identity_app/migrations/0003_update_geographic_data.py
# MIGRATION CORRECTIVE: Ajouter champs manquants GeographicData
# =============================================================================

from django.db import migrations, models
import django.core.validators

class Migration(migrations.Migration):

    dependencies = [
        ('identity_app', '0002_remove_personidentity_rsu_persons_provinc_b5c7b7_idx_and_more'),
    ]

    operations = [
        # ✅ AJOUT: Champs manquants attendus par les tests
        migrations.AddField(
            model_name='geographicdata',
            name='district',
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name='District/Arrondissement'
            ),
        ),
        migrations.AddField(
            model_name='geographicdata',
            name='latitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=8,
                max_digits=10,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(-4.0),
                    django.core.validators.MaxValueValidator(2.3)
                ],
                verbose_name='Latitude'
            ),
        ),
        migrations.AddField(
            model_name='geographicdata',
            name='longitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=8,
                max_digits=11,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(8.5),
                    django.core.validators.MaxValueValidator(14.5)
                ],
                verbose_name='Longitude'
            ),
        ),
        migrations.AddField(
            model_name='geographicdata',
            name='distance_to_hospital',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Distance au centre de santé le plus proche',
                null=True,
                verbose_name='Distance hôpital (km)'
            ),
        ),
        migrations.AddField(
            model_name='geographicdata',
            name='distance_to_school',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Distance à l\'école primaire la plus proche',
                null=True,
                verbose_name='Distance école (km)'
            ),
        ),
        migrations.AddField(
            model_name='geographicdata',
            name='has_electricity',
            field=models.BooleanField(
                default=False,
                verbose_name='Accès électricité'
            ),
        ),
        migrations.AddField(
            model_name='geographicdata',
            name='has_water',
            field=models.BooleanField(
                default=False,
                verbose_name='Accès eau potable'
            ),
        ),
        migrations.AddField(
            model_name='geographicdata',
            name='has_road_access',
            field=models.BooleanField(
                default=False,
                verbose_name='Accès routier praticable'
            ),
        ),
        migrations.AddField(
            model_name='geographicdata',
            name='accessibility_score',
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                max_digits=5,
                verbose_name='Score accessibilité (0-100)'
            ),
        ),
        
        # ✅ AJOUT: Index pour performances
        migrations.AddIndex(
            model_name='geographicdata',
            index=models.Index(
                fields=['province', 'district'],
                name='geo_province_district_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='geographicdata',
            index=models.Index(
                fields=['accessibility_score'],
                name='geo_accessibility_idx'
            ),
        ),
    ]