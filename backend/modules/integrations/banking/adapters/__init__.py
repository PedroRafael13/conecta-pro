"""
Adapters para integracao bancaria Open Banking.

Exporta os adapters disponiveis para uso pelo BankingService.
"""

from .base import (
    AccountBalance,
    AccountType,
    AuthenticationError,
    BankCode,
    BankCredentials,
    BankingAdapterError,
    BankStatement,
    BankTransaction,
    BaseBankingAdapter,
    InsufficientFundsError,
    InvalidAccountError,
    PaymentRequest,
    PaymentResponse,
    PaymentStatus,
    PixKey,
    RateLimitError,
    TransactionType,
)
from .bb import BBAdapter
from .bradesco import BradescoAdapter
from .inter import InterAdapter
from .itau import ItauAdapter

__all__ = [
    # Base
    "BaseBankingAdapter",
    "BankCredentials",
    "BankCode",
    # Types
    "AccountType",
    "TransactionType",
    "PaymentStatus",
    # Data classes
    "AccountBalance",
    "BankTransaction",
    "BankStatement",
    "PaymentRequest",
    "PaymentResponse",
    "PixKey",
    # Errors
    "BankingAdapterError",
    "AuthenticationError",
    "RateLimitError",
    "InsufficientFundsError",
    "InvalidAccountError",
    # Adapters
    "BBAdapter",
    "ItauAdapter",
    "BradescoAdapter",
    "InterAdapter",
]
