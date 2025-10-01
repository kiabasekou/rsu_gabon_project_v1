from django.test import TestCase
from apps.services_app.services import VulnerabilityService, GeotargetingService
from apps.services_app.models import GeographicInterventionCost
from .fixtures import TestDataFactory


class ServicesIntegrationTest(TestCase):
    """Tests d'intégration entre services"""
    
    def setUp(self):
        """Configuration tests"""
        self.vuln_data = TestDataFactory.create_vulnerable_household()
        self.person = self.vuln_data['person']
        self.household = self.vuln_data['household']
        
        self.vuln_service = VulnerabilityService()
        self.geo_service = GeotargetingService()
        
        # Créer coûts géographiques
        GeographicInterventionCost.objects.create(
            zone_key='ZONE_1',
            cost_per_person=150000
        )
    
    def test_vulnerability_service(self):
        """Test VulnerabilityService"""
        result = self.vuln_service.calculate_and_save_assessment(self.person.id)
        
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'vulnerability_score'))
        self.assertTrue(hasattr(result, 'risk_level'))
        
        score = result.vulnerability_score
        self.assertGreaterEqual(float(score), 60)
        
        print(f"✅ Vulnerability - Score: {score} - Niveau: {result.risk_level}")
    
    def test_geotargeting_service(self):
        """Test GeotargetingService"""
        result = self.geo_service.analyze_geographic_vulnerability()
        
        self.assertIsNotNone(result)
        # Le résultat est un dict avec des stats par province
        self.assertIsInstance(result, dict)
        
        print(f"✅ Geotargeting - Analyse complétée")

    def test_end_to_end_workflow(self):
        """Test workflow complet"""
        print("\n🔄 Test Workflow Complet...")
        
        # 1. Vulnérabilité
        vuln_result = self.vuln_service.calculate_and_save_assessment(self.person.id)
        self.assertIsNotNone(vuln_result)
        print(f"   1️⃣ Score: {vuln_result.vulnerability_score}")
        
        # 2. Géociblage
        geo_result = self.geo_service.analyze_geographic_vulnerability()
        self.assertIsNotNone(geo_result)
        print(f"   2️⃣ Analyse géographique complétée")
        
        print("✅ Workflow complet OK")