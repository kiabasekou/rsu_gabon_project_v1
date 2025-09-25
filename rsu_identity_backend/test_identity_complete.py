
# =============================================================================
# FICHIER: test_identity_complete.py (Script de test complet)
# =============================================================================

#!/usr/bin/env python
"""
🧪 Script de test complet Identity App
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rsu_identity.settings.development')
django.setup()

import requests
import json
from datetime import datetime

def test_identity_apis_complete():
    """Test complet des APIs Identity App"""
    BASE_URL = "http://localhost:8000"
    
    print("🧪 Test complet Identity App APIs")
    print("=" * 60)
    
    # 1. Authentification
    print("\n1. Authentification...")
    auth_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/api/v1/auth/token/", json=auth_data)
    
    if response.status_code != 200:
        print(f"❌ Échec authentification: {response.status_code}")
        return
    
    access_token = response.json()['access']
    headers = {'Authorization': f'Bearer {access_token}'}
    print("✅ Authentification réussie")
    
    # 2. Test PersonIdentity CRUD
    print("\n2. Test PersonIdentity CRUD...")
    
    # CREATE
    person_data = {
        'first_name': 'Test',
        'last_name': 'Integration',
        'birth_date': '1990-01-01',
        'gender': 'M',
        'province': 'ESTUAIRE',
        'phone_number': '+24177123456',
        'address': '123 Test Street'
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/identity/persons/", json=person_data, headers=headers)
    if response.status_code == 201:
        person_id = response.json()['id']
        print(f"✅ Création personne: {person_id}")
    else:
        print(f"❌ Échec création personne: {response.status_code} - {response.text}")
        return
    
    # READ
    response = requests.get(f"{BASE_URL}/api/v1/identity/persons/{person_id}/", headers=headers)
    if response.status_code == 200:
        person = response.json()
        print(f"✅ Lecture personne: {person['full_name']}")
    else:
        print(f"❌ Échec lecture personne: {response.status_code}")
    
    # UPDATE
    update_data = {'monthly_income': 250000}
    response = requests.patch(f"{BASE_URL}/api/v1/identity/persons/{person_id}/", json=update_data, headers=headers)
    if response.status_code == 200:
        print("✅ Mise à jour personne")
    else:
        print(f"❌ Échec mise à jour: {response.status_code}")
    
    # 3. Test recherche doublons
    print("\n3. Test recherche doublons...")
    response = requests.get(f"{BASE_URL}/api/v1/identity/persons/search_duplicates/", 
                          params={'first_name': 'Test', 'last_name': 'Integration'}, 
                          headers=headers)
    if response.status_code == 200:
        candidates = response.json()['candidates']
        print(f"✅ Recherche doublons: {len(candidates)} candidats trouvés")
    else:
        print(f"❌ Échec recherche doublons: {response.status_code}")
    
    # 4. Test validation NIP
    print("\n4. Test validation NIP...")
    nip_data = {'nip': '1234567890123'}
    response = requests.post(f"{BASE_URL}/api/v1/identity/persons/{person_id}/validate_nip/", 
                           json=nip_data, headers=headers)
    if response.status_code in [200, 400]:  # Succès ou échec simulé acceptable
        print("✅ Test validation NIP")
    else:
        print(f"❌ Erreur validation NIP: {response.status_code}")
    
    # 5. Test Household
    print("\n5. Test création ménage...")
    household_data = {
        'head_of_household': person_id,
        'household_size': 4,
        'household_type': 'NUCLEAR',
        'housing_type': 'OWNED',
        'water_access': 'PIPED',
        'electricity_access': 'GRID'
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/identity/households/", json=household_data, headers=headers)
    
    if response.status_code == 201:
        household_id = response.json()['id']
        print(f"✅ Création ménage: {household_id}")
    else:
        print(f"❌ Échec création ménage: {response.status_code} - {response.text}")
    
    # 6. Test statistiques
    print("\n6. Test rapports et statistiques...")
    response = requests.get(f"{BASE_URL}/api/v1/identity/persons/vulnerability_report/", 
                          params={'province': 'ESTUAIRE'}, headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Rapport vulnérabilité: {stats['total_persons']} personnes")
    else:
        print(f"❌ Échec rapport: {response.status_code}")
    
    # 7. Test données géographiques
    print("\n7. Test données géographiques...")
    geo_data = {
        'location_name': 'Test Location',
        'province': 'ESTUAIRE',
        'center_latitude': 0.4162,
        'center_longitude': 9.4673,
        'zone_type': 'URBAN_CENTER',
        'population_estimate': 5000
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/identity/geographic-data/", json=geo_data, headers=headers)
    if response.status_code == 201:
        print("✅ Création données géographiques")
    else:
        print(f"❌ Échec données géographiques: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎉 Tests Identity App terminés!")
    print(f"📊 Résultats - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    test_identity_apis_complete()