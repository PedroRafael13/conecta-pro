"""
Repository de Rondas de Inspecao - Versao Async.

Author: Conecta PRO Team
Date: 2026-01-23
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, select, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import InspectionRound, InspectionRoundStatus, InspectionCheckpoint
from ..schemas import InspectionRoundFilter


class InspectionRoundRepository:
    """Repository para operacoes de banco de dados de Rondas de Inspecao."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, round_data: dict) -> InspectionRound:
        """Cria uma nova ronda."""
        inspection_round = InspectionRound(**round_data)
        self.db.add(inspection_round)
        await self.db.flush()
        await self.db.refresh(inspection_round)
        return inspection_round

    async def get_by_id(self, round_id: str) -> Optional[InspectionRound]:
        """Busca ronda por ID."""
        query = select(InspectionRound).where(
            InspectionRound.id == round_id,
            InspectionRound.is_active == True,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[InspectionRound]:
        """Busca ronda por codigo."""
        query = select(InspectionRound).where(
            InspectionRound.code == code,
            InspectionRound.is_active == True,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[InspectionRoundFilter] = None,
    ) -> Tuple[List[InspectionRound], int]:
        """Lista rondas com filtros e paginacao."""
        conditions = [
            InspectionRound.tenant_id == tenant_id,
            InspectionRound.is_active == True,
        ]

        if filters:
            if filters.inspector_id:
                conditions.append(InspectionRound.inspector_id == str(filters.inspector_id))
            if filters.inspector_role:
                conditions.append(InspectionRound.inspector_role == filters.inspector_role)
            if filters.status:
                conditions.append(InspectionRound.status == filters.status)
            if filters.start_date:
                conditions.append(InspectionRound.created_at >= filters.start_date)
            if filters.end_date:
                conditions.append(InspectionRound.created_at <= filters.end_date)
            if filters.has_occurrences is not None:
                if filters.has_occurrences:
                    conditions.append(InspectionRound.total_occurrences > 0)
                else:
                    conditions.append(InspectionRound.total_occurrences == 0)
            if filters.has_disciplinary_actions is not None:
                if filters.has_disciplinary_actions:
                    conditions.append(InspectionRound.total_disciplinary_actions > 0)
                else:
                    conditions.append(InspectionRound.total_disciplinary_actions == 0)

        # Count total
        count_query = select(func.count(InspectionRound.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one()

        # Get data
        query = (
            select(InspectionRound)
            .where(and_(*conditions))
            .order_by(InspectionRound.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        rounds = list(result.scalars().all())

        return rounds, total

    async def update(self, inspection_round: InspectionRound) -> InspectionRound:
        """Atualiza uma ronda."""
        await self.db.flush()
        await self.db.refresh(inspection_round)
        return inspection_round

    async def delete(self, inspection_round: InspectionRound) -> None:
        """Soft delete de uma ronda."""
        inspection_round.is_active = False
        await self.db.flush()

    async def get_next_sequence(self, tenant_id: str, year: int) -> int:
        """Retorna proximo numero sequencial para codigo."""
        query = select(func.count(InspectionRound.id)).where(
            InspectionRound.tenant_id == tenant_id,
            func.extract('year', InspectionRound.created_at) == year,
        )
        result = await self.db.execute(query)
        count = result.scalar_one()
        return (count or 0) + 1

    async def get_rounds_by_inspector(
        self,
        inspector_id: str,
        tenant_id: str,
        limit: int = 50,
    ) -> List[InspectionRound]:
        """Busca rondas de um inspetor."""
        query = (
            select(InspectionRound)
            .where(
                InspectionRound.inspector_id == inspector_id,
                InspectionRound.tenant_id == tenant_id,
                InspectionRound.is_active == True,
            )
            .order_by(InspectionRound.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_rounds_in_progress(self, tenant_id: str) -> List[InspectionRound]:
        """Retorna rondas em andamento."""
        query = select(InspectionRound).where(
            InspectionRound.tenant_id == tenant_id,
            InspectionRound.status == InspectionRoundStatus.EM_ANDAMENTO.value,
            InspectionRound.is_active == True,
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_rounds_scheduled_today(self, tenant_id: str) -> List[InspectionRound]:
        """Retorna rondas agendadas para hoje."""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)

        query = select(InspectionRound).where(
            InspectionRound.tenant_id == tenant_id,
            InspectionRound.status == InspectionRoundStatus.AGENDADA.value,
            InspectionRound.scheduled_date >= today_start,
            InspectionRound.scheduled_date <= today_end,
            InspectionRound.is_active == True,
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_status(self, tenant_id: str) -> dict:
        """Conta rondas por status."""
        query = (
            select(InspectionRound.status, func.count(InspectionRound.id))
            .where(
                InspectionRound.tenant_id == tenant_id,
                InspectionRound.is_active == True,
            )
            .group_by(InspectionRound.status)
        )
        result = await self.db.execute(query)
        return {status: count for status, count in result.all()}

    async def get_stats_by_inspector(self, tenant_id: str, limit: int = 10) -> List[dict]:
        """Retorna estatisticas por inspetor."""
        query = (
            select(
                InspectionRound.inspector_id,
                InspectionRound.inspector_name,
                InspectionRound.inspector_role,
                func.count(InspectionRound.id).label('total_rounds'),
                func.sum(InspectionRound.total_occurrences).label('total_occurrences'),
                func.sum(InspectionRound.total_disciplinary_actions).label('total_disciplinary_actions'),
                func.avg(InspectionRound.duration_minutes).label('avg_duration'),
                func.max(InspectionRound.created_at).label('last_round'),
            )
            .where(
                InspectionRound.tenant_id == tenant_id,
                InspectionRound.is_active == True,
            )
            .group_by(
                InspectionRound.inspector_id,
                InspectionRound.inspector_name,
                InspectionRound.inspector_role,
            )
            .order_by(func.count(InspectionRound.id).desc())
            .limit(limit)
        )
        result = await self.db.execute(query)

        return [
            {
                'inspector_id': r.inspector_id,
                'inspector_name': r.inspector_name,
                'inspector_role': r.inspector_role,
                'total_rounds': r.total_rounds,
                'total_occurrences': r.total_occurrences or 0,
                'total_disciplinary_actions': r.total_disciplinary_actions or 0,
                'avg_duration_minutes': float(r.avg_duration) if r.avg_duration else 0,
                'last_round_date': r.last_round,
            }
            for r in result.all()
        ]

    # ==========================================================================
    # CHECKPOINT OPERATIONS
    # ==========================================================================

    async def create_checkpoint(self, checkpoint_data: dict) -> InspectionCheckpoint:
        """Cria um novo checkpoint."""
        checkpoint = InspectionCheckpoint(**checkpoint_data)
        self.db.add(checkpoint)
        await self.db.flush()
        await self.db.refresh(checkpoint)
        return checkpoint

    async def get_checkpoint_by_id(self, checkpoint_id: str) -> Optional[InspectionCheckpoint]:
        """Busca checkpoint por ID."""
        query = select(InspectionCheckpoint).where(
            InspectionCheckpoint.id == checkpoint_id,
            InspectionCheckpoint.is_active == True,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_checkpoints_by_round(self, round_id: str) -> List[InspectionCheckpoint]:
        """Lista checkpoints de uma ronda."""
        query = (
            select(InspectionCheckpoint)
            .where(
                InspectionCheckpoint.inspection_round_id == round_id,
                InspectionCheckpoint.is_active == True,
            )
            .order_by(InspectionCheckpoint.sequence)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_checkpoint(self, checkpoint: InspectionCheckpoint) -> InspectionCheckpoint:
        """Atualiza um checkpoint."""
        await self.db.flush()
        await self.db.refresh(checkpoint)
        return checkpoint

    async def get_next_checkpoint_sequence(self, round_id: str) -> int:
        """Retorna proximo numero sequencial para checkpoint."""
        query = select(func.max(InspectionCheckpoint.sequence)).where(
            InspectionCheckpoint.inspection_round_id == round_id,
        )
        result = await self.db.execute(query)
        max_seq = result.scalar_one_or_none()
        return (max_seq or 0) + 1

    async def count_checkpoints_by_status(self, round_id: str) -> dict:
        """Conta checkpoints por status."""
        query = (
            select(InspectionCheckpoint.status, func.count(InspectionCheckpoint.id))
            .where(
                InspectionCheckpoint.inspection_round_id == round_id,
                InspectionCheckpoint.is_active == True,
            )
            .group_by(InspectionCheckpoint.status)
        )
        result = await self.db.execute(query)
        return {status: count for status, count in result.all()}
