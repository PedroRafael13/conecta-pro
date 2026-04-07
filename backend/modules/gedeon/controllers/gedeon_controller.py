"""
API do GEDEON — endpoints para o frontend consultar
o contexto acumulado antes de montar um kit.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text as sa_text
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


@router.get("/context/{cliente_id}/{competencia}/tipo2")
async def context_tipo2(
    cliente_id: str,
    competencia: str,
    current_user=Depends(get_current_user),
):
    ctx = await gedeon_context.get(cliente_id, competencia)
    docs = ctx.get("documentos_gerados", {})
    nfse_ok = bool(docs.get("nfs_e"))
    boleto_ok = bool(docs.get("boleto"))
    score = (50 if nfse_ok else 0) + (50 if boleto_ok else 0)
    pendencias = []
    if not nfse_ok:
        pendencias.append("NFS-e nao emitida")
    if not boleto_ok:
        pendencias.append("Boleto nao gerado")
    return {
        "cliente_id": cliente_id,
        "competencia": competencia,
        "tipo_kit": "seguranca_eletronica",
        "score_prontidao": score,
        "checklist": {
            "nfs_e": {"ok": nfse_ok, "obrigatorio": True, "dados": docs.get("nfs_e")},
            "boleto": {"ok": boleto_ok, "obrigatorio": True, "dados": docs.get("boleto")},
        },
        "pode_enviar": nfse_ok and boleto_ok,
        "pendencias": pendencias,
    }


@router.get("/dashboard")
async def dashboard(
    current_user=Depends(get_current_user),
):
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


@router.get("/alertas/vencimentos")
async def alertas_vencimentos(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    certidoes = await kronos.verificar_certidoes(db=db)
    asos = await kronos.verificar_asos_funcionarios(db=db)
    todos = certidoes + asos
    criticos = [c for c in todos if c.get("nivel") == "critico"]
    altos = [c for c in todos if c.get("nivel") == "alto"]
    return {
        "total_alertas": len(todos),
        "criticos": len(criticos),
        "altos": len(altos),
        "certidoes": certidoes,
        "asos_funcionarios": asos,
        "itens_criticos": criticos,
    }


@router.get("/conformidade/{cliente_id}/{competencia}")
async def verificar_conformidade(
    cliente_id: str,
    competencia: str,
    current_user=Depends(get_current_user),
):
    ctx = await gedeon_context.get(cliente_id, competencia)
    documentos_presentes = [d["tipo"] for d in ctx.get("documentos_gerados", [])]
    tipo_kit = ctx.get("tipo_kit", "maos_de_obra")
    resultado = argos.verificar_conformidade(
        tipo_kit=tipo_kit,
        documentos_presentes=documentos_presentes,
        movimentacoes=ctx.get("movimentacao_pessoal", []),
        certidoes_status=ctx.get("certidoes", {}),
    )
    return {"cliente_id": cliente_id, "competencia": competencia, "tipo_kit": tipo_kit, **resultado}


@router.post("/hermes/classificar")
async def classificar_documento(
    nome_arquivo: str = Query(..., description="Nome do arquivo a classificar"),
    conteudo_preview: str = Query("", description="Trecho do conteudo (opcional)"),
    current_user=Depends(get_current_user),
):
    resultado = hermes.classificar_documento(nome_arquivo, conteudo_preview)
    return {"nome_arquivo": nome_arquivo, **resultado}


@router.get("/kits/status")
async def kits_status_mensal(
    competencia: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Status consolidado de todos os kits do mes — gedeon_kit_config + Redis."""
    if not competencia:
        competencia = datetime.utcnow().strftime("%Y-%m")
    rows = await db.execute(
        sa_text(
            "SELECT c.id::text AS id, c.name, gkc.tipo_kit "
            "FROM gedeon_kit_config gkc "
            "JOIN clients c ON c.id = gkc.client_id "
            "WHERE gkc.ativo = TRUE ORDER BY c.name"
        )
    )
    clientes = rows.mappings().all()
    status_kits = []
    for row in clientes:
        ctx = await gedeon_context.get(row["id"], competencia)
        score = ctx.get("score_prontidao", 100)
        tipo_ok = ctx.get("tipo_kit") or row["tipo_kit"]
        status_kits.append(
            {
                "cliente_id": row["id"],
                "nome": row["name"],
                "tipo_kit": tipo_ok,
                "score": score,
                "pendencias": len(ctx.get("pendencias", [])),
                "status": "pronto" if score >= 90 else "alerta" if score >= 70 else "critico",
            }
        )
    venc_alerta = len(await kronos.verificar_certidoes(db=db))
    return {
        "competencia": competencia,
        "total_clientes": len(status_kits),
        "prontos": sum(1 for k in status_kits if k["status"] == "pronto"),
        "alertas": sum(1 for k in status_kits if k["status"] == "alerta"),
        "criticos": sum(1 for k in status_kits if k["status"] == "critico"),
        "vencimentos_alerta": venc_alerta,
        "kits": status_kits,
    }


@router.get("/kits/config")
async def kits_config(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retorna tipo_kit por cliente ativo para o frontend saber qual checklist abrir."""
    rows = await db.execute(
        sa_text(
            "SELECT c.id::text AS id, c.name, gkc.tipo_kit, gkc.servicos "
            "FROM gedeon_kit_config gkc "
            "JOIN clients c ON c.id = gkc.client_id "
            "WHERE gkc.ativo = TRUE ORDER BY c.name"
        )
    )
    return {
        "configs": [
            {"cliente_id": r["id"], "nome": r["name"], "tipo_kit": r["tipo_kit"], "servicos": r["servicos"] or []}
            for r in rows.mappings().all()
        ]
    }


@router.get("/atlas/insights")
async def atlas_insights(
    current_user=Depends(get_current_user),
):
    """ATLAS: insights mensais do aprendizado continuo."""
    from modules.gedeon.agents.atlas import atlas

    competencia = datetime.utcnow().strftime("%Y-%m")
    insights = atlas.gerar_insights_mensais()
    return {
        "competencia": competencia,
        "total_insights": len(insights),
        "insights": insights,
        "agente": "ATLAS",
        "descricao": "Aprendizado Continuo — o sistema fica mais inteligente a cada kit",
    }


@router.get("/atlas/historico/{cliente_id}/{competencia}")
async def atlas_historico(
    cliente_id: str,
    competencia: str,
    current_user=Depends(get_current_user),
):
    """ATLAS: historico de kits do cliente."""
    from modules.gedeon.agents.atlas import atlas

    return atlas.obter_contexto_historico(cliente_id, competencia)


@router.get("/atlas/anomalia/{cliente_id}")
async def atlas_anomalia(
    cliente_id: str,
    score_atual: int = Query(..., ge=0, le=100),
    docs_atual: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
):
    """ATLAS: detecta anomalia comparando com historico."""
    from modules.gedeon.agents.atlas import atlas

    anomalia = atlas.detectar_anomalia(cliente_id, docs_atual, score_atual)
    return {
        "cliente_id": cliente_id,
        "score_atual": score_atual,
        "anomalia_detectada": anomalia is not None,
        "mensagem": anomalia,
    }


@router.get("/sophia/buscar")
async def sophia_buscar(
    q: str,
    cliente_id: str | None = None,
    tipo: str | None = None,
    competencia: str | None = None,
    limite: int = 10,
    current_user=Depends(get_current_user),
):
    """SOPHIA: busca semantica em linguagem natural."""
    from modules.gedeon.agents.sophia import sophia

    filtros: dict = {}
    if cliente_id:
        filtros["cliente_id"] = cliente_id
    if tipo:
        filtros["tipo"] = tipo
    if competencia:
        filtros["competencia"] = competencia
    resultados = sophia.buscar(q, limite=limite, filtros=filtros or None)
    return {"query": q, "total": len(resultados), "resultados": resultados}


@router.get("/sophia/perguntar")
async def sophia_perguntar(
    q: str,
    current_user=Depends(get_current_user),
):
    """SOPHIA: pergunta em linguagem natural."""
    from modules.gedeon.agents.sophia import sophia

    return {"pergunta": q, "resposta": sophia.responder_pergunta(q)}


@router.post("/sophia/indexar")
async def sophia_indexar(
    current_user=Depends(get_current_user),
):
    """SOPHIA: indexar acervo completo."""
    from modules.gedeon.agents.sophia import sophia

    total = await sophia.indexar_acervo_completo()
    return {"status": "ok", "indexados": total}


def _gerar_checklist(ctx: dict) -> dict:
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
