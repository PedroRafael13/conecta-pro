"""
Controller (endpoints) para Post.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from core.logging import logger
from modules.operations.models.post import PostStatus, PostType, ShiftType
from modules.operations.repositories.post_repository import PostRepository
from modules.operations.schemas.post import (
    PostCreate,
    PostFilter,
    PostListResponse,
    PostResponse,
    PostStats,
    PostUpdate,
)

router = APIRouter(prefix="/posts", tags=["Operations - Posts"])


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    """
    Cria um novo posto de trabalho.

    Requer autenticação.
    """
    repo = PostRepository(db)
    post = await repo.create(data, created_by=current_user.id)

    logger.info(f"Post criado por {current_user.email}: {post.id}")
    return PostResponse.model_validate(post)


@router.get("/", response_model=PostListResponse)
async def list_posts(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Página atual"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    post_type: Optional[PostType] = None,
    status_filter: Optional[PostStatus] = Query(None, alias="status"),
    shift_type: Optional[ShiftType] = None,
    contract_id: Optional[str] = None,
    client_id: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    requires_armed: Optional[bool] = None,
    requires_vehicle: Optional[bool] = None,
    has_vacancy: Optional[bool] = None,
    search: Optional[str] = None,
) -> PostListResponse:
    """
    Lista postos com filtros e paginação.
    """
    repo = PostRepository(db)

    filters = PostFilter(
        post_type=post_type,
        status=status_filter,
        shift_type=shift_type,
        contract_id=contract_id,
        client_id=client_id,
        city=city,
        state=state,
        requires_armed=requires_armed,
        requires_vehicle=requires_vehicle,
        has_vacancy=has_vacancy,
        search=search,
    )

    posts, total = await repo.list(filters=filters, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size

    return PostListResponse(
        items=[PostResponse.model_validate(post) for post in posts],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=PostStats)
async def get_post_stats(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> PostStats:
    """
    Obtém estatísticas de postos.
    """
    repo = PostRepository(db)
    return await repo.get_stats()


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    """
    Busca posto por ID.
    """
    repo = PostRepository(db)
    post = await repo.get_by_id(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Posto não encontrado",
        )

    return PostResponse.model_validate(post)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    data: PostUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    """
    Atualiza um posto.
    """
    repo = PostRepository(db)
    post = await repo.update(post_id, data)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Posto não encontrado",
        )

    logger.info(f"Post atualizado por {current_user.email}: {post.id}")
    return PostResponse.model_validate(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Remove um posto (soft delete).
    """
    repo = PostRepository(db)
    deleted = await repo.delete(post_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Posto não encontrado",
        )

    logger.info(f"Post deletado por {current_user.email}: {post_id}")


@router.get("/contract/{contract_id}", response_model=list[PostResponse])
async def get_posts_by_contract(
    contract_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> list[PostResponse]:
    """
    Lista postos de um contrato.
    """
    repo = PostRepository(db)
    posts = await repo.get_by_contract(contract_id)

    return [PostResponse.model_validate(post) for post in posts]


@router.get("/client/{client_id}", response_model=list[PostResponse])
async def get_posts_by_client(
    client_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> list[PostResponse]:
    """
    Lista postos de um cliente.
    """
    repo = PostRepository(db)
    posts = await repo.get_by_client(client_id)

    return [PostResponse.model_validate(post) for post in posts]
