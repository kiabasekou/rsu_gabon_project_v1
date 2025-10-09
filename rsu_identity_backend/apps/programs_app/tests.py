"""
🇬🇦 RSU Gabon - Programs App Tests
Fichier: apps/programs_app/tests.py
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.core_app.models import RSUUser
from apps.identity_app.models import PersonIdentity
from .models import ProgramCategory, SocialProgram, ProgramEnrollment
from decimal import Decimal


class ProgramsAPITest(APITestCase):
    """Tests APIs Programs"""
    
    def setUp(self):
        # Créer utilisateur
        self.user = RSUUser.objects.create_user(
            username='testprograms',
            email='test@programs.ga',
            password='TestPass123!',
            user_type='ADMIN',
            employee_id='PROG-001'
        )
        
        # Authentifier
        self.client = APIClient()
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'testprograms',
            'password': 'TestPass123!'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Créer catégorie
        self.category = ProgramCategory.objects.create(
            name='Transferts Monétaires',
            description='Programmes de transferts directs'
        )
    
    def test_create_program(self):
        """Test création programme"""
        data = {
            'code': 'TMC-2025',
            'name': 'Transfert Monétaire Conditionnel',
            'category': self.category.id,
            'description': 'Programme de soutien aux familles vulnérables',
            'status': 'DRAFT',
            'start_date': '2025-01-01',
            'total_budget': 1000000000,
            'benefit_amount': 50000,
            'frequency': 'MONTHLY',
            'eligibility_criteria': {
                'vulnerability_min': 50
            },
            'target_provinces': ['ESTUAIRE', 'NGOUNIE']
        }
        
        response = self.client.post('/api/v1/programs/programs/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 'TMC-2025')
        self.assertIn('id', response.data)
    
    def test_list_programs(self):
        """Test liste programmes"""
        response = self.client.get('/api/v1/programs/programs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)