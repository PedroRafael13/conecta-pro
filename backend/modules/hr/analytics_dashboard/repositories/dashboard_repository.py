"""Repository para DashboardConfig e DashboardWidget."""

import logging
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.hr.analytics_dashboard.models import (
    DashboardConfig,
    DashboardWidget,
    DashboardVisibility,
)
from modules.hr.analytics_dashboard.schemas import (
    DashboardConfigCreate,
    DashboardConfigUpdate,
    DashboardWidgetCreate,
    DashboardWidgetUpdate,
)

logger = logging.getLogger(__name__)


class DashboardRepository:
    """Repository para operações de dashboard."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== Dashboard Config ====================

    async def create_dashboard(
        self,
        data: DashboardConfigCreate,
        condominio_id: UUID,
        owner_id: UUID,
    ) -> DashboardConfig:
        """Cria novo dashboard."""
        dashboard = DashboardConfig(
            condominio_id=condominio_id,
            owner_id=owner_id,
            created_by=owner_id,
            **data.model_dump(exclude_unset=True),
        )
        self.db.add(dashboard)
        await self.db.commit()
        await self.db.refresh(dashboard)
        return dashboard

    async def get_dashboard_by_id(
        self,
        dashboard_id: UUID,
        include_widgets: bool = False,
    ) -> Optional[DashboardConfig]:
        """Busca dashboard por ID."""
        query = select(DashboardConfig).where(
            DashboardConfig.id == dashboard_id,
            DashboardConfig.is_active == True,  # noqa: E712
        )
        if include_widgets:
            query = query.options(selectinload(DashboardConfig.widgets))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_dashboard_by_slug(
        self,
        slug: str,
        condominio_id: UUID,
    ) -> Optional[DashboardConfig]:
        """Busca dashboard por slug."""
        query = select(DashboardConfig).where(
            DashboardConfig.slug == slug,
            DashboardConfig.condominio_id == condominio_id,
            DashboardConfig.is_active == True,  # noqa: E712
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_dashboards(
        self,
        condominio_id: UUID,
        user_id: UUID,
        user_role: str = None,
        department_id: UUID = None,
        dashboard_type: str = None,
        include_shared: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[DashboardConfig], int]:
        """Lista dashboards com filtros."""
        conditions = [
            DashboardConfig.condominio_id == condominio_id,
            DashboardConfig.is_active == True,  # noqa: E712
        ]

        # Filtrar por acesso
        access_conditions = [DashboardConfig.owner_id == user_id]

        if include_shared:
            access_conditions.extend([
                DashboardConfig.visibility == DashboardVisibility.PUBLIC.value,
                DashboardConfig.visibility == DashboardVisibility.ORGANIZATION.value,
            ])

        conditions.append(or_(*access_conditions))

        if dashboard_type:
            conditions.append(DashboardConfig.dashboard_type == dashboard_type)

        # Query principal
        query = (
            select(DashboardConfig)
            .where(and_(*conditions))
            .order_by(
                DashboardConfig.is_pinned.desc(),
                DashboardConfig.is_default.desc(),
                DashboardConfig.sort_order,
                DashboardConfig.name,
            )
        )

        # Contagem total
        count_query = select(func.count(DashboardConfig.id)).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Paginação
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        dashboards = result.scalars().all()

        return list(dashboards), total

    async def update_dashboard(
        self,
        dashboard_id: UUID,
        data: DashboardConfigUpdate,
    ) -> Optional[DashboardConfig]:
        """Atualiza dashboard."""
        dashboard = await self.get_dashboard_by_id(dashboard_id)
        if not dashboard:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(dashboard, field, value)

        dashboard.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(dashboard)
        return dashboard

    async def delete_dashboard(self, dashboard_id: UUID) -> bool:
        """Deleta dashboard (soft delete)."""
        stmt = (
            update(DashboardConfig)
            .where(DashboardConfig.id == dashboard_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def set_default_dashboard(
        self,
        dashboard_id: UUID,
        condominio_id: UUID,
        owner_id: UUID,
    ) -> None:
        """Define dashboard como padrão."""
        # Remover default de outros
        stmt = (
            update(DashboardConfig)
            .where(
                DashboardConfig.condominio_id == condominio_id,
                DashboardConfig.owner_id == owner_id,
                DashboardConfig.is_default == True,  # noqa: E712
            )
            .values(is_default=False)
        )
        await self.db.execute(stmt)

        # Definir novo default
        stmt = (
            update(DashboardConfig)
            .where(DashboardConfig.id == dashboard_id)
            .values(is_default=True)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def increment_view_count(self, dashboard_id: UUID) -> None:
        """Incrementa contador de visualizações."""
        stmt = (
            update(DashboardConfig)
            .where(DashboardConfig.id == dashboard_id)
            .values(
                view_count=DashboardConfig.view_count + 1,
                last_viewed_at=datetime.utcnow(),
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def clone_dashboard(
        self,
        source_id: UUID,
        new_name: str,
        owner_id: UUID,
        include_widgets: bool = True,
    ) -> Optional[DashboardConfig]:
        """Clona um dashboard."""
        source = await self.get_dashboard_by_id(source_id, include_widgets=True)
        if not source:
            return None

        # Gerar slug único
        import re
        base_slug = re.sub(r"[^a-zA-Z0-9]+", "-", new_name.lower()).strip("-")
        slug = f"{base_slug}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Criar cópia
        new_dashboard = DashboardConfig(
            condominio_id=source.condominio_id,
            owner_id=owner_id,
            created_by=owner_id,
            name=new_name,
            slug=slug,
            description=source.description,
            dashboard_type=source.dashboard_type,
            visibility=DashboardVisibility.PRIVATE.value,
            layout_type=source.layout_type,
            columns=source.columns,
            row_height=source.row_height,
            refresh_interval=source.refresh_interval,
            auto_refresh=source.auto_refresh,
            default_period=source.default_period,
            default_filters=source.default_filters,
            theme=source.theme,
            color_scheme=source.color_scheme,
            tags=source.tags,
            settings=source.settings,
        )
        self.db.add(new_dashboard)
        await self.db.flush()

        # Clonar widgets
        if include_widgets and source.widgets:
            for widget in source.widgets:
                new_widget = DashboardWidget(
                    dashboard_id=new_dashboard.id,
                    title=widget.title,
                    subtitle=widget.subtitle,
                    widget_type=widget.widget_type,
                    grid_x=widget.grid_x,
                    grid_y=widget.grid_y,
                    grid_width=widget.grid_width,
                    grid_height=widget.grid_height,
                    data_source=widget.data_source,
                    aggregation=widget.aggregation,
                    group_by=widget.group_by,
                    filters=widget.filters,
                    chart_config=widget.chart_config,
                    colors=widget.colors,
                    kpi_metric=widget.kpi_metric,
                    kpi_target=widget.kpi_target,
                    thresholds=widget.thresholds,
                    settings=widget.settings,
                )
                self.db.add(new_widget)

        await self.db.commit()
        await self.db.refresh(new_dashboard)
        return new_dashboard

    # ==================== Dashboard Widget ====================

    async def create_widget(
        self,
        dashboard_id: UUID,
        data: DashboardWidgetCreate,
    ) -> DashboardWidget:
        """Cria novo widget."""
        widget = DashboardWidget(
            dashboard_id=dashboard_id,
            **data.model_dump(exclude_unset=True),
        )
        self.db.add(widget)
        await self.db.commit()
        await self.db.refresh(widget)
        return widget

    async def get_widget_by_id(
        self,
        widget_id: UUID,
    ) -> Optional[DashboardWidget]:
        """Busca widget por ID."""
        query = select(DashboardWidget).where(
            DashboardWidget.id == widget_id,
            DashboardWidget.is_active == True,  # noqa: E712
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_widgets(
        self,
        dashboard_id: UUID,
        visible_only: bool = True,
    ) -> List[DashboardWidget]:
        """Lista widgets de um dashboard."""
        conditions = [
            DashboardWidget.dashboard_id == dashboard_id,
            DashboardWidget.is_active == True,  # noqa: E712
        ]
        if visible_only:
            conditions.append(DashboardWidget.is_visible == True)  # noqa: E712

        query = (
            select(DashboardWidget)
            .where(and_(*conditions))
            .order_by(DashboardWidget.grid_y, DashboardWidget.grid_x)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_widget(
        self,
        widget_id: UUID,
        data: DashboardWidgetUpdate,
    ) -> Optional[DashboardWidget]:
        """Atualiza widget."""
        widget = await self.get_widget_by_id(widget_id)
        if not widget:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(widget, field, value)

        widget.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(widget)
        return widget

    async def update_widget_positions(
        self,
        positions: List[dict],
    ) -> int:
        """Atualiza posições de múltiplos widgets."""
        updated = 0
        for pos in positions:
            stmt = (
                update(DashboardWidget)
                .where(DashboardWidget.id == pos["widget_id"])
                .values(
                    grid_x=pos["x"],
                    grid_y=pos["y"],
                    grid_width=pos["width"],
                    grid_height=pos["height"],
                    updated_at=datetime.utcnow(),
                )
            )
            result = await self.db.execute(stmt)
            updated += result.rowcount

        await self.db.commit()
        return updated

    async def delete_widget(self, widget_id: UUID) -> bool:
        """Deleta widget (soft delete)."""
        stmt = (
            update(DashboardWidget)
            .where(DashboardWidget.id == widget_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def delete_all_widgets(self, dashboard_id: UUID) -> int:
        """Deleta todos widgets de um dashboard."""
        stmt = (
            update(DashboardWidget)
            .where(DashboardWidget.dashboard_id == dashboard_id)
            .values(is_active=False)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def mark_widget_refreshed(self, widget_id: UUID) -> None:
        """Marca widget como atualizado."""
        stmt = (
            update(DashboardWidget)
            .where(DashboardWidget.id == widget_id)
            .values(last_refreshed_at=datetime.utcnow(), is_loading=False)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_widgets_needing_refresh(
        self,
        dashboard_id: UUID,
    ) -> List[DashboardWidget]:
        """Retorna widgets que precisam de refresh."""
        query = select(DashboardWidget).where(
            DashboardWidget.dashboard_id == dashboard_id,
            DashboardWidget.is_active == True,  # noqa: E712
            DashboardWidget.is_visible == True,  # noqa: E712
            or_(
                DashboardWidget.last_refreshed_at.is_(None),
                DashboardWidget.last_refreshed_at
                < func.now() - func.make_interval(0, 0, 0, 0, 0, 0, DashboardWidget.cache_duration_seconds),
            ),
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
