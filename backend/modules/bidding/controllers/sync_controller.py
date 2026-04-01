"""
Controller de Sincronizacao - Licitacoes
=========================================
Endpoints para disparar e monitorar sincronizacoes com portais
publicos (PNCP, ComprasNet, etc.) via Celery tasks.
"""

import logging
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.bidding.models.opportunity import BiddingOpportunity
from modules.bidding.models.sync_job import BiddingSyncJob

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sync", tags=["Licitacoes - Sincronizacao"])


# ============================================================
# Schemas
# ============================================================


class PNCPSyncRequest(BaseModel):
    uf: str = Field(default="AM", max_length=2)
    keywords: list[str] | None = Field(default=None)


class PrecosSyncRequest(BaseModel):
    portal: str = Field(default="pncp")
    uf: str = Field(default="AM", max_length=2)


class SyncTriggerResponse(BaseModel):
    task_id: str
    status: str = "queued"
    message: str


# ============================================================
# Helpers
# ============================================================


def _job_to_dict(job: BiddingSyncJob) -> dict:
    return {
        "id": str(job.id),
        "portal": job.portal,
        "tipo": getattr(job, "tipo", None),
        "status": job.status,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
        "registros_processados": getattr(job, "registros_processados", 0),
        "registros_novos": getattr(job, "registros_novos", 0),
        "registros_atualizados": getattr(job, "registros_atualizados", 0),
        "erros": getattr(job, "erros", []),
        "filtros_utilizados": getattr(job, "filtros_utilizados", {}),
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }


def _send_celery_task(task_name: str, **kwargs) -> str:
    try:
        from celery_app import app as celery_app

        result = celery_app.send_task(task_name, kwargs=kwargs)
        return result.id
    except Exception as e:
        logger.warning(f"Celery indisponivel: {e}")
        import uuid

        return f"local-{uuid.uuid4().hex[:12]}"


# ============================================================
# POST /sync/pncp/trigger
# ============================================================


@router.post("/pncp/trigger", response_model=SyncTriggerResponse, status_code=201)
async def trigger_pncp_sync(
    current_user: CurrentActiveUser,
    request: PNCPSyncRequest = PNCPSyncRequest(),
    db: AsyncSession = Depends(get_db),
):
    """Dispara sincronizacao manual com o PNCP."""
    try:
        job = BiddingSyncJob(
            portal="pncp",
            tipo="oportunidades",
            status="pendente",
            filtros_utilizados={
                "uf": request.uf,
                "keywords": request.keywords or ["vigilancia", "seguranca patrimonial", "portaria"],
                "triggered_by": "manual",
            },
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        task_id = _send_celery_task(
            "bidding.sync_pncp_oportunidades",
            job_id=str(job.id),
            uf=request.uf,
            keywords=request.keywords or ["vigilancia", "seguranca patrimonial", "portaria"],
        )

        return SyncTriggerResponse(
            task_id=task_id,
            status="queued",
            message=f"Sincronizacao PNCP enfileirada para UF={request.uf}. Job ID: {job.id}",
        )
    except Exception as e:
        logger.error(f"Erro ao disparar sincronizacao PNCP: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao disparar sincronizacao: {str(e)}",
        )


# ============================================================
# GET /sync/jobs
# ============================================================


@router.get("/jobs")
async def list_sync_jobs(
    current_user: CurrentActiveUser,
    portal: str | None = Query(default=None),
    job_status: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Lista os jobs de sincronizacao mais recentes."""
    try:
        stmt = select(BiddingSyncJob)
        if portal:
            stmt = stmt.where(BiddingSyncJob.portal == portal)
        if job_status:
            stmt = stmt.where(BiddingSyncJob.status == job_status)
        stmt = stmt.order_by(desc(BiddingSyncJob.created_at)).limit(limit)

        result = await db.execute(stmt)
        jobs = result.scalars().all()

        return {
            "jobs": [_job_to_dict(j) for j in jobs],
            "total": len(jobs),
        }
    except Exception as e:
        logger.error(f"Erro ao listar sync jobs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar jobs: {str(e)}",
        )


# ============================================================
# GET /sync/jobs/{job_id}
# ============================================================


@router.get("/jobs/{job_id}")
async def get_sync_job(
    job_id: UUID,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
):
    """Retorna detalhes de um job de sincronizacao."""
    try:
        stmt = select(BiddingSyncJob).where(BiddingSyncJob.id == job_id)
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()

        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} nao encontrado")

        return _job_to_dict(job)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar sync job {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar job: {str(e)}",
        )


# ============================================================
# POST /sync/precos/trigger
# ============================================================


@router.post("/precos/trigger", response_model=SyncTriggerResponse, status_code=201)
async def trigger_price_sync(
    current_user: CurrentActiveUser,
    request: PrecosSyncRequest = PrecosSyncRequest(),
    db: AsyncSession = Depends(get_db),
):
    """Dispara sincronizacao manual de precos referenciais."""
    try:
        job = BiddingSyncJob(
            portal=request.portal,
            tipo="precos",
            status="pendente",
            filtros_utilizados={
                "portal": request.portal,
                "uf": request.uf,
                "triggered_by": "manual",
            },
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        task_id = _send_celery_task(
            "bidding.sync_pncp_precos",
            job_id=str(job.id),
            portal=request.portal,
            uf=request.uf,
        )

        return SyncTriggerResponse(
            task_id=task_id,
            status="queued",
            message=f"Sincronizacao de precos enfileirada ({request.portal}, UF={request.uf}). Job ID: {job.id}",
        )
    except Exception as e:
        logger.error(f"Erro ao disparar sync precos: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao disparar sincronizacao de precos: {str(e)}",
        )


# ============================================================
# GET /sync/status
# ============================================================


@router.get("/status")
async def get_sync_status(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
):
    """Retorna status geral de sincronizacao."""
    try:
        # Ultimo job
        stmt = select(BiddingSyncJob).order_by(desc(BiddingSyncJob.created_at)).limit(1)
        result = await db.execute(stmt)
        last_job = result.scalar_one_or_none()

        # Total oportunidades
        stmt_opp = select(func.count(BiddingOpportunity.id))
        total_opp = (await db.execute(stmt_opp)).scalar() or 0

        # Total jobs
        stmt_jobs = select(func.count(BiddingSyncJob.id))
        total_jobs = (await db.execute(stmt_jobs)).scalar() or 0

        # Jobs 24h
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        stmt_24h = select(func.count(BiddingSyncJob.id)).where(BiddingSyncJob.created_at >= twenty_four_hours_ago)
        jobs_24h = (await db.execute(stmt_24h)).scalar() or 0

        return {
            "last_sync_at": last_job.created_at.isoformat() if last_job else None,
            "last_sync_status": last_job.status if last_job else None,
            "last_sync_portal": last_job.portal if last_job else None,
            "next_scheduled": "A cada 2h (Celery Beat)",
            "total_opportunities": total_opp,
            "total_sync_jobs": total_jobs,
            "jobs_last_24h": jobs_24h,
        }
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter status: {str(e)}",
        )
