#!/usr/bin/env python
"""
🇬🇦 RSU Gabon - Import Données Test FINAL
Fichier: rsu_identity_backend/import_test_data.py
"""

import os
import sys
import django
import csv
from decimal import Decimal
from datetime import datetime, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rsu_identity.settings.development')
django.setup()

from apps.identity_app.models import PersonIdentity
from apps.core_app.models import RSUUser

def import_csv_data():
    """Importer données depuis CSV"""
    
    csv_file = 'data/test_data_gabon_synthetic.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ Fichier introuvable: {csv_file}")
        return
    
    print(f"📂 Lecture fichier: {csv_file}")
    
    # Lire CSV
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    print(f"✅ {len(data)} lignes trouvées")
    
    # Admin user
    admin_user = RSUUser.objects.filter(username='admin').first()
    if not admin_user:
        print("❌ Admin user introuvable")
        return
    
    print(f"✅ Admin user: {admin_user.username}")
    
    # Importer personnes
    print("\n📥 Import personnes...")
    persons_created = 0
    errors = []
    
    for i, row in enumerate(data, 1):
        try:
            # Parser birth_date avec fallback
            birth_date = parse_date(row.get('birth_date'))
            if not birth_date:
                # ✅ Si pas de date, utiliser date par défaut
                birth_date = date(1990, 1, 1)
            
            person = PersonIdentity.objects.create(
                first_name=row.get('first_name', 'Unknown'),
                last_name=row.get('last_name', 'Unknown'),
                birth_date=birth_date,  # ✅ Toujours une valeur
                gender=row.get('gender', 'M'),
                province=row.get('province', 'ESTUAIRE'),
                department=row.get('department', ''),
                commune=row.get('commune', ''),
                phone_number=row.get('phone_number', ''),
                email=row.get('email', ''),
                address=row.get('address', ''),
                vulnerability_score=parse_decimal(row.get('vulnerability_score', 0)),
                monthly_income=parse_decimal(row.get('monthly_income', 0)),
                has_disability=parse_bool(row.get('has_disability', False)),
                education_level=row.get('education_level', 'NONE'),
                employment_status=row.get('employment_status', 'UNEMPLOYED'),
                marital_status=row.get('marital_status', 'SINGLE'),
                verification_status='VERIFIED',
                created_by=admin_user
            )
            persons_created += 1
            
            if i % 20 == 0:
                print(f"   ✅ {i}/{len(data)} personnes importées...")
                
        except Exception as e:
            errors.append((i, str(e)))
            if len(errors) <= 5:  # Afficher seulement 5 premières erreurs
                print(f"   ⚠️  Ligne {i}: {str(e)}")
            continue
    
    print(f"\n✅ {persons_created} personnes créées avec succès!")
    if errors:
        print(f"⚠️  {len(errors)} lignes ignorées")
    
    # Statistiques
    print("\n📊 STATISTIQUES:")
    print(f"   • Personnes: {PersonIdentity.objects.count()}")
    
    from django.db.models import Count
    print(f"   • Par province:")
    stats = PersonIdentity.objects.values('province').annotate(count=Count('id')).order_by('-count')
    for stat in stats:
        print(f"      - {stat['province']}: {stat['count']}")
    
    print(f"\n   • Par genre:")
    gender_stats = PersonIdentity.objects.values('gender').annotate(count=Count('id'))
    for stat in gender_stats:
        gender_label = {'M': 'Masculin', 'F': 'Féminin', 'OTHER': 'Autre'}.get(stat['gender'], stat['gender'])
        print(f"      - {gender_label}: {stat['count']}")
    
    print(f"\n   • Score vulnérabilité moyen: {PersonIdentity.objects.aggregate(avg=Count('vulnerability_score'))}")

def parse_date(date_str):
    """Parser date depuis string avec plusieurs formats"""
    if not date_str or date_str.strip() == '':
        return None
    
    # Essayer plusieurs formats
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except:
            continue
    
    return None

def parse_decimal(value):
    """Parser decimal depuis string"""
    if not value or str(value).strip() == '':
        return Decimal('0')
    try:
        # Nettoyer la valeur
        clean_value = str(value).replace(',', '.').replace(' ', '')
        return Decimal(clean_value)
    except:
        return Decimal('0')

def parse_bool(value):
    """Parser boolean depuis string"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'oui', 't', 'y')
    return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🇬🇦 RSU GABON - IMPORT DONNÉES TEST")
    print("="*60 + "\n")
    
    try:
        import_csv_data()
        print("\n" + "="*60)
        print("✅ IMPORT TERMINÉ AVEC SUCCÈS")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {str(e)}")
        import traceback
        traceback.print_exc()