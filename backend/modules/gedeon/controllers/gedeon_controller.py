"""
API do GEDEON — endpoints para o frontend consultar
o contexto acumulado antes de montar um kit.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db
from modules.gedeon.agents.argos import argos
from modules.gedeon.agents.hermes import hermes
from modules.gedeon.agents.kronos import kronos
from modules.gedeon.context.gedeon_context import gedeon_context

router = APIRouter(prefix="/gedeon", tags=["GEDEON"])


@router.get("/context/{cliente_id}/{competencia}")
async def get_context(
    cliente_id: str,
    competencia: str,
    current_user=Depends(get_current_user),
):
    """
    Retorna o contexto acumulado pelo GEDEON para
    um cliente em uma competência específica.
    Usado para pré-preencher o checklist de montagem.
    """
    ctx = await gedeon_context.get(cliente_id, competencia)
    return {
        "cliente_id": ctx["cliente_id"],
        "competencia": ctx["competencia"],
        "score_prontidao": ctx["score_prontidao"],
        "movimentacao_pessoal": ctx["movimentacao_pessoal"],
        "ocorrencias": ctx["ocorrencias"],
        "certidoes": ctx["certidoes"],
        "documentos_gerados": ctx["documentos_gerados"],
        "pendencias": ctx["pendencias"],
        "tipo_kit": ctx["tipo_kit"],
        "ultima_atualizacao": ctx["ultima_atualizacao"],
        "checklist_pre_preenchido": _gerar_checklist(ctx),
    }


@router.get("/dashboard")
async def dashboard(
    current_user=Depends(get_current_user),
):
    """
    Visão geral de todos os clientes para o mês atual.
    Mostra quais kits estão prontos e quais têm pendências.
    """
    competencia = datetime.utcnow().strftime("%Y-%m")
    contexts = await gedeon_context.get_all_clients_context(competencia)
    return {
        "competencia": competencia,
        "total_clientes": len(contexts),
        "prontos": sum(1 for c in contexts if c["score_prontidao"] >= 90),
        "com_pendencias": sum(1 for c in contexts if 0 < c["score_prontidao"] < 90),
        "criticos": sum(1 for c in contexts if c["score_prontidao"] == 0),
        "clientes": contexts,
    }


# ── KRONOS — Alertas de Vencimento ───────────────────────────────────────────


@router.get("/alertas/vencimentos")
async def alertas_vencimentos(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    KRONOS: retorna alertas de vencimento de certidões e ASOs.
    """
    certidoes = await kronos.verificar_certidoes(db=db)
    asos = await kronos.verificar_asos_funcionarios(db=db)

    criticos = [c for c in certidoes if c["nivel"] == "critico"]
    criticos += [a for a in asos if a["nivel"] == "critico"]

    return {
        "certidoes": certidoes,
        "asos": asos,
        "resumo": {
            "total_certidoes": len(certidoes),
            "total_asos": len(asos),
            "criticos": len(criticos),
            "alerta_geral": "critico"
            if criticos
            else ("alto" if any(x["nivel"] == "alto" for x in certidoes + asos) else "ok"),
        },
    }


# ── ARGOS — Conformidade de Kit ───────────────────────────────────────────────


@router.get("/conformidade/{cliente_id}/{competencia}")
async def verificar_conformidade(
    cliente_id: str,
    competencia: str,
    current_user=Depends(get_current_user),
):
    """
    ARGOS: verifica conformidade do kit para um cliente/competência.
    Retorna score 0-100 e lista de documentos faltando.
    """
    ctx = await gedeon_context.get(cliente_id, competencia)
    documentos_presentes = [d["tipo"] for d in ctx.get("documentos_gerados", [])]
    movimentacoes = ctx.get("movimentacao_pessoal", [])
    certidoes_status = ctx.get("certidoes", {})
    tipo_kit = ctx.get("tipo_kit", "maos_de_obra")

    resultado = argos.verificar_conformidade(
        tipo_kit=tipo_kit,
        documentos_presentes=documentos_presentes,
        movimentacoes=movimentacoes,
        certidoes_status=certidoes_status,
    )

    return {
        "cliente_id": cliente_id,
        "competencia": competencia,
        "tipo_kit": tipo_kit,
        **resultado,
    }


# ── HERMES — Classificação de Documento ──────────────────────────────────────


@router.post("/hermes/classificar")
async def classificar_documento(
    nome_arquivo: str = Query(..., description="Nome do arquivo a classificar"),
    conteudo_preview: str = Query("", description="Trecho do conteúdo (opcional)"),
    current_user=Depends(get_current_user),
):
    """
    HERMES: classifica automaticamente um documento pelo nome/preview.
    """
    resultado = hermes.classificar_documento(nome_arquivo, conteudo_preview)
    return {
        "nome_arquivo": nome_arquivo,
        **resultado,
    }


def _gerar_checklist(ctx: dict) -> dict:
    """
    Gerar checklist pré-preenchido com base no contexto.
    Retorna o que GEDEON já sabe vs o que precisa confirmar.
    """
    return {
        "movimentacao": {
            "pre_preenchido": ctx["movimentacao_pessoal"],
            "confirmado": len(ctx["movimentacao_pessoal"]) > 0,
            "requer_input": True,
        },
        "certidoes": {
            "status": ctx["certidoes"],
            "critico": ctx["certidoes"].get("critico", 0) > 0,
            "confirmado": ctx["certidoes"].get("critico", 0) == 0,
        },
        "documentos": {
            "gerados": ctx["documentos_gerados"],
            "confirmado": bool(ctx["documentos_gerados"]),
        },
        "pendencias": {
            "itens": ctx["pendencias"],
            "tem_pendencias": len(ctx["pendencias"]) > 0,
            "requer_decisao": any(p.get("requer_decisao") for p in ctx["pendencias"]),
        },
        "score_geral": ctx["score_prontidao"],
    }
