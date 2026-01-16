"""
Modulo de integracao bancaria Open Banking.

Fornece adapters para os principais bancos brasileiros
e servico unificado para operacoes bancarias.
"""

from .adapters import (
    AccountBalance,
    AccountType,
    BankCode,
    BankCredentials,
    BankingAdapterError,
    BankStatement,
    BankTransaction,
    BBAdapter,
    BradescoAdapter,
    ItauAdapter,
    PaymentRequest,
    PaymentResponse,
    PaymentStatus,
    PixKey,
    TransactionType,
)
from .services import BankingService

__all__ = [
    # Service
    "BankingService",
    # Adapters
    "BBAdapter",
    "ItauAdapter",
    "BradescoAdapter",
    # Types
    "BankCode",
    "AccountType",
    "TransactionType",
    "PaymentStatus",
    # Data classes
    "BankCredentials",
    "AccountBalance",
    "BankTransaction",
    "BankStatement",
    "PaymentRequest",
    "PaymentResponse",
    "PixKey",
    # Errors
    "BankingAdapterError",
]
