"""
Sistema de Rate Limiting para Integrações Governamentais.

Implementa:
- Rate limits por serviço governamental
- Filas Celery com prioridades
- Token bucket para controle de taxa
"""

from .celery_config import (
    CeleryConfig,
    TaskPriority,
    criar_celery_app,
    get_celery_config,
)
from .queue_manager import (
    GerenciadorFilas,
    StatusFila,
    get_queue_manager,
)
from .rate_limiter import (
    LIMITES_SERVICOS,
    LimiteServico,
    RateLimiter,
    get_rate_limiter,
)

__all__ = [
    # Rate Limiter
    "RateLimiter",
    "LimiteServico",
    "LIMITES_SERVICOS",
    "get_rate_limiter",
    # Celery
    "CeleryConfig",
    "TaskPriority",
    "criar_celery_app",
    "get_celery_config",
    # Queue Manager
    "GerenciadorFilas",
    "StatusFila",
    "get_queue_manager",
]
