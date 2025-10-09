#!/usr/bin/env python
"""
🇬🇦 RSU Gabon - Script Installation Programs App
Standards Top 1% - Installation Automatique
Fichier: rsu_identity_backend/setup_programs_app.py
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rsu_identity.settings.development')
django.setup()

from django.core.management import call_command
from apps.programs_app.models import ProgramCategory, SocialProgram
from apps.core_app.models import RSUUser
from decimal import Decimal
from datetime import date, timedelta


def print_step(step, message):
    """Affiche étape avec style"""
    print(f"\n{'='*60}")
    print(f"📋 ÉTAPE {step}: {message}")
    print(f"{'='*60}\n")


def create_sample_data():
    """Crée données d'exemple"""
    print_step(1, "CRÉATION DONNÉES D'EXEMPLE")
    
    # Vérifier si données existent déjà
    if ProgramCategory.objects.exists():
        print("⚠️  Des catégories existent déjà.")
        response = input("Supprimer et recréer ? (y/N): ")
        if response.lower() == 'y':
            ProgramCategory.objects.all().delete()
            SocialProgram.objects.all().delete()
            print("✅ Données supprimées")
        else:
            print("❌ Installation annulée")
            return False
    
    # Récupérer admin user
    admin_user = RSUUser.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ Erreur: Aucun superuser trouvé")
        print("   Créez un superuser avec: python manage.py createsuperuser")
        return False
    
    print(f"✅ Admin user: {admin_user.username}")
    
    # Créer catégories
    print("\n📁 Création catégories...")
    categories = [
        {
            "name": "Transferts Monétaires",
            "description": "Programmes de transferts directs aux ménages vulnérables",
            "icon": "💰"
        },
        {
            "name": "Éducation",
            "description": "Bourses scolaires et aide à la scolarisation",
            "icon": "🎓"
        },
        {
            "name": "Santé",
            "description": "Assurance maladie et accès aux soins",
            "icon": "🏥"
        },
        {
            "name": "Alimentation",
            "description": "Aide alimentaire et nutrition",
            "icon": "🍎"
        },
        {
            "name": "Logement",
            "description": "Aide au logement et réhabilitation",
            "icon": "🏠"
        }
    ]
    
    created_categories = {}
    for cat_data in categories:
        cat = ProgramCategory.objects.create(**cat_data)
        created_categories[cat.name] = cat
        print(f"   ✅ {cat.icon} {cat.name}")
    
    # Créer programmes
    print("\n📋 Création programmes...")
    today = date.today()
    programs = [
        {
            "code": "TMC-2025",
            "name": "Transfert Monétaire Conditionnel 2025",
            "category": created_categories["Transferts Monétaires"],
            "description": "Programme de soutien financier direct aux familles les plus vulnérables du Gabon",
            "objectives": "Réduire la pauvreté extrême et améliorer les conditions de vie des ménages",
            "status": "ACTIVE",
            "start_date": today,
            "end_date": today + timedelta(days=365),
            "total_budget": Decimal("1000000000"),  # 1 milliard FCFA
            "benefit_amount": Decimal("50000"),  # 50,000 FCFA/mois
            "frequency": "MONTHLY",
            "max_beneficiaries": 1000,
            "eligibility_criteria": {
                "vulnerability_min": 50,
                "age_min": 18,
                "provinces": ["ESTUAIRE", "HAUT_OGOOUE", "NGOUNIE"]
            },
            "target_provinces": ["ESTUAIRE", "HAUT_OGOOUE", "NGOUNIE"]
        },
        {
            "code": "BOURSE-EDU-2025",
            "name": "Bourses Scolaires 2025",
            "category": created_categories["Éducation"],
            "description": "Bourses pour enfants issus de familles défavorisées",
            "objectives": "Favoriser l'accès à l'éducation pour tous",
            "status": "ACTIVE",
            "start_date": today,
            "end_date": date(2025, 6, 30),
            "total_budget": Decimal("500000000"),
            "benefit_amount": Decimal("75000"),
            "frequency": "QUARTERLY",
            "max_beneficiaries": 500,
            "eligibility_criteria": {
                "vulnerability_min": 40,
                "age_min": 6,
                "age_max": 18
            },
            "target_provinces": ["ESTUAIRE", "HAUT_OGOOUE", "MOYEN_OGOOUE"]
        },
        {
            "code": "AMU-2025",
            "name": "Assurance Maladie Universelle",
            "category": created_categories["Santé"],
            "description": "Couverture santé universelle pour les plus vulnérables",
            "objectives": "Garantir l'accès aux soins de santé pour tous",
            "status": "ACTIVE",
            "start_date": today,
            "total_budget": Decimal("2000000000"),
            "benefit_amount": Decimal("25000"),
            "frequency": "MONTHLY",
            "max_beneficiaries": 5000,
            "eligibility_criteria": {
                "vulnerability_min": 60
            },
            "target_provinces": []  # Toutes provinces
        },
        {
            "code": "AIDE-ALIM-2025",
            "name": "Aide Alimentaire d'Urgence",
            "category": created_categories["Alimentation"],
            "description": "Distribution de kits alimentaires aux familles en situation critique",
            "objectives": "Assurer sécurité alimentaire des populations vulnérables",
            "status": "DRAFT",
            "start_date": today + timedelta(days=30),
            "total_budget": Decimal("300000000"),
            "benefit_amount": Decimal("30000"),
            "frequency": "ONE_TIME",
            "max_beneficiaries": 2000,
            "eligibility_criteria": {
                "vulnerability_min": 75
            },
            "target_provinces": ["NGOUNIE", "NYANGA", "OGOOUE_LOLO"]
        },
        {
            "code": "REHAB-LOG-2025",
            "name": "Programme Réhabilitation Logement",
            "category": created_categories["Logement"],
            "description": "Aide à la rénovation de logements insalubres",
            "objectives": "Améliorer conditions d'habitat des familles vulnérables",
            "status": "DRAFT",
            "start_date": today + timedelta(days=60),
            "total_budget": Decimal("800000000"),
            "benefit_amount": Decimal("500000"),
            "frequency": "ONE_TIME",
            "max_beneficiaries": 300,
            "eligibility_criteria": {
                "vulnerability_min": 65,
                "household_size_min": 3
            },
            "target_provinces": ["ESTUAIRE", "OGOOUE_MARITIME"]
        }
    ]
    
    created_programs = []
    for prog_data in programs:
        prog = SocialProgram.objects.create(
            **prog_data,
            managed_by=admin_user,
            created_by=admin_user
        )
        created_programs.append(prog)
        
        status_icon = "🟢" if prog.status == "ACTIVE" else "🟡"
        print(f"   {status_icon} {prog.code} - {prog.name}")
        print(f"      Budget: {prog.total_budget:,.0f} FCFA")
        print(f"      Aide: {prog.benefit_amount:,.0f} FCFA/{prog.get_frequency_display()}")
    
    return True


def run_tests():
    """Exécute tests basiques"""
    print_step(2, "TESTS APIs")
    
    print("🧪 Test 1: Compter programmes...")
    count = SocialProgram.objects.count()
    print(f"   ✅ {count} programmes trouvés")
    
    print("\n🧪 Test 2: Programmes actifs...")
    active = SocialProgram.objects.filter(status='ACTIVE').count()
    print(f"   ✅ {active} programmes actifs")
    
    print("\n🧪 Test 3: Budget total...")
    total_budget = sum(
        p.total_budget for p in SocialProgram.objects.all()
    )
    print(f"   ✅ Budget total: {total_budget:,.0f} FCFA")
    
    print("\n🧪 Test 4: Catégories...")
    categories = ProgramCategory.objects.count()
    print(f"   ✅ {categories} catégories")


def display_summary():
    """Affiche résumé"""
    print_step(3, "RÉSUMÉ INSTALLATION")
    
    programs = SocialProgram.objects.all()
    categories = ProgramCategory.objects.all()
    
    print("📊 STATISTIQUES:")
    print(f"   • {categories.count()} catégories créées")
    print(f"   • {programs.count()} programmes créés")
    print(f"   • {programs.filter(status='ACTIVE').count()} programmes actifs")
    print(f"   • Budget total: {sum(p.total_budget for p in programs):,.0f} FCFA")
    
    print("\n📋 PROGRAMMES PAR CATÉGORIE:")
    for cat in categories:
        count = cat.programs.count()
        print(f"   {cat.icon} {cat.name}: {count} programme(s)")
    
    print("\n🎯 ENDPOINTS DISPONIBLES:")
    print("   GET  /api/v1/programs/programs/")
    print("   POST /api/v1/programs/programs/")
    print("   GET  /api/v1/programs/categories/")
    print("   GET  /api/v1/programs/enrollments/")
    print("   GET  /api/v1/programs/payments/")
    
    print("\n🔗 ADMIN DJANGO:")
    print("   http://localhost:8000/admin/programs_app/")
    
    print("\n✅ INSTALLATION TERMINÉE AVEC SUCCÈS!")


def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("🇬🇦 RSU GABON - INSTALLATION PROGRAMS APP")
    print("="*60)
    
    try:
        # Créer données
        if not create_sample_data():
            print("\n❌ Installation annulée")
            return
        
        # Tests
        run_tests()
        
        # Résumé
        display_summary()
        
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()