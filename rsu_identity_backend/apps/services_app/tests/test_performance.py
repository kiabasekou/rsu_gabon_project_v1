# apps/services_app/tests/test_performance.py
"""
🧪 RSU GABON - Tests Performance Services
Tests de charge et temps de réponse
Standards: Top 1% International
"""

import time
from django.test import TestCase
from apps.services_app.services import VulnerabilityService
from .fixtures import TestDataFactory


class PerformanceTest(TestCase):
    """Tests de performance des services"""
    
    def setUp(self):
        """Configuration tests"""
        self.vuln_service = VulnerabilityService()
    
    def test_single_assessment_performance(self):
        """Test performance calcul individuel"""
        print("⏱️  Test calcul individuel...")
        
        data = TestDataFactory.create_vulnerable_household()
        person = data['person']
        
        start = time.time()
        result = self.vuln_service.calculate_and_save_assessment(person.id)
        duration = time.time() - start
        
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'vulnerability_score'))
        self.assertLess(duration, 2.0)
        
        print(f"✅ Calcul en {duration*1000:.0f}ms - Score: {result.vulnerability_score}")
    
    def test_bulk_100_assessments_performance(self):
        """Test performance bulk 100 calculs"""
        print("🚀 Test Bulk 100 personnes...")
        
        person_ids = []
        for i in range(100):
            data = TestDataFactory.create_household(
                head_person=TestDataFactory.create_person(
                    first_name=f"Test{i}",
                    last_name="BULK",
                    age_years=25 + (i % 40)
                ),
                total_monthly_income=50000 + (i * 1000),
                household_size=2 + (i % 8)
            )
            person_ids.append(data.head_of_household.id)
        
        start = time.time()
        results = self.vuln_service.bulk_calculate_assessments(person_ids)
        duration = time.time() - start
        
        self.assertEqual(results['success'], 100)
        self.assertLess(duration, 15.0)
        
        avg_time = (duration / 100) * 1000
        print(f"✅ 100 calculs en {duration:.2f}s (moy: {avg_time:.0f}ms/calcul)")
    
    def test_bulk_500_assessments_performance(self):
        """Test performance bulk 500 calculs"""
        print("🚀 Test Bulk 500 personnes (peut être long)...")
        
        person_ids = []
        for i in range(500):
            data = TestDataFactory.create_household(
                head_person=TestDataFactory.create_person(
                    first_name=f"Bulk{i}",
                    last_name="LARGE",
                    age_years=20 + (i % 50)
                ),
                total_monthly_income=30000 + (i * 500),
                household_size=1 + (i % 10)
            )
            person_ids.append(data.head_of_household.id)
        
        start = time.time()
        results = self.vuln_service.bulk_calculate_assessments(person_ids)
        duration = time.time() - start
        
        self.assertEqual(results['success'], 500)
        self.assertLess(duration, 90.0)
        
        avg_time = (duration / 500) * 1000
        print(f"✅ 500 calculs en {duration:.2f}s (moy: {avg_time:.0f}ms/calcul)")
    
    def test_statistics_generation_performance(self):
        """Test performance génération statistiques"""
        print("📊 Test génération statistiques...")
        
        for i in range(50):
            if i % 3 == 0:
                TestDataFactory.create_vulnerable_household()
            elif i % 3 == 1:
                TestDataFactory.create_middle_class_household()
            else:
                TestDataFactory.create_household(
                    head_person=TestDataFactory.create_person(
                        first_name=f"Pauvre{i}",
                        age_years=30 + i
                    ),
                    total_monthly_income=75000
                )
        
        start = time.time()
        stats = self.vuln_service.get_vulnerability_statistics()
        duration = time.time() - start
        
        self.assertIsNotNone(stats)
        self.assertIn('total_assessments', stats)
        self.assertLess(duration, 3.0)
        
        print(f"✅ Stats en {duration*1000:.0f}ms")