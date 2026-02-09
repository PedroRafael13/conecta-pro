"""Celery Tasks - Módulo Operacional.

Sprint: Módulo Operacional - Sistema de Notificações Push
Sprint: Geração Automática de Escalas
"""

import asyncio
import logging

from celery_app import app
from core.database.session import get_async_db_session, get_sync_db
from modules.operacional.services.notification_triggers import (
    OperacionalNotificationTriggers,
    _get_active_tenants,
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
    Itera sobre todos os tenants ativos.
    """
    try:
        with get_sync_db() as db:
            tenant_ids = _get_active_tenants(db)
            logger.info(f"[Operacional Task] Verificando atrasos em {len(tenant_ids)} tenants")

            results = []
            for tenant_id in tenant_ids:
                try:
                    triggers = OperacionalNotificationTriggers(db, tenant_id)
                    result = triggers.check_late_employees()
                    results.append({"tenant_id": str(tenant_id), **result})
                except Exception as e:
                    logger.error(f"[Operacional Task] Atrasos falhou para tenant {tenant_id}: {e}")

            logger.info(f"[Operacional Task] Verificação de atrasos concluída: {len(results)} tenants")
            return results

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
    Itera sobre todos os tenants ativos.
    """
    try:
        with get_sync_db() as db:
            tenant_ids = _get_active_tenants(db)
            logger.info(f"[Operacional Task] Verificando aprovações em {len(tenant_ids)} tenants")

            results = []
            for tenant_id in tenant_ids:
                try:
                    triggers = OperacionalNotificationTriggers(db, tenant_id)
                    result = triggers.check_pending_approvals()
                    results.append({"tenant_id": str(tenant_id), **result})
                except Exception as e:
                    logger.error(f"[Operacional Task] Aprovações falhou para tenant {tenant_id}: {e}")

            logger.info(f"[Operacional Task] Verificação de aprovações concluída: {len(results)} tenants")
            return results

    except Exception as exc:
        logger.error(f"[Operacional Task] Erro ao verificar aprovações: {exc}")
        raise self.retry(exc=exc)


@app.task(
    name="operacional.auto_generate_monthly_scales",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def auto_generate_monthly_scales_task(self, month: int = None, year: int = None):
    """Tarefa Celery: Gera escalas automaticamente para o mês.

    Executada no dia 1º de cada mês via Celery Beat, ou sob demanda.
    Itera sobre todos os tenants ativos.

    Args:
        month: Mês (1-12), se None usa mês atual
        year: Ano, se None usa ano atual
    """
    try:
        from modules.operacional.services.auto_scale_service import AutoScaleService

        async def _generate():
            async with get_async_db_session() as db:
                service = AutoScaleService(db)

                if month and year:
                    result = await service.generate_scales_for_month(month, year)
                else:
                    result = await service.generate_scales_for_current_month()

                return result

        # Executar função async
        result = asyncio.run(_generate())

        logger.info(f"[Operacional Task] Geração automática de escalas: {result}")
        return result

    except Exception as exc:
        logger.error(f"[Operacional Task] Erro ao gerar escalas: {exc}")
        raise self.retry(exc=exc)
