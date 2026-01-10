"""
domains/financial/value_objects/accounting_amount.py - ACCOUNTING AMOUNT
========================================================================
Enterprise-grade accounting amount with debit/credit semantics
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Union, Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator


class AccountingAmount(BaseModel):
    """
    Valor contabil imutavel com semantica debito/credito.

    Implementa operacoes contabeis seguras mantendo
    integridade da partida dobrada.
    """

    model_config = ConfigDict(frozen=True)

    amount: Decimal = Field(..., ge=Decimal("0"), max_digits=15, decimal_places=2)
    entry_type: Literal["debit", "credit"]
    currency: str = Field(default="BRL", pattern=r"^[A-Z]{3}$")

    def __init__(
        self,
        amount: Union[Decimal, float, str, int],
        entry_type: Literal["debit", "credit"],
        currency: str = "BRL",
        **kwargs
    ):
        if isinstance(amount, (float, str, int)):
            amount = Decimal(str(amount)).quantize(
                Decimal('0.01'),
                rounding=ROUND_HALF_UP
            )
        super().__init__(amount=amount, entry_type=entry_type, currency=currency, **kwargs)

    @model_validator(mode='after')
    def validate_positive(self) -> 'AccountingAmount':
        """Valida que valor contabil e positivo."""
        if self.amount < 0:
            raise ValueError("Valor contabil deve ser positivo")
        return self

    def __str__(self) -> str:
        prefix = "D" if self.entry_type == "debit" else "C"
        return f"{prefix} {self.currency} {self.amount:,.2f}"

    def __repr__(self) -> str:
        return f"AccountingAmount({self.amount}, '{self.entry_type}', '{self.currency}')"

    @property
    def is_debit(self) -> bool:
        """Verifica se e debito."""
        return self.entry_type == "debit"

    @property
    def is_credit(self) -> bool:
        """Verifica se e credito."""
        return self.entry_type == "credit"

    @property
    def signed_amount(self) -> Decimal:
        """Retorna valor com sinal (debito positivo, credito negativo)."""
        return self.amount if self.is_debit else -self.amount

    def opposite(self) -> 'AccountingAmount':
        """Retorna contrapartida (inverte debito/credito)."""
        new_type: Literal["debit", "credit"] = "credit" if self.is_debit else "debit"
        return AccountingAmount(self.amount, new_type, self.currency)

    def format_brl(self) -> str:
        """Formata valor no padrao brasileiro."""
        formatted = f"{self.amount:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        prefix = "D" if self.is_debit else "C"
        return f"{prefix} R$ {formatted}"

    @classmethod
    def debit(cls, amount: Union[Decimal, float, str, int], currency: str = "BRL") -> 'AccountingAmount':
        """Cria lancamento a debito."""
        return cls(amount, "debit", currency)

    @classmethod
    def credit(cls, amount: Union[Decimal, float, str, int], currency: str = "BRL") -> 'AccountingAmount':
        """Cria lancamento a credito."""
        return cls(amount, "credit", currency)

    @classmethod
    def zero_debit(cls, currency: str = "BRL") -> 'AccountingAmount':
        """Cria debito zerado."""
        return cls(Decimal("0"), "debit", currency)

    @classmethod
    def zero_credit(cls, currency: str = "BRL") -> 'AccountingAmount':
        """Cria credito zerado."""
        return cls(Decimal("0"), "credit", currency)


class DebitCreditPair(BaseModel):
    """
    Par debito/credito balanceado.

    Garante que debitos = creditos para partida dobrada.
    """

    model_config = ConfigDict(frozen=True)

    debit: AccountingAmount
    credit: AccountingAmount

    @model_validator(mode='after')
    def validate_balance(self) -> 'DebitCreditPair':
        """Valida balanceamento debito = credito."""
        if self.debit.amount != self.credit.amount:
            raise ValueError(
                f"Debito ({self.debit.amount}) deve ser igual ao Credito ({self.credit.amount})"
            )
        if self.debit.currency != self.credit.currency:
            raise ValueError("Debito e Credito devem ter mesma moeda")
        if self.debit.entry_type != "debit":
            raise ValueError("Primeiro valor deve ser debito")
        if self.credit.entry_type != "credit":
            raise ValueError("Segundo valor deve ser credito")
        return self

    @property
    def amount(self) -> Decimal:
        """Retorna valor do par."""
        return self.debit.amount

    @property
    def currency(self) -> str:
        """Retorna moeda do par."""
        return self.debit.currency

    @classmethod
    def create(
        cls,
        amount: Union[Decimal, float, str, int],
        currency: str = "BRL"
    ) -> 'DebitCreditPair':
        """Cria par debito/credito balanceado."""
        return cls(
            debit=AccountingAmount.debit(amount, currency),
            credit=AccountingAmount.credit(amount, currency)
        )
