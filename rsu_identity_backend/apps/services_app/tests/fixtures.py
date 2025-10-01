# apps/services_app/tests/fixtures.py
"""
🧪 RSU GABON - Test Fixtures
Helpers standardisés pour créer données de test valides
Standards: Top 1% International
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Optional

from apps.identity_app.models import PersonIdentity, Household


class TestDataFactory:
    """Factory pour créer données de test cohérentes"""
    
    @staticmethod
    def create_person(
        first_name: str = "Test",
        last_name: str = "USER",
        age_years: int = 30,
        gender: str = "M",
        **kwargs
    ) -> PersonIdentity:
        """
        Crée une PersonIdentity valide pour tests
        
        Args:
            age_years: Âge en années (converti en birth_date)
            gender: 'M' ou 'F'
        """
        birth_date = date.today() - timedelta(days=age_years * 365)
        
        defaults = {
            'first_name': first_name,
            'last_name': last_name,
            'birth_date': birth_date,
            'gender': gender,
            'province': 'ESTUAIRE'
        }
        defaults.update(kwargs)
        
        return PersonIdentity.objects.create(**defaults)
    
    @staticmethod
    def create_household(
        head_person: Optional[PersonIdentity] = None,
        total_monthly_income: int = 150000,
        household_size: int = 4,
        **kwargs
    ) -> Household:
        """
        Crée un Household valide pour tests
        
        Args:
            head_person: Chef de ménage (créé auto si None)
            total_monthly_income: Revenus en FCFA
            household_size: Nombre de membres
        """
        if head_person is None:
            head_person = TestDataFactory.create_person(
                first_name="Chef",
                last_name="MENAGE",
                age_years=45
            )
        
        defaults = {
            'head_of_household': head_person,
            'household_size': household_size,
            'total_monthly_income': Decimal(str(total_monthly_income)),
            'province': 'ESTUAIRE',
            'housing_type': 'OWNED',
            'water_access': 'PIPED',
            'electricity_access': 'CONNECTED',
            'has_toilet': True,
            'members_under_15': max(0, household_size // 3),
            'members_15_64': max(1, household_size - (household_size // 3)),
            'members_over_64': 0
        }
        defaults.update(kwargs)
        
        return Household.objects.create(**defaults)
    
    @staticmethod
    def create_vulnerable_household() -> Dict:
        """Crée ménage vulnérable complet pour tests"""
        person = TestDataFactory.create_person(
            first_name="Marie",
            last_name="VULNERABLE",
            age_years=35,
            gender="F",
            has_disability=True,
            education_level="PRIMARY"
        )
        
        household = TestDataFactory.create_household(
            head_person=person,
            total_monthly_income=45000,
            household_size=7,
            housing_type='RENTED',
            water_access='VENDOR',
            electricity_access='NONE',
            has_toilet=False,
            has_disabled_members=True,
            has_children_under_5=True,
            members_under_15=4,
            members_15_64=2,
            members_over_64=1
        )
        
        return {'person': person, 'household': household}
    
    @staticmethod
    def create_middle_class_household() -> Dict:
        """Crée ménage classe moyenne pour tests"""
        person = TestDataFactory.create_person(
            first_name="Jean",
            last_name="CLASSE_MOYENNE",
            age_years=40,
            gender="M",
            education_level="UNIVERSITY"
        )
        
        household = TestDataFactory.create_household(
            head_person=person,
            total_monthly_income=350000,
            household_size=4,
            housing_type='OWNED',
            has_bank_account=True,
            has_disabled_members=False
        )
        
        return {'person': person, 'household': household}


def create_test_person(**kwargs) -> PersonIdentity:
    """Alias simple pour créer personne test"""
    return TestDataFactory.create_person(**kwargs)


def create_test_household(**kwargs) -> Household:
    """Alias simple pour créer ménage test"""
    return TestDataFactory.create_household(**kwargs)