"""Model para aprovações de compra."""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class ApprovalType(StrEnum):
    """Tipo de aprovação."""

    REQUISICAO = "requisicao"
    COTACAO = "cotacao"
    ORDEM_COMPRA = "ordem_compra"
    RECEBIMENTO = "recebimento"
    PAGAMENTO = "pagamento"


class ApprovalStatus(StrEnum):
    """Status da aprovação."""

    PENDENTE = "pendente"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"
    DELEGADO = "delegado"
    EXPIRADO = "expirado"
    CANCELADO = "cancelado"


class ApprovalLevel(StrEnum):
    """Nível de aprovação."""

    OPERACIONAL = "operacional"  # Até R$ 1.000
    SUPERVISAO = "supervisao"  # Até R$ 5.000
    GERENCIAL = "gerencial"  # Até R$ 20.000
    DIRETORIA = "diretoria"  # Até R$ 100.000
    CONSELHO = "conselho"  # Acima de R$ 100.000


class ApprovalAction(StrEnum):
    """Ação de aprovação."""

    APROVAR = "aprovar"
    REJEITAR = "rejeitar"
    SOLICITAR_INFO = "solicitar_info"
    DELEGAR = "delegar"
    DEVOLVER = "devolver"


class PurchaseApproval(Base):
    """Aprovação de compra (workflow)."""

    __tablename__ = "purchase_approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Documento de origem
    approval_type = Column(String(20), nullable=False)
    document_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    document_number = Column(String(50), nullable=True)  # Número do documento

    # Sequência de aprovação
    sequence = Column(Integer, nullable=False, default=1)  # Ordem na sequência
    approval_level = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default=ApprovalStatus.PENDENTE.value)

    # Valores
    document_total = Column(Numeric(15, 2), nullable=True)  # Valor do documento

    # Aprovador
    approver_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True)
    approver_role = Column(String(50), nullable=True)  # Cargo do aprovador

    # Delegação
    original_approver_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    delegated_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    delegation_reason = Column(Text, nullable=True)
    delegated_at = Column(DateTime, nullable=True)

    # Prazo
    requested_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    deadline = Column(DateTime, nullable=True)  # Prazo para aprovação
    responded_at = Column(DateTime, nullable=True)
    response_time_hours = Column(Numeric(8, 2), nullable=True)  # Tempo de resposta

    # Resposta
    action = Column(String(20), nullable=True)  # Ação tomada
    comments = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Informações adicionais solicitadas
    info_requested = Column(Text, nullable=True)
    info_provided = Column(Text, nullable=True)
    info_requested_at = Column(DateTime, nullable=True)
    info_provided_at = Column(DateTime, nullable=True)

    # Notificações
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime, nullable=True)
    reminder_count = Column(Integer, default=0)
    last_reminder_at = Column(DateTime, nullable=True)

    # Histórico de ações
    action_history = Column(JSONB, default=list)
    # [{action, timestamp, user_id, comments}]

    # Anexos
    attachments = Column(JSONB, default=list)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_purchase_approvals_document", "document_id"),
        Index("ix_purchase_approvals_approver", "approver_id"),
        Index("ix_purchase_approvals_status", "status"),
        Index("ix_purchase_approvals_type_status", "approval_type", "status"),
        Index("ix_purchase_approvals_condominio_status", "condominio_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<PurchaseApproval {self.approval_type}:{self.document_number} - {self.status}>"

    @property
    def is_pending(self) -> bool:
        """Verifica se está pendente."""
        return self.status == ApprovalStatus.PENDENTE.value

    @property
    def is_approved(self) -> bool:
        """Verifica se foi aprovado."""
        return self.status == ApprovalStatus.APROVADO.value

    @property
    def is_rejected(self) -> bool:
        """Verifica se foi rejeitado."""
        return self.status == ApprovalStatus.REJEITADO.value

    @property
    def is_expired(self) -> bool:
        """Verifica se expirou."""
        if self.status == ApprovalStatus.EXPIRADO.value:
            return True
        if self.deadline and self.status == ApprovalStatus.PENDENTE.value:
            return datetime.utcnow() > self.deadline
        return False

    @property
    def is_delegated(self) -> bool:
        """Verifica se foi delegado."""
        return self.status == ApprovalStatus.DELEGADO.value or self.delegated_by is not None

    @property
    def time_pending_hours(self) -> float | None:
        """Tempo pendente em horas."""
        if self.status == ApprovalStatus.PENDENTE.value:
            delta = datetime.utcnow() - self.requested_at
            return delta.total_seconds() / 3600
        return None

    @property
    def is_overdue(self) -> bool:
        """Verifica se está atrasado."""
        if self.deadline and self.status == ApprovalStatus.PENDENTE.value:
            return datetime.utcnow() > self.deadline
        return False

    @property
    def needs_reminder(self) -> bool:
        """Verifica se precisa de lembrete."""
        if not self.is_pending:
            return False
        if self.is_overdue:
            return True
        # Lembrete a cada 24h se pendente
        if self.last_reminder_at:
            hours_since = (datetime.utcnow() - self.last_reminder_at).total_seconds() / 3600
            return hours_since >= 24
        hours_pending = self.time_pending_hours or 0
        return hours_pending >= 24

    def approve(self, comments: str | None = None) -> None:
        """Aprova."""
        self._respond(ApprovalStatus.APROVADO.value, ApprovalAction.APROVAR.value, comments)

    def reject(self, reason: str, comments: str | None = None) -> None:
        """Rejeita."""
        self.rejection_reason = reason
        self._respond(ApprovalStatus.REJEITADO.value, ApprovalAction.REJEITAR.value, comments)

    def delegate(self, new_approver_id: uuid.UUID, delegator_id: uuid.UUID, reason: str) -> None:
        """Delega para outro aprovador."""
        self.original_approver_id = self.approver_id
        self.approver_id = new_approver_id
        self.delegated_by = delegator_id
        self.delegation_reason = reason
        self.delegated_at = datetime.utcnow()
        self.status = ApprovalStatus.DELEGADO.value
        self._add_history(ApprovalAction.DELEGAR.value, f"Delegado para outro aprovador: {reason}")
        # Reseta para pendente com novo aprovador
        self.status = ApprovalStatus.PENDENTE.value

    def request_info(self, info_request: str) -> None:
        """Solicita informações adicionais."""
        self.info_requested = info_request
        self.info_requested_at = datetime.utcnow()
        self._add_history(ApprovalAction.SOLICITAR_INFO.value, info_request)

    def provide_info(self, info: str) -> None:
        """Fornece informações solicitadas."""
        self.info_provided = info
        self.info_provided_at = datetime.utcnow()
        self._add_history("info_fornecida", info)

    def mark_expired(self) -> None:
        """Marca como expirado."""
        self.status = ApprovalStatus.EXPIRADO.value
        self._add_history("expirado", "Prazo de aprovação expirado")

    def cancel(self, reason: str | None = None) -> None:
        """Cancela a aprovação."""
        self.status = ApprovalStatus.CANCELADO.value
        self._add_history("cancelado", reason or "Aprovação cancelada")

    def send_notification(self) -> None:
        """Registra envio de notificação."""
        self.notification_sent = True
        self.notification_sent_at = datetime.utcnow()

    def send_reminder(self) -> None:
        """Registra envio de lembrete."""
        self.reminder_count = (self.reminder_count or 0) + 1
        self.last_reminder_at = datetime.utcnow()
        self._add_history("lembrete", f"Lembrete #{self.reminder_count} enviado")

    def _respond(self, status: str, action: str, comments: str | None = None) -> None:
        """Registra resposta."""
        self.status = status
        self.action = action
        self.comments = comments
        self.responded_at = datetime.utcnow()

        # Calcula tempo de resposta
        if self.requested_at:
            delta = self.responded_at - self.requested_at
            self.response_time_hours = Decimal(str(delta.total_seconds() / 3600))

        self._add_history(action, comments)

    def _add_history(self, action: str, details: str | None = None) -> None:
        """Adiciona ao histórico."""
        if not self.action_history:
            self.action_history = []
        self.action_history.append(
            {
                "action": action,
                "details": details,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": str(self.approver_id),
            }
        )

    @staticmethod
    def get_required_level(amount: Decimal) -> str:
        """Determina nível de aprovação necessário pelo valor."""
        if amount <= 1000:
            return ApprovalLevel.OPERACIONAL.value
        if amount <= 5000:
            return ApprovalLevel.SUPERVISAO.value
        if amount <= 20000:
            return ApprovalLevel.GERENCIAL.value
        if amount <= 100000:
            return ApprovalLevel.DIRETORIA.value
        return ApprovalLevel.CONSELHO.value

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "approval_type": self.approval_type,
            "document_id": str(self.document_id),
            "document_number": self.document_number,
            "status": self.status,
            "approval_level": self.approval_level,
            "sequence": self.sequence,
            "approver_id": str(self.approver_id),
            "document_total": float(self.document_total) if self.document_total else None,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "action": self.action,
            "comments": self.comments,
            "is_pending": self.is_pending,
            "is_overdue": self.is_overdue,
            "is_delegated": self.is_delegated,
        }
