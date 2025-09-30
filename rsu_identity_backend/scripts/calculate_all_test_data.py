# Script: scripts/calculate_all_test_data.py

from apps.identity_app.models import PersonIdentity
from apps.services_app.services import VulnerabilityService, EligibilityService
from apps.services_app.models import SocialProgram

print("🔄 Calcul vulnérabilité toutes les personnes...")

# Récupérer toutes les personnes
persons = PersonIdentity.objects.all()
person_ids = list(persons.values_list('id', flat=True))

print(f"📊 {len(person_ids)} personnes à traiter")

# Calcul vulnérabilité
vuln_service = VulnerabilityService()
results = vuln_service.bulk_calculate_assessments(person_ids, batch_size=50)

print(f"\n✅ Vulnérabilité: {results['success']}/{len(person_ids)}")
print(f"❌ Erreurs: {results['errors']}")

# Calcul éligibilité si programmes existent
programs = SocialProgram.objects.filter(is_active=True)
if programs.exists():
    elig_service = EligibilityService()
    for program in programs:
        print(f"\n🔄 Éligibilité {program.code}...")
        elig_results = elig_service.bulk_calculate_eligibility(
            person_ids,
            program.code
        )
        print(f"✅ {elig_results['success']} éligibilités calculées")

print("\n✅ Tous les calculs terminés")


#python manage.py shell < scripts/calculate_all_test_data.py