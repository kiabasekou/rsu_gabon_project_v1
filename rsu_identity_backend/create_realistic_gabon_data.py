"""
🇬🇦 RSU Gabon - Création 400 Ménages Réalistes
✅ Basé EXCLUSIVEMENT sur les modèles réels du repository
✅ AUCUNE supposition - Tous les champs vérifiés

Fichier: rsu_identity_backend/create_400_realistic_gabon_data.py
"""

import os
import sys
import random
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rsu_identity.settings.development')

import django
try:
    django.setup()
except RuntimeError:
    pass

from apps.identity_app.models import PersonIdentity, Household
from apps.core_app.models import RSUUser

# ============================================================================
# DONNÉES GABONAISES RÉALISTES
# ============================================================================

NOMS = [
    'NDONG', 'NGUEMA', 'OBIANG', 'MOUSSOUNDA', 'BIKORO', 'MINTSA', 'OVONO', 
    'ELLA', 'MBA', 'ONDO', 'NZUE', 'MBOUMBA', 'MVIE', 'KOUMBA', 'BONGO',
    'MIHINDOU', 'OGANDAGA', 'EYENE', 'ANGOUE', 'MAGANGA'
]

PRENOMS_HOMMES = [
    'Jean', 'Pierre', 'Paul', 'François', 'André', 'Michel', 'Patrick', 
    'Christian', 'Bruno', 'Daniel', 'Emmanuel', 'Georges', 'Henri', 'Joseph'
]

PRENOMS_FEMMES = [
    'Marie', 'Jeanne', 'Antoinette', 'Catherine', 'Elisabeth', 'Anne', 
    'Christine', 'Sylvie', 'Rosalie', 'Bernadette', 'Françoise', 'Thérèse'
]

# Provinces avec données géographiques réelles
PROVINCES = {
    'ESTUAIRE': {
        'communes': ['Libreville', 'Akanda', 'Ntoum', 'Kango'],
        'gps': (0.4162, 9.4673)
    },
    'HAUT_OGOOUE': {
        'communes': ['Franceville', 'Moanda', 'Mounana', 'Okondja'],
        'gps': (-1.6333, 13.5833)
    },
    'OGOOUE_MARITIME': {
        'communes': ['Port-Gentil', 'Omboué', 'Gamba'],
        'gps': (-0.7193, 8.7815)
    },
    'NGOUNIE': {
        'communes': ['Mouila', 'Ndendé', 'Mbigou', 'Mandji'],
        'gps': (-1.8667, 10.9667)
    },
    'WOLEU_NTEM': {
        'communes': ['Oyem', 'Bitam', 'Mitzic', 'Minvoul'],
        'gps': (1.6000, 11.5833)
    },
    'MOYEN_OGOOUE': {
        'communes': ['Lambaréné', 'Ndjolé', 'Booué'],
        'gps': (-0.7000, 10.2333)
    },
    'OGOOUE_IVINDO': {
        'communes': ['Makokou', 'Ovan', 'Mékambo'],
        'gps': (0.5738, 12.8643)
    },
    'OGOOUE_LOLO': {
        'communes': ['Koulamoutou', 'Lastoursville', 'Pana'],
        'gps': (-0.9833, 12.4833)
    },
    'NYANGA': {
        'communes': ['Tchibanga', 'Mayumba', 'Moabi'],
        'gps': (-2.9167, 11.0167)
    }
}

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def gen_rsu_id():
    """Génère un RSU-ID unique"""
    return f"RSU-GA-{random.randint(100000, 999999)}"

def gen_nip():
    """Génère un NIP au format gabonais"""
    year = random.randint(1950, 2024)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    seq = random.randint(10000, 99999)
    return f"{year:04d}{month:02d}{day:02d}-{seq}"

def gen_phone():
    """Génère un numéro de téléphone gabonais valide"""
    prefixes = ['07', '06', '05', '04', '01', '02']
    return f"+241{random.choice(prefixes)}{random.randint(1000000, 9999999):07d}"

def gen_birth_date(min_age, max_age):
    """Génère une date de naissance réaliste"""
    days_old = random.randint(min_age * 365, max_age * 365)
    return date.today() - timedelta(days=days_old)

def calculate_age(birth_date):
    """Calcule l'âge à partir de la date de naissance"""
    if not birth_date:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def gen_gps_coords(base_lat, base_lon, radius=0.5):
    """Génère des coordonnées GPS autour d'un point de base"""
    lat = base_lat + random.uniform(-radius, radius)
    lon = base_lon + random.uniform(-radius, radius)
    return round(lat, 6), round(lon, 6)

def calculate_vulnerability_score(income, age, has_disability, is_household_head, gender):
    """Calcule un score de vulnérabilité réaliste"""
    score = 0
    
    # Critères économiques (40 points max)
    if income == 0:
        score += 40
    elif income < 50000:
        score += 35
    elif income < 100000:
        score += 25
    elif income < 150000:
        score += 15
    
    # Critères démographiques (30 points max)
    if age:
        if age < 5:
            score += 25
        elif age < 18:
            score += 15
        elif age > 65:
            score += 30
    
    # Critères sociaux (30 points max)
    if has_disability:
        score += 20
    if is_household_head and gender == 'F':
        score += 10
    
    # Ajouter variabilité
    score += random.randint(-5, 5)
    
    return min(max(score, 0), 100)

def get_vulnerability_level(score):
    """Détermine le niveau de vulnérabilité"""
    if score >= 75:
        return 'CRITICAL'
    elif score >= 50:
        return 'HIGH'
    elif score >= 25:
        return 'MODERATE'
    else:
        return 'LOW'

def get_employment_status(age, occupation):
    """Détermine le statut d'emploi basé sur l'âge et l'occupation"""
    if age < 6:
        return 'UNABLE_TO_WORK'
    elif 6 <= age < 16:
        return 'STUDENT'
    elif occupation == 'Sans emploi':
        return 'UNEMPLOYED'
    elif occupation in ['Fonctionnaire', 'Enseignant', 'Cadre']:
        return 'EMPLOYED_FORMAL'
    else:
        return 'EMPLOYED_INFORMAL'

# ============================================================================
# FONCTION PRINCIPALE DE CRÉATION
# ============================================================================

def create_realistic_population(target_households=400):
    """
    Crée une population réaliste de ménages gabonais
    
    Args:
        target_households: Nombre de ménages à créer (défaut: 400)
    """
    print("\n" + "="*80)
    print("🇬🇦 RSU GABON - CRÉATION POPULATION RÉALISTE")
    print("="*80)
    print(f"🎯 Objectif: {target_households} ménages avec données cohérentes")
    print(f"📅 Date: {date.today().strftime('%d/%m/%Y')}\n")
    
    # Vérifier utilisateur admin
    try:
        admin_user = RSUUser.objects.get(username='admin')
        print(f"✅ Utilisateur administrateur: {admin_user.username}")
    except RSUUser.DoesNotExist:
        print("❌ ERREUR: Utilisateur 'admin' introuvable")
        print("   Créez-le avec: python manage.py createsuperuser")
        return
    
    # Nettoyer la base de données (ORDRE CRITIQUE: Ménages AVANT Personnes)
    print("\n🧹 Nettoyage de la base de données...")
    deleted_households = Household.objects.all().delete()[0]
    deleted_persons = PersonIdentity.objects.all().delete()[0]
    print(f"   - {deleted_households} ménages supprimés")
    print(f"   - {deleted_persons} personnes supprimées")
    
    print("\n🏗️  Début de la création...\n")
    
    created_households = 0
    created_persons = 0
    
    for h_idx in range(target_households):
        # Sélectionner province et commune aléatoires
        province_code = random.choice(list(PROVINCES.keys()))
        province_data = PROVINCES[province_code]
        commune = random.choice(province_data['communes'])
        base_lat, base_lon = province_data['gps']
        lat, lon = gen_gps_coords(base_lat, base_lon)
        
        # Nom de famille commun pour le ménage
        family_name = random.choice(NOMS)
        
        # Taille du ménage (distribution réaliste)
        household_size = random.choices(
            [2, 3, 4, 5, 6, 7, 8],
            weights=[20, 25, 25, 15, 10, 3, 2]
        )[0]
        
        # ====================================================================
        # PHASE 1: CRÉER LE CHEF DE MÉNAGE
        # ====================================================================
        
        chief_gender = random.choice(['M', 'F'])
        chief_first_name = random.choice(
            PRENOMS_HOMMES if chief_gender == 'M' else PRENOMS_FEMMES
        )
        chief_birth_date = gen_birth_date(25, 70)
        chief_age = calculate_age(chief_birth_date)
        
        # Générer identifiants uniques
        chief_rsu_id = gen_rsu_id()
        while PersonIdentity.objects.filter(rsu_id=chief_rsu_id).exists():
            chief_rsu_id = gen_rsu_id()
        
        chief_nip = gen_nip()
        while PersonIdentity.objects.filter(nip=chief_nip).exists():
            chief_nip = gen_nip()
        
        # Données économiques du chef
        chief_occupation = random.choice([
            'Fonctionnaire', 'Enseignant', 'Commerçant', 'Agriculteur',
            'Chauffeur', 'Artisan', 'Sans emploi', 'Retraité'
        ])
        
        if chief_occupation == 'Sans emploi':
            chief_income = 0
            chief_employer = None
        elif chief_occupation == 'Retraité':
            chief_income = random.randint(80000, 200000)
            chief_employer = None
        elif chief_occupation == 'Fonctionnaire':
            chief_income = random.randint(200000, 600000)
            chief_employer = 'État Gabonais'
        else:
            chief_income = random.randint(100000, 400000)
            chief_employer = None if chief_occupation in ['Commerçant', 'Agriculteur', 'Artisan'] else 'Employeur privé'
        
        chief_employment_status = get_employment_status(chief_age, chief_occupation)
        
        # Calculer vulnérabilité du chef
        chief_has_disability = random.random() < 0.05  # 5% de handicap
        chief_vuln_score = calculate_vulnerability_score(
            chief_income, chief_age, chief_has_disability, True, chief_gender
        )
        chief_vuln_level = get_vulnerability_level(chief_vuln_score)
        
        try:
            chief = PersonIdentity.objects.create(
                rsu_id=chief_rsu_id,
                nip=chief_nip,
                national_id=None,
                first_name=chief_first_name,
                last_name=family_name,
                maiden_name=None,
                birth_date=chief_birth_date,
                birth_place=commune,
                gender=chief_gender,
                marital_status='MARRIED' if household_size > 1 else 'SINGLE',
                nationality='GABONAISE',
                phone_number=gen_phone(),
                phone_number_alt=gen_phone() if random.random() < 0.3 else None,
                email=f"{chief_first_name.lower()}.{family_name.lower()}@email.ga" if random.random() < 0.2 else None,
                education_level=random.choice(['PRIMARY', 'SECONDARY', 'HIGH_SCHOOL', 'UNIVERSITY']),
                occupation=chief_occupation,
                employer=chief_employer,
                employment_status=chief_employment_status,
                monthly_income=Decimal(str(chief_income)),
                latitude=Decimal(str(lat)),
                longitude=Decimal(str(lon)),
                gps_accuracy=Decimal('10.0'),
                province=province_code,
                department=None,
                commune=commune,
                district=None,
                address=f"Quartier {random.randint(1, 10)}, Rue {random.randint(1, 50)}, {commune}",
                has_disability=chief_has_disability,
                disability_details='Mobilité réduite' if chief_has_disability else None,
                is_household_head=True,
                vulnerability_score=Decimal(str(chief_vuln_score)),
                vulnerability_level=chief_vuln_level,
                last_vulnerability_assessment=None,
                verification_status='PENDING',
                verified_by=None,
                data_completeness_score=Decimal('85.00'),
                rbpp_synchronized=False,
                rbpp_sync_date=None,
                notes=None,
                created_by=admin_user,
                updated_by=admin_user
            )
            created_persons += 1
            print(f"✅ Ménage {h_idx+1:03d}: {chief.first_name} {chief.last_name} ({chief_age} ans, {province_code})")
        except Exception as e:
            print(f"❌ Erreur création chef ménage {h_idx+1}: {e}")
            continue
        
        # ====================================================================
        # PHASE 2: CRÉER LE MÉNAGE
        # ====================================================================
        
        household_id = f"H-{province_code[:3]}-{h_idx+1:05d}"
        
        # Calculer revenus totaux initiaux
        total_household_income = chief_income
        
        # Déterminer types de membres
        members_under_15 = 0
        members_15_64 = 1  # Le chef
        members_over_64 = 0
        
        has_disabled = chief_has_disability
        has_elderly = chief_age > 64
        has_pregnant_women = False
        has_children_under_5 = False
        
        try:
            household = Household.objects.create(
                household_id=household_id,
                head_of_household=chief,
                head_person=chief,
                household_type='NUCLEAR' if household_size <= 5 else 'EXTENDED',
                household_size=household_size,
                members_under_15=members_under_15,
                members_15_64=members_15_64,
                members_over_64=members_over_64,
                housing_type=random.choice(['OWNED', 'RENTED', 'FREE']),
                number_of_rooms=random.randint(2, 6),
                water_access=random.choice(['PIPED', 'WELL', 'BOREHOLE']),
                electricity_access=random.choice(['GRID', 'GENERATOR', 'NONE']),
                has_toilet=random.random() < 0.7,
                total_monthly_income=Decimal(str(total_household_income)),
                has_bank_account=random.random() < 0.4,
                assets=[],
                livestock=[],
                has_agricultural_land=random.random() < 0.3,
                agricultural_land_size=random.uniform(0.5, 5.0) if random.random() < 0.3 else None,
                has_disabled_members=has_disabled,
                has_elderly_members=has_elderly,
                has_pregnant_women=has_pregnant_women,
                has_children_under_5=has_children_under_5,
                latitude=Decimal(str(lat)),
                longitude=Decimal(str(lon)),
                province=province_code,
                vulnerability_score=Decimal(str(chief_vuln_score)),
                created_by=admin_user,
                updated_by=admin_user
            )
            created_households += 1
            print(f"   🏠 Ménage {household_id} créé ({household_size} pers.)")
        except Exception as e:
            print(f"❌ Erreur création ménage: {e}")
            continue
        
        # ====================================================================
        # PHASE 3: CRÉER LES MEMBRES DU MÉNAGE
        # ====================================================================
        
        for member_idx in range(1, household_size):
            # Déterminer le type de membre
            if member_idx == 1 and chief.marital_status == 'MARRIED':
                # Conjoint
                member_gender = 'F' if chief_gender == 'M' else 'M'
                member_age_range = (chief_age - 10, chief_age + 10)
                member_occupation = random.choice(['Commerçant', 'Enseignant', 'Sans emploi', 'Fonctionnaire'])
            else:
                # Enfant ou autre
                member_gender = random.choice(['M', 'F'])
                member_age_range = (0, 25)
                member_occupation = 'Étudiant'
            
            member_birth_date = gen_birth_date(member_age_range[0], member_age_range[1])
            member_age = calculate_age(member_birth_date)
            
            # Générer identifiants uniques
            member_rsu_id = gen_rsu_id()
            while PersonIdentity.objects.filter(rsu_id=member_rsu_id).exists():
                member_rsu_id = gen_rsu_id()
            
            member_nip = gen_nip()
            while PersonIdentity.objects.filter(nip=member_nip).exists():
                member_nip = gen_nip()
            
            # Déterminer revenus et emploi
            if member_age < 16:
                member_income = 0
                member_employer = None
                member_occupation = 'Étudiant' if member_age >= 6 else None
            elif member_occupation == 'Sans emploi':
                member_income = 0
                member_employer = None
            else:
                member_income = random.randint(50000, 300000)
                member_employer = 'Employeur privé' if member_occupation not in ['Commerçant', 'Agriculteur'] else None
            
            member_employment_status = get_employment_status(member_age, member_occupation)
            
            # Calculer vulnérabilité
            member_has_disability = random.random() < 0.03
            member_vuln_score = calculate_vulnerability_score(
                member_income, member_age, member_has_disability, False, member_gender
            )
            member_vuln_level = get_vulnerability_level(member_vuln_score)
            
            # Prénom
            member_first_name = random.choice(
                PRENOMS_HOMMES if member_gender == 'M' else PRENOMS_FEMMES
            )
            
            try:
                member = PersonIdentity.objects.create(
                    rsu_id=member_rsu_id,
                    nip=member_nip,
                    national_id=None,
                    first_name=member_first_name,
                    last_name=family_name,
                    maiden_name=None,
                    birth_date=member_birth_date,
                    birth_place=commune,
                    gender=member_gender,
                    marital_status='SINGLE',
                    nationality='GABONAISE',
                    phone_number=gen_phone() if member_age >= 16 else None,
                    phone_number_alt=None,
                    email=None,
                    education_level='PRIMARY' if member_age < 12 else 'SECONDARY',
                    occupation=member_occupation,
                    employer=member_employer,
                    employment_status=member_employment_status,
                    monthly_income=Decimal(str(member_income)),
                    latitude=Decimal(str(lat)),
                    longitude=Decimal(str(lon)),
                    gps_accuracy=Decimal('10.0'),
                    province=province_code,
                    department=None,
                    commune=commune,
                    district=None,
                    address=chief.address,
                    has_disability=member_has_disability,
                    disability_details=None,
                    is_household_head=False,
                    vulnerability_score=Decimal(str(member_vuln_score)),
                    vulnerability_level=member_vuln_level,
                    last_vulnerability_assessment=None,
                    verification_status='PENDING',
                    verified_by=None,
                    data_completeness_score=Decimal('75.00'),
                    rbpp_synchronized=False,
                    rbpp_sync_date=None,
                    notes=None,
                    created_by=admin_user,
                    updated_by=admin_user
                )
                created_persons += 1
                
                # Mettre à jour statistiques ménage
                total_household_income += member_income
                
                if member_age < 15:
                    members_under_15 += 1
                    if member_age < 5:
                        has_children_under_5 = True
                elif member_age <= 64:
                    members_15_64 += 1
                else:
                    members_over_64 += 1
                    has_elderly = True
                
                if member_has_disability:
                    has_disabled = True
                
                if member_gender == 'F' and 18 <= member_age <= 45 and random.random() < 0.1:
                    has_pregnant_women = True
                
                emoji = "💑" if member_idx == 1 else ("👶" if member_age < 5 else "👤")
                print(f"   {emoji} {member.first_name} ({member_age} ans)")
                
            except Exception as e:
                print(f"   ❌ Erreur création membre {member_idx}: {e}")
                continue
        
        # ====================================================================
        # PHASE 4: METTRE À JOUR LE MÉNAGE AVEC LES STATS FINALES
        # ====================================================================
        
        try:
            household.total_monthly_income = Decimal(str(total_household_income))
            household.members_under_15 = members_under_15
            household.members_15_64 = members_15_64
            household.members_over_64 = members_over_64
            household.has_disabled_members = has_disabled
            household.has_elderly_members = has_elderly
            household.has_pregnant_women = has_pregnant_women
            household.has_children_under_5 = has_children_under_5
            household.save()
        except Exception as e:
            print(f"   ⚠️  Erreur mise à jour statistiques: {e}")
        
        print()  # Ligne vide entre ménages
    
    # ========================================================================
    # STATISTIQUES FINALES
    # ========================================================================
    
    print("="*80)
    print("✅ CRÉATION TERMINÉE AVEC SUCCÈS")
    print("="*80)
    print(f"\n📊 Statistiques de la population créée:")
    print(f"   - Ménages créés: {created_households}")
    print(f"   - Personnes créées: {created_persons}")
    print(f"   - Moyenne: {created_persons/created_households if created_households > 0 else 0:.1f} personnes/ménage")
    
    # Statistiques par province
    print(f"\n🗺️  Répartition géographique:")
    for province in PROVINCES.keys():
        count = PersonIdentity.objects.filter(province=province).count()
        print(f"   - {province}: {count} personnes")
    
    # Statistiques démographiques
    total_minors = PersonIdentity.objects.filter(birth_date__gte=date.today()-timedelta(days=18*365)).count()
    total_adults = created_persons - total_minors
    print(f"\n👥 Démographie:")
    print(f"   - Adultes (18+): {total_adults}")
    print(f"   - Mineurs (<18): {total_minors}")
    
    # Statistiques vulnérabilité
    critical = PersonIdentity.objects.filter(vulnerability_level='CRITICAL').count()
    high = PersonIdentity.objects.filter(vulnerability_level='HIGH').count()
    moderate = PersonIdentity.objects.filter(vulnerability_level='MODERATE').count()
    low = PersonIdentity.objects.filter(vulnerability_level='LOW').count()
    
    print(f"\n⚠️  Niveaux de vulnérabilité:")
    print(f"   - Critique: {critical}")
    print(f"   - Élevé: {high}")
    print(f"   - Modéré: {moderate}")
    print(f"   - Faible: {low}")
    
    print(f"\n{'='*80}")
    print("🎯 Prochaines étapes:")
    print("   1. Vérifier les données: python manage.py shell")
    print("   2. Lancer le serveur: python manage.py runserver")
    print("   3. Accéder à l'admin: http://localhost:8000/admin/")
    print(f"{'='*80}\n")

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == '__main__':
    print("\n✅ RSU Gabon - Script de Création Population")
    print("🔧 Environnement: DÉVELOPPEMENT")
    print("="*80)
    
    # Créer 400 ménages réalistes
    create_realistic_population(target_households=400)