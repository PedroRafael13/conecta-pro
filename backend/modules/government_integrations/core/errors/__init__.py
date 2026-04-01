"""
Sistema de Gerenciamento de Erros para Integrações Governamentais.

Implementa:
- Classificação automática de erros
- Retry com backoff exponencial
- Fila de reprocessamento
"""

from .error_classifier import (
    CategoriaErro,
    ClassificadorErros,
    ErroIntegracao,
)
from .reprocessing_queue import (
    FilaReprocessamento,
    StatusReprocessamento,
)
from .retry_handler import (
    RetryConfig,
    com_retry,
    retry_com_backoff,
)

__all__ = [
    "CategoriaErro",
    "ErroIntegracao",
    "ClassificadorErros",
    "RetryConfig",
    "retry_com_backoff",
    "com_retry",
    "StatusReprocessamento",
    "FilaReprocessamento",
]
