"""
Jobs Celery para Sincronização Governamental.

Tarefas agendadas para extração automática de dados.
"""

from .sync_tasks import (
    sincronizar_nfe,
    sincronizar_esocial,
    sincronizar_fgts,
    sincronizar_nfse,
    sincronizar_rfb,
    sincronizar_todos,
)
from .monitoring_tasks import (
    verificar_disponibilidade,
    verificar_certificados,
    reprocessar_falhas,
)
from .gov_sync_jobs import (
    GovSyncJobManager,
    SyncJobType,
    SyncJobConfig,
    SYNC_JOBS_CONFIG,
)

__all__ = [
    # Job Manager
    "GovSyncJobManager",
    "SyncJobType",
    "SyncJobConfig",
    "SYNC_JOBS_CONFIG",
    # Sync
    "sincronizar_nfe",
    "sincronizar_esocial",
    "sincronizar_fgts",
    "sincronizar_nfse",
    "sincronizar_rfb",
    "sincronizar_todos",
    # Monitoring
    "verificar_disponibilidade",
    "verificar_certificados",
    "reprocessar_falhas",
]
