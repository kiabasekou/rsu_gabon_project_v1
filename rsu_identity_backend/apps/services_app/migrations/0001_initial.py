# ===================================================================
# RSU GABON - MIGRATION SERVICES APP
# CRÉER: apps/services_app/migrations/0001_initial.py
# ===================================================================

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    
    initial = True
    
    dependencies = [
        ('core_app', '0001_initial'),
        ('identity_app', '0005_add_test_fields'),
    ]
    
    operations = [
        migrations.CreateModel(
            name='VulnerabilityAssessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modifié le')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('global_score', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Score global vulnérabilité (0-100)')),
                ('vulnerability_level', models.CharField(choices=[('CRITICAL', 'Critique'), ('HIGH', 'Élevée'), ('MODERATE', 'Modérée'), ('LOW', 'Faible')], max_length=20, verbose_name='Niveau vulnérabilité')),
                ('dimension_scores', models.JSONField(default=dict, help_text='5 dimensions: économique, social, géographique, santé, éducation', verbose_name='Scores par dimension')),
                ('priority_interventions', models.JSONField(default=list, help_text='Liste des interventions prioritaires recommandées', verbose_name='Interventions prioritaires')),
                ('social_programs_eligibility', models.JSONField(default=dict, help_text='Éligibilité calculée pour chaque programme social', verbose_name='Éligibilité programmes sociaux')),
                ('geographic_priority_zone', models.CharField(choices=[('ZONE_1', 'Zone Priorité 1 - Critique'), ('ZONE_2', 'Zone Priorité 2 - Élevée'), ('ZONE_3', 'Zone Priorité 3 - Modérée'), ('ZONE_4', 'Zone Priorité 4 - Standard')], max_length=30, verbose_name='Zone priorité géographique')),
                ('confidence_score', models.DecimalField(decimal_places=2, help_text='Score de confiance de l\'évaluation IA (0-100)', max_digits=5, verbose_name='Score confiance évaluation')),
                ('assessment_date', models.DateTimeField(auto_now_add=True, verbose_name='Date évaluation')),
                ('validation_status', models.CharField(choices=[('PENDING', 'En attente'), ('VALIDATED', 'Validé'), ('REJECTED', 'Rejeté'), ('REVIEW', 'À réviser')], default='PENDING', max_length=20, verbose_name='Statut validation')),
                ('validator_notes', models.TextField(blank=True, null=True, verbose_name='Notes du validateur')),
                ('assessed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core_app.rsuuser', verbose_name='Évaluateur')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to='core_app.rsuuser', verbose_name='Créé par')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vulnerability_assessments', to='identity_app.personidentity', verbose_name='Personne évaluée')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to='core_app.rsuuser', verbose_name='Modifié par')),
            ],
            options={
                'verbose_name': 'Zone priorité géographique',
                'verbose_name_plural': 'Zones priorité géographique',
                'db_table': 'services_geographic_priority_zones',
                'ordering': ['priority_level', 'province', 'zone_name'],
            },
        ),
        migrations.AddConstraint(
            model_name='vulnerabilityassessment',
            constraint=models.UniqueConstraint(fields=('person', 'assessment_date'), name='unique_person_assessment_date'),
        ),
        migrations.AddConstraint(
            model_name='socialprogrameligibility',
            constraint=models.UniqueConstraint(fields=('person', 'program_code'), name='unique_person_program'),
        ),
    ](blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to='core_app.rsuuser', verbose_name='Modifié par')),
            ],
            options={
                'verbose_name': 'Évaluation vulnérabilité',
                'verbose_name_plural': 'Évaluations vulnérabilité',
                'db_table': 'services_vulnerability_assessments',
                'ordering': ['-assessment_date'],
            },
        ),
        migrations.CreateModel(
            name='SocialProgramEligibility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modifié le')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('program_code', models.CharField(choices=[('AIDE_ALIMENTAIRE', 'Programme Aide Alimentaire'), ('ALLOCATION_FAMILLE', 'Allocations Familiales'), ('AIDE_LOGEMENT', 'Aide au Logement'), ('FORMATION_PROF', 'Formation Professionnelle'), ('MICRO_CREDIT', 'Micro-crédit'), ('SANTE_GRATUITE', 'Santé Gratuite'), ('EDUCATION_BOURSE', 'Bourses Éducation'), ('INSERTION_JEUNES', 'Insertion Jeunes'), ('AIDE_HANDICAP', 'Aide Handicap'), ('PROTECTION_ENFANCE', 'Protection Enfance')], max_length=20, verbose_name='Code programme')),
                ('eligibility_score', models.DecimalField(decimal_places=2, help_text='Score éligibilité calculé par IA (0-100)', max_digits=5, verbose_name='Score éligibilité')),
                ('recommendation_level', models.CharField(choices=[('HIGHLY_RECOMMENDED', 'Fortement recommandé'), ('RECOMMENDED', 'Recommandé'), ('CONDITIONALLY_ELIGIBLE', 'Éligible sous conditions'), ('NOT_ELIGIBLE', 'Non éligible')], max_length=20, verbose_name='Niveau recommandation')),
                ('criteria_met', models.JSONField(default=dict, help_text='Détail des critères remplis/non remplis', verbose_name='Critères remplis')),
                ('missing_documents', models.JSONField(default=list, help_text='Liste des documents manquants si applicable', verbose_name='Documents manquants')),
                ('estimated_benefit_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Montant estimé du bénéfice (FCFA)', max_digits=10, null=True, verbose_name='Montant estimé bénéfice')),
                ('calculated_at', models.DateTimeField(auto_now_add=True, verbose_name='Calculé le')),
                ('enrollment_status', models.CharField(choices=[('NOT_ENROLLED', 'Non inscrit'), ('PENDING_ENROLLMENT', 'Inscription en cours'), ('ENROLLED', 'Inscrit'), ('SUSPENDED', 'Suspendu'), ('COMPLETED', 'Terminé')], default='NOT_ENROLLED', max_length=20, verbose_name='Statut inscription')),
                ('enrollment_date', models.DateTimeField(blank=True, null=True, verbose_name='Date inscription')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to='core_app.rsuuser', verbose_name='Créé par')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program_eligibilities', to='identity_app.personidentity', verbose_name='Personne')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to='core_app.rsuuser', verbose_name='Modifié par')),
            ],
            options={
                'verbose_name': 'Éligibilité programme social',
                'verbose_name_plural': 'Éligibilités programmes sociaux',
                'db_table': 'services_program_eligibilities',
                'ordering': ['-calculated_at'],
            },
        ),
        migrations.CreateModel(
            name='GeographicPriorityZone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modifié le')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('zone_code', models.CharField(max_length=20, unique=True, verbose_name='Code zone')),
                ('zone_name', models.CharField(max_length=100, verbose_name='Nom zone')),
                ('province', models.CharField(choices=[('ESTUAIRE', 'Estuaire'), ('HAUT_OGOOUE', 'Haut-Ogooué'), ('MOYEN_OGOOUE', 'Moyen-Ogooué'), ('NGOUNIE', 'Ngounié'), ('NYANGA', 'Nyanga'), ('OGOOUE_IVINDO', 'Ogooué-Ivindo'), ('OGOOUE_LOLO', 'Ogooué-Lolo'), ('OGOOUE_MARITIME', 'Ogooué-Maritime'), ('WOLEU_NTEM', 'Woleu-Ntem')], max_length=50, verbose_name='Province')),
                ('priority_level', models.CharField(choices=[('CRITICAL', 'Critique'), ('HIGH', 'Élevée'), ('MODERATE', 'Modérée'), ('LOW', 'Faible')], max_length=20, verbose_name='Niveau priorité')),
                ('vulnerability_indicators', models.JSONField(default=dict, help_text='Indicateurs de vulnérabilité de la zone', verbose_name='Indicateurs vulnérabilité')),
                ('population_estimate', models.PositiveIntegerField(help_text='Estimation population de la zone', verbose_name='Estimation population')),
                ('center_latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Latitude centre')),
                ('center_longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Longitude centre')),
                ('radius_km', models.PositiveIntegerField(blank=True, help_text='Rayon approximatif en kilomètres', null=True, verbose_name='Rayon (km)')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to='core_app.rsuuser', verbose_name='Créé par')),
                ('updated_by', models.ForeignKey