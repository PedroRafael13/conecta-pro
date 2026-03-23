"""
Celery Tasks para sincronização Sólides.
Sprint 33: Integration Framework

Tasks agendadas para sincronização automática e health checks.
"""

import asyncio
import logging
import os
from uuid import UUID, uuid4

from celery import shared_task

logger = logging.getLogger(__name__)


def get_event_loop():
    """Obtém ou cria event loop para execução de código async."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def run_async(coro):
    """Executa coroutine de forma síncrona."""
    loop = get_event_loop()
    return loop.run_until_complete(coro)


def _propagate_employees_to_db(solides_employees: list[dict]) -> dict:
    """Propaga dados do Tangerino para tabela employees (por CPF).

    Atualiza campos pessoais (nascimento, sexo, PIS, admissao, solides_id).
    NAO toca em cargo e salario (mantidos do cadastro interno).
    Inativa funcionarios que nao estao mais no Solides.

    Returns:
        Dict com estatisticas de propagacao.
    """
    from datetime import datetime

    from sqlalchemy import create_engine, text

    db_url = os.environ.get("DATABASE_URL", "").replace("+asyncpg", "")
    if not db_url:
        logger.warning("[Solides] DATABASE_URL nao configurado, pulando propagacao")
        return {"propagated": 0, "error": "no_db_url"}

    engine = create_engine(db_url)
    updated = 0
    not_found = 0
    inactivated = 0
    cpfs_solides = set()

    with engine.connect() as conn:
        for emp in solides_employees:
            cpf = (emp.get("cpf") or "").replace(".", "").replace("-", "").strip()
            if not cpf:
                continue
            cpfs_solides.add(cpf)

            # Parse birthDate (ms timestamp)
            birth = None
            bd = emp.get("birthDate")
            if bd:
                try:
                    birth = datetime.fromtimestamp(bd / 1000).date()
                except Exception:
                    pass

            # Parse admissionDate
            adm = None
            ad = emp.get("admissionDate")
            if ad:
                try:
                    adm = datetime.fromtimestamp(ad / 1000).date()
                except Exception:
                    pass

            # Gender (varchar(1))
            gender = emp.get("gender", "")
            sexo = None
            if "FEM" in gender.upper():
                sexo = "F"
            elif "MASC" in gender.upper():
                sexo = "M"

            pis = (emp.get("pis", "") or "")[:20]
            sid = str(emp.get("id", ""))
            name = emp.get("name", "")

            sets = []
            params = {"cpf": cpf}
            if birth:
                sets.append("data_nascimento = :b")
                params["b"] = birth
            if sexo:
                sets.append("sexo = :s")
                params["s"] = sexo
            if pis:
                sets.append("pis = :p")
                params["p"] = pis
            if adm:
                sets.append("data_admissao = :a")
                params["a"] = adm
            if sid:
                sets.append("solides_id = :sid")
                params["sid"] = sid
            if name:
                sets.append("nome = :nome")
                params["nome"] = name

            if sets:
                sql = f"UPDATE employees SET {', '.join(sets)} WHERE cpf = :cpf AND status = 'ativo'"
                r = conn.execute(text(sql), params)
                if r.rowcount > 0:
                    updated += 1
                else:
                    not_found += 1

        # Inativar quem tem solides_id mas nao esta mais no Solides
        if cpfs_solides:
            cpf_list = ",".join(f"'{c}'" for c in cpfs_solides)
            inact_sql = text(
                f"UPDATE employees SET status = 'inativo' "
                f"WHERE solides_id IS NOT NULL AND cpf NOT IN ({cpf_list}) "
                f"AND status = 'ativo'"
            )
            r = conn.execute(inact_sql)
            inactivated = r.rowcount

        conn.commit()

    logger.info(
        "[Solides] Propagacao: %d atualizados, %d sem match, %d inativados",
        updated,
        not_found,
        inactivated,
    )
    return {
        "propagated": updated,
        "not_found": not_found,
        "inactivated": inactivated,
        "total_solides": len(solides_employees),
    }


# ==================== SYNC TASKS ====================


@shared_task(
    bind=True,
    name="solides.full_sync",
    max_retries=3,
    default_retry_delay=300,
    soft_time_limit=3600,
    time_limit=3900,
)
def sync_solides_full(
    self, condominio_id: str = None, entity_types: list[str] | None = None, triggered_by: str = "scheduler"
):
    """
    Task para sincronização completa com Sólides.

    Args:
        condominio_id: ID do condomínio (opcional)
        entity_types: Tipos de entidade (ou todas configuradas)
        triggered_by: Quem disparou (user, scheduler, webhook)
    """
    logger.info("[Solides Task] Iniciando full sync")

    async def _sync():
        from modules.integrations.connectors.solides.connector import SolidesConnector

        api_token = os.getenv("SOLIDES_API_TOKEN")
        if not api_token:
            return {"success": False, "error": "SOLIDES_API_TOKEN não configurado"}

        connector = SolidesConnector(
            account_id=uuid4(),
            tenant_id=UUID(condominio_id) if condominio_id else uuid4(),
            config={},
            credentials={"api_token": api_token},
        )

        await connector.setup()

        try:
            results = {
                "employees": 0,
                "job_roles": 0,
                "workplaces": 0,
                "work_schedules": 0,
            }

            # Sincronizar cada entidade
            employees_data = []
            for entity_type in entity_types or ["employees", "job_roles", "workplaces", "work_schedules"]:
                try:
                    result = await connector.fetch_entities(entity_type, page_size=100)
                    if result.success:
                        results[entity_type] = len(result.data)
                        logger.info(f"[Solides Task] Sincronizado {entity_type}: {len(result.data)} registros")
                        if entity_type == "employees":
                            employees_data = result.data
                except Exception as e:
                    logger.error(f"[Solides Task] Erro ao sincronizar {entity_type}: {e}")

            # Propagar dados dos funcionarios para tabela employees
            propagation = {"propagated": 0}
            if employees_data:
                try:
                    propagation = _propagate_employees_to_db(employees_data)
                    logger.info(f"[Solides Task] Propagacao: {propagation}")
                except Exception as e:
                    logger.error(f"[Solides Task] Erro na propagacao: {e}")
                    propagation = {"propagated": 0, "error": str(e)}

            return {
                "success": True,
                "triggered_by": triggered_by,
                "results": results,
                "total": sum(results.values()),
                "propagation": propagation,
            }
        finally:
            await connector.teardown()

    try:
        return run_async(_sync())
    except Exception as e:
        logger.error(f"[Solides Task] Erro no full sync: {e}")
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    name="solides.incremental_sync",
    max_retries=5,
    default_retry_delay=60,
    soft_time_limit=600,
    time_limit=660,
)
def sync_solides_incremental(self, condominio_id: str = None, entity_types: list[str] | None = None):
    """
    Task para sincronização incremental com Sólides.
    """
    logger.debug("[Solides Task] Iniciando incremental sync")

    async def _sync():
        from modules.integrations.connectors.solides.connector import SolidesConnector

        api_token = os.getenv("SOLIDES_API_TOKEN")
        if not api_token:
            return {"success": False, "error": "Token não configurado"}

        connector = SolidesConnector(
            account_id=uuid4(),
            tenant_id=UUID(condominio_id) if condominio_id else uuid4(),
            config={},
            credentials={"api_token": api_token},
        )

        await connector.setup()

        try:
            # Busca funcionarios atuais do Solides
            result = await connector.fetch_entities("employees", page_size=100)

            propagation = {"propagated": 0}
            if result.success and result.data:
                try:
                    propagation = _propagate_employees_to_db(result.data)
                except Exception as e:
                    logger.error(f"[Solides Task] Erro na propagacao incremental: {e}")
                    propagation = {"propagated": 0, "error": str(e)}

            return {
                "success": result.success,
                "processed": len(result.data) if result.success else 0,
                "propagation": propagation,
            }
        finally:
            await connector.teardown()

    try:
        return run_async(_sync())
    except Exception as e:
        logger.error(f"[Solides Task] Erro no incremental sync: {e}")
        raise self.retry(exc=e)


@shared_task(name="solides.sync_all_condominios_incremental")
def sync_all_condominios_incremental():
    """
    Task para sincronização incremental de TODOS os condomínios ativos.
    """
    logger.info("[Solides Task] Iniciando sync incremental de todos condomínios")

    # Por enquanto, executa um único sync global
    # Futuramente: buscar lista de condomínios configurados
    result = sync_solides_incremental.delay()

    return {"condominios": 1, "task_id": str(result.id)}


@shared_task(name="solides.sync_single_entity")
def sync_single_entity(condominio_id: str = None, entity_type: str = "employees", solides_id: str = None):
    """
    Task para sincronizar uma única entidade.
    """
    logger.info(f"[Solides Task] Sync single entity: {entity_type}/{solides_id}")

    async def _sync():
        from modules.integrations.connectors.solides.connector import SolidesConnector

        api_token = os.getenv("SOLIDES_API_TOKEN")
        if not api_token:
            return {"success": False, "error": "Token não configurado"}

        connector = SolidesConnector(
            account_id=uuid4(),
            tenant_id=UUID(condominio_id) if condominio_id else uuid4(),
            config={},
            credentials={"api_token": api_token},
        )

        await connector.setup()

        try:
            if solides_id:
                result = await connector.fetch_entity_by_id(entity_type, solides_id)
                return {"success": result is not None, "action": "fetched" if result else "not_found", "data": result}
            else:
                return {"success": False, "error": "solides_id é obrigatório"}
        finally:
            await connector.teardown()

    return run_async(_sync())


# ==================== HEALTH CHECK TASKS ====================


@shared_task(name="solides.health_check")
def check_solides_health(condominio_id: str = None):
    """
    Task para verificar saúde da conexão com Sólides.
    """
    logger.debug("[Solides Task] Health check")

    async def _check():
        from modules.integrations.connectors.solides.connector import SolidesConnector

        api_token = os.getenv("SOLIDES_API_TOKEN")
        if not api_token:
            return {"status": "error", "message": "Token não configurado"}

        connector = SolidesConnector(
            account_id=uuid4(),
            tenant_id=UUID(condominio_id) if condominio_id else uuid4(),
            config={},
            credentials={"api_token": api_token},
        )

        await connector.setup()

        try:
            result = await connector.health_check()
            return {
                "status": "healthy" if result.healthy else "unhealthy",
                "latency_ms": result.latency_ms,
                "message": result.message,
                "api": result.details.get("api", "unknown"),
            }
        finally:
            await connector.teardown()

    return run_async(_check())


@shared_task(name="solides.health_check_all")
def check_all_solides_health():
    """
    Task para verificar saúde de TODAS as integrações ativas.
    """
    logger.info("[Solides Task] Health check de todas integrações")

    # Executa um único health check global
    result = check_solides_health.delay()

    return {"condominios_checked": 1, "task_id": str(result.id)}


# ==================== WEBHOOK PROCESSING ====================


@shared_task(name="solides.process_webhook_queue")
def process_webhooks():
    """
    Task para processar webhooks enfileirados.
    """
    logger.debug("[Solides Task] Processando webhooks")

    # Placeholder - implementar quando webhooks forem configurados
    return {"processed": 0, "message": "Nenhum webhook na fila"}


@shared_task(name="solides.retry_failed_webhooks")
def retry_failed_webhooks():
    """
    Task para reprocessar webhooks que falharam.
    """
    logger.info("[Solides Task] Reprocessando webhooks com falha")

    # Placeholder - implementar quando webhooks forem configurados
    return {"retried": 0, "message": "Nenhum webhook com falha"}


# ==================== CLEANUP TASKS ====================


@shared_task(name="solides.cleanup_old_logs")
def cleanup_old_sync_logs(days: int = 30):
    """
    Task para limpar logs antigos de sincronização.
    """
    logger.info(f"[Solides Task] Limpando logs mais antigos que {days} dias")

    # Placeholder - implementar com banco de dados
    return {"deleted_logs": 0, "message": f"Cleanup de logs > {days} dias"}


@shared_task(name="solides.cleanup_old_webhooks")
def cleanup_old_webhook_logs(days: int = 7):
    """
    Task para limpar logs antigos de webhooks.
    """
    logger.info(f"[Solides Task] Limpando webhooks mais antigos que {days} dias")

    # Placeholder - implementar com banco de dados
    return {"deleted_webhooks": 0, "message": f"Cleanup de webhooks > {days} dias"}


# ==================== HELPER FUNCTIONS ====================


def schedule_full_sync(condominio_id: str = None, delay_seconds: int = 0):
    """
    Agenda full sync para um condomínio.
    """
    return sync_solides_full.apply_async(
        args=[condominio_id], kwargs={"triggered_by": "manual"}, countdown=delay_seconds, queue="integrations"
    )


def schedule_incremental_sync(condominio_id: str = None):
    """
    Agenda sync incremental para um condomínio.
    """
    return sync_solides_incremental.apply_async(args=[condominio_id], queue="integrations")


def schedule_entity_sync(condominio_id: str, entity_type: str, solides_id: str):
    """
    Agenda sync de uma entidade específica.
    """
    return sync_single_entity.apply_async(args=[condominio_id, entity_type, solides_id], queue="integrations")
