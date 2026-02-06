"""
domains/financial/entities/chart_of_accounts.py - CHART OF ACCOUNTS
===================================================================
Enterprise chart of accounts entity with hierarchical structure
"""

from typing import Dict, List, Optional, Any, NewType
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

from .enums import AccountType, AccountStatus

# Strong typing for domain identifiers
AccountId = NewType('AccountId', UUID)


class AccountBalance(BaseModel):
    """Saldo da conta - Value Object."""

    model_config = ConfigDict(frozen=True)

    debit_balance: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    credit_balance: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    period_start: datetime
    period_end: datetime

    @property
    def net_balance(self) -> Decimal:
        """Saldo liquido (debitos - creditos)."""
        return self.debit_balance - self.credit_balance

    @property
    def balance_for_debit_nature(self) -> Decimal:
        """Saldo para contas de natureza devedora."""
        return self.debit_balance - self.credit_balance

    @property
    def balance_for_credit_nature(self) -> Decimal:
        """Saldo para contas de natureza credora."""
        return self.credit_balance - self.debit_balance


class AccountEntity(BaseModel):
    """
    Entidade de conta contabil.

    Representa uma conta no plano de contas com
    hierarquia e regras de negocio.
    """

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True
    )

    # Identity
    account_id: UUID = Field(default_factory=uuid4)
    account_code: str = Field(
        ...,
        pattern=r"^(\d{1,4})(\.\d{1,2}){0,4}$",
        description="Codigo hierarquico: 1.1.1.01"
    )
    account_name: str = Field(..., min_length=3, max_length=100)

    # Classification
    account_type: AccountType
    status: AccountStatus = Field(default=AccountStatus.ACTIVE)

    # Hierarchy
    parent_account_id: Optional[UUID] = None
    level: int = Field(..., ge=1, le=5)
    is_analytical: bool = Field(default=True)  # True = recebe lancamentos

    # Financial
    currency: str = Field(default="BRL", pattern=r"^[A-Z]{3}$")
    opening_balance: Decimal = Field(default=Decimal("0"))
    current_balance: Decimal = Field(default=Decimal("0"))

    # Metadata
    description: Optional[str] = Field(None, max_length=500)
    cost_center_required: bool = Field(default=False)
    project_required: bool = Field(default=False)

    # Multi-tenant
    tenant_id: UUID

    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_by: Optional[str] = None

    @field_validator('account_code')
    @classmethod
    def validate_account_code_format(cls, v: str) -> str:
        """Valida formato do codigo da conta."""
        parts = v.split('.')
        if len(parts) > 5:
            raise ValueError("Codigo de conta nao pode ter mais de 5 niveis")
        return v

    @model_validator(mode='after')
    def validate_account(self) -> 'AccountEntity':
        """Valida regras de negocio da conta."""
        # Valida nivel vs codigo
        parts = self.account_code.split('.')
        if len(parts) != self.level:
            raise ValueError(
                f"Nivel ({self.level}) deve corresponder a hierarquia do codigo ({len(parts)})"
            )

        # Contas sinteticas nao recebem lancamentos
        if not self.is_analytical and self.current_balance != Decimal("0"):
            # Contas sinteticas tem saldo calculado dos filhos
            pass  # Permitido para consolidacao

        return self

    # ==========================================================================
    # Business Methods
    # ==========================================================================

    @property
    def is_debit_nature(self) -> bool:
        """Verifica se conta tem natureza devedora."""
        return AccountType(self.account_type).is_debit_nature()

    @property
    def is_credit_nature(self) -> bool:
        """Verifica se conta tem natureza credora."""
        return AccountType(self.account_type).is_credit_nature()

    @property
    def is_balance_sheet(self) -> bool:
        """Verifica se e conta patrimonial."""
        return AccountType(self.account_type).is_balance_sheet_account()

    @property
    def is_income_statement(self) -> bool:
        """Verifica se e conta de resultado."""
        return AccountType(self.account_type).is_income_statement_account()

    @property
    def allows_posting(self) -> bool:
        """Verifica se permite lancamentos."""
        return (
            self.is_analytical and
            self.status == AccountStatus.ACTIVE
        )

    def calculate_balance(self, debits: Decimal, credits: Decimal) -> Decimal:
        """Calcula saldo baseado na natureza da conta."""
        if self.is_debit_nature:
            return self.opening_balance + debits - credits
        else:
            return self.opening_balance + credits - debits

    def apply_debit(self, amount: Decimal) -> Decimal:
        """Aplica debito e retorna novo saldo."""
        if not self.allows_posting:
            raise ValueError(f"Conta {self.account_code} nao permite lancamentos")

        if self.is_debit_nature:
            self.current_balance += amount
        else:
            self.current_balance -= amount

        self.updated_at = datetime.utcnow()
        return self.current_balance

    def apply_credit(self, amount: Decimal) -> Decimal:
        """Aplica credito e retorna novo saldo."""
        if not self.allows_posting:
            raise ValueError(f"Conta {self.account_code} nao permite lancamentos")

        if self.is_credit_nature:
            self.current_balance += amount
        else:
            self.current_balance -= amount

        self.updated_at = datetime.utcnow()
        return self.current_balance

    def activate(self, user_id: str) -> None:
        """Ativa a conta."""
        self.status = AccountStatus.ACTIVE
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

    def deactivate(self, user_id: str) -> None:
        """Desativa a conta."""
        if self.current_balance != Decimal("0"):
            raise ValueError("Nao e possivel desativar conta com saldo")
        self.status = AccountStatus.INACTIVE
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

    def block(self, user_id: str) -> None:
        """Bloqueia a conta."""
        self.status = AccountStatus.BLOCKED
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

    def get_account_hierarchy(self) -> List[str]:
        """Retorna hierarquia de codigos da conta."""
        parts = self.account_code.split('.')
        hierarchy = []
        current = ""
        for part in parts:
            current = f"{current}.{part}" if current else part
            hierarchy.append(current)
        return hierarchy

    @staticmethod
    def generate_child_code(parent_code: str, sequence: int) -> str:
        """Gera codigo para conta filha."""
        return f"{parent_code}.{sequence:02d}"


class ChartOfAccountsEntity(BaseModel):
    """
    Plano de contas completo.

    Gerencia hierarquia de contas e validacoes do plano.
    """

    model_config = ConfigDict(validate_assignment=True)

    # Identity
    chart_id: UUID = Field(default_factory=uuid4)
    chart_name: str = Field(..., min_length=3, max_length=100)
    chart_version: str = Field(default="1.0")

    # Configuration
    fiscal_year: int = Field(..., ge=2020, le=2035)
    base_currency: str = Field(default="BRL", pattern=r"^[A-Z]{3}$")
    max_levels: int = Field(default=5, ge=3, le=7)

    # Accounts
    accounts: Dict[str, AccountEntity] = Field(default_factory=dict)

    # Multi-tenant
    tenant_id: UUID

    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str

    def add_account(self, account: AccountEntity) -> None:
        """Adiciona conta ao plano."""
        # Valida tenant
        if account.tenant_id != self.tenant_id:
            raise ValueError("Conta pertence a outro tenant")

        # Valida nivel maximo
        if account.level > self.max_levels:
            raise ValueError(f"Nivel {account.level} excede maximo {self.max_levels}")

        # Valida unicidade
        if account.account_code in self.accounts:
            raise ValueError(f"Conta {account.account_code} ja existe")

        # Valida hierarquia
        if account.parent_account_id:
            parent = self._find_account_by_id(account.parent_account_id)
            if not parent:
                raise ValueError("Conta pai nao encontrada")
            if parent.is_analytical:
                raise ValueError("Conta pai deve ser sintetica")

        self.accounts[account.account_code] = account
        self.updated_at = datetime.utcnow()

    def get_account(self, account_code: str) -> Optional[AccountEntity]:
        """Busca conta por codigo."""
        return self.accounts.get(account_code)

    def get_account_by_id(self, account_id: UUID) -> Optional[AccountEntity]:
        """Busca conta por ID."""
        return self._find_account_by_id(account_id)

    def _find_account_by_id(self, account_id: UUID) -> Optional[AccountEntity]:
        """Busca interna por ID."""
        for account in self.accounts.values():
            if account.account_id == account_id:
                return account
        return None

    def get_analytical_accounts(self) -> List[AccountEntity]:
        """Retorna todas as contas analiticas."""
        return [acc for acc in self.accounts.values() if acc.is_analytical]

    def get_synthetic_accounts(self) -> List[AccountEntity]:
        """Retorna todas as contas sinteticas."""
        return [acc for acc in self.accounts.values() if not acc.is_analytical]

    def get_accounts_by_type(self, account_type: AccountType) -> List[AccountEntity]:
        """Retorna contas por tipo."""
        return [
            acc for acc in self.accounts.values()
            if acc.account_type == account_type.value
        ]

    def get_children(self, parent_code: str) -> List[AccountEntity]:
        """Retorna contas filhas de uma conta."""
        return [
            acc for acc in self.accounts.values()
            if acc.account_code.startswith(f"{parent_code}.") and
            acc.account_code.count('.') == parent_code.count('.') + 1
        ]

    def calculate_synthetic_balances(self) -> Dict[str, Decimal]:
        """Calcula saldos das contas sinteticas."""
        balances: Dict[str, Decimal] = {}

        # Primeiro, copia saldos das analiticas
        for code, account in self.accounts.items():
            if account.is_analytical:
                balances[code] = account.current_balance

        # Depois, calcula sinteticas de baixo para cima
        for level in range(self.max_levels - 1, 0, -1):
            for code, account in self.accounts.items():
                if account.level == level and not account.is_analytical:
                    children = self.get_children(code)
                    balances[code] = sum(
                        balances.get(child.account_code, Decimal("0"))
                        for child in children
                    )

        return balances

    def validate_hierarchy(self) -> List[str]:
        """Valida integridade da hierarquia."""
        errors = []

        for code, account in self.accounts.items():
            # Verifica se pai existe
            if account.level > 1:
                parent_code = '.'.join(code.split('.')[:-1])
                if parent_code not in self.accounts:
                    errors.append(f"Conta {code}: pai {parent_code} nao existe")

        return errors

    def export_structure(self) -> List[Dict[str, Any]]:
        """Exporta estrutura do plano de contas."""
        return [
            {
                "code": acc.account_code,
                "name": acc.account_name,
                "type": acc.account_type,
                "level": acc.level,
                "is_analytical": acc.is_analytical,
                "balance": str(acc.current_balance)
            }
            for acc in sorted(self.accounts.values(), key=lambda x: x.account_code)
        ]
