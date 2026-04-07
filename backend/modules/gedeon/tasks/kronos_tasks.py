"""
Tarefas Celery do KRONOS/THEMIS — execução agendada.
KRONOS: verifica vencimentos às 06h e publica alertas no Event Bus.
THEMIS: verifica assinaturas pendentes a cada 4h.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="gedeon.kronos.verificacao_diaria", bind=True, max_retries=3)
def kronos_verificacao_diaria(self):
    """
    Verifica vencimentos de certidões, ASOs e EPIs diariamente às 06h.
    Publica eventos FIN_INADIMPLENCIA_DETECTADA e SAUDE_ASO_EMITIDO no barramento.
    """
    import asyncio

    try:
        from modules.gedeon.agents.kronos import KronosAgent

        kronos = KronosAgent()
        result = asyncio.run(kronos.executar_verificacao_completa())
        logger.info(
            "KRONOS diário: %d certidões, %d ASOs, %d alertas publicados",
            result.get("certidoes_alerta", 0),
            result.get("asos_alerta", 0),
            result.get("eventos_publicados", 0),
        )
        return result
    except Exception as exc:
        logger.error("KRONOS falhou: %s", exc)
        raise self.retry(exc=exc, countdown=300)


@shared_task(name="gedeon.themis.verificacao_assinaturas", bind=True, max_retries=3)
def themis_verificacao_assinaturas(self):
    """
    Verifica assinaturas GED pendentes e publica alertas a cada 4h.
    Publica GED_ASSINATURA_PENDENTE para contratos vencendo.
    """
    import asyncio

    try:
        from modules.gedeon.agents.themis import ThemisAgent

        themis = ThemisAgent()
        result = asyncio.run(themis.verificar_e_alertar())
        logger.info(
            "THEMIS: %d pendentes, %d críticos",
            result.get("total_pendentes", 0),
            result.get("criticos", 0),
        )
        return result
    except Exception as exc:
        logger.error("THEMIS falhou: %s", exc)
        raise self.retry(exc=exc, countdown=60)


@shared_task(name="gedeon.fiscal.verificar_certidoes", bind=True, max_retries=3)
def fiscal_verificar_certidoes(self):
    """
    Verifica vencimento de certidões fiscais e publica FISCAL_CERTIDAO_VENCIDA.
    Executa diariamente às 07h, complementar ao KRONOS.
    """
    import asyncio

    try:
        from modules.fiscal.publishers import verificar_e_publicar_vencimentos

        async def _run():
            # Busca certidões do GED e verifica vencimentos
            from sqlalchemy import text

            from core.database import get_sync_db

            with get_sync_db() as db:
                rows = db.execute(
                    text(
                        "SELECT id::text, tipo, data_vencimento, client_id::text "
                        "FROM ged_documents "
                        "WHERE document_type IN ('certidao','cnd','cndt','crf') "
                        "AND is_active = true "
                        "AND data_vencimento IS NOT NULL "
                        "AND data_vencimento <= CURRENT_DATE + interval '30 days' "
                        "ORDER BY data_vencimento ASC LIMIT 200"
                    )
                ).fetchall()

            certidoes = [
                {
                    "id": r[0],
                    "tipo": r[1],
                    "data_vencimento": str(r[2]),
                    "cliente_id": r[3],
                }
                for r in rows
            ]
            publicadas = await verificar_e_publicar_vencimentos(certidoes)
            return {"total_verificadas": len(certidoes), "eventos_publicados": publicadas}

        result = asyncio.run(_run())
        logger.info("Fiscal certidões: %s", result)
        return result
    except Exception as exc:
        logger.error("fiscal_verificar_certidoes falhou: %s", exc)
        raise self.retry(exc=exc, countdown=300)
