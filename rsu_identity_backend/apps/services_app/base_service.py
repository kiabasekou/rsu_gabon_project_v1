# ===================================================================
# RSU GABON - BASE SERVICE (COPIE LOCALE SERVICES_APP)
# Emplacement: apps/services_app/services/base_service.py
# ===================================================================

"""
🇬🇦 RSU Gabon - Service de Base
Base pour tous les services métier RSU
"""

import logging
from typing import Any, Dict, List, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

logger = logging.getLogger(__name__)

class ServiceHelper:
    """
    Classe utilitaire pour fonctions communes aux services
    """
    
    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """Division sécurisée avec valeur par défaut"""
        try:
            if denominator == 0:
                return default
            return numerator / denominator
        except (TypeError, ValueError):
            return default
    
    @staticmethod
    def calculate_percentage(part: float, total: float) -> float:
        """Calcul pourcentage sécurisé"""
        if total == 0:
            return 0.0
        return (part / total) * 100
    
    @staticmethod
    def normalize_score(score: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
        """Normalisation score dans plage donnée"""
        if score < min_val:
            return min_val
        if score > max_val:
            return max_val
        return score
    
    @staticmethod
    def weighted_average(values_weights: List[tuple]) -> float:
        """
        Calcul moyenne pondérée
        Args:
            values_weights: Liste de tuples (valeur, poids)
        """
        if not values_weights:
            return 0.0
        
        total_weighted = sum(value * weight for value, weight in values_weights)
        total_weights = sum(weight for _, weight in values_weights)
        
        if total_weights == 0:
            return 0.0
        
        return total_weighted / total_weights

class BaseService:
    """
    Service de base pour tous les services métier RSU
    """
    
    def __init__(self):
        """Initialisation service de base"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.helper = ServiceHelper()
    
    def log_operation(self, operation: str, details: Optional[Dict] = None):
        """Log standardisé des opérations"""
        log_data = {
            'service': self.__class__.__name__,
            'operation': operation,
            'timestamp': timezone.now().isoformat(),
        }
        
        if details:
            log_data.update(details)
        
        self.logger.info(f"Operation: {operation}", extra=log_data)
    
    def handle_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """Gestion standardisée des erreurs"""
        error_data = {
            'service': self.__class__.__name__,
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': timezone.now().isoformat(),
        }
        
        self.logger.error(f"Error in {operation}: {error}", extra=error_data)
        
        return {
            'success': False,
            'error': str(error),
            'error_type': type(error).__name__,
            'timestamp': timezone.now().isoformat()
        }
    
    def validate_required_fields(self, data: Dict, required_fields: List[str]) -> List[str]:
        """
        Validation des champs obligatoires
        
        Args:
            data: Dictionnaire de données
            required_fields: Liste des champs obligatoires
            
        Returns:
            Liste des champs manquants
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                missing_fields.append(field)
        
        return missing_fields
    
    @transaction.atomic
    def safe_bulk_operation(self, operation_func, items: List[Any]) -> Dict[str, Any]:
        """
        Exécution sécurisée d'opération en lot
        
        Args:
            operation_func: Fonction à exécuter pour chaque item
            items: Liste des éléments à traiter
            
        Returns:
            Résultats de l'opération
        """
        results = {
            'success': 0,
            'errors': 0,
            'items_processed': [],
            'error_details': []
        }
        
        try:
            for item in items:
                try:
                    result = operation_func(item)
                    results['items_processed'].append(result)
                    results['success'] += 1
                    
                except Exception as e:
                    results['errors'] += 1
                    results['error_details'].append({
                        'item': str(item),
                        'error': str(e)
                    })
            
            self.log_operation('bulk_operation', {
                'total_items': len(items),
                'success_count': results['success'],
                'error_count': results['errors']
            })
            
        except Exception as e:
            return self.handle_error(e, 'safe_bulk_operation')
        
        return results
    
    def calculate_weighted_score(self, scores: Dict[str, float], weights: Dict[str, float]) -> float:
        """
        Calcul score pondéré standardisé
        
        Args:
            scores: Dictionnaire {dimension: score}
            weights: Dictionnaire {dimension: poids}
            
        Returns:
            Score pondéré final
        """
        if not scores or not weights:
            return 0.0
        
        weighted_values = []
        
        for dimension, score in scores.items():
            weight = weights.get(dimension, 0.0)
            if weight > 0:
                weighted_values.append((score, weight))
        
        if not weighted_values:
            return 0.0
        
        return self.helper.weighted_average(weighted_values)
    
    def format_currency(self, amount: float, currency: str = 'XAF') -> str:
        """Formatage standardisé des montants"""
        try:
            if currency == 'XAF':
                return f"{amount:,.0f} F CFA"
            else:
                return f"{amount:,.2f} {currency}"
        except (TypeError, ValueError):
            return f"0 {currency}"
    
    def calculate_roi(self, benefits: float, costs: float) -> float:
        """Calcul ROI standardisé"""
        if costs == 0:
            return 0.0
        return ((benefits - costs) / costs) * 100
    
    def get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut du service"""
        return {
            'cache_timeout': 3600,  # 1 heure
            'batch_size': 100,
            'max_retries': 3,
            'log_level': 'INFO'
        }