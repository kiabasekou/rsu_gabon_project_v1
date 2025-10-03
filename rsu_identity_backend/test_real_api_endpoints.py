#!/usr/bin/env python
"""
🧪 RSU GABON - TESTS APIS RÉELS
Basé sur l'architecture réelle du repository GitHub
Tests des endpoints existants uniquement
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rsu_identity.settings.development')
django.setup()

from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from apps.core_app.models import RSUUser
from apps.identity_app.models import PersonIdentity, Household
from apps.services_app.models import VulnerabilityAssessment
from decimal import Decimal


class APIRootTest(APITestCase):
    """Test point d'entrée API"""
    
    def test_api_root(self):
        """Test GET /api/"""
        print("\n🔍 Test 1: API Root...")
        
        client = APIClient()
        response = client.get('/api/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('endpoints', response.data)
        
        print(f"   ✅ API Root accessible")
        print(f"   ✅ Version: {response.data.get('version')}")
        print("✅ Test 1 PASSED\n")


class AuthenticationTest(APITestCase):
    """Tests authentification JWT"""
    
    def setUp(self):
        self.user = RSUUser.objects.create_user(
            username='testjwt',
            email='testjwt@rsu.ga',
            password='TestPass123!',
            user_type='ADMIN',
            employee_id='JWT-001'
        )
    
    def test_01_obtain_token(self):
        """Test POST /api/v1/auth/token/"""
        print("\n🔍 Test 2: Obtention token JWT...")
        
        client = APIClient()
        response = client.post('/api/v1/auth/token/', {
            'username': 'testjwt',
            'password': 'TestPass123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        print(f"   ✅ Access token: {response.data['access'][:30]}...")
        print(f"   ✅ Refresh token: {response.data['refresh'][:30]}...")
        print("✅ Test 2 PASSED\n")
    
    def test_02_refresh_token(self):
        """Test POST /api/v1/auth/token/refresh/"""
        print("\n🔍 Test 3: Rafraîchissement token...")
        
        client = APIClient()
        
        # Obtenir refresh token
        token_resp = client.post('/api/v1/auth/token/', {
            'username': 'testjwt',
            'password': 'TestPass123!'
        }, format='json')
        
        refresh_token = token_resp.data['refresh']
        
        # Rafraîchir
        response = client.post('/api/v1/auth/token/refresh/', {
            'refresh': refresh_token
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        
        print("   ✅ Token rafraîchi avec succès")
        print("✅ Test 3 PASSED\n")
    
    def test_03_invalid_credentials(self):
        """Test credentials invalides"""
        print("\n🔍 Test 4: Credentials invalides...")
        
        client = APIClient()
        response = client.post('/api/v1/auth/token/', {
            'username': 'testjwt',
            'password': 'WrongPassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        print("   ✅ Accès refusé comme attendu (401)")
        print("✅ Test 4 PASSED\n")


class CoreAPITest(APITestCase):
    """Tests Core App APIs"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = RSUUser.objects.create_user(
            username='testcore',
            email='testcore@rsu.ga',
            password='TestPass123!',
            user_type='ADMIN',
            employee_id='CORE-001'
        )
        
        # Authentifier
        token_resp = self.client.post('/api/v1/auth/token/', {
            'username': 'testcore',
            'password': 'TestPass123!'
        }, format='json')
        
        self.token = token_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_01_list_users(self):
        """Test GET /api/v1/core/users/"""
        print("\n🔍 Test 5: Liste utilisateurs...")
        
        response = self.client.get('/api/v1/core/users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        print(f"   ✅ {len(response.data['results'])} utilisateur(s)")
        print("✅ Test 5 PASSED\n")
    
    def test_02_retrieve_user(self):
        """Test GET /api/v1/core/users/{id}/"""
        print("\n🔍 Test 6: Détails utilisateur...")
        
        response = self.client.get(f'/api/v1/core/users/{self.user.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testcore')
        
        print(f"   ✅ Utilisateur: {response.data['username']}")
        print("✅ Test 6 PASSED\n")


class IdentityAPITest(APITestCase):
    """Tests Identity App APIs"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = RSUUser.objects.create_user(
            username='testidentity',
            email='testidentity@rsu.ga',
            password='TestPass123!',
            user_type='SURVEYOR',
            employee_id='ID-001',
            assigned_provinces=['ESTUAIRE', 'NYANGA']  # ✅ AJOUT CRITIQUE
        )
        
        # Authentifier
        token_resp = self.client.post('/api/v1/auth/token/', {
            'username': 'testidentity',
            'password': 'TestPass123!'
        }, format='json')
        
        self.token = token_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_01_list_persons(self):
        """Test GET /api/v1/identity/persons/"""
        print("\n🔍 Test 7: Liste personnes...")
        
        # Créer personnes test
        for i in range(3):
            PersonIdentity.objects.create(
                first_name=f'Test{i}',
                last_name='Person',
                birth_date='1990-01-01',
                gender='M',
                province='ESTUAIRE',
                created_by=self.user
            )
        
        response = self.client.get('/api/v1/identity/persons/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 3)
        
        print(f"   ✅ {len(response.data['results'])} personne(s)")
        print("✅ Test 7 PASSED\n")
    
    def test_02_create_person(self):
        """Test POST /api/v1/identity/persons/"""
        print("\n🔍 Test 8: Création personne...")
        
        data = {
            'first_name': 'Jean',
            'last_name': 'Mbanda',
            'birth_date': '1985-06-15',
            'gender': 'M',
            'province': 'ESTUAIRE',
            'phone_number': '+24177123456'
        }
        
        response = self.client.post('/api/v1/identity/persons/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'Jean')
        self.assertIn('rsu_id', response.data)
        
        print(f"   ✅ Personne créée: {response.data['rsu_id']}")
        print("✅ Test 8 PASSED\n")
    
    def test_03_retrieve_person(self):
        """Test GET /api/v1/identity/persons/{id}/"""
        print("\n🔍 Test 9: Détails personne...")
        
        person = PersonIdentity.objects.create(
            first_name='Marie',
            last_name='Nguema',
            birth_date='1990-01-01',
            gender='F',
            province='ESTUAIRE',
            created_by=self.user
        )
        
        response = self.client.get(f'/api/v1/identity/persons/{person.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Marie')
        
        print(f"   ✅ Personne: {response.data['full_name']}")
        print("✅ Test 9 PASSED\n")
    
    def test_04_update_person(self):
        """Test PATCH /api/v1/identity/persons/{id}/"""
        print("\n🔍 Test 10: Mise à jour personne...")
        
        person = PersonIdentity.objects.create(
            first_name='Update',
            last_name='Test',
            birth_date='1990-01-01',
            gender='M',
            province='ESTUAIRE',
            monthly_income=100000,
            created_by=self.user
        )
        
        response = self.client.patch(
            f'/api/v1/identity/persons/{person.id}/',
            {'monthly_income': 150000},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['monthly_income'], '150000.00')
        
        print("   ✅ Revenu mis à jour: 100k → 150k FCFA")
        print("✅ Test 10 PASSED\n")
    
    def test_05_filter_persons_by_province(self):
        """Test GET /api/v1/identity/persons/?province=NYANGA"""
        print("\n🔍 Test 11: Filtrage par province...")
        
        PersonIdentity.objects.create(
            first_name='Nyanga',
            last_name='Test',
            birth_date='1990-01-01',
            gender='M',
            province='NYANGA',
            created_by=self.user
        )
        
        response = self.client.get('/api/v1/identity/persons/?province=NYANGA')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        
        print(f"   ✅ {len(response.data['results'])} personne(s) NYANGA")
        print("✅ Test 11 PASSED\n")
    
    def test_06_list_households(self):
        """Test GET /api/v1/identity/households/"""
        print("\n🔍 Test 12: Liste ménages...")
        
        person = PersonIdentity.objects.create(
            first_name='Chef',
            last_name='Menage',
            birth_date='1980-01-01',
            gender='M',
            province='ESTUAIRE',
            created_by=self.user
        )
        
        Household.objects.create(
            head_of_household=person,
            household_size=5,
            total_monthly_income=120000,
            province='ESTUAIRE',
            created_by=self.user
        )
        
        response = self.client.get('/api/v1/identity/households/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
        
        print(f"   ✅ {len(response.data['results'])} ménage(s)")
        print("✅ Test 12 PASSED\n")


class ServicesAPITest(APITestCase):
    """Tests Services App APIs"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = RSUUser.objects.create_user(
            username='testservices',
            email='testservices@rsu.ga',
            password='TestPass123!',
            user_type='ADMIN',
            employee_id='SRV-001'
        )
        
        # Authentifier
        token_resp = self.client.post('/api/v1/auth/token/', {
            'username': 'testservices',
            'password': 'TestPass123!'
        }, format='json')
        
        self.token = token_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Créer personne test
        self.person = PersonIdentity.objects.create(
            first_name='Vulnerable',
            last_name='Test',
            birth_date='1990-01-01',
            gender='M',
            province='NYANGA',
            monthly_income=40000,
            created_by=self.user
        )
        
        self.household = Household.objects.create(
            head_of_household=self.person,
            household_size=7,
            total_monthly_income=40000,
            province='NYANGA',
            created_by=self.user
        )
    
    def test_01_list_vulnerability_assessments(self):
        """Test GET /api/v1/services/vulnerability-assessments/"""
        print("\n🔍 Test 13: Liste assessments vulnérabilité...")
        
        # Créer assessment
        VulnerabilityAssessment.objects.create(
            person=self.person,
            vulnerability_score=Decimal('75.50'),
            risk_level='HIGH',
            household_composition_score=Decimal('60.00'),
            economic_vulnerability_score=Decimal('80.00'),
            social_vulnerability_score=Decimal('70.00'),
            created_by=self.user
        )
        
        response = self.client.get('/api/v1/services/vulnerability-assessments/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
        
        print(f"   ✅ {len(response.data['results'])} assessment(s)")
        print("✅ Test 13 PASSED\n")
    
    def test_02_filter_by_risk_level(self):
        """Test GET /api/v1/services/vulnerability-assessments/?risk_level=CRITICAL"""
        print("\n🔍 Test 14: Filtrage par niveau risque...")
        
        # Créer assessments
        person_critical = PersonIdentity.objects.create(
            first_name='Critical',
            last_name='Test',
            birth_date='1990-01-01',
            gender='M',
            province='NYANGA',
            created_by=self.user
        )
        
        VulnerabilityAssessment.objects.create(
            person=person_critical,
            vulnerability_score=Decimal('85.00'),
            risk_level='CRITICAL',
            household_composition_score=Decimal('80.00'),
            economic_vulnerability_score=Decimal('90.00'),
            social_vulnerability_score=Decimal('85.00'),
            created_by=self.user
        )
        
        response = self.client.get('/api/v1/services/vulnerability-assessments/?risk_level=CRITICAL')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        
        for assessment in response.data['results']:
            self.assertEqual(assessment['risk_level'], 'CRITICAL')
        
        print(f"   ✅ {len(response.data['results'])} assessment(s) CRITICAL")
        print("✅ Test 14 PASSED\n")


class UnauthorizedAccessTest(APITestCase):
    """Tests accès non autorisés"""
    
    def test_01_no_token(self):
        """Test accès sans token"""
        print("\n🔍 Test 15: Accès sans token...")
        
        client = APIClient()
        response = client.get('/api/v1/identity/persons/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        print("   ✅ Accès refusé (401)")
        print("✅ Test 15 PASSED\n")
    
    def test_02_invalid_token(self):
        """Test token invalide"""
        print("\n🔍 Test 16: Token invalide...")
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer INVALID_TOKEN_123')
        
        response = client.get('/api/v1/identity/persons/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        print("   ✅ Token invalide rejeté (401)")
        print("✅ Test 16 PASSED\n")


def run_all_tests():
    """Execute tous les tests API"""
    from django.core.management import call_command
    
    print("\n" + "=" * 70)
    print("🧪 RSU GABON - TESTS APIs REST (ARCHITECTURE RÉELLE)")
    print("=" * 70)
    print("Basé sur le repository GitHub\n")
    
    test_classes = [
        'test_real_api_endpoints.APIRootTest',
        'test_real_api_endpoints.AuthenticationTest',
        'test_real_api_endpoints.CoreAPITest',
        'test_real_api_endpoints.IdentityAPITest',
        'test_real_api_endpoints.ServicesAPITest',
        'test_real_api_endpoints.UnauthorizedAccessTest'
    ]
    
    for test_class in test_classes:
        call_command('test', test_class, verbosity=2)
    
    print("\n" + "=" * 70)
    print("✅ ✅ ✅ TESTS APIs TERMINÉS ✅ ✅ ✅")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()