"""
Tasks Celery de pipeline de analise e monitoramento de disputas.
================================================================

Tasks:
- processar_pipeline_edital: Pipeline completo ANALYST->ASSESSOR->PRICER
- monitorar_disputa_sessao: Monitora sessao de disputa em tempo real
- verificar_resultado_licitacao: Verifica resultado de licitacao apos encerramento
- preparar_recursos_impugnacao: Prepara analise para recursos/impugnacoes
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
# Task: Pipeline completo de analise de edital
# ──────────────────────────────────────────────


@shared_task(
    bind=True,
    name="bidding.processar_pipeline_edital",
    queue="gov.batch",
    max_retries=2,
    default_retry_delay=120,
    soft_time_limit=600,
    time_limit=900,
)
def processar_pipeline_edital(
    self,
    tender_id: str | None = None,
    edital_text: str | None = None,
    numero_edital: str | None = None,
    orgao: str | None = None,
    uf: str | None = "AM",
):
    """
    Executa pipeline completo de analise de edital: ANALYST -> ASSESSOR -> PRICER.

    Persiste resultados em bidding_analyses, bidding_assessments, bidding_pricing.

    Args:
        tender_id: ID do tender (se ja existe no banco).
        edital_text: Texto do edital para analise.
        numero_edital: Numero do edital.
        orgao: Nome do orgao licitante.
        uf: UF do orgao.

    Returns:
        Dict com resumo do pipeline.
    """
    from core.database.session import get_sync_db

    if not edital_text and not tender_id:
        raise ValueError("edital_text ou tender_id e obrigatorio")

    logger.info(f"[BIDDING] Iniciando pipeline edital: tender_id={tender_id}, numero={numero_edital}")

    pipeline_result = {
        "tender_id": tender_id,
        "numero_edital": numero_edital,
        "steps": {},
        "status": "running",
    }

    try:
        # ── Step 1: ANALYST ──
        logger.info("[BIDDING] Pipeline step 1/3: ANALYST")
        analysis_result = run_async(
            _executar_analyst(
                edital_text=edital_text,
                numero_edital=numero_edital,
                orgao=orgao,
                uf=uf,
            )
        )

        # Persistir analise
        analysis_id = None
        with get_sync_db() as db:
            from modules.bidding.models.analysis import BiddingAnalysis

            analysis_record = BiddingAnalysis(
                id=uuid.uuid4(),
                tender_id=uuid.UUID(tender_id) if tender_id else None,
                objeto_resumido=analysis_result.get("objeto_resumido"),
                modalidade_identificada=analysis_result.get("modalidade"),
                criterio_julgamento=analysis_result.get("criterio_julgamento"),
                requisitos_habilitacao=analysis_result.get("requisitos_habilitacao"),
                red_flags=analysis_result.get("red_flags"),
                documentos_necessarios=analysis_result.get("documentos_necessarios"),
                raw_analysis=analysis_result,
            )
            db.add(analysis_record)
            db.flush()
            analysis_id = analysis_record.id

        pipeline_result["steps"]["analyst"] = {
            "status": "success",
            "analysis_id": str(analysis_id),
            "objeto_resumido": analysis_result.get("objeto_resumido", "")[:200],
            "red_flags_count": len(analysis_result.get("red_flags", [])),
            "confianca": analysis_result.get("confianca_analise", 0),
        }

        # ── Step 2: ASSESSOR ──
        logger.info("[BIDDING] Pipeline step 2/3: ASSESSOR")
        assessment_result = run_async(_executar_assessor(analysis=analysis_result))

        # Persistir avaliacao
        assessment_id = None
        with get_sync_db() as db:
            from modules.bidding.models.assessment import BiddingAssessment

            assessment_record = BiddingAssessment(
                id=uuid.uuid4(),
                tender_id=uuid.UUID(tender_id) if tender_id else None,
                analysis_id=analysis_id,
                score=assessment_result.get("score"),
                recomendacao=assessment_result.get("recomendacao"),
                justificativa=assessment_result.get("justificativa"),
                requisitos_nao_atendidos=assessment_result.get("requisitos_faltantes"),
                acoes_necessarias=assessment_result.get("mitigacoes_sugeridas"),
                raw_assessment=assessment_result,
            )
            db.add(assessment_record)
            db.flush()
            assessment_id = assessment_record.id

        pipeline_result["steps"]["assessor"] = {
            "status": "success",
            "assessment_id": str(assessment_id),
            "score": assessment_result.get("score", 0),
            "recomendacao": assessment_result.get("recomendacao"),
        }

        # ── Step 3: PRICER ──
        logger.info("[BIDDING] Pipeline step 3/3: PRICER")
        pricing_result = run_async(_executar_pricer(analysis=analysis_result))

        # Persistir precificacao
        pricing_id = None
        with get_sync_db() as db:
            from modules.bidding.models.pricing import BiddingPricing

            # Extrair cenario moderado como principal
            cenarios = pricing_result.get("cenarios", [])
            cenario_moderado = next(
                (c for c in cenarios if c.get("tipo") == "moderado"),
                cenarios[0] if cenarios else {},
            )

            pricing_record = BiddingPricing(
                id=uuid.uuid4(),
                tender_id=uuid.UUID(tender_id) if tender_id else None,
                assessment_id=assessment_id,
                custos_diretos=cenario_moderado.get("custo_total_direto"),
                custos_indiretos=cenario_moderado.get("custos_indiretos"),
                impostos=cenario_moderado.get("total_impostos"),
                valor_total=cenario_moderado.get("preco_mensal"),
                cenario="moderado",
                cenarios_completos=cenarios,
                regime_tributario=pricing_result.get("regime_tributario"),
                bdi_percentual=float(cenario_moderado.get("bdi_percentual", 0)),
                raw_pricing=pricing_result,
            )
            db.add(pricing_record)
            db.flush()
            pricing_id = pricing_record.id

        pipeline_result["steps"]["pricer"] = {
            "status": "success",
            "pricing_id": str(pricing_id),
            "preco_mensal_moderado": str(cenario_moderado.get("preco_mensal", 0)),
            "cenarios_count": len(cenarios),
        }

        # ── Resultado final ──
        pipeline_result["status"] = "completed"
        pipeline_result["recomendacao"] = assessment_result.get("recomendacao")
        pipeline_result["score"] = assessment_result.get("score", 0)

        # Atualizar recomendacao na analise
        with get_sync_db() as db:
            from modules.bidding.models.analysis import BiddingAnalysis

            analysis_record = db.get(BiddingAnalysis, analysis_id)
            if analysis_record:
                analysis_record.recomendacao_participacao = assessment_result.get("recomendacao")

        logger.info(
            f"[BIDDING] Pipeline concluido: "
            f"recomendacao={pipeline_result['recomendacao']}, "
            f"score={pipeline_result['score']}"
        )

        return pipeline_result

    except Exception as e:
        logger.error(f"[BIDDING] Erro no pipeline de edital: {e}")
        pipeline_result["status"] = "failed"
        pipeline_result["error"] = str(e)[:500]
        raise self.retry(exc=e)


async def _executar_analyst(
    edital_text: str,
    numero_edital: str | None = None,
    orgao: str | None = None,
    uf: str | None = None,
) -> dict:
    """Executa AnalystAgent para analise do edital."""
    from modules.bidding.agents.analyst_agent import AnalystAgent

    agent = AnalystAgent()
    return await agent.execute(
        edital_text=edital_text,
        numero_edital=numero_edital,
        orgao=orgao,
        uf=uf,
    )


async def _executar_assessor(analysis: dict) -> dict:
    """Executa AssessorAgent para avaliacao Go/No-Go."""
    from modules.bidding.agents.assessor_agent import AssessorAgent

    agent = AssessorAgent()
    return await agent.execute(analysis=analysis)


async def _executar_pricer(analysis: dict) -> dict:
    """Executa PricerAgent para precificacao."""
    from modules.bidding.agents.pricer_agent import PricerAgent

    agent = PricerAgent()
    return await agent.execute(analysis=analysis)


# ──────────────────────────────────────────────
# Task: Monitorar sessao de disputa em tempo real
# ──────────────────────────────────────────────


@shared_task(
    bind=True,
    name="bidding.monitorar_disputa_sessao",
    queue="gov.batch",
    max_retries=5,
    default_retry_delay=30,
    soft_time_limit=1800,
    time_limit=2400,
)
def monitorar_disputa_sessao(
    self,
    tender_id: str,
    portal: str = "pncp",
    portal_url: str | None = None,
    intervalo_segundos: int = 30,
    max_ciclos: int = 120,
):
    """
    Monitora sessao de disputa de licitacao em tempo real.

    Verifica atualizacoes periodicamente e registra lances,
    classificacao e status da sessao.

    Args:
        tender_id: UUID do tender.
        portal: Portal da licitacao (pncp, comprasnet, etc).
        portal_url: URL da sessao no portal.
        intervalo_segundos: Intervalo entre verificacoes.
        max_ciclos: Maximo de ciclos de verificacao.

    Returns:
        Dict: {status, lances_registrados, resultado_final}
    """
    import time

    from core.database.session import get_sync_db

    logger.info(f"[BIDDING] Iniciando monitoramento disputa: tender_id={tender_id}, portal={portal}")

    lances_registrados = 0
    ciclo_atual = 0
    status_final = "timeout"

    try:
        while ciclo_atual < max_ciclos:
            ciclo_atual += 1

            # Verificar status da sessao
            sessao_data = run_async(
                _verificar_sessao_disputa(
                    tender_id=tender_id,
                    portal=portal,
                    portal_url=portal_url,
                )
            )

            if not sessao_data:
                logger.warning(f"[BIDDING] Sem dados da sessao no ciclo {ciclo_atual}")
                time.sleep(intervalo_segundos)
                continue

            # Registrar novos lances
            novos_lances = sessao_data.get("novos_lances", [])
            if novos_lances:
                with get_sync_db() as db:
                    from sqlalchemy import text

                    for lance in novos_lances:
                        db.execute(
                            text("""
                                INSERT INTO bidding_dispute_logs (id, tender_id, tipo, dados, created_at)
                                VALUES (:id, :tender_id, :tipo, :dados, :created_at)
                                ON CONFLICT DO NOTHING
                            """),
                            {
                                "id": str(uuid.uuid4()),
                                "tender_id": tender_id,
                                "tipo": "lance",
                                "dados": str(lance),
                                "created_at": datetime.utcnow(),
                            },
                        )
                        lances_registrados += 1

            # Verificar se sessao encerrou
            status_sessao = sessao_data.get("status")
            if status_sessao in ("encerrada", "suspensa", "deserta", "fracassada"):
                status_final = status_sessao
                logger.info(f"[BIDDING] Sessao encerrada: {status_final}")
                break

            if ciclo_atual < max_ciclos:
                time.sleep(intervalo_segundos)

        summary = {
            "tender_id": tender_id,
            "status": status_final,
            "ciclos_executados": ciclo_atual,
            "lances_registrados": lances_registrados,
        }

        logger.info(f"[BIDDING] Monitoramento disputa concluido: status={status_final}, lances={lances_registrados}")

        return summary

    except Exception as e:
        logger.error(f"[BIDDING] Erro no monitoramento de disputa: {e}")
        raise self.retry(exc=e)


async def _verificar_sessao_disputa(
    tender_id: str,
    portal: str = "pncp",
    portal_url: str | None = None,
) -> dict | None:
    """Verifica status da sessao de disputa no portal."""
    try:
        from modules.bidding.integrations.pncp.client import PNCPClient

        if portal == "pncp":
            async with PNCPClient() as client:
                return await client.verificar_sessao(tender_id=tender_id)
    except Exception as e:
        logger.warning(f"[BIDDING] Erro ao verificar sessao: {e}")
    return None


# ──────────────────────────────────────────────
# Task: Verificar resultado de licitacao
# ──────────────────────────────────────────────


@shared_task(
    bind=True,
    name="bidding.verificar_resultado_licitacao",
    queue="gov.batch",
    max_retries=3,
    default_retry_delay=600,
    soft_time_limit=300,
    time_limit=600,
)
def verificar_resultado_licitacao(
    self,
    tender_id: str,
    portal: str = "pncp",
):
    """
    Verifica resultado de licitacao apos encerramento da sessao.

    Busca ata de resultado, classificacao final e adjudicacao.

    Args:
        tender_id: UUID do tender.
        portal: Portal da licitacao.

    Returns:
        Dict: {resultado, classificacao, adjudicado, valor_final}
    """
    from core.database.session import get_sync_db

    logger.info(f"[BIDDING] Verificando resultado licitacao: tender_id={tender_id}")

    try:
        resultado = run_async(
            _buscar_resultado_licitacao(
                tender_id=tender_id,
                portal=portal,
            )
        )

        if resultado:
            # Atualizar oportunidade com resultado
            with get_sync_db() as db:
                from sqlalchemy import select

                from modules.bidding.models.opportunity import BiddingOpportunity

                opp = db.execute(
                    select(BiddingOpportunity).where(BiddingOpportunity.id == uuid.UUID(tender_id))
                ).scalar_one_or_none()

                if opp:
                    opp.status = resultado.get("status", "encerrada")
                    opp.updated_at = datetime.utcnow()

        summary = {
            "tender_id": tender_id,
            "resultado": resultado.get("resultado") if resultado else "nao_disponivel",
            "classificacao": resultado.get("classificacao") if resultado else None,
            "adjudicado": resultado.get("adjudicado", False) if resultado else False,
            "valor_final": resultado.get("valor_final") if resultado else None,
        }

        logger.info(f"[BIDDING] Resultado licitacao: {summary['resultado']}")

        return summary

    except Exception as e:
        logger.error(f"[BIDDING] Erro ao verificar resultado: {e}")
        raise self.retry(exc=e)


async def _buscar_resultado_licitacao(tender_id: str, portal: str = "pncp") -> dict | None:
    """Busca resultado da licitacao no portal."""
    try:
        from modules.bidding.integrations.pncp.client import PNCPClient

        if portal == "pncp":
            async with PNCPClient() as client:
                return await client.buscar_resultado(tender_id=tender_id)
    except Exception as e:
        logger.warning(f"[BIDDING] Erro ao buscar resultado: {e}")
    return None


# ──────────────────────────────────────────────
# Task: Preparar recursos e impugnacoes
# ──────────────────────────────────────────────


@shared_task(
    bind=True,
    name="bidding.preparar_recursos_impugnacao",
    queue="gov.batch",
    max_retries=2,
    default_retry_delay=120,
    soft_time_limit=600,
    time_limit=900,
)
def preparar_recursos_impugnacao(
    self,
    tender_id: str,
    tipo: str = "recurso",
    motivo: str | None = None,
    edital_text: str | None = None,
):
    """
    Prepara analise para recursos ou impugnacoes de editais.

    Utiliza AnalystAgent para gerar fundamentacao juridica.

    Args:
        tender_id: UUID do tender.
        tipo: Tipo (recurso ou impugnacao).
        motivo: Motivo/fundamentacao do recurso.
        edital_text: Texto do edital para referencia.

    Returns:
        Dict: {tipo, fundamentacao, prazo, recomendacao}
    """
    logger.info(f"[BIDDING] Preparando {tipo} para tender_id={tender_id}")

    try:
        resultado = run_async(
            _analisar_recurso(
                tender_id=tender_id,
                tipo=tipo,
                motivo=motivo,
                edital_text=edital_text,
            )
        )

        summary = {
            "tender_id": tender_id,
            "tipo": tipo,
            "fundamentacao": resultado.get("fundamentacao", ""),
            "prazo": resultado.get("prazo"),
            "recomendacao": resultado.get("recomendacao", "avaliar"),
            "viabilidade": resultado.get("viabilidade", 0),
        }

        logger.info(
            f"[BIDDING] Analise {tipo} concluida: "
            f"recomendacao={summary['recomendacao']}, viabilidade={summary['viabilidade']}%"
        )

        return summary

    except Exception as e:
        logger.error(f"[BIDDING] Erro ao preparar {tipo}: {e}")
        raise self.retry(exc=e)


async def _analisar_recurso(
    tender_id: str,
    tipo: str = "recurso",
    motivo: str | None = None,
    edital_text: str | None = None,
) -> dict:
    """Analisa viabilidade de recurso/impugnacao."""
    from modules.bidding.agents.analyst_agent import AnalystAgent

    agent = AnalystAgent()

    prompt = f"Analise de {tipo} para licitacao.\nMotivo: {motivo or 'Nao especificado'}"
    if edital_text:
        prompt += f"\n\nTexto do edital (trecho):\n{edital_text[:5000]}"

    return await agent.execute(
        edital_text=prompt,
        numero_edital=tender_id,
    )
