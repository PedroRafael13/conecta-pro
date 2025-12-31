"""Service para gerenciamento de dashboards."""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.analytics_dashboard.models import (
    DashboardConfig,
    DashboardWidget,
    DataSource,
    AggregationType,
)
from modules.hr.analytics_dashboard.repositories import (
    DashboardRepository,
    CacheRepository,
)
from modules.hr.analytics_dashboard.schemas import (
    DashboardConfigCreate,
    DashboardConfigUpdate,
    DashboardWidgetCreate,
    DashboardWidgetUpdate,
    WidgetDataResponse,
)
from modules.hr.analytics_dashboard.services.metrics_aggregator_service import (
    MetricsAggregatorService,
)
from modules.hr.analytics_dashboard.services.kpi_calculator_service import (
    KPICalculatorService,
)

logger = logging.getLogger(__name__)


class DashboardService:
    """Service para operações de dashboard."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.dashboard_repo = DashboardRepository(db)
        self.cache_repo = CacheRepository(db)
        self.metrics_service = MetricsAggregatorService(db)
        self.kpi_service = KPICalculatorService(db)

    # ==================== Dashboard Operations ====================

    async def create_dashboard(
        self,
        data: DashboardConfigCreate,
        condominio_id: UUID,
        owner_id: UUID,
    ) -> DashboardConfig:
        """Cria novo dashboard."""
        dashboard = await self.dashboard_repo.create_dashboard(
            data=data,
            condominio_id=condominio_id,
            owner_id=owner_id,
        )
        logger.info("Dashboard criado: %s - %s", dashboard.id, dashboard.name)
        return dashboard

    async def get_dashboard(
        self,
        dashboard_id: UUID,
        user_id: UUID,
        include_widgets: bool = True,
        record_view: bool = True,
    ) -> Optional[DashboardConfig]:
        """Obtém dashboard com verificação de acesso."""
        dashboard = await self.dashboard_repo.get_dashboard_by_id(
            dashboard_id=dashboard_id,
            include_widgets=include_widgets,
        )

        if not dashboard:
            return None

        if not dashboard.can_view(user_id):
            logger.warning("Acesso negado ao dashboard %s para usuário %s", dashboard_id, user_id)
            return None

        if record_view:
            await self.dashboard_repo.increment_view_count(dashboard_id)

        return dashboard

    async def list_user_dashboards(
        self,
        condominio_id: UUID,
        user_id: UUID,
        *,
        user_role: str = None,
        department_id: UUID = None,
        dashboard_type: str = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple:
        """Lista dashboards do usuário."""
        return await self.dashboard_repo.list_dashboards(
            condominio_id=condominio_id,
            user_id=user_id,
            user_role=user_role,
            department_id=department_id,
            dashboard_type=dashboard_type,
            page=page,
            page_size=page_size,
        )

    async def update_dashboard(
        self,
        dashboard_id: UUID,
        data: DashboardConfigUpdate,
        user_id: UUID,
    ) -> Optional[DashboardConfig]:
        """Atualiza dashboard com verificação de permissão."""
        dashboard = await self.dashboard_repo.get_dashboard_by_id(dashboard_id)

        if not dashboard or not dashboard.can_edit(user_id):
            return None

        return await self.dashboard_repo.update_dashboard(dashboard_id, data)

    async def delete_dashboard(
        self,
        dashboard_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Deleta dashboard com verificação de permissão."""
        dashboard = await self.dashboard_repo.get_dashboard_by_id(dashboard_id)

        if not dashboard or not dashboard.can_edit(user_id):
            return False

        # Invalidar cache dos widgets
        widgets = await self.dashboard_repo.list_widgets(dashboard_id)
        for widget in widgets:
            await self.cache_repo.invalidate_by_widget(widget.id)

        return await self.dashboard_repo.delete_dashboard(dashboard_id)

    async def clone_dashboard(
        self,
        source_id: UUID,
        new_name: str,
        user_id: UUID,
        include_widgets: bool = True,
    ) -> Optional[DashboardConfig]:
        """Clona dashboard."""
        source = await self.dashboard_repo.get_dashboard_by_id(source_id)

        if not source or not source.can_view(user_id):
            return None

        return await self.dashboard_repo.clone_dashboard(
            source_id=source_id,
            new_name=new_name,
            owner_id=user_id,
            include_widgets=include_widgets,
        )

    async def set_default_dashboard(
        self,
        dashboard_id: UUID,
        user_id: UUID,
        condominio_id: UUID,
    ) -> bool:
        """Define dashboard como padrão do usuário."""
        dashboard = await self.dashboard_repo.get_dashboard_by_id(dashboard_id)

        if not dashboard or not dashboard.can_view(user_id):
            return False

        await self.dashboard_repo.set_default_dashboard(
            dashboard_id=dashboard_id,
            condominio_id=condominio_id,
            owner_id=user_id,
        )
        return True

    # ==================== Widget Operations ====================

    async def add_widget(
        self,
        dashboard_id: UUID,
        data: DashboardWidgetCreate,
        user_id: UUID,
    ) -> Optional[DashboardWidget]:
        """Adiciona widget ao dashboard."""
        dashboard = await self.dashboard_repo.get_dashboard_by_id(dashboard_id)

        if not dashboard or not dashboard.can_edit(user_id):
            return None

        widget = await self.dashboard_repo.create_widget(dashboard_id, data)
        logger.info("Widget adicionado: %s ao dashboard %s", widget.id, dashboard_id)
        return widget

    async def update_widget(
        self,
        widget_id: UUID,
        data: DashboardWidgetUpdate,
        user_id: UUID,
    ) -> Optional[DashboardWidget]:
        """Atualiza widget."""
        widget = await self.dashboard_repo.get_widget_by_id(widget_id)
        if not widget:
            return None

        dashboard = await self.dashboard_repo.get_dashboard_by_id(widget.dashboard_id)
        if not dashboard or not dashboard.can_edit(user_id):
            return None

        # Invalidar cache do widget
        await self.cache_repo.invalidate_by_widget(widget_id)

        return await self.dashboard_repo.update_widget(widget_id, data)

    async def remove_widget(
        self,
        widget_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Remove widget do dashboard."""
        widget = await self.dashboard_repo.get_widget_by_id(widget_id)
        if not widget:
            return False

        dashboard = await self.dashboard_repo.get_dashboard_by_id(widget.dashboard_id)
        if not dashboard or not dashboard.can_edit(user_id):
            return False

        await self.cache_repo.invalidate_by_widget(widget_id)
        return await self.dashboard_repo.delete_widget(widget_id)

    async def update_widget_positions(
        self,
        dashboard_id: UUID,
        positions: List[dict],
        user_id: UUID,
    ) -> bool:
        """Atualiza posições de múltiplos widgets."""
        dashboard = await self.dashboard_repo.get_dashboard_by_id(dashboard_id)

        if not dashboard or not dashboard.can_edit(user_id):
            return False

        await self.dashboard_repo.update_widget_positions(positions)
        return True

    async def get_widget_data(
        self,
        widget_id: UUID,
        user_id: UUID,
        filters: dict = None,
        force_refresh: bool = False,
    ) -> Optional[WidgetDataResponse]:
        """Obtém dados de um widget."""
        widget = await self.dashboard_repo.get_widget_by_id(widget_id)
        if not widget:
            return None

        dashboard = await self.dashboard_repo.get_dashboard_by_id(widget.dashboard_id)
        if not dashboard or not dashboard.can_view(user_id):
            return None

        # Combinar filtros
        combined_filters = {}
        if widget.inherit_dashboard_filters and dashboard.default_filters:
            combined_filters.update(dashboard.default_filters)
        if widget.filters:
            combined_filters.update(widget.filters)
        if filters:
            combined_filters.update(filters)

        # Calcular dados baseado no tipo
        if widget.kpi_metric:
            # Widget de KPI
            kpi_data = await self.kpi_service.calculate_kpi(
                kpi_code=widget.kpi_metric,
                condominio_id=dashboard.condominio_id,
                filters=combined_filters,
                use_cache=not force_refresh,
            )
            data = kpi_data.model_dump(mode="json")
            from_cache = kpi_data.from_cache
        else:
            # Widget de agregação
            data_source = DataSource(widget.data_source)
            aggregation = AggregationType(widget.aggregation)

            result = await self.metrics_service.aggregate_data(
                data_source=data_source,
                aggregation=aggregation,
                condominio_id=dashboard.condominio_id,
                group_by=widget.group_by,
                filters=combined_filters,
                limit=widget.limit,
                use_cache=not force_refresh,
            )
            data = result
            from_cache = False  # Simplificação

        # Marcar widget como atualizado
        await self.dashboard_repo.mark_widget_refreshed(widget_id)

        return WidgetDataResponse(
            widget_id=widget_id,
            data=data,
            metadata={
                "widget_type": widget.widget_type,
                "data_source": widget.data_source,
            },
            computed_at=datetime.utcnow(),
            from_cache=from_cache,
            cache_expires_at=None,
        )

    async def refresh_dashboard_data(
        self,
        dashboard_id: UUID,
        user_id: UUID,
    ) -> Dict[str, Any]:
        """Atualiza dados de todos os widgets do dashboard."""
        dashboard = await self.dashboard_repo.get_dashboard_by_id(dashboard_id)

        if not dashboard or not dashboard.can_view(user_id):
            return {"error": "Dashboard não encontrado ou sem acesso"}

        widgets = await self.dashboard_repo.list_widgets(dashboard_id)

        results = {
            "dashboard_id": str(dashboard_id),
            "widgets_refreshed": 0,
            "widgets_failed": 0,
            "details": [],
        }

        for widget in widgets:
            try:
                await self.get_widget_data(
                    widget_id=widget.id,
                    user_id=user_id,
                    force_refresh=True,
                )
                results["widgets_refreshed"] += 1
                results["details"].append({
                    "widget_id": str(widget.id),
                    "status": "success",
                })
            except Exception as e:
                results["widgets_failed"] += 1
                results["details"].append({
                    "widget_id": str(widget.id),
                    "status": "failed",
                    "error": str(e),
                })

        return results

    async def get_dashboard_templates(
        self,
        condominio_id: UUID = None,
    ) -> List[DashboardConfig]:
        """Retorna templates de dashboard disponíveis."""
        dashboards, _ = await self.dashboard_repo.list_dashboards(
            condominio_id=condominio_id,
            user_id=None,  # Templates são públicos
            page_size=100,
        )
        return [d for d in dashboards if d.is_template]
