#!/usr/bin/env python
"""
Script de diagnostic - Identifie tous les champs manquants dans eligibility_service.py
"""
import os
import sys
import django
import re

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rsu_identity.settings.development')
django.setup()

from apps.identity_app.models import PersonIdentity, Household
from apps.services_app.models import VulnerabilityAssessment, SocialProgramEligibility

def get_model_fields(model):
    """Récupère tous les champs d'un modèle"""
    fields = []
    for field in model._meta.get_fields():
        if not field.many_to_many and not field.one_to_many:
            fields.append(field.name)
    return set(fields)

def analyze_service_file():
    """Analyse le fichier eligibility_service.py"""
    
    print("=" * 80)
    print("DIAGNOSTIC COMPLET - eligibility_service.py")
    print("=" * 80)
    
    # Charger les champs réels
    person_fields = get_model_fields(PersonIdentity)
    household_fields = get_model_fields(Household)
    vuln_fields = get_model_fields(VulnerabilityAssessment)
    elig_fields = get_model_fields(SocialProgramEligibility)
    
    print("\nCHAMPS DISPONIBLES DANS LES MODÈLES:")
    print(f"\nPersonIdentity ({len(person_fields)} champs):")
    for field in sorted(person_fields):
        print(f"  ✓ {field}")
    
    print(f"\nHousehold ({len(household_fields)} champs):")
    for field in sorted(household_fields):
        print(f"  ✓ {field}")
    
    # Lire le fichier eligibility_service.py
    service_file = 'apps/services_app/services/eligibility_service.py'
    
    if not os.path.exists(service_file):
        print(f"\n❌ Fichier non trouvé: {service_file}")
        return
    
    with open(service_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n" + "=" * 80)
    print("CHAMPS UTILISÉS DANS LE CODE (eligibility_service.py)")
    print("=" * 80)
    
    # Patterns à rechercher
    patterns = {
        'person': r'person\.([a-z_]+)',
        'household': r'household\.([a-z_]+)',
        'assessment': r'assessment\.([a-z_]+)',
        'eligibility': r'eligibility\.([a-z_]+)'
    }
    
    issues = {
        'person': [],
        'household': [],
        'assessment': [],
        'eligibility': []
    }
    
    # Analyser chaque pattern
    for obj_type, pattern in patterns.items():
        matches = re.findall(pattern, content)
        unique_fields = set(matches)
        
        print(f"\n{obj_type.upper()} - {len(unique_fields)} champs utilisés:")
        
        for field in sorted(unique_fields):
            # Vérifier si le champ existe
            if obj_type == 'person' and field not in person_fields:
                print(f"  ❌ {field} (N'EXISTE PAS)")
                issues['person'].append(field)
            elif obj_type == 'household' and field not in household_fields:
                print(f"  ❌ {field} (N'EXISTE PAS)")
                issues['household'].append(field)
            elif obj_type == 'assessment' and field not in vuln_fields:
                print(f"  ❌ {field} (N'EXISTE PAS)")
                issues['assessment'].append(field)
            elif obj_type == 'eligibility' and field not in elig_fields:
                print(f"  ❌ {field} (N'EXISTE PAS)")
                issues['eligibility'].append(field)
            else:
                print(f"  ✓ {field}")
    
    # Résumé des problèmes
    print("\n" + "=" * 80)
    print("RÉSUMÉ DES CORRECTIONS NÉCESSAIRES")
    print("=" * 80)
    
    total_issues = sum(len(v) for v in issues.values())
    
    if total_issues == 0:
        print("\n✅ AUCUN PROBLÈME DÉTECTÉ - Le service est compatible!")
    else:
        print(f"\n❌ TOTAL: {total_issues} champs incompatibles détectés\n")
        
        if issues['person']:
            print(f"\nPersonIdentity - {len(issues['person'])} corrections:")
            for field in issues['person']:
                # Suggérer remplacement
                suggestion = suggest_replacement(field, person_fields)
                if suggestion:
                    print(f"  • {field} → {suggestion}")
                else:
                    print(f"  • {field} → SUPPRIMER ou ajouter au modèle")
        
        if issues['household']:
            print(f"\nHousehold - {len(issues['household'])} corrections:")
            for field in issues['household']:
                suggestion = suggest_replacement(field, household_fields)
                if suggestion:
                    print(f"  • {field} → {suggestion}")
                else:
                    print(f"  • {field} → SUPPRIMER ou ajouter au modèle")
        
        if issues['assessment']:
            print(f"\nVulnerabilityAssessment - {len(issues['assessment'])} corrections:")
            for field in issues['assessment']:
                suggestion = suggest_replacement(field, vuln_fields)
                if suggestion:
                    print(f"  • {field} → {suggestion}")
                else:
                    print(f"  • {field} → SUPPRIMER")
        
        if issues['eligibility']:
            print(f"\nSocialProgramEligibility - {len(issues['eligibility'])} corrections:")
            for field in issues['eligibility']:
                suggestion = suggest_replacement(field, elig_fields)
                if suggestion:
                    print(f"  • {field} → {suggestion}")
                else:
                    print(f"  • {field} → SUPPRIMER")
    
    print("\n" + "=" * 80)

def suggest_replacement(missing_field, available_fields):
    """Suggère un champ de remplacement basé sur la similarité"""
    replacements = {
        'children_count': 'members_under_15',
        'elderly_count': 'members_over_64',
        'monthly_income': 'total_monthly_income',
        'global_score': 'vulnerability_score',
        'calculated_at': 'assessment_date',
        'household': 'headed_household',
        'has_chronic_illness': 'has_disability',
        'national_id_number': 'national_id',
        'birth_certificate_number': None,  # N'existe pas
        'disabled_count': 'has_disabled_members',
        'pregnant_count': 'has_pregnant_women',
    }
    
    return replacements.get(missing_field)

if __name__ == "__main__":
    analyze_service_file()