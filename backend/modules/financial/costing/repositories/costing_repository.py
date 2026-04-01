"""Costing Repositories - CRUD e filtros para ABC e Rateio."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.financial.costing.models import (
    AllocationStatus,
    AnalysisStatus,
    CostActivity,
    CostAllocation,
    CostAnalysis,
    CostDriver,
    CostObject,
    CostPool,
    DriverStatus,
    PoolStatus,
)


class CostDriverRepository:
    """Repositório para Cost Driver."""

    def __init__(self, db: AsyncSession):
        """Inicializa repositório."""
        self.db = db

    async def create(self, driver: CostDriver) -> CostDriver:
        """Cria um novo driver."""
        self.db.add(driver)
        await self.db.commit()
        await self.db.refresh(driver)
        return driver

    async def get_by_id(self, driver_id: UUID, condominio_id: UUID) -> CostDriver | None:
        """Busca driver por ID."""
        result = await self.db.execute(
            select(CostDriver).where(
                and_(
                    CostDriver.id == driver_id,
                    CostDriver.condominio_id == condominio_id,
                    CostDriver.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str, condominio_id: UUID) -> CostDriver | None:
        """Busca driver por código."""
        result = await self.db.execute(
            select(CostDriver).where(
                and_(
                    CostDriver.code == code,
                    CostDriver.condominio_id == condominio_id,
                    CostDriver.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        condominio_id: UUID,
        skip: int = 0,
        limit: int = 100,
        driver_type: str = None,
        driver_category: str = None,
        status: str = None,
        is_automated: bool = None,
        active: bool = None,
        search: str = None,
    ) -> tuple[list[CostDriver], int]:
        """Lista drivers com filtros."""
        query = select(CostDriver).where(
            and_(
                CostDriver.condominio_id == condominio_id,
                CostDriver.deleted_at.is_(None),
            )
        )

        # Filtros
        if driver_type:
            query = query.where(CostDriver.driver_type == driver_type)
        if driver_category:
            query = query.where(CostDriver.driver_category == driver_category)
        if status:
            query = query.where(CostDriver.status == status)
        if is_automated is not None:
            query = query.where(CostDriver.is_automated == is_automated)
        if active is not None:
            query = query.where(CostDriver.active == active)
        if search:
            query = query.where(
                or_(
                    CostDriver.code.ilike(f"%{search}%"),
                    CostDriver.name.ilike(f"%{search}%"),
                )
            )

        # Count
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()

        # Pagination
        query = query.offset(skip).limit(limit).order_by(CostDriver.code)
        result = await self.db.execute(query)
        drivers = result.scalars().all()

        return list(drivers), total

    async def update(self, driver: CostDriver) -> CostDriver:
        """Atualiza driver."""
        driver.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(driver)
        return driver

    async def delete(self, driver: CostDriver, deleted_by: UUID = None) -> None:
        """Soft delete do driver."""
        driver.deleted_at = datetime.utcnow()
        driver.deleted_by = deleted_by
        driver.active = False
        await self.db.commit()

    async def get_stats(self, condominio_id: UUID) -> dict:
        """Estatísticas dos drivers."""
        result = await self.db.execute(
            select(
                func.count(CostDriver.id).label("total"),
                func.count(CostDriver.id).filter(CostDriver.status == DriverStatus.ACTIVE).label("active"),
                func.sum(CostDriver.total_allocated_amount).label("total_allocated"),
                func.avg(CostDriver.unit_cost).label("avg_unit_cost"),
            ).where(
                and_(
                    CostDriver.condominio_id == condominio_id,
                    CostDriver.deleted_at.is_(None),
                )
            )
        )
        row = result.one()
        return {
            "total": row.total or 0,
            "active": row.active or 0,
            "total_allocated": row.total_allocated or Decimal("0"),
            "avg_unit_cost": row.avg_unit_cost or Decimal("0"),
        }


class CostActivityRepository:
    """Repositório para Cost Activity."""

    def __init__(self, db: AsyncSession):
        """Inicializa repositório."""
        self.db = db

    async def create(self, activity: CostActivity) -> CostActivity:
        """Cria uma nova atividade."""
        self.db.add(activity)
        await self.db.commit()
        await self.db.refresh(activity)
        return activity

    async def get_by_id(self, activity_id: UUID, condominio_id: UUID) -> CostActivity | None:
        """Busca atividade por ID."""
        result = await self.db.execute(
            select(CostActivity)
            .options(selectinload(CostActivity.primary_driver))
            .options(selectinload(CostActivity.cost_pool))
            .where(
                and_(
                    CostActivity.id == activity_id,
                    CostActivity.condominio_id == condominio_id,
                    CostActivity.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str, condominio_id: UUID) -> CostActivity | None:
        """Busca atividade por código."""
        result = await self.db.execute(
            select(CostActivity).where(
                and_(
                    CostActivity.code == code,
                    CostActivity.condominio_id == condominio_id,
                    CostActivity.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_all(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        skip: int = 0,
        limit: int = 100,
        activity_type: str = None,
        activity_level: str = None,
        status: str = None,
        value_added_type: str = None,
        cost_pool_id: UUID = None,
        cost_center_id: UUID = None,
        is_core: bool = None,
        active: bool = None,
        search: str = None,
    ) -> tuple[list[CostActivity], int]:
        """Lista atividades com filtros."""
        query = select(CostActivity).where(
            and_(
                CostActivity.condominio_id == condominio_id,
                CostActivity.deleted_at.is_(None),
            )
        )

        # Filtros
        if activity_type:
            query = query.where(CostActivity.activity_type == activity_type)
        if activity_level:
            query = query.where(CostActivity.activity_level == activity_level)
        if status:
            query = query.where(CostActivity.status == status)
        if value_added_type:
            query = query.where(CostActivity.value_added_type == value_added_type)
        if cost_pool_id:
            query = query.where(CostActivity.cost_pool_id == cost_pool_id)
        if cost_center_id:
            query = query.where(CostActivity.cost_center_id == cost_center_id)
        if is_core is not None:
            query = query.where(CostActivity.is_core == is_core)
        if active is not None:
            query = query.where(CostActivity.active == active)
        if search:
            query = query.where(
                or_(
                    CostActivity.code.ilike(f"%{search}%"),
                    CostActivity.name.ilike(f"%{search}%"),
                )
            )

        # Count
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()

        # Pagination
        query = query.offset(skip).limit(limit).order_by(CostActivity.code)
        result = await self.db.execute(query)
        activities = result.scalars().all()

        return list(activities), total

    async def get_tree(self, condominio_id: UUID) -> list[CostActivity]:
        """Retorna árvore hierárquica de atividades."""
        result = await self.db.execute(
            select(CostActivity)
            .where(
                and_(
                    CostActivity.condominio_id == condominio_id,
                    CostActivity.deleted_at.is_(None),
                )
            )
            .order_by(CostActivity.path, CostActivity.order_index)
        )
        return list(result.scalars().all())

    async def update(self, activity: CostActivity) -> CostActivity:
        """Atualiza atividade."""
        activity.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(activity)
        return activity

    async def delete(self, activity: CostActivity, deleted_by: UUID = None) -> None:
        """Soft delete da atividade."""
        activity.deleted_at = datetime.utcnow()
        activity.deleted_by = deleted_by
        activity.active = False
        await self.db.commit()

    async def get_by_pool(self, pool_id: UUID, condominio_id: UUID) -> list[CostActivity]:
        """Busca atividades por pool."""
        result = await self.db.execute(
            select(CostActivity).where(
                and_(
                    CostActivity.cost_pool_id == pool_id,
                    CostActivity.condominio_id == condominio_id,
                    CostActivity.deleted_at.is_(None),
                )
            )
        )
        return list(result.scalars().all())


class CostPoolRepository:
    """Repositório para Cost Pool."""

    def __init__(self, db: AsyncSession):
        """Inicializa repositório."""
        self.db = db

    async def create(self, pool: CostPool) -> CostPool:
        """Cria um novo pool."""
        self.db.add(pool)
        await self.db.commit()
        await self.db.refresh(pool)
        return pool

    async def get_by_id(self, pool_id: UUID, condominio_id: UUID) -> CostPool | None:
        """Busca pool por ID."""
        result = await self.db.execute(
            select(CostPool).where(
                and_(
                    CostPool.id == pool_id,
                    CostPool.condominio_id == condominio_id,
                    CostPool.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str, condominio_id: UUID) -> CostPool | None:
        """Busca pool por código."""
        result = await self.db.execute(
            select(CostPool).where(
                and_(
                    CostPool.code == code,
                    CostPool.condominio_id == condominio_id,
                    CostPool.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_all(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        skip: int = 0,
        limit: int = 100,
        pool_type: str = None,
        status: str = None,
        allocation_basis: str = None,
        cost_center_id: UUID = None,
        is_homogeneous: bool = None,
        active: bool = None,
        search: str = None,
    ) -> tuple[list[CostPool], int]:
        """Lista pools com filtros."""
        query = select(CostPool).where(
            and_(
                CostPool.condominio_id == condominio_id,
                CostPool.deleted_at.is_(None),
            )
        )

        # Filtros
        if pool_type:
            query = query.where(CostPool.pool_type == pool_type)
        if status:
            query = query.where(CostPool.status == status)
        if allocation_basis:
            query = query.where(CostPool.allocation_basis == allocation_basis)
        if cost_center_id:
            query = query.where(CostPool.cost_center_id == cost_center_id)
        if is_homogeneous is not None:
            query = query.where(CostPool.is_homogeneous == is_homogeneous)
        if active is not None:
            query = query.where(CostPool.active == active)
        if search:
            query = query.where(
                or_(
                    CostPool.code.ilike(f"%{search}%"),
                    CostPool.name.ilike(f"%{search}%"),
                )
            )

        # Count
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()

        # Pagination
        query = query.offset(skip).limit(limit).order_by(CostPool.code)
        result = await self.db.execute(query)
        pools = result.scalars().all()

        return list(pools), total

    async def update(self, pool: CostPool) -> CostPool:
        """Atualiza pool."""
        pool.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(pool)
        return pool

    async def delete(self, pool: CostPool, deleted_by: UUID = None) -> None:
        """Soft delete do pool."""
        pool.deleted_at = datetime.utcnow()
        pool.deleted_by = deleted_by
        pool.active = False
        await self.db.commit()

    async def get_with_unallocated(self, condominio_id: UUID) -> list[CostPool]:
        """Busca pools com custo não alocado."""
        result = await self.db.execute(
            select(CostPool).where(
                and_(
                    CostPool.condominio_id == condominio_id,
                    CostPool.deleted_at.is_(None),
                    CostPool.status == PoolStatus.ACTIVE,
                    CostPool.unallocated_cost > 0,
                )
            )
        )
        return list(result.scalars().all())


class CostObjectRepository:
    """Repositório para Cost Object."""

    def __init__(self, db: AsyncSession):
        """Inicializa repositório."""
        self.db = db

    async def create(self, obj: CostObject) -> CostObject:
        """Cria um novo objeto de custo."""
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get_by_id(self, object_id: UUID, condominio_id: UUID) -> CostObject | None:
        """Busca objeto por ID."""
        result = await self.db.execute(
            select(CostObject).where(
                and_(
                    CostObject.id == object_id,
                    CostObject.condominio_id == condominio_id,
                    CostObject.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str, condominio_id: UUID) -> CostObject | None:
        """Busca objeto por código."""
        result = await self.db.execute(
            select(CostObject).where(
                and_(
                    CostObject.code == code,
                    CostObject.condominio_id == condominio_id,
                    CostObject.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_all(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        skip: int = 0,
        limit: int = 100,
        object_type: str = None,
        status: str = None,
        profitability_level: str = None,
        category: str = None,
        is_strategic: bool = None,
        is_profitable: bool = None,
        active: bool = None,
        search: str = None,
    ) -> tuple[list[CostObject], int]:
        """Lista objetos com filtros."""
        query = select(CostObject).where(
            and_(
                CostObject.condominio_id == condominio_id,
                CostObject.deleted_at.is_(None),
            )
        )

        # Filtros
        if object_type:
            query = query.where(CostObject.object_type == object_type)
        if status:
            query = query.where(CostObject.status == status)
        if profitability_level:
            query = query.where(CostObject.profitability_level == profitability_level)
        if category:
            query = query.where(CostObject.category == category)
        if is_strategic is not None:
            query = query.where(CostObject.is_strategic == is_strategic)
        if is_profitable is True:
            query = query.where(CostObject.net_margin > 0)
        elif is_profitable is False:
            query = query.where(CostObject.net_margin <= 0)
        if active is not None:
            query = query.where(CostObject.active == active)
        if search:
            query = query.where(
                or_(
                    CostObject.code.ilike(f"%{search}%"),
                    CostObject.name.ilike(f"%{search}%"),
                )
            )

        # Count
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()

        # Pagination
        query = query.offset(skip).limit(limit).order_by(CostObject.code)
        result = await self.db.execute(query)
        objects = result.scalars().all()

        return list(objects), total

    async def update(self, obj: CostObject) -> CostObject:
        """Atualiza objeto."""
        obj.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: CostObject, deleted_by: UUID = None) -> None:
        """Soft delete do objeto."""
        obj.deleted_at = datetime.utcnow()
        obj.deleted_by = deleted_by
        obj.active = False
        await self.db.commit()

    async def get_profitability_ranking(self, condominio_id: UUID, limit: int = 10) -> list[CostObject]:
        """Ranking de rentabilidade."""
        result = await self.db.execute(
            select(CostObject)
            .where(
                and_(
                    CostObject.condominio_id == condominio_id,
                    CostObject.deleted_at.is_(None),
                    CostObject.active.is_(True),
                )
            )
            .order_by(CostObject.net_margin_percent.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_unprofitable(self, condominio_id: UUID) -> list[CostObject]:
        """Objetos não rentáveis."""
        result = await self.db.execute(
            select(CostObject).where(
                and_(
                    CostObject.condominio_id == condominio_id,
                    CostObject.deleted_at.is_(None),
                    CostObject.active.is_(True),
                    CostObject.net_margin < 0,
                )
            )
        )
        return list(result.scalars().all())


class CostAllocationRepository:
    """Repositório para Cost Allocation."""

    def __init__(self, db: AsyncSession):
        """Inicializa repositório."""
        self.db = db

    async def create(self, allocation: CostAllocation) -> CostAllocation:
        """Cria uma nova alocação."""
        # Gera número sequencial
        result = await self.db.execute(
            select(func.count(CostAllocation.id)).where(CostAllocation.condominio_id == allocation.condominio_id)
        )
        count = result.scalar_one() + 1
        allocation.allocation_number = f"ALLOC-{datetime.utcnow().strftime('%Y%m')}-{count:06d}"

        self.db.add(allocation)
        await self.db.commit()
        await self.db.refresh(allocation)
        return allocation

    async def create_batch(self, allocations: list[CostAllocation]) -> list[CostAllocation]:
        """Cria lote de alocações."""
        _batch_id = allocations[0].batch_id if allocations else None  # Reserved
        for i, allocation in enumerate(allocations):
            allocation.batch_sequence = i + 1
            result = await self.db.execute(
                select(func.count(CostAllocation.id)).where(CostAllocation.condominio_id == allocation.condominio_id)
            )
            count = result.scalar_one() + 1
            allocation.allocation_number = f"ALLOC-{datetime.utcnow().strftime('%Y%m')}-{count:06d}"
            self.db.add(allocation)

        await self.db.commit()
        for allocation in allocations:
            await self.db.refresh(allocation)
        return allocations

    async def get_by_id(self, allocation_id: UUID, condominio_id: UUID) -> CostAllocation | None:
        """Busca alocação por ID."""
        result = await self.db.execute(
            select(CostAllocation)
            .options(selectinload(CostAllocation.activity))
            .options(selectinload(CostAllocation.cost_object))
            .options(selectinload(CostAllocation.driver))
            .where(
                and_(
                    CostAllocation.id == allocation_id,
                    CostAllocation.condominio_id == condominio_id,
                    CostAllocation.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, allocation_number: str, condominio_id: UUID) -> CostAllocation | None:
        """Busca alocação por número."""
        result = await self.db.execute(
            select(CostAllocation).where(
                and_(
                    CostAllocation.allocation_number == allocation_number,
                    CostAllocation.condominio_id == condominio_id,
                    CostAllocation.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_all(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        skip: int = 0,
        limit: int = 100,
        allocation_type: str = None,
        status: str = None,
        allocation_method: str = None,
        source_pool_id: UUID = None,
        activity_id: UUID = None,
        cost_object_id: UUID = None,
        driver_id: UUID = None,
        reference_period: str = None,
        batch_id: UUID = None,
        is_reversed: bool = None,
        is_posted: bool = None,
        active: bool = None,
    ) -> tuple[list[CostAllocation], int]:
        """Lista alocações com filtros."""
        query = select(CostAllocation).where(
            and_(
                CostAllocation.condominio_id == condominio_id,
                CostAllocation.deleted_at.is_(None),
            )
        )

        # Filtros
        if allocation_type:
            query = query.where(CostAllocation.allocation_type == allocation_type)
        if status:
            query = query.where(CostAllocation.status == status)
        if allocation_method:
            query = query.where(CostAllocation.allocation_method == allocation_method)
        if source_pool_id:
            query = query.where(CostAllocation.source_pool_id == source_pool_id)
        if activity_id:
            query = query.where(CostAllocation.activity_id == activity_id)
        if cost_object_id:
            query = query.where(CostAllocation.cost_object_id == cost_object_id)
        if driver_id:
            query = query.where(CostAllocation.driver_id == driver_id)
        if reference_period:
            query = query.where(CostAllocation.reference_period == reference_period)
        if batch_id:
            query = query.where(CostAllocation.batch_id == batch_id)
        if is_reversed is not None:
            query = query.where(CostAllocation.is_reversed == is_reversed)
        if is_posted is not None:
            query = query.where(CostAllocation.is_posted == is_posted)
        if active is not None:
            query = query.where(CostAllocation.active == active)

        # Count
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()

        # Pagination
        query = query.offset(skip).limit(limit).order_by(CostAllocation.allocation_date.desc())
        result = await self.db.execute(query)
        allocations = result.scalars().all()

        return list(allocations), total

    async def update(self, allocation: CostAllocation) -> CostAllocation:
        """Atualiza alocação."""
        allocation.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(allocation)
        return allocation

    async def get_pending(self, condominio_id: UUID) -> list[CostAllocation]:
        """Busca alocações pendentes de aprovação."""
        result = await self.db.execute(
            select(CostAllocation).where(
                and_(
                    CostAllocation.condominio_id == condominio_id,
                    CostAllocation.deleted_at.is_(None),
                    CostAllocation.status == AllocationStatus.PENDING,
                )
            )
        )
        return list(result.scalars().all())

    async def get_by_period(self, condominio_id: UUID, period: str) -> list[CostAllocation]:
        """Busca alocações por período."""
        result = await self.db.execute(
            select(CostAllocation).where(
                and_(
                    CostAllocation.condominio_id == condominio_id,
                    CostAllocation.deleted_at.is_(None),
                    CostAllocation.reference_period == period,
                    CostAllocation.is_reversed.is_(False),
                )
            )
        )
        return list(result.scalars().all())

    async def get_summary_by_period(self, condominio_id: UUID, period: str) -> dict:
        """Resumo de alocações por período."""
        result = await self.db.execute(
            select(
                func.count(CostAllocation.id).label("total"),
                func.sum(CostAllocation.allocated_amount).label("total_amount"),
                func.count(CostAllocation.id)
                .filter(CostAllocation.status == AllocationStatus.PENDING)
                .label("pending"),
                func.sum(CostAllocation.allocated_amount)
                .filter(CostAllocation.status == AllocationStatus.PENDING)
                .label("pending_amount"),
            ).where(
                and_(
                    CostAllocation.condominio_id == condominio_id,
                    CostAllocation.deleted_at.is_(None),
                    CostAllocation.reference_period == period,
                    CostAllocation.is_reversed.is_(False),
                )
            )
        )
        row = result.one()
        return {
            "period": period,
            "total_allocations": row.total or 0,
            "total_amount": row.total_amount or Decimal("0"),
            "pending_count": row.pending or 0,
            "pending_amount": row.pending_amount or Decimal("0"),
        }


class CostAnalysisRepository:
    """Repositório para Cost Analysis."""

    def __init__(self, db: AsyncSession):
        """Inicializa repositório."""
        self.db = db

    async def create(self, analysis: CostAnalysis) -> CostAnalysis:
        """Cria uma nova análise."""
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis

    async def get_by_id(self, analysis_id: UUID, condominio_id: UUID) -> CostAnalysis | None:
        """Busca análise por ID."""
        result = await self.db.execute(
            select(CostAnalysis).where(
                and_(
                    CostAnalysis.id == analysis_id,
                    CostAnalysis.condominio_id == condominio_id,
                    CostAnalysis.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str, condominio_id: UUID) -> CostAnalysis | None:
        """Busca análise por código."""
        result = await self.db.execute(
            select(CostAnalysis).where(
                and_(
                    CostAnalysis.code == code,
                    CostAnalysis.condominio_id == condominio_id,
                    CostAnalysis.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_all(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        skip: int = 0,
        limit: int = 100,
        analysis_type: str = None,
        status: str = None,
        scope: str = None,
        is_scheduled: bool = None,
        is_template: bool = None,
        is_favorite: bool = None,
        active: bool = None,
        search: str = None,
    ) -> tuple[list[CostAnalysis], int]:
        """Lista análises com filtros."""
        query = select(CostAnalysis).where(
            and_(
                CostAnalysis.condominio_id == condominio_id,
                CostAnalysis.deleted_at.is_(None),
            )
        )

        # Filtros
        if analysis_type:
            query = query.where(CostAnalysis.analysis_type == analysis_type)
        if status:
            query = query.where(CostAnalysis.status == status)
        if scope:
            query = query.where(CostAnalysis.scope == scope)
        if is_scheduled is not None:
            query = query.where(CostAnalysis.is_scheduled == is_scheduled)
        if is_template is not None:
            query = query.where(CostAnalysis.is_template == is_template)
        if is_favorite is not None:
            query = query.where(CostAnalysis.is_favorite == is_favorite)
        if active is not None:
            query = query.where(CostAnalysis.active == active)
        if search:
            query = query.where(
                or_(
                    CostAnalysis.code.ilike(f"%{search}%"),
                    CostAnalysis.name.ilike(f"%{search}%"),
                )
            )

        # Count
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()

        # Pagination
        query = query.offset(skip).limit(limit).order_by(CostAnalysis.created_at.desc())
        result = await self.db.execute(query)
        analyses = result.scalars().all()

        return list(analyses), total

    async def update(self, analysis: CostAnalysis) -> CostAnalysis:
        """Atualiza análise."""
        analysis.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis

    async def delete(self, analysis: CostAnalysis, deleted_by: UUID = None) -> None:
        """Soft delete da análise."""
        analysis.deleted_at = datetime.utcnow()
        analysis.deleted_by = deleted_by
        analysis.active = False
        await self.db.commit()

    async def get_scheduled(self, condominio_id: UUID = None) -> list[CostAnalysis]:
        """Busca análises agendadas."""
        query = select(CostAnalysis).where(
            and_(
                CostAnalysis.deleted_at.is_(None),
                CostAnalysis.is_scheduled.is_(True),
                CostAnalysis.status != AnalysisStatus.ARCHIVED,
            )
        )
        if condominio_id:
            query = query.where(CostAnalysis.condominio_id == condominio_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_templates(self, condominio_id: UUID) -> list[CostAnalysis]:
        """Busca templates de análise."""
        result = await self.db.execute(
            select(CostAnalysis).where(
                and_(
                    CostAnalysis.condominio_id == condominio_id,
                    CostAnalysis.deleted_at.is_(None),
                    CostAnalysis.is_template.is_(True),
                )
            )
        )
        return list(result.scalars().all())
