"""Model para contas bancarias."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.financial.models.bank_transaction import BankTransaction


class BankAccountType(StrEnum):
    """Tipo de conta bancaria."""

    CORRENTE = "corrente"
    POUPANCA = "poupanca"
    APLICACAO = "aplicacao"
    INVESTIMENTO = "investimento"
    CAIXA = "caixa"  # Caixa fisico do condominio
    DIGITAL = "digital"  # Conta digital (Nubank, Inter, etc)


class BankAccountStatus(StrEnum):
    """Status da conta bancaria."""

    ATIVA = "ativa"
    INATIVA = "inativa"
    BLOQUEADA = "bloqueada"
    ENCERRADA = "encerrada"


class PixKeyType(StrEnum):
    """Tipo de chave PIX."""

    CPF = "cpf"
    CNPJ = "cnpj"
    EMAIL = "email"
    TELEFONE = "telefone"
    ALEATORIA = "aleatoria"


class BankAccount(Base):
    """Conta bancaria do condominio."""

    __tablename__ = "bank_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificacao
    name = Column(String(100), nullable=False)  # Nome amigavel
    description = Column(Text, nullable=True)

    # Dados bancarios
    bank_code = Column(String(10), nullable=False)  # Codigo do banco (ex: 001, 341)
    bank_name = Column(String(100), nullable=False)  # Nome do banco
    agency = Column(String(10), nullable=False)  # Numero da agencia
    agency_digit = Column(String(2), nullable=True)  # Digito da agencia
    account_number = Column(String(20), nullable=False)  # Numero da conta
    account_digit = Column(String(2), nullable=False)  # Digito da conta

    # Tipo e status
    account_type = Column(
        String(20),
        nullable=False,
        default=BankAccountType.CORRENTE.value,
    )
    status = Column(
        String(20),
        nullable=False,
        default=BankAccountStatus.ATIVA.value,
    )

    # Titular
    holder_name = Column(String(150), nullable=True)  # Nome do titular
    holder_document = Column(String(20), nullable=True)  # CPF/CNPJ do titular

    # Saldos
    opening_balance = Column(Numeric(15, 2), default=Decimal("0"))  # Saldo inicial
    current_balance = Column(Numeric(15, 2), default=Decimal("0"))  # Saldo atual
    available_balance = Column(Numeric(15, 2), default=Decimal("0"))  # Saldo disponivel
    blocked_balance = Column(Numeric(15, 2), default=Decimal("0"))  # Saldo bloqueado
    last_balance_update = Column(DateTime, nullable=True)

    # PIX
    pix_enabled = Column(Boolean, default=False)
    pix_key = Column(String(100), nullable=True)
    pix_key_type = Column(String(20), nullable=True)

    # Boleto
    boleto_enabled = Column(Boolean, default=False)
    boleto_wallet = Column(String(10), nullable=True)  # Carteira de cobranca
    boleto_agreement = Column(String(20), nullable=True)  # Convenio
    boleto_variation = Column(String(10), nullable=True)  # Variacao da carteira
    boleto_assignor_code = Column(String(20), nullable=True)  # Codigo do cedente

    # Integracao bancaria
    integration_enabled = Column(Boolean, default=False)
    integration_type = Column(String(30), nullable=True)  # api, ofx, cnab
    integration_config = Column(JSONB, default=dict)
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_status = Column(String(20), nullable=True)

    # Configuracoes
    is_main_account = Column(Boolean, default=False)  # Conta principal
    allow_negative_balance = Column(Boolean, default=False)
    overdraft_limit = Column(Numeric(15, 2), default=Decimal("0"))  # Limite do cheque especial
    minimum_balance = Column(Numeric(15, 2), default=Decimal("0"))  # Saldo minimo

    # Contatos do banco
    bank_manager_name = Column(String(100), nullable=True)
    bank_manager_phone = Column(String(20), nullable=True)
    bank_manager_email = Column(String(100), nullable=True)

    # Data de abertura/encerramento
    opening_date = Column(Date, nullable=True)
    closing_date = Column(Date, nullable=True)

    # Observacoes
    notes = Column(Text, nullable=True)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relationships
    transactions: list["BankTransaction"] = relationship(
        "BankTransaction",
        back_populates="bank_account",
        lazy="dynamic",
    )

    __table_args__ = (
        Index("ix_bank_accounts_condominio", "condominio_id"),
        Index("ix_bank_accounts_status", "status"),
        Index("ix_bank_accounts_type", "account_type"),
        Index("ix_bank_accounts_bank", "bank_code"),
        Index(
            "ix_bank_accounts_unique",
            "condominio_id",
            "bank_code",
            "agency",
            "account_number",
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        return f"<BankAccount {self.bank_name} - {self.account_number}>"

    @property
    def full_account_number(self) -> str:
        """Retorna numero completo da conta."""
        agency = f"{self.agency}-{self.agency_digit}" if self.agency_digit else self.agency
        account = f"{self.account_number}-{self.account_digit}"
        return f"{agency} / {account}"

    @property
    def is_active(self) -> bool:
        """Verifica se esta ativa."""
        return self.status == BankAccountStatus.ATIVA.value and self.ativo

    @property
    def has_pix(self) -> bool:
        """Verifica se tem PIX habilitado."""
        return self.pix_enabled and self.pix_key is not None

    @property
    def has_boleto(self) -> bool:
        """Verifica se tem boleto habilitado."""
        return self.boleto_enabled and self.boleto_wallet is not None

    @property
    def total_available(self) -> Decimal:
        """Retorna saldo total disponivel incluindo limite."""
        base = self.available_balance or Decimal("0")
        if self.allow_negative_balance:
            return base + (self.overdraft_limit or Decimal("0"))
        return base

    def update_balance(
        self,
        amount: Decimal,
        is_credit: bool = True,
    ) -> None:
        """Atualiza saldo da conta."""
        if is_credit:
            self.current_balance = (self.current_balance or Decimal("0")) + amount
            self.available_balance = (self.available_balance or Decimal("0")) + amount
        else:
            self.current_balance = (self.current_balance or Decimal("0")) - amount
            self.available_balance = (self.available_balance or Decimal("0")) - amount
        self.last_balance_update = datetime.utcnow()

    def block_balance(self, amount: Decimal) -> bool:
        """Bloqueia parte do saldo."""
        if amount > (self.available_balance or Decimal("0")):
            return False
        self.available_balance = (self.available_balance or Decimal("0")) - amount
        self.blocked_balance = (self.blocked_balance or Decimal("0")) + amount
        return True

    def unblock_balance(self, amount: Decimal) -> bool:
        """Desbloqueia parte do saldo."""
        if amount > (self.blocked_balance or Decimal("0")):
            return False
        self.blocked_balance = (self.blocked_balance or Decimal("0")) - amount
        self.available_balance = (self.available_balance or Decimal("0")) + amount
        return True

    def can_debit(self, amount: Decimal) -> bool:
        """Verifica se pode debitar valor."""
        return amount <= self.total_available

    def activate(self) -> None:
        """Ativa a conta."""
        self.status = BankAccountStatus.ATIVA.value

    def deactivate(self) -> None:
        """Desativa a conta."""
        self.status = BankAccountStatus.INATIVA.value

    def block(self) -> None:
        """Bloqueia a conta."""
        self.status = BankAccountStatus.BLOQUEADA.value

    def close(self, closing_date: date | None = None) -> None:
        """Encerra a conta."""
        self.status = BankAccountStatus.ENCERRADA.value
        self.closing_date = closing_date or date.today()
        self.ativo = False

    def set_as_main(self) -> None:
        """Define como conta principal."""
        self.is_main_account = True

    def to_dict(self) -> dict:
        """Converte para dicionario."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "bank_code": self.bank_code,
            "bank_name": self.bank_name,
            "agency": self.agency,
            "account_number": self.account_number,
            "full_account_number": self.full_account_number,
            "account_type": self.account_type,
            "status": self.status,
            "holder_name": self.holder_name,
            "current_balance": float(self.current_balance or 0),
            "available_balance": float(self.available_balance or 0),
            "blocked_balance": float(self.blocked_balance or 0),
            "pix_enabled": self.pix_enabled,
            "pix_key": self.pix_key,
            "boleto_enabled": self.boleto_enabled,
            "is_main_account": self.is_main_account,
            "is_active": self.is_active,
            "opening_date": self.opening_date.isoformat() if self.opening_date else None,
            "last_balance_update": (self.last_balance_update.isoformat() if self.last_balance_update else None),
        }
