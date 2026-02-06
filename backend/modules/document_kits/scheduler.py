"""
Scheduler para Geração Automática de Kits Mensais.

Este módulo configura jobs agendados para geração automática de kits
documentais mensais para todos os condomínios.

Autor: Jordan Santos de Jesus LTDA
Data: 23/01/2026
"""

import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session_factory
from modules.document_kits.services.kit_monthly_generator_service import KitMonthlyGeneratorService

logger = logging.getLogger(__name__)

# System user ID para criação automática
SYSTEM_USER_ID = "00000000-0000-0000-0000-000000000000"

# Instância global do scheduler
scheduler: AsyncIOScheduler | None = None


async def generate_monthly_kits_job():
    """
    Job agendado para geração automática de kits mensais.

    Executado automaticamente no dia 1 de cada mês às 02:00.
    Gera kits para todos os condomínios que possuem funcionários.
    """
    logger.info("========== INICIANDO JOB DE GERAÇÃO MENSAL DE KITS ==========")

    try:
        # Obter mês/ano atual
        now = datetime.now()
        month = now.month
        year = now.year

        logger.info(f"Gerando kits para período: {month:02d}/{year}")

        # Criar sessão async
        async with async_session_factory() as db:
            generator = KitMonthlyGeneratorService(db)

            # Executar geração em lote
            result = await generator.generate_kits_for_all_condominiums(
                month=month,
                year=year,
                created_by_id=SYSTEM_USER_ID,
            )

            # Log do resultado
            if result["success"]:
                logger.info(
                    f"Geração mensal concluída com sucesso: "
                    f"{result['condominiums_processed']} condomínios processados, "
                    f"{result['total_assignments_created']} kits criados, "
                    f"{result['total_assignments_skipped']} já existentes, "
                    f"{result['total_assignments_failed']} falhas"
                )
            else:
                logger.error(f"Erro na geração mensal: {result.get('error', 'Erro desconhecido')}")

        logger.info("========== JOB DE GERAÇÃO MENSAL FINALIZADO ==========")

    except Exception as e:
        logger.error(f"Erro fatal no job de geração mensal: {e}", exc_info=True)


def start_scheduler():
    """
    Inicia o scheduler de jobs agendados.

    Configura e inicia o APScheduler com os jobs necessários.
    """
    global scheduler

    if scheduler is not None:
        logger.warning("Scheduler já está iniciado")
        return

    logger.info("Iniciando scheduler de kits mensais...")

    scheduler = AsyncIOScheduler()

    # Job de geração mensal: Todo dia 1 às 02:00
    scheduler.add_job(
        generate_monthly_kits_job,
        trigger=CronTrigger(day=1, hour=2, minute=0),
        id="generate_monthly_kits",
        name="Geração Mensal de Kits Documentais",
        replace_existing=True,
        max_instances=1,  # Apenas uma instância por vez
        coalesce=True,  # Se perder execução, executa apenas uma vez
    )

    scheduler.start()

    logger.info("Scheduler iniciado com sucesso!")
    logger.info("Job configurado: Geração mensal (dia 1 às 02:00)")


def stop_scheduler():
    """
    Para o scheduler de jobs agendados.
    """
    global scheduler

    if scheduler is None:
        logger.warning("Scheduler não está iniciado")
        return

    logger.info("Parando scheduler...")
    scheduler.shutdown(wait=True)
    scheduler = None
    logger.info("Scheduler parado")


def get_scheduler_status() -> dict:
    """
    Retorna status do scheduler e próximas execuções.

    Returns:
        Dict com informações do scheduler
    """
    global scheduler

    if scheduler is None:
        return {
            "running": False,
            "message": "Scheduler não está iniciado",
        }

    jobs = []
    for job in scheduler.get_jobs():
        next_run = job.next_run_time.isoformat() if job.next_run_time else None
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": next_run,
            "trigger": str(job.trigger),
        })

    return {
        "running": True,
        "jobs_count": len(jobs),
        "jobs": jobs,
    }
