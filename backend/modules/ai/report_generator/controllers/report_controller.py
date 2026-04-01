"""
Report Controller - Endpoints REST para relatórios.

Expõe APIs para geração, agendamento e exportação de relatórios.
"""

import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.ai.report_generator.models.report import ReportStatusEnum, ReportTypeEnum
from modules.ai.report_generator.models.report_execution import ExecutionStatusEnum
from modules.ai.report_generator.models.report_schedule import ScheduleStatusEnum
from modules.ai.report_generator.models.report_template import TemplateCategoryEnum, TemplateStatusEnum
from modules.ai.report_generator.repositories import ReportRepository
from modules.ai.report_generator.schemas import (
    ExportReportRequest,
    ExportReportResponse,
    GenerateReportRequest,
    GenerateReportResponse,
    ReportDashboardResponse,
    ReportExecutionListResponse,
    ReportExecutionResponse,
    ReportListResponse,
    ReportResponse,
    ReportScheduleCreate,
    ReportScheduleListResponse,
    ReportScheduleResponse,
    ReportScheduleUpdate,
    ReportStatsResponse,
    ReportSummary,
    ReportTemplateCreate,
    ReportTemplateListResponse,
    ReportTemplateResponse,
    ReportTemplateUpdate,
    ReportUpdate,
)
from modules.ai.report_generator.services import (
    ReportExporter,
    ReportGeneratorService,
    ReportScheduler,
    TemplateEngine,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["AI Report Generator"])


# ============== REPORT ENDPOINTS ==============


@router.post("/generate", response_model=GenerateReportResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_report(
    request: GenerateReportRequest,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """
    Gera um novo relatório.

    Inicia a geração de um relatório baseado no template ou configuração fornecida.
    """
    try:
        service = ReportGeneratorService(db)
        report, execution = await service.generate_report(
            template_id=request.template_id,
            template_code=request.template_code,
            name=request.name,
            report_type=request.report_type,
            period_start=request.period_start,
            period_end=request.period_end,
            period_type=request.period_type,
            parameters=request.parameters,
            filters=request.filters,
            output_formats=request.output_formats,
            include_insights=request.include_insights,
            include_recommendations=request.include_recommendations,
            include_anomalies=request.include_anomalies,
            priority=request.priority,
        )

        return GenerateReportResponse(
            report_id=report.id,
            execution_id=execution.id,
            status=execution.status,
            message="Relatório gerado com sucesso" if execution.is_completed else "Geração em andamento",
            estimated_time_seconds=None,
            progress_url=f"/api/v1/reports/executions/{execution.id}",
        )
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=ReportListResponse)
async def list_reports(
    current_user: CurrentActiveUser,
    report_type: ReportTypeEnum | None = None,
    status: ReportStatusEnum | None = None,
    category: str | None = None,
    template_id: UUID | None = None,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lista relatórios com filtros e paginação."""
    repository = ReportRepository(db)
    skip = (page - 1) * size

    reports, total = repository.list_reports(
        report_type=report_type,
        status=status,
        category=category,
        template_id=template_id,
        period_start=period_start,
        period_end=period_end,
        search=search,
        skip=skip,
        limit=size,
    )

    return ReportListResponse(
        items=[ReportSummary(**r.to_summary_dict()) for r in reports],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Busca relatório por ID."""
    repository = ReportRepository(db)
    report = repository.get_report(report_id)

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relatório não encontrado")

    # Marca como visualizado
    report.mark_as_viewed()
    repository.update_report(report)

    return report


@router.patch("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: UUID,
    update_data: ReportUpdate,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Atualiza relatório."""
    repository = ReportRepository(db)
    report = repository.get_report(report_id)

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relatório não encontrado")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(report, field, value)

    return repository.update_report(report)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Remove relatório."""
    repository = ReportRepository(db)
    if not repository.delete_report(report_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relatório não encontrado")


@router.post("/{report_id}/export", response_model=ExportReportResponse)
async def export_report(
    report_id: UUID,
    request: ExportReportRequest,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Exporta relatório para formato especificado."""
    exporter = ReportExporter(db)

    try:
        result = exporter.export_report(
            report_id=report_id,
            format_type=request.format,
            include_charts=request.include_charts,
            include_data=request.include_data,
            page_size=request.page_size,
            orientation=request.orientation,
            password=request.password,
        )

        return ExportReportResponse(
            report_id=report_id,
            format=request.format,
            file_path=result["file_path"],
            file_url=result.get("file_url"),
            file_size_bytes=result["file_size_bytes"],
            generated_at=datetime.fromisoformat(result["generated_at"]),
            expires_at=None,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============== TEMPLATE ENDPOINTS ==============


@router.post("/templates", response_model=ReportTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: ReportTemplateCreate,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Cria novo template de relatório."""
    engine = TemplateEngine(db)

    try:
        template = engine.create_template(
            code=template_data.code,
            name=template_data.name,
            description=template_data.description,
            category=template_data.category,
            data_sources=template_data.data_sources,
            parameters=[p.model_dump() for p in template_data.parameters] if template_data.parameters else None,
            sections_config=[s.model_dump() for s in template_data.sections_config]
            if template_data.sections_config
            else None,
            widgets_config=template_data.widgets_config,
            metrics_config=template_data.metrics_config,
            supported_formats=template_data.supported_formats,
            ai_insights_enabled=template_data.ai_insights_enabled,
        )
        return template
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/templates", response_model=ReportTemplateListResponse)
async def list_templates(
    current_user: CurrentActiveUser,
    category: TemplateCategoryEnum | None = None,
    status: TemplateStatusEnum | None = None,
    is_public: bool | None = None,
    is_system: bool | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lista templates de relatório."""
    repository = ReportRepository(db)
    skip = (page - 1) * size

    templates, total = repository.list_templates(
        category=category.value if category else None,
        status=status,
        is_public=is_public,
        is_system=is_system,
        search=search,
        skip=skip,
        limit=size,
    )

    return ReportTemplateListResponse(
        items=templates,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.get("/templates/{template_id}", response_model=ReportTemplateResponse)
async def get_template(
    template_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Busca template por ID."""
    repository = ReportRepository(db)
    template = repository.get_template(template_id)

    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template não encontrado")

    return template


@router.patch("/templates/{template_id}", response_model=ReportTemplateResponse)
async def update_template(
    template_id: UUID,
    update_data: ReportTemplateUpdate,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Atualiza template."""
    engine = TemplateEngine(db)

    try:
        template = engine.update_template(template_id, **update_data.model_dump(exclude_unset=True))
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template não encontrado")
        return template
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Remove template."""
    repository = ReportRepository(db)
    if not repository.delete_template(template_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template não encontrado")


@router.post("/templates/{template_id}/clone", response_model=ReportTemplateResponse)
async def clone_template(
    template_id: UUID,
    current_user: CurrentActiveUser,
    new_code: str = Query(...),
    new_name: str = Query(...),
    db: Session = Depends(get_db),
):
    """Clona um template existente."""
    engine = TemplateEngine(db)

    try:
        template = engine.clone_template(template_id, new_code, new_name)
        return template
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/templates/{template_id}/publish", response_model=ReportTemplateResponse)
async def publish_template(
    template_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Publica um template (ativa)."""
    engine = TemplateEngine(db)

    try:
        template = engine.publish_template(template_id)
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template não encontrado")
        return template
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/templates/{template_id}/validate")
async def validate_template(
    template_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Valida um template."""
    engine = TemplateEngine(db)

    try:
        result = engine.validate_template(template_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/templates/initialize-defaults")
async def initialize_default_templates(
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Inicializa templates padrão do sistema."""
    engine = TemplateEngine(db)
    templates = engine.initialize_default_templates()

    return {
        "message": f"{len(templates)} templates criados",
        "templates": [{"code": t.code, "name": t.name} for t in templates],
    }


# ============== SCHEDULE ENDPOINTS ==============


@router.post("/schedules", response_model=ReportScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: ReportScheduleCreate,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Cria novo agendamento de relatório."""
    scheduler = ReportScheduler(db)

    schedule = scheduler.create_schedule(
        name=schedule_data.name,
        template_id=schedule_data.template_id,
        frequency=schedule_data.frequency,
        run_time=schedule_data.run_time.isoformat() if schedule_data.run_time else None,
        timezone=schedule_data.timezone,
        days_of_week=schedule_data.days_of_week,
        days_of_month=schedule_data.days_of_month,
        period_type=schedule_data.period_type,
        parameters=schedule_data.parameters,
        filters=schedule_data.filters,
        output_formats=schedule_data.output_formats,
        email_recipients=schedule_data.email_recipients,
        email_subject=schedule_data.email_subject,
        email_body=schedule_data.email_body,
        webhook_url=schedule_data.webhook_url,
        start_date=schedule_data.start_date,
        end_date=schedule_data.end_date,
        max_runs=schedule_data.max_runs,
    )

    return schedule


@router.get("/schedules", response_model=ReportScheduleListResponse)
async def list_schedules(
    current_user: CurrentActiveUser,
    template_id: UUID | None = None,
    status: ScheduleStatusEnum | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lista agendamentos de relatório."""
    repository = ReportRepository(db)
    skip = (page - 1) * size

    schedules, total = repository.list_schedules(
        template_id=template_id,
        status=status,
        skip=skip,
        limit=size,
    )

    return ReportScheduleListResponse(
        items=schedules,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.get("/schedules/{schedule_id}", response_model=ReportScheduleResponse)
async def get_schedule(
    schedule_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Busca agendamento por ID."""
    repository = ReportRepository(db)
    schedule = repository.get_schedule(schedule_id)

    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

    return schedule


@router.patch("/schedules/{schedule_id}", response_model=ReportScheduleResponse)
async def update_schedule(
    schedule_id: UUID,
    update_data: ReportScheduleUpdate,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Atualiza agendamento."""
    scheduler = ReportScheduler(db)

    schedule = scheduler.update_schedule(schedule_id, **update_data.model_dump(exclude_unset=True))

    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

    return schedule


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Remove agendamento."""
    repository = ReportRepository(db)
    if not repository.delete_schedule(schedule_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")


@router.post("/schedules/{schedule_id}/pause", response_model=ReportScheduleResponse)
async def pause_schedule(
    schedule_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Pausa agendamento."""
    scheduler = ReportScheduler(db)
    schedule = scheduler.pause_schedule(schedule_id)

    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

    return schedule


@router.post("/schedules/{schedule_id}/resume", response_model=ReportScheduleResponse)
async def resume_schedule(
    schedule_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Retoma agendamento."""
    scheduler = ReportScheduler(db)
    schedule = scheduler.resume_schedule(schedule_id)

    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

    return schedule


@router.post("/schedules/process-due")
async def process_due_schedules(
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Processa agendamentos pendentes."""
    scheduler = ReportScheduler(db)
    results = scheduler.process_due_schedules()

    return {
        "processed": len(results),
        "results": results,
    }


# ============== EXECUTION ENDPOINTS ==============


@router.get("/executions", response_model=ReportExecutionListResponse)
async def list_executions(
    current_user: CurrentActiveUser,
    report_id: UUID | None = None,
    template_id: UUID | None = None,
    schedule_id: UUID | None = None,
    status: ExecutionStatusEnum | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lista execuções de relatório."""
    repository = ReportRepository(db)
    skip = (page - 1) * size

    executions, total = repository.list_executions(
        report_id=report_id,
        template_id=template_id,
        schedule_id=schedule_id,
        status=status,
        skip=skip,
        limit=size,
    )

    return ReportExecutionListResponse(
        items=executions,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.get("/executions/{execution_id}", response_model=ReportExecutionResponse)
async def get_execution(
    execution_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Busca execução por ID."""
    repository = ReportRepository(db)
    execution = repository.get_execution(execution_id)

    if not execution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execução não encontrada")

    return execution


# ============== DASHBOARD & STATS ==============


@router.get("/dashboard", response_model=ReportDashboardResponse)
async def get_dashboard(
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Retorna dashboard de relatórios."""
    repository = ReportRepository(db)
    data = repository.get_dashboard_data()

    stats = data["report_stats"]
    schedule_stats = data["schedule_stats"]

    return ReportDashboardResponse(
        total_reports=stats["total_reports"],
        reports_by_status=stats["by_status"],
        reports_by_type=stats["by_type"],
        reports_this_month=stats["total_reports"],
        reports_trend=[],
        average_generation_time_ms=stats["average_generation_time_ms"],
        total_insights_generated=stats["total_insights"],
        total_anomalies_detected=0,
        most_used_templates=data["most_used_templates"],
        recent_reports=[ReportSummary(**r) for r in data["recent_reports"]],
        scheduled_reports_count=schedule_stats["total_schedules"],
        failed_schedules_count=schedule_stats["failed"],
    )


@router.get("/stats", response_model=ReportStatsResponse)
async def get_stats(
    current_user: CurrentActiveUser,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Retorna estatísticas de relatórios."""
    repository = ReportRepository(db)
    stats = repository.get_report_stats(days=days)
    repository.get_execution_metrics(days=days)

    return ReportStatsResponse(
        period=f"Últimos {days} dias",
        total_generated=stats["total_reports"],
        total_exported=stats["completed"],
        total_delivered=0,
        generation_success_rate=stats["success_rate"],
        delivery_success_rate=0.0,
        average_generation_time_ms=stats["average_generation_time_ms"],
        insights_per_report=stats["total_insights"] / max(1, stats["total_reports"]),
        most_common_types=[{"type": k, "count": v} for k, v in stats["by_type"].items()],
        most_common_formats=[],
        busiest_hours=[],
    )


# ============== METADATA ENDPOINTS ==============


@router.get("/metadata/data-sources")
async def get_data_sources(
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Retorna fontes de dados disponíveis."""
    engine = TemplateEngine(db)
    return engine.get_available_data_sources()


@router.get("/metadata/section-types")
async def get_section_types(
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Retorna tipos de seção disponíveis."""
    engine = TemplateEngine(db)
    return engine.get_available_section_types()


@router.get("/metadata/chart-types")
async def get_chart_types(
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Retorna tipos de gráfico disponíveis."""
    engine = TemplateEngine(db)
    return engine.get_available_chart_types()


@router.get("/metadata/export-formats")
async def get_export_formats(
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Retorna formatos de exportação suportados."""
    exporter = ReportExporter(db)
    return exporter.get_supported_formats()
