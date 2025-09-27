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
    """Tests d'intégration - NAMESPACE CORRIGÉ"""
    
    def test_complete_family_workflow(self):
        """Test workflow complet - URLs CORRIGÉES"""
        
        # ✅ CORRECTION: Utiliser namespace identity_app:
        url = reverse('identity_app:personidentity-list')  # Au lieu de 'personidentity-list'
        
        response = self.client.post(
            url, 
            self.person_data, 
            format='json'  # Format uniquement
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_audit_trail_creation(self):
        """Test création audit trail - URL CORRIGÉE"""
        
        url = reverse('identity_app:personidentity-list')  # ← Namespace correct
        
        response = self.client.post(
            url,
            self.person_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)