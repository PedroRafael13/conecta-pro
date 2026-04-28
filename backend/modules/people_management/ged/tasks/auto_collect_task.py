"""
Celery task: Coleta Automática mensal (D4).

Executa sync Onvio + auto-assemble + matching via ColetaAutomaticaService.
Registra resultado em ged_coleta_logs e atualiza ged_coleta_config.last_run.
"""

import logging
from datetime import date

logger = logging.getLogger(__name__)

try:
    from celery import shared_task
except ImportError:

    def shared_task(*args, **kwargs):
        def decorator(func):
            func.delay = lambda *a, **kw: func(*a, **kw)
            func.apply_async = lambda *a, **kw: func(*a, **kw)
            return func

        if args and callable(args[0]):
            return decorator(args[0])
        return decorator


@shared_task(
    name="ged.auto_collect_documents",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    queue="operacional",
)
def ged_auto_collect_documents(self, reference_month_iso: str | None = None) -> dict:
    """Task Celery para coleta automática mensal (D4).

    Orquestra: sync Onvio → auto-assemble → matching → log ged_coleta_logs.

    Args:
        reference_month_iso: Mês de referência ISO (YYYY-MM-DD).
            Se None, usa os 3 meses mais recentes.

    Returns:
        Dict com status, duration_ms, sync_novos, kits_assembled, onvio_matched, erros.
    """
    import asyncio

    if reference_month_iso is not None:
        try:
            ref = date.fromisoformat(reference_month_iso).replace(day=1)
            reference_month_iso = ref.isoformat()
        except (ValueError, TypeError):
            logger.error("Data invalida: %s", reference_month_iso)
            return {"error": f"Data invalida: {reference_month_iso}"}

    logger.info("Task ged_auto_collect_documents iniciada para mes_ref=%s", reference_month_iso or "ultimos 3 meses")

    async def _run() -> dict:
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

        from core.config.settings import get_settings
        from modules.people_management.ged.services.coleta_automatica_service import (
            ColetaAutomaticaService,
        )

        settings = get_settings()
        engine = create_async_engine(settings.database_url)
        _factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with _factory() as db:
            svc = ColetaAutomaticaService(db)
            result = await svc.executar(
                run_type="cron",
                triggered_by="celery-beat",
                mes_ref=reference_month_iso,
            )
            return result

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _run())
                result = future.result(timeout=600)
        else:
            result = asyncio.run(_run())

        logger.info(
            "Task ged_auto_collect_documents concluida: status=%s kits=%d",
            result.get("status"),
            result.get("kits_assembled", 0),
        )
        return result

    except Exception as exc:
        logger.error("Erro fatal na task ged_auto_collect_documents: %s", exc)
        if hasattr(self, "retry"):
            raise self.retry(exc=exc)
        return {"error": str(exc)}
