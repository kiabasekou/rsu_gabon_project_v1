# =============================================================================
# FICHIER: apps/identity_app/tests/test_integration.py  
# CORRECTION: Headers Content-Type pour éviter erreur 415
# =============================================================================

"""
Tests d'intégration Identity App
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.identity_app.models import PersonIdentity, Household
from apps.core_app.models import RSUUser

User = get_user_model()

class IdentityIntegrationTests(APITestCase):
    """Tests d'intégration workflow complet"""
    
    def setUp(self):
        """Configuration test avec utilisateur authentifié"""
        self.user = RSUUser.objects.create_user(
            username='integration_test',
            email='test@rsu.ga',
            password='test123',
            user_type='SURVEYOR',
            employee_id='INT-001'
        )
        
        # ✅ CORRECTION: Authentifier client API
        self.client.force_authenticate(user=self.user)
        
        self.person_data = {
            'first_name': 'Integration',
            'last_name': 'Test',
            'birth_date': '1990-01-01',
            'gender': 'M',
            'phone_number': '+24177123456',
            'province': 'ESTUAIRE',
            'address': '123 Test Street'
        }
        
        self.household_data = {
            'head_name': 'Chef Ménage Test',
            'province': 'ESTUAIRE',
            'commune': 'Libreville',
            'address': '456 Family Street',
            'total_members': 3
        }
    
    def test_complete_family_workflow(self):
        """Test workflow complet : personne → ménage → membres"""
        
        # 1. Créer personne (chef ménage)
        url = reverse('personidentity-list')
        
        # ✅ CORRECTION: Spécifier Content-Type JSON explicitement
        response = self.client.post(
            url, 
            self.person_data, 
            format='json',  # Force format JSON
            content_type='application/json'  # Header explicite
        )
        
        # Debug en cas d'erreur
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Erreur création personne: {response.status_code}")
            print(f"Response data: {response.data}")
            print(f"Content-Type: {response.get('Content-Type', 'Non défini')}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        person_id = response.data['id']
        rsu_id = response.data['rsu_id']
        
        # Vérifications personne créée
        self.assertTrue(rsu_id.startswith('RSU-GA-'))
        self.assertEqual(response.data['first_name'], 'Integration')
        
        # 2. Créer ménage avec cette personne comme chef
        household_data = self.household_data.copy()
        household_data['head'] = person_id
        
        household_url = reverse('household-list')
        household_response = self.client.post(
            household_url,
            household_data,
            format='json',
            content_type='application/json'
        )
        
        self.assertEqual(household_response.status_code, status.HTTP_201_CREATED)
        household_id = household_response.data['id']
        
        # 3. Ajouter membre au ménage
        member_data = {
            'first_name': 'Membre',
            'last_name': 'Test',
            'birth_date': '1995-05-15',
            'gender': 'F',
            'phone_number': '+24177234567',
            'province': 'ESTUAIRE',
            'relationship_to_head': 'SPOUSE'
        }
        
        member_response = self.client.post(
            url,
            member_data,
            format='json',
            content_type='application/json'
        )
        
        self.assertEqual(member_response.status_code, status.HTTP_201_CREATED)
        
        # 4. Vérifier intégrité données
        person = PersonIdentity.objects.get(id=person_id)
        self.assertIsNotNone(person.rsu_id)
        self.assertEqual(person.full_name, 'Integration Test')
        
        # 5. Vérifier scoring automatique
        self.assertGreaterEqual(person.data_completeness_score, 0)
    
    def test_audit_trail_creation(self):
        """Test création d'audit trail"""
        from apps.core_app.models import AuditLog
        
        # Compter logs avant
        initial_logs = AuditLog.objects.count()
        
        # Créer personne (doit générer log)
        url = reverse('personidentity-list')
        
        # ✅ CORRECTION: Headers Content-Type appropriés
        response = self.client.post(
            url, 
            self.person_data, 
            format='json',
            content_type='application/json',
            HTTP_ACCEPT='application/json'  # Header Accept explicite
        )
        
        # Debug détaillé si erreur
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.items())}")
            print(f"Content: {response.content.decode()}")
            print(f"Request headers: {self.client.defaults}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier génération audit log
        final_logs = AuditLog.objects.count()
        self.assertGreater(final_logs, initial_logs, 
                          "Un audit log devrait être créé lors de la création d'une personne")
        
        # Vérifier contenu audit log
        latest_log = AuditLog.objects.latest('created_at')
        self.assertEqual(latest_log.action, 'CREATE')
        self.assertEqual(latest_log.user, self.user)
        self.assertIn('PersonIdentity', latest_log.description)
        
    def test_geographic_data_integration(self):
        """Test intégration données géographiques"""
        from apps.identity_app.models import GeographicData
        
        # Créer données géographiques
        geo_data = GeographicData.objects.create(
            location_name='Test Location',
            province='ESTUAIRE',
            district='Test District',
            latitude=-0.3976,  # Libreville
            longitude=9.4573,
            distance_to_hospital=5,
            distance_to_school=2,
            has_electricity=True,
            has_water=True,
            has_road_access=True,
            created_by=self.user
        )
        
        # Vérifier calcul automatique score
        geo_data.refresh_from_db()
        self.assertGreater(geo_data.accessibility_score, 0)
        
        # Créer personne liée à cette zone
        person_data = self.person_data.copy()
        person_data.update({
            'latitude': str(geo_data.latitude),
            'longitude': str(geo_data.longitude),
            'district': geo_data.district
        })
        
        url = reverse('personidentity-list')
        response = self.client.post(
            url,
            person_data,
            format='json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier cohérence géographique
        person = PersonIdentity.objects.get(id=response.data['id'])
        self.assertEqual(person.province, geo_data.province)
        self.assertEqual(str(person.latitude), str(geo_data.latitude))
        
    def test_error_handling_and_validation(self):
        """Test gestion erreurs et validations"""
        url = reverse('personidentity-list')
        
        # Test données invalides
        invalid_data = {
            'first_name': '',  # Requis
            'birth_date': '2030-01-01',  # Date future
            'phone_number': '+33123456789',  # Non gabonais
            'latitude': '48.8566',  # Hors Gabon (Paris)
            'longitude': '2.3522'
        }
        
        response = self.client.post(
            url,
            invalid_data,
            format='json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Vérifier erreurs spécifiques
        errors = response.data
        self.assertIn('first_name', errors)
        self.assertIn('birth_date', errors)
        self.assertIn('phone_number', errors)
        self.assertIn('non_field_errors', errors)  # GPS validation
        
    def test_duplicate_detection_workflow(self):
        """Test workflow détection doublons"""
        # Créer première personne
        url = reverse('personidentity-list')
        response1 = self.client.post(
            url,
            self.person_data,
            format='json',
            content_type='application/json'
        )
        
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Tenter créer doublon similaire
        similar_data = self.person_data.copy()
        similar_data['phone_number'] = '+24177123457'  # Légèrement différent
        
        response2 = self.client.post(
            url,
            similar_data,
            format='json',
            content_type='application/json'
        )
        
        # Devrait réussir mais avec warning potentiel doublon
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        # Test endpoint recherche doublons
        duplicate_url = reverse('personidentity-search-duplicates')
        search_response = self.client.post(
            duplicate_url,
            {
                'first_name': 'Integration',
                'last_name': 'Test',
                'birth_date': '1990-01-01'
            },
            format='json',
            content_type='application/json'
        )
        
        self.assertEqual(search_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(search_response.data), 1)