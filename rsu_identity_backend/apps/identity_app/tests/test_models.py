
# =============================================================================
# FICHIER: apps/identity_app/tests/test_models.py
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
from utils.gabonese_data import generate_rsu_id

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
        person = PersonIdentity(
            first_name='Test',
            last_name='User',
            birth_date='1990-01-01',
            gender='M',
            phone_number='+24177123456',  # Format gabonais valide
            created_by=self.user
        )
        
        # Ne doit pas lever d'exception
        person.full_clean()
        person.save()
        
        # Test format invalide
        person.phone_number = '+33123456789'  # Format français
        with self.assertRaises(ValidationError):
            person.full_clean()
    
    def test_vulnerability_indicators(self):
        """Test indicateurs de vulnérabilité"""
        # Personne vulnérable : âgée, handicapée, femme chef de ménage
        person = PersonIdentity.objects.create(
            first_name='Fatou',
            last_name='Ba',
            birth_date='1950-01-01',  # Âgée
            gender='F',
            has_disability=True,
            is_household_head=True,
            monthly_income=50000,  # Sous seuil pauvreté
            created_by=self.user
        )
        
        self.assertTrue(person.is_vulnerable_age())
        self.assertTrue(person.has_disability)
        self.assertTrue(person.is_household_head)
        self.assertLess(person.monthly_income, 75000)  # Seuil pauvreté extrême
    
    def test_data_completeness_score(self):
        """Test calcul score complétude"""
        person = PersonIdentity.objects.create(
            first_name='Complete',
            last_name='Data',
            birth_date='1990-01-01',
            gender='M',
            phone_number='+24177123456',
            email='complete@test.ga',
            province='ESTUAIRE',
            address='123 Rue Test',
            occupation='Ingénieur',
            education_level='UNIVERSITY',
            monthly_income=500000,
            latitude=Decimal('0.4162'),
            longitude=Decimal('9.4673'),
            created_by=self.user
        )
        
        score = person.calculate_completeness_score()
        self.assertGreater(score, 80)  # Score élevé avec données complètes

class HouseholdModelTests(TestCase):
    """Tests du modèle Household"""
    
    def setUp(self):
        self.user = RSUUser.objects.create_user(
            username='test_user',
            email='test@rsu.ga',
            password='test123',
            user_type='SURVEYOR',
            employee_id='TEST-001'
        )
        
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
        household = Household.objects.create(
            head_of_household=self.head,
            household_size=5,
            created_by=self.user
        )
        
        self.assertTrue(household.household_id.startswith('HH-GA-'))
    
    def test_dependency_ratio_calculation(self):
        """Test calcul ratio de dépendance"""
        household = Household.objects.create(
            head_of_household=self.head,
            household_size=6,
            created_by=self.user
        )
        
        # Créer membres avec différents âges
        child = PersonIdentity.objects.create(
            first_name='Enfant',
            last_name='Un',
            birth_date=timezone.now().date().replace(year=timezone.now().year - 8),
            gender='M',
            created_by=self.user
        )
        
        elderly = PersonIdentity.objects.create(
            first_name='Grand',
            last_name='Pere',
            birth_date=timezone.now().date().replace(year=timezone.now().year - 70),
            gender='M',
            created_by=self.user
        )
        
        adult = PersonIdentity.objects.create(
            first_name='Adulte',
            last_name='Actif',
            birth_date=timezone.now().date().replace(year=timezone.now().year - 35),
            gender='F',
            created_by=self.user
        )
        
        # Ajouter membres au ménage
        HouseholdMember.objects.create(
            household=household,
            person=self.head,
            relationship_to_head='HEAD',
            created_by=self.user
        )
        
        HouseholdMember.objects.create(
            household=household,
            person=child,
            relationship_to_head='CHILD',
            created_by=self.user
        )
        
        HouseholdMember.objects.create(
            household=household,
            person=elderly,
            relationship_to_head='PARENT',
            created_by=self.user
        )
        
        HouseholdMember.objects.create(
            household=household,
            person=adult,
            relationship_to_head='SPOUSE',
            created_by=self.user
        )
        
        # Calculer ratio : 2 dépendants (enfant + âgé) / 2 actifs = 100%
        ratio = household.calculate_dependency_ratio()
        self.assertEqual(ratio, 100.0)

class GeographicDataModelTests(TestCase):
    """Tests du modèle GeographicData"""
    
    def test_accessibility_score_calculation(self):
        """Test calcul score d'accessibilité"""
        # Zone très accessible
        accessible_zone = GeographicData.objects.create(
            location_name='Libreville Centre',
            province='ESTUAIRE',
            center_latitude=Decimal('0.4162'),
            center_longitude=Decimal('9.4673'),
            zone_type='URBAN_CENTER',
            road_condition='PAVED',
            distance_to_health_center_km=2.0,
            distance_to_school_km=1.0,
            distance_to_market_km=0.5,
            public_transport_available=True,
            mobile_network_coverage=True
        )
        
        score = accessible_zone.calculate_accessibility_score()
        self.assertGreater(score, 80)
        
        # Zone très isolée
        remote_zone = GeographicData.objects.create(
            location_name='Village Isolé',
            province='OGOOUE_IVINDO',
            center_latitude=Decimal('0.5'),
            center_longitude=Decimal('12.0'),
            zone_type='RURAL_REMOTE',
            road_condition='IMPASSABLE',
            distance_to_health_center_km=80.0,
            distance_to_school_km=30.0,
            distance_to_market_km=50.0,
            public_transport_available=False,
            mobile_network_coverage=False,
            difficult_access_rainy_season=True
        )
        
        score = remote_zone.calculate_accessibility_score()
        self.assertLess(score, 30)

