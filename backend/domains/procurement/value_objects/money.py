"""
domains/procurement/value_objects/money.py - MONEY VALUE OBJECT
===============================================================
Enterprise-grade monetary value object with precision
"""

from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, ConfigDict, Field


class Money(BaseModel):
    """
    Valor monetario imutavel com precisao decimal.

    Implementa operacoes matematicas seguras para valores financeiros.
    """

    model_config = ConfigDict(frozen=True)  # Immutable value object

    amount: Decimal = Field(..., max_digits=15, decimal_places=2)
    currency: str = Field(default="BRL", pattern=r"^[A-Z]{3}$")

    def __init__(self, amount: Decimal | float | str | int = Decimal("0"), currency: str = "BRL", **kwargs):
        if isinstance(amount, (float, str, int)):
            amount = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        super().__init__(amount=amount, currency=currency, **kwargs)

    def __add__(self, other: "Money") -> "Money":
        """Soma monetaria."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        """Subtracao monetaria."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {self.currency} and {other.currency}")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, multiplier: Decimal | int | float) -> "Money":
        """Multiplicacao monetaria."""
        if isinstance(multiplier, (int, float)):
            multiplier = Decimal(str(multiplier))
        result = (self.amount * multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return Money(result, self.currency)

    def __truediv__(self, divisor: Decimal | int | float) -> "Money":
        """Divisao monetaria."""
        if isinstance(divisor, (int, float)):
            divisor = Decimal(str(divisor))
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        result = (self.amount / divisor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return Money(result, self.currency)

    def __lt__(self, other: "Money") -> bool:
        self._check_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        self._check_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        self._check_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        self._check_same_currency(other)
        return self.amount >= other.amount

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    def __str__(self) -> str:
        return self.format_brl()

    def __repr__(self) -> str:
        return f"Money({self.amount}, '{self.currency}')"

    def _check_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare {self.currency} and {other.currency}")

    @property
    def is_positive(self) -> bool:
        """Verifica se valor e positivo."""
        return self.amount > 0

    @property
    def is_negative(self) -> bool:
        """Verifica se valor e negativo."""
        return self.amount < 0

    @property
    def is_zero(self) -> bool:
        """Verifica se valor e zero."""
        return self.amount == 0

    def abs(self) -> "Money":
        """Retorna valor absoluto."""
        return Money(abs(self.amount), self.currency)

    def negate(self) -> "Money":
        """Retorna valor negado."""
        return Money(-self.amount, self.currency)

    def percentage(self, percent: Decimal | float) -> "Money":
        """Calcula percentual do valor."""
        if isinstance(percent, float):
            percent = Decimal(str(percent))
        return self * (percent / Decimal("100"))

    def format_brl(self) -> str:
        """Formata valor no padrao brasileiro."""
        formatted = f"{self.amount:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"

    def format_international(self) -> str:
        """Formata valor no padrao internacional."""
        return f"{self.currency} {self.amount:,.2f}"

    @classmethod
    def zero(cls, currency: str = "BRL") -> "Money":
        """Cria valor zero."""
        return cls(Decimal("0"), currency)

    @classmethod
    def from_cents(cls, cents: int, currency: str = "BRL") -> "Money":
        """Cria valor a partir de centavos."""
        return cls(Decimal(cents) / Decimal("100"), currency)
