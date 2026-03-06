"""
Controller para operações bancárias (Cora, Inter).

Endpoints para consulta de saldos, extratos e status de conexão.
"""

import logging
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from core.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/banking", tags=["Banking"])


# --- Response Schemas ---


class BankBalanceItem(BaseModel):
    bank_code: str
    bank_name: str
    account: str
    balance: float
    available_balance: float
    blocked_balance: float
    updated_at: str


class BankingBalancesResponse(BaseModel):
    balances: list[BankBalanceItem]
    total_balance: float
    updated_at: str


class BankTransactionItem(BaseModel):
    id: str
    bank_code: str
    date: str
    description: str
    amount: float
    type: str  # credit | debit
    category: str | None = None
    balance_after: float | None = None


class BankingStatementResponse(BaseModel):
    transactions: list[BankTransactionItem]
    total_credits: float
    total_debits: float
    period_start: str
    period_end: str


class BankConnectionStatus(BaseModel):
    bank_code: str
    bank_name: str
    connected: bool
    last_sync: str | None = None
    error: str | None = None


# --- Helper ---


def _get_banking_service():
    """Retorna instância do BankingService com adapters configurados."""
    from modules.integrations.banking.services import BankingService

    return BankingService()


async def _try_adapter_balance(
    service,
    bank_code: str,
    bank_name: str,
    account_label: str,
) -> BankBalanceItem | None:
    """Tenta obter saldo de um adapter registrado."""
    try:
        balance = await service.get_balance(bank_code)
        return BankBalanceItem(
            bank_code=bank_code,
            bank_name=bank_name,
            account=account_label,
            balance=float(balance.total),
            available_balance=float(balance.available),
            blocked_balance=float(balance.blocked),
            updated_at=balance.updated_at.isoformat() if balance.updated_at else datetime.now().isoformat(),
        )
    except Exception as exc:
        logger.debug("Saldo indisponível para %s: %s", bank_name, str(exc))
        return BankBalanceItem(
            bank_code=bank_code,
            bank_name=bank_name,
            account=account_label,
            balance=0,
            available_balance=0,
            blocked_balance=0,
            updated_at=datetime.now().isoformat(),
        )


# --- Endpoints ---


@router.get("/balances", response_model=BankingBalancesResponse)
async def get_bank_balances(
    current_user=Depends(get_current_user),
):
    """Consulta saldos de todas as contas bancárias configuradas."""
    now = datetime.now().isoformat()
    balances: list[BankBalanceItem] = []

    # Bancos configurados no sistema
    banks = [
        ("403", "Banco Cora", "****-7"),
        ("077", "Banco Inter", "****-3"),
    ]

    service = _get_banking_service()

    for bank_code, bank_name, account_label in banks:
        item = await _try_adapter_balance(service, bank_code, bank_name, account_label)
        if item:
            balances.append(item)

    total = sum(b.available_balance for b in balances)

    return BankingBalancesResponse(
        balances=balances,
        total_balance=total,
        updated_at=now,
    )


@router.get("/statement", response_model=BankingStatementResponse)
async def get_bank_statement(
    days: int = Query(default=30, ge=1, le=365),
    bank_code: str | None = Query(default=None),
    current_user=Depends(get_current_user),
):
    """Consulta extrato bancário recente."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    transactions: list[BankTransactionItem] = []
    service = _get_banking_service()

    banks_to_query = []
    if bank_code:
        banks_to_query.append(bank_code)
    else:
        banks_to_query = ["403", "077"]

    for code in banks_to_query:
        try:
            statement = await service.get_statement(code, start_date, end_date)
            for tx in statement.transactions:
                tx_type = "credit" if tx.amount >= 0 else "debit"
                transactions.append(
                    BankTransactionItem(
                        id=tx.transaction_id,
                        bank_code=code,
                        date=tx.date.isoformat() if tx.date else "",
                        description=tx.description or "",
                        amount=float(abs(tx.amount)),
                        type=tx_type,
                        category=str(tx.transaction_type) if tx.transaction_type else None,
                    )
                )
        except Exception as exc:
            logger.debug("Extrato indisponível para banco %s: %s", code, str(exc))

    total_credits = sum(t.amount for t in transactions if t.type == "credit")
    total_debits = sum(t.amount for t in transactions if t.type == "debit")

    return BankingStatementResponse(
        transactions=transactions,
        total_credits=total_credits,
        total_debits=total_debits,
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
    )


@router.get("/status", response_model=list[BankConnectionStatus])
async def get_bank_status(
    current_user=Depends(get_current_user),
):
    """Consulta status de conexão dos bancos integrados."""
    statuses: list[BankConnectionStatus] = []

    banks = [
        ("403", "Banco Cora"),
        ("077", "Banco Inter"),
    ]

    service = _get_banking_service()

    for bank_code, bank_name in banks:
        try:
            # Tenta obter saldo como health check
            await service.get_balance(bank_code)
            statuses.append(
                BankConnectionStatus(
                    bank_code=bank_code,
                    bank_name=bank_name,
                    connected=True,
                    last_sync=datetime.now().isoformat(),
                )
            )
        except Exception as exc:
            statuses.append(
                BankConnectionStatus(
                    bank_code=bank_code,
                    bank_name=bank_name,
                    connected=False,
                    last_sync=None,
                    error=str(exc),
                )
            )

    return statuses
