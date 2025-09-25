
# =============================================================================
# FICHIER: apps/identity_app/tests/test_integration.py
# =============================================================================

"""
Tests d'intégration Identity App
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.identity_app.models import PersonIdentity, Household, HouseholdMember
from apps.core_app.models import RSUUser, AuditLog

class IdentityIntegrationTests(APITestCase):
    """Tests d'intégration complets"""
    
    def setUp(self):
        self.admin = RSUUser.objects.create_user(
            username='admin',
            email='admin@rsu.ga',
            password='admin123',
            user_type='ADMIN',
            employee_id='ADMIN-001'
        )
    
    def test_complete_family_workflow(self):
        """Test workflow complet : personne → ménage → membres"""
        self.client.force_authenticate(user=self.admin)
        
        # 1. Créer chef de ménage
        person_data = {
            'first_name': 'Marie',
            'last_name': 'Mbadinga',
            'birth_date': '1975-03-15',
            'gender': 'F',
            'province': 'ESTUAIRE',
            'phone_number': '+24177123456',
            'is_household_head': True
        }
        
        url = reverse('identity_app:persons-list')
        response = self.client.post(url, person_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        head_id = response.data['id']
        
        # 2. Créer ménage
        household_data = {
            'head_of_household': head_id,
            'household_size': 3,
            'household_type': 'NUCLEAR',
            'housing_type': 'RENTED',
            'water_access': 'PIPED',
            'electricity_access': 'GRID',
            'total_monthly_income': 300000
        }
        
        url = reverse('identity_app:households-list')
        response = self.client.post(url, household_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        household_id = response.data['id']
        
        # 3. Créer conjoint
        spouse_data = {
            'first_name': 'Paul',
            'last_name': 'Mbadinga',
            'birth_date': '1970-08-20',
            'gender': 'M',
            'province': 'ESTUAIRE'
        }
        
        url = reverse('identity_app:persons-list')
        response = self.client.post(url, spouse_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        spouse_id = response.data['id']
        
        # 4. Ajouter conjoint au ménage
        member_data = {
            'person': spouse_id,
            'relationship_to_head': 'SPOUSE',
            'contributes_to_income': True,
            'monthly_contribution': 200000
        }
        
        url = reverse('identity_app:household-members-list')
        response = self.client.post(url, {**member_data, 'household': household_id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 5. Vérifier la structure finale
        url = reverse('identity_app:households-detail', kwargs={'pk': household_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['members']), 1)  # Chef + conjoint via members
    
    def test_audit_trail_creation(self):
        """Test création d'audit trail"""
        initial_logs = AuditLog.objects.count()
        
        self.client.force_authenticate(user=self.admin)
        
        # Créer personne
        url = reverse('identity_app:persons-list')
        response = self.client.post(url, {
            'first_name': 'Audit',
            'last_name': 'Test',
            'birth_date': '1990-01-01',
            'gender': 'M',
            'province': 'ESTUAIRE'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier création d'un log d'audit
        self.assertEqual(AuditLog.objects.count(), initial_logs + 1)
        
        latest_log = AuditLog.objects.latest('created_at')
        self.assertEqual(latest_log.action, 'CREATE')
        self.assertEqual(latest_log.user, self.admin)
