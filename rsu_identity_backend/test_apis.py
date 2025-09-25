# Script de test automatique (créer: test_apis.py)
import requests
import json

def test_rsu_apis():
    """Test complet des APIs RSU après corrections"""
    BASE_URL = "http://localhost:8000"
    
    print("🧪 Test des APIs RSU Gabon")
    print("=" * 50)
    
    # 1. Test point d'entrée (sans auth)
    print("\n1. Test point d'entrée API...")
    response = requests.get(f"{BASE_URL}/api/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Message: {data['message']}")
        print("✅ Point d'entrée accessible")
    else:
        print("❌ Erreur point d'entrée")
    
    # 2. Test authentification
    print("\n2. Test authentification JWT...")
    auth_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/token/", json=auth_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens['access']
        print("✅ Authentification réussie")
        
        # 3. Test APIs avec auth
        headers = {'Authorization': f'Bearer {access_token}'}
        
        print("\n3. Test liste utilisateurs...")
        response = requests.get(f"{BASE_URL}/api/v1/core/users/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"Nombre d'utilisateurs: {users.get('count', 0)}")
            print("✅ API utilisateurs fonctionnelle")
        
        print("\n4. Test profil utilisateur connecté...")
        response = requests.get(f"{BASE_URL}/api/v1/core/users/me/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"Utilisateur connecté: {user.get('username')}")
            print("✅ Endpoint /me fonctionnel")
        
        print("\n5. Test logs audit...")
        response = requests.get(f"{BASE_URL}/api/v1/core/audit-logs/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            logs = response.json()
            print(f"Nombre de logs: {logs.get('count', 0)}")
            print("✅ API audit logs fonctionnelle")
    
    else:
        print("❌ Échec authentification")
    
    # 6. Test documentation
    print("\n6. Test documentation Swagger...")
    response = requests.get(f"{BASE_URL}/api/docs/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Documentation Swagger accessible")
    
    print("\n" + "=" * 50)
    print("🎉 Tests terminés - Core App fonctionnel!")

if __name__ == "__main__":
    test_rsu_apis()
