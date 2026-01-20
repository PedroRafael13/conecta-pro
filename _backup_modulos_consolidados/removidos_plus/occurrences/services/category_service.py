"""Service para OccurrenceCategory."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.occurrences.repositories.category_repository import CategoryRepository
from modules.occurrences.schemas.category import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryTree,
    CategoryUpdate,
)

logger = logging.getLogger(__name__)


class CategoryService:
    """Service para operações de OccurrenceCategory."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = CategoryRepository(session)

    async def create(self, data: CategoryCreate) -> CategoryResponse:
        """Cria uma nova categoria."""
        # Verificar se já existe com mesmo nome
        existing = await self.repository.get_by_name(data.name)
        if existing:
            raise ValueError(f"Categoria com nome '{data.name}' já existe")

        category = await self.repository.create(data)

        # Se tem parent, definir hierarquia
        if data.parent_id:
            parent = await self.repository.get_by_id(data.parent_id)
            if parent:
                category.set_parent(parent)

        await self.session.commit()
        await self.session.refresh(category)
        return CategoryResponse.model_validate(category)

    async def get_by_id(
        self, category_id: str | UUID, include_children: bool = False
    ) -> Optional[CategoryResponse]:
        """Busca categoria por ID."""
        category = await self.repository.get_by_id(category_id, include_children)
        if not category:
            return None
        return CategoryResponse.model_validate(category)

    async def get_by_code(self, code: str) -> Optional[CategoryResponse]:
        """Busca categoria por código."""
        category = await self.repository.get_by_code(code)
        if not category:
            return None
        return CategoryResponse.model_validate(category)

    async def update(
        self, category_id: str | UUID, data: CategoryUpdate
    ) -> Optional[CategoryResponse]:
        """Atualiza uma categoria."""
        category = await self.repository.update(category_id, data)
        if not category:
            return None
        await self.session.commit()
        return CategoryResponse.model_validate(category)

    async def delete(self, category_id: str | UUID) -> bool:
        """Deleta uma categoria."""
        result = await self.repository.delete(category_id)
        if result:
            await self.session.commit()
        return result

    async def list_all(
        self,
        is_active: bool = True,
        is_public: bool = None,
        parent_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
    ) -> CategoryListResponse:
        """Lista todas as categorias."""
        skip = (page - 1) * page_size
        categories, total = await self.repository.list_all(
            is_active, is_public, parent_id, skip, page_size
        )

        items = [CategoryResponse.model_validate(cat) for cat in categories]
        return CategoryListResponse(items=items, total=total)

    async def get_root_categories(self) -> list[CategoryResponse]:
        """Lista categorias raiz."""
        categories = await self.repository.get_root_categories()
        return [CategoryResponse.model_validate(cat) for cat in categories]

    async def get_children(self, parent_id: str | UUID) -> list[CategoryResponse]:
        """Lista subcategorias."""
        categories = await self.repository.get_children(parent_id)
        return [CategoryResponse.model_validate(cat) for cat in categories]

    async def get_tree(self) -> list[CategoryTree]:
        """Retorna árvore de categorias."""
        tree_data = await self.repository.get_tree()

        def convert_to_tree(data: dict) -> CategoryTree:
            children = [convert_to_tree(child) for child in data.get("children", [])]
            return CategoryTree(
                id=data["id"],
                code=data["code"],
                name=data["name"],
                icon=data.get("icon"),
                color=data.get("color"),
                level=data["level"],
                occurrence_count=data["occurrence_count"],
                children=children,
            )

        return [convert_to_tree(item) for item in tree_data]

    async def get_with_sla(self, category_id: str | UUID) -> Optional[dict]:
        """Retorna categoria com informações de SLA."""
        return await self.repository.get_with_sla(category_id)

    async def move_to_parent(
        self, category_id: str | UUID, new_parent_id: Optional[str | UUID]
    ) -> Optional[CategoryResponse]:
        """Move categoria para outro pai."""
        category = await self.repository.get_by_id(category_id)
        if not category:
            return None

        if new_parent_id:
            parent = await self.repository.get_by_id(new_parent_id)
            if parent:
                category.set_parent(parent)
        else:
            category.parent_id = None
            category.level = 0
            category.path = f"/{category.code}"

        await self.session.commit()
        return CategoryResponse.model_validate(category)

    async def reorder(self, category_id: str | UUID, new_order: int) -> Optional[CategoryResponse]:
        """Reordena categoria."""
        update_data = CategoryUpdate(order=new_order)
        return await self.update(category_id, update_data)

    async def toggle_active(self, category_id: str | UUID) -> Optional[CategoryResponse]:
        """Ativa/desativa categoria."""
        category = await self.repository.get_by_id(category_id)
        if not category:
            return None

        update_data = CategoryUpdate(is_active=not category.is_active)
        return await self.update(category_id, update_data)
