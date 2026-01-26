"""Celery Tasks - Módulo Operacional.

Sprint: Módulo Operacional - Sistema de Notificações Push
"""

import logging
from uuid import UUID

from celery_app import app
from core.database.session import get_sync_db
from modules.operacional.services.notification_triggers import (
    OperacionalNotificationTriggers,
)

logger = logging.getLogger(__name__)


@app.task(
    name="operacional.check_late_employees",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def check_late_employees_task(self):
    """Tarefa Celery: Verifica colaboradores atrasados.

    Executada a cada 5 minutos via Celery Beat.
    """
    try:
        with get_sync_db() as db:
            # TODO: Obter tenant_id de configuração ou processar todos os tenants
            tenant_id = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")

            triggers = OperacionalNotificationTriggers(db, tenant_id)
            result = triggers.check_late_employees()

            logger.info(f"[Operacional Task] Verificação de atrasos: {result}")
            return result

    except Exception as exc:
        logger.error(f"[Operacional Task] Erro ao verificar atrasos: {exc}")
        raise self.retry(exc=exc)


@app.task(
    name="operacional.check_pending_approvals",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def check_pending_approvals_task(self):
    """Tarefa Celery: Verifica aprovações pendentes.

    Executada a cada 1 hora via Celery Beat.
    """
    try:
        with get_sync_db() as db:
            # TODO: Obter tenant_id de configuração ou processar todos os tenants
            tenant_id = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")

            triggers = OperacionalNotificationTriggers(db, tenant_id)
            result = triggers.check_pending_approvals()

            logger.info(f"[Operacional Task] Verificação de aprovações: {result}")
            return result

    except Exception as exc:
        logger.error(f"[Operacional Task] Erro ao verificar aprovações: {exc}")
        raise self.retry(exc=exc)
