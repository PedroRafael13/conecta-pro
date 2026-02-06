"""Controller para OccurrenceComment."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from core.auth.dependencies import get_current_user, require_roles
from modules.occurrences.models.comment import CommentVisibility
from modules.occurrences.schemas.comment import (
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    CommentUpdate,
)
from modules.occurrences.services import CommentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/occurrence-comments", tags=["Occurrence Comments"])


async def get_comment_service(
    session: AsyncSession = Depends(get_async_session),
) -> CommentService:
    """Dependency para CommentService."""
    return CommentService(session)


@router.post(
    "/",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar comentario",
)
async def create_comment(
    data: CommentCreate,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(get_current_user),
) -> CommentResponse:
    """Cria um novo comentario em uma ocorrencia."""
    try:
        # Define autor se nao informado
        if not data.author_id:
            data.author_id = current_user.get("sub")
        if not data.author_name:
            data.author_name = current_user.get("name", "Usuario")

        # Verifica se e staff
        user_role = current_user.get("role", "morador")
        if user_role in ["admin", "sindico", "porteiro", "zelador"]:
            data.is_staff = True

        result = await service.create(data)
        logger.info(
            f"Comentario {result.id} criado na ocorrencia {data.occurrence_id} "
            f"por {current_user.get('email')}"
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar comentario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar comentario",
        )


@router.get(
    "/occurrence/{occurrence_id}",
    response_model=CommentListResponse,
    summary="Listar comentarios de uma ocorrencia",
)
async def list_comments_by_occurrence(
    occurrence_id: UUID,
    visibility: Optional[CommentVisibility] = Query(None, description="Visibilidade"),
    include_deleted: bool = Query(False, description="Incluir deletados"),
    page: int = Query(1, ge=1, description="Pagina"),
    page_size: int = Query(50, ge=1, le=200, description="Itens por pagina"),
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(get_current_user),
) -> CommentListResponse:
    """Lista comentarios de uma ocorrencia."""
    # Verifica permissao para ver comentarios internos
    user_role = current_user.get("role", "morador")
    if visibility == CommentVisibility.INTERNAL and user_role == "morador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissao para ver comentarios internos",
        )

    return await service.list_by_occurrence(
        occurrence_id, visibility, include_deleted, page, page_size
    )


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Buscar comentario por ID",
)
async def get_comment(
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> CommentResponse:
    """Busca comentario por ID."""
    result = await service.get_by_id(comment_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario nao encontrado",
        )
    return result


@router.get(
    "/{comment_id}/replies",
    response_model=list[CommentResponse],
    summary="Listar respostas de um comentario",
)
async def list_replies(
    comment_id: UUID,
    include_deleted: bool = Query(False, description="Incluir deletados"),
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[CommentResponse]:
    """Lista respostas de um comentario."""
    return await service.list_replies(comment_id, include_deleted)


@router.get(
    "/occurrence/{occurrence_id}/solutions",
    response_model=list[CommentResponse],
    summary="Listar comentarios solucao",
)
async def get_solutions(
    occurrence_id: UUID,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[CommentResponse]:
    """Lista comentarios marcados como solucao."""
    return await service.get_solutions(occurrence_id)


@router.get(
    "/occurrence/{occurrence_id}/pinned",
    response_model=list[CommentResponse],
    summary="Listar comentarios fixados",
)
async def get_pinned(
    occurrence_id: UUID,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[CommentResponse]:
    """Lista comentarios fixados."""
    return await service.get_pinned(occurrence_id)


@router.get(
    "/occurrence/{occurrence_id}/first-response",
    response_model=CommentResponse,
    summary="Primeira resposta de staff",
)
async def get_first_response(
    occurrence_id: UUID,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> CommentResponse:
    """Retorna o primeiro comentario de staff."""
    result = await service.get_first_response(occurrence_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma resposta de staff encontrada",
        )
    return result


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Atualizar comentario",
)
async def update_comment(
    comment_id: UUID,
    data: CommentUpdate,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(get_current_user),
) -> CommentResponse:
    """Atualiza um comentario."""
    # Verificar se e o autor
    existing = await service.get_by_id(comment_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario nao encontrado",
        )

    user_id = current_user.get("sub")
    user_role = current_user.get("role", "morador")
    if existing.author_id != user_id and user_role not in ["admin", "sindico"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissao para editar este comentario",
        )

    result = await service.update(comment_id, data)
    logger.info(f"Comentario {comment_id} atualizado por {current_user.get('email')}")
    return result


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar comentario",
)
async def delete_comment(
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(get_current_user),
) -> None:
    """Deleta um comentario (soft delete)."""
    # Verificar permissao
    existing = await service.get_by_id(comment_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario nao encontrado",
        )

    user_id = current_user.get("sub")
    user_role = current_user.get("role", "morador")
    if existing.author_id != user_id and user_role not in ["admin", "sindico"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissao para deletar este comentario",
        )

    result = await service.delete(comment_id, user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar comentario",
        )
    logger.info(f"Comentario {comment_id} deletado por {current_user.get('email')}")


@router.post(
    "/{comment_id}/solution",
    response_model=CommentResponse,
    summary="Marcar como solucao",
)
async def mark_as_solution(
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(require_roles(["admin", "sindico", "porteiro"])),
) -> CommentResponse:
    """Marca comentario como solucao."""
    result = await service.mark_as_solution(comment_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario nao encontrado",
        )
    logger.info(f"Comentario {comment_id} marcado como solucao por {current_user.get('email')}")
    return result


@router.delete(
    "/{comment_id}/solution",
    response_model=CommentResponse,
    summary="Remover marcacao de solucao",
)
async def unmark_as_solution(
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(require_roles(["admin", "sindico", "porteiro"])),
) -> CommentResponse:
    """Remove marcacao de solucao."""
    result = await service.unmark_as_solution(comment_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario nao encontrado",
        )
    logger.info(
        f"Marcacao de solucao removida do comentario {comment_id} "
        f"por {current_user.get('email')}"
    )
    return result


@router.post(
    "/{comment_id}/pin",
    response_model=CommentResponse,
    summary="Fixar comentario",
)
async def pin_comment(
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(require_roles(["admin", "sindico", "porteiro"])),
) -> CommentResponse:
    """Fixa um comentario."""
    result = await service.pin(comment_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario nao encontrado",
        )
    logger.info(f"Comentario {comment_id} fixado por {current_user.get('email')}")
    return result


@router.delete(
    "/{comment_id}/pin",
    response_model=CommentResponse,
    summary="Desfixar comentario",
)
async def unpin_comment(
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(require_roles(["admin", "sindico", "porteiro"])),
) -> CommentResponse:
    """Desfixa um comentario."""
    result = await service.unpin(comment_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario nao encontrado",
        )
    logger.info(f"Comentario {comment_id} desfixado por {current_user.get('email')}")
    return result


@router.post(
    "/{comment_id}/like",
    response_model=CommentResponse,
    summary="Curtir comentario",
)
async def like_comment(
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> CommentResponse:
    """Adiciona like a um comentario."""
    result = await service.add_like(comment_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario nao encontrado",
        )
    return result


@router.delete(
    "/{comment_id}/like",
    response_model=CommentResponse,
    summary="Remover curtida",
)
async def unlike_comment(
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> CommentResponse:
    """Remove like de um comentario."""
    result = await service.remove_like(comment_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario nao encontrado",
        )
    return result
