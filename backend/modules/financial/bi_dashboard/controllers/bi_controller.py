"""Controller de BI e Dashboards Financeiros."""

import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status
from sqlalchemy.orm import Session

from core.auth.dependencies import get_current_user
from core.database.session import get_db
from modules.financial.bi_dashboard.models import (
    AlertLevel,
    DashboardStatus,
    DashboardType,
    DataSource,
    KPICategory,
    KPIStatus,
    ReportFormat,
    ReportFrequency,
    ReportStatus,
    ReportType,
    WidgetType,
)
from modules.financial.bi_dashboard.repositories import (
    CacheRepository,
    DashboardRepository,
    KPIRepository,
    ReportRepository,
    WidgetRepository,
)
from modules.financial.bi_dashboard.schemas import (
    CacheInvalidate,
    CacheStats,
    DashboardCreate,
    DashboardFilters,
    DashboardListResponse,
    DashboardResponse,
    DashboardStats,
    DashboardUpdate,
    KPICreate,
    KPIFilters,
    KPIHistory,
    KPIResponse,
    KPISummary,
    KPIUpdate,
    KPIValue,
    ReportCreate,
    ReportFilters,
    ReportResponse,
    ReportUpdate,
    WidgetCreate,
    WidgetData,
    WidgetFilters,
    WidgetResponse,
    WidgetUpdate,
)
from modules.financial.bi_dashboard.services import (
    AnalyticsService,
    BIService,
    ForecastService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bi", tags=["BI Financeiro"])


# =============================================================================
# DASHBOARD ENDPOINTS
# =============================================================================


@router.post("/dashboards", response_model=DashboardResponse, status_code=http_status.HTTP_201_CREATED)
async def create_dashboard(
    data: DashboardCreate,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Cria novo dashboard."""
    repo = DashboardRepository(db)
    existing = repo.get_by_codigo(data.codigo, condominio_id)
    if existing:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Dashboard com codigo {data.codigo} ja existe",
        )
    dashboard = repo.create(condominio_id, data, current_user.get("id"))
    return dashboard


@router.get("/dashboards", response_model=DashboardListResponse)
async def list_dashboards(
    condominio_id: UUID = Query(...),
    tipo: DashboardType | None = None,
    status: DashboardStatus | None = None,
    is_public: bool | None = None,
    is_favorite: bool | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Lista dashboards com filtros."""
    repo = DashboardRepository(db)
    filters = DashboardFilters(
        tipo=tipo,
        status=status,
        is_public=is_public,
        is_favorite=is_favorite,
        search=search,
    )
    items, total = repo.list_all(condominio_id, filters, skip, limit)
    return DashboardListResponse(
        items=items,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        pages=(total + limit - 1) // limit,
    )


@router.get("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Busca dashboard por ID."""
    repo = DashboardRepository(db)
    dashboard = repo.get_by_id(dashboard_id, condominio_id, include_widgets=True)
    if not dashboard:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Dashboard nao encontrado",
        )
    repo.record_view(dashboard)
    return dashboard


@router.put("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: UUID,
    data: DashboardUpdate,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza dashboard."""
    repo = DashboardRepository(db)
    dashboard = repo.get_by_id(dashboard_id, condominio_id)
    if not dashboard:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Dashboard nao encontrado",
        )
    return repo.update(dashboard, data, current_user.get("id"))


@router.delete("/dashboards/{dashboard_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_dashboard(
    dashboard_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Deleta dashboard."""
    repo = DashboardRepository(db)
    dashboard = repo.get_by_id(dashboard_id, condominio_id)
    if not dashboard:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Dashboard nao encontrado",
        )
    repo.delete(dashboard)


@router.post("/dashboards/{dashboard_id}/publish", response_model=DashboardResponse)
async def publish_dashboard(
    dashboard_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Publica dashboard."""
    repo = DashboardRepository(db)
    dashboard = repo.get_by_id(dashboard_id, condominio_id)
    if not dashboard:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Dashboard nao encontrado",
        )
    dashboard.publish()
    db.commit()
    db.refresh(dashboard)
    return dashboard


@router.post("/dashboards/{dashboard_id}/archive", response_model=DashboardResponse)
async def archive_dashboard(
    dashboard_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Arquiva dashboard."""
    repo = DashboardRepository(db)
    dashboard = repo.get_by_id(dashboard_id, condominio_id)
    if not dashboard:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Dashboard nao encontrado",
        )
    dashboard.archive()
    db.commit()
    db.refresh(dashboard)
    return dashboard


@router.post("/dashboards/{dashboard_id}/favorite", response_model=DashboardResponse)
async def toggle_dashboard_favorite(
    dashboard_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Alterna favorito do dashboard."""
    repo = DashboardRepository(db)
    dashboard = repo.get_by_id(dashboard_id, condominio_id)
    if not dashboard:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Dashboard nao encontrado",
        )
    return repo.toggle_favorite(dashboard)


@router.post("/dashboards/{dashboard_id}/set-default", response_model=DashboardResponse)
async def set_default_dashboard(
    dashboard_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Define dashboard como padrao."""
    repo = DashboardRepository(db)
    dashboard = repo.get_by_id(dashboard_id, condominio_id)
    if not dashboard:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Dashboard nao encontrado",
        )
    return repo.set_default(dashboard, condominio_id)


@router.get("/dashboards/default", response_model=DashboardResponse)
async def get_default_dashboard(
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Busca dashboard padrao."""
    repo = DashboardRepository(db)
    dashboard = repo.get_default(condominio_id)
    if not dashboard:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Nenhum dashboard padrao definido",
        )
    return dashboard


@router.post("/dashboards/{dashboard_id}/duplicate", response_model=DashboardResponse)
async def duplicate_dashboard(
    dashboard_id: UUID,
    novo_nome: str = Query(...),
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Duplica dashboard."""
    repo = DashboardRepository(db)
    dashboard = repo.get_by_id(dashboard_id, condominio_id)
    if not dashboard:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Dashboard nao encontrado",
        )
    return repo.duplicate(dashboard, novo_nome, created_by=current_user.get("id"))


@router.get("/dashboards/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Retorna estatisticas de dashboards."""
    repo = DashboardRepository(db)
    return repo.get_stats(condominio_id)


# =============================================================================
# WIDGET ENDPOINTS
# =============================================================================


@router.post("/widgets", response_model=WidgetResponse, status_code=http_status.HTTP_201_CREATED)
async def create_widget(
    data: WidgetCreate,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Cria novo widget."""
    repo = WidgetRepository(db)
    widget = repo.create(condominio_id, data, current_user.get("id"))
    return widget


@router.get("/widgets", response_model=list[WidgetResponse])
async def list_widgets(
    condominio_id: UUID = Query(...),
    dashboard_id: UUID | None = None,
    tipo: WidgetType | None = None,
    data_source: DataSource | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Lista widgets com filtros."""
    repo = WidgetRepository(db)
    filters = WidgetFilters(
        dashboard_id=dashboard_id,
        tipo=tipo,
        data_source=data_source,
    )
    items, _ = repo.list_all(condominio_id, filters, skip, limit)
    return items


@router.get("/widgets/{widget_id}", response_model=WidgetResponse)
async def get_widget(
    widget_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Busca widget por ID."""
    repo = WidgetRepository(db)
    widget = repo.get_by_id(widget_id, condominio_id)
    if not widget:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Widget nao encontrado",
        )
    return widget


@router.put("/widgets/{widget_id}", response_model=WidgetResponse)
async def update_widget(
    widget_id: UUID,
    data: WidgetUpdate,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Atualiza widget."""
    repo = WidgetRepository(db)
    widget = repo.get_by_id(widget_id, condominio_id)
    if not widget:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Widget nao encontrado",
        )
    return repo.update(widget, data)


@router.delete("/widgets/{widget_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_widget(
    widget_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Deleta widget."""
    repo = WidgetRepository(db)
    widget = repo.get_by_id(widget_id, condominio_id)
    if not widget:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Widget nao encontrado",
        )
    repo.delete(widget)


@router.get("/widgets/{widget_id}/data", response_model=WidgetData)
async def get_widget_data(
    widget_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Busca dados do widget."""
    repo = WidgetRepository(db)
    widget = repo.get_by_id(widget_id, condominio_id)
    if not widget:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Widget nao encontrado",
        )

    bi_service = BIService(db)
    data = bi_service.get_widget_data(
        data_source=widget.data_source,
        metric_field=widget.metric_field or "valor",
        dimension_field=widget.dimension_field,
        aggregation=widget.aggregation,
        filters=widget.filters,
        date_range_days=widget.date_range_days,
        group_by=widget.group_by,
        limit=widget.limit,
        condominio_id=condominio_id,
    )

    repo.mark_loaded(widget)

    return WidgetData(
        widget_id=widget_id,
        data=data["data"],
        total_rows=data["total_rows"],
        loaded_at=datetime.utcnow(),
        cached=False,
        ttl_remaining=widget.cache_ttl_seconds,
    )


@router.post("/widgets/{widget_id}/refresh", response_model=WidgetData)
async def refresh_widget_data(
    widget_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Forca refresh dos dados do widget."""
    return await get_widget_data(widget_id, condominio_id, db)


@router.put("/widgets/{widget_id}/position")
async def update_widget_position(
    widget_id: UUID,
    x: int = Query(..., ge=0),
    y: int = Query(..., ge=0),
    w: int | None = Query(None, ge=1),
    h: int | None = Query(None, ge=1),
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Atualiza posicao do widget."""
    repo = WidgetRepository(db)
    widget = repo.get_by_id(widget_id, condominio_id)
    if not widget:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Widget nao encontrado",
        )
    return repo.update_position(widget, x, y, w, h)


@router.put("/widgets/{widget_id}/visibility")
async def set_widget_visibility(
    widget_id: UUID,
    is_visible: bool = Query(...),
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Define visibilidade do widget."""
    repo = WidgetRepository(db)
    widget = repo.get_by_id(widget_id, condominio_id)
    if not widget:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Widget nao encontrado",
        )
    return repo.set_visibility(widget, is_visible)


@router.post("/widgets/{widget_id}/clone", response_model=WidgetResponse)
async def clone_widget(
    widget_id: UUID,
    target_dashboard_id: UUID = Query(...),
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Clona widget para outro dashboard."""
    repo = WidgetRepository(db)
    widget = repo.get_by_id(widget_id, condominio_id)
    if not widget:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Widget nao encontrado",
        )
    return repo.clone(widget, target_dashboard_id, created_by=current_user.get("id"))


@router.get("/dashboards/{dashboard_id}/widgets", response_model=list[WidgetResponse])
async def get_dashboard_widgets(
    dashboard_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Lista widgets de um dashboard."""
    repo = WidgetRepository(db)
    return repo.get_by_dashboard(dashboard_id, condominio_id)


# =============================================================================
# KPI ENDPOINTS
# =============================================================================


@router.post("/kpis", response_model=KPIResponse, status_code=http_status.HTTP_201_CREATED)
async def create_kpi(
    data: KPICreate,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Cria novo KPI."""
    repo = KPIRepository(db)
    existing = repo.get_by_codigo(data.codigo, condominio_id)
    if existing:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"KPI com codigo {data.codigo} ja existe",
        )
    kpi = repo.create(condominio_id, data, current_user.get("id"))
    return kpi


@router.get("/kpis", response_model=list[KPIResponse])
async def list_kpis(
    condominio_id: UUID = Query(...),
    categoria: KPICategory | None = None,
    status: KPIStatus | None = None,
    alert_level: AlertLevel | None = None,
    show_in_summary: bool | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Lista KPIs com filtros."""
    repo = KPIRepository(db)
    filters = KPIFilters(
        categoria=categoria,
        status=status,
        alert_level=alert_level,
        show_in_summary=show_in_summary,
        search=search,
    )
    items, _ = repo.list_all(condominio_id, filters, skip, limit)
    return items


@router.get("/kpis/{kpi_id}", response_model=KPIResponse)
async def get_kpi(
    kpi_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Busca KPI por ID."""
    repo = KPIRepository(db)
    kpi = repo.get_by_id(kpi_id, condominio_id)
    if not kpi:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="KPI nao encontrado",
        )
    return kpi


@router.put("/kpis/{kpi_id}", response_model=KPIResponse)
async def update_kpi(
    kpi_id: UUID,
    data: KPIUpdate,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza KPI."""
    repo = KPIRepository(db)
    kpi = repo.get_by_id(kpi_id, condominio_id)
    if not kpi:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="KPI nao encontrado",
        )
    return repo.update(kpi, data, current_user.get("id"))


@router.delete("/kpis/{kpi_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_kpi(
    kpi_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Deleta KPI."""
    repo = KPIRepository(db)
    kpi = repo.get_by_id(kpi_id, condominio_id)
    if not kpi:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="KPI nao encontrado",
        )
    repo.delete(kpi)


@router.post("/kpis/{kpi_id}/calculate", response_model=KPIValue)
async def calculate_kpi(
    kpi_id: UUID,
    condominio_id: UUID = Query(...),
    save_history: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Calcula valor atual do KPI."""
    repo = KPIRepository(db)
    kpi = repo.get_by_id(kpi_id, condominio_id)
    if not kpi:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="KPI nao encontrado",
        )

    bi_service = BIService(db)
    new_value = bi_service.calculate_kpi(kpi, condominio_id)
    repo.update_value(kpi, new_value, save_history)

    return KPIValue(
        kpi_id=kpi_id,
        codigo=kpi.codigo,
        nome=kpi.nome,
        valor=kpi.valor_atual,
        valor_anterior=kpi.valor_anterior,
        variacao=kpi.variacao_percentual,
        trend=kpi.trend.value if kpi.trend else None,
        meta=kpi.meta_valor,
        meta_atingida=kpi.meta_atingida,
        alert_level=kpi.alert_level.value,
        formatted_value=kpi.format_value(),
        color=kpi.get_color_for_value(kpi.valor_atual) if hasattr(kpi, "get_color_for_value") else kpi.color,
        calculated_at=datetime.utcnow(),
    )


@router.get("/kpis/{kpi_id}/history", response_model=KPIHistory)
async def get_kpi_history(
    kpi_id: UUID,
    condominio_id: UUID = Query(...),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Busca historico de valores do KPI."""
    repo = KPIRepository(db)
    kpi = repo.get_by_id(kpi_id, condominio_id)
    if not kpi:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="KPI nao encontrado",
        )

    history = repo.get_history(kpi, days)

    values = [Decimal(str(h["value"])) for h in history]

    return KPIHistory(
        kpi_id=kpi_id,
        codigo=kpi.codigo,
        nome=kpi.nome,
        entries=[{"date": datetime.fromisoformat(h["date"]), "value": Decimal(str(h["value"]))} for h in history],
        min_value=min(values) if values else None,
        max_value=max(values) if values else None,
        avg_value=sum(values) / len(values) if values else None,
        trend=kpi.trend.value if kpi.trend else None,
        period_days=days,
    )


@router.get("/kpis/summary", response_model=list[KPIResponse])
async def get_kpis_summary(
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Lista KPIs para resumo."""
    repo = KPIRepository(db)
    return repo.get_summary(condominio_id)


@router.get("/kpis/alerts", response_model=list[KPIResponse])
async def get_kpis_alerts(
    condominio_id: UUID = Query(...),
    min_level: AlertLevel = Query(AlertLevel.WARNING),
    db: Session = Depends(get_db),
):
    """Lista KPIs em alerta."""
    repo = KPIRepository(db)
    return repo.get_alerts(condominio_id, min_level)


@router.get("/kpis/stats", response_model=KPISummary)
async def get_kpis_stats(
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Retorna estatisticas de KPIs."""
    repo = KPIRepository(db)
    return repo.get_stats(condominio_id)


@router.post("/kpis/calculate-all")
async def calculate_all_kpis(
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Calcula todos os KPIs pendentes."""
    repo = KPIRepository(db)
    bi_service = BIService(db)

    kpis = repo.get_needing_calculation(condominio_id)
    calculated = 0

    for kpi in kpis:
        try:
            new_value = bi_service.calculate_kpi(kpi, condominio_id)
            repo.update_value(kpi, new_value, save_history=True)
            calculated += 1
        except Exception as e:
            logger.warning(f"Erro ao calcular KPI {kpi}: {e}")

    return {"calculated": calculated, "total": len(kpis)}


# =============================================================================
# REPORT ENDPOINTS
# =============================================================================


@router.post("/reports", response_model=ReportResponse, status_code=http_status.HTTP_201_CREATED)
async def create_report(
    data: ReportCreate,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Cria novo relatorio agendado."""
    repo = ReportRepository(db)
    existing = repo.get_by_codigo(data.codigo, condominio_id)
    if existing:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Relatorio com codigo {data.codigo} ja existe",
        )
    report = repo.create(condominio_id, data, current_user.get("id"))
    return report


@router.get("/reports", response_model=list[ReportResponse])
async def list_reports(
    condominio_id: UUID = Query(...),
    tipo: ReportType | None = None,
    formato: ReportFormat | None = None,
    status: ReportStatus | None = None,
    frequencia: ReportFrequency | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Lista relatorios com filtros."""
    repo = ReportRepository(db)
    filters = ReportFilters(
        tipo=tipo,
        formato=formato,
        status=status,
        frequencia=frequencia,
        search=search,
    )
    items, _ = repo.list_all(condominio_id, filters, skip, limit)
    return items


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Busca relatorio por ID."""
    repo = ReportRepository(db)
    report = repo.get_by_id(report_id, condominio_id)
    if not report:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Relatorio nao encontrado",
        )
    return report


@router.put("/reports/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: UUID,
    data: ReportUpdate,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza relatorio."""
    repo = ReportRepository(db)
    report = repo.get_by_id(report_id, condominio_id)
    if not report:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Relatorio nao encontrado",
        )
    return repo.update(report, data, current_user.get("id"))


@router.delete("/reports/{report_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Deleta relatorio."""
    repo = ReportRepository(db)
    report = repo.get_by_id(report_id, condominio_id)
    if not report:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Relatorio nao encontrado",
        )
    repo.delete(report)


@router.post("/reports/{report_id}/pause", response_model=ReportResponse)
async def pause_report(
    report_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Pausa agendamento do relatorio."""
    repo = ReportRepository(db)
    report = repo.get_by_id(report_id, condominio_id)
    if not report:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Relatorio nao encontrado",
        )
    return repo.pause(report)


@router.post("/reports/{report_id}/resume", response_model=ReportResponse)
async def resume_report(
    report_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Retoma agendamento do relatorio."""
    repo = ReportRepository(db)
    report = repo.get_by_id(report_id, condominio_id)
    if not report:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Relatorio nao encontrado",
        )
    return repo.resume(report)


@router.post("/reports/{report_id}/execute")
async def execute_report_now(
    report_id: UUID,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Executa relatorio imediatamente."""
    repo = ReportRepository(db)
    report = repo.get_by_id(report_id, condominio_id)
    if not report:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Relatorio nao encontrado",
        )

    # Simula execucao
    repo.mark_executed(report, success=True)

    return {
        "report_id": str(report_id),
        "executed_at": datetime.utcnow().isoformat(),
        "success": True,
    }


@router.get("/reports/due", response_model=list[ReportResponse])
async def get_due_reports(
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Lista relatorios prontos para execucao."""
    repo = ReportRepository(db)
    return repo.get_due_reports(condominio_id)


# =============================================================================
# CACHE ENDPOINTS
# =============================================================================


@router.get("/cache/stats", response_model=CacheStats)
async def get_cache_stats(
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Retorna estatisticas do cache."""
    repo = CacheRepository(db)
    return repo.get_stats(condominio_id)


@router.post("/cache/invalidate")
async def invalidate_cache(
    data: CacheInvalidate,
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    """Invalida cache."""
    repo = CacheRepository(db)

    if data.invalidate_all:
        count = repo.invalidate_all(condominio_id)
    elif data.cache_keys:
        count = 0
        for key in data.cache_keys:
            if repo.invalidate(key, condominio_id):
                count += 1
    elif data.entity_type and data.entity_ids:
        count = 0
        for entity_id in data.entity_ids:
            count += repo.invalidate_by_entity(data.entity_type, entity_id, condominio_id)
    elif data.tipo:
        count = repo.invalidate_by_type(data.tipo, condominio_id)
    else:
        count = 0

    return {"invalidated": count}


@router.post("/cache/cleanup")
async def cleanup_cache(
    condominio_id: UUID = Query(...),
    older_than_hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """Limpa cache expirado."""
    repo = CacheRepository(db)
    count = repo.cleanup_expired(condominio_id, older_than_hours)
    return {"cleaned": count}


# =============================================================================
# ANALYTICS IA ENDPOINTS
# =============================================================================


@router.post("/analytics/anomalies")
async def detect_anomalies(
    values: list[Decimal],
    threshold: float = Query(2.0, ge=1.0, le=4.0),
    db: Session = Depends(get_db),
):
    """Detecta anomalias nos dados."""
    service = AnalyticsService(db)
    return service.detect_anomalies(values, threshold)


@router.post("/analytics/trend")
async def calculate_trend(
    values: list[Decimal],
    db: Session = Depends(get_db),
):
    """Calcula tendencia dos dados."""
    service = AnalyticsService(db)
    return service.calculate_trend(values)


@router.post("/analytics/distribution")
async def analyze_distribution(
    values: list[Decimal],
    db: Session = Depends(get_db),
):
    """Analisa distribuicao dos dados."""
    service = AnalyticsService(db)
    return service.analyze_distribution(values)


@router.post("/analytics/growth-rate")
async def calculate_growth_rate(
    values: list[Decimal],
    period: str = Query("monthly"),
    db: Session = Depends(get_db),
):
    """Calcula taxa de crescimento."""
    service = AnalyticsService(db)
    return service.calculate_growth_rate(values, period)


@router.post("/analytics/suggest-targets")
async def suggest_targets(
    historical_values: list[Decimal],
    growth_target: Decimal | None = None,
    db: Session = Depends(get_db),
):
    """Sugere metas baseado em historico."""
    service = AnalyticsService(db)
    return service.suggest_targets(historical_values, growth_target)


@router.post("/analytics/variance")
async def analyze_variance(
    actual: Decimal,
    budget: Decimal,
    description: str = "",
    db: Session = Depends(get_db),
):
    """Analisa variancia orcamento vs realizado."""
    service = AnalyticsService(db)
    return service.analyze_variance(actual, budget, description)


# =============================================================================
# FORECAST IA ENDPOINTS
# =============================================================================


@router.post("/forecast/generate")
async def generate_forecast(
    historical_values: list[Decimal],
    periods: int = Query(12, ge=1, le=60),
    db: Session = Depends(get_db),
):
    """Gera previsao com cenarios."""
    service = ForecastService(db)
    return service.generate_forecast(historical_values, periods)


@router.post("/forecast/moving-average")
async def moving_average_forecast(
    values: list[Decimal],
    window: int = Query(3, ge=2, le=12),
    periods: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db),
):
    """Previsao por media movel."""
    service = ForecastService(db)
    return service.moving_average_forecast(values, window, periods)


@router.post("/forecast/break-even")
async def calculate_break_even(
    fixed_costs: Decimal,
    variable_cost_per_unit: Decimal,
    price_per_unit: Decimal,
    db: Session = Depends(get_db),
):
    """Calcula ponto de equilibrio."""
    service = ForecastService(db)
    return service.calculate_break_even(fixed_costs, variable_cost_per_unit, price_per_unit)


@router.post("/forecast/cash-flow-projection")
async def project_cash_flow(
    opening_balance: Decimal,
    expected_inflows: list[Decimal],
    expected_outflows: list[Decimal],
    db: Session = Depends(get_db),
):
    """Projeta fluxo de caixa."""
    service = ForecastService(db)
    return service.cash_flow_projection(opening_balance, expected_inflows, expected_outflows)


@router.post("/forecast/npv")
async def calculate_npv(
    initial_investment: Decimal,
    cash_flows: list[Decimal],
    discount_rate: Decimal,
    db: Session = Depends(get_db),
):
    """Calcula Valor Presente Liquido."""
    service = ForecastService(db)
    return service.calculate_npv(initial_investment, cash_flows, discount_rate)


@router.post("/forecast/payback")
async def calculate_payback(
    initial_investment: Decimal,
    cash_flows: list[Decimal],
    db: Session = Depends(get_db),
):
    """Calcula periodo de payback."""
    service = ForecastService(db)
    return service.calculate_payback(initial_investment, cash_flows)


# =============================================================================
# SUMMARY ENDPOINTS
# =============================================================================


@router.get("/summary/financial")
async def get_financial_summary(
    condominio_id: UUID = Query(...),
    period_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Retorna resumo financeiro consolidado."""
    bi_service = BIService(db)
    return bi_service.get_financial_summary(condominio_id, period_days)


@router.get("/summary/compare")
async def compare_periods(
    condominio_id: UUID = Query(...),
    data_source: DataSource = Query(...),
    metric_field: str = Query(...),
    current_days: int = Query(30, ge=1, le=365),
    previous_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Compara metricas entre periodos."""
    bi_service = BIService(db)
    return bi_service.compare_periods(
        condominio_id,
        data_source,
        metric_field,
        current_days,
        previous_days,
    )
