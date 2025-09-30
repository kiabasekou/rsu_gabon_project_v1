# ===================================================================
# RSU GABON - BASE SERVICE (Corrigé pour apps/services_app)
# Standards Top 1% - Architecture Service Layer
# ===================================================================

"""
Service de base pour toutes les opérations métier RSU Gabon

Emplacement: apps/services_app/services/base_service.py

Ce fichier fournit la classe BaseService dont héritent tous les services
métier (VulnerabilityService, EligibilityService, GeotargetingService).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """
    Classe de base pour tous les services métier RSU
    
    Fournit des fonctionnalités communes:
    - Gestion transactions atomiques
    - Logging opérations pour audit trail
    - Gestion erreurs standardisée
    
    Usage:
        class MonService(BaseService):
            def ma_methode(self):
                self.log_operation('operation_name', {'data': 'value'})
                return self.execute_with_transaction(self._internal_method)
    """
    
    def __init__(self):
        """Initialise le service avec logger"""
        self.logger = logger
        
    @transaction.atomic
    def execute_with_transaction(self, operation, *args, **kwargs):
        """
        Exécute une opération dans une transaction atomique Django
        
        Args:
            operation: Fonction à exécuter
            *args: Arguments positionnels pour la fonction
            **kwargs: Arguments nommés pour la fonction
            
        Returns:
            Résultat de l'opération
            
        Raises:
            Exception: Toute exception levée par l'opération
            
        Note:
            En cas d'erreur, la transaction est automatiquement annulée
            (rollback) pour garantir l'intégrité des données.
        """
        try:
            result = operation(*args, **kwargs)
            self.logger.debug(
                f"{self.__class__.__name__}.execute_with_transaction: SUCCESS"
            )
            return result
        except Exception as e:
            self.logger.error(
                f"Erreur transaction dans {self.__class__.__name__}: {str(e)}",
                exc_info=True
            )
            raise
            
    def log_operation(self, operation: str, data: Dict[str, Any]):
        """
        Log une opération métier pour audit trail
        
        Args:
            operation: Nom de l'opération (ex: 'vulnerability_calculated')
            data: Données contextuelles de l'opération
            
        Example:
            self.log_operation('assessment_created', {
                'person_id': 123,
                'vulnerability_score': 75.5,
                'level': 'HIGH'
            })
        """
        self.logger.info(
            f"[{self.__class__.__name__}] {operation}: {data}"
        )
    
    def log_error(self, operation: str, error: Exception, context: Dict[str, Any] = None):
        """
        Log une erreur avec contexte pour debugging
        
        Args:
            operation: Nom de l'opération qui a échoué
            error: Exception levée
            context: Contexte additionnel (optionnel)
        """
        error_data = {
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        self.logger.error(
            f"[{self.__class__.__name__}] ERROR in {operation}: {error_data}",
            exc_info=True
        )
    
    def validate_required_fields(self, data: Dict, required_fields: List[str]):
        """
        Valide la présence de champs requis dans un dictionnaire
        
        Args:
            data: Dictionnaire à valider
            required_fields: Liste des champs requis
            
        Raises:
            ValueError: Si un champ requis est manquant
            
        Example:
            self.validate_required_fields(
                person_data,
                ['first_name', 'last_name', 'age']
            )
        """
        missing_fields = [
            field for field in required_fields 
            if field not in data or data[field] is None
        ]
        
        if missing_fields:
            error_msg = f"Champs requis manquants: {', '.join(missing_fields)}"
            self.logger.error(f"{self.__class__.__name__}: {error_msg}")
            raise ValueError(error_msg)
    
    def safe_execute(self, operation_name: str, operation, *args, **kwargs) -> Optional[Any]:
        """
        Exécute une opération avec gestion d'erreur standardisée
        
        Args:
            operation_name: Nom de l'opération (pour logging)
            operation: Fonction à exécuter
            *args: Arguments positionnels
            **kwargs: Arguments nommés
            
        Returns:
            Résultat de l'opération ou None si erreur
            
        Example:
            result = self.safe_execute(
                'calculate_score',
                self._internal_calculation,
                person_id=123
            )
        """
        try:
            result = operation(*args, **kwargs)
            self.log_operation(f"{operation_name}_success", {
                'args': str(args)[:100],  # Limiter taille log
                'kwargs': str(kwargs)[:100]
            })
            return result
        except Exception as e:
            self.log_error(operation_name, e, {
                'args': str(args)[:100],
                'kwargs': str(kwargs)[:100]
            })
            return None


# ===================================================================
# CLASSE UTILITAIRE - Service Helper
# ===================================================================

class ServiceHelper:
    """
    Fonctions utilitaires pour les services métier
    """
    
    @staticmethod
    def format_fcfa(amount: float) -> str:
        """
        Formate un montant en FCFA avec séparateurs
        
        Args:
            amount: Montant en FCFA
            
        Returns:
            str: Montant formaté (ex: "50 000 FCFA")
        """
        return f"{amount:,.0f} FCFA".replace(',', ' ')
    
    @staticmethod
    def calculate_percentage(part: float, total: float, precision: int = 2) -> float:
        """
        Calcule un pourcentage avec gestion division par zéro
        
        Args:
            part: Partie
            total: Total
            precision: Nombre de décimales
            
        Returns:
            float: Pourcentage ou 0.0 si total = 0
        """
        if total == 0:
            return 0.0
        return round((part / total) * 100, precision)
    
    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """
        Division sécurisée avec valeur par défaut
        
        Args:
            numerator: Numérateur
            denominator: Dénominateur
            default: Valeur retournée si denominator = 0
            
        Returns:
            float: Résultat ou valeur par défaut
        """
        if denominator == 0:
            return default
        return numerator / denominator
    
    @staticmethod
    def clamp(value: float, min_value: float, max_value: float) -> float:
        """
        Limite une valeur dans un intervalle
        
        Args:
            value: Valeur à limiter
            min_value: Valeur minimum
            max_value: Valeur maximum
            
        Returns:
            float: Valeur limitée
        """
        return max(min_value, min(value, max_value))


# ===================================================================
# EXPORTS
# ===================================================================

__all__ = ['BaseService', 'ServiceHelper']