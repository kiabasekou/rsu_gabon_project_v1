"""
🇬🇦 RSU Gabon - Service de Base
Standards Top 1% - Architecture Service Layer
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class BaseService(ABC):
    """
    Service de base pour toutes les opérations métier
    """
    
    def __init__(self):
        self.logger = logger
        
    @transaction.atomic
    def execute_with_transaction(self, operation, *args, **kwargs):
        """Exécute une opération dans une transaction"""
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Erreur dans {self.__class__.__name__}: {str(e)}")
            raise
            
    def log_operation(self, operation: str, data: Dict[str, Any]):
        """Log une opération pour audit"""
        self.logger.info(f"{self.__class__.__name__} - {operation}: {data}")
