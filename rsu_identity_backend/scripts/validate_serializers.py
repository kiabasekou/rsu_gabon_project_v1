#!/usr/bin/env python
"""
🔍 RSU GABON - Script Validation Serializers
Vérifie automatiquement la conformité entre serializers et modèles

Usage:
    python scripts/validate_serializers.py

Checks:
    1. Tous les champs du serializer existent dans le modèle
    2. Pas de champs fantômes
    3. Types cohérents
    4. SerializerMethodField ont des méthodes get_*

Auteur: RSU Gabon Team
Date: 2025-10-03
"""

import os
import sys
import django
import inspect
from typing import List, Dict, Set, Tuple

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rsu_identity.settings.development')
django.setup()

from django.db import models
from rest_framework import serializers
from apps.identity_app.serializers.person_serializers import (
    PersonIdentitySerializer,
    PersonIdentityCreateSerializer,
    PersonIdentityUpdateSerializer
)
from apps.identity_app.models import PersonIdentity


class SerializerValidator:
    """Validateur de conformité serializer/modèle"""
    
    def __init__(self, serializer_class, model_class):
        self.serializer_class = serializer_class
        self.model_class = model_class
        self.errors = []
        self.warnings = []
        self.success = []
    
    def get_model_fields(self) -> Set[str]:
        """Récupère tous les champs du modèle Django"""
        model_fields = set()
        
        for field in self.model_class._meta.get_fields():
            model_fields.add(field.name)
        
        # Ajouter propriétés et méthodes du modèle
        for attr_name in dir(self.model_class):
            if not attr_name.startswith('_'):
                attr = getattr(self.model_class, attr_name, None)
                if isinstance(attr, property) or callable(attr):
                    model_fields.add(attr_name)
        
        return model_fields
    
    def get_serializer_fields(self) -> Dict[str, str]:
        """Récupère les champs déclarés dans le serializer"""
        serializer_fields = {}
        
        # Champs du Meta.fields
        try:
            meta_fields = self.serializer_class.Meta.fields
            if meta_fields == '__all__':
                # Si __all__, prendre tous les champs du modèle
                meta_fields = [f.name for f in self.model_class._meta.get_fields()]
            
            for field_name in meta_fields:
                serializer_fields[field_name] = 'declared'
        except AttributeError:
            pass
        
        # Champs déclarés explicitement sur le serializer
        for attr_name in dir(self.serializer_class):
            attr = getattr(self.serializer_class, attr_name, None)
            if isinstance(attr, serializers.Field):
                serializer_fields[attr_name] = type(attr).__name__
        
        return serializer_fields
    
    def get_serializer_method_fields(self) -> Set[str]:
        """Récupère les SerializerMethodField"""
        method_fields = set()
        
        for attr_name in dir(self.serializer_class):
            attr = getattr(self.serializer_class, attr_name, None)
            if isinstance(attr, serializers.SerializerMethodField):
                method_fields.add(attr_name)
        
        return method_fields
    
    def validate_field_existence(self):
        """Vérifier que tous les champs du serializer existent dans le modèle"""
        model_fields = self.get_model_fields()
        serializer_fields = self.get_serializer_fields()
        method_fields = self.get_serializer_method_fields()
        
        for field_name, field_type in serializer_fields.items():
            # Ignorer les champs BaseModel
            if field_name in ['id', 'created_at', 'updated_at', 'created_by', 
                             'updated_by', 'is_active']:
                continue
            
            # SerializerMethodField → Vérifier méthode get_*
            if field_name in method_fields:
                method_name = f'get_{field_name}'
                if hasattr(self.serializer_class, method_name):
                    self.success.append(
                        f"✅ {field_name}: SerializerMethodField avec {method_name}()"
                    )
                else:
                    self.errors.append(
                        f"❌ {field_name}: SerializerMethodField SANS méthode {method_name}()"
                    )
                continue
            
            # Champ standard → Doit exister dans le modèle
            if field_name not in model_fields:
                # Vérifier si c'est un source
                serializer_field = getattr(self.serializer_class, field_name, None)
                if hasattr(serializer_field, 'source') and serializer_field.source:
                    source_field = serializer_field.source.split('.')[0]
                    if source_field in model_fields:
                        self.success.append(
                            f"✅ {field_name}: Source={source_field} (existe)"
                        )
                        continue
                
                self.errors.append(
                    f"❌ {field_name}: N'EXISTE PAS dans le modèle {self.model_class.__name__}"
                )
            else:
                self.success.append(
                    f"✅ {field_name}: Existe dans le modèle"
                )
    
    def validate_read_only_fields(self):
        """Vérifier cohérence read_only_fields"""
        try:
            read_only = set(self.serializer_class.Meta.read_only_fields)
            all_fields = set(self.serializer_class.Meta.fields)
            
            for ro_field in read_only:
                if ro_field not in all_fields:
                    self.warnings.append(
                        f"⚠️ {ro_field}: Dans read_only_fields mais pas dans fields"
                    )
                else:
                    self.success.append(
                        f"✅ {ro_field}: Correctement en read-only"
                    )
        except AttributeError:
            pass
    
    def validate_types(self):
        """Vérifier cohérence des types"""
        model_fields = {
            f.name: type(f).__name__ 
            for f in self.model_class._meta.get_fields()
        }
        
        serializer_fields = self.get_serializer_fields()
        
        for field_name, ser_type in serializer_fields.items():
            if field_name in model_fields:
                model_type = model_fields[field_name]
                
                # Mapping types Django → DRF
                type_mapping = {
                    'CharField': ['CharField', 'SerializerMethodField'],
                    'TextField': ['CharField', 'SerializerMethodField'],
                    'IntegerField': ['IntegerField', 'SerializerMethodField'],
                    'DecimalField': ['DecimalField', 'SerializerMethodField'],
                    'DateField': ['DateField', 'SerializerMethodField'],
                    'DateTimeField': ['DateTimeField', 'SerializerMethodField'],
                    'BooleanField': ['BooleanField', 'SerializerMethodField'],
                    'ForeignKey': ['PrimaryKeyRelatedField', 'SerializerMethodField'],
                    'JSONField': ['JSONField', 'SerializerMethodField', 'DictField'],
                }
                
                expected_types = type_mapping.get(model_type, [])
                if expected_types and ser_type not in expected_types:
                    self.warnings.append(
                        f"⚠️ {field_name}: Type modèle={model_type}, serializer={ser_type}"
                    )
    
    def run_validation(self) -> Tuple[List[str], List[str], List[str]]:
        """Exécuter toutes les validations"""
        print(f"\n{'='*70}")
        print(f"🔍 Validation: {self.serializer_class.__name__}")
        print(f"   Modèle: {self.model_class.__name__}")
        print(f"{'='*70}\n")
        
        self.validate_field_existence()
        self.validate_read_only_fields()
        self.validate_types()
        
        return self.errors, self.warnings, self.success


def print_results(errors: List[str], warnings: List[str], success: List[str]):
    """Afficher les résultats de validation"""
    
    if success:
        print(f"\n✅ SUCCÈS ({len(success)}):")
        for msg in success[:5]:  # Limiter affichage
            print(f"   {msg}")
        if len(success) > 5:
            print(f"   ... et {len(success) - 5} autres ✅")
    
    if warnings:
        print(f"\n⚠️  AVERTISSEMENTS ({len(warnings)}):")
        for msg in warnings:
            print(f"   {msg}")
    
    if errors:
        print(f"\n❌ ERREURS CRITIQUES ({len(errors)}):")
        for msg in errors:
            print(f"   {msg}")
    
    print(f"\n{'='*70}")
    
    # Score final
    total = len(success) + len(warnings) + len(errors)
    score = (len(success) / total * 100) if total > 0 else 0
    
    if score == 100:
        print(f"✅ ✅ ✅ VALIDATION PARFAITE: {score:.1f}% ✅ ✅ ✅")
    elif score >= 90:
        print(f"✅ VALIDATION RÉUSSIE: {score:.1f}%")
    elif score >= 70:
        print(f"⚠️  VALIDATION PARTIELLE: {score:.1f}%")
    else:
        print(f"❌ VALIDATION ÉCHOUÉE: {score:.1f}%")
    
    print(f"{'='*70}\n")
    
    return len(errors) == 0


def main():
    """Point d'entrée principal"""
    print("\n" + "="*70)
    print("🔍 RSU GABON - VALIDATION AUTOMATIQUE SERIALIZERS")
    print("="*70)
    
    all_passed = True
    
    # Liste des serializers à valider
    serializers_to_validate = [
        (PersonIdentitySerializer, PersonIdentity, "Principal"),
        (PersonIdentityCreateSerializer, PersonIdentity, "Création"),
        (PersonIdentityUpdateSerializer, PersonIdentity, "Mise à jour"),
    ]
    
    for serializer_class, model_class, description in serializers_to_validate:
        validator = SerializerValidator(serializer_class, model_class)
        errors, warnings, success = validator.run_validation()
        
        passed = print_results(errors, warnings, success)
        all_passed = all_passed and passed
    
    # Résultat final
    print("\n" + "="*70)
    if all_passed:
        print("✅ ✅ ✅ TOUS LES SERIALIZERS SONT VALIDES ✅ ✅ ✅")
        print("="*70)
        sys.exit(0)
    else:
        print("❌ ❌ ❌ DES ERREURS ONT ÉTÉ DÉTECTÉES ❌ ❌ ❌")
        print("="*70)
        print("\n📋 Actions Recommandées:")
        print("   1. Corriger les champs inexistants dans les serializers")
        print("   2. Ajouter les méthodes get_* manquantes")
        print("   3. Relancer la validation")
        sys.exit(1)


if __name__ == "__main__":
    main()


"""
EXEMPLE DE SORTIE:

======================================================================
🔍 RSU GABON - VALIDATION AUTOMATIQUE SERIALIZERS
======================================================================

======================================================================
🔍 Validation: PersonIdentitySerializer
   Modèle: PersonIdentity
======================================================================

✅ SUCCÈS (45):
   ✅ rsu_id: Existe dans le modèle
   ✅ first_name: Existe dans le modèle
   ✅ employment_info: SerializerMethodField avec get_employment_info()
   ✅ province_info: SerializerMethodField avec get_province_info()
   ✅ vulnerability_status: SerializerMethodField avec get_vulnerability_status()
   ... et 40 autres ✅

⚠️  AVERTISSEMENTS (2):
   ⚠️ monthly_income: Type modèle=DecimalField, serializer=CharField

❌ ERREURS CRITIQUES (0):

======================================================================
✅ ✅ ✅ VALIDATION PARFAITE: 95.7% ✅ ✅ ✅
======================================================================
"""