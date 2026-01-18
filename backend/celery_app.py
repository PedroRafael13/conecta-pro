"""
Aplicação Celery - Conecta Plus.

Ponto de entrada para os workers Celery de integrações governamentais.
"""

import os
import sys
from celery import Celery
from kombu import Queue, Exchange

# Broker e Backend (Redis)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")
BROKER_URL = os.getenv("CELERY_BROKER_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

# Criar aplicação Celery
app = Celery(
    "conecta_plus",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=[
        "modules.government_integrations.jobs.sync_tasks",
        "modules.government_integrations.jobs.monitoring_tasks",
        "modules.integrations.connectors.solides.tasks",
    ]
)

# Exchanges
government_exchange = Exchange("government", type="direct")
government_priority_exchange = Exchange("government_priority", type="direct")
integrations_exchange = Exchange("integrations", type="direct")

# Filas
app.conf.task_queues = [
    # Alta prioridade
    Queue("gov.esocial", government_priority_exchange, routing_key="esocial",
          queue_arguments={"x-max-priority": 10}),
    Queue("gov.fgts", government_priority_exchange, routing_key="fgts",
          queue_arguments={"x-max-priority": 10}),

    # Serviços SEFAZ
    Queue("gov.sefaz.nfe", government_exchange, routing_key="sefaz.nfe",
          queue_arguments={"x-max-priority": 10}),
    Queue("gov.sefaz.cte", government_exchange, routing_key="sefaz.cte",
          queue_arguments={"x-max-priority": 10}),
    Queue("gov.sefaz.mdfe", government_exchange, routing_key="sefaz.mdfe",
          queue_arguments={"x-max-priority": 10}),

    # NFS-e
    Queue("gov.nfse", government_exchange, routing_key="nfse",
          queue_arguments={"x-max-priority": 10}),

    # Batch/Sync/Monitoramento
    Queue("gov.batch", government_exchange, routing_key="batch",
          queue_arguments={"x-max-priority": 5}),

    # Integrações - Sólides
    Queue("integrations", integrations_exchange, routing_key="integrations",
          queue_arguments={"x-max-priority": 5}),
    Queue("webhooks", integrations_exchange, routing_key="webhooks",
          queue_arguments={"x-max-priority": 8}),
    Queue("maintenance", integrations_exchange, routing_key="maintenance",
          queue_arguments={"x-max-priority": 3}),
]

# Roteamento de tasks
app.conf.task_routes = {
    # Sync tasks
    "government_integrations.tasks.sync.*": {"queue": "gov.batch"},
    "government_integrations.tasks.sync.sincronizar_nfe": {"queue": "gov.sefaz.nfe"},
    "government_integrations.tasks.sync.sincronizar_esocial": {"queue": "gov.esocial"},
    "government_integrations.tasks.sync.sincronizar_fgts": {"queue": "gov.fgts"},
    "government_integrations.tasks.sync.sincronizar_nfse": {"queue": "gov.nfse"},

    # Monitoring tasks
    "government_integrations.tasks.monitoring.*": {"queue": "gov.batch"},
    "government_integrations.tasks.reprocess.*": {"queue": "gov.batch"},
    "government_integrations.tasks.maintenance.*": {"queue": "gov.batch"},

    # Sólides Integration tasks
    "solides.full_sync": {"queue": "integrations"},
    "solides.incremental_sync": {"queue": "integrations"},
    "solides.sync_all_condominios_incremental": {"queue": "integrations"},
    "solides.sync_single_entity": {"queue": "integrations"},
    "solides.health_check": {"queue": "integrations"},
    "solides.health_check_all": {"queue": "integrations"},
    "solides.process_webhook_queue": {"queue": "webhooks"},
    "solides.retry_failed_webhooks": {"queue": "integrations"},
    "solides.cleanup_old_logs": {"queue": "maintenance"},
    "solides.cleanup_old_webhooks": {"queue": "maintenance"},
}

# Configurações gerais
app.conf.update(
    # Timezone
    timezone="America/Sao_Paulo",
    enable_utc=True,

    # Serialização
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Comportamento
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,

    # Limites
    worker_prefetch_multiplier=1,
    task_soft_time_limit=300,  # 5 min
    task_time_limit=600,       # 10 min

    # Retry
    task_default_retry_delay=60,

    # Resultados
    result_expires=86400,  # 24h

    # Default queue
    task_default_queue="gov.batch",
)

# Beat Schedule (tarefas agendadas)
app.conf.beat_schedule = {
    # Verificação de disponibilidade a cada 5 minutos
    "check-endpoints-5min": {
        "task": "government_integrations.tasks.monitoring.verificar_disponibilidade",
        "schedule": 300.0,  # 5 minutos
        "options": {"queue": "gov.batch"},
    },
    # Verificação de certificados a cada 6 horas
    "check-certificates-6h": {
        "task": "government_integrations.tasks.monitoring.verificar_certificados",
        "schedule": 21600.0,  # 6 horas
        "options": {"queue": "gov.batch"},
    },
    # Reprocessamento de falhas a cada 15 minutos
    "reprocess-failures-15min": {
        "task": "government_integrations.tasks.reprocess.reprocessar_falhas",
        "schedule": 900.0,  # 15 minutos
        "options": {"queue": "gov.batch"},
    },
    # Relatório diário às 06:00
    "daily-report": {
        "task": "government_integrations.tasks.monitoring.gerar_relatorio_diario",
        "schedule": 86400.0,  # 24 horas
        "options": {"queue": "gov.batch"},
    },
    # Limpeza de cache diária
    "cleanup-cache-daily": {
        "task": "government_integrations.tasks.maintenance.limpar_cache",
        "schedule": 86400.0,  # 24 horas
        "options": {"queue": "gov.batch"},
    },

    # =========================================================================
    # SÓLIDES - INTEGRAÇÃO RH/DP
    # =========================================================================
    # Sync incremental a cada 15 minutos
    "solides-incremental-sync-all": {
        "task": "solides.sync_all_condominios_incremental",
        "schedule": 900.0,  # 15 minutos
        "options": {"queue": "integrations"},
    },
    # Health check a cada 5 minutos
    "solides-health-check-all": {
        "task": "solides.health_check_all",
        "schedule": 300.0,  # 5 minutos
        "options": {"queue": "integrations"},
    },
    # Processar fila de webhooks a cada 30 segundos
    "solides-process-webhooks": {
        "task": "solides.process_webhook_queue",
        "schedule": 30.0,
        "options": {"queue": "webhooks"},
    },
    # Retry de webhooks falhos a cada hora
    "solides-retry-failed-webhooks": {
        "task": "solides.retry_failed_webhooks",
        "schedule": 3600.0,  # 1 hora
        "options": {"queue": "integrations"},
    },
    # Cleanup de logs de sync (diário às 4 AM via crontab)
    "solides-cleanup-sync-logs": {
        "task": "solides.cleanup_old_logs",
        "schedule": 86400.0,  # 24 horas
        "args": (30,),  # manter 30 dias
        "options": {"queue": "maintenance"},
    },
    # Cleanup de logs de webhook (diário às 4:30 AM via crontab)
    "solides-cleanup-webhook-logs": {
        "task": "solides.cleanup_old_webhooks",
        "schedule": 86400.0,  # 24 horas
        "args": (7,),  # manter 7 dias
        "options": {"queue": "maintenance"},
    },
}


if __name__ == "__main__":
    app.start()
