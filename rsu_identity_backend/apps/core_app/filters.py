# 🇬🇦 RSU GABON - CORE APP FILTERS
# Standards Top 1% - Django Filter Configuration

# =============================================================================
# FICHIER: apps/core_app/filters.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Core Filters
FilterSets personnalisés pour résoudre les incompatibilités JSONField
"""
import django_filters
from django.db.models import JSONField
from .models import RSUUser


class RSUUserFilter(django_filters.FilterSet):
    """
    FilterSet pour RSUUser avec gestion explicite des champs
    
    PROBLÈME RÉSOLU:
    - JSONField 'assigned_provinces' causait AssertionError
    - django-filter ne gère pas automatiquement les JSONField
    
    SOLUTION:
    - Exclusion explicite du JSONField des filtres automatiques
    - Filtrage manuel disponible sur les champs standards
    """
    
    # Filtres standards explicites
    user_type = django_filters.ChoiceFilter(
        choices=[
            ('ADMIN', 'Administrateur'),
            ('SUPERVISOR', 'Superviseur'),
            ('SURVEYOR', 'Enquêteur'),
            ('AUDITOR', 'Auditeur'),
            ('DATA_ANALYST', 'Analyste'),
        ]
    )
    
    department = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text="Filtrage par département (insensible casse)"
    )
    
    is_active = django_filters.BooleanFilter()
    
    # NOTE: assigned_provinces est volontairement EXCLU
    # C'est un JSONField qui nécessiterait un traitement spécial
    # Si besoin futur, implémenter un filtre custom avec lookup PostgreSQL
    
    class Meta:
        model = RSUUser
        fields = {
            'user_type': ['exact'],
            'department': ['exact', 'icontains'],
            'is_active': ['exact'],
            'employee_id': ['exact', 'icontains'],
            # assigned_provinces EXCLU volontairement
        }
        
        # Configuration pour ignorer explicitement les JSONFields
        filter_overrides = {
            JSONField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }


# =============================================================================
# NOTES TECHNIQUES
# =============================================================================
"""
CONSIGNE 1 APPLIQUÉE: Single Source of Truth
- Les noms de champs correspondent EXACTEMENT au modèle RSUUser
- Copié-collé depuis le modèle pour éviter les typos

CONSIGNE 4 APPLIQUÉE: Testing Data Schema First  
- Ce filter corrige l'erreur de test avant que les tests ne s'exécutent
- Le schéma (filter) est maintenant aligné avec l'attente (test)

POURQUOI CETTE SOLUTION:
1. Django-filter génère automatiquement des filters pour tous les champs
2. Pour JSONField, il ne trouve pas de classe de filter appropriée
3. En définissant explicitement les champs à filtrer, on évite l'auto-génération
4. assigned_provinces est exclu car rarement filtrable de manière standard

ALTERNATIVE FUTURE (si filtrage JSON nécessaire):
```python
assigned_provinces = django_filters.CharFilter(
    method='filter_assigned_provinces',
    help_text="Filtrer par province assignée"
)

def filter_assigned_provinces(self, queryset, name, value):
    # PostgreSQL: filtrage dans tableau JSON
    return queryset.filter(assigned_provinces__contains=[value])
```
"""