"""
Repository para operações de banco de dados com Checklist.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.facilities.models.checklist import (
    Checklist,
    ChecklistItem,
    ChecklistStatus,
    ItemStatus,
)
from modules.facilities.schemas.checklist import (
    ChecklistCreate,
    ChecklistFilter,
    ChecklistItemCreate,
    ChecklistStats,
    ChecklistUpdate,
)


class ChecklistRepository:
    """Repository para operações CRUD de Checklist."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _generate_code(self) -> str:
        """Gera código único para checklist."""
        result = await self.db.execute(
            select(func.count(Checklist.id)).where(Checklist.is_active.is_(True))
        )
        count = result.scalar() or 0
        return f"CHK-{count + 1:05d}"

    async def create(
        self,
        data: ChecklistCreate,
        created_by: Optional[str] = None,
    ) -> Checklist:
        """Cria um novo checklist."""
        code = data.code or await self._generate_code()

        checklist = Checklist(
            id=str(uuid4()),
            code=code,
            name=data.name,
            description=data.description,
            version=data.version,
            status=ChecklistStatus.DRAFT.value,
            is_template=data.is_template,
            category=data.category,
            area_id=data.area_id,
            inspection_id=data.inspection_id,
            template_id=data.template_id,
            client_id=data.client_id,
            notes=data.notes,
            tags=data.tags,
            created_by=created_by,
        )

        self.db.add(checklist)

        # Adicionar itens se fornecidos
        if data.items:
            for i, item_data in enumerate(data.items):
                item = self._create_item(checklist.id, item_data, i)
                self.db.add(item)

        await self.db.commit()
        await self.db.refresh(checklist)

        # Atualizar métricas
        if checklist.items:
            checklist.update_metrics()
            await self.db.commit()
            await self.db.refresh(checklist)

        logger.info(f"Checklist criado: {checklist.id} - {checklist.code}")
        return checklist

    def _create_item(
        self,
        checklist_id: str,
        data: ChecklistItemCreate,
        order: int,
    ) -> ChecklistItem:
        """Cria um item de checklist."""
        return ChecklistItem(
            id=str(uuid4()),
            checklist_id=checklist_id,
            order=data.order or order,
            category=data.category,
            subcategory=data.subcategory,
            question=data.question,
            description=data.description,
            help_text=data.help_text,
            status=ItemStatus.PENDING.value,
            answer_type=data.answer_type,
            answer_options=data.answer_options,
            is_required=data.is_required,
            weight=data.weight,
            requires_photo=data.requires_photo,
            requires_notes_on_fail=data.requires_notes_on_fail,
            reference=data.reference,
            norm_reference=data.norm_reference,
        )

    async def get_by_id(self, checklist_id: str) -> Optional[Checklist]:
        """Busca checklist por ID."""
        result = await self.db.execute(
            select(Checklist).where(
                Checklist.id == checklist_id,
                Checklist.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Checklist]:
        """Busca checklist por código."""
        result = await self.db.execute(
            select(Checklist).where(
                Checklist.code == code.upper(),
                Checklist.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: Optional[ChecklistFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Checklist], int]:
        """Lista checklists com filtros e paginação."""
        query = select(Checklist).where(Checklist.is_active.is_(True))

        if filters:
            query = self._apply_filters(query, filters)

        # Count total
        count_query = select(func.count(Checklist.id)).where(
            Checklist.is_active.is_(True)
        )
        if filters:
            count_query = self._apply_filters(count_query, filters)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Checklist.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        checklists = list(result.scalars().all())

        return checklists, total

    def _apply_filters(self, query, filters: ChecklistFilter):  # pylint: disable=too-many-branches
        """Aplica filtros à query."""
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Checklist.name.ilike(search_term),
                    Checklist.code.ilike(search_term),
                )
            )

        if filters.status:
            query = query.where(Checklist.status == filters.status.value)

        if filters.is_template is not None:
            query = query.where(Checklist.is_template == filters.is_template)

        if filters.category:
            query = query.where(Checklist.category == filters.category)

        if filters.area_id:
            query = query.where(Checklist.area_id == filters.area_id)

        if filters.client_id:
            query = query.where(Checklist.client_id == filters.client_id)

        if filters.inspection_id:
            query = query.where(Checklist.inspection_id == filters.inspection_id)

        if filters.filled_by:
            query = query.where(Checklist.filled_by == filters.filled_by)

        if filters.has_critical_items:
            query = query.where(Checklist.items_critical > 0)

        if filters.min_score is not None:
            query = query.where(Checklist.score >= filters.min_score)

        if filters.max_score is not None:
            query = query.where(Checklist.score <= filters.max_score)

        if filters.created_start:
            query = query.where(Checklist.created_at >= filters.created_start)

        if filters.created_end:
            query = query.where(Checklist.created_at <= filters.created_end)

        return query

    async def update(
        self,
        checklist_id: str,
        data: ChecklistUpdate,
    ) -> Optional[Checklist]:
        """Atualiza um checklist."""
        checklist = await self.get_by_id(checklist_id)
        if not checklist:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "status" and value:
                setattr(checklist, field, value.value)
            else:
                setattr(checklist, field, value)

        checklist.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(checklist)

        logger.info(f"Checklist atualizado: {checklist.id}")
        return checklist

    async def add_item(
        self,
        checklist_id: str,
        data: ChecklistItemCreate,
    ) -> Optional[ChecklistItem]:
        """Adiciona um item ao checklist."""
        checklist = await self.get_by_id(checklist_id)
        if not checklist:
            return None

        # Determinar ordem
        order = len(checklist.items) if checklist.items else 0

        item = self._create_item(checklist_id, data, order)
        self.db.add(item)

        await self.db.commit()
        await self.db.refresh(item)

        # Atualizar métricas do checklist
        await self.db.refresh(checklist)
        checklist.update_metrics()
        await self.db.commit()

        logger.info(f"Item adicionado ao checklist {checklist_id}")
        return item

    async def answer_item(
        self,
        item_id: str,
        status: ItemStatus,
        answer: Optional[str] = None,
        notes: Optional[str] = None,
        photos: Optional[List[str]] = None,
        answered_by: Optional[str] = None,
    ) -> Optional[ChecklistItem]:
        """Responde um item do checklist."""
        result = await self.db.execute(
            select(ChecklistItem).where(
                ChecklistItem.id == item_id,
                ChecklistItem.is_active.is_(True),
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return None

        item.status = status.value
        item.answer = answer
        item.notes = notes
        item.photos = photos
        item.answered_at = datetime.utcnow()
        item.answered_by = answered_by
        item.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(item)

        # Atualizar métricas do checklist pai
        checklist = await self.get_by_id(item.checklist_id)
        if checklist:
            checklist.update_metrics()
            await self.db.commit()

        logger.info(f"Item {item_id} respondido: {status.value}")
        return item

    async def clone(
        self,
        checklist_id: str,
        new_name: str,
        area_id: Optional[str] = None,
        inspection_id: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Optional[Checklist]:
        """Clona um checklist (útil para usar templates)."""
        original = await self.get_by_id(checklist_id)
        if not original:
            return None

        new_code = await self._generate_code()

        new_checklist = Checklist(
            id=str(uuid4()),
            code=new_code,
            name=new_name,
            description=original.description,
            version=original.version,
            status=ChecklistStatus.DRAFT.value,
            is_template=False,
            category=original.category,
            area_id=area_id or original.area_id,
            inspection_id=inspection_id,
            template_id=original.id if original.is_template else original.template_id,
            client_id=original.client_id,
            notes=original.notes,
            tags=original.tags,
            created_by=created_by,
        )

        self.db.add(new_checklist)

        # Clonar itens
        if original.items:
            for item in original.items:
                new_item = ChecklistItem(
                    id=str(uuid4()),
                    checklist_id=new_checklist.id,
                    order=item.order,
                    category=item.category,
                    subcategory=item.subcategory,
                    question=item.question,
                    description=item.description,
                    help_text=item.help_text,
                    status=ItemStatus.PENDING.value,
                    answer_type=item.answer_type,
                    answer_options=item.answer_options,
                    is_required=item.is_required,
                    weight=item.weight,
                    requires_photo=item.requires_photo,
                    requires_notes_on_fail=item.requires_notes_on_fail,
                    reference=item.reference,
                    norm_reference=item.norm_reference,
                )
                self.db.add(new_item)

        await self.db.commit()
        await self.db.refresh(new_checklist)

        # Atualizar métricas
        new_checklist.update_metrics()
        await self.db.commit()
        await self.db.refresh(new_checklist)

        logger.info(f"Checklist clonado: {original.id} -> {new_checklist.id}")
        return new_checklist

    async def delete(self, checklist_id: str) -> bool:
        """Soft delete de checklist."""
        checklist = await self.get_by_id(checklist_id)
        if not checklist:
            return False

        checklist.is_active = False
        checklist.updated_at = datetime.utcnow()

        await self.db.commit()

        logger.info(f"Checklist deletado (soft): {checklist.id}")
        return True

    async def get_stats(  # pylint: disable=too-many-locals
        self,
        client_id: Optional[str] = None,
        area_id: Optional[str] = None,
    ) -> ChecklistStats:
        """Obtém estatísticas de checklists."""
        base_filter = [Checklist.is_active.is_(True)]
        if client_id:
            base_filter.append(Checklist.client_id == client_id)
        if area_id:
            base_filter.append(Checklist.area_id == area_id)

        # Total
        total_result = await self.db.execute(
            select(func.count(Checklist.id)).where(and_(*base_filter))
        )
        total = total_result.scalar() or 0

        # Templates
        templates_result = await self.db.execute(
            select(func.count(Checklist.id)).where(
                and_(*base_filter, Checklist.is_template.is_(True))
            )
        )
        templates = templates_result.scalar() or 0

        # Por status
        by_status: Dict[str, int] = {}
        for status in ChecklistStatus:
            status_result = await self.db.execute(
                select(func.count(Checklist.id)).where(
                    and_(*base_filter, Checklist.status == status.value)
                )
            )
            count = status_result.scalar() or 0
            if count > 0:
                by_status[status.value] = count

        # Por categoria
        by_category: Dict[str, int] = {}
        cat_result = await self.db.execute(
            select(Checklist.category, func.count(Checklist.id))
            .where(and_(*base_filter, Checklist.category.isnot(None)))
            .group_by(Checklist.category)
        )
        for cat, count in cat_result.all():
            by_category[cat] = count

        # Pontuação média
        avg_score_result = await self.db.execute(
            select(func.avg(Checklist.score)).where(
                and_(*base_filter, Checklist.score.isnot(None))
            )
        )
        avg_score = avg_score_result.scalar()

        # Taxa média de preenchimento
        avg_rate_result = await self.db.execute(
            select(
                func.avg(Checklist.completed_items * 100.0 / func.nullif(Checklist.total_items, 0))
            ).where(and_(*base_filter, Checklist.total_items > 0))
        )
        avg_completion_rate = avg_rate_result.scalar() or 0.0

        # Com itens críticos
        critical_result = await self.db.execute(
            select(func.count(Checklist.id)).where(
                and_(*base_filter, Checklist.items_critical > 0)
            )
        )
        with_critical = critical_result.scalar() or 0

        # Concluídos este mês
        today = date.today()
        first_day = today.replace(day=1)

        completed_result = await self.db.execute(
            select(func.count(Checklist.id)).where(
                and_(
                    *base_filter,
                    Checklist.status == ChecklistStatus.COMPLETED.value,
                    Checklist.filled_at >= datetime.combine(first_day, datetime.min.time()),
                )
            )
        )
        completed_this_month = completed_result.scalar() or 0

        return ChecklistStats(
            total=total,
            templates=templates,
            by_status=by_status,
            by_category=by_category,
            avg_score=float(avg_score) if avg_score else None,
            avg_completion_rate=float(avg_completion_rate),
            with_critical_items=with_critical,
            completed_this_month=completed_this_month,
        )
