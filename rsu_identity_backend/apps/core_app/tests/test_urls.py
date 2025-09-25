
# =============================================================================
# FICHIER: apps/core_app/tests/test_urls.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Tests URLs Core App
Tests de routing et accessibilité des endpoints
"""
from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.core_app.views import RSUUserViewSet, AuditLogViewSet

User = get_user_model()

class CoreAppURLTests(TestCase):
    """Tests de résolution des URLs Core App"""
    
    def test_users_list_url_resolves(self):
        """Test résolution URL liste utilisateurs"""
        url = reverse('core_app:users-list')
        self.assertEqual(resolve(url).func.cls, RSUUserViewSet)
    
    def test_users_detail_url_resolves(self):
        """Test résolution URL détail utilisateur"""
        url = reverse('core_app:users-detail', kwargs={'pk': 1})
        self.assertEqual(resolve(url).func.cls, RSUUserViewSet)
    
    def test_audit_logs_list_url_resolves(self):
        """Test résolution URL logs audit"""
        url = reverse('core_app:audit-logs-list')
        self.assertEqual(resolve(url).func.cls, AuditLogViewSet)

class CoreAppAPITests(APITestCase):
    """Tests d'intégration des APIs Core App"""
    
    def setUp(self):
        """Configuration des tests"""
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.ga',
            password='test123',
            user_type='ADMIN',
            employee_id='TEST-ADMIN-001'
        )
        self.surveyor_user = User.objects.create_user(
            username='surveyor_test',
            email='surveyor@test.ga', 
            password='test123',
            user_type='SURVEYOR',
            employee_id='TEST-SURV-001'
        )
    
    def test_api_root_accessible(self):
        """Test accessibilité point d'entrée API"""
        url = reverse('api-root')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('endpoints', response.data)
    
    def test_users_list_requires_auth(self):
        """Test authentification requise pour liste utilisateurs"""
        url = reverse('core_app:users-list')
        
        # Sans authentification
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_users_list_with_auth(self):
        """Test liste utilisateurs avec authentification"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('core_app:users-list')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_user_me_endpoint(self):
        """Test endpoint profil utilisateur connecté"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('core_app:users-me')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'admin_test')
    
    def test_audit_logs_admin_only(self):
        """Test accès logs audit selon permissions"""
        # Admin peut voir les logs
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('core_app:audit-logs-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Enquêteur a accès limité
        self.client.force_authenticate(user=self.surveyor_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Mais voit seulement ses propres actions
    
    def test_swagger_docs_accessible(self):
        """Test accessibilité documentation Swagger"""
        url = reverse('swagger-ui')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_create_admin_only(self):
        """Test création utilisateur - admins seulement"""
        url = reverse('core_app:users-list')
        data = {
            'username': 'new_user',
            'employee_id': 'TEST-NEW-001',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'new@test.ga',
            'password': 'newpassword123',
            'password_confirm': 'newpassword123',
            'user_type': 'OPERATOR'
        }
        
        # Enquêteur ne peut pas créer
        self.client.force_authenticate(user=self.surveyor_user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin peut créer
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)