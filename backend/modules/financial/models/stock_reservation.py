"""Model para reservas de estoque."""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.financial.models.product import Product
    from modules.financial.models.warehouse import Warehouse


class ReservationType(str, Enum):
    """Tipo de reserva."""

    VENDA = "venda"
    ORDEM_SERVICO = "ordem_servico"
    TRANSFERENCIA = "transferencia"
    PRODUCAO = "producao"
    REQUISICAO = "requisicao"
    EVENTO = "evento"
    MANUTENCAO = "manutencao"
    OUTRO = "outro"


class ReservationStatus(str, Enum):
    """Status da reserva."""

    ATIVA = "ativa"
    PARCIALMENTE_ATENDIDA = "parcialmente_atendida"
    ATENDIDA = "atendida"
    EXPIRADA = "expirada"
    CANCELADA = "cancelada"
    LIBERADA = "liberada"


class ReservationPriority(str, Enum):
    """Prioridade da reserva."""

    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"
    CRITICA = "critica"


class StockReservation(Base):
    """Reserva de estoque."""

    __tablename__ = "stock_reservations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificação
    number = Column(String(20), nullable=False, index=True)  # RES-YYYY-NNNN
    description = Column(String(200), nullable=True)
    reservation_type = Column(String(20), nullable=False)
    status = Column(String(30), nullable=False, default=ReservationStatus.ATIVA.value)
    priority = Column(String(20), nullable=False, default=ReservationPriority.MEDIA.value)

    # Produto
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    # Armazém
    warehouse_id = Column(
        UUID(as_uuid=True),
        ForeignKey("warehouses.id"),
        nullable=False,
        index=True,
    )

    # Stock Item (opcional - para reserva de lote específico)
    stock_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("stock_items.id"),
        nullable=True,
        index=True,
    )

    # Lote específico
    batch_number = Column(String(50), nullable=True)

    # Quantidades
    quantity_requested = Column(Numeric(15, 4), nullable=False)  # Quantidade solicitada
    quantity_reserved = Column(Numeric(15, 4), default=0)  # Quantidade reservada
    quantity_released = Column(Numeric(15, 4), default=0)  # Quantidade liberada/consumida
    quantity_pending = Column(Numeric(15, 4), default=0)  # Quantidade pendente
    unit_of_measure = Column(String(10), nullable=False, default="un")

    # Datas
    reservation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    required_date = Column(DateTime, nullable=True)  # Data de necessidade
    expiry_date = Column(DateTime, nullable=True)  # Data de expiração da reserva
    released_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Referência (documento de origem)
    reference_type = Column(String(50), nullable=True)  # sales_order, work_order, etc
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    reference_number = Column(String(50), nullable=True)

    # Solicitante
    requester_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=True,
    )
    requester_name = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    cost_center = Column(String(50), nullable=True)

    # Aprovação
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)

    # Liberação
    released_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    release_notes = Column(Text, nullable=True)

    # Cancelamento
    cancelled_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Configurações
    auto_release = Column(Boolean, default=False)  # Liberação automática na data
    auto_expire = Column(Boolean, default=True)  # Expira automaticamente
    allow_partial = Column(Boolean, default=True)  # Permite liberação parcial

    # Observações
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)

    # Metadados
    metadata = Column(JSONB, default=dict)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    product: "Product" = relationship("Product")
    warehouse: "Warehouse" = relationship("Warehouse")

    __table_args__ = (
        Index("ix_stock_reservations_number", "number"),
        Index("ix_stock_reservations_status", "status"),
        Index("ix_stock_reservations_type", "reservation_type"),
        Index("ix_stock_reservations_product", "product_id"),
        Index("ix_stock_reservations_warehouse", "warehouse_id"),
        Index("ix_stock_reservations_reference", "reference_type", "reference_id"),
        Index("ix_stock_reservations_condominio", "condominio_id"),
        Index("ix_stock_reservations_expiry", "expiry_date"),
        Index("ix_stock_reservations_required", "required_date"),
    )

    def __repr__(self) -> str:
        return f"<StockReservation {self.number}>"

    @property
    def is_active(self) -> bool:
        """Verifica se está ativa."""
        return self.status == ReservationStatus.ATIVA.value

    @property
    def is_fulfilled(self) -> bool:
        """Verifica se foi totalmente atendida."""
        return self.status == ReservationStatus.ATENDIDA.value

    @property
    def is_partial(self) -> bool:
        """Verifica se está parcialmente atendida."""
        return self.status == ReservationStatus.PARCIALMENTE_ATENDIDA.value

    @property
    def is_expired(self) -> bool:
        """Verifica se está expirada."""
        if self.expiry_date:
            return datetime.utcnow() > self.expiry_date and self.is_active
        return False

    @property
    def is_cancelled(self) -> bool:
        """Verifica se está cancelada."""
        return self.status == ReservationStatus.CANCELADA.value

    @property
    def is_released(self) -> bool:
        """Verifica se foi liberada."""
        return self.status == ReservationStatus.LIBERADA.value

    @property
    def fulfillment_percentage(self) -> Decimal:
        """Percentual de atendimento."""
        if self.quantity_requested and self.quantity_requested > 0:
            return Decimal(
                (self.quantity_released or Decimal("0")) / self.quantity_requested * 100
            ).quantize(Decimal("0.01"))
        return Decimal("0")

    @property
    def is_overdue(self) -> bool:
        """Verifica se está atrasada."""
        if self.required_date:
            return datetime.utcnow() > self.required_date and self.is_active
        return False

    @property
    def days_until_required(self) -> Optional[int]:
        """Dias até a data necessária."""
        if self.required_date:
            delta = self.required_date - datetime.utcnow()
            return delta.days
        return None

    @property
    def days_until_expiry(self) -> Optional[int]:
        """Dias até expiração."""
        if self.expiry_date:
            delta = self.expiry_date - datetime.utcnow()
            return delta.days
        return None

    @property
    def is_high_priority(self) -> bool:
        """Verifica se é alta prioridade."""
        return self.priority in [
            ReservationPriority.ALTA.value,
            ReservationPriority.URGENTE.value,
            ReservationPriority.CRITICA.value,
        ]

    def reserve(self, quantity: Decimal) -> bool:
        """Efetiva a reserva de quantidade."""
        if quantity > (self.quantity_requested - (self.quantity_reserved or Decimal("0"))):
            return False

        self.quantity_reserved = (self.quantity_reserved or Decimal("0")) + quantity
        self.quantity_pending = self.quantity_requested - self.quantity_reserved
        return True

    def release(
        self,
        quantity: Decimal,
        user_id: uuid.UUID,
        notes: Optional[str] = None,
    ) -> bool:
        """Libera quantidade reservada."""
        available = (self.quantity_reserved or Decimal("0")) - (
            self.quantity_released or Decimal("0")
        )
        if quantity > available:
            return False

        self.quantity_released = (self.quantity_released or Decimal("0")) + quantity
        self.released_by = user_id
        self.released_at = datetime.utcnow()
        self.release_notes = notes

        # Atualiza status
        if self.quantity_released >= self.quantity_requested:
            self.status = ReservationStatus.ATENDIDA.value
        elif self.quantity_released > 0:
            self.status = ReservationStatus.PARCIALMENTE_ATENDIDA.value

        return True

    def release_all(self, user_id: uuid.UUID, notes: Optional[str] = None) -> None:
        """Libera toda quantidade reservada."""
        self.quantity_released = self.quantity_reserved
        self.released_by = user_id
        self.released_at = datetime.utcnow()
        self.release_notes = notes
        self.status = ReservationStatus.LIBERADA.value

    def cancel(self, user_id: uuid.UUID, reason: str) -> None:
        """Cancela a reserva."""
        self.status = ReservationStatus.CANCELADA.value
        self.cancelled_by = user_id
        self.cancelled_at = datetime.utcnow()
        self.cancellation_reason = reason
        self.quantity_reserved = Decimal("0")
        self.quantity_pending = Decimal("0")

    def expire(self) -> None:
        """Marca como expirada."""
        self.status = ReservationStatus.EXPIRADA.value
        self.quantity_reserved = Decimal("0")
        self.quantity_pending = Decimal("0")

    def approve(self, approver_id: uuid.UUID, notes: Optional[str] = None) -> None:
        """Aprova a reserva."""
        self.approved_by = approver_id
        self.approved_at = datetime.utcnow()
        self.approval_notes = notes

    def extend_expiry(self, days: int) -> None:
        """Estende data de expiração."""
        if self.expiry_date:
            self.expiry_date = self.expiry_date + timedelta(days=days)
        else:
            self.expiry_date = datetime.utcnow() + timedelta(days=days)

    def update_pending(self) -> None:
        """Atualiza quantidade pendente."""
        self.quantity_pending = self.quantity_requested - (self.quantity_reserved or Decimal("0"))

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "number": self.number,
            "description": self.description,
            "reservation_type": self.reservation_type,
            "status": self.status,
            "priority": self.priority,
            "product_id": str(self.product_id),
            "warehouse_id": str(self.warehouse_id),
            "batch_number": self.batch_number,
            "quantity_requested": float(self.quantity_requested),
            "quantity_reserved": float(self.quantity_reserved) if self.quantity_reserved else 0,
            "quantity_released": float(self.quantity_released) if self.quantity_released else 0,
            "quantity_pending": float(self.quantity_pending) if self.quantity_pending else 0,
            "fulfillment_percentage": float(self.fulfillment_percentage),
            "reservation_date": (
                self.reservation_date.isoformat() if self.reservation_date else None
            ),
            "required_date": self.required_date.isoformat() if self.required_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "reference_type": self.reference_type,
            "reference_number": self.reference_number,
            "is_active": self.is_active,
            "is_fulfilled": self.is_fulfilled,
            "is_expired": self.is_expired,
            "is_overdue": self.is_overdue,
            "days_until_required": self.days_until_required,
        }
