"""Controller para categorias de contas a receber."""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_session
from modules.financial.models.receivable_category import CategoryType
from modules.financial.repositories.receivable_repository import ReceivableCategoryRepository
from modules.financial.schemas.receivable import (
    ReceivableCategoryCreate,
    ReceivableCategoryResponse,
    ReceivableCategoryUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/receivable-categories", tags=["Categorias (Contas a Receber)"])


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> ReceivableCategoryRepository:
    """Retorna instancia do repository."""
    return ReceivableCategoryRepository(session)


@router.post(
    "/",
    response_model=ReceivableCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar categoria",
)
async def create_category(
    data: ReceivableCategoryCreate,
    repo: ReceivableCategoryRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> ReceivableCategoryResponse:
    """Cria uma nova categoria de conta a receber."""
    try:
        category = await repo.create(data, UUID(current_user["id"]))
        return ReceivableCategoryResponse.model_validate(category)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar categoria: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar categoria",
        )


@router.get(
    "/",
    response_model=List[ReceivableCategoryResponse],
    summary="Listar categorias",
)
async def list_categories(
    condominio_id: UUID,
    search: Optional[str] = Query(None, description="Busca no nome"),
    category_type: Optional[str] = Query(None, alias="type", description="Tipo"),
    is_active: Optional[bool] = Query(None, description="Apenas ativas"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    repo: ReceivableCategoryRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
):
    """Lista categorias com filtros."""
    categories = await repo.list(
        condominio_id,
        search=search,
        category_type=CategoryType(category_type) if category_type else None,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )
    return [ReceivableCategoryResponse.model_validate(c) for c in categories]


@router.get(
    "/tree",
    response_model=List[ReceivableCategoryResponse],
    summary="Arvore de categorias",
)
async def get_category_tree(
    condominio_id: UUID,
    repo: ReceivableCategoryRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
):
    """Retorna categorias em estrutura de arvore (apenas raiz)."""
    categories = await repo.get_root_categories(condominio_id)
    return [ReceivableCategoryResponse.model_validate(c) for c in categories]


@router.get(
    "/{category_id}",
    response_model=ReceivableCategoryResponse,
    summary="Buscar categoria",
)
async def get_category(
    category_id: UUID,
    repo: ReceivableCategoryRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> ReceivableCategoryResponse:
    """Busca categoria por ID."""
    category = await repo.get_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )
    return ReceivableCategoryResponse.model_validate(category)


@router.get(
    "/{category_id}/children",
    response_model=List[ReceivableCategoryResponse],
    summary="Subcategorias",
)
async def get_children(
    category_id: UUID,
    repo: ReceivableCategoryRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
):
    """Retorna subcategorias de uma categoria."""
    category = await repo.get_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )

    children = await repo.get_children(category_id)
    return [ReceivableCategoryResponse.model_validate(c) for c in children]


@router.put(
    "/{category_id}",
    response_model=ReceivableCategoryResponse,
    summary="Atualizar categoria",
)
async def update_category(
    category_id: UUID,
    data: ReceivableCategoryUpdate,
    repo: ReceivableCategoryRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> ReceivableCategoryResponse:
    """Atualiza uma categoria."""
    try:
        category = await repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria nao encontrada",
            )

        category = await repo.update(category, data)
        return ReceivableCategoryResponse.model_validate(category)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir categoria",
)
async def delete_category(
    category_id: UUID,
    repo: ReceivableCategoryRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
):
    """Exclui uma categoria (soft delete)."""
    category = await repo.get_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )

    # Verifica se tem subcategorias
    children = await repo.get_children(category_id)
    if children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Categoria com subcategorias nao pode ser excluida",
        )

    await repo.delete(category)


@router.post(
    "/{category_id}/activate",
    response_model=ReceivableCategoryResponse,
    summary="Ativar categoria",
)
async def activate_category(
    category_id: UUID,
    repo: ReceivableCategoryRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> ReceivableCategoryResponse:
    """Ativa uma categoria."""
    category = await repo.get_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )

    category.is_active = True
    await repo.session.commit()
    return ReceivableCategoryResponse.model_validate(category)


@router.post(
    "/{category_id}/deactivate",
    response_model=ReceivableCategoryResponse,
    summary="Desativar categoria",
)
async def deactivate_category(
    category_id: UUID,
    repo: ReceivableCategoryRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> ReceivableCategoryResponse:
    """Desativa uma categoria."""
    category = await repo.get_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )

    category.is_active = False
    await repo.session.commit()
    return ReceivableCategoryResponse.model_validate(category)
