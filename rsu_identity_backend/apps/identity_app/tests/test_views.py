
# =============================================================================
# FICHIER: apps/identity_app/tests/test_views.py
# =============================================================================

"""
Tests des ViewSets Identity App
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.identity_app.models import PersonIdentity, Household
from apps.core_app.models import RSUUser

class PersonIdentityViewSetTests(APITestCase):
    """Tests PersonIdentityViewSet"""
    
    def setUp(self):
        # Utilisateur admin
        self.admin_user = RSUUser.objects.create_user(
            username='admin',
            email='admin@rsu.ga',
            password='test123',
            user_type='ADMIN',
            employee_id='ADMIN-001'
        )
        
        # Utilisateur enquêteur
        self.surveyor = RSUUser.objects.create_user(
            username='surveyor',
            email='surveyor@rsu.ga',
            password='test123',
            user_type='SURVEYOR',
            employee_id='SURV-001',
            assigned_provinces=['ESTUAIRE', 'HAUT_OGOOUE']
        )
        
        # Personne test
        self.person = PersonIdentity.objects.create(
            first_name='Test',
            last_name='Person',
            birth_date='1990-01-01',
            gender='M',
            province='ESTUAIRE',
            phone_number='+24177123456',
            created_by=self.admin_user
        )
        
        self.valid_person_data = {
            'first_name': 'New',
            'last_name': 'Person',
            'birth_date': '1985-05-15',
            'gender': 'F',
            'province': 'ESTUAIRE',
            'phone_number': '+24177654321'
        }
    
    def test_list_persons_requires_auth(self):
        """Test liste nécessite authentification"""
        url = reverse('identity_app:persons-list')
        response = self.client.post(
            url, 
            data, 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_persons_with_auth(self):
        """Test liste avec authentification"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('identity_app:persons-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_create_person(self):
        """Test création personne"""
        self.client.force_authenticate(user=self.surveyor)
        url = reverse('identity_app:persons-list')
        response = self.client.post(url, self.valid_person_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PersonIdentity.objects.count(), 2)
    
    def test_geographic_filtering(self):
        """Test filtrage géographique par enquêteur"""
        # Créer personne hors province assignée
        PersonIdentity.objects.create(
            first_name='Out',
            last_name='Province',
            birth_date='1990-01-01',
            gender='M',
            province='NYANGA',  # Pas dans assigned_provinces du surveyor
            created_by=self.admin_user
        )
        
        self.client.force_authenticate(user=self.surveyor)
        url = reverse('identity_app:persons-list')
        response = self.client.get(url)
        
        # Ne doit voir que les personnes de ses provinces
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['province'], 'ESTUAIRE')
    
    def test_search_duplicates(self):
        """Test recherche de doublons"""
        # Créer un doublon potentiel
        PersonIdentity.objects.create(
            first_name='Test',  # Même prénom
            last_name='Person',  # Même nom
            birth_date='1990-01-02',  # Date proche
            gender='M',
            province='ESTUAIRE',
            created_by=self.admin_user
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('identity_app:persons-search-duplicates')
        response = self.client.get(url, {
            'first_name': 'Test',
            'last_name': 'Person'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['candidates']), 0)
    
    def test_validate_nip(self):
        """Test validation NIP"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('identity_app:persons-validate-nip', kwargs={'pk': self.person.pk})
        response = self.client.post(url, {'nip': '1234567890123'})
        
        # Peut être succès ou échec selon simulation
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
    
    def test_vulnerability_report(self):
        """Test rapport vulnérabilité"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('identity_app:persons-vulnerability-report')
        response = self.client.get(url, {'province': 'ESTUAIRE'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_persons', response.data)
        self.assertIn('by_gender', response.data)

class HouseholdViewSetTests(APITestCase):
    """Tests HouseholdViewSet"""
    
    def setUp(self):
        self.user = RSUUser.objects.create_user(
            username='test_user',
            email='test@rsu.ga',
            password='test123',
            user_type='ADMIN',
            employee_id='TEST-001'
        )
        
        self.head = PersonIdentity.objects.create(
            first_name='Chef',
            last_name='Menage',
            birth_date='1980-01-01',
            gender='M',
            is_household_head=True,
            created_by=self.user
        )
    
    def test_create_household(self):
        """Test création ménage"""
        self.client.force_authenticate(user=self.user)
        url = reverse('identity_app:households-list')
        
        data = {
            'head_of_household': self.head.pk,
            'household_size': 4,
            'household_type': 'NUCLEAR',
            'housing_type': 'OWNED',
            'water_access': 'PIPED',
            'electricity_access': 'GRID'
        }
        
        # ✅ Correct
        response = self.client.post(
            url, 
            data, 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Household.objects.count(), 1)
