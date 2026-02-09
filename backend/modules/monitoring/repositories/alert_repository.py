"""
Repository para alertas.
"""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.alert import Alert, AlertLevel, AlertStatus


class AlertRepository:
    """Repository para operacoes com alertas."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, alert: Alert) -> Alert:
        """Cria um novo alerta."""
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def get_by_id(self, alert_id: UUID) -> Alert | None:
        """Busca alerta por ID."""
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active(
        self,
        level: AlertLevel | None = None,
        limit: int = 100,
    ) -> list[Alert]:
        """Busca alertas ativos."""
        stmt = select(Alert).where(
            Alert.status == AlertStatus.ACTIVE,
            Alert.is_active,
        )

        if level:
            stmt = stmt.where(Alert.level == level)

        stmt = stmt.order_by(Alert.triggered_at.desc()).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_metric(
        self,
        metric_name: str,
        limit: int = 50,
    ) -> list[Alert]:
        """Busca alertas por metrica."""
        stmt = (
            select(Alert)
            .where(
                Alert.metric_name == metric_name,
                Alert.is_active,
            )
            .order_by(Alert.triggered_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_recent(
        self,
        hours: int = 24,
        limit: int = 100,
    ) -> list[Alert]:
        """Busca alertas recentes."""
        threshold = datetime.utcnow() - timedelta(hours=hours)

        stmt = (
            select(Alert)
            .where(
                Alert.triggered_at >= threshold,
                Alert.is_active,
            )
            .order_by(Alert.triggered_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, alert: Alert) -> Alert:
        """Atualiza um alerta."""
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def count_by_level(
        self,
        hours: int = 24,
    ) -> dict:
        """Conta alertas por nivel."""
        threshold = datetime.utcnow() - timedelta(hours=hours)

        counts = {}
        for level in AlertLevel:
            stmt = select(func.count(Alert.id)).where(
                Alert.triggered_at >= threshold,
                Alert.level == level,
                Alert.is_active,
            )
            result = await self.db.execute(stmt)
            counts[level.value] = result.scalar() or 0

        return counts

    async def count_by_status(
        self,
        hours: int = 24,
    ) -> dict:
        """Conta alertas por status."""
        threshold = datetime.utcnow() - timedelta(hours=hours)

        counts = {}
        for status in AlertStatus:
            stmt = select(func.count(Alert.id)).where(
                Alert.triggered_at >= threshold,
                Alert.status == status,
                Alert.is_active,
            )
            result = await self.db.execute(stmt)
            counts[status.value] = result.scalar() or 0

        return counts

    async def get_unresolved_older_than(
        self,
        minutes: int,
    ) -> list[Alert]:
        """Busca alertas nao resolvidos mais antigos que X minutos."""
        threshold = datetime.utcnow() - timedelta(minutes=minutes)

        stmt = select(Alert).where(
            Alert.status == AlertStatus.ACTIVE,
            Alert.triggered_at < threshold,
            Alert.is_active,
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
