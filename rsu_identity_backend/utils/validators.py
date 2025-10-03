# =============================================================================
# FICHIER: utils/validators.py (CRÉER CE FICHIER)
# OBJECTIF: Validateurs cohérence données employment
# =============================================================================

from django.core.exceptions import ValidationError
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class EmploymentDataValidator:
    """
    Validateur de cohérence des données d'emploi
    Prévient les incohérences métier
    """
    
    # Mapping secteurs → fourchettes salaire attendues (FCFA)
    SECTOR_SALARY_RANGES = {
        'SECTEUR_PUBLIC': {
            'min': 150000,
            'max': 5000000,
            'typical': (200000, 800000)
        },
        'SECTEUR_PRIVE_FORMEL': {
            'min': 100000,
            'max': 10000000,
            'typical': (150000, 1500000)
        },
        'SECTEUR_INFORMEL': {
            'min': 0,
            'max': 500000,
            'typical': (30000, 150000)
        },
        'INDEPENDANT': {
            'min': 0,
            'max': 5000000,
            'typical': (50000, 500000)
        }
    }
    
    # Employeurs secteur public connus
    PUBLIC_SECTOR_EMPLOYERS = [
        'ministère', 'minister', 'gouvernement', 'government',
        'mairie', 'préfecture', 'assemblée nationale', 
        'caisse nationale', 'cnss', 'hospital', 'hôpital',
        'université', 'lycée', 'école publique'
    ]
    
    # Grandes entreprises formelles Gabon
    MAJOR_FORMAL_EMPLOYERS = [
        'total', 'gabon oil', 'perenco', 'assala',
        'setrag', 'sucaf', 'olam', 'comilog',
        'bgfi', 'bicig', 'uba', 'ecobank',
        'gabon telecom', 'airtel', 'moov'
    ]
    
    @classmethod
    def validate_employment_coherence(cls, employment_status, employer, occupation, monthly_income):
        """
        Validation principale de cohérence
        
        Returns:
            dict: {
                'valid': bool,
                'warnings': list,
                'errors': list,
                'suggestions': list
            }
        """
        warnings = []
        errors = []
        suggestions = []
        
        # RÈGLE 1: Chômeur sans employeur
        if employment_status == 'UNEMPLOYED':
            if employer:
                errors.append(
                    "Incohérence: Un chômeur ne peut avoir d'employeur"
                )
            if monthly_income and monthly_income > 50000:
                warnings.append(
                    f"Chômeur avec revenu {monthly_income:,.0f} FCFA suspect"
                )
        
        # RÈGLE 2: Employé sans employeur
        if employment_status in ['EMPLOYED_FORMAL', 'EMPLOYED_INFORMAL']:
            if not employer:
                warnings.append("Employeur manquant pour personne employée")
            
            if employer and monthly_income:
                sector = cls._detect_sector(employer)
                salary_range = cls.SECTOR_SALARY_RANGES.get(sector)
                
                if salary_range:
                    if monthly_income < salary_range['min']:
                        warnings.append(
                            f"Salaire bas pour {sector}: {monthly_income:,.0f} FCFA"
                        )
        
        # RÈGLE 3: Occupation sans statut
        if occupation and not employment_status:
            warnings.append("Profession renseignée mais statut emploi manquant")
        
        return {
            'valid': len(errors) == 0,
            'warnings': warnings,
            'errors': errors,
            'suggestions': suggestions
        }
    
    @classmethod
    def _detect_sector(cls, employer):
        """Détecte le secteur d'activité"""
        if not employer:
            return None
        
        employer_lower = employer.lower()
        
        for keyword in cls.PUBLIC_SECTOR_EMPLOYERS:
            if keyword in employer_lower:
                return 'SECTEUR_PUBLIC'
        
        for keyword in cls.MAJOR_FORMAL_EMPLOYERS:
            if keyword in employer_lower:
                return 'SECTEUR_PRIVE_FORMEL'
        
        return 'SECTEUR_PRIVE_FORMEL'


# =============================================================================
# UTILISATION
# =============================================================================
"""
# Dans PersonIdentityCreateSerializer:

from utils.validators import EmploymentDataValidator

def validate(self, attrs):
    attrs = super().validate(attrs)
    
    result = EmploymentDataValidator.validate_employment_coherence(
        employment_status=attrs.get('employment_status'),
        employer=attrs.get('employer'),
        occupation=attrs.get('occupation'),
        monthly_income=attrs.get('monthly_income')
    )
    
    if not result['valid']:
        raise serializers.ValidationError({
            'non_field_errors': result['errors']
        })
    
    if result['warnings']:
        logger.warning(f"Employment warnings: {result['warnings']}")
    
    return attrs
"""