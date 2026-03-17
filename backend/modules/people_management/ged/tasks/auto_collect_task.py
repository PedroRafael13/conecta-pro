"""
Celery task: Auto-coleta de documentos apos fechamento de folha.

Executa apos o fechamento da folha de pagamento mensal.
Busca todos os clientes com funcionarios ativos, cria kits
e coleta documentos automaticamente.
"""

import logging
from datetime import date

logger = logging.getLogger(__name__)

try:
    from celery import shared_task
except ImportError:
    # Fallback para ambientes sem Celery instalado
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
    queue="ged",
)
def ged_auto_collect_documents(self, reference_month_iso: str) -> dict:
    """Task Celery para coleta automatica de documentos em kits.

    Deve ser chamada apos o fechamento da folha de pagamento mensal.
    Cria kits para todos os clientes ativos e coleta documentos
    de DP, Fiscal e Operacoes.

    Args:
        reference_month_iso: Mes de referencia em formato ISO (YYYY-MM-DD).
            Sera normalizado para o primeiro dia do mes.

    Returns:
        Dicionario com resumo da execucao.
    """
    import asyncio

    logger.info("Task ged_auto_collect_documents iniciada para %s", reference_month_iso)

    try:
        reference_month = date.fromisoformat(reference_month_iso)
    except (ValueError, TypeError):
        logger.error("Data invalida: %s", reference_month_iso)
        return {"error": f"Data invalida: {reference_month_iso}"}

    reference_month = reference_month.replace(day=1)

    async def _run():
        from core.database import async_session_factory

        async with async_session_factory() as db:
            try:
                from modules.people_management.ged.services.kit_builder_service import KitBuilderService

                builder = KitBuilderService(db)
                result = await builder.auto_build_all_kits(reference_month)
                await db.commit()

                logger.info(
                    "Task ged_auto_collect_documents concluida: %d kits criados para %s",
                    result.get("kits_created", 0),
                    reference_month.strftime("%m/%Y"),
                )
                return result

            except Exception as e:
                await db.rollback()
                logger.error("Erro na task ged_auto_collect_documents: %s", e)
                raise

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Dentro de um loop existente (ex: testes)
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _run())
                return future.result(timeout=600)
        else:
            return asyncio.run(_run())
    except RuntimeError:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Erro fatal na task ged_auto_collect_documents: %s", exc)
        if hasattr(self, "retry"):
            raise self.retry(exc=exc)
        return {"error": str(exc)}
