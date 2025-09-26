import uuid
import random
from django.conf import settings

"""
🇬🇦 RSU Gabon - Données de Référence Gabonaises
Standards Top 1% - Contextualisation Locale
"""

# Provinces du Gabon
PROVINCES = {
    'ESTUAIRE': {
        'name': 'Estuaire',
        'capital': 'Libreville',
        'type': 'URBAN_CENTER',
        'population_density': 'HIGH'
    },
    'HAUT_OGOOUE': {
        'name': 'Haut-Ogooué', 
        'capital': 'Franceville',
        'type': 'MINING',
        'population_density': 'MEDIUM'
    },
    'MOYEN_OGOOUE': {
        'name': 'Moyen-Ogooué',
        'capital': 'Lambaréné', 
        'type': 'FOREST',
        'population_density': 'LOW'
    },
    'NGOUNIE': {
        'name': 'Ngounié',
        'capital': 'Mouila',
        'type': 'FOREST',
        'population_density': 'LOW'
    },
    'NYANGA': {
        'name': 'Nyanga',
        'capital': 'Tchibanga',
        'type': 'RURAL_REMOTE',
        'population_density': 'VERY_LOW'
    },
    'OGOOUE_IVINDO': {
        'name': 'Ogooué-Ivindo',
        'capital': 'Makokou',
        'type': 'FOREST',
        'population_density': 'VERY_LOW'
    },
    'OGOOUE_LOLO': {
        'name': 'Ogooué-Lolo',
        'capital': 'Koulamoutou',
        'type': 'FOREST',
        'population_density': 'VERY_LOW'
    },
    'OGOOUE_MARITIME': {
        'name': 'Ogooué-Maritime',
        'capital': 'Port-Gentil',
        'type': 'COASTAL',
        'population_density': 'MEDIUM'
    },
    'WOLEU_NTEM': {
        'name': 'Woleu-Ntem',
        'capital': 'Oyem',
        'type': 'BORDER',
        'population_density': 'MEDIUM'
    }
}

# Types de zones géographiques
GEOGRAPHIC_ZONES = [
    ('URBAN_CENTER', 'Centre Urbain'),
    ('URBAN_PERIPHERY', 'Périphérie Urbaine'),
    ('RURAL_ACCESSIBLE', 'Rural Accessible'),
    ('RURAL_REMOTE', 'Rural Isolé'),
    ('COASTAL', 'Zone Côtière'),
    ('FOREST', 'Zone Forestière'),
    ('MINING', 'Zone Minière'),
    ('BORDER', 'Zone Frontalière'),
]

# Langues locales gabonaises
LOCAL_LANGUAGES = [
    'FANG',
    'MYENE',
    'NZEBI',
    'BAPOUNOU',
    'BANDJABI',
    'TEKE',
    'KOTA',
    'SHAKE',
    'BENGA',
    'SIRA',
]

# Validation numéro de téléphone gabonais
import re
GABON_PHONE_REGEX = re.compile(r'^\+241[0-9]{8}$')

def validate_gabon_phone(phone_number: str) -> bool:
    """Valide un numéro de téléphone gabonais"""
    return bool(GABON_PHONE_REGEX.match(phone_number))

# ✅ CORRECTION CRITIQUE: Signature fonction sans paramètre 'self'
def generate_rsu_id():
    """
    Génère un RSU-ID unique au format: RSU-GA-XXXXXXXX
    RSU = Registre Social Unifié
    GA = Gabon
    XXXXXXXX = 8 caractères alphanumériques
    
    Returns:
        str: RSU-ID unique (ex: RSU-GA-A1B2C3D4)
    """
    prefix = getattr(settings, 'RSU_ID_PREFIX', 'RSU-GA-')
    
    # Générer 8 caractères alphanumériques
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    unique_part = ''.join(random.choices(chars, k=8))
    
    rsu_id = f"{prefix}{unique_part}"
    
    # ✅ AMÉLIORATION: Vérification unicité avec import conditionnel
    try:
        from apps.identity_app.models import PersonIdentity
        while PersonIdentity.objects.filter(rsu_id=rsu_id).exists():
            unique_part = ''.join(random.choices(chars, k=8))
            rsu_id = f"{prefix}{unique_part}"
    except ImportError:
        # Pendant les migrations ou tests, PersonIdentity peut ne pas être disponible
        pass
    
    return rsu_id

def get_province_info(province_code: str) -> dict:
    """Retourne les informations d'une province"""
    return PROVINCES.get(province_code, {})

# Seuils économiques contextualisés
ECONOMIC_THRESHOLDS = {
    'EXTREME_POVERTY': 75000,  # FCFA/mois
    'POVERTY': 150000,
    'LOWER_MIDDLE_CLASS': 300000,
    'MIDDLE_CLASS': 500000,
    'UPPER_MIDDLE_CLASS': 1000000,
}

# Programmes sociaux types
SOCIAL_PROGRAM_TYPES = [
    ('MATERNAL_HEALTH', 'Santé Maternelle'),
    ('CHILD_NUTRITION', 'Nutrition Infantile'),
    ('RURAL_DEVELOPMENT', 'Développement Rural'),
    ('EDUCATION_SUPPORT', 'Appui Éducation'),
    ('ELDERLY_CARE', 'Soins Personnes Âgées'),
    ('DISABILITY_SUPPORT', 'Appui Handicap'),
    ('EMERGENCY_RELIEF', 'Aide d\'Urgence'),
    ('LIVELIHOOD_SUPPORT', 'Appui Moyens Subsistance'),
]

# ✅ AJOUT: Validation coordonnées GPS Gabon
def validate_gabon_coordinates(latitude: float, longitude: float) -> bool:
    """
    Valide que les coordonnées GPS sont dans les limites du Gabon
    
    Limites approximatives du Gabon:
    - Latitude: -4.0° à 2.3° (Sud-Nord)
    - Longitude: 8.5° à 14.5° (Ouest-Est)
    
    Args:
        latitude: Latitude en degrés décimaux
        longitude: Longitude en degrés décimaux
        
    Returns:
        bool: True si les coordonnées sont au Gabon
    """
    # Bornes géographiques du Gabon
    GABON_BOUNDS = {
        'min_lat': -4.0,
        'max_lat': 2.3,
        'min_lng': 8.5,
        'max_lng': 14.5
    }
    
    return (
        GABON_BOUNDS['min_lat'] <= latitude <= GABON_BOUNDS['max_lat'] and
        GABON_BOUNDS['min_lng'] <= longitude <= GABON_BOUNDS['max_lng']
    )