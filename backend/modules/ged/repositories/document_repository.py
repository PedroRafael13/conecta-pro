"""Repository para Document."""

import logging
from typing import Optional, List, Tuple
from uuid import uuid4
from datetime import datetime

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from modules.ged.models.document import Document, DocumentStatus, DocumentType
from modules.ged.schemas.document import DocumentCreate, DocumentUpdate, DocumentFilter

logger = logging.getLogger(__name__)


class DocumentRepository:
    """Repository para operações de Document."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    def _generate_code(self) -> str:
        """Gera código único para documento."""
        return f"DOC-{str(uuid4())[:8].upper()}"

    async def create(self, data: DocumentCreate) -> Document:
        """Cria um novo documento."""
        document = Document(
            code=self._generate_code(),
            **data.model_dump(),
        )
        self.session.add(document)
        await self.session.flush()
        return document

    async def get_by_id(self, document_id: str) -> Optional[Document]:
        """Busca documento por ID."""
        result = await self.session.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Document]:
        """Busca documento por código."""
        result = await self.session.execute(
            select(Document).where(Document.code == code)
        )
        return result.scalar_one_or_none()

    async def get_by_checksum(self, checksum: str) -> Optional[Document]:
        """Busca documento por checksum."""
        result = await self.session.execute(
            select(Document).where(Document.checksum == checksum)
        )
        return result.scalar_one_or_none()

    async def update(
        self, document_id: str, data: DocumentUpdate
    ) -> Optional[Document]:
        """Atualiza um documento."""
        document = await self.get_by_id(document_id)
        if not document:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)

        await self.session.flush()
        return document

    async def soft_delete(self, document_id: str) -> bool:
        """Remove documento (soft delete)."""
        document = await self.get_by_id(document_id)
        if not document:
            return False
        document.soft_delete()
        await self.session.flush()
        return True

    async def list_with_filters(
        self,
        filters: Optional[DocumentFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> Tuple[List[Document], int]:
        """Lista documentos com filtros e paginação."""
        query = select(Document).where(Document.status != DocumentStatus.EXCLUIDO)

        if filters:
            if filters.folder_id:
                query = query.where(Document.folder_id == filters.folder_id)
            if filters.document_type:
                query = query.where(Document.document_type == filters.document_type)
            if filters.category:
                query = query.where(Document.category == filters.category)
            if filters.status:
                query = query.where(Document.status == filters.status)
            if filters.confidentiality:
                query = query.where(Document.confidentiality == filters.confidentiality)
            if filters.file_type:
                query = query.where(Document.file_type == filters.file_type)
            if filters.condominium_id:
                query = query.where(Document.condominium_id == filters.condominium_id)
            if filters.contract_id:
                query = query.where(Document.contract_id == filters.contract_id)
            if filters.owner_id:
                query = query.where(Document.owner_id == filters.owner_id)
            if filters.is_public is not None:
                query = query.where(Document.is_public == filters.is_public)
            if filters.is_signed is not None:
                query = query.where(Document.is_signed == filters.is_signed)
            if filters.requires_approval is not None:
                query = query.where(
                    Document.requires_approval == filters.requires_approval
                )
            if filters.requires_signature is not None:
                query = query.where(
                    Document.requires_signature == filters.requires_signature
                )
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.where(
                    or_(
                        Document.title.ilike(search_term),
                        Document.description.ilike(search_term),
                        Document.code.ilike(search_term),
                        Document.file_name.ilike(search_term),
                        Document.ocr_text.ilike(search_term),
                    )
                )
            if filters.created_from:
                query = query.where(Document.created_at >= filters.created_from)
            if filters.created_to:
                query = query.where(Document.created_at <= filters.created_to)

        # Contagem total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Ordenação
        order_column = getattr(Document, order_by, Document.created_at)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Paginação
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        documents = result.scalars().all()

        return list(documents), total

    async def get_by_folder(
        self, folder_id: str, skip: int = 0, limit: int = 50
    ) -> List[Document]:
        """Retorna documentos de uma pasta."""
        query = (
            select(Document)
            .where(
                and_(
                    Document.folder_id == folder_id,
                    Document.status != DocumentStatus.EXCLUIDO,
                )
            )
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending_approval(
        self, condominium_id: str = None, skip: int = 0, limit: int = 20
    ) -> List[Document]:
        """Retorna documentos pendentes de aprovação."""
        query = select(Document).where(
            Document.status == DocumentStatus.PENDENTE_APROVACAO
        )
        if condominium_id:
            query = query.where(Document.condominium_id == condominium_id)

        query = query.order_by(Document.created_at.asc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending_signature(
        self, condominium_id: str = None, skip: int = 0, limit: int = 20
    ) -> List[Document]:
        """Retorna documentos pendentes de assinatura."""
        query = select(Document).where(
            and_(
                Document.requires_signature == True,
                Document.is_signed == False,
                Document.status != DocumentStatus.EXCLUIDO,
            )
        )
        if condominium_id:
            query = query.where(Document.condominium_id == condominium_id)

        query = query.order_by(Document.signature_deadline.asc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_expired(
        self, condominium_id: str = None, skip: int = 0, limit: int = 20
    ) -> List[Document]:
        """Retorna documentos expirados."""
        query = select(Document).where(Document.status == DocumentStatus.EXPIRADO)
        if condominium_id:
            query = query.where(Document.condominium_id == condominium_id)

        query = query.order_by(Document.valid_until.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_expiring_soon(
        self, days: int = 30, condominium_id: str = None
    ) -> List[Document]:
        """Retorna documentos prestes a expirar."""
        from datetime import date, timedelta

        expiry_date = date.today() + timedelta(days=days)
        query = select(Document).where(
            and_(
                Document.valid_until <= expiry_date,
                Document.valid_until >= date.today(),
                Document.is_perpetual == False,
                Document.status.notin_(
                    [DocumentStatus.EXCLUIDO, DocumentStatus.EXPIRADO]
                ),
            )
        )
        if condominium_id:
            query = query.where(Document.condominium_id == condominium_id)

        result = await self.session.execute(query.order_by(Document.valid_until.asc()))
        return list(result.scalars().all())

    async def approve(
        self, document_id: str, approved_by: str
    ) -> Optional[Document]:
        """Aprova documento."""
        document = await self.get_by_id(document_id)
        if not document:
            return None
        document.approve(approved_by)
        await self.session.flush()
        return document

    async def reject(
        self, document_id: str, reason: str
    ) -> Optional[Document]:
        """Rejeita documento."""
        document = await self.get_by_id(document_id)
        if not document:
            return None
        document.reject(reason)
        await self.session.flush()
        return document

    async def publish(self, document_id: str) -> Optional[Document]:
        """Publica documento."""
        document = await self.get_by_id(document_id)
        if not document:
            return None
        document.publish()
        await self.session.flush()
        return document

    async def archive(
        self, document_id: str, archived_by: str
    ) -> Optional[Document]:
        """Arquiva documento."""
        document = await self.get_by_id(document_id)
        if not document:
            return None
        document.archive(archived_by)
        await self.session.flush()
        return document

    async def unarchive(self, document_id: str) -> Optional[Document]:
        """Desarquiva documento."""
        document = await self.get_by_id(document_id)
        if not document:
            return None
        document.unarchive()
        await self.session.flush()
        return document

    async def move(
        self, document_id: str, folder_id: str
    ) -> Optional[Document]:
        """Move documento para outra pasta."""
        document = await self.get_by_id(document_id)
        if not document:
            return None
        document.folder_id = folder_id
        await self.session.flush()
        return document

    async def increment_view(self, document_id: str) -> None:
        """Incrementa visualizações."""
        document = await self.get_by_id(document_id)
        if document:
            document.increment_view()
            await self.session.flush()

    async def increment_download(self, document_id: str) -> None:
        """Incrementa downloads."""
        document = await self.get_by_id(document_id)
        if document:
            document.increment_download()
            await self.session.flush()

    async def set_ocr_result(
        self, document_id: str, text: str, confidence: float
    ) -> Optional[Document]:
        """Define resultado do OCR."""
        document = await self.get_by_id(document_id)
        if not document:
            return None
        document.set_ocr_result(text, confidence)
        await self.session.flush()
        return document

    async def mark_as_indexed(
        self, document_id: str, keywords: List[str] = None
    ) -> Optional[Document]:
        """Marca como indexado."""
        document = await self.get_by_id(document_id)
        if not document:
            return None
        document.mark_as_indexed(keywords)
        await self.session.flush()
        return document

    async def search_fulltext(
        self, query: str, condominium_id: str = None, limit: int = 20
    ) -> List[Document]:
        """Busca full-text em documentos."""
        search_term = f"%{query}%"
        stmt = select(Document).where(
            and_(
                Document.status != DocumentStatus.EXCLUIDO,
                or_(
                    Document.title.ilike(search_term),
                    Document.description.ilike(search_term),
                    Document.ocr_text.ilike(search_term),
                    Document.file_name.ilike(search_term),
                ),
            )
        )
        if condominium_id:
            stmt = stmt.where(Document.condominium_id == condominium_id)

        result = await self.session.execute(
            stmt.order_by(Document.view_count.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_stats(self, condominium_id: str = None) -> dict:
        """Retorna estatísticas de documentos."""
        query = select(Document).where(Document.status != DocumentStatus.EXCLUIDO)
        if condominium_id:
            query = query.where(Document.condominium_id == condominium_id)

        result = await self.session.execute(query)
        documents = result.scalars().all()

        stats = {
            "total_documents": len(documents),
            "by_status": {},
            "by_type": {},
            "by_category": {},
            "by_confidentiality": {},
            "total_size_bytes": 0,
            "total_size_mb": 0,
            "pending_approval": 0,
            "pending_signature": 0,
            "expired": 0,
            "expiring_soon": 0,
            "avg_views": 0,
            "avg_downloads": 0,
        }

        total_views = 0
        total_downloads = 0

        for doc in documents:
            # Por status
            status_val = doc.status.value
            stats["by_status"][status_val] = stats["by_status"].get(status_val, 0) + 1

            # Por tipo
            type_val = doc.document_type.value
            stats["by_type"][type_val] = stats["by_type"].get(type_val, 0) + 1

            # Por categoria
            cat_val = doc.category.value
            stats["by_category"][cat_val] = stats["by_category"].get(cat_val, 0) + 1

            # Por confidencialidade
            conf_val = doc.confidentiality.value
            stats["by_confidentiality"][conf_val] = (
                stats["by_confidentiality"].get(conf_val, 0) + 1
            )

            # Tamanho
            stats["total_size_bytes"] += doc.file_size_bytes

            # Contadores especiais
            if doc.is_pending_approval:
                stats["pending_approval"] += 1
            if doc.is_pending_signature:
                stats["pending_signature"] += 1
            if doc.is_expired:
                stats["expired"] += 1
            if doc.days_until_expiry and 0 < doc.days_until_expiry <= 30:
                stats["expiring_soon"] += 1

            total_views += doc.view_count
            total_downloads += doc.download_count

        if documents:
            stats["avg_views"] = round(total_views / len(documents), 2)
            stats["avg_downloads"] = round(total_downloads / len(documents), 2)

        stats["total_size_mb"] = round(stats["total_size_bytes"] / (1024 * 1024), 2)
        return stats
