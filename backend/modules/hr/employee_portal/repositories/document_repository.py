"""Repository para documentos do funcionário."""

import logging
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.employee_portal.models import (
    EmployeeDocument,
    DocumentType,
    DocumentStatus,
)
from modules.hr.employee_portal.schemas import DocumentCreate, DocumentUpdate

logger = logging.getLogger(__name__)


class DocumentRepository:
    """Repository para operações de documentos."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: DocumentCreate,
        condominio_id: UUID,
        *,
        created_by: Optional[UUID] = None,
    ) -> EmployeeDocument:
        """Cria novo documento."""
        document = EmployeeDocument(
            id=uuid4(),
            condominio_id=condominio_id,
            employee_id=data.employee_id,
            document_code=self._generate_code(),
            document_type=data.document_type.value,
            status=DocumentStatus.DRAFT.value,
            title=data.title,
            description=data.description,
            category=data.category,
            tags=data.tags,
            file_name=data.file_name,
            file_path=data.file_path,
            file_size=data.file_size,
            file_type=data.file_type,
            file_hash=data.file_hash,
            reference_date=data.reference_date,
            reference_month=data.reference_month,
            reference_year=data.reference_year,
            valid_from=data.valid_from,
            valid_until=data.valid_until,
            is_perpetual=data.is_perpetual,
            is_visible=data.is_visible,
            requires_acknowledgement=data.requires_acknowledgement,
            is_confidential=data.is_confidential,
            is_mandatory=data.is_mandatory,
            requires_signature=data.requires_signature,
            parent_document_id=data.parent_document_id,
            related_documents=[str(d) for d in data.related_documents],
            metadata=data.metadata,
            created_by=created_by,
        )

        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)

        logger.info("Documento %s criado para funcionário %s", document.id, data.employee_id)
        return document

    def _generate_code(self) -> str:
        """Gera código único do documento."""
        import random
        import string
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
        return f"DOC{suffix}"

    async def get_by_id(self, document_id: UUID) -> Optional[EmployeeDocument]:
        """Busca documento por ID."""
        result = await self.db.execute(
            select(EmployeeDocument).where(EmployeeDocument.id == document_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[EmployeeDocument]:
        """Busca documento por código."""
        result = await self.db.execute(
            select(EmployeeDocument).where(EmployeeDocument.document_code == code)
        )
        return result.scalar_one_or_none()

    async def list_by_employee(
        self,
        employee_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        document_type: Optional[DocumentType] = None,
        category: Optional[str] = None,
        only_visible: bool = True,
        only_pending_ack: bool = False,
        only_pending_signature: bool = False,
        search: Optional[str] = None,
    ) -> Tuple[List[EmployeeDocument], int]:
        """Lista documentos do funcionário."""
        query = select(EmployeeDocument).where(
            EmployeeDocument.employee_id == employee_id
        )

        if only_visible:
            query = query.where(EmployeeDocument.is_visible.is_(True))
            query = query.where(
                EmployeeDocument.status.in_([
                    DocumentStatus.PUBLISHED.value,
                    DocumentStatus.ACKNOWLEDGED.value,
                ])
            )

        if document_type:
            query = query.where(EmployeeDocument.document_type == document_type.value)

        if category:
            query = query.where(EmployeeDocument.category == category)

        if only_pending_ack:
            query = query.where(
                and_(
                    EmployeeDocument.requires_acknowledgement.is_(True),
                    EmployeeDocument.acknowledged_at.is_(None),
                )
            )

        if only_pending_signature:
            query = query.where(
                and_(
                    EmployeeDocument.requires_signature.is_(True),
                    EmployeeDocument.signed_at.is_(None),
                )
            )

        if search:
            query = query.where(
                or_(
                    EmployeeDocument.title.ilike(f"%{search}%"),
                    EmployeeDocument.description.ilike(f"%{search}%"),
                )
            )

        # Total
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Paginação
        query = query.order_by(desc(EmployeeDocument.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def update(
        self,
        document_id: UUID,
        data: DocumentUpdate,
    ) -> Optional[EmployeeDocument]:
        """Atualiza documento."""
        document = await self.get_by_id(document_id)
        if not document:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "related_documents" and value is not None:
                value = [str(d) for d in value]
            setattr(document, field, value)

        document.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def publish(
        self,
        document_id: UUID,
        *,
        published_by: Optional[UUID] = None,
        send_notification: bool = True,
    ) -> Optional[EmployeeDocument]:
        """Publica documento."""
        document = await self.get_by_id(document_id)
        if not document:
            return None

        document.status = DocumentStatus.PUBLISHED.value
        document.published_at = datetime.utcnow()
        document.published_by = published_by

        if send_notification:
            document.notification_sent = True
            document.notification_sent_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(document)

        logger.info("Documento %s publicado", document_id)
        return document

    async def record_view(self, document_id: UUID) -> Optional[EmployeeDocument]:
        """Registra visualização do documento."""
        document = await self.get_by_id(document_id)
        if not document:
            return None

        document.record_view()
        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def record_download(self, document_id: UUID) -> Optional[EmployeeDocument]:
        """Registra download do documento."""
        document = await self.get_by_id(document_id)
        if not document:
            return None

        document.record_download()
        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def acknowledge(
        self,
        document_id: UUID,
        *,
        ip_address: Optional[str] = None,
        device_info: Optional[str] = None,
    ) -> Optional[EmployeeDocument]:
        """Registra ciência do documento."""
        document = await self.get_by_id(document_id)
        if not document:
            return None

        if document.acknowledged_at:
            return document

        document.acknowledged_at = datetime.utcnow()
        document.acknowledgement_ip = ip_address
        document.acknowledgement_device = device_info
        document.status = DocumentStatus.ACKNOWLEDGED.value

        await self.db.commit()
        await self.db.refresh(document)

        logger.info("Ciência registrada para documento %s", document_id)
        return document

    async def sign(
        self,
        document_id: UUID,
        signature_hash: str,
        *,
        signed_by: UUID,
        certificate: Optional[str] = None,
    ) -> Optional[EmployeeDocument]:
        """Assina documento digitalmente."""
        document = await self.get_by_id(document_id)
        if not document:
            return None

        if document.signed_at:
            raise ValueError("Documento já foi assinado")

        document.signed_at = datetime.utcnow()
        document.signed_by = signed_by
        document.signature_hash = signature_hash
        document.signature_certificate = certificate
        document.status = DocumentStatus.SIGNED.value

        await self.db.commit()
        await self.db.refresh(document)

        logger.info("Documento %s assinado", document_id)
        return document

    async def archive(
        self,
        document_id: UUID,
        *,
        archived_by: Optional[UUID] = None,
    ) -> Optional[EmployeeDocument]:
        """Arquiva documento."""
        document = await self.get_by_id(document_id)
        if not document:
            return None

        document.status = DocumentStatus.ARCHIVED.value
        document.archived_at = datetime.utcnow()
        document.archived_by = archived_by

        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def get_pending_count(self, employee_id: UUID) -> dict:
        """Conta documentos pendentes."""
        pending_ack = await self.db.execute(
            select(func.count(EmployeeDocument.id)).where(
                and_(
                    EmployeeDocument.employee_id == employee_id,
                    EmployeeDocument.is_visible.is_(True),
                    EmployeeDocument.requires_acknowledgement.is_(True),
                    EmployeeDocument.acknowledged_at.is_(None),
                )
            )
        )

        pending_signature = await self.db.execute(
            select(func.count(EmployeeDocument.id)).where(
                and_(
                    EmployeeDocument.employee_id == employee_id,
                    EmployeeDocument.is_visible.is_(True),
                    EmployeeDocument.requires_signature.is_(True),
                    EmployeeDocument.signed_at.is_(None),
                )
            )
        )

        unread = await self.db.execute(
            select(func.count(EmployeeDocument.id)).where(
                and_(
                    EmployeeDocument.employee_id == employee_id,
                    EmployeeDocument.is_visible.is_(True),
                    EmployeeDocument.first_viewed_at.is_(None),
                )
            )
        )

        return {
            "pending_acknowledgement": pending_ack.scalar() or 0,
            "pending_signature": pending_signature.scalar() or 0,
            "unread": unread.scalar() or 0,
        }

    async def get_expiring_documents(
        self,
        days_ahead: int = 30,
    ) -> List[EmployeeDocument]:
        """Busca documentos prestes a expirar."""
        target_date = date.today() + timedelta(days=days_ahead)
        result = await self.db.execute(
            select(EmployeeDocument).where(
                and_(
                    EmployeeDocument.is_perpetual.is_(False),
                    EmployeeDocument.valid_until.isnot(None),
                    EmployeeDocument.valid_until <= target_date,
                    EmployeeDocument.valid_until >= date.today(),
                    EmployeeDocument.status != DocumentStatus.EXPIRED.value,
                )
            )
        )
        return list(result.scalars().all())


from datetime import timedelta
