"""Cronjobs - Configuração de tarefas agendadas do módulo operacional.

Sprint: Módulo Operacional - Sistema de Notificações Push
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from modules.operacional.services.notification_triggers import (
    run_late_employees_check,
    run_pending_approvals_check,
)

logger = logging.getLogger(__name__)

# Scheduler global
scheduler = BackgroundScheduler()


def setup_operacional_cronjobs():
    """Configura cronjobs do módulo operacional."""

    # Verifica colaboradores atrasados a cada 5 minutos
    scheduler.add_job(
        run_late_employees_check,
        trigger=IntervalTrigger(minutes=5),
        id="check_late_employees",
        name="Verificar colaboradores atrasados",
        replace_existing=True,
        max_instances=1,
    )

    # Verifica aprovações pendentes a cada hora
    scheduler.add_job(
        run_pending_approvals_check,
        trigger=IntervalTrigger(hours=1),
        id="check_pending_approvals",
        name="Verificar aprovações pendentes",
        replace_existing=True,
        max_instances=1,
    )

    logger.info("Cronjobs do módulo operacional configurados")


def start_scheduler():
    """Inicia o scheduler de cronjobs."""
    if not scheduler.running:
        setup_operacional_cronjobs()
        scheduler.start()
        logger.info("Scheduler de cronjobs iniciado")


def stop_scheduler():
    """Para o scheduler de cronjobs."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler de cronjobs parado")
