"""
Repository para thresholds.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.metric_threshold import MetricThreshold


class ThresholdRepository:
    """Repository para operacoes com thresholds."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, threshold: MetricThreshold) -> MetricThreshold:
        """Cria um novo threshold."""
        self.db.add(threshold)
        await self.db.commit()
        await self.db.refresh(threshold)
        return threshold

    async def get_by_id(self, threshold_id: UUID) -> Optional[MetricThreshold]:
        """Busca threshold por ID."""
        stmt = select(MetricThreshold).where(MetricThreshold.id == threshold_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_metric_name(self, metric_name: str) -> Optional[MetricThreshold]:
        """Busca threshold por nome da metrica."""
        stmt = select(MetricThreshold).where(
            MetricThreshold.metric_name == metric_name,
            MetricThreshold.is_active == True,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        enabled_only: bool = False,
        category: Optional[str] = None,
    ) -> List[MetricThreshold]:
        """Busca todos os thresholds."""
        stmt = select(MetricThreshold).where(MetricThreshold.is_active == True)

        if enabled_only:
            stmt = stmt.where(MetricThreshold.enabled == True)

        if category:
            stmt = stmt.where(MetricThreshold.category == category)

        stmt = stmt.order_by(MetricThreshold.category, MetricThreshold.metric_name)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_enabled(self) -> List[MetricThreshold]:
        """Busca thresholds habilitados."""
        return await self.get_all(enabled_only=True)

    async def get_categories(self) -> List[str]:
        """Retorna lista de categorias unicas."""
        stmt = (
            select(MetricThreshold.category)
            .where(MetricThreshold.is_active == True)
            .distinct()
        )
        result = await self.db.execute(stmt)
        return [row[0] for row in result.all()]

    async def update(self, threshold: MetricThreshold) -> MetricThreshold:
        """Atualiza um threshold."""
        await self.db.commit()
        await self.db.refresh(threshold)
        return threshold

    async def delete(self, threshold_id: UUID) -> bool:
        """Desativa um threshold (soft delete)."""
        threshold = await self.get_by_id(threshold_id)
        if not threshold:
            return False

        threshold.is_active = False
        await self.db.commit()
        return True

    async def exists(self, metric_name: str) -> bool:
        """Verifica se threshold existe para metrica."""
        threshold = await self.get_by_metric_name(metric_name)
        return threshold is not None
