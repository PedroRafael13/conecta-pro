"""
Model EquipmentComodato - Contratos de Comodato de Equipamentos.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class ComodatoStatus(str, Enum):
    """Status do contrato de comodato."""

    DRAFT = "draft"  # Rascunho
    PENDING_SIGNATURE = "pending_signature"  # Aguardando assinatura
    ACTIVE = "active"  # Ativo
    SUSPENDED = "suspended"  # Suspenso
    TERMINATED = "terminated"  # Encerrado
    RETURNED = "returned"  # Equipamento devolvido
    TRANSFERRED = "transferred"  # Transferido para outro cliente


class EquipmentComodato(Base):
    """
    Model para contratos de comodato de equipamentos.

    Gerencia empréstimo de equipamentos a clientes,
    com controle de termos, prazos e devoluções.
    """

    __tablename__ = "equipment_comodatos"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    comodato_code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(30),
        default=ComodatoStatus.DRAFT.value,
        nullable=False,
        index=True,
    )

    # Equipamento
    equipment_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )
    equipment_code: Mapped[str] = mapped_column(String(30), nullable=False)
    equipment_name: Mapped[str] = mapped_column(String(200), nullable=False)
    equipment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    equipment_value: Mapped[float] = mapped_column(Float, nullable=False)
    equipment_condition: Mapped[str] = mapped_column(
        String(30),
        default="novo",
    )  # novo, usado_bom, usado_regular

    # Cliente (comodatário)
    client_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )
    client_name: Mapped[str] = mapped_column(String(200), nullable=False)
    client_document: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )  # CNPJ/CPF
    contract_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )  # Contrato principal

    # Responsável do cliente
    responsible_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    responsible_document: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    responsible_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    responsible_email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Vigência
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )  # Null = indeterminado
    duration_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    auto_renewal: Mapped[bool] = mapped_column(Boolean, default=True)
    renewal_period_months: Mapped[int] = mapped_column(Integer, default=12)
    notice_period_days: Mapped[int] = mapped_column(
        Integer,
        default=30,
    )  # Aviso prévio

    # Local de uso
    usage_location: Mapped[str] = mapped_column(Text, nullable=False)
    usage_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gps_latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gps_longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Termos e condições
    terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    special_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    usage_restrictions: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    maintenance_responsibility: Mapped[str] = mapped_column(
        String(30),
        default="comodante",
    )  # comodante, comodatario, compartilhada

    # Multas e penalidades
    damage_penalty_percent: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )  # % do valor do equipamento
    loss_penalty_percent: Mapped[Optional[float]] = mapped_column(
        Float,
        default=100.0,
    )  # % do valor em caso de perda
    early_return_penalty: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # Assinatura
    signed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    signed_by_client: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    signed_by_company: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    client_signature: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_signature: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    signature_document_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # Documentos
    contract_pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    delivery_term_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )  # Termo de entrega
    return_term_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )  # Termo de devolução
    photos_delivery: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )  # Fotos na entrega
    photos_return: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )  # Fotos na devolução

    # Entrega
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivered_by: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    received_by: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    delivery_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Devolução
    return_requested_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    return_scheduled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    returned_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    returned_by: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    return_received_by: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    return_condition: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
    )  # bom, danificado, perdido
    return_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Danos e cobranças
    has_damages: Mapped[bool] = mapped_column(Boolean, default=False)
    damage_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    damage_photos: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    damage_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    penalty_applied: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_lost: Mapped[bool] = mapped_column(Boolean, default=False)

    # Transferência
    transferred_to_client_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    transferred_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    transfer_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_comodato_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Encerramento
    terminated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    terminated_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    termination_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Histórico
    history: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )  # [{action, date, by, notes}]

    # Metadados
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    metadata_extra: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Auditoria
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Properties
    @property
    def is_signed(self) -> bool:
        """Verifica se o contrato está assinado."""
        return self.signed_at is not None

    @property
    def is_active_contract(self) -> bool:
        """Verifica se o contrato está ativo."""
        return self.status == ComodatoStatus.ACTIVE.value

    @property
    def is_expired(self) -> bool:
        """Verifica se o contrato expirou."""
        if not self.end_date:
            return False
        return datetime.utcnow() > self.end_date

    @property
    def days_until_expiry(self) -> Optional[int]:
        """Dias até a expiração."""
        if not self.end_date:
            return None
        delta = self.end_date - datetime.utcnow()
        return delta.days

    @property
    def is_delivered(self) -> bool:
        """Verifica se foi entregue."""
        return self.delivered_at is not None

    @property
    def is_returned(self) -> bool:
        """Verifica se foi devolvido."""
        return self.returned_at is not None

    # Methods
    def activate(self) -> None:
        """Ativa o contrato de comodato."""
        self.status = ComodatoStatus.ACTIVE.value
        self._add_history("activated", "Contrato ativado")

    def sign(
        self,
        signed_by_client: str,
        signed_by_company: str,
        client_signature: Optional[str] = None,
    ) -> None:
        """Registra assinatura do contrato."""
        self.status = ComodatoStatus.ACTIVE.value
        self.signed_at = datetime.utcnow()
        self.signed_by_client = signed_by_client
        self.signed_by_company = signed_by_company
        self.client_signature = client_signature
        self._add_history("signed", f"Assinado por {signed_by_client}")

    def deliver(
        self,
        delivered_by: str,
        received_by: str,
        notes: Optional[str] = None,
    ) -> None:
        """Registra entrega do equipamento."""
        self.delivered_at = datetime.utcnow()
        self.delivered_by = delivered_by
        self.received_by = received_by
        self.delivery_notes = notes
        self._add_history("delivered", f"Entregue a {received_by}")

    def request_return(self, reason: Optional[str] = None) -> None:
        """Solicita devolução do equipamento."""
        self.return_requested_at = datetime.utcnow()
        self._add_history("return_requested", reason or "Devolução solicitada")

    def schedule_return(self, scheduled_date: datetime) -> None:
        """Agenda devolução."""
        self.return_scheduled_at = scheduled_date
        self._add_history(
            "return_scheduled",
            f"Devolução agendada para {scheduled_date.isoformat()}",
        )

    def register_return(
        self,
        returned_by: str,
        received_by: str,
        condition: str,
        notes: Optional[str] = None,
    ) -> None:
        """Registra devolução do equipamento."""
        self.status = ComodatoStatus.RETURNED.value
        self.returned_at = datetime.utcnow()
        self.returned_by = returned_by
        self.return_received_by = received_by
        self.return_condition = condition
        self.return_notes = notes
        self._add_history("returned", f"Devolvido por {returned_by} - Condição: {condition}")

    def register_damage(
        self,
        description: str,
        cost: float,
        photos: Optional[list] = None,
    ) -> None:
        """Registra dano no equipamento."""
        self.has_damages = True
        self.damage_description = description
        self.damage_cost = cost
        self.damage_photos = photos
        self._add_history("damage_registered", f"Dano registrado: {description}")

    def apply_penalty(self, amount: float, reason: str) -> None:
        """Aplica penalidade."""
        self.penalty_applied = amount
        self._add_history("penalty_applied", f"Penalidade de R$ {amount}: {reason}")

    def mark_as_lost(self) -> None:
        """Marca equipamento como perdido."""
        self.is_lost = True
        self.penalty_applied = self.equipment_value * (self.loss_penalty_percent or 100) / 100
        self._add_history("marked_lost", "Equipamento marcado como perdido")

    def suspend(self, reason: str) -> None:
        """Suspende o contrato."""
        self.status = ComodatoStatus.SUSPENDED.value
        self._add_history("suspended", reason)

    def terminate(self, reason: str, terminated_by: str) -> None:
        """Encerra o contrato."""
        self.status = ComodatoStatus.TERMINATED.value
        self.terminated_at = datetime.utcnow()
        self.terminated_by = terminated_by
        self.termination_reason = reason
        self._add_history("terminated", reason)

    def transfer(
        self,
        new_client_id: str,
        new_comodato_id: str,
        reason: str,
    ) -> None:
        """Transfere para outro cliente."""
        self.status = ComodatoStatus.TRANSFERRED.value
        self.transferred_to_client_id = new_client_id
        self.transferred_at = datetime.utcnow()
        self.transfer_reason = reason
        self.new_comodato_id = new_comodato_id
        self._add_history("transferred", f"Transferido: {reason}")

    def _add_history(self, action: str, notes: str) -> None:
        """Adiciona entrada ao histórico."""
        if not self.history:
            self.history = []
        self.history.append({
            "action": action,
            "date": datetime.utcnow().isoformat(),
            "notes": notes,
        })
