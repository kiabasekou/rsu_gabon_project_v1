from django.test import TestCase
from apps.identity_app.models import PersonIdentity
from apps.services_app.services import (
    VulnerabilityService,
    EligibilityService,
    GeotargetingService
)

class ServicesIntegrationTest(TestCase):
    """Tests d'intégration des services métier"""
    
    def setUp(self):
        # Créer données de test
        self.person = PersonIdentity.objects.create(
            first_name="Test",
            last_name="GABON",
            age=35,
            gender='F',
            province='OGOOUE_IVINDO'
        )
    
    def test_vulnerability_service(self):
        """Test VulnerabilityService"""
        service = VulnerabilityService()
        assessment = service.calculate_and_save_assessment(self.person.id)
        
        self.assertIsNotNone(assessment)
        self.assertGreaterEqual(assessment.global_score, 0)
        self.assertLessEqual(assessment.global_score, 100)
    
    def test_eligibility_service(self):
        """Test EligibilityService"""
        service = EligibilityService()
        # Créer programme de test d'abord
        # eligibility = service.calculate_program_eligibility(...)
        pass
    
    def test_geotargeting_service(self):
        """Test GeotargetingService"""
        service = GeotargetingService()
        analysis = service.analyze_geographic_vulnerability()
        
        self.assertIn('provinces_analyzed', analysis)