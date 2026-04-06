"""
API do GEDEON — endpoints para o frontend consultar
o contexto acumulado antes de montar um kit.
"""

from datetime import datetime

from fastapi import APIRouter, Depends

from core.auth.dependencies import get_current_user
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
