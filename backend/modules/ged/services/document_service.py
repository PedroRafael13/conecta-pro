"""Service para Document."""

import logging
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from modules.ged.repositories.document_repository import DocumentRepository
from modules.ged.repositories.folder_repository import FolderRepository
from modules.ged.repositories.document_version_repository import (
    DocumentVersionRepository,
)
from modules.ged.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentFilter,
    DocumentResponse,
    DocumentListResponse,
    DocumentStats,
)
from modules.ged.schemas.document_version import DocumentVersionCreate

logger = logging.getLogger(__name__)


class DocumentService:
    """Service para operações de Document."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = DocumentRepository(session)
        self.folder_repository = FolderRepository(session)
        self.version_repository = DocumentVersionRepository(session)

    async def create(self, data: DocumentCreate) -> DocumentResponse:
        """Cria um novo documento."""
        # Verifica se pasta existe
        folder = await self.folder_repository.get_by_id(data.folder_id)
        if not folder:
            raise ValueError("Pasta não encontrada")

        # Verifica extensão permitida
        if not folder.is_extension_allowed(data.file_extension):
            raise ValueError(
                f"Extensão .{data.file_extension} não permitida nesta pasta"
            )

        # Verifica tamanho
        if not folder.is_size_allowed(data.file_size_bytes):
            raise ValueError(
                f"Arquivo excede o limite de {folder.max_file_size_mb}MB"
            )

        # Verifica duplicidade por checksum
        existing = await self.repository.get_by_checksum(data.checksum)
        if existing:
            logger.warning("Documento duplicado detectado: %s", data.checksum)

        document = await self.repository.create(data)

        # Cria primeira versão
        version_data = DocumentVersionCreate(
            document_id=document.id,
            version_number=1,
            file_name=data.file_name,
            file_path=data.file_path,
            file_size_bytes=data.file_size_bytes,
            mime_type=data.mime_type,
            checksum=data.checksum,
            created_by=data.created_by,
            thumbnail_path=data.thumbnail_path,
            change_summary="Versão inicial",
        )
        await self.version_repository.create(version_data)

        # Atualiza estatísticas da pasta
        await self.folder_repository.update_document_stats(
            data.folder_id, data.file_size_bytes, 1
        )

        await self.session.commit()
        logger.info("Documento criado: %s - %s", document.id, document.title)
        return DocumentResponse.model_validate(document)

    async def get_by_id(self, document_id: str) -> Optional[DocumentResponse]:
        """Busca documento por ID."""
        document = await self.repository.get_by_id(document_id)
        if not document:
            return None
        return DocumentResponse.model_validate(document)

    async def get_by_code(self, code: str) -> Optional[DocumentResponse]:
        """Busca documento por código."""
        document = await self.repository.get_by_code(code)
        if not document:
            return None
        return DocumentResponse.model_validate(document)

    async def update(
        self, document_id: str, data: DocumentUpdate
    ) -> Optional[DocumentResponse]:
        """Atualiza um documento."""
        document = await self.repository.update(document_id, data)
        if not document:
            return None
        await self.session.commit()
        logger.info("Documento atualizado: %s", document_id)
        return DocumentResponse.model_validate(document)

    async def delete(self, document_id: str) -> bool:
        """Remove documento (soft delete)."""
        document = await self.repository.get_by_id(document_id)
        if not document:
            return False

        # Atualiza estatísticas da pasta
        await self.folder_repository.update_document_stats(
            document.folder_id, -document.file_size_bytes, -1
        )

        result = await self.repository.soft_delete(document_id)
        if result:
            await self.session.commit()
            logger.info("Documento removido: %s", document_id)
        return result

    async def list(
        self,
        filters: Optional[DocumentFilter] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> DocumentListResponse:
        """Lista documentos com filtros e paginação."""
        skip = (page - 1) * page_size
        documents, total = await self.repository.list_with_filters(
            filters=filters,
            skip=skip,
            limit=page_size,
            order_by=order_by,
            order_desc=order_desc,
        )

        pages = (total + page_size - 1) // page_size if total > 0 else 0

        return DocumentListResponse(
            items=[DocumentResponse.model_validate(d) for d in documents],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def get_by_folder(
        self, folder_id: str, page: int = 1, page_size: int = 50
    ) -> List[DocumentResponse]:
        """Retorna documentos de uma pasta."""
        skip = (page - 1) * page_size
        documents = await self.repository.get_by_folder(folder_id, skip, page_size)
        return [DocumentResponse.model_validate(d) for d in documents]

    async def get_pending_approval(
        self, condominium_id: str = None, page: int = 1, page_size: int = 20
    ) -> List[DocumentResponse]:
        """Retorna documentos pendentes de aprovação."""
        skip = (page - 1) * page_size
        documents = await self.repository.get_pending_approval(
            condominium_id, skip, page_size
        )
        return [DocumentResponse.model_validate(d) for d in documents]

    async def get_pending_signature(
        self, condominium_id: str = None, page: int = 1, page_size: int = 20
    ) -> List[DocumentResponse]:
        """Retorna documentos pendentes de assinatura."""
        skip = (page - 1) * page_size
        documents = await self.repository.get_pending_signature(
            condominium_id, skip, page_size
        )
        return [DocumentResponse.model_validate(d) for d in documents]

    async def get_expired(
        self, condominium_id: str = None, page: int = 1, page_size: int = 20
    ) -> List[DocumentResponse]:
        """Retorna documentos expirados."""
        skip = (page - 1) * page_size
        documents = await self.repository.get_expired(condominium_id, skip, page_size)
        return [DocumentResponse.model_validate(d) for d in documents]

    async def get_expiring_soon(
        self, days: int = 30, condominium_id: str = None
    ) -> List[DocumentResponse]:
        """Retorna documentos prestes a expirar."""
        documents = await self.repository.get_expiring_soon(days, condominium_id)
        return [DocumentResponse.model_validate(d) for d in documents]

    async def approve(
        self, document_id: str, approved_by: str
    ) -> Optional[DocumentResponse]:
        """Aprova documento."""
        document = await self.repository.approve(document_id, approved_by)
        if not document:
            return None
        await self.session.commit()
        logger.info("Documento aprovado: %s por %s", document_id, approved_by)
        return DocumentResponse.model_validate(document)

    async def reject(
        self, document_id: str, reason: str
    ) -> Optional[DocumentResponse]:
        """Rejeita documento."""
        document = await self.repository.reject(document_id, reason)
        if not document:
            return None
        await self.session.commit()
        logger.info("Documento rejeitado: %s", document_id)
        return DocumentResponse.model_validate(document)

    async def publish(self, document_id: str) -> Optional[DocumentResponse]:
        """Publica documento."""
        document = await self.repository.publish(document_id)
        if not document:
            return None
        await self.session.commit()
        logger.info("Documento publicado: %s", document_id)
        return DocumentResponse.model_validate(document)

    async def archive(
        self, document_id: str, archived_by: str
    ) -> Optional[DocumentResponse]:
        """Arquiva documento."""
        document = await self.repository.archive(document_id, archived_by)
        if not document:
            return None
        await self.session.commit()
        logger.info("Documento arquivado: %s", document_id)
        return DocumentResponse.model_validate(document)

    async def unarchive(self, document_id: str) -> Optional[DocumentResponse]:
        """Desarquiva documento."""
        document = await self.repository.unarchive(document_id)
        if not document:
            return None
        await self.session.commit()
        logger.info("Documento desarquivado: %s", document_id)
        return DocumentResponse.model_validate(document)

    async def move(
        self, document_id: str, folder_id: str
    ) -> Optional[DocumentResponse]:
        """Move documento para outra pasta."""
        document = await self.repository.get_by_id(document_id)
        if not document:
            return None

        # Verifica se pasta destino existe
        folder = await self.folder_repository.get_by_id(folder_id)
        if not folder:
            raise ValueError("Pasta destino não encontrada")

        # Atualiza estatísticas das pastas
        await self.folder_repository.update_document_stats(
            document.folder_id, -document.file_size_bytes, -1
        )
        await self.folder_repository.update_document_stats(
            folder_id, document.file_size_bytes, 1
        )

        document = await self.repository.move(document_id, folder_id)
        await self.session.commit()
        logger.info("Documento movido: %s para pasta %s", document_id, folder_id)
        return DocumentResponse.model_validate(document)

    async def view(self, document_id: str) -> Optional[DocumentResponse]:
        """Registra visualização do documento."""
        await self.repository.increment_view(document_id)
        await self.session.commit()
        document = await self.repository.get_by_id(document_id)
        return DocumentResponse.model_validate(document) if document else None

    async def download(self, document_id: str) -> Optional[DocumentResponse]:
        """Registra download do documento."""
        await self.repository.increment_download(document_id)
        await self.session.commit()
        document = await self.repository.get_by_id(document_id)
        return DocumentResponse.model_validate(document) if document else None

    async def search(
        self, query: str, condominium_id: str = None, limit: int = 20
    ) -> List[DocumentResponse]:
        """Busca full-text em documentos."""
        documents = await self.repository.search_fulltext(query, condominium_id, limit)
        return [DocumentResponse.model_validate(d) for d in documents]

    async def get_stats(self, condominium_id: str = None) -> DocumentStats:
        """Retorna estatísticas de documentos."""
        stats = await self.repository.get_stats(condominium_id)
        return DocumentStats(**stats)

    async def submit_for_approval(
        self, document_id: str
    ) -> Optional[DocumentResponse]:
        """Submete documento para aprovação."""
        document = await self.repository.get_by_id(document_id)
        if not document:
            return None

        document.submit_for_approval()
        await self.session.commit()
        logger.info("Documento submetido para aprovação: %s", document_id)
        return DocumentResponse.model_validate(document)

    async def create_new_version(
        self,
        document_id: str,
        file_name: str,
        file_path: str,
        file_size_bytes: int,
        mime_type: str,
        checksum: str,
        created_by: str,
        change_summary: str = None,
    ) -> Optional[DocumentResponse]:
        """Cria nova versão do documento."""
        document = await self.repository.get_by_id(document_id)
        if not document:
            return None

        # Cria nova versão
        version_number = document.create_new_version()
        version_data = DocumentVersionCreate(
            document_id=document_id,
            version_number=version_number,
            file_name=file_name,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            mime_type=mime_type,
            checksum=checksum,
            created_by=created_by,
            change_summary=change_summary or f"Versão {version_number}",
        )
        await self.version_repository.create(version_data)

        # Atualiza documento
        document.file_name = file_name
        document.file_path = file_path
        document.file_size_bytes = file_size_bytes
        document.checksum = checksum

        await self.session.commit()
        logger.info(
            "Nova versão criada: %s v%s", document_id, version_number
        )
        return DocumentResponse.model_validate(document)

    async def check_expiry(self) -> int:
        """Verifica e marca documentos expirados."""
        expired_docs = await self.repository.get_expiring_soon(days=0)
        count = 0

        for doc in expired_docs:
            if doc.check_expiry():
                count += 1

        await self.session.commit()
        logger.info("%s documentos marcados como expirados", count)
        return count
