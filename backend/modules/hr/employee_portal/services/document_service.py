"""Service para documentos do funcionário."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.employee_portal.models import DocumentType, EmployeeDocument
from modules.hr.employee_portal.repositories import DocumentRepository
from modules.hr.employee_portal.schemas import DocumentCreate

logger = logging.getLogger(__name__)


class DocumentService:
    """Service para operações de documentos."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DocumentRepository(db)

    async def upload_document(
        self,
        data: DocumentCreate,
        condominio_id: UUID,
        *,
        created_by: UUID | None = None,
    ) -> EmployeeDocument:
        """Faz upload de documento."""
        return await self.repo.create(data, condominio_id, created_by=created_by)

    async def get_document(self, document_id: UUID) -> EmployeeDocument | None:
        """Busca documento por ID."""
        return await self.repo.get_by_id(document_id)

    async def list_employee_documents(
        self,
        employee_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        document_type: DocumentType | None = None,
        category: str | None = None,
        search: str | None = None,
        only_pending_ack: bool = False,
        only_pending_signature: bool = False,
    ) -> tuple[list[EmployeeDocument], int]:
        """Lista documentos do funcionário."""
        return await self.repo.list_by_employee(
            employee_id,
            page=page,
            page_size=page_size,
            document_type=document_type,
            category=category,
            search=search,
            only_visible=True,
            only_pending_ack=only_pending_ack,
            only_pending_signature=only_pending_signature,
        )

    async def view_document(
        self,
        document_id: UUID,
        employee_id: UUID,
    ) -> EmployeeDocument | None:
        """Visualiza documento (registra view)."""
        document = await self.repo.get_by_id(document_id)
        if not document or document.employee_id != employee_id:
            return None

        if not document.is_published:
            raise ValueError("Documento não disponível")

        return await self.repo.record_view(document_id)

    async def download_document(
        self,
        document_id: UUID,
        employee_id: UUID,
    ) -> EmployeeDocument | None:
        """Download do documento (registra download)."""
        document = await self.repo.get_by_id(document_id)
        if not document or document.employee_id != employee_id:
            return None

        return await self.repo.record_download(document_id)

    async def acknowledge_document(
        self,
        document_id: UUID,
        employee_id: UUID,
        *,
        ip_address: str | None = None,
        device_info: str | None = None,
    ) -> EmployeeDocument | None:
        """Registra ciência no documento."""
        document = await self.repo.get_by_id(document_id)
        if not document or document.employee_id != employee_id:
            return None

        if not document.requires_acknowledgement:
            raise ValueError("Documento não requer ciência")

        return await self.repo.acknowledge(
            document_id,
            ip_address=ip_address,
            device_info=device_info,
        )

    async def sign_document(
        self,
        document_id: UUID,
        employee_id: UUID,
        signature_hash: str,
        *,
        certificate: str | None = None,
    ) -> EmployeeDocument | None:
        """Assina documento digitalmente."""
        document = await self.repo.get_by_id(document_id)
        if not document or document.employee_id != employee_id:
            return None

        if not document.requires_signature:
            raise ValueError("Documento não requer assinatura")

        return await self.repo.sign(
            document_id,
            signature_hash,
            signed_by=employee_id,
            certificate=certificate,
        )

    async def publish_document(
        self,
        document_id: UUID,
        *,
        published_by: UUID | None = None,
        send_notification: bool = True,
    ) -> EmployeeDocument | None:
        """Publica documento."""
        return await self.repo.publish(
            document_id,
            published_by=published_by,
            send_notification=send_notification,
        )

    async def get_pending_counts(
        self,
        employee_id: UUID,
    ) -> dict:
        """Retorna contagem de documentos pendentes."""
        return await self.repo.get_pending_count(employee_id)

    async def get_document_categories(
        self,
        employee_id: UUID,
    ) -> list[str]:
        """Retorna categorias de documentos disponíveis."""
        # Reservado para personalização por funcionário
        _ = employee_id  # Para uso futuro
        return [
            "folha_pagamento",
            "ferias",
            "contratos",
            "beneficios",
            "treinamentos",
            "atestados",
            "outros",
        ]
