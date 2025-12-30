"""Repository para DocumentVersion."""

import logging
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from modules.ged.models.document_version import (
    DocumentVersion,
    VersionStatus,
    VersionType,
)
from modules.ged.schemas.document_version import DocumentVersionCreate

logger = logging.getLogger(__name__)


class DocumentVersionRepository:
    """Repository para operações de DocumentVersion."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: DocumentVersionCreate) -> DocumentVersion:
        """Cria uma nova versão."""
        # Marca versões anteriores como não atuais
        await self._mark_previous_versions_not_current(data.document_id)

        version = DocumentVersion(**data.model_dump())
        self.session.add(version)
        await self.session.flush()
        return version

    async def _mark_previous_versions_not_current(self, document_id: str) -> None:
        """Marca versões anteriores como não atuais."""
        query = select(DocumentVersion).where(
            and_(
                DocumentVersion.document_id == document_id,
                DocumentVersion.is_current == True,
            )
        )
        result = await self.session.execute(query)
        versions = result.scalars().all()

        for version in versions:
            version.is_current = False
            version.status = VersionStatus.ARQUIVADA

        await self.session.flush()

    async def get_by_id(self, version_id: str) -> Optional[DocumentVersion]:
        """Busca versão por ID."""
        result = await self.session.execute(
            select(DocumentVersion).where(DocumentVersion.id == version_id)
        )
        return result.scalar_one_or_none()

    async def get_by_document(
        self, document_id: str, include_archived: bool = False
    ) -> List[DocumentVersion]:
        """Retorna versões de um documento."""
        query = select(DocumentVersion).where(
            DocumentVersion.document_id == document_id
        )

        if not include_archived:
            query = query.where(DocumentVersion.status != VersionStatus.OBSOLETA)

        query = query.order_by(DocumentVersion.version_number.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_current(self, document_id: str) -> Optional[DocumentVersion]:
        """Retorna versão atual do documento."""
        result = await self.session.execute(
            select(DocumentVersion).where(
                and_(
                    DocumentVersion.document_id == document_id,
                    DocumentVersion.is_current == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_number(
        self, document_id: str, version_number: int
    ) -> Optional[DocumentVersion]:
        """Busca versão específica."""
        result = await self.session.execute(
            select(DocumentVersion).where(
                and_(
                    DocumentVersion.document_id == document_id,
                    DocumentVersion.version_number == version_number,
                )
            )
        )
        return result.scalar_one_or_none()

    async def set_as_current(self, version_id: str) -> Optional[DocumentVersion]:
        """Define versão como atual."""
        version = await self.get_by_id(version_id)
        if not version:
            return None

        # Marca versões anteriores como não atuais
        await self._mark_previous_versions_not_current(version.document_id)

        version.set_as_current()
        await self.session.flush()
        return version

    async def archive(self, version_id: str) -> Optional[DocumentVersion]:
        """Arquiva versão."""
        version = await self.get_by_id(version_id)
        if not version:
            return None
        version.archive()
        await self.session.flush()
        return version

    async def mark_as_obsolete(self, version_id: str) -> Optional[DocumentVersion]:
        """Marca versão como obsoleta."""
        version = await self.get_by_id(version_id)
        if not version:
            return None
        version.mark_as_obsolete()
        await self.session.flush()
        return version

    async def approve(
        self, version_id: str, approved_by: str
    ) -> Optional[DocumentVersion]:
        """Aprova versão."""
        version = await self.get_by_id(version_id)
        if not version:
            return None
        version.approve(approved_by)
        await self.session.flush()
        return version

    async def increment_view(self, version_id: str) -> None:
        """Incrementa visualizações."""
        version = await self.get_by_id(version_id)
        if version:
            version.increment_view()
            await self.session.flush()

    async def increment_download(self, version_id: str) -> None:
        """Incrementa downloads."""
        version = await self.get_by_id(version_id)
        if version:
            version.increment_download()
            await self.session.flush()

    async def get_version_count(self, document_id: str) -> int:
        """Retorna contagem de versões."""
        result = await self.session.execute(
            select(func.count()).where(DocumentVersion.document_id == document_id)
        )
        return result.scalar() or 0

    async def get_next_version_number(self, document_id: str) -> int:
        """Retorna próximo número de versão."""
        result = await self.session.execute(
            select(func.max(DocumentVersion.version_number)).where(
                DocumentVersion.document_id == document_id
            )
        )
        max_version = result.scalar() or 0
        return max_version + 1

    async def compare_versions(
        self, version_id_1: str, version_id_2: str
    ) -> Optional[dict]:
        """Compara duas versões."""
        version1 = await self.get_by_id(version_id_1)
        version2 = await self.get_by_id(version_id_2)

        if not version1 or not version2:
            return None

        return version1.compare_with(version2)

    async def delete_old_versions(
        self, document_id: str, keep_count: int = 10
    ) -> int:
        """Remove versões antigas, mantendo as N mais recentes."""
        versions = await self.get_by_document(document_id, include_archived=True)

        if len(versions) <= keep_count:
            return 0

        to_delete = versions[keep_count:]
        deleted = 0

        for version in to_delete:
            if not version.is_current:
                version.status = VersionStatus.OBSOLETA
                deleted += 1

        await self.session.flush()
        return deleted
