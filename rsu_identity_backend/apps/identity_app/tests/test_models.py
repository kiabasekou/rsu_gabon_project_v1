# =============================================================================
# FICHIER: apps/identity_app/tests/test_models.py
# CORRECTION: Tests avec imports et usage corrects
# =============================================================================

"""
Tests des modèles Identity App
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from apps.identity_app.models import PersonIdentity, Household, HouseholdMember, GeographicData
from apps.core_app.models import RSUUser
from utils.gabonese_data import generate_rsu_id  # Import correct

class PersonIdentityModelTests(TestCase):
    """Tests du modèle PersonIdentity"""
    
    def setUp(self):
        self.user = RSUUser.objects.create_user(
            username='test_user',
            email='test@rsu.ga',
            password='test123',
            user_type='SURVEYOR',
            employee_id='TEST-001'
        )
    
    def test_rsu_id_generation(self):
        """Test génération automatique RSU-ID"""
        person = PersonIdentity.objects.create(
            first_name='Jean',
            last_name='Mbanda',
            birth_date='1990-01-01',
            gender='M',
            created_by=self.user
        )
        
        self.assertTrue(person.rsu_id.startswith('RSU-GA-'))
        self.assertEqual(len(person.rsu_id), 15)  # RSU-GA- + 8 chars
    
    def test_full_name_property(self):
        """Test propriété full_name"""
        person = PersonIdentity.objects.create(
            first_name='Marie',
            last_name='Nguema',
            birth_date='1985-05-15',
            gender='F',
            created_by=self.user
        )
        
        self.assertEqual(person.full_name, 'Marie Nguema')
    
    def test_age_calculation(self):
        """Test calcul de l'âge"""
        # Personne née il y a 30 ans
        birth_date = timezone.now().date().replace(year=timezone.now().year - 30)
        person = PersonIdentity.objects.create(
            first_name='Paul',
            last_name='Obiang',
            birth_date=birth_date,
            gender='M',
            created_by=self.user
        )
        
        self.assertEqual(person.age, 30)
    
    def test_phone_validation(self):
        """Test validation numéro gabonais"""
        # ✅ CORRECTION: Créer et sauvegarder d'abord pour générer rsu_id
        person = PersonIdentity.objects.create(
            first_name='Test',
            last_name='Phone',
            birth_date='1990-01-01',
            gender='M',
            phone_number='+24177123456',  # Numéro gabonais valide
            created_by=self.user
        )
        
        # Vérifier que rsu_id est généré automatiquement
        self.assertTrue(person.rsu_id.startswith('RSU-GA-'))
        
        # ✅ Test validation après création (rsu_id existe)
        try:
            person.full_clean()  # Ne devrait pas lever d'exception
            validation_passed = True
        except ValidationError as e:
            validation_passed = False
            self.fail(f"Validation échouée pour un numéro valide: {e}")
        
        self.assertTrue(validation_passed, "Validation téléphone réussie")
        
        # ✅ Test numéros gabonais valides
        valid_numbers = [
            '+24177123456',  # Airtel
            '+24106789012',  # Gabon Telecom  
            '+24162345678',  # Moov
            '+24104567890',  # Format alternatif
        ]
        
        for i, number in enumerate(valid_numbers):
            person_valid = PersonIdentity.objects.create(
                first_name=f'Test{i}',
                last_name='ValidPhone',
                birth_date='1985-01-01',
                gender='F',
                phone_number=number,
                created_by=self.user
            )
            
            # Validation automatique à la création - ne devrait pas lever d'exception
            self.assertIsNotNone(person_valid.rsu_id)
            self.assertTrue(person_valid.rsu_id.startswith('RSU-GA-'))
    
    def test_phone_validation_invalid_numbers(self):
        """Test validation numéros invalides"""
        invalid_numbers = [
            '+33123456789',   # France (non-gabonais)
            '+237123456789',  # Cameroun (non-gabonais)
            '77123456',       # Format local sans +241
            '+24112345',      # Trop court
            '+241771234567890', # Trop long
            'invalid-phone',  # Format invalide
        ]
        
        for i, invalid_number in enumerate(invalid_numbers):
            with self.assertRaises(ValidationError, 
                                msg=f"Numéro invalide accepté: {invalid_number}"):
                person = PersonIdentity(
                    first_name=f'Invalid{i}',
                    last_name='Phone',
                    birth_date='1990-01-01',
                    gender='M',
                    phone_number=invalid_number,
                    created_by=self.user
                )
                person.full_clean()  # Devrait lever ValidationError

    
    def test_vulnerability_indicators(self):
        """Test indicateurs de vulnérabilité"""
        person = PersonIdentity.objects.create(
            first_name='Vulnerable',
            last_name='Person',
            birth_date='1950-01-01',  # Personne âgée
            gender='F',
            has_disability=True,
            monthly_income=Decimal('50000'),  # Sous le seuil
            is_household_head=True,
            created_by=self.user
        )
        
        indicators = person.get_vulnerability_indicators()
        expected_indicators = ['DISABILITY', 'ELDERLY', 'FEMALE_HEAD', 'EXTREME_POVERTY']
        
        for indicator in expected_indicators:
            self.assertIn(indicator, indicators)
    
    def test_data_completeness_score(self):
        """Test calcul score complétude"""
        person = PersonIdentity.objects.create(
            first_name='Complete',
            last_name='Data',
            birth_date='1985-01-01',
            gender='M',
            phone_number='+24177123456',
            province='ESTUAIRE',
            address='123 Rue Test',
            occupation='Ingénieur',
            education_level='UNIVERSITY',
            marital_status='MARRIED',
            birth_place='Libreville',
            latitude=Decimal('0.3901'),
            longitude=Decimal('9.4544'),
            created_by=self.user
        )
        
        score = person.calculate_completeness_score()
        self.assertGreater(score, 80.0)  # Score élevé attendu
        self.assertLessEqual(score, 100.0)


class GeographicDataModelTests(TestCase):
    """Tests du modèle GeographicData"""
    
    def test_accessibility_score_calculation(self):
        """Test calcul score d'accessibilité"""
        geo_data = GeographicData.objects.create(
            province='ESTUAIRE',
            department='LIBREVILLE',
            commune='LIBREVILLE',
            district='Centre-Ville',
            latitude=Decimal('0.3901'),
            longitude=Decimal('9.4544'),
            distance_to_hospital=Decimal('2.5'),
            distance_to_school=Decimal('1.0'),
            has_electricity=True,
            has_water=True,
            has_road_access=True
        )
        
        score = geo_data.calculate_accessibility_score()
        self.assertGreater(score, 70.0)  # Bon score attendu
        self.assertLessEqual(score, 100.0)


class HouseholdModelTests(TestCase):
    """Tests des modèles Household et HouseholdMember"""
    
    def setUp(self):
        self.user = RSUUser.objects.create_user(
            username='test_user',
            email='test@rsu.ga',
            password='test123',
            user_type='SURVEYOR',
            employee_id='TEST-001'
        )
        
        # ✅ CORRECTION: Créer PersonIdentity avec chef de ménage
        self.head = PersonIdentity.objects.create(
            first_name='Chef',
            last_name='Menage',
            birth_date='1980-01-01',
            gender='M',
            is_household_head=True,
            created_by=self.user
        )
    
    def test_household_id_generation(self):
        """Test génération ID ménage"""
        # ✅ CORRECTION: Utiliser head_of_household (obligatoire) au lieu de head_person
        household = Household.objects.create(
            head_of_household=self.head,  # ← Champ obligatoire correct
            household_size=4,
            province='ESTUAIRE',
            created_by=self.user
        )
        
        self.assertTrue(household.household_id.startswith('HH-GA-'))
        self.assertEqual(len(household.household_id), 14)  # HH-GA- + 8 chars
    
    def test_dependency_ratio_calculation(self):
        """Test calcul ratio de dépendance"""
        # ✅ CORRECTION: Utiliser head_of_household + définir membres par âge
        household = Household.objects.create(
            head_of_household=self.head,  # ← Champ obligatoire correct
            household_size=5,
            members_under_15=2,    # 2 enfants
            members_over_64=1,     # 1 âgé
            members_15_64=2,       # 2 actifs
            province='ESTUAIRE',
            created_by=self.user
        )
        
        ratio = household.calculate_dependency_ratio()
        expected_ratio = (2 + 1) / 2 * 100  # (2 enfants + 1 âgé) / 2 actifs * 100 = 150%
        self.assertEqual(ratio, expected_ratio)
        self.assertEqual(ratio, 150.0)  # Vérification exacte
    
    def test_household_relationships(self):
        """Test relations ménage-membres"""
        household = Household.objects.create(
            head_of_household=self.head,
            household_size=3,
            province='ESTUAIRE',
            created_by=self.user
        )
        
        # Vérifier que le chef est bien lié
        self.assertEqual(household.head_of_household, self.head)
        self.assertEqual(household.head_of_household.full_name, 'Chef Menage')
        
        # Vérifier génération ID ménage
        self.assertIsNotNone(household.household_id)
        self.assertTrue(len(household.household_id) > 10)

