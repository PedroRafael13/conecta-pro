"""
Tasks Celery para sincronizacao automatica com PNCP e pipeline de licitacoes.
==============================================================================

Tasks:
- sync_pncp_oportunidades: Busca oportunidades no PNCP a cada 2h
- sync_pncp_precos: Busca precos de referencia diariamente
- verificar_certidoes_vencimento: Verifica certidoes a cada 6h
- processar_pipeline_edital: Pipeline completo ANALYST->ASSESSOR->PRICER
"""

import asyncio
import logging
import uuid
from datetime import date, datetime, timedelta

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
# Keywords de busca para seguranca patrimonial
# ──────────────────────────────────────────────

SECURITY_KEYWORDS = [
    "vigilancia",
    "seguranca patrimonial",
    "seguranca eletronica",
    "portaria",
    "monitoramento",
    "cftv",
    "alarme",
    "controle de acesso",
    "vigilancia armada",
    "vigilancia desarmada",
    "seguranca privada",
]


# ──────────────────────────────────────────────
# Task 1: Sync oportunidades PNCP
# ──────────────────────────────────────────────


@shared_task(
    bind=True,
    name="bidding.sync_pncp_oportunidades",
    queue="gov.batch",
    max_retries=3,
    default_retry_delay=300,
    soft_time_limit=600,
    time_limit=900,
)
def sync_pncp_oportunidades(
    self,
    uf: str = "AM",
    dias: int = 30,
    max_paginas: int = 5,
):
    """
    Busca oportunidades de licitacao no PNCP para seguranca/vigilancia.

    Args:
        uf: UF para filtrar busca (default: AM).
        dias: Dias para tras a buscar (default: 30).
        max_paginas: Maximo de paginas por busca (default: 5).

    Returns:
        Dict com resumo: {total_found, new, updated, errors}
    """
    from core.database.session import get_sync_db

    logger.info(f"[BIDDING] Iniciando sync PNCP oportunidades: UF={uf}, dias={dias}")

    # Criar registro de sync job
    sync_job_id = None
    with get_sync_db() as db:
        from modules.bidding.models.sync_job import BiddingSyncJob

        sync_job = BiddingSyncJob(
            id=uuid.uuid4(),
            portal="pncp",
            job_type="sync_oportunidades",
            status="running",
            started_at=datetime.utcnow(),
            parameters={"uf": uf, "dias": dias, "max_paginas": max_paginas},
        )
        db.add(sync_job)
        db.flush()
        sync_job_id = sync_job.id

    try:
        # Buscar oportunidades via ScoutAgent (async)
        opportunities = run_async(_buscar_oportunidades_pncp(uf=uf, dias=dias, max_paginas=max_paginas))

        # Persistir resultados no banco
        new_count = 0
        updated_count = 0
        error_count = 0

        with get_sync_db() as db:
            from sqlalchemy import select

            from modules.bidding.models.opportunity import BiddingOpportunity

            for opp in opportunities:
                try:
                    # Verificar se ja existe (portal + portal_id)
                    portal_id = f"{opp['numero_compra']}/{opp['ano_compra']}/{opp['sequencial_compra']}"

                    existing = db.execute(
                        select(BiddingOpportunity).where(
                            BiddingOpportunity.portal == "pncp",
                            BiddingOpportunity.portal_id == portal_id,
                        )
                    ).scalar_one_or_none()

                    if existing:
                        # Atualizar score e datas
                        existing.relevancia_score = opp.get("relevancia_score", 0)
                        existing.valor_estimado = opp.get("valor_estimado")
                        existing.data_abertura = (
                            datetime.fromisoformat(opp["data_abertura"])
                            if opp.get("data_abertura")
                            else existing.data_abertura
                        )
                        existing.data_encerramento = (
                            datetime.fromisoformat(opp["data_encerramento"])
                            if opp.get("data_encerramento")
                            else existing.data_encerramento
                        )
                        existing.updated_at = datetime.utcnow()
                        updated_count += 1
                    else:
                        # Criar novo registro
                        new_opp = BiddingOpportunity(
                            id=uuid.uuid4(),
                            portal="pncp",
                            portal_id=portal_id,
                            objeto=opp.get("objeto", ""),
                            valor_estimado=opp.get("valor_estimado"),
                            modalidade=opp.get("modalidade"),
                            orgao_nome=opp.get("orgao_nome"),
                            orgao_cnpj=opp.get("orgao_cnpj"),
                            uf=opp.get("orgao_uf", uf),
                            data_publicacao=(
                                datetime.fromisoformat(opp["data_publicacao"]) if opp.get("data_publicacao") else None
                            ),
                            data_abertura=(
                                datetime.fromisoformat(opp["data_abertura"]) if opp.get("data_abertura") else None
                            ),
                            data_encerramento=(
                                datetime.fromisoformat(opp["data_encerramento"])
                                if opp.get("data_encerramento")
                                else None
                            ),
                            url_edital=opp.get("link_pncp"),
                            status="nova",
                            relevancia_score=opp.get("relevancia_score", 0),
                        )
                        db.add(new_opp)
                        new_count += 1

                except Exception as e:
                    logger.error(f"[BIDDING] Erro ao persistir oportunidade: {e}")
                    error_count += 1

        # Atualizar sync job com resultado
        with get_sync_db() as db:
            from modules.bidding.models.sync_job import BiddingSyncJob

            job = db.get(BiddingSyncJob, sync_job_id)
            if job:
                job.status = "completed"
                job.finished_at = datetime.utcnow()
                job.records_found = len(opportunities)
                job.records_saved = new_count + updated_count

        summary = {
            "total_found": len(opportunities),
            "new": new_count,
            "updated": updated_count,
            "errors": error_count,
            "uf": uf,
            "sync_job_id": str(sync_job_id),
        }

        logger.info(
            f"[BIDDING] Sync PNCP concluido: "
            f"{summary['total_found']} encontrados, "
            f"{summary['new']} novos, "
            f"{summary['updated']} atualizados, "
            f"{summary['errors']} erros"
        )

        return summary

    except Exception as e:
        logger.error(f"[BIDDING] Erro na sync PNCP oportunidades: {e}")

        # Atualizar sync job com erro
        try:
            with get_sync_db() as db:
                from modules.bidding.models.sync_job import BiddingSyncJob

                job = db.get(BiddingSyncJob, sync_job_id)
                if job:
                    job.status = "failed"
                    job.finished_at = datetime.utcnow()
                    job.error_message = str(e)[:500]
        except Exception:
            logger.error("[BIDDING] Erro ao atualizar sync job com falha")

        raise self.retry(exc=e)


async def _buscar_oportunidades_pncp(
    uf: str = "AM",
    dias: int = 30,
    max_paginas: int = 5,
) -> list[dict]:
    """Executa busca async no PNCP via ScoutAgent."""
    from modules.bidding.agents.scout_agent import ScoutAgent, ScoutSearchParams

    params = ScoutSearchParams(
        keywords=SECURITY_KEYWORDS,
        ufs=[uf],
        data_inicial=date.today() - timedelta(days=dias),
        data_final=date.today(),
        max_paginas=max_paginas,
    )

    agent = ScoutAgent()
    return await agent.execute(search_params=params)


# ──────────────────────────────────────────────
# Task 2: Sync precos de referencia PNCP
# ──────────────────────────────────────────────


@shared_task(
    bind=True,
    name="bidding.sync_pncp_precos",
    queue="gov.batch",
    max_retries=3,
    default_retry_delay=600,
    soft_time_limit=900,
    time_limit=1200,
)
def sync_pncp_precos(
    self,
    uf: str = "AM",
    dias: int = 90,
):
    """
    Busca precos de referencia para servicos de seguranca no PNCP.

    Armazena em bidding_price_history para uso pelo PricerAgent
    na comparacao de precos de mercado.

    Args:
        uf: UF para filtrar busca (default: AM).
        dias: Dias para tras a buscar (default: 90).

    Returns:
        Dict com resumo: {total_found, saved, errors}
    """
    from core.database.session import get_sync_db

    logger.info(f"[BIDDING] Iniciando sync precos PNCP: UF={uf}, dias={dias}")

    # Criar sync job
    sync_job_id = None
    with get_sync_db() as db:
        from modules.bidding.models.sync_job import BiddingSyncJob

        sync_job = BiddingSyncJob(
            id=uuid.uuid4(),
            portal="pncp",
            job_type="sync_precos",
            status="running",
            started_at=datetime.utcnow(),
            parameters={"uf": uf, "dias": dias},
        )
        db.add(sync_job)
        db.flush()
        sync_job_id = sync_job.id

    try:
        # Buscar contratos com precos no PNCP
        price_data = run_async(_buscar_precos_pncp(uf=uf, dias=dias))

        saved_count = 0
        error_count = 0

        with get_sync_db() as db:
            from modules.bidding.models.price_history import BiddingPriceHistory

            for item in price_data:
                try:
                    price_record = BiddingPriceHistory(
                        id=uuid.uuid4(),
                        descricao=item["descricao"],
                        fonte="pncp",
                        valor_unitario=item["valor_unitario"],
                        unidade=item.get("unidade", "mensal"),
                        orgao=item.get("orgao"),
                        data_referencia=item.get("data_referencia"),
                        metadata_extra=item.get("metadata", {}),
                    )
                    db.add(price_record)
                    saved_count += 1

                except Exception as e:
                    logger.error(f"[BIDDING] Erro ao salvar preco: {e}")
                    error_count += 1

        # Atualizar sync job
        with get_sync_db() as db:
            from modules.bidding.models.sync_job import BiddingSyncJob

            job = db.get(BiddingSyncJob, sync_job_id)
            if job:
                job.status = "completed"
                job.finished_at = datetime.utcnow()
                job.records_found = len(price_data)
                job.records_saved = saved_count

        summary = {
            "total_found": len(price_data),
            "saved": saved_count,
            "errors": error_count,
            "uf": uf,
            "sync_job_id": str(sync_job_id),
        }

        logger.info(
            f"[BIDDING] Sync precos PNCP concluido: {summary['total_found']} encontrados, {summary['saved']} salvos"
        )

        return summary

    except Exception as e:
        logger.error(f"[BIDDING] Erro na sync PNCP precos: {e}")

        try:
            with get_sync_db() as db:
                from modules.bidding.models.sync_job import BiddingSyncJob

                job = db.get(BiddingSyncJob, sync_job_id)
                if job:
                    job.status = "failed"
                    job.finished_at = datetime.utcnow()
                    job.error_message = str(e)[:500]
        except Exception:
            logger.error("[BIDDING] Erro ao atualizar sync job com falha")

        raise self.retry(exc=e)


async def _buscar_precos_pncp(uf: str = "AM", dias: int = 90) -> list[dict]:
    """Busca contratos no PNCP e extrai precos de referencia."""
    from modules.bidding.integrations.pncp.client import PNCPClient

    price_data = []

    async with PNCPClient() as client:
        # Buscar contratos de seguranca/vigilancia
        result = await client.buscar_contratos(uf=uf, pagina=1, tamanho_pagina=50)

        if not result.get("sucesso"):
            logger.warning(f"[BIDDING] Falha ao buscar contratos PNCP: {result.get('erro')}")
            return []

        for contrato in result.get("contratos", []):
            objeto = (contrato.objeto if hasattr(contrato, "objeto") else str(contrato)).lower()

            # Filtrar apenas contratos de seguranca
            is_security = any(kw in objeto for kw in SECURITY_KEYWORDS)
            if not is_security:
                continue

            # Extrair dados de preco
            valor = contrato.valor_global or contrato.valor_inicial if hasattr(contrato, "valor_global") else None

            if valor and float(valor) > 0:
                price_data.append(
                    {
                        "descricao": contrato.objeto if hasattr(contrato, "objeto") else str(contrato),
                        "valor_unitario": float(valor),
                        "unidade": "mensal",
                        "orgao": contrato.nome_orgao if hasattr(contrato, "nome_orgao") else None,
                        "data_referencia": (
                            datetime.combine(contrato.data_assinatura, datetime.min.time())
                            if hasattr(contrato, "data_assinatura") and contrato.data_assinatura
                            else datetime.utcnow()
                        ),
                        "metadata": {
                            "numero_contrato": (
                                contrato.numero_contrato if hasattr(contrato, "numero_contrato") else None
                            ),
                            "cnpj_orgao": (contrato.cnpj_orgao if hasattr(contrato, "cnpj_orgao") else None),
                            "cnpj_fornecedor": (
                                contrato.cnpj_fornecedor if hasattr(contrato, "cnpj_fornecedor") else None
                            ),
                            "uf": uf,
                        },
                    }
                )

    logger.info(f"[BIDDING] {len(price_data)} precos de referencia extraidos do PNCP")
    return price_data


# ──────────────────────────────────────────────
# Task 3: Verificar certidoes e documentos
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
# Task 4: Pipeline completo de analise de edital
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
