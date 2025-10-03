from rest_framework.test import APITestCase
from rest_framework import status

class EmploymentFieldsTestCase(APITestCase):
    """Tests des nouveaux champs employment"""
    
    def setUp(self):
        self.user = RSUUser.objects.create_user(
            username='test_employment',
            password='Test123!',
            user_type='SURVEYOR',
            employee_id='EMP-001'
        )
        self.client.force_authenticate(self.user)
    
    def test_create_employed_person_with_employer(self):
        """Création personne employée avec employeur"""
        data = {
            'first_name': 'Jean',
            'last_name': 'Test',
            'birth_date': '1990-01-01',
            'gender': 'M',
            'province': 'ESTUAIRE',
            'occupation': 'Comptable',
            'employer': 'Total Gabon',
            'employment_status': 'EMPLOYED_FORMAL',
            'monthly_income': 250000
        }
        
        response = self.client.post('/api/v1/identity/persons/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['employer'], 'Total Gabon')
        self.assertEqual(response.data['employment_status'], 'EMPLOYED_FORMAL')
    
    def test_create_unemployed_with_employer_fails(self):
        """Validation: chômeur ne peut avoir employeur"""
        data = {
            'first_name': 'Marie',
            'last_name': 'Test',
            'birth_date': '1995-01-01',
            'gender': 'F',
            'province': 'NYANGA',
            'employment_status': 'UNEMPLOYED',
            'employer': 'Total Gabon',  # ❌ Incohérent
        }
        
        response = self.client.post('/api/v1/identity/persons/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('employer', response.data)
    
    def test_filter_by_employment_status(self):
        """Filtrage par statut emploi"""
        # Créer personnes avec différents statuts
        for i, status in enumerate(['UNEMPLOYED', 'EMPLOYED_FORMAL', 'STUDENT']):
            PersonIdentity.objects.create(
                first_name=f'Person{i}',
                last_name='Test',
                birth_date='1990-01-01',
                gender='M',
                province='ESTUAIRE',
                employment_status=status,
                created_by=self.user
            )
        
        response = self.client.get('/api/v1/identity/persons/?employment_status=UNEMPLOYED')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['employment_status'], 'UNEMPLOYED')
    
    def test_employment_statistics_endpoint(self):
        """Endpoint statistiques emploi"""
        response = self.client.get('/api/v1/identity/persons/employment_statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('statistics', response.data)
    
    def test_unemployed_vulnerable_endpoint(self):
        """Endpoint chômeurs vulnérables"""
        response = self.client.get(
            '/api/v1/identity/persons/unemployed_vulnerable/',
            {'min_household_size': 4, 'max_income': 75000}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('persons', response.data)