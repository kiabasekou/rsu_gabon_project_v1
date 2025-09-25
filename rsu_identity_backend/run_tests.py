
# =============================================================================
# FICHIER: run_tests.py (Script principal de tests)
# =============================================================================

#!/usr/bin/env python
"""
🧪 Runner principal des tests RSU Identity App
"""
import os
import sys
import django
import subprocess

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rsu_identity.settings.development')
django.setup()

def run_all_tests():
    """Exécute tous les tests Identity App"""
    
    print("🧪 TESTS COMPLETS IDENTITY APP RSU GABON")
    print("=" * 70)
    
    # 1. Tests unitaires Django
    print("\n1. Tests unitaires modèles et serializers...")
    result = subprocess.run([
        sys.executable, 'manage.py', 'test', 
        'apps.identity_app.tests.test_models',
        'apps.identity_app.tests.test_serializers',
        '--verbosity=2'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Tests unitaires réussis")
    else:
        print("❌ Échecs tests unitaires:")
        print(result.stdout)
        print(result.stderr)
    
    # 2. Tests API ViewSets
    print("\n2. Tests ViewSets et APIs...")
    result = subprocess.run([
        sys.executable, 'manage.py', 'test', 
        'apps.identity_app.tests.test_views',
        '--verbosity=2'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Tests ViewSets réussis")
    else:
        print("❌ Échecs tests ViewSets:")
        print(result.stdout)
        print(result.stderr)
    
    # 3. Tests d'intégration
    print("\n3. Tests d'intégration...")
    result = subprocess.run([
        sys.executable, 'manage.py', 'test', 
        'apps.identity_app.tests.test_integration',
        '--verbosity=2'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Tests intégration réussis")
    else:
        print("❌ Échecs tests intégration:")
        print(result.stdout)
        print(result.stderr)
    
    # 4. Coverage report
    print("\n4. Génération rapport de couverture...")
    subprocess.run([
        'coverage', 'run', '--source=apps.identity_app', 
        'manage.py', 'test', 'apps.identity_app'
    ])
    
    result = subprocess.run(['coverage', 'report'], capture_output=True, text=True)
    print("📊 Couverture de code:")
    print(result.stdout)
    
    # 5. Test API intégration (si serveur lancé)
    print("\n5. Test intégration APIs en conditions réelles...")
    try:
        import requests
        response = requests.get("http://localhost:8000/api/", timeout=5)
        if response.status_code == 200:
            print("✅ Serveur détecté - lancement tests API...")
            from test_identity_complete import test_identity_apis_complete
            test_identity_apis_complete()
        else:
            print("⚠️  Serveur non accessible pour tests API")
    except:
        print("⚠️  Serveur non lancé - tests API ignorés")
    
    print("\n" + "=" * 70)
    print("🎉 TESTS IDENTITY APP TERMINÉS")
    print("📋 Pour lancer manuellement:")
    print("   python manage.py test apps.identity_app")
    print("   python test_identity_complete.py")


if __name__ == "__main__":
    run_all_tests()