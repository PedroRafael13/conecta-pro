"""Repository de Dashboard Financeiro."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session, joinedload

from modules.financial.bi_dashboard.models.dashboard_config import (
    FinancialDashboard,
    DashboardType,
    DashboardStatus,
)
from modules.financial.bi_dashboard.schemas.dashboard_schemas import (
    DashboardCreate,
    DashboardUpdate,
    DashboardFilters,
    DashboardStats,
)


class DashboardRepository:
    """Repository para operacoes de Dashboard."""

    def __init__(self, db: Session):
        """Inicializa repository."""
        self.db = db

    def create(
        self,
        condominio_id: UUID,
        data: DashboardCreate,
        created_by: UUID = None,
    ) -> FinancialDashboard:
        """Cria novo dashboard."""
        dashboard = FinancialDashboard(
            condominio_id=condominio_id,
            codigo=data.codigo,
            nome=data.nome,
            descricao=data.descricao,
            tipo=data.tipo,
            layout=data.layout,
            refresh_interval=data.refresh_interval,
            is_public=data.is_public,
            is_default=data.is_default,
            theme=data.theme,
            primary_color=data.primary_color,
            background_color=data.background_color,
            custom_css=data.custom_css,
            default_period_days=data.default_period_days,
            default_filters=data.default_filters,
            available_filters=data.available_filters,
            allowed_roles=data.allowed_roles,
            allowed_users=data.allowed_users,
            tags=data.tags,
            created_by=created_by,
            owner_id=created_by,
        )
        self.db.add(dashboard)
        self.db.commit()
        self.db.refresh(dashboard)
        return dashboard

    def get_by_id(
        self,
        dashboard_id: UUID,
        condominio_id: UUID = None,
        include_widgets: bool = False,
    ) -> Optional[FinancialDashboard]:
        """Busca dashboard por ID."""
        query = self.db.query(FinancialDashboard).filter(
            FinancialDashboard.id == dashboard_id,
            FinancialDashboard.deleted_at.is_(None),
        )
        if condominio_id:
            query = query.filter(FinancialDashboard.condominio_id == condominio_id)
        if include_widgets:
            query = query.options(joinedload(FinancialDashboard.widgets))
        return query.first()

    def get_by_codigo(
        self,
        codigo: str,
        condominio_id: UUID,
    ) -> Optional[FinancialDashboard]:
        """Busca dashboard por codigo."""
        return self.db.query(FinancialDashboard).filter(
            FinancialDashboard.codigo == codigo,
            FinancialDashboard.condominio_id == condominio_id,
            FinancialDashboard.deleted_at.is_(None),
        ).first()

    def list_all(
        self,
        condominio_id: UUID,
        filters: DashboardFilters = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[FinancialDashboard], int]:
        """Lista dashboards com filtros."""
        query = self.db.query(FinancialDashboard).filter(
            FinancialDashboard.condominio_id == condominio_id,
            FinancialDashboard.deleted_at.is_(None),
        )

        if filters:
            if filters.tipo:
                query = query.filter(FinancialDashboard.tipo == filters.tipo)
            if filters.status:
                query = query.filter(FinancialDashboard.status == filters.status)
            if filters.is_public is not None:
                query = query.filter(FinancialDashboard.is_public == filters.is_public)
            if filters.is_favorite is not None:
                query = query.filter(
                    FinancialDashboard.is_favorite == filters.is_favorite
                )
            if filters.owner_id:
                query = query.filter(FinancialDashboard.owner_id == filters.owner_id)
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        FinancialDashboard.nome.ilike(search_term),
                        FinancialDashboard.descricao.ilike(search_term),
                        FinancialDashboard.codigo.ilike(search_term),
                    )
                )
            if filters.created_after:
                query = query.filter(
                    FinancialDashboard.created_at >= filters.created_after
                )
            if filters.created_before:
                query = query.filter(
                    FinancialDashboard.created_at <= filters.created_before
                )

        total = query.count()
        items = (
            query.order_by(desc(FinancialDashboard.is_favorite))
            .order_by(desc(FinancialDashboard.last_viewed_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return items, total

    def update(
        self,
        dashboard: FinancialDashboard,
        data: DashboardUpdate,
        updated_by: UUID = None,
    ) -> FinancialDashboard:
        """Atualiza dashboard."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(dashboard, field, value)

        dashboard.updated_by = updated_by
        dashboard.last_modified_at = datetime.utcnow()
        dashboard.version += 1

        self.db.commit()
        self.db.refresh(dashboard)
        return dashboard

    def delete(self, dashboard: FinancialDashboard) -> bool:
        """Soft delete de dashboard."""
        dashboard.deleted_at = datetime.utcnow()
        dashboard.status = DashboardStatus.ARCHIVED
        self.db.commit()
        return True

    def hard_delete(self, dashboard: FinancialDashboard) -> bool:
        """Hard delete de dashboard."""
        self.db.delete(dashboard)
        self.db.commit()
        return True

    def get_default(self, condominio_id: UUID) -> Optional[FinancialDashboard]:
        """Busca dashboard padrao."""
        return self.db.query(FinancialDashboard).filter(
            FinancialDashboard.condominio_id == condominio_id,
            FinancialDashboard.is_default == True,
            FinancialDashboard.status == DashboardStatus.ACTIVE,
            FinancialDashboard.deleted_at.is_(None),
        ).first()

    def set_default(
        self,
        dashboard: FinancialDashboard,
        condominio_id: UUID,
    ) -> FinancialDashboard:
        """Define dashboard como padrao."""
        # Remove padrao anterior
        self.db.query(FinancialDashboard).filter(
            FinancialDashboard.condominio_id == condominio_id,
            FinancialDashboard.is_default == True,
        ).update({"is_default": False})

        dashboard.is_default = True
        self.db.commit()
        self.db.refresh(dashboard)
        return dashboard

    def toggle_favorite(
        self,
        dashboard: FinancialDashboard,
    ) -> FinancialDashboard:
        """Alterna favorito."""
        dashboard.is_favorite = not dashboard.is_favorite
        self.db.commit()
        self.db.refresh(dashboard)
        return dashboard

    def record_view(self, dashboard: FinancialDashboard) -> FinancialDashboard:
        """Registra visualizacao."""
        dashboard.increment_view()
        self.db.commit()
        self.db.refresh(dashboard)
        return dashboard

    def get_stats(self, condominio_id: UUID) -> DashboardStats:
        """Retorna estatisticas de dashboards."""
        base_query = self.db.query(FinancialDashboard).filter(
            FinancialDashboard.condominio_id == condominio_id,
            FinancialDashboard.deleted_at.is_(None),
        )

        total = base_query.count()
        active = base_query.filter(
            FinancialDashboard.status == DashboardStatus.ACTIVE
        ).count()
        draft = base_query.filter(
            FinancialDashboard.status == DashboardStatus.DRAFT
        ).count()
        archived = base_query.filter(
            FinancialDashboard.status == DashboardStatus.ARCHIVED
        ).count()
        public = base_query.filter(FinancialDashboard.is_public == True).count()
        private = base_query.filter(FinancialDashboard.is_public == False).count()

        total_views = base_query.with_entities(
            func.sum(FinancialDashboard.view_count)
        ).scalar() or 0

        most_viewed = base_query.order_by(
            desc(FinancialDashboard.view_count)
        ).first()

        by_type = {}
        for tipo in DashboardType:
            count = base_query.filter(FinancialDashboard.tipo == tipo).count()
            if count > 0:
                by_type[tipo.value] = count

        return DashboardStats(
            total=total,
            active=active,
            draft=draft,
            archived=archived,
            public=public,
            private=private,
            total_views=int(total_views),
            most_viewed={
                "id": str(most_viewed.id),
                "nome": most_viewed.nome,
                "views": most_viewed.view_count,
            } if most_viewed else None,
            by_type=by_type,
        )

    def get_user_dashboards(
        self,
        condominio_id: UUID,
        user_id: UUID,
        user_role: str,
    ) -> list[FinancialDashboard]:
        """Lista dashboards acessiveis pelo usuario."""
        return self.db.query(FinancialDashboard).filter(
            FinancialDashboard.condominio_id == condominio_id,
            FinancialDashboard.status == DashboardStatus.ACTIVE,
            FinancialDashboard.deleted_at.is_(None),
            or_(
                FinancialDashboard.is_public == True,
                FinancialDashboard.owner_id == user_id,
                FinancialDashboard.allowed_users.contains([str(user_id)]),
                FinancialDashboard.allowed_roles.contains([user_role]),
            ),
        ).order_by(
            desc(FinancialDashboard.is_favorite),
            desc(FinancialDashboard.last_viewed_at),
        ).all()

    def duplicate(
        self,
        dashboard: FinancialDashboard,
        new_name: str,
        new_codigo: str = None,
        created_by: UUID = None,
    ) -> FinancialDashboard:
        """Duplica dashboard."""
        new_dashboard = dashboard.duplicate(new_name)
        if new_codigo:
            new_dashboard.codigo = new_codigo
        new_dashboard.created_by = created_by
        new_dashboard.owner_id = created_by

        self.db.add(new_dashboard)
        self.db.commit()
        self.db.refresh(new_dashboard)
        return new_dashboard
