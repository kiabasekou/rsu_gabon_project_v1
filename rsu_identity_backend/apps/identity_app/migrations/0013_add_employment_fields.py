"""
ÉTAPE 1/5: MIGRATION (apps/identity_app/migrations/0010_add_employment_fields.py)
"""

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('identity_app', '0009_alter_personidentity_vulnerability_score'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='personidentity',
            name='employer',
            field=models.CharField(
                max_length=200, null=True, blank=True,
                verbose_name='Employeur'
            ),
        ),
        migrations.AddField(
            model_name='personidentity',
            name='employment_status',
            field=models.CharField(
                max_length=20, null=True, blank=True,
                choices=[
                    ('EMPLOYED_FORMAL', 'Employé Formel'),
                    ('EMPLOYED_INFORMAL', 'Employé Informel'),
                    ('SELF_EMPLOYED', 'Indépendant'),
                    ('UNEMPLOYED', 'Sans Emploi'),
                    ('STUDENT', 'Étudiant'),
                    ('RETIRED', 'Retraité'),
                    ('HOMEMAKER', 'Au Foyer'),
                    ('UNABLE_TO_WORK', 'Inapte'),
                ],
                verbose_name='Statut Emploi'
            ),
        ),
        migrations.AddIndex(
            model_name='personidentity',
            index=models.Index(
                fields=['employment_status', 'province'],
                name='identity_employm_idx'
            ),
        ),
    ]
