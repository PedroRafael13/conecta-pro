"""Model para formas de pagamento."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class PaymentMethodType(str, Enum):
    """Tipo de forma de pagamento."""

    DINHEIRO = "dinheiro"
    PIX = "pix"
    TED = "ted"
    DOC = "doc"
    BOLETO = "boleto"
    CHEQUE = "cheque"
    CARTAO_CREDITO = "cartao_credito"
    CARTAO_DEBITO = "cartao_debito"
    DEBITO_AUTOMATICO = "debito_automatico"
    DEPOSITO = "deposito"
    TRANSFERENCIA = "transferencia"
    COMPENSACAO = "compensacao"  # Compensação entre contas
    OUTRO = "outro"


class PaymentMethodStatus(str, Enum):
    """Status da forma de pagamento."""

    ATIVO = "ativo"
    INATIVO = "inativo"


class PaymentMethod(Base):
    """Forma de pagamento."""

    __tablename__ = "payment_methods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificação
    code = Column(String(20), nullable=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    payment_type = Column(String(30), nullable=False, default=PaymentMethodType.BOLETO.value)
    status = Column(String(20), nullable=False, default=PaymentMethodStatus.ATIVO.value)

    # Configurações
    requires_bank_account = Column(Boolean, default=False)
    requires_authorization = Column(Boolean, default=False)
    requires_document = Column(Boolean, default=False)  # Requer comprovante

    # Conta bancária associada (para TED, DOC, débito automático)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=True)

    # Prazos e limites
    days_to_process = Column(Integer, default=0)  # D+0, D+1, etc
    min_value = Column(String(20), nullable=True)  # Valor mínimo
    max_value = Column(String(20), nullable=True)  # Valor máximo
    daily_limit = Column(String(20), nullable=True)  # Limite diário

    # Taxas
    fee_percentage = Column(String(10), nullable=True)  # % de taxa
    fee_fixed = Column(String(20), nullable=True)  # Valor fixo de taxa

    # Configurações específicas (JSONB)
    settings = Column(JSONB, default=dict)
    # Para boleto: {"banco": "001", "carteira": "17", "convenio": "123456"}
    # Para PIX: {"chave": "...", "tipo_chave": "cpf"}
    # Para cartão: {"adquirente": "cielo", "merchant_id": "..."}

    # Ordenação e exibição
    display_order = Column(Integer, default=0)
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)

    # Controle
    is_default = Column(Boolean, default=False)  # Padrão do condomínio
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_payment_methods_type", "payment_type"),
        Index("ix_payment_methods_status", "status"),
        Index("ix_payment_methods_condominio", "condominio_id"),
    )

    def __repr__(self) -> str:
        return f"<PaymentMethod {self.name}>"

    @property
    def is_electronic(self) -> bool:
        """Verifica se é pagamento eletrônico."""
        return self.payment_type in [
            PaymentMethodType.PIX.value,
            PaymentMethodType.TED.value,
            PaymentMethodType.DOC.value,
            PaymentMethodType.DEBITO_AUTOMATICO.value,
            PaymentMethodType.TRANSFERENCIA.value,
        ]

    @property
    def is_instant(self) -> bool:
        """Verifica se é pagamento instantâneo."""
        return self.payment_type in [
            PaymentMethodType.PIX.value,
            PaymentMethodType.DINHEIRO.value,
            PaymentMethodType.CARTAO_DEBITO.value,
        ]

    @property
    def total_fee(self) -> float:
        """Retorna taxa total (fixa + percentual não calculável sem valor)."""
        fixed = float(self.fee_fixed or 0)
        return fixed

    def calculate_fee(self, value: float) -> float:
        """Calcula taxa para um valor."""
        fixed = float(self.fee_fixed or 0)
        percentage = float(self.fee_percentage or 0)
        return fixed + (value * percentage / 100)

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "code": self.code,
            "name": self.name,
            "payment_type": self.payment_type,
            "status": self.status,
            "is_electronic": self.is_electronic,
            "is_instant": self.is_instant,
            "days_to_process": self.days_to_process,
            "is_default": self.is_default,
        }
