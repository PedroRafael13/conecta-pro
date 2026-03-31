"""Controller de BI e Dashboards Financeiros."""

import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status
from sqlalchemy.orm import Session

from core.auth.dependencies import get_current_user
from core.database.session import get_sync_db_dependency as get_db
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


@router.get("/kpis")
async def list_kpis(
    condominio_id: UUID = Query(...),
    categoria: KPICategory | None = None,
    status: KPIStatus | None = None,
    alert_level: AlertLevel | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lista KPIs com filtros (raw SQL para compatibilidade com schema atual)."""
    from sqlalchemy import text

    try:
        where_clauses = ["condominio_id = :condominio_id"]
        params: dict = {"condominio_id": str(condominio_id)}

        if categoria:
            where_clauses.append("categoria = :categoria")
            params["categoria"] = str(categoria)
        if status:
            where_clauses.append("status = :status")
            params["status"] = str(status)
        if alert_level:
            where_clauses.append("alert_level = :alert_level")
            params["alert_level"] = str(alert_level)
        if search:
            where_clauses.append("(nome ILIKE :search OR codigo ILIKE :search)")
            params["search"] = f"%{search}%"

        where_sql = " AND ".join(where_clauses)

        rows = db.execute(
            text(
                f"""
                SELECT id, condominio_id, codigo, nome, descricao,
                       categoria, status, frequencia, formula,
                       valor_atual, valor_anterior, variacao_percent,
                       tendencia, alert_level, meta_valor, historico,
                       ultima_atualizacao, created_at, updated_at
                FROM financial_kpis
                WHERE {where_sql}
                ORDER BY id
                OFFSET :skip LIMIT :limit
                """
            ),
            {**params, "skip": skip, "limit": limit},
        ).fetchall()

        result = []
        for row in rows:
            result.append(
                {
                    "id": str(row.id),
                    "condominio_id": str(row.condominio_id),
                    "codigo": row.codigo,
                    "nome": row.nome,
                    "descricao": row.descricao,
                    "categoria": row.categoria,
                    "status": row.status,
                    "frequencia": row.frequencia,
                    "formula": row.formula,
                    "valor_atual": float(row.valor_atual) if row.valor_atual is not None else None,
                    "valor_anterior": float(row.valor_anterior) if row.valor_anterior is not None else None,
                    "variacao_percent": float(row.variacao_percent) if row.variacao_percent is not None else None,
                    "tendencia": row.tendencia,
                    "alert_level": row.alert_level,
                    "meta_valor": float(row.meta_valor) if row.meta_valor is not None else None,
                    "ultima_atualizacao": row.ultima_atualizacao.isoformat() if row.ultima_atualizacao else None,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                }
            )

        return result
    except Exception as e:
        logger.error(f"Erro ao listar KPIs: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar KPIs: {str(e)}",
        )


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


# =============================================================================
# BI ANALYTICS ENDPOINTS (Frontend dashboard)
# =============================================================================


@router.get("/kpis-summary")
async def get_bi_kpis_summary(
    condominio_id: UUID = Query(...),
    period_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Retorna KPIs resumidos para o BI Dashboard."""
    from sqlalchemy import func

    try:
        from modules.financial.models.payable_account import PayableAccount
        from modules.financial.models.receivable_account import ReceivableAccount, ReceivableStatus

        cutoff = datetime.utcnow().date()

        total_receivable = db.query(func.coalesce(func.sum(ReceivableAccount.net_value), 0)).filter(
            ReceivableAccount.condominio_id == condominio_id,
            ReceivableAccount.status == ReceivableStatus.PENDENTE.value,
        ).scalar() or Decimal("0")

        overdue_receivable = db.query(func.coalesce(func.sum(ReceivableAccount.net_value), 0)).filter(
            ReceivableAccount.condominio_id == condominio_id,
            ReceivableAccount.status == ReceivableStatus.PENDENTE.value,
            ReceivableAccount.due_date < cutoff,
        ).scalar() or Decimal("0")

        total_payable = db.query(func.coalesce(func.sum(PayableAccount.net_value), 0)).filter(
            PayableAccount.condominio_id == condominio_id,
            PayableAccount.status == "pendente",
        ).scalar() or Decimal("0")

        return {
            "total_receivable": float(total_receivable),
            "overdue_receivable": float(overdue_receivable),
            "total_payable": float(total_payable),
            "default_rate": (float(overdue_receivable / total_receivable * 100) if total_receivable > 0 else 0.0),
            "period_days": period_days,
            "generated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.warning(f"Erro ao calcular KPIs BI: {e}")
        return {
            "total_receivable": 0.0,
            "overdue_receivable": 0.0,
            "total_payable": 0.0,
            "default_rate": 0.0,
            "period_days": period_days,
            "generated_at": datetime.utcnow().isoformat(),
        }


@router.get("/cashflow-analysis")
async def get_cashflow_analysis(
    condominio_id: UUID = Query(...),
    period_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Analise de fluxo de caixa para o periodo."""
    from sqlalchemy import func

    try:
        from modules.financial.models.cashflow_entry import CashFlowEntry, CashFlowEntryType

        start_date = datetime.utcnow().date()
        from datetime import timedelta

        end_date = start_date + timedelta(days=period_days)

        inflows = db.query(func.coalesce(func.sum(CashFlowEntry.expected_amount), 0)).filter(
            CashFlowEntry.condominio_id == condominio_id,
            CashFlowEntry.entry_type == CashFlowEntryType.ENTRADA.value,
            CashFlowEntry.entry_date >= start_date,
            CashFlowEntry.entry_date <= end_date,
        ).scalar() or Decimal("0")

        outflows = db.query(func.coalesce(func.sum(CashFlowEntry.expected_amount), 0)).filter(
            CashFlowEntry.condominio_id == condominio_id,
            CashFlowEntry.entry_type == CashFlowEntryType.SAIDA.value,
            CashFlowEntry.entry_date >= start_date,
            CashFlowEntry.entry_date <= end_date,
        ).scalar() or Decimal("0")

        return {
            "period_days": period_days,
            "total_inflows": float(inflows),
            "total_outflows": float(outflows),
            "net_cashflow": float(inflows) - float(outflows),
            "generated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.warning(f"Erro na analise de cashflow: {e}")
        return {
            "period_days": period_days,
            "total_inflows": 0.0,
            "total_outflows": 0.0,
            "net_cashflow": 0.0,
            "generated_at": datetime.utcnow().isoformat(),
        }


@router.get("/receivables-aging")
async def get_receivables_aging(
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Aging de contas a receber (vencidas por faixa)."""
    from datetime import timedelta

    from sqlalchemy import func

    try:
        from modules.financial.models.receivable_account import ReceivableAccount, ReceivableStatus

        today = datetime.utcnow().date()

        buckets = {
            "a_vencer": (None, today),
            "0_30": (today - timedelta(days=30), today),
            "31_60": (today - timedelta(days=60), today - timedelta(days=31)),
            "61_90": (today - timedelta(days=90), today - timedelta(days=61)),
            "acima_90": (None, today - timedelta(days=91)),
        }

        result = {}
        for label, (date_from, date_to) in buckets.items():
            q = db.query(
                func.count(ReceivableAccount.id),
                func.coalesce(func.sum(ReceivableAccount.net_value), 0),
            ).filter(
                ReceivableAccount.condominio_id == condominio_id,
                ReceivableAccount.status == ReceivableStatus.PENDENTE.value,
            )

            if label == "a_vencer":
                q = q.filter(ReceivableAccount.due_date >= today)
            elif label == "acima_90":
                q = q.filter(ReceivableAccount.due_date < date_to)
            else:
                q = q.filter(
                    ReceivableAccount.due_date >= date_from,
                    ReceivableAccount.due_date < date_to,
                )

            count, total = q.one()
            result[label] = {"count": count, "total": float(total)}

        result["generated_at"] = datetime.utcnow().isoformat()
        return result
    except Exception as e:
        logger.warning(f"Erro no aging de recebiveis: {e}")
        return {
            "a_vencer": {"count": 0, "total": 0.0},
            "0_30": {"count": 0, "total": 0.0},
            "31_60": {"count": 0, "total": 0.0},
            "61_90": {"count": 0, "total": 0.0},
            "acima_90": {"count": 0, "total": 0.0},
            "generated_at": datetime.utcnow().isoformat(),
        }


@router.get("/payables-aging")
async def get_payables_aging(
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Aging de contas a pagar (vencidas por faixa)."""
    from datetime import timedelta

    from sqlalchemy import func

    try:
        from modules.financial.models.payable_account import PayableAccount

        today = datetime.utcnow().date()

        buckets = {
            "a_vencer": "a_vencer",
            "0_30": (today - timedelta(days=30), today),
            "31_60": (today - timedelta(days=60), today - timedelta(days=31)),
            "61_90": (today - timedelta(days=90), today - timedelta(days=61)),
            "acima_90": "acima_90",
        }

        result = {}
        for label, spec in buckets.items():
            q = db.query(
                func.count(PayableAccount.id),
                func.coalesce(func.sum(PayableAccount.net_value), 0),
            ).filter(
                PayableAccount.condominio_id == condominio_id,
                PayableAccount.status == "pendente",
            )

            if label == "a_vencer":
                q = q.filter(PayableAccount.due_date >= today)
            elif label == "acima_90":
                q = q.filter(PayableAccount.due_date < today - timedelta(days=91))
            else:
                date_from, date_to = spec
                q = q.filter(
                    PayableAccount.due_date >= date_from,
                    PayableAccount.due_date < date_to,
                )

            count, total = q.one()
            result[label] = {"count": count, "total": float(total)}

        result["generated_at"] = datetime.utcnow().isoformat()
        return result
    except Exception as e:
        logger.warning(f"Erro no aging de pagaveis: {e}")
        return {
            "a_vencer": {"count": 0, "total": 0.0},
            "0_30": {"count": 0, "total": 0.0},
            "31_60": {"count": 0, "total": 0.0},
            "61_90": {"count": 0, "total": 0.0},
            "acima_90": {"count": 0, "total": 0.0},
            "generated_at": datetime.utcnow().isoformat(),
        }


@router.get("/cost-analysis")
async def get_cost_analysis(
    condominio_id: UUID = Query(...),
    period_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Analise de custos por categoria."""
    from datetime import timedelta

    from sqlalchemy import func

    try:
        from modules.financial.models.payable_account import PayableAccount

        cutoff = datetime.utcnow().date() - timedelta(days=period_days)

        count_q = (
            db.query(func.count(PayableAccount.id))
            .filter(
                PayableAccount.condominio_id == condominio_id,
                PayableAccount.due_date >= cutoff,
            )
            .scalar()
            or 0
        )

        total_q = db.query(func.coalesce(func.sum(PayableAccount.net_value), 0)).filter(
            PayableAccount.condominio_id == condominio_id,
            PayableAccount.due_date >= cutoff,
        ).scalar() or Decimal("0")

        return {
            "period_days": period_days,
            "total_invoices": count_q,
            "total_cost": float(total_q),
            "generated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.warning(f"Erro na analise de custos: {e}")
        return {
            "period_days": period_days,
            "categories": [],
            "total_cost": 0.0,
            "generated_at": datetime.utcnow().isoformat(),
        }


@router.get("/revenue-analysis")
async def get_revenue_analysis(
    condominio_id: UUID = Query(...),
    period_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Analise de receitas por categoria."""
    from datetime import timedelta

    from sqlalchemy import func

    try:
        from modules.financial.models.receivable_account import ReceivableAccount, ReceivableStatus

        cutoff = datetime.utcnow().date() - timedelta(days=period_days)

        total_billed = db.query(func.coalesce(func.sum(ReceivableAccount.gross_value), 0)).filter(
            ReceivableAccount.condominio_id == condominio_id,
            ReceivableAccount.due_date >= cutoff,
        ).scalar() or Decimal("0")

        total_received = db.query(func.coalesce(func.sum(ReceivableAccount.paid_value), 0)).filter(
            ReceivableAccount.condominio_id == condominio_id,
            ReceivableAccount.status == ReceivableStatus.PAGA.value,
            ReceivableAccount.due_date >= cutoff,
        ).scalar() or Decimal("0")

        return {
            "period_days": period_days,
            "total_billed": float(total_billed),
            "total_received": float(total_received),
            "collection_rate": (float(total_received / total_billed * 100) if total_billed > 0 else 0.0),
            "generated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.warning(f"Erro na analise de receitas: {e}")
        return {
            "period_days": period_days,
            "total_billed": 0.0,
            "total_received": 0.0,
            "collection_rate": 0.0,
            "generated_at": datetime.utcnow().isoformat(),
        }


@router.get("/profitability")
async def get_profitability(
    condominio_id: UUID = Query(...),
    period_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Analise de lucratividade do periodo."""
    from datetime import timedelta

    from sqlalchemy import func

    try:
        from modules.financial.models.payable_account import PayableAccount
        from modules.financial.models.receivable_account import ReceivableAccount, ReceivableStatus

        cutoff = datetime.utcnow().date() - timedelta(days=period_days)

        revenue = db.query(func.coalesce(func.sum(ReceivableAccount.paid_value), 0)).filter(
            ReceivableAccount.condominio_id == condominio_id,
            ReceivableAccount.status == ReceivableStatus.PAGA.value,
            ReceivableAccount.due_date >= cutoff,
        ).scalar() or Decimal("0")

        costs = db.query(func.coalesce(func.sum(PayableAccount.net_value), 0)).filter(
            PayableAccount.condominio_id == condominio_id,
            PayableAccount.status == "paga",
            PayableAccount.due_date >= cutoff,
        ).scalar() or Decimal("0")

        gross_profit = float(revenue) - float(costs)
        margin = (gross_profit / float(revenue) * 100) if float(revenue) > 0 else 0.0

        return {
            "period_days": period_days,
            "revenue": float(revenue),
            "costs": float(costs),
            "gross_profit": gross_profit,
            "margin_percent": margin,
            "generated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.warning(f"Erro na analise de lucratividade: {e}")
        return {
            "period_days": period_days,
            "revenue": 0.0,
            "costs": 0.0,
            "gross_profit": 0.0,
            "margin_percent": 0.0,
            "generated_at": datetime.utcnow().isoformat(),
        }


@router.get("/alerts")
async def get_bi_alerts(
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lista alertas financeiros ativos para o condominio."""
    from sqlalchemy import func

    alerts = []

    try:
        from modules.financial.models.receivable_account import ReceivableAccount, ReceivableStatus

        today = datetime.utcnow().date()

        overdue_count = (
            db.query(func.count(ReceivableAccount.id))
            .filter(
                ReceivableAccount.condominio_id == condominio_id,
                ReceivableAccount.status == ReceivableStatus.PENDENTE.value,
                ReceivableAccount.due_date < today,
            )
            .scalar()
            or 0
        )

        overdue_value = db.query(func.coalesce(func.sum(ReceivableAccount.net_value), 0)).filter(
            ReceivableAccount.condominio_id == condominio_id,
            ReceivableAccount.status == ReceivableStatus.PENDENTE.value,
            ReceivableAccount.due_date < today,
        ).scalar() or Decimal("0")

        if overdue_count > 0:
            level = "critico" if overdue_count > 10 else "alto" if overdue_count > 5 else "medio"
            alerts.append(
                {
                    "type": "inadimplencia",
                    "level": level,
                    "title": "Contas a receber vencidas",
                    "description": f"{overdue_count} titulos vencidos totalizando R$ {float(overdue_value):,.2f}",
                    "value": float(overdue_value),
                    "count": overdue_count,
                }
            )

    except Exception as e:
        logger.warning(f"Erro ao buscar alertas BI: {e}")

    return {"alerts": alerts, "total": len(alerts), "generated_at": datetime.utcnow().isoformat()}


@router.get("/performance-dashboard")
async def get_performance_dashboard(
    condominio_id: UUID = Query(...),
    period_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Dashboard consolidado de performance financeira."""
    from datetime import timedelta

    from sqlalchemy import func

    try:
        from modules.financial.models.payable_account import PayableAccount
        from modules.financial.models.receivable_account import ReceivableAccount, ReceivableStatus

        cutoff = datetime.utcnow().date() - timedelta(days=period_days)
        today = datetime.utcnow().date()

        total_receivable = db.query(func.coalesce(func.sum(ReceivableAccount.net_value), 0)).filter(
            ReceivableAccount.condominio_id == condominio_id,
            ReceivableAccount.status == ReceivableStatus.PENDENTE.value,
        ).scalar() or Decimal("0")

        overdue_receivable = db.query(func.coalesce(func.sum(ReceivableAccount.net_value), 0)).filter(
            ReceivableAccount.condominio_id == condominio_id,
            ReceivableAccount.status == ReceivableStatus.PENDENTE.value,
            ReceivableAccount.due_date < today,
        ).scalar() or Decimal("0")

        total_payable = db.query(func.coalesce(func.sum(PayableAccount.net_value), 0)).filter(
            PayableAccount.condominio_id == condominio_id,
            PayableAccount.status == "pendente",
        ).scalar() or Decimal("0")

        revenue = db.query(func.coalesce(func.sum(ReceivableAccount.paid_value), 0)).filter(
            ReceivableAccount.condominio_id == condominio_id,
            ReceivableAccount.status == ReceivableStatus.PAGA.value,
            ReceivableAccount.due_date >= cutoff,
        ).scalar() or Decimal("0")

        default_rate = float(overdue_receivable / total_receivable * 100) if float(total_receivable) > 0 else 0.0

        score = max(0, 100 - int(default_rate) - (10 if float(total_payable) > float(revenue) else 0))

        return {
            "period_days": period_days,
            "score": score,
            "total_receivable": float(total_receivable),
            "overdue_receivable": float(overdue_receivable),
            "total_payable": float(total_payable),
            "revenue_period": float(revenue),
            "default_rate": default_rate,
            "health": "excelente" if score >= 80 else "bom" if score >= 60 else "atencao" if score >= 40 else "critico",
            "generated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.warning(f"Erro no performance dashboard: {e}")
        return {
            "period_days": period_days,
            "score": 0,
            "total_receivable": 0.0,
            "overdue_receivable": 0.0,
            "total_payable": 0.0,
            "revenue_period": 0.0,
            "default_rate": 0.0,
            "health": "sem_dados",
            "generated_at": datetime.utcnow().isoformat(),
        }


@router.get("/trends")
async def get_financial_trends(
    condominio_id: UUID = Query(...),
    months: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Tendencias financeiras mensais."""
    from datetime import timedelta

    from sqlalchemy import func

    try:
        from modules.financial.models.receivable_account import ReceivableAccount, ReceivableStatus

        result = []
        today = datetime.utcnow().date()

        for i in range(months - 1, -1, -1):
            month_start = (today.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1)

            revenue = (
                db.query(func.coalesce(func.sum(ReceivableAccount.paid_value), 0))
                .filter(
                    ReceivableAccount.condominio_id == condominio_id,
                    ReceivableAccount.status == ReceivableStatus.PAGA.value,
                    ReceivableAccount.due_date >= month_start,
                    ReceivableAccount.due_date < month_end,
                )
                .scalar()
                or 0
            )

            result.append(
                {
                    "period": month_start.strftime("%Y-%m"),
                    "revenue": float(revenue),
                }
            )

        return {
            "months": months,
            "data": result,
            "generated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.warning(f"Erro nas tendencias financeiras: {e}")
        return {
            "months": months,
            "data": [],
            "generated_at": datetime.utcnow().isoformat(),
        }


@router.get("/comparison")
async def get_period_comparison(
    condominio_id: UUID = Query(...),
    current_period_days: int = Query(30, ge=1, le=365),
    previous_period_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Comparacao entre dois periodos financeiros."""
    from datetime import timedelta

    from sqlalchemy import func

    try:
        from modules.financial.models.receivable_account import ReceivableAccount, ReceivableStatus

        today = datetime.utcnow().date()
        current_start = today - timedelta(days=current_period_days)
        previous_start = current_start - timedelta(days=previous_period_days)
        previous_end = current_start

        current_revenue = db.query(func.coalesce(func.sum(ReceivableAccount.paid_value), 0)).filter(
            ReceivableAccount.condominio_id == condominio_id,
            ReceivableAccount.status == ReceivableStatus.PAGA.value,
            ReceivableAccount.due_date >= current_start,
            ReceivableAccount.due_date <= today,
        ).scalar() or Decimal("0")

        previous_revenue = db.query(func.coalesce(func.sum(ReceivableAccount.paid_value), 0)).filter(
            ReceivableAccount.condominio_id == condominio_id,
            ReceivableAccount.status == ReceivableStatus.PAGA.value,
            ReceivableAccount.due_date >= previous_start,
            ReceivableAccount.due_date < previous_end,
        ).scalar() or Decimal("0")

        variation = (
            float((current_revenue - previous_revenue) / previous_revenue * 100) if float(previous_revenue) > 0 else 0.0
        )

        return {
            "current_period": {
                "days": current_period_days,
                "start": current_start.isoformat(),
                "end": today.isoformat(),
                "revenue": float(current_revenue),
            },
            "previous_period": {
                "days": previous_period_days,
                "start": previous_start.isoformat(),
                "end": previous_end.isoformat(),
                "revenue": float(previous_revenue),
            },
            "variation_percent": variation,
            "trend": "up" if variation > 0 else "down" if variation < 0 else "stable",
            "generated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.warning(f"Erro na comparacao de periodos: {e}")
        return {
            "current_period": {"days": current_period_days, "revenue": 0.0},
            "previous_period": {"days": previous_period_days, "revenue": 0.0},
            "variation_percent": 0.0,
            "trend": "stable",
            "generated_at": datetime.utcnow().isoformat(),
        }
