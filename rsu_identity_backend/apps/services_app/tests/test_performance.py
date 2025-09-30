# ===================================================================
# Tests Performance & Charge
# ===================================================================

from django.test import TestCase
from django.utils import timezone
import time
from apps.identity_app.models import PersonIdentity, Household
from apps.services_app.services import VulnerabilityService
from apps.services_app.models import GeographicInterventionCost
from decimal import Decimal


class PerformanceTest(TestCase):
    """Tests performance services"""
    
    def setUp(self):
        """Setup données test"""
        self.service = VulnerabilityService()
        
        # Créer coûts
        for i in range(1, 5):
            GeographicInterventionCost.objects.create(
                zone_key=f'ZONE_{i}',
                cost_per_person=Decimal(str(150000 - (i-1)*25000))
            )
    
    def test_single_assessment_performance(self):
        """Test performance calcul individuel"""
        # Créer personne
        household = Household.objects.create(
            household_size=5,
            monthly_income=50000
        )
        person = PersonIdentity.objects.create(
            first_name="Perf",
            last_name="TEST",
            age=30,
            gender='F',
            province='NYANGA',
            household=household
        )
        
        # Mesurer temps
        start = time.time()
        assessment = self.service.calculate_and_save_assessment(person.id)
        duration = time.time() - start
        
        print(f"\n⏱️ Temps calcul individuel: {duration:.3f}s")
        
        # Performance acceptable: < 2 secondes
        self.assertLess(duration, 2.0, 
            f"Calcul trop lent: {duration:.3f}s (max 2s)")
        self.assertIsNotNone(assessment)
    
    def test_bulk_100_assessments_performance(self):
        """Test performance bulk 100 calculs"""
        # Créer 100 personnes
        persons = []
        for i in range(100):
            household = Household.objects.create(
                household_size=5,
                monthly_income=50000
            )
            person = PersonIdentity.objects.create(
                first_name=f"Bulk{i}",
                last_name="PERF",
                age=30,
                gender='F',
                province='NYANGA',
                household=household
            )
            persons.append(person)
        
        person_ids = [p.id for p in persons]
        
        # Mesurer temps bulk
        start = time.time()
        results = self.service.bulk_calculate_assessments(
            person_ids,
            batch_size=50
        )
        duration = time.time() - start
        
        print(f"\n⏱️ Temps bulk 100 personnes: {duration:.3f}s")
        print(f"   📊 Succès: {results['success']}/100")
        print(f"   ⚡ Vitesse: {100/duration:.1f} calculs/seconde")
        
        # Performance acceptable: < 60 secondes
        self.assertLess(duration, 60.0,
            f"Bulk trop lent: {duration:.3f}s (max 60s)")
        self.assertGreaterEqual(results['success'], 95)
    
    def test_bulk_500_assessments_performance(self):
        """Test performance bulk 500 calculs (optionnel)"""
        print("\n🚀 Test Bulk 500 personnes (peut être long)...")
        
        # Créer 500 personnes
        persons = []
        provinces = ['NYANGA', 'ESTUAIRE', 'OGOOUE_LOLO', 'HAUT_OGOOUE']
        
        for i in range(500):
            household = Household.objects.create(
                household_size=4 + (i % 5),
                monthly_income=30000 + (i * 100)
            )
            person = PersonIdentity.objects.create(
                first_name=f"Bulk{i}",
                last_name="PERF500",
                age=20 + (i % 50),
                gender='F' if i % 2 == 0 else 'M',
                province=provinces[i % 4],
                household=household
            )
            persons.append(person)
        
        person_ids = [p.id for p in persons]
        
        # Mesurer temps
        start = time.time()
        results = self.service.bulk_calculate_assessments(
            person_ids,
            batch_size=100
        )
        duration = time.time() - start
        
        print(f"\n⏱️ Temps bulk 500 personnes: {duration:.1f}s")
        print(f"   📊 Succès: {results['success']}/500")
        print(f"   ⚡ Vitesse: {500/duration:.1f} calculs/seconde")
        
        # Performance acceptable: < 5 minutes
        self.assertLess(duration, 300.0,
            f"Bulk trop lent: {duration:.1f}s (max 300s)")
        self.assertGreaterEqual(results['success'], 475)  # 95%
    
    def test_statistics_generation_performance(self):
        """Test performance génération statistiques"""
        # Créer 50 assessments
        for i in range(50):
            household = Household.objects.create(
                household_size=5,
                monthly_income=50000
            )
            person = PersonIdentity.objects.create(
                first_name=f"Stats{i}",
                last_name="TEST",
                age=30,
                gender='F',
                province='NYANGA',
                household=household
            )
            self.service.calculate_and_save_assessment(person.id)
        
        # Mesurer génération stats
        start = time.time()
        stats = self.service.get_vulnerability_statistics()
        duration = time.time() - start
        
        print(f"\n⏱️ Temps génération stats: {duration:.3f}s")
        
        # Performance acceptable: < 5 secondes
        self.assertLess(duration, 5.0)
        self.assertGreaterEqual(stats['total_assessments'], 50)


# Lancer tests:
# python manage.py test apps.services_app.tests.test_performance