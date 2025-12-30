"""
Repository para operações de banco de dados com Scale.
"""

import calendar
from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.operations.models.scale import Scale, ScaleStatus
from modules.operations.schemas.scale import ScaleCreate, ScaleFilter, ScaleUpdate


class ScaleRepository:
    """Repository para operações CRUD de Scale."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _generate_code(self, post_id: str, month: int, year: int) -> str:
        """Gera código único para a escala."""
        return f"ESC-{year}-{month:02d}-{post_id[:8].upper()}"

    async def create(self, data: ScaleCreate, created_by: Optional[str] = None) -> Scale:
        """
        Cria uma nova escala.

        Args:
            data: Dados da escala
            created_by: ID do usuário criador

        Returns:
            Scale criada
        """
        code = await self._generate_code(data.post_id, data.month, data.year)

        # Calcular datas de início e fim do mês
        start_date = date(data.year, data.month, 1)
        last_day = calendar.monthrange(data.year, data.month)[1]
        end_date = date(data.year, data.month, last_day)

        scale = Scale(
            id=str(uuid4()),
            code=code,
            post_id=data.post_id,
            scale_type=data.scale_type.value,
            status=ScaleStatus.DRAFT.value,
            month=data.month,
            year=data.year,
            start_date=start_date,
            end_date=end_date,
            config=data.config,
            notes=data.notes,
            created_by=created_by,
        )

        self.db.add(scale)
        await self.db.commit()
        await self.db.refresh(scale)

        logger.info(f"Scale criada: {scale.id} ({scale.code})")
        return scale

    async def get_by_id(self, scale_id: str) -> Optional[Scale]:
        """
        Busca escala por ID.

        Args:
            scale_id: ID da escala

        Returns:
            Scale ou None
        """
        result = await self.db.execute(
            select(Scale).where(Scale.id == scale_id, Scale.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Scale]:
        """
        Busca escala por código.

        Args:
            code: Código da escala

        Returns:
            Scale ou None
        """
        result = await self.db.execute(
            select(Scale).where(Scale.code == code, Scale.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def get_by_post_and_period(self, post_id: str, month: int, year: int) -> Optional[Scale]:
        """
        Busca escala por posto e período.

        Args:
            post_id: ID do posto
            month: Mês
            year: Ano

        Returns:
            Scale ou None
        """
        result = await self.db.execute(
            select(Scale).where(
                Scale.post_id == post_id,
                Scale.month == month,
                Scale.year == year,
                Scale.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: Optional[ScaleFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Scale], int]:
        """
        Lista escalas com filtros e paginação.

        Args:
            filters: Filtros de busca
            page: Página atual
            page_size: Itens por página

        Returns:
            Tupla (escalas, total)
        """
        query = select(Scale).where(Scale.is_active.is_(True))

        if filters:
            query = self._apply_filters(query, filters)

        # Count total
        count_query = select(func.count(Scale.id)).where(Scale.is_active.is_(True))
        if filters:
            count_query = self._apply_filters(count_query, filters)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Scale.year.desc(), Scale.month.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        scales = list(result.scalars().all())

        return scales, total

    def _apply_filters(self, query, filters: ScaleFilter):
        """Aplica filtros à query."""
        if filters.post_id:
            query = query.where(Scale.post_id == filters.post_id)

        if filters.scale_type:
            query = query.where(Scale.scale_type == filters.scale_type.value)

        if filters.status:
            query = query.where(Scale.status == filters.status.value)

        if filters.month:
            query = query.where(Scale.month == filters.month)

        if filters.year:
            query = query.where(Scale.year == filters.year)

        if filters.is_current_month:
            today = date.today()
            query = query.where(
                Scale.month == today.month,
                Scale.year == today.year,
            )

        return query

    async def update(self, scale_id: str, data: ScaleUpdate) -> Optional[Scale]:
        """
        Atualiza uma escala.

        Args:
            scale_id: ID da escala
            data: Dados para atualização

        Returns:
            Scale atualizada ou None
        """
        scale = await self.get_by_id(scale_id)
        if not scale:
            return None

        # Verifica se pode editar
        if not scale.can_edit:
            logger.warning(f"Tentativa de editar escala não editável: {scale_id}")
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field in ("scale_type", "status") and value:
                setattr(scale, field, value.value)
            else:
                setattr(scale, field, value)

        scale.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(scale)

        logger.info(f"Scale atualizada: {scale.id}")
        return scale

    async def approve(
        self, scale_id: str, approved_by: str, notes: Optional[str] = None
    ) -> Optional[Scale]:
        """
        Aprova uma escala.

        Args:
            scale_id: ID da escala
            approved_by: ID do aprovador
            notes: Observações

        Returns:
            Scale aprovada ou None
        """
        scale = await self.get_by_id(scale_id)
        if not scale:
            return None

        if scale.status != ScaleStatus.PENDING_APPROVAL.value:
            logger.warning(f"Escala não está pendente de aprovação: {scale_id}")
            return None

        scale.status = ScaleStatus.APPROVED.value
        scale.approved_by = approved_by
        scale.approved_at = datetime.utcnow()
        if notes:
            scale.notes = f"{scale.notes or ''}\n[Aprovação] {notes}".strip()
        scale.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(scale)

        logger.info(f"Scale aprovada: {scale.id}")
        return scale

    async def publish(self, scale_id: str, published_by: str) -> Optional[Scale]:
        """
        Publica uma escala.

        Args:
            scale_id: ID da escala
            published_by: ID do publicador

        Returns:
            Scale publicada ou None
        """
        scale = await self.get_by_id(scale_id)
        if not scale:
            return None

        if scale.status != ScaleStatus.APPROVED.value:
            logger.warning(f"Escala não está aprovada: {scale_id}")
            return None

        scale.status = ScaleStatus.PUBLISHED.value
        scale.published_by = published_by
        scale.published_at = datetime.utcnow()
        scale.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(scale)

        logger.info(f"Scale publicada: {scale.id}")
        return scale

    async def delete(self, scale_id: str) -> bool:
        """
        Soft delete de escala.

        Args:
            scale_id: ID da escala

        Returns:
            True se deletada
        """
        scale = await self.get_by_id(scale_id)
        if not scale:
            return False

        if not scale.can_edit:
            logger.warning(f"Tentativa de deletar escala não editável: {scale_id}")
            return False

        scale.is_active = False
        scale.status = ScaleStatus.CANCELLED.value
        scale.updated_at = datetime.utcnow()

        await self.db.commit()

        logger.info(f"Scale deletada (soft): {scale.id}")
        return True

    async def update_metrics(self, scale_id: str) -> Optional[Scale]:
        """
        Atualiza métricas da escala baseado nos turnos.

        Args:
            scale_id: ID da escala

        Returns:
            Scale atualizada ou None
        """
        scale = await self.get_by_id(scale_id)
        if not scale:
            return None

        total_shifts = len(scale.shifts)
        total_hours = sum(s.planned_hours for s in scale.shifts if not s.is_off_day)
        overtime_hours = sum(s.overtime_hours for s in scale.shifts)
        estimated_cost = sum(s.total_cost for s in scale.shifts)

        scale.total_shifts = total_shifts
        scale.total_hours = total_hours
        scale.overtime_hours = overtime_hours
        scale.estimated_cost = estimated_cost
        scale.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(scale)

        return scale
