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


@shared_task(name="gedeon.verificar_kits_completos", bind=True, max_retries=3)
def verificar_kits_completos(self):
    """
    Verifica kits GED com completion_percentage=100% e sent_at IS NULL.
    Para cada kit completo não enviado sem notificação nas últimas 24h,
    cria alerta interno para Jordan conferir e aprovar o envio.
    NÃO envia email nem WhatsApp — apenas notificação in_app.
    Idempotente: não recria notificação se já existe uma nas últimas 24h
    para o mesmo kit (reference_id + reference_type = ged_kit_completo).
    Agendado diariamente às 08:00 Manaus (12:00 UTC).
    """
    try:
        from sqlalchemy import text

        from core.database import get_sync_db

        with get_sync_db() as db:
            user_row = db.execute(
                text("SELECT id FROM users WHERE email = 'jjesus@conectamais.pro' LIMIT 1")
            ).fetchone()
            if not user_row:
                logger.warning("verificar_kits_completos: jjesus@conectamais.pro não encontrado")
                return {"kits_alertados": 0, "erro": "usuario_nao_encontrado"}
            user_id = user_row[0]

            tenant_row = db.execute(text("SELECT id FROM tenants LIMIT 1")).fetchone()
            if not tenant_row:
                logger.warning("verificar_kits_completos: nenhum tenant encontrado")
                return {"kits_alertados": 0, "erro": "tenant_nao_encontrado"}
            tenant_id = tenant_row[0]

            kits = db.execute(
                text("""
                    SELECT k.id, k.reference_month, gc.name AS cliente
                    FROM ged_document_kits k
                    LEFT JOIN ged_clients gc ON gc.id = k.client_id
                    WHERE k.completion_percentage = 100
                      AND k.sent_at IS NULL
                      AND NOT EXISTS (
                          SELECT 1 FROM communication_notifications cn
                          WHERE cn.reference_id = k.id
                            AND cn.reference_type = 'ged_kit_completo'
                            AND cn.created_at > NOW() - INTERVAL '24 hours'
                      )
                """)
            ).fetchall()

            alertados = 0
            for kit in kits:
                kit_id = kit[0]
                reference_month = kit[1]
                cliente = kit[2] or "Cliente"
                mes_ano = reference_month.strftime("%m/%Y") if reference_month else "—"

                db.execute(
                    text("""
                        INSERT INTO communication_notifications
                          (tenant_id, user_id, title, body, type,
                           reference_type, reference_id, action_url,
                           channels, extra_data)
                        VALUES (
                          :tenant_id, :user_id, :title, :body, 'kit_completo',
                          'ged_kit_completo', :reference_id,
                          :action_url,
                          '["in_app"]'::jsonb,
                          '{}'::jsonb
                        )
                    """),
                    {
                        "tenant_id": str(tenant_id),
                        "user_id": str(user_id),
                        "title": f"Kit Completo — {cliente} ({mes_ano})",
                        "body": (
                            f"O kit documental de {cliente} referente a {mes_ano} "
                            f"está 100% completo e aguarda envio. "
                            f"Acesse o GED para conferir os documentos e enviar ao cliente."
                        ),
                        "reference_id": str(kit_id),
                        "action_url": f"/ged/kits/{kit_id}",
                    },
                )
                alertados += 1
                logger.info("Kit completo alertado: %s — %s (%s)", kit_id, cliente, mes_ano)

            db.commit()

        logger.info("verificar_kits_completos: %d kits alertados", alertados)
        return {"kits_alertados": alertados}

    except Exception as exc:
        logger.error("verificar_kits_completos falhou: %s", exc)
        raise self.retry(exc=exc, countdown=300)
