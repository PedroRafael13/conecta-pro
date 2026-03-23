"""Controller para endpoints de Relatórios."""

import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db
from modules.hr.analytics_dashboard.models import ReportFormat, ReportStatus
from modules.hr.analytics_dashboard.repositories import ReportRepository
from modules.hr.analytics_dashboard.schemas import (
    ReportRunResponse,
    ScheduledReportCreate,
    ScheduledReportResponse,
    ScheduledReportUpdate,
)
from modules.hr.analytics_dashboard.services import ReportGeneratorService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["Relatórios"])


@router.get("", response_model=list[ScheduledReportResponse])
async def list_reports(
    report_type: str | None = Query(None),
    report_status: ReportStatus | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lista relatórios agendados."""
    repo = ReportRepository(db)
    reports, _total = await repo.list_reports(
        condominio_id=current_user["condominio_id"],
        report_type=report_type,
        status=report_status,
        page=page,
        page_size=page_size,
    )
    return reports


@router.post("", response_model=ScheduledReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    data: ScheduledReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Cria novo relatório agendado."""
    repo = ReportRepository(db)
    report = await repo.create_report(
        data=data,
        condominio_id=current_user["condominio_id"],
        owner_id=current_user["id"],
    )
    return report


@router.get("/upcoming")
async def list_upcoming_reports(
    hours_ahead: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lista relatórios que serão executados nas próximas horas."""
    repo = ReportRepository(db)
    reports = await repo.get_upcoming_reports(
        condominio_id=current_user["condominio_id"],
        hours_ahead=hours_ahead,
    )
    return [
        {
            "id": str(r.id),
            "name": r.name,
            "report_type": r.report_type,
            "next_run_at": r.next_run_at.isoformat() if r.next_run_at else None,
            "recipients_count": len(r.recipients or []),
        }
        for r in reports
    ]


@router.get("/statistics")
async def get_report_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Obtém estatísticas de relatórios."""
    repo = ReportRepository(db)
    stats = await repo.get_statistics(
        condominio_id=current_user["condominio_id"],
    )
    return stats


@router.get("/{report_id}", response_model=ScheduledReportResponse)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Obtém relatório por ID."""
    repo = ReportRepository(db)
    report = await repo.get_report_by_id(report_id)
    if not report or report.condominio_id != current_user["condominio_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatório não encontrado",
        )
    return report


@router.patch("/{report_id}", response_model=ScheduledReportResponse)
async def update_report(
    report_id: UUID,
    data: ScheduledReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza relatório."""
    repo = ReportRepository(db)

    # Verificar propriedade
    existing = await repo.get_report_by_id(report_id)
    if not existing or existing.owner_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatório não encontrado",
        )

    report = await repo.update_report(report_id, data)
    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Deleta relatório."""
    repo = ReportRepository(db)

    existing = await repo.get_report_by_id(report_id)
    if not existing or existing.owner_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatório não encontrado",
        )

    await repo.delete_report(report_id)


@router.post("/{report_id}/run", response_model=ReportRunResponse)
async def run_report(
    report_id: UUID,
    period_start: datetime | None = Query(None),
    period_end: datetime | None = Query(None),
    output_format: ReportFormat | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Executa relatório manualmente."""
    repo = ReportRepository(db)

    report = await repo.get_report_by_id(report_id)
    if not report or report.condominio_id != current_user["condominio_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatório não encontrado",
        )

    service = ReportGeneratorService(db)
    result = await service.generate_report(
        report=report,
        period_start=period_start,
        period_end=period_end,
        output_format=output_format,
    )

    return result


@router.post("/{report_id}/pause", status_code=status.HTTP_204_NO_CONTENT)
async def pause_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Pausa agendamento de relatório."""
    repo = ReportRepository(db)

    existing = await repo.get_report_by_id(report_id)
    if not existing or existing.owner_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatório não encontrado",
        )

    success = await repo.pause_report(report_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível pausar o relatório",
        )


@router.post("/{report_id}/resume", response_model=ScheduledReportResponse)
async def resume_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Retoma agendamento de relatório."""
    repo = ReportRepository(db)

    existing = await repo.get_report_by_id(report_id)
    if not existing or existing.owner_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatório não encontrado",
        )

    report = await repo.resume_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível retomar o relatório",
        )
    return report


@router.get("/{report_id}/history")
async def get_report_history(  # pylint: disable=unused-argument
    report_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Obtém histórico de execuções do relatório."""
    repo = ReportRepository(db)

    report = await repo.get_report_by_id(report_id)
    if not report or report.condominio_id != current_user["condominio_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatório não encontrado",
        )

    # Em produção, teria uma tabela de histórico de execuções
    # Por enquanto, retornamos dados do relatório
    return {
        "report_id": str(report.id),
        "report_name": report.name,
        "total_runs": report.run_count,
        "success_count": report.success_count,
        "failure_count": report.failure_count,
        "last_run_at": report.last_run_at.isoformat() if report.last_run_at else None,
        "last_status": report.last_status,
        "last_error": report.last_error,
    }


@router.get("/{report_id}/download/{run_id}")
async def download_report(
    report_id: UUID,
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Download de arquivo do relatório."""
    repo = ReportRepository(db)

    report = await repo.get_report_by_id(report_id)
    if not report or report.condominio_id != current_user["condominio_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatório não encontrado",
        )

    # Em produção, retornaria FileResponse com o arquivo
    return {
        "message": "Download não implementado nesta versão",
        "report_id": str(report_id),
        "run_id": str(run_id),
        "file_path": report.last_file_path,
    }


@router.post("/process-due")
async def process_due_reports(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Processa relatórios pendentes (admin/scheduler)."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores",
        )

    service = ReportGeneratorService(db)
    result = await service.process_due_reports()
    return result
