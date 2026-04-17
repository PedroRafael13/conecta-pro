"""GEDEON Fase 3 — Onvio API Endpoints"""

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.database.session import get_sync_db
from modules.gedeon.models.onvio_models import OnvioDocument, OnvioSyncLog
from modules.gedeon.onvio.onvio_client import OnvioClient
from modules.gedeon.onvio.onvio_sync_service import OnvioSyncService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/onvio", tags=["Onvio Sync"])


@router.get("/status")
async def status_sessao():
    """Verifica se a sessão Onvio está ativa no Redis."""
    c = OnvioClient()
    return {"sessao_valida": c.validar_sessao(), "redis_key": "onvio:session"}


@router.post("/sync")
async def trigger_sync(
    mes_ref: str | None = None,
):
    """Inicia sincronização completa ou filtrada por mês (MM.AAAA)."""

    def _run_sync() -> dict:
        with get_sync_db() as sync_db:
            svc = OnvioSyncService(sync_db)
            return svc.sync_completo(mes_ref=mes_ref)

    try:
        loop = asyncio.get_event_loop()
        resultado = await loop.run_in_executor(None, _run_sync)
        return {"message": "Sync iniciado", "resultado": resultado}
    except Exception as exc:
        logger.error("Erro no sync Onvio: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/documentos")
async def listar_documentos(
    categoria: str | None = None,
    mes_ref: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Lista documentos importados do Onvio."""
    stmt = select(OnvioDocument).order_by(OnvioDocument.data_onvio.desc()).limit(limit)
    if categoria:
        stmt = stmt.where(OnvioDocument.categoria == categoria)
    if mes_ref:
        stmt = stmt.where(OnvioDocument.mes_ref == mes_ref)

    result = await db.execute(stmt)
    docs = result.scalars().all()

    count_stmt = select(func.count(OnvioDocument.id))
    if categoria:
        count_stmt = count_stmt.where(OnvioDocument.categoria == categoria)
    if mes_ref:
        count_stmt = count_stmt.where(OnvioDocument.mes_ref == mes_ref)
    total = (await db.execute(count_stmt)).scalar() or 0

    return {
        "total": total,
        "documentos": [
            {
                "id": str(d.id),
                "nome": d.nome_arquivo,
                "categoria": d.categoria,
                "mes_ref": d.mes_ref,
                "data_onvio": str(d.data_onvio),
            }
            for d in docs
        ],
    }


@router.get("/historico")
async def historico_sync(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Retorna histórico de execuções de sync."""
    result = await db.execute(select(OnvioSyncLog).order_by(OnvioSyncLog.created_at.desc()).limit(limit))
    logs = result.scalars().all()
    return [
        {
            "id": str(l.id),
            "mes_ref": l.mes_ref,
            "status": l.status,
            "novos": l.docs_novos,
            "erros": l.docs_erro,
            "duracao_s": l.duracao_s,
            "created_at": str(l.created_at),
        }
        for l in logs
    ]


@router.get("/stats")
async def stats_documentos(db: AsyncSession = Depends(get_db)):
    """Totais de documentos por categoria."""
    result = await db.execute(
        select(OnvioDocument.categoria, func.count(OnvioDocument.id)).group_by(OnvioDocument.categoria)
    )
    cats = result.fetchall()
    count_result = await db.execute(select(func.count(OnvioDocument.id)))
    total = count_result.scalar() or 0
    return {"total": total, "por_categoria": dict(cats)}


@router.get("/guias/fgts")
async def listar_guias_fgts(mes_ref: str | None = None, db: AsyncSession = Depends(get_db)):
    sql = "SELECT id, mes_ref, tipo, valor, status, arquivo_pdf FROM fgts_guias"
    params: dict = {}
    if mes_ref:
        sql += " WHERE mes_ref = :mes_ref"
        params["mes_ref"] = mes_ref
    sql += " ORDER BY mes_ref DESC"
    result = await db.execute(text(sql), params)
    rows = result.mappings().all()
    return [
        {
            "id": str(r["id"]),
            "mes_ref": r["mes_ref"],
            "tipo": r["tipo"],
            "valor": r["valor"],
            "status": r["status"],
            "arquivo_pdf": r["arquivo_pdf"],
        }
        for r in rows
    ]


@router.get("/guias/inss")
async def listar_guias_inss(mes_ref: str | None = None, db: AsyncSession = Depends(get_db)):
    sql = "SELECT id, mes_ref, valor, status, arquivo_pdf FROM inss_guias"
    params: dict = {}
    if mes_ref:
        sql += " WHERE mes_ref = :mes_ref"
        params["mes_ref"] = mes_ref
    sql += " ORDER BY mes_ref DESC"
    result = await db.execute(text(sql), params)
    rows = result.mappings().all()
    return [
        {
            "id": str(r["id"]),
            "mes_ref": r["mes_ref"],
            "valor": r["valor"],
            "status": r["status"],
            "arquivo_pdf": r["arquivo_pdf"],
        }
        for r in rows
    ]
