"""
Configuração Celery para Integrações Governamentais.

Define filas, prioridades e roteamento de tasks.
"""

import logging
from dataclasses import dataclass
from datetime import timedelta
from enum import IntEnum
from typing import Any

from celery import Celery
from kombu import Exchange, Queue

logger = logging.getLogger(__name__)


class TaskPriority(IntEnum):
    """Prioridades de tasks (menor = mais prioritário)."""

    CRITICA = 1  # Prazo legal iminente
    ALTA = 2  # eSocial, FGTS
    NORMAL = 5  # NF-e, CT-e padrão
    BAIXA = 7  # Sincronização batch
    BACKGROUND = 10  # Limpeza, relatórios


@dataclass
class CeleryConfig:
    """Configuração do Celery."""

    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/0"

    # Timezone
    timezone: str = "America/Sao_Paulo"
    enable_utc: bool = True

    # Serialização
    task_serializer: str = "json"
    result_serializer: str = "json"
    accept_content: list[str] = None

    # Comportamento
    task_acks_late: bool = True  # Confirma após execução
    task_reject_on_worker_lost: bool = True
    task_track_started: bool = True

    # Limites
    worker_prefetch_multiplier: int = 1  # Uma task por vez
    task_soft_time_limit: int = 300  # 5 minutos soft limit
    task_time_limit: int = 600  # 10 minutos hard limit

    # Retry
    task_default_retry_delay: int = 60
    task_max_retries: int = 3

    # Resultados
    result_expires: int = 86400  # 24 horas

    def __post_init__(self):
        if self.accept_content is None:
            self.accept_content = ["json"]


# Definição de Exchanges
EXCHANGES = {
    "government": Exchange("government", type="direct"),
    "government_priority": Exchange("government_priority", type="direct"),
    "government_dlq": Exchange("government_dlq", type="direct"),
}

# Definição de Filas
QUEUES = [
    # Filas de alta prioridade
    Queue(
        "gov.esocial", EXCHANGES["government_priority"], routing_key="esocial", queue_arguments={"x-max-priority": 10}
    ),
    Queue("gov.fgts", EXCHANGES["government_priority"], routing_key="fgts", queue_arguments={"x-max-priority": 10}),
    # Filas padrão por serviço
    Queue("gov.sefaz.nfe", EXCHANGES["government"], routing_key="sefaz.nfe", queue_arguments={"x-max-priority": 10}),
    Queue("gov.sefaz.cte", EXCHANGES["government"], routing_key="sefaz.cte", queue_arguments={"x-max-priority": 10}),
    Queue("gov.sefaz.mdfe", EXCHANGES["government"], routing_key="sefaz.mdfe", queue_arguments={"x-max-priority": 10}),
    Queue("gov.nfse", EXCHANGES["government"], routing_key="nfse", queue_arguments={"x-max-priority": 10}),
    Queue("gov.sped", EXCHANGES["government"], routing_key="sped", queue_arguments={"x-max-priority": 10}),
    # Fila de baixa prioridade (batch, sync)
    Queue("gov.batch", EXCHANGES["government"], routing_key="batch", queue_arguments={"x-max-priority": 5}),
    # Dead Letter Queue
    Queue(
        "gov.dlq",
        EXCHANGES["government_dlq"],
        routing_key="dlq",
    ),
]

# Roteamento de Tasks
TASK_ROUTES = {
    # eSocial
    "government_integrations.tasks.esocial.*": {
        "queue": "gov.esocial",
        "routing_key": "esocial",
    },
    # FGTS
    "government_integrations.tasks.fgts.*": {
        "queue": "gov.fgts",
        "routing_key": "fgts",
    },
    # SEFAZ NF-e
    "government_integrations.tasks.sefaz.nfe.*": {
        "queue": "gov.sefaz.nfe",
        "routing_key": "sefaz.nfe",
    },
    # SEFAZ CT-e
    "government_integrations.tasks.sefaz.cte.*": {
        "queue": "gov.sefaz.cte",
        "routing_key": "sefaz.cte",
    },
    # SEFAZ MDF-e
    "government_integrations.tasks.sefaz.mdfe.*": {
        "queue": "gov.sefaz.mdfe",
        "routing_key": "sefaz.mdfe",
    },
    # NFS-e
    "government_integrations.tasks.nfse.*": {
        "queue": "gov.nfse",
        "routing_key": "nfse",
    },
    # SPED
    "government_integrations.tasks.sped.*": {
        "queue": "gov.sped",
        "routing_key": "sped",
    },
    # Batch/Sync
    "government_integrations.tasks.batch.*": {
        "queue": "gov.batch",
        "routing_key": "batch",
    },
    "government_integrations.tasks.sync.*": {
        "queue": "gov.batch",
        "routing_key": "batch",
    },
}

# Agendamentos (Celery Beat)
BEAT_SCHEDULE = {
    # Sincronização NF-e a cada 30 minutos
    "sync-nfe-30min": {
        "task": "government_integrations.tasks.sync.sincronizar_nfe",
        "schedule": timedelta(minutes=30),
        "options": {"queue": "gov.batch", "priority": TaskPriority.BAIXA},
    },
    # Verificação de disponibilidade a cada 5 minutos
    "check-availability-5min": {
        "task": "government_integrations.tasks.monitoring.verificar_disponibilidade",
        "schedule": timedelta(minutes=5),
        "options": {"queue": "gov.batch", "priority": TaskPriority.BACKGROUND},
    },
    # Reprocessamento de falhas a cada 15 minutos
    "reprocess-failures-15min": {
        "task": "government_integrations.tasks.reprocess.reprocessar_falhas",
        "schedule": timedelta(minutes=15),
        "options": {"queue": "gov.batch", "priority": TaskPriority.NORMAL},
    },
    # Limpeza de cache diária
    "cleanup-daily": {
        "task": "government_integrations.tasks.maintenance.limpar_cache",
        "schedule": timedelta(hours=24),
        "options": {"queue": "gov.batch", "priority": TaskPriority.BACKGROUND},
    },
    # Verificação de certificados a cada 6 horas
    "check-certificates-6h": {
        "task": "government_integrations.tasks.monitoring.verificar_certificados",
        "schedule": timedelta(hours=6),
        "options": {"queue": "gov.batch", "priority": TaskPriority.ALTA},
    },
}


def criar_celery_app(config: CeleryConfig | None = None, name: str = "government_integrations") -> Celery:
    """
    Cria e configura aplicação Celery.

    Args:
        config: Configuração do Celery
        name: Nome da aplicação

    Returns:
        Instância configurada do Celery
    """
    if config is None:
        config = CeleryConfig()

    app = Celery(name)

    # Configuração básica
    app.conf.update(
        broker_url=config.broker_url,
        result_backend=config.result_backend,
        timezone=config.timezone,
        enable_utc=config.enable_utc,
        task_serializer=config.task_serializer,
        result_serializer=config.result_serializer,
        accept_content=config.accept_content,
        task_acks_late=config.task_acks_late,
        task_reject_on_worker_lost=config.task_reject_on_worker_lost,
        task_track_started=config.task_track_started,
        worker_prefetch_multiplier=config.worker_prefetch_multiplier,
        task_soft_time_limit=config.task_soft_time_limit,
        task_time_limit=config.task_time_limit,
        task_default_retry_delay=config.task_default_retry_delay,
        task_max_retries=config.task_max_retries,
        result_expires=config.result_expires,
    )

    # Filas
    app.conf.task_queues = QUEUES

    # Roteamento
    app.conf.task_routes = TASK_ROUTES

    # Beat Schedule
    app.conf.beat_schedule = BEAT_SCHEDULE

    # Default queue
    app.conf.task_default_queue = "gov.batch"
    app.conf.task_default_exchange = "government"
    app.conf.task_default_routing_key = "batch"

    # Configurar dead letter queue
    app.conf.task_reject_on_worker_lost = True
    app.conf.task_acks_on_failure_or_timeout = False

    logger.info(f"Celery app '{name}' configurado com {len(QUEUES)} filas")

    return app


def get_celery_config() -> dict[str, Any]:
    """Retorna configuração atual como dicionário."""
    config = CeleryConfig()
    return {
        "broker_url": config.broker_url,
        "result_backend": config.result_backend,
        "queues": [q.name for q in QUEUES],
        "routes": list(TASK_ROUTES.keys()),
        "beat_tasks": list(BEAT_SCHEDULE.keys()),
    }


# Decoradores para tasks com rate limiting integrado
def governo_task(servico: str, prioridade: TaskPriority = TaskPriority.NORMAL, rate_limit: str | None = None):
    """
    Decorador para tasks de integração governamental.

    Args:
        servico: Nome do serviço (sefaz_nfe, esocial, etc)
        prioridade: Prioridade da task
        rate_limit: Rate limit específico (ex: "10/m")

    Exemplo:
        @governo_task("sefaz_nfe", TaskPriority.NORMAL)
        def consultar_nfe(chave: str):
            ...
    """

    def decorator(func):
        # Importar aqui para evitar circular import
        from functools import wraps

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Rate limiting é aplicado pelo queue_manager
            return await func(*args, **kwargs)

        # Adicionar metadata
        wrapper._governo_servico = servico
        wrapper._governo_prioridade = prioridade
        wrapper._governo_rate_limit = rate_limit

        return wrapper

    return decorator
