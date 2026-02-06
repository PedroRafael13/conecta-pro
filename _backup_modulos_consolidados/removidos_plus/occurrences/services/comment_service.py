"""Service para OccurrenceComment."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.occurrences.models.comment import CommentVisibility
from modules.occurrences.repositories.comment_repository import CommentRepository
from modules.occurrences.repositories.occurrence_repository import OccurrenceRepository
from modules.occurrences.schemas.comment import (
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    CommentUpdate,
)

logger = logging.getLogger(__name__)


class CommentService:
    """Service para operações de OccurrenceComment."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = CommentRepository(session)
        self.occurrence_repository = OccurrenceRepository(session)

    async def create(self, data: CommentCreate) -> CommentResponse:
        """Cria um novo comentário."""
        # Verificar se ocorrência existe
        occurrence = await self.occurrence_repository.get_by_id(data.occurrence_id)
        if not occurrence:
            raise ValueError(f"Ocorrência {data.occurrence_id} não encontrada")

        # Verificar se é primeira resposta de staff
        if data.is_staff and not occurrence.first_response_at:
            data.is_first_response = True
            occurrence.register_first_response()

        comment = await self.repository.create(data)

        # Incrementar contador de comentários
        occurrence.increment_comments()

        # Se for resposta, incrementar contador do pai
        if data.parent_id:
            parent = await self.repository.get_by_id(data.parent_id)
            if parent:
                parent.increment_replies()

        await self.session.commit()
        await self.session.refresh(comment)
        return CommentResponse.model_validate(comment)

    async def get_by_id(self, comment_id: str | UUID) -> Optional[CommentResponse]:
        """Busca comentário por ID."""
        comment = await self.repository.get_by_id(comment_id)
        if not comment:
            return None
        return CommentResponse.model_validate(comment)

    async def update(
        self, comment_id: str | UUID, data: CommentUpdate
    ) -> Optional[CommentResponse]:
        """Atualiza um comentário."""
        comment = await self.repository.update(comment_id, data)
        if not comment:
            return None
        await self.session.commit()
        return CommentResponse.model_validate(comment)

    async def delete(
        self, comment_id: str | UUID, deleted_by_id: str
    ) -> bool:
        """Deleta um comentário."""
        result = await self.repository.delete(comment_id, deleted_by_id)
        if result:
            await self.session.commit()
        return result

    async def list_by_occurrence(
        self,
        occurrence_id: str | UUID,
        visibility: Optional[CommentVisibility] = None,
        include_deleted: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> CommentListResponse:
        """Lista comentários de uma ocorrência."""
        skip = (page - 1) * page_size
        comments, total = await self.repository.list_by_occurrence(
            occurrence_id, visibility, include_deleted, skip, page_size
        )

        items = [CommentResponse.model_validate(c) for c in comments]
        return CommentListResponse(items=items, total=total, page=page, page_size=page_size)

    async def list_replies(
        self, parent_id: str | UUID, include_deleted: bool = False
    ) -> list[CommentResponse]:
        """Lista respostas de um comentário."""
        comments = await self.repository.list_replies(parent_id, include_deleted)
        return [CommentResponse.model_validate(c) for c in comments]

    async def get_solutions(self, occurrence_id: str | UUID) -> list[CommentResponse]:
        """Lista comentários marcados como solução."""
        comments = await self.repository.get_solutions(occurrence_id)
        return [CommentResponse.model_validate(c) for c in comments]

    async def get_pinned(self, occurrence_id: str | UUID) -> list[CommentResponse]:
        """Lista comentários fixados."""
        comments = await self.repository.get_pinned(occurrence_id)
        return [CommentResponse.model_validate(c) for c in comments]

    async def mark_as_solution(self, comment_id: str | UUID) -> Optional[CommentResponse]:
        """Marca comentário como solução."""
        comment = await self.repository.mark_as_solution(comment_id)
        if not comment:
            return None
        await self.session.commit()
        return CommentResponse.model_validate(comment)

    async def unmark_as_solution(self, comment_id: str | UUID) -> Optional[CommentResponse]:
        """Remove marcação de solução."""
        comment = await self.repository.unmark_as_solution(comment_id)
        if not comment:
            return None
        await self.session.commit()
        return CommentResponse.model_validate(comment)

    async def pin(self, comment_id: str | UUID) -> Optional[CommentResponse]:
        """Fixa comentário."""
        comment = await self.repository.pin(comment_id)
        if not comment:
            return None
        await self.session.commit()
        return CommentResponse.model_validate(comment)

    async def unpin(self, comment_id: str | UUID) -> Optional[CommentResponse]:
        """Desfixa comentário."""
        comment = await self.repository.unpin(comment_id)
        if not comment:
            return None
        await self.session.commit()
        return CommentResponse.model_validate(comment)

    async def add_like(self, comment_id: str | UUID) -> Optional[CommentResponse]:
        """Adiciona like."""
        comment = await self.repository.add_like(comment_id)
        if not comment:
            return None
        await self.session.commit()
        return CommentResponse.model_validate(comment)

    async def remove_like(self, comment_id: str | UUID) -> Optional[CommentResponse]:
        """Remove like."""
        comment = await self.repository.remove_like(comment_id)
        if not comment:
            return None
        await self.session.commit()
        return CommentResponse.model_validate(comment)

    async def get_first_response(self, occurrence_id: str | UUID) -> Optional[CommentResponse]:
        """Retorna primeiro comentário de staff."""
        comment = await self.repository.get_first_response(occurrence_id)
        if not comment:
            return None
        return CommentResponse.model_validate(comment)
