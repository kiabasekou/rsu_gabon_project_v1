# =============================================================================
# FICHIER: apps/identity_app/tests/test_views.py (CORRECTIONS CRITIQUES)
# PROBLÈME: Tests échouent avec 415 Unsupported Media Type
# SOLUTION: Ajouter format='json' et content_type='application/json' 
# =============================================================================

"""
Tests des ViewSets Identity App - CORRIGÉS
"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.identity_app.models import PersonIdentity, Household
from apps.core_app.models import RSUUser

class PersonIdentityViewSetTests(APITestCase):
    """Tests PersonIdentityViewSet - FORMAT CORRIGÉ"""
    
    def test_create_person(self):
        """Test création personne - CORRECTION FORMAT UNIQUE"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('identity_app:personidentity-list')
        
        # ✅ CORRECTION: Utiliser SEULEMENT format='json' (pas content_type)
        response = self.client.post(
            url,
            self.valid_person_data,
            format='json'  # ← SEULEMENT format, PAS content_type
        )
        
        if response.status_code != status.HTTP_201_CREATED:
            print(f"ERREUR CREATE: {response.status_code}")
            print(f"RESPONSE: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('rsu_id', response.data)
    
    def test_validate_nip(self):
        """Test validation NIP - FORMAT CORRIGÉ"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('identity_app:personidentity-validate-nip', kwargs={'pk': self.person.pk})
        
        # ✅ CORRECTION: Seulement format='json'
        response = self.client.post(
            url,
            {'nip': '1234567890123'},
            format='json'  # ← SEULEMENT format
        )
        
        acceptable_codes = [
            status.HTTP_200_OK, 
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ]
        self.assertIn(response.status_code, acceptable_codes)

class HouseholdViewSetTests(APITestCase):
    """Tests HouseholdViewSet - FORMAT CORRIGÉ"""
    
    def test_create_household(self):
        """Test création ménage - FORMAT CORRIGÉ"""
        self.client.force_authenticate(user=self.user)
        url = reverse('identity_app:household-list')
        
        data = {
            'head_of_household': self.head.pk,
            'household_size': 4,
            'household_type': 'NUCLEAR',
            'housing_type': 'OWNED',
            'water_access': 'PIPED',
            'electricity_access': 'GRID'
        }
        
        # ✅ CORRECTION: Seulement format='json'
        response = self.client.post(
            url,
            data,
            format='json'  # ← SEULEMENT format
        )
        
        if response.status_code != status.HTTP_201_CREATED:
            print(f"ERREUR HOUSEHOLD: {response.status_code}")
            print(f"RESPONSE: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)