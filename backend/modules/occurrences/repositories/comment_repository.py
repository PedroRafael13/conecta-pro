"""Repository para OccurrenceComment."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.occurrences.models.comment import CommentVisibility, OccurrenceComment
from modules.occurrences.schemas.comment import CommentCreate, CommentUpdate

logger = logging.getLogger(__name__)


class CommentRepository:
    """Repository para operações de OccurrenceComment."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: CommentCreate) -> OccurrenceComment:
        """Cria um novo comentário."""
        comment = OccurrenceComment(**data.model_dump(exclude_none=True))
        self.session.add(comment)
        await self.session.flush()
        await self.session.refresh(comment)
        logger.info(f"Comentário criado para ocorrência: {comment.occurrence_id}")
        return comment

    async def get_by_id(self, comment_id: str | UUID) -> Optional[OccurrenceComment]:
        """Busca comentário por ID."""
        if isinstance(comment_id, str):
            comment_id = UUID(comment_id)

        result = await self.session.execute(
            select(OccurrenceComment).where(OccurrenceComment.id == comment_id)
        )
        return result.scalar_one_or_none()

    async def update(
        self, comment_id: str | UUID, data: CommentUpdate
    ) -> Optional[OccurrenceComment]:
        """Atualiza um comentário."""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return None

        if data.content:
            comment.edit(data.content)
        if data.visibility:
            comment.visibility = data.visibility

        await self.session.flush()
        await self.session.refresh(comment)
        return comment

    async def delete(self, comment_id: str | UUID, deleted_by_id: str) -> bool:
        """Deleta um comentário (soft delete)."""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return False

        comment.soft_delete(deleted_by_id)
        await self.session.flush()
        return True

    async def list_by_occurrence(
        self,
        occurrence_id: str | UUID,
        visibility: Optional[CommentVisibility] = None,
        include_deleted: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[OccurrenceComment], int]:
        """Lista comentários de uma ocorrência."""
        if isinstance(occurrence_id, str):
            occurrence_id = UUID(occurrence_id)

        query = select(OccurrenceComment).where(
            OccurrenceComment.occurrence_id == occurrence_id
        )

        if not include_deleted:
            query = query.where(OccurrenceComment.is_deleted.is_(False))
        if visibility:
            query = query.where(OccurrenceComment.visibility == visibility)

        # Only root comments (not replies)
        query = query.where(OccurrenceComment.parent_id.is_(None))

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Order and paginate
        query = query.order_by(OccurrenceComment.created_at.asc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        comments = list(result.scalars().all())

        return comments, total

    async def list_replies(
        self, parent_id: str | UUID, include_deleted: bool = False
    ) -> list[OccurrenceComment]:
        """Lista respostas de um comentário."""
        if isinstance(parent_id, str):
            parent_id = UUID(parent_id)

        query = select(OccurrenceComment).where(
            OccurrenceComment.parent_id == parent_id
        )

        if not include_deleted:
            query = query.where(OccurrenceComment.is_deleted.is_(False))

        query = query.order_by(OccurrenceComment.created_at.asc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_author(
        self, author_id: str, skip: int = 0, limit: int = 50
    ) -> list[OccurrenceComment]:
        """Lista comentários de um autor."""
        result = await self.session.execute(
            select(OccurrenceComment)
            .where(
                and_(
                    OccurrenceComment.author_id == author_id,
                    OccurrenceComment.is_deleted.is_(False),
                )
            )
            .order_by(OccurrenceComment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_solutions(
        self, occurrence_id: str | UUID
    ) -> list[OccurrenceComment]:
        """Lista comentários marcados como solução."""
        if isinstance(occurrence_id, str):
            occurrence_id = UUID(occurrence_id)

        result = await self.session.execute(
            select(OccurrenceComment)
            .where(
                and_(
                    OccurrenceComment.occurrence_id == occurrence_id,
                    OccurrenceComment.is_solution.is_(True),
                    OccurrenceComment.is_deleted.is_(False),
                )
            )
            .order_by(OccurrenceComment.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_pinned(
        self, occurrence_id: str | UUID
    ) -> list[OccurrenceComment]:
        """Lista comentários fixados."""
        if isinstance(occurrence_id, str):
            occurrence_id = UUID(occurrence_id)

        result = await self.session.execute(
            select(OccurrenceComment)
            .where(
                and_(
                    OccurrenceComment.occurrence_id == occurrence_id,
                    OccurrenceComment.is_pinned.is_(True),
                    OccurrenceComment.is_deleted.is_(False),
                )
            )
            .order_by(OccurrenceComment.created_at.asc())
        )
        return list(result.scalars().all())

    async def mark_as_solution(self, comment_id: str | UUID) -> Optional[OccurrenceComment]:
        """Marca comentário como solução."""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return None

        comment.mark_as_solution()
        await self.session.flush()
        return comment

    async def unmark_as_solution(self, comment_id: str | UUID) -> Optional[OccurrenceComment]:
        """Remove marcação de solução."""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return None

        comment.unmark_as_solution()
        await self.session.flush()
        return comment

    async def pin(self, comment_id: str | UUID) -> Optional[OccurrenceComment]:
        """Fixa comentário."""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return None

        comment.pin()
        await self.session.flush()
        return comment

    async def unpin(self, comment_id: str | UUID) -> Optional[OccurrenceComment]:
        """Desfixa comentário."""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return None

        comment.unpin()
        await self.session.flush()
        return comment

    async def add_like(self, comment_id: str | UUID) -> Optional[OccurrenceComment]:
        """Adiciona like."""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return None

        comment.add_like()
        await self.session.flush()
        return comment

    async def remove_like(self, comment_id: str | UUID) -> Optional[OccurrenceComment]:
        """Remove like."""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return None

        comment.remove_like()
        await self.session.flush()
        return comment

    async def count_by_occurrence(self, occurrence_id: str | UUID) -> int:
        """Conta comentários de uma ocorrência."""
        if isinstance(occurrence_id, str):
            occurrence_id = UUID(occurrence_id)

        result = await self.session.execute(
            select(func.count())
            .select_from(OccurrenceComment)
            .where(
                and_(
                    OccurrenceComment.occurrence_id == occurrence_id,
                    OccurrenceComment.is_deleted.is_(False),
                )
            )
        )
        return result.scalar() or 0

    async def get_first_response(
        self, occurrence_id: str | UUID
    ) -> Optional[OccurrenceComment]:
        """Retorna primeiro comentário de staff."""
        if isinstance(occurrence_id, str):
            occurrence_id = UUID(occurrence_id)

        result = await self.session.execute(
            select(OccurrenceComment)
            .where(
                and_(
                    OccurrenceComment.occurrence_id == occurrence_id,
                    OccurrenceComment.is_staff.is_(True),
                    OccurrenceComment.is_deleted.is_(False),
                )
            )
            .order_by(OccurrenceComment.created_at.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()
