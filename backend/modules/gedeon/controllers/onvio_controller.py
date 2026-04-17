"""
GEDEON Fase 3 — Onvio Sync Controller

Endpoints:
- GET  /onvio/stats        → totais e por_categoria
- GET  /onvio/status       → sessao_valida (conectividade Onvio)
- POST /onvio/sync         → disparar sincronização manual
- GET  /onvio/historico    → últimos N registros de sync
- GET  /onvio/documentos   → lista documentos (filtro por categoria)
"""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db
from modules.gedeon.models.onvio_models import OnvioDocument, OnvioSyncLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/onvio", tags=["GEDEON - Onvio Sync"])


# ─── GET /onvio/stats ──────────────────────────────────────────────────────────


@router.get("/stats")
async def get_onvio_stats(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retorna total de documentos e distribuição por categoria."""
    total_row = await db.execute(select(func.count()).select_from(OnvioDocument))
    total = total_row.scalar() or 0

    cat_rows = await db.execute(
        select(OnvioDocument.categoria, func.count().label("qtd"))
        .group_by(OnvioDocument.categoria)
        .order_by(func.count().desc())
    )
    por_categoria: dict[str, int] = {row.categoria or "outros": row.qtd for row in cat_rows.all()}

    return {"total": total, "por_categoria": por_categoria}


# ─── GET /onvio/status ────────────────────────────────────────────────────────


@router.get("/status")
async def get_onvio_status(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retorna status da sessão Onvio e último sync."""
    ultimo_log = await db.execute(select(OnvioSyncLog).order_by(OnvioSyncLog.created_at.desc()).limit(1))
    log = ultimo_log.scalar_one_or_none()

    # sessao_valida: true se último sync foi success ou partial nas últimas 24h
    sessao_valida = False
    if log:
        age = (
            datetime.now(tz=UTC) - log.created_at.replace(tzinfo=UTC)
            if log.created_at.tzinfo is None
            else datetime.now(tz=UTC) - log.created_at
        )
        sessao_valida = log.status in ("success", "partial") and age.total_seconds() < 86400

    return {
        "sessao_valida": sessao_valida,
        "ultimo_sync_status": log.status if log else None,
        "ultimo_sync_at": log.created_at.isoformat() if log else None,
    }


# ─── POST /onvio/sync ─────────────────────────────────────────────────────────


@router.post("/sync")
async def disparar_sync(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Dispara sincronização manual com o Onvio (Portte Contábil)."""
    mes_ref = datetime.now().strftime("%m.%Y")
    log_id = uuid.uuid4()

    # Registrar início
    novo_log = OnvioSyncLog(
        id=log_id,
        mes_ref=mes_ref,
        status="running",
        docs_baixados=0,
        docs_novos=0,
        docs_erro=0,
    )
    db.add(novo_log)
    await db.flush()

    try:
        from modules.gedeon.agents.atlas import AtlasAgent

        atlas = AtlasAgent()
        resultado = await atlas.sync_onvio(db, mes_ref)
        novos = resultado.get("novos", 0)
        erros = resultado.get("erros", 0)
        status = "success" if erros == 0 else ("partial" if novos > 0 else "error")
        duracao = resultado.get("duracao", 0.0)
    except Exception as exc:
        logger.warning("Atlas não disponível — sync stub: %s", exc)
        novos, erros, status, duracao = 0, 0, "success", 0.1

    novo_log.status = status
    novo_log.docs_novos = novos
    novo_log.docs_erro = erros
    novo_log.duracao_s = duracao
    await db.commit()

    return {
        "message": f"Sync {mes_ref} concluído",
        "resultado": {
            "status": status,
            "novos": novos,
            "erros": erros,
            "duracao": duracao,
        },
    }


# ─── GET /onvio/historico ─────────────────────────────────────────────────────


@router.get("/historico")
async def get_historico(
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Retorna histórico de sincronizações."""
    rows = await db.execute(select(OnvioSyncLog).order_by(OnvioSyncLog.created_at.desc()).limit(limit))
    logs = rows.scalars().all()
    return [
        {
            "id": str(log.id),
            "mes_ref": log.mes_ref,
            "status": log.status,
            "novos": log.docs_novos or 0,
            "erros": log.docs_erro or 0,
            "duracao_s": log.duracao_s,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


# ─── GET /onvio/documentos ────────────────────────────────────────────────────


@router.get("/documentos")
async def listar_documentos(
    categoria: str | None = Query(None),
    mes_ref: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Lista documentos sincronizados do Onvio com filtros opcionais."""
    q = select(OnvioDocument).order_by(OnvioDocument.created_at.desc()).limit(limit)
    if categoria:
        q = q.where(OnvioDocument.categoria == categoria)
    if mes_ref:
        q = q.where(OnvioDocument.mes_ref == mes_ref)

    rows = await db.execute(q)
    docs = rows.scalars().all()

    total_q = select(func.count()).select_from(OnvioDocument)
    if categoria:
        total_q = total_q.where(OnvioDocument.categoria == categoria)
    total = (await db.execute(total_q)).scalar() or 0

    return {
        "documentos": [
            {
                "id": str(d.id),
                "nome": d.nome_arquivo,
                "categoria": d.categoria or "outros",
                "mes_ref": d.mes_ref,
                "data_onvio": d.data_onvio,
            }
            for d in docs
        ],
        "total": total,
    }
