"""Repository para KPIDefinition."""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.analytics_dashboard.models import (
    DEFAULT_KPIS,
    KPICategory,
    KPIDefinition,
)
from modules.hr.analytics_dashboard.schemas import (
    KPIDefinitionCreate,
    KPIDefinitionUpdate,
)

logger = logging.getLogger(__name__)


class KPIRepository:
    """Repository para operações de KPI."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_kpi(
        self,
        data: KPIDefinitionCreate,
        condominio_id: UUID = None,
        created_by: UUID = None,
    ) -> KPIDefinition:
        """Cria novo KPI."""
        kpi = KPIDefinition(
            condominio_id=condominio_id,
            created_by=created_by,
            **data.model_dump(exclude_unset=True),
        )
        self.db.add(kpi)
        await self.db.commit()
        await self.db.refresh(kpi)
        return kpi

    async def get_kpi_by_id(self, kpi_id: UUID) -> KPIDefinition | None:
        """Busca KPI por ID."""
        query = select(KPIDefinition).where(
            KPIDefinition.id == kpi_id,
            KPIDefinition.is_active.is_(True),
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_kpi_by_code(
        self,
        code: str,
        condominio_id: UUID = None,
    ) -> KPIDefinition | None:
        """Busca KPI por código."""
        conditions = [
            KPIDefinition.code == code.upper(),
            KPIDefinition.is_active.is_(True),
        ]

        # Buscar KPI específico do condomínio ou global
        if condominio_id:
            conditions.append(
                or_(
                    KPIDefinition.condominio_id == condominio_id,
                    KPIDefinition.condominio_id.is_(None),
                )
            )
        else:
            conditions.append(KPIDefinition.condominio_id.is_(None))

        query = select(KPIDefinition).where(and_(*conditions)).order_by(KPIDefinition.condominio_id.desc().nulls_last())
        result = await self.db.execute(query)
        return result.scalars().first()

    async def list_kpis(
        self,
        condominio_id: UUID = None,
        category: KPICategory = None,
        featured_only: bool = False,
        include_system: bool = True,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[KPIDefinition], int]:
        """Lista KPIs com filtros."""
        conditions = [KPIDefinition.is_active.is_(True)]

        if condominio_id:
            conditions.append(
                or_(
                    KPIDefinition.condominio_id == condominio_id,
                    KPIDefinition.condominio_id.is_(None),
                )
            )
        else:
            conditions.append(KPIDefinition.condominio_id.is_(None))

        if category:
            conditions.append(KPIDefinition.category == category.value)

        if featured_only:
            conditions.append(KPIDefinition.is_featured.is_(True))

        if not include_system:
            conditions.append(KPIDefinition.is_system.is_(False))

        # Query principal
        query = (
            select(KPIDefinition)
            .where(and_(*conditions))
            .order_by(
                KPIDefinition.is_featured.desc(),
                KPIDefinition.sort_order,
                KPIDefinition.name,
            )
        )

        # Contagem total
        count_query = select(func.count(KPIDefinition.id)).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Paginação
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        kpis = result.scalars().all()

        return list(kpis), total

    async def list_kpis_by_category(
        self,
        condominio_id: UUID = None,
    ) -> dict:
        """Lista KPIs agrupados por categoria."""
        kpis, _ = await self.list_kpis(condominio_id=condominio_id, page_size=200)

        grouped = {}
        for kpi in kpis:
            category = kpi.category
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(kpi)

        return grouped

    async def update_kpi(
        self,
        kpi_id: UUID,
        data: KPIDefinitionUpdate,
    ) -> KPIDefinition | None:
        """Atualiza KPI."""
        kpi = await self.get_kpi_by_id(kpi_id)
        if not kpi:
            return None

        # Não permitir editar KPIs de sistema
        if kpi.is_system:
            logger.warning(f"Tentativa de editar KPI de sistema: {kpi.code}")
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(kpi, field, value)

        kpi.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(kpi)
        return kpi

    async def delete_kpi(self, kpi_id: UUID) -> bool:
        """Deleta KPI (soft delete)."""
        kpi = await self.get_kpi_by_id(kpi_id)
        if not kpi or kpi.is_system:
            return False

        stmt = (
            update(KPIDefinition)
            .where(KPIDefinition.id == kpi_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def set_featured(
        self,
        kpi_id: UUID,
        is_featured: bool,
    ) -> KPIDefinition | None:
        """Define KPI como destaque."""
        stmt = (
            update(KPIDefinition)
            .where(KPIDefinition.id == kpi_id)
            .values(is_featured=is_featured, updated_at=datetime.utcnow())
        )
        await self.db.execute(stmt)
        await self.db.commit()
        return await self.get_kpi_by_id(kpi_id)

    async def reorder_kpis(
        self,
        kpi_orders: list[dict],
    ) -> int:
        """Reordena KPIs."""
        updated = 0
        for order in kpi_orders:
            stmt = (
                update(KPIDefinition).where(KPIDefinition.id == order["kpi_id"]).values(sort_order=order["sort_order"])
            )
            result = await self.db.execute(stmt)
            updated += result.rowcount

        await self.db.commit()
        return updated

    async def seed_default_kpis(self) -> int:
        """Cria KPIs padrão se não existirem."""
        created = 0
        for kpi_data in DEFAULT_KPIS:
            existing = await self.get_kpi_by_code(kpi_data["code"])
            if not existing:
                kpi = KPIDefinition(
                    is_system=True,
                    **kpi_data,
                )
                self.db.add(kpi)
                created += 1

        if created > 0:
            await self.db.commit()
            logger.info(f"Criados {created} KPIs padrão")

        return created

    async def get_kpi_codes(
        self,
        condominio_id: UUID = None,
    ) -> list[str]:
        """Retorna lista de códigos de KPI."""
        conditions = [KPIDefinition.is_active.is_(True)]

        if condominio_id:
            conditions.append(
                or_(
                    KPIDefinition.condominio_id == condominio_id,
                    KPIDefinition.condominio_id.is_(None),
                )
            )

        query = select(KPIDefinition.code).where(and_(*conditions))
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def clone_kpi_for_condominio(
        self,
        kpi_code: str,
        condominio_id: UUID,
        created_by: UUID = None,
    ) -> KPIDefinition | None:
        """Clona KPI global para customização do condomínio."""
        source = await self.get_kpi_by_code(kpi_code)
        if not source:
            return None

        # Verificar se já existe customização
        existing = await self.get_kpi_by_code(kpi_code, condominio_id)
        if existing and existing.condominio_id == condominio_id:
            return existing

        new_kpi = KPIDefinition(
            condominio_id=condominio_id,
            created_by=created_by,
            code=source.code,
            name=source.name,
            description=source.description,
            category=source.category,
            unit=source.unit,
            decimal_places=source.decimal_places,
            direction=source.direction,
            target_value=source.target_value,
            threshold_critical=source.threshold_critical,
            threshold_warning=source.threshold_warning,
            threshold_good=source.threshold_good,
            threshold_excellent=source.threshold_excellent,
            frequency=source.frequency,
            default_chart_type=source.default_chart_type,
            is_system=False,
        )
        self.db.add(new_kpi)
        await self.db.commit()
        await self.db.refresh(new_kpi)
        return new_kpi
