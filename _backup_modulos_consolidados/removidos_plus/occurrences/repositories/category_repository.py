"""Repository para OccurrenceCategory."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.occurrences.models.category import OccurrenceCategory
from modules.occurrences.schemas.category import CategoryCreate, CategoryUpdate

logger = logging.getLogger(__name__)


class CategoryRepository:
    """Repository para operações de OccurrenceCategory."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: CategoryCreate) -> OccurrenceCategory:
        """Cria uma nova categoria."""
        category = OccurrenceCategory(**data.model_dump(exclude_none=True))
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        logger.info(f"Categoria criada: {category.name}")
        return category

    async def get_by_id(
        self, category_id: str | UUID, include_children: bool = False
    ) -> Optional[OccurrenceCategory]:
        """Busca categoria por ID."""
        if isinstance(category_id, str):
            category_id = UUID(category_id)

        query = select(OccurrenceCategory).where(OccurrenceCategory.id == category_id)
        if include_children:
            query = query.options(selectinload(OccurrenceCategory.children))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[OccurrenceCategory]:
        """Busca categoria por código."""
        result = await self.session.execute(
            select(OccurrenceCategory).where(OccurrenceCategory.code == code)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[OccurrenceCategory]:
        """Busca categoria por nome."""
        result = await self.session.execute(
            select(OccurrenceCategory).where(OccurrenceCategory.name == name)
        )
        return result.scalar_one_or_none()

    async def update(
        self, category_id: str | UUID, data: CategoryUpdate
    ) -> Optional[OccurrenceCategory]:
        """Atualiza uma categoria."""
        category = await self.get_by_id(category_id)
        if not category:
            return None

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def delete(self, category_id: str | UUID) -> bool:
        """Deleta uma categoria (soft delete)."""
        category = await self.get_by_id(category_id)
        if not category:
            return False

        category.is_active = False
        await self.session.flush()
        return True

    async def list_all(
        self,
        is_active: bool = True,
        is_public: bool = None,
        parent_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[OccurrenceCategory], int]:
        """Lista todas as categorias."""
        query = select(OccurrenceCategory)

        if is_active is not None:
            query = query.where(OccurrenceCategory.is_active == is_active)
        if is_public is not None:
            query = query.where(OccurrenceCategory.is_public == is_public)
        if parent_id:
            query = query.where(OccurrenceCategory.parent_id == UUID(parent_id))
        elif parent_id is None:
            # Root categories only
            query = query.where(OccurrenceCategory.parent_id.is_(None))

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Order and paginate
        query = query.order_by(OccurrenceCategory.order.asc(), OccurrenceCategory.name.asc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        categories = list(result.scalars().all())

        return categories, total

    async def get_root_categories(self) -> list[OccurrenceCategory]:
        """Lista categorias raiz."""
        result = await self.session.execute(
            select(OccurrenceCategory)
            .where(
                and_(
                    OccurrenceCategory.parent_id.is_(None),
                    OccurrenceCategory.is_active.is_(True),
                )
            )
            .options(selectinload(OccurrenceCategory.children))
            .order_by(OccurrenceCategory.order.asc(), OccurrenceCategory.name.asc())
        )
        return list(result.scalars().all())

    async def get_children(self, parent_id: str | UUID) -> list[OccurrenceCategory]:
        """Lista subcategorias."""
        if isinstance(parent_id, str):
            parent_id = UUID(parent_id)

        result = await self.session.execute(
            select(OccurrenceCategory)
            .where(
                and_(
                    OccurrenceCategory.parent_id == parent_id,
                    OccurrenceCategory.is_active.is_(True),
                )
            )
            .options(selectinload(OccurrenceCategory.children))
            .order_by(OccurrenceCategory.order.asc(), OccurrenceCategory.name.asc())
        )
        return list(result.scalars().all())

    async def get_tree(self) -> list[dict]:
        """Retorna árvore de categorias."""
        root_categories = await self.get_root_categories()

        async def build_tree(category: OccurrenceCategory) -> dict:
            children = await self.get_children(category.id)
            return {
                "id": str(category.id),
                "code": category.code,
                "name": category.name,
                "icon": category.icon,
                "color": category.color,
                "level": category.level,
                "occurrence_count": category.occurrence_count,
                "children": [await build_tree(child) for child in children],
            }

        return [await build_tree(cat) for cat in root_categories]

    async def increment_occurrence_count(self, category_id: str | UUID) -> None:
        """Incrementa contador de ocorrências."""
        category = await self.get_by_id(category_id)
        if category:
            category.increment_count()
            await self.session.flush()

    async def decrement_occurrence_count(self, category_id: str | UUID) -> None:
        """Decrementa contador de ocorrências."""
        category = await self.get_by_id(category_id)
        if category:
            category.decrement_count()
            await self.session.flush()

    async def update_avg_resolution(
        self, category_id: str | UUID, resolution_hours: float
    ) -> None:
        """Atualiza média de resolução."""
        category = await self.get_by_id(category_id)
        if category:
            category.update_avg_resolution(resolution_hours)
            await self.session.flush()

    async def get_with_sla(self, category_id: str | UUID) -> Optional[dict]:
        """Retorna categoria com informações de SLA."""
        category = await self.get_by_id(category_id)
        if not category:
            return None

        return {
            "id": str(category.id),
            "name": category.name,
            "sla_response_hours": category.default_sla_response_hours,
            "sla_resolution_hours": category.default_sla_resolution_hours,
            "default_priority": category.default_priority,
            "auto_assign_to_id": category.auto_assign_to_id,
            "auto_assign_to_name": category.auto_assign_to_name,
        }
