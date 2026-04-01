"""
Celery task: Sincronizacao diaria de CNDs.

Executa diariamente para verificar se ha certidoes negativas
renovadas e atualizar todos os kits EM_MONTAGEM com as versoes
mais recentes.
"""

import logging
import os
from datetime import datetime

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


# Mapeamento de tipos de CND para caminhos no storage
CND_STORAGE_PATHS = {
    "cnd_federal": "documents/fiscal/certidoes/cnd_federal.pdf",
    "cnd_estadual": "documents/fiscal/certidoes/cnd_estadual.pdf",
    "cnd_municipal": "documents/fiscal/certidoes/cnd_municipal.pdf",
    "crf_fgts": "documents/fiscal/certidoes/crf_fgts.pdf",
    "cndt_trabalhista": "documents/fiscal/certidoes/cndt_trabalhista.pdf",
}

GED_STORAGE_BASE = os.environ.get("GED_STORAGE_PATH", "/opt/conecta-pro/storage/ged")


@shared_task(
    name="ged.sync_cnds",
    bind=True,
    max_retries=2,
    default_retry_delay=600,
    queue="ged",
)
def ged_sync_cnds(self) -> dict:
    """Task Celery para sincronizacao de CNDs em kits.

    Verifica se alguma CND foi renovada (arquivo modificado recentemente)
    e atualiza em todos os kits EM_MONTAGEM.

    Execucao recomendada: diariamente via Celery Beat.

    Returns:
        Dicionario com resumo da sincronizacao.
    """
    import asyncio

    logger.info("Task ged_sync_cnds iniciada")

    async def _run():
        from core.database import async_session_factory

        async with async_session_factory() as db:
            try:
                from modules.people_management.ged.events.handlers import on_cnd_renewed

                total_updated = 0
                total_created = 0
                cnds_checked = 0
                cnds_renewed = []

                for cnd_type, relative_path in CND_STORAGE_PATHS.items():
                    full_path = os.path.join(GED_STORAGE_BASE, relative_path)
                    cnds_checked += 1

                    # Verificar se o arquivo existe e foi modificado nas ultimas 24h
                    if os.path.exists(full_path):
                        mod_time = datetime.fromtimestamp(os.path.getmtime(full_path))
                        now = datetime.utcnow()
                        hours_since_modified = (now - mod_time).total_seconds() / 3600

                        if hours_since_modified <= 24:
                            logger.info(
                                "CND %s renovada (modificada ha %.1fh): %s",
                                cnd_type,
                                hours_since_modified,
                                relative_path,
                            )

                            result = await on_cnd_renewed(
                                db=db,
                                cnd_type=cnd_type,
                                file_path=relative_path,
                            )

                            total_updated += result.get("documents_updated", 0)
                            total_created += result.get("documents_created", 0)
                            cnds_renewed.append(cnd_type)
                    else:
                        logger.debug("CND %s nao encontrada em %s", cnd_type, full_path)

                if cnds_renewed:
                    await db.commit()
                    logger.info(
                        "Task ged_sync_cnds: %d CNDs renovadas, %d docs atualizados, %d criados",
                        len(cnds_renewed),
                        total_updated,
                        total_created,
                    )
                else:
                    logger.info("Task ged_sync_cnds: nenhuma CND renovada nas ultimas 24h")

                return {
                    "cnds_checked": cnds_checked,
                    "cnds_renewed": cnds_renewed,
                    "documents_updated": total_updated,
                    "documents_created": total_created,
                    "executed_at": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                await db.rollback()
                logger.error("Erro na task ged_sync_cnds: %s", e)
                raise

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _run())
                return future.result(timeout=300)
        else:
            return asyncio.run(_run())
    except RuntimeError:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Erro fatal na task ged_sync_cnds: %s", exc)
        if hasattr(self, "retry"):
            raise self.retry(exc=exc)
        return {"error": str(exc)}
