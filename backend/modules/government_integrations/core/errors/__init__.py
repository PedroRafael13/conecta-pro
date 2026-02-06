"""
Sistema de Gerenciamento de Erros para Integrações Governamentais.

Implementa:
- Classificação automática de erros
- Retry com backoff exponencial
- Fila de reprocessamento
"""

from .error_classifier import (
    CategoriaErro,
    ErroIntegracao,
    ClassificadorErros,
)
from .retry_handler import (
    RetryConfig,
    retry_com_backoff,
    com_retry,
)
from .reprocessing_queue import (
    StatusReprocessamento,
    FilaReprocessamento,
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
