
# =============================================================================
# FICHIER: apps/identity_app/tests/test_serializers.py
# =============================================================================

"""
Tests des serializers Identity App
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from apps.identity_app.serializers import (
    PersonIdentitySerializer, PersonIdentityCreateSerializer,
    HouseholdSerializer, GeographicDataSerializer
)
from apps.identity_app.models import PersonIdentity, Household
from apps.core_app.models import RSUUser

class PersonIdentitySerializerTests(APITestCase):
    """Tests PersonIdentity serializers"""
    
    def setUp(self):
        self.user = RSUUser.objects.create_user(
            username='test_user',
            email='test@rsu.ga',
            password='test123',
            user_type='SURVEYOR',
            employee_id='TEST-001'
        )
        
        self.valid_person_data = {
            'first_name': 'Jean',
            'last_name': 'Doe',
            'birth_date': '1990-01-01',
            'gender': 'M',
            'phone_number': '+24177123456',
            'province': 'ESTUAIRE',
            'address': '123 Test Street'
        }
    
    def test_create_person_serializer_valid_data(self):
        """Test création avec données valides"""
        serializer = PersonIdentityCreateSerializer(data=self.valid_person_data)
        self.assertTrue(serializer.is_valid())
        
        person = serializer.save()
        self.assertEqual(person.first_name, 'Jean')
        self.assertTrue(person.rsu_id.startswith('RSU-GA-'))
    
    def test_phone_validation(self):
        """Test validation numéro téléphone"""
        invalid_data = self.valid_person_data.copy()
        invalid_data['phone_number'] = '+33123456789'  # Format français
        
        serializer = PersonIdentityCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)
    
    def test_birth_date_validation(self):
        """Test validation date naissance"""
        # Date future
        future_data = self.valid_person_data.copy()
        future_data['birth_date'] = '2030-01-01'
        
        serializer = PersonIdentityCreateSerializer(data=future_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('birth_date', serializer.errors)
    
    def test_province_validation(self):
        """Test validation province gabonaise"""
        invalid_data = self.valid_person_data.copy()
        invalid_data['province'] = 'INVALID_PROVINCE'
        
        serializer = PersonIdentityCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('province', serializer.errors)
    
    def test_gps_coordinates_validation(self):
        """Test validation coordonnées GPS Gabon"""
        # Coordonnées hors Gabon
        invalid_coords = self.valid_person_data.copy()
        invalid_coords['latitude'] = '48.8566'  # Paris
        invalid_coords['longitude'] = '2.3522'
        
        serializer = PersonIdentityCreateSerializer(data=invalid_coords)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_person_full_serializer(self):
        """Test serializer complet avec calculs"""
        person = PersonIdentity.objects.create(**self.valid_person_data)
        serializer = PersonIdentitySerializer(person)
        
        data = serializer.data
        self.assertIn('age', data)
        self.assertIn('full_name', data)
        self.assertIn('vulnerability_status', data)
        self.assertIn('province_info', data)
