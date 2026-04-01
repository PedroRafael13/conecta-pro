"""
Tasks Celery de notificacoes e monitoramento de certidoes.
==========================================================

Tasks:
- verificar_certidoes_vencimento: Verifica certidoes a cada 6h
- notificar_oportunidade_nova: Despacha notificacao de nova oportunidade
- notificar_prazo_edital: Notifica prazos criticos de editais
- notificar_resultado_pipeline: Envia resultado do pipeline de analise
"""

import asyncio
import logging
import uuid
from datetime import datetime

from celery import shared_task

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────


def run_async(coro):
    """Helper para executar coroutines em tasks Celery."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ──────────────────────────────────────────────
# Task: Verificar certidoes e documentos
# ──────────────────────────────────────────────


@shared_task(
    bind=True,
    name="bidding.verificar_certidoes_vencimento",
    queue="gov.batch",
    max_retries=2,
    default_retry_delay=600,
    soft_time_limit=300,
    time_limit=600,
)
def verificar_certidoes_vencimento(
    self,
    cnpj: str = "35.710.481/0001-03",
    documentos: list[dict] | None = None,
):
    """
    Verifica vencimento de certidoes e documentos usando SentinelAgent.

    Cria notificacoes para documentos vencendo ou vencidos.

    Args:
        cnpj: CNPJ da empresa a verificar.
        documentos: Lista de documentos com datas (override).
                    Cada dict: {"tipo": str, "data_emissao": str, "data_validade": str}

    Returns:
        Dict: {total_checked, alertas_criticos, alertas_urgentes, apto_licitar}
    """
    from core.database.session import get_sync_db

    logger.info(f"[BIDDING] Verificando certidoes para CNPJ {cnpj}")

    try:
        # Executar SentinelAgent (async)
        result = run_async(_verificar_certidoes(cnpj=cnpj, documentos=documentos))

        alertas_criticos = len(result.get("alertas_criticos", []))
        alertas_urgentes = len(result.get("alertas_urgentes", []))
        alertas_atencao = len(result.get("alertas_atencao", []))

        # Persistir notificacoes no banco para alertas criticos e urgentes
        if alertas_criticos > 0 or alertas_urgentes > 0:
            with get_sync_db() as db:
                from sqlalchemy import text

                # Inserir notificacoes para alertas criticos
                for alerta in result.get("alertas_criticos", []):
                    db.execute(
                        text("""
                            INSERT INTO notifications (id, title, message, type, priority, created_at)
                            VALUES (:id, :title, :message, :type, :priority, :created_at)
                            ON CONFLICT DO NOTHING
                        """),
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Certidao CRITICA - Licitacoes",
                            "message": alerta,
                            "type": "bidding_certidao",
                            "priority": "critical",
                            "created_at": datetime.utcnow(),
                        },
                    )

                # Inserir notificacoes para alertas urgentes
                for alerta in result.get("alertas_urgentes", []):
                    db.execute(
                        text("""
                            INSERT INTO notifications (id, title, message, type, priority, created_at)
                            VALUES (:id, :title, :message, :type, :priority, :created_at)
                            ON CONFLICT DO NOTHING
                        """),
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Certidao URGENTE - Licitacoes",
                            "message": alerta,
                            "type": "bidding_certidao",
                            "priority": "high",
                            "created_at": datetime.utcnow(),
                        },
                    )

        summary = {
            "total_checked": result.get("total_documentos", 0),
            "alertas_criticos": alertas_criticos,
            "alertas_urgentes": alertas_urgentes,
            "alertas_atencao": alertas_atencao,
            "apto_licitar": result.get("apto_licitar", False),
            "cnpj": cnpj,
        }

        logger.info(
            f"[BIDDING] Verificacao certidoes concluida: "
            f"{summary['total_checked']} verificados, "
            f"{alertas_criticos} criticos, "
            f"{alertas_urgentes} urgentes, "
            f"apto={summary['apto_licitar']}"
        )

        return summary

    except Exception as e:
        logger.error(f"[BIDDING] Erro na verificacao de certidoes: {e}")
        raise self.retry(exc=e)


async def _verificar_certidoes(
    cnpj: str = "35.710.481/0001-03",
    documentos: list[dict] | None = None,
) -> dict:
    """Executa SentinelAgent para verificar certidoes."""
    from modules.bidding.agents.sentinel_agent import SentinelAgent

    agent = SentinelAgent()
    return await agent.execute(documentos=documentos, cnpj=cnpj)


# ──────────────────────────────────────────────
# Task: Notificar nova oportunidade encontrada
# ──────────────────────────────────────────────


@shared_task(
    bind=True,
    name="bidding.notificar_oportunidade_nova",
    queue="gov.batch",
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=120,
    time_limit=180,
)
def notificar_oportunidade_nova(
    self,
    opportunity_id: str,
    objeto: str,
    valor_estimado: float | None = None,
    orgao_nome: str | None = None,
    relevancia_score: float = 0,
):
    """
    Despacha notificacao de nova oportunidade de licitacao encontrada.

    Args:
        opportunity_id: UUID da oportunidade.
        objeto: Descricao do objeto licitado.
        valor_estimado: Valor estimado da licitacao.
        orgao_nome: Nome do orgao licitante.
        relevancia_score: Score de relevancia (0-100).

    Returns:
        Dict: {notified, channels}
    """
    from core.database.session import get_sync_db

    logger.info(f"[BIDDING] Notificando nova oportunidade: {opportunity_id}")

    try:
        priority = "high" if relevancia_score >= 80 else "normal" if relevancia_score >= 50 else "low"

        valor_fmt = f"R$ {valor_estimado:,.2f}" if valor_estimado else "Nao informado"

        message = (
            f"Nova oportunidade de licitacao encontrada!\n"
            f"Orgao: {orgao_nome or 'Nao informado'}\n"
            f"Objeto: {objeto[:200]}\n"
            f"Valor estimado: {valor_fmt}\n"
            f"Relevancia: {relevancia_score:.0f}%"
        )

        with get_sync_db() as db:
            from sqlalchemy import text

            db.execute(
                text("""
                    INSERT INTO notifications (id, title, message, type, priority, created_at)
                    VALUES (:id, :title, :message, :type, :priority, :created_at)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "id": str(uuid.uuid4()),
                    "title": "Nova Oportunidade de Licitacao",
                    "message": message,
                    "type": "bidding_oportunidade",
                    "priority": priority,
                    "created_at": datetime.utcnow(),
                },
            )

        logger.info(f"[BIDDING] Notificacao enviada: oportunidade {opportunity_id}, prioridade={priority}")

        return {
            "notified": True,
            "channels": ["database"],
            "priority": priority,
            "opportunity_id": opportunity_id,
        }

    except Exception as e:
        logger.error(f"[BIDDING] Erro ao notificar oportunidade: {e}")
        raise self.retry(exc=e)


# ──────────────────────────────────────────────
# Task: Notificar prazo critico de edital
# ──────────────────────────────────────────────


@shared_task(
    bind=True,
    name="bidding.notificar_prazo_edital",
    queue="gov.batch",
    max_retries=2,
    default_retry_delay=60,
    soft_time_limit=120,
    time_limit=180,
)
def notificar_prazo_edital(
    self,
    tender_id: str,
    numero_edital: str,
    data_abertura: str,
    dias_restantes: int,
):
    """
    Notifica prazos criticos de editais em andamento.

    Args:
        tender_id: UUID do tender.
        numero_edital: Numero do edital.
        data_abertura: Data de abertura ISO format.
        dias_restantes: Dias restantes ate a abertura.

    Returns:
        Dict: {notified, priority}
    """
    from core.database.session import get_sync_db

    logger.info(f"[BIDDING] Notificando prazo edital {numero_edital}: {dias_restantes} dias restantes")

    try:
        if dias_restantes <= 1:
            priority = "critical"
            title = "URGENTE: Edital abre AMANHA!"
        elif dias_restantes <= 3:
            priority = "high"
            title = f"Edital abre em {dias_restantes} dias"
        elif dias_restantes <= 7:
            priority = "normal"
            title = f"Edital abre em {dias_restantes} dias"
        else:
            priority = "low"
            title = f"Lembrete: edital abre em {dias_restantes} dias"

        message = f"Edital: {numero_edital}\nData de abertura: {data_abertura}\nDias restantes: {dias_restantes}"

        with get_sync_db() as db:
            from sqlalchemy import text

            db.execute(
                text("""
                    INSERT INTO notifications (id, title, message, type, priority, created_at)
                    VALUES (:id, :title, :message, :type, :priority, :created_at)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "message": message,
                    "type": "bidding_prazo",
                    "priority": priority,
                    "created_at": datetime.utcnow(),
                },
            )

        logger.info(f"[BIDDING] Notificacao prazo enviada: {numero_edital}, prioridade={priority}")

        return {
            "notified": True,
            "priority": priority,
            "tender_id": tender_id,
            "dias_restantes": dias_restantes,
        }

    except Exception as e:
        logger.error(f"[BIDDING] Erro ao notificar prazo edital: {e}")
        raise self.retry(exc=e)


# ──────────────────────────────────────────────
# Task: Notificar resultado do pipeline de analise
# ──────────────────────────────────────────────


@shared_task(
    bind=True,
    name="bidding.notificar_resultado_pipeline",
    queue="gov.batch",
    max_retries=2,
    default_retry_delay=60,
    soft_time_limit=120,
    time_limit=180,
)
def notificar_resultado_pipeline(
    self,
    tender_id: str | None = None,
    numero_edital: str | None = None,
    recomendacao: str | None = None,
    score: float = 0,
    preco_mensal: float | None = None,
):
    """
    Envia notificacao com resultado do pipeline de analise.

    Args:
        tender_id: UUID do tender.
        numero_edital: Numero do edital.
        recomendacao: Recomendacao (PARTICIPAR/NAO_PARTICIPAR/AVALIAR).
        score: Score de viabilidade.
        preco_mensal: Preco mensal estimado.

    Returns:
        Dict: {notified, priority}
    """
    from core.database.session import get_sync_db

    logger.info(f"[BIDDING] Notificando resultado pipeline: edital={numero_edital}, rec={recomendacao}")

    try:
        if recomendacao == "PARTICIPAR" and score >= 70:
            priority = "high"
            title = f"RECOMENDADO: Participar edital {numero_edital or 'N/I'}"
        elif recomendacao == "NAO_PARTICIPAR":
            priority = "normal"
            title = f"NAO recomendado: Edital {numero_edital or 'N/I'}"
        else:
            priority = "normal"
            title = f"Analise concluida: Edital {numero_edital or 'N/I'}"

        preco_fmt = f"R$ {preco_mensal:,.2f}" if preco_mensal else "Nao calculado"

        message = (
            f"Pipeline de analise concluido!\n"
            f"Edital: {numero_edital or 'N/I'}\n"
            f"Recomendacao: {recomendacao or 'N/I'}\n"
            f"Score: {score:.0f}/100\n"
            f"Preco mensal estimado: {preco_fmt}"
        )

        with get_sync_db() as db:
            from sqlalchemy import text

            db.execute(
                text("""
                    INSERT INTO notifications (id, title, message, type, priority, created_at)
                    VALUES (:id, :title, :message, :type, :priority, :created_at)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "message": message,
                    "type": "bidding_pipeline",
                    "priority": priority,
                    "created_at": datetime.utcnow(),
                },
            )

        logger.info(f"[BIDDING] Notificacao resultado pipeline enviada: {numero_edital}")

        return {
            "notified": True,
            "priority": priority,
            "tender_id": tender_id,
            "recomendacao": recomendacao,
        }

    except Exception as e:
        logger.error(f"[BIDDING] Erro ao notificar resultado pipeline: {e}")
        raise self.retry(exc=e)
