"""Controller para OccurrenceCategory."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from core.auth.dependencies import get_current_user, require_roles
from modules.occurrences.schemas.category import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryTree,
    CategoryUpdate,
)
from modules.occurrences.services import CategoryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/occurrence-categories", tags=["Occurrence Categories"])


async def get_category_service(
    session: AsyncSession = Depends(get_async_session),
) -> CategoryService:
    """Dependency para CategoryService."""
    return CategoryService(session)


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar categoria",
)
async def create_category(
    data: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
    current_user: dict = Depends(require_roles(["admin", "sindico"])),
) -> CategoryResponse:
    """Cria uma nova categoria de ocorrencia."""
    try:
        result = await service.create(data)
        logger.info(f"Categoria {result.name} criada por {current_user.get('email')}")
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar categoria: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar categoria",
        )


@router.get(
    "/",
    response_model=CategoryListResponse,
    summary="Listar categorias",
)
async def list_categories(
    is_active: bool = Query(True, description="Apenas ativas"),
    is_public: Optional[bool] = Query(None, description="Apenas publicas"),
    parent_id: Optional[str] = Query(None, description="ID da categoria pai"),
    page: int = Query(1, ge=1, description="Pagina"),
    page_size: int = Query(100, ge=1, le=500, description="Itens por pagina"),
    service: CategoryService = Depends(get_category_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> CategoryListResponse:
    """Lista categorias de ocorrencia."""
    return await service.list_all(is_active, is_public, parent_id, page, page_size)


@router.get(
    "/tree",
    response_model=list[CategoryTree],
    summary="Arvore de categorias",
)
async def get_category_tree(
    service: CategoryService = Depends(get_category_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[CategoryTree]:
    """Retorna arvore hierarquica de categorias."""
    return await service.get_tree()


@router.get(
    "/root",
    response_model=list[CategoryResponse],
    summary="Categorias raiz",
)
async def get_root_categories(
    service: CategoryService = Depends(get_category_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[CategoryResponse]:
    """Lista categorias raiz (sem pai)."""
    return await service.get_root_categories()


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Buscar categoria por ID",
)
async def get_category(
    category_id: UUID,
    include_children: bool = Query(False, description="Incluir subcategorias"),
    service: CategoryService = Depends(get_category_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> CategoryResponse:
    """Busca categoria por ID."""
    result = await service.get_by_id(category_id, include_children)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )
    return result


@router.get(
    "/code/{code}",
    response_model=CategoryResponse,
    summary="Buscar categoria por codigo",
)
async def get_category_by_code(
    code: str,
    service: CategoryService = Depends(get_category_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> CategoryResponse:
    """Busca categoria por codigo."""
    result = await service.get_by_code(code)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )
    return result


@router.get(
    "/{category_id}/children",
    response_model=list[CategoryResponse],
    summary="Listar subcategorias",
)
async def get_children(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[CategoryResponse]:
    """Lista subcategorias de uma categoria."""
    return await service.get_children(category_id)


@router.get(
    "/{category_id}/sla",
    summary="Informacoes de SLA",
)
async def get_category_sla(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Retorna informacoes de SLA da categoria."""
    result = await service.get_with_sla(category_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )
    return result


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Atualizar categoria",
)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
    current_user: dict = Depends(require_roles(["admin", "sindico"])),
) -> CategoryResponse:
    """Atualiza uma categoria."""
    result = await service.update(category_id, data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )
    logger.info(f"Categoria {category_id} atualizada por {current_user.get('email')}")
    return result


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar categoria",
)
async def delete_category(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
    current_user: dict = Depends(require_roles(["admin"])),
) -> None:
    """Deleta uma categoria."""
    result = await service.delete(category_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )
    logger.info(f"Categoria {category_id} deletada por {current_user.get('email')}")


@router.post(
    "/{category_id}/move",
    response_model=CategoryResponse,
    summary="Mover categoria",
)
async def move_category(
    category_id: UUID,
    new_parent_id: Optional[UUID] = Query(None, description="ID do novo pai"),
    service: CategoryService = Depends(get_category_service),
    current_user: dict = Depends(require_roles(["admin", "sindico"])),
) -> CategoryResponse:
    """Move categoria para outro pai."""
    result = await service.move_to_parent(category_id, new_parent_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )
    logger.info(f"Categoria {category_id} movida por {current_user.get('email')}")
    return result


@router.post(
    "/{category_id}/reorder",
    response_model=CategoryResponse,
    summary="Reordenar categoria",
)
async def reorder_category(
    category_id: UUID,
    new_order: int = Query(..., ge=0, description="Nova ordem"),
    service: CategoryService = Depends(get_category_service),
    current_user: dict = Depends(require_roles(["admin", "sindico"])),  # noqa pylint: disable=unused-argument
) -> CategoryResponse:
    """Reordena uma categoria."""
    result = await service.reorder(category_id, new_order)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )
    return result


@router.post(
    "/{category_id}/toggle-active",
    response_model=CategoryResponse,
    summary="Ativar/desativar categoria",
)
async def toggle_category_active(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
    current_user: dict = Depends(require_roles(["admin", "sindico"])),
) -> CategoryResponse:
    """Ativa ou desativa uma categoria."""
    result = await service.toggle_active(category_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )
    logger.info(f"Status da categoria {category_id} alterado por {current_user.get('email')}")
    return result
