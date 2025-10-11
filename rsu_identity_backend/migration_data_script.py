# Script de migration data
# migration_data_script.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rsu_identity.settings.base')
django.setup()

from apps.programs_app.models import SocialProgram as MasterProgram
from apps.services_app.models import VulnerabilityAssessment
from apps.services_app.models import OldSocialProgram


# 1. Copier programmes de services_app vers programs_app
old_programs = OldSocialProgram.objects.all()  # Avant suppression
for old_prog in old_programs:
    MasterProgram.objects.get_or_create(
        code=old_prog.code,
        defaults={
            'name': old_prog.name,
            'total_budget': old_prog.annual_budget,
            'budget_spent': old_prog.budget_used_fcfa,
            'status': 'ACTIVE' if old_prog.is_active else 'DRAFT',
            # ... autres champs
        }
    )

# 2. Mettre à jour les FK dans VulnerabilityAssessment
for assessment in VulnerabilityAssessment.objects.all():
    try:
        master_prog = MasterProgram.objects.get(code=assessment.old_program_code)
        assessment.program = master_prog
        assessment.save()
    except MasterProgram.DoesNotExist:
        print(f"❌ Programme introuvable pour l'évaluation ID {assessment.id} (code: {assessment.old_program_code})")

    assessment.program = master_prog
    assessment.save()

count = 0
for assessment in VulnerabilityAssessment.objects.all():
    try:
        master_prog = MasterProgram.objects.get(code=assessment.old_program_code)
        assessment.program = master_prog
        assessment.save()
        count += 1
    except MasterProgram.DoesNotExist:
        print(f"❌ Programme introuvable pour l'évaluation ID {assessment.id}")
print(f"✅ {count} évaluations mises à jour avec succès.")
