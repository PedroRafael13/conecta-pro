"""Repository para OccurrenceAttachment."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.occurrences.models.attachment import AttachmentType, OccurrenceAttachment
from modules.occurrences.schemas.attachment import AttachmentCreate

logger = logging.getLogger(__name__)


class AttachmentRepository:
    """Repository para operações de OccurrenceAttachment."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: AttachmentCreate) -> OccurrenceAttachment:
        """Cria um novo anexo."""
        attachment = OccurrenceAttachment(**data.model_dump(exclude_none=True))
        self.session.add(attachment)
        await self.session.flush()
        await self.session.refresh(attachment)
        logger.info(f"Anexo criado: {attachment.original_filename}")
        return attachment

    async def get_by_id(self, attachment_id: str | UUID) -> Optional[OccurrenceAttachment]:
        """Busca anexo por ID."""
        if isinstance(attachment_id, str):
            attachment_id = UUID(attachment_id)

        result = await self.session.execute(
            select(OccurrenceAttachment).where(OccurrenceAttachment.id == attachment_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, attachment_id: str | UUID) -> bool:
        """Deleta um anexo (soft delete)."""
        attachment = await self.get_by_id(attachment_id)
        if not attachment:
            return False

        attachment.soft_delete()
        await self.session.flush()
        return True

    async def list_by_occurrence(
        self,
        occurrence_id: str | UUID,
        file_type: Optional[AttachmentType] = None,
        is_public: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[OccurrenceAttachment], int]:
        """Lista anexos de uma ocorrência com paginação."""
        if isinstance(occurrence_id, str):
            occurrence_id = UUID(occurrence_id)

        base_query = select(OccurrenceAttachment).where(
            OccurrenceAttachment.occurrence_id == occurrence_id,
            OccurrenceAttachment.is_deleted.is_(False),
        )

        if file_type:
            base_query = base_query.where(OccurrenceAttachment.file_type == file_type)
        if is_public is not None:
            base_query = base_query.where(OccurrenceAttachment.is_public == is_public)

        # Contar total
        count_result = await self.session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar() or 0

        # Buscar com paginação
        query = base_query.order_by(OccurrenceAttachment.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def list_images(self, occurrence_id: str | UUID) -> list[OccurrenceAttachment]:
        """Lista imagens de uma ocorrência."""
        attachments, _ = await self.list_by_occurrence(occurrence_id, AttachmentType.IMAGE)
        return attachments

    async def list_documents(self, occurrence_id: str | UUID) -> list[OccurrenceAttachment]:
        """Lista documentos de uma ocorrência."""
        if isinstance(occurrence_id, str):
            occurrence_id = UUID(occurrence_id)

        result = await self.session.execute(
            select(OccurrenceAttachment)
            .where(
                and_(
                    OccurrenceAttachment.occurrence_id == occurrence_id,
                    OccurrenceAttachment.file_type.in_([
                        AttachmentType.DOCUMENT,
                        AttachmentType.SPREADSHEET,
                        AttachmentType.PDF,
                    ]),
                    OccurrenceAttachment.is_deleted.is_(False),
                )
            )
            .order_by(OccurrenceAttachment.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_media(self, occurrence_id: str | UUID) -> list[OccurrenceAttachment]:
        """Lista mídias de uma ocorrência."""
        if isinstance(occurrence_id, str):
            occurrence_id = UUID(occurrence_id)

        result = await self.session.execute(
            select(OccurrenceAttachment)
            .where(
                and_(
                    OccurrenceAttachment.occurrence_id == occurrence_id,
                    OccurrenceAttachment.file_type.in_([
                        AttachmentType.IMAGE,
                        AttachmentType.VIDEO,
                        AttachmentType.AUDIO,
                    ]),
                    OccurrenceAttachment.is_deleted.is_(False),
                )
            )
            .order_by(OccurrenceAttachment.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_by_occurrence(self, occurrence_id: str | UUID) -> int:
        """Conta anexos de uma ocorrência."""
        if isinstance(occurrence_id, str):
            occurrence_id = UUID(occurrence_id)

        result = await self.session.execute(
            select(func.count())
            .select_from(OccurrenceAttachment)
            .where(
                and_(
                    OccurrenceAttachment.occurrence_id == occurrence_id,
                    OccurrenceAttachment.is_deleted.is_(False),
                )
            )
        )
        return result.scalar() or 0

    async def get_total_size(self, occurrence_id: str | UUID) -> int:
        """Retorna tamanho total dos anexos."""
        if isinstance(occurrence_id, str):
            occurrence_id = UUID(occurrence_id)

        result = await self.session.execute(
            select(func.sum(OccurrenceAttachment.file_size))
            .where(
                and_(
                    OccurrenceAttachment.occurrence_id == occurrence_id,
                    OccurrenceAttachment.is_deleted.is_(False),
                )
            )
        )
        return result.scalar() or 0

    async def mark_as_scanned(
        self, attachment_id: str | UUID, is_safe: bool, result: str = None
    ) -> Optional[OccurrenceAttachment]:
        """Marca anexo como escaneado."""
        attachment = await self.get_by_id(attachment_id)
        if not attachment:
            return None

        attachment.mark_as_scanned(is_safe, result)
        await self.session.flush()
        return attachment

    async def get_unsafe(self) -> list[OccurrenceAttachment]:
        """Lista anexos marcados como inseguros."""
        result = await self.session.execute(
            select(OccurrenceAttachment)
            .where(
                and_(
                    OccurrenceAttachment.is_safe.is_(False),
                    OccurrenceAttachment.is_deleted.is_(False),
                )
            )
            .order_by(OccurrenceAttachment.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_pending_scan(self) -> list[OccurrenceAttachment]:
        """Lista anexos pendentes de scan."""
        result = await self.session.execute(
            select(OccurrenceAttachment)
            .where(
                and_(
                    OccurrenceAttachment.is_scanned.is_(False),
                    OccurrenceAttachment.is_deleted.is_(False),
                )
            )
            .order_by(OccurrenceAttachment.created_at.asc())
        )
        return list(result.scalars().all())

    async def find_duplicates(self, file_hash: str) -> list[OccurrenceAttachment]:
        """Busca anexos duplicados por hash."""
        result = await self.session.execute(
            select(OccurrenceAttachment)
            .where(
                and_(
                    OccurrenceAttachment.file_hash == file_hash,
                    OccurrenceAttachment.is_deleted.is_(False),
                )
            )
            .order_by(OccurrenceAttachment.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_stats_by_type(self, occurrence_id: str | UUID = None) -> dict:
        """Retorna estatísticas por tipo de arquivo."""
        query = select(
            OccurrenceAttachment.file_type,
            func.count().label("count"),
            func.sum(OccurrenceAttachment.file_size).label("total_size"),
        ).where(OccurrenceAttachment.is_deleted.is_(False))

        if occurrence_id:
            if isinstance(occurrence_id, str):
                occurrence_id = UUID(occurrence_id)
            query = query.where(OccurrenceAttachment.occurrence_id == occurrence_id)

        query = query.group_by(OccurrenceAttachment.file_type)

        result = await self.session.execute(query)
        rows = result.all()

        stats = {}
        for row in rows:
            file_type = row.file_type.value if row.file_type else "unknown"
            stats[file_type] = {
                "count": row.count,
                "total_size": row.total_size or 0,
            }

        return stats
