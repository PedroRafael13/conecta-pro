"""Model para anexos/comprovantes de reembolso."""

import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.reimbursement.models.reimbursement_request import ReimbursementRequest
    from modules.reimbursement.models.reimbursement_item import ReimbursementItem


class AttachmentType(str, Enum):
    """Tipo de anexo."""

    NOTA_FISCAL = "nota_fiscal"
    CUPOM_FISCAL = "cupom_fiscal"
    RECIBO = "recibo"
    FATURA = "fatura"
    COMPROVANTE_PAGAMENTO = "comprovante_pagamento"
    COMPROVANTE_CARTAO = "comprovante_cartao"
    BOLETO = "boleto"
    EXTRATO = "extrato"
    OUTROS = "outros"


# Labels para tipos de anexo
ATTACHMENT_TYPE_LABELS = {
    AttachmentType.NOTA_FISCAL: "Nota Fiscal",
    AttachmentType.CUPOM_FISCAL: "Cupom Fiscal",
    AttachmentType.RECIBO: "Recibo",
    AttachmentType.FATURA: "Fatura",
    AttachmentType.COMPROVANTE_PAGAMENTO: "Comprovante de Pagamento",
    AttachmentType.COMPROVANTE_CARTAO: "Comprovante de Cartão",
    AttachmentType.BOLETO: "Boleto",
    AttachmentType.EXTRATO: "Extrato",
    AttachmentType.OUTROS: "Outros",
}


class ReimbursementAttachment(Base):
    """Anexo/comprovante de uma solicitação ou item de reembolso."""

    __tablename__ = "reimbursement_attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Vinculação (pode ser à solicitação ou a um item específico)
    request_id = Column(
        UUID(as_uuid=True),
        ForeignKey("reimbursement_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("reimbursement_items.id", ondelete="CASCADE"),
        nullable=True,  # Opcional: pode ser anexo geral da solicitação
        index=True,
    )

    # Tipo de anexo
    attachment_type = Column(String(30), nullable=False, default=AttachmentType.OUTROS.value)

    # Arquivo
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Caminho no storage
    file_size_bytes = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)

    # Thumbnail (para imagens)
    thumbnail_path = Column(String(500), nullable=True)

    # Validação
    is_valid = Column(Boolean, default=True)  # Se o comprovante é válido
    validation_notes = Column(Text, nullable=True)

    # Metadados
    original_name = Column(String(255), nullable=True)  # Nome original do arquivo
    description = Column(Text, nullable=True)

    # Upload
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Controle
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    request: Optional["ReimbursementRequest"] = relationship(
        "ReimbursementRequest",
        back_populates="attachments",
        foreign_keys=[request_id],
    )
    item: Optional["ReimbursementItem"] = relationship(
        "ReimbursementItem",
        back_populates="attachments",
        foreign_keys=[item_id],
    )

    __table_args__ = (
        Index("ix_reimbursement_attachments_request", "request_id"),
        Index("ix_reimbursement_attachments_item", "item_id"),
        Index("ix_reimbursement_attachments_type", "attachment_type"),
    )

    def __repr__(self) -> str:
        return f"<ReimbursementAttachment {self.id} - {self.file_name}>"

    @property
    def type_label(self) -> str:
        """Retorna o label do tipo de anexo."""
        try:
            return ATTACHMENT_TYPE_LABELS.get(
                AttachmentType(self.attachment_type),
                self.attachment_type,
            )
        except ValueError:
            return self.attachment_type

    @property
    def file_size_formatted(self) -> str:
        """Retorna o tamanho do arquivo formatado."""
        if not self.file_size_bytes:
            return "0 B"

        size = self.file_size_bytes
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @property
    def is_image(self) -> bool:
        """Verifica se é uma imagem."""
        if not self.mime_type:
            return False
        return self.mime_type.startswith("image/")

    @property
    def is_pdf(self) -> bool:
        """Verifica se é um PDF."""
        return self.mime_type == "application/pdf"

    def mark_as_invalid(self, notes: str) -> None:
        """Marca o anexo como inválido."""
        self.is_valid = False
        self.validation_notes = notes

    def mark_as_valid(self) -> None:
        """Marca o anexo como válido."""
        self.is_valid = True
        self.validation_notes = None

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "request_id": str(self.request_id),
            "item_id": str(self.item_id) if self.item_id else None,
            "attachment_type": self.attachment_type,
            "type_label": self.type_label,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_size_bytes": self.file_size_bytes,
            "file_size_formatted": self.file_size_formatted,
            "mime_type": self.mime_type,
            "thumbnail_path": self.thumbnail_path,
            "is_valid": self.is_valid,
            "validation_notes": self.validation_notes,
            "original_name": self.original_name,
            "description": self.description,
            "is_image": self.is_image,
            "is_pdf": self.is_pdf,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "is_active": self.is_active,
        }
