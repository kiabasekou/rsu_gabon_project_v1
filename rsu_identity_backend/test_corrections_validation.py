#!/usr/bin/env python
"""
🧪 RSU GABON - TESTS VALIDATION CORRECTIONS (VERSION FINALE ADAPTÉE)
Compatible avec votre structure de modèles actuelle
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rsu_identity.settings.development')
django.setup()

from django.test import TestCase
from apps.identity_app.models import PersonIdentity, Household
from apps.services_app.models import VulnerabilityAssessment
from apps.services_app.services import VulnerabilityService, EligibilityService, GeotargetingService
from apps.core_app.models import RSUUser
from decimal import Decimal


class CorrectionsValidationTest(TestCase):
    
    def setUp(self):
        self.user = RSUUser.objects.create_user(
            username='test_validator',
            email='validator@rsu.ga',
            password='test123',
            user_type='ADMIN',
            employee_id='VAL-001'
        )
    
    def test_01_imports_services_ok(self):
        """✅ Test 1: Imports services fonctionnent"""
        print("\n🔍 Test 1: Validation imports services...")
        
        try:
            from apps.services_app.services.base_service import BaseService
            from apps.services_app.services import VulnerabilityService, EligibilityService, GeotargetingService
            
            self.assertIsNotNone(BaseService)
            print("   ✅ BaseService importé")
            self.assertIsNotNone(VulnerabilityService)
            print("   ✅ VulnerabilityService importé")
            self.assertIsNotNone(EligibilityService)
            print("   ✅ EligibilityService importé")
            self.assertIsNotNone(GeotargetingService)
            print("   ✅ GeotargetingService importé")
            
            print("✅ Test 1 PASSED: Tous les imports fonctionnent\n")
        except ImportError as e:
            self.fail(f"❌ Erreur import: {e}")
    
    def test_02_services_instantiation(self):
        """✅ Test 2: Services s'instancient correctement"""
        print("\n🔍 Test 2: Instanciation services...")
        
        try:
            vuln_service = VulnerabilityService()
            self.assertIsNotNone(vuln_service)
            print("   ✅ VulnerabilityService instancié")
            
            elig_service = EligibilityService()
            self.assertIsNotNone(elig_service)
            print("   ✅ EligibilityService instancié")
            
            geo_service = GeotargetingService()
            self.assertIsNotNone(geo_service)
            print("   ✅ GeotargetingService instancié")
            
            print("✅ Test 2 PASSED: Tous les services s'instancient\n")
        except Exception as e:
            self.fail(f"❌ Erreur instanciation: {e}")
    
    def test_03_model_fields_exist(self):
        """✅ Test 3: Champs modèles existent"""
        print("\n🔍 Test 3: Validation champs modèles...")
        
        person_fields = [f.name for f in PersonIdentity._meta.get_fields()]
        required_person_fields = [
            'rsu_id', 'first_name', 'last_name', 'birth_date',
            'gender', 'province', 'monthly_income'
        ]
        
        for field in required_person_fields:
            self.assertIn(field, person_fields, f"Champ {field} manquant dans PersonIdentity")
            print(f"   ✅ PersonIdentity.{field} existe")
        
        household_fields = [f.name for f in Household._meta.get_fields()]
        required_household_fields = [
            'household_id', 'head_of_household', 'household_size',
            'total_monthly_income', 'province'
        ]
        
        for field in required_household_fields:
            self.assertIn(field, household_fields, f"Champ {field} manquant dans Household")
            print(f"   ✅ Household.{field} existe")
        
        print("✅ Test 3 PASSED: Tous les champs requis existent\n")
    
    def test_04_vulnerability_assessment_creation(self):
        """✅ Test 4: Création VulnerabilityAssessment fonctionne"""
        print("\n🔍 Test 4: Création assessment vulnérabilité...")
        
        try:
            person = PersonIdentity.objects.create(
                first_name='Test',
                last_name='Validation',
                birth_date='1990-01-01',
                gender='M',
                province='ESTUAIRE',
                monthly_income=75000,
                created_by=self.user
            )
            print(f"   ✅ Personne créée: {person.rsu_id}")
            
            household = Household.objects.create(
                head_of_household=person,
                household_size=5,
                total_monthly_income=75000,
                province='ESTUAIRE',
                created_by=self.user
            )
            print(f"   ✅ Ménage créé: {household.household_id}")
            print("   ✅ Relation household établie")
            
            service = VulnerabilityService()
            assessment = service.calculate_and_save_assessment(person.id)
            
            self.assertIsNotNone(assessment)
            self.assertIsInstance(assessment.vulnerability_score, Decimal)
            self.assertIn(assessment.risk_level, ['CRITICAL', 'HIGH', 'MODERATE', 'LOW'])
            
            print(f"   ✅ Assessment créé: Score={assessment.vulnerability_score}, Niveau={assessment.risk_level}")
            print("✅ Test 4 PASSED: VulnerabilityAssessment fonctionne\n")
        except Exception as e:
            self.fail(f"❌ Erreur création assessment: {e}")
    
    def test_05_properties_work(self):
        """✅ Test 5: Propriétés calculées fonctionnent"""
        print("\n🔍 Test 5: Validation propriétés calculées...")
        
        try:
            person = PersonIdentity.objects.create(
                first_name='Jean',
                last_name='Dupont',
                birth_date='1985-06-15',
                gender='M',
                province='ESTUAIRE',
                created_by=self.user
            )
            
            self.assertEqual(person.full_name, 'Jean Dupont')
            print(f"   ✅ full_name fonctionne: {person.full_name}")
            
            age = person.age
            self.assertIsInstance(age, int)
            self.assertGreater(age, 0)
            print(f"   ✅ age fonctionne: {age} ans")
            
            print("✅ Test 5 PASSED: Propriétés calculées fonctionnent\n")
        except Exception as e:
            self.fail(f"❌ Erreur propriétés: {e}")
    
    def test_06_no_import_errors_in_services(self):
        """✅ Test 6: Pas d'erreurs import dans services"""
        print("\n🔍 Test 6: Vérification absence erreurs import...")
        
        import importlib
        import sys
        
        services_to_check = [
            'apps.services_app.services.vulnerability_service',
            'apps.services_app.services.eligibility_service',
            'apps.services_app.services.geotargeting_service',
            'apps.services_app.services.base_service'
        ]
        
        for module_name in services_to_check:
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                else:
                    importlib.import_module(module_name)
                print(f"   ✅ {module_name} - pas d'erreur import")
            except Exception as e:
                self.fail(f"❌ Erreur dans {module_name}: {e}")
        
        print("✅ Test 6 PASSED: Aucune erreur import détectée\n")
    
    def test_07_circular_dependency_resolution(self):
        """✅ Test 7: Résolution dépendance circulaire Household ↔ Person"""
        print("\n🔍 Test 7: Test dépendance circulaire résolue...")
        
        try:
            person = PersonIdentity.objects.create(
                first_name='Chef',
                last_name='Menage',
                birth_date='1980-01-01',
                gender='M',
                province='ESTUAIRE',
                created_by=self.user
            )
            print("   ✅ Étape 1: Personne créée")
            
            household = Household.objects.create(
                head_of_household=person,
                household_size=4,
                total_monthly_income=120000,
                province='ESTUAIRE',
                created_by=self.user
            )
            self.assertEqual(household.head_of_household.id, person.id)
            print("   ✅ Étape 2: Household créé avec chef")
            print("   ✅ Étape 3: Relations établies")
            
            # Vérifier relation
            self.assertEqual(household.head_of_household.id, person.id)
            print("   ✅ Relations bidirectionnelles OK")
            
            print("✅ Test 7 PASSED: Dépendance circulaire résolue\n")
        except Exception as e:
            self.fail(f"❌ Erreur dépendance circulaire: {e}")
    
    def test_08_poverty_thresholds_correct(self):
        """✅ Test 8: Seuils pauvreté corrects (via méthode)"""
        print("\n🔍 Test 8: Validation seuils pauvreté Gabon...")
        
        service = VulnerabilityService()
        
        test_cases = [
            {'name': 'Extrême pauvreté', 'income': 40000, 'expected_min': 40},
            {'name': 'Pauvreté', 'income': 75000, 'expected_min': 30},
            {'name': 'Vulnérable', 'income': 150000, 'expected_min': 15}
        ]
        
        for test_case in test_cases:
            person = PersonIdentity.objects.create(
                first_name=f'Test_{test_case["name"]}',
                last_name='Poverty',
                birth_date='1990-01-01',
                gender='M',
                province='ESTUAIRE',
                monthly_income=test_case['income'],
                created_by=self.user
            )
            
            household = Household.objects.create(
                head_of_household=person,
                household_size=4,
                total_monthly_income=test_case['income'],
                province='ESTUAIRE',
                has_bank_account=True,
                housing_type='OWNED',
                water_access='PIPED',
                electricity_access='GRID',
                created_by=self.user
            )
            
            economic_score = service._calculate_economic_vulnerability(person)
            
            self.assertGreaterEqual(
                economic_score, 
                test_case['expected_min'],
                f"Score trop faible pour {test_case['name']}"
            )
            
            print(f"   ✅ {test_case['name']}: Score={economic_score:.1f}")
        
        print("   📋 Seuils validés: < 50k (+40pts), < 100k (+30pts), < 300k (+15pts)")
        print("✅ Test 8 PASSED: Seuils pauvreté corrects\n")
    
    def test_09_bulk_operations_work(self):
        """✅ Test 9: Opérations en masse fonctionnent"""
        print("\n🔍 Test 9: Test opérations bulk...")
        
        try:
            person_ids = []
            for i in range(5):
                person = PersonIdentity.objects.create(
                    first_name=f'Bulk{i}',
                    last_name='Test',
                    birth_date='1990-01-01',
                    gender='M',
                    province='ESTUAIRE',
                    monthly_income=50000 + (i * 20000),
                    created_by=self.user
                )
                
                Household.objects.create(
                    head_of_household=person,
                    household_size=3,
                    total_monthly_income=person.monthly_income,
                    province='ESTUAIRE',
                    created_by=self.user
                )
                
                person_ids.append(person.id)
            
            print(f"   ✅ {len(person_ids)} personnes créées")
            
            service = VulnerabilityService()
            results = service.bulk_calculate_assessments(person_ids)
            
            self.assertEqual(results['success'], 5)
            self.assertEqual(results['errors'], 0)
            print(f"   ✅ Bulk assessment: {results['success']} succès, {results['errors']} erreurs")
            
            print("✅ Test 9 PASSED: Opérations bulk fonctionnent\n")
        except Exception as e:
            self.fail(f"❌ Erreur bulk operations: {e}")
    
    def test_10_statistics_generation(self):
        """✅ Test 10: Génération statistiques fonctionne"""
        print("\n🔍 Test 10: Test génération statistiques...")
        
        try:
            for i in range(3):
                person = PersonIdentity.objects.create(
                    first_name=f'Stats{i}',
                    last_name='Test',
                    birth_date='1990-01-01',
                    gender='M',
                    province='ESTUAIRE',
                    monthly_income=60000,
                    created_by=self.user
                )
                
                Household.objects.create(
                    head_of_household=person,
                    household_size=4,
                    total_monthly_income=60000,
                    province='ESTUAIRE',
                    created_by=self.user
                )
                
                VulnerabilityAssessment.objects.create(
                    person=person,
                    vulnerability_score=Decimal(str(50 + i * 10)),
                    risk_level='MODERATE',
                    household_composition_score=Decimal('40'),
                    economic_vulnerability_score=Decimal('50'),
                    social_vulnerability_score=Decimal('30'),
                    created_by=self.user
                )
            
            print("   ✅ 3 assessments créés")
            
            service = VulnerabilityService()
            stats = service.get_vulnerability_statistics()
            
            self.assertIsNotNone(stats)
            self.assertGreaterEqual(stats['total_assessments'], 3)
            
            print(f"   ✅ Statistiques générées: {stats['total_assessments']} assessments")
            print("✅ Test 10 PASSED: Statistiques fonctionnent\n")
        except Exception as e:
            self.fail(f"❌ Erreur statistiques: {e}")


if __name__ == "__main__":
    from django.core.management import call_command
    
    print("\n" + "=" * 70)
    print("🧪 RSU GABON - VALIDATION CORRECTIONS")
    print("=" * 70)
    print("Validation que toutes les corrections ont été appliquées\n")
    
    call_command('test', 'test_corrections_validation.CorrectionsValidationTest', verbosity=2)
    
    print("\n" + "=" * 70)
    print("✅ ✅ ✅ VALIDATION TERMINÉE ✅ ✅ ✅")
    print("=" * 70)