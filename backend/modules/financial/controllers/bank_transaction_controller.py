"""Controller para transações bancárias."""

import logging
from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_session
from modules.financial.models import (
    ReconciliationStatus,
    TransactionCategory,
    TransactionStatus,
    TransactionType,
)
from modules.financial.repositories import BankAccountRepository, BankTransactionRepository
from modules.financial.schemas import (
    BankTransactionCreate,
    BankTransactionFilter,
    BankTransactionImport,
    BankTransactionResponse,
    BankTransactionUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bank-transactions", tags=["Transações Bancárias"])


def get_repository(session: AsyncSession = Depends(get_session)) -> BankTransactionRepository:
    """Retorna instância do BankTransactionRepository."""
    return BankTransactionRepository(session)


def get_account_repository(session: AsyncSession = Depends(get_session)) -> BankAccountRepository:
    """Retorna instância do BankAccountRepository."""
    return BankAccountRepository(session)


# ==================== CRUD ====================


@router.post(
    "/",
    response_model=BankTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar transação",
)
async def create_transaction(
    data: BankTransactionCreate,
    repo: BankTransactionRepository = Depends(get_repository),
    account_repo: BankAccountRepository = Depends(get_account_repository),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> BankTransactionResponse:
    """Cria nova transação bancária."""
    # Verifica se conta existe
    account = await account_repo.get_by_id(data.bank_account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta bancária não encontrada",
        )

    try:
        transaction = await repo.create(data.model_dump())

        # Atualiza saldo da conta se transação efetivada
        if transaction.status == TransactionStatus.EFETIVADA:
            if transaction.transaction_type == TransactionType.CREDITO:
                account.update_balance(transaction.amount)
            else:
                account.update_balance(-transaction.amount)
            await session.commit()

        logger.info(f"Transação criada: {transaction.id} por {current_user.get('email')}")
        return BankTransactionResponse.model_validate(transaction)
    except Exception as e:
        logger.error(f"Erro ao criar transação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar transação",
        )


@router.get(
    "/",
    response_model=List[BankTransactionResponse],
    summary="Listar transações",
)
async def list_transactions(
    bank_account_id: UUID,
    transaction_type: Optional[TransactionType] = Query(None),
    category: Optional[TransactionCategory] = Query(None),
    transaction_status: Optional[TransactionStatus] = Query(None),
    reconciliation_status: Optional[ReconciliationStatus] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    min_amount: Optional[Decimal] = Query(None),
    max_amount: Optional[Decimal] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    repo: BankTransactionRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> List[BankTransactionResponse]:
    """Lista transações bancárias com filtros."""
    filters = BankTransactionFilter(
        bank_account_id=bank_account_id,
        transaction_type=transaction_type,
        category=category,
        status=transaction_status,
        reconciliation_status=reconciliation_status,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
    )
    transactions = await repo.list_with_filters(filters, skip=skip, limit=limit)
    return [BankTransactionResponse.model_validate(t) for t in transactions]


@router.get(
    "/pending-reconciliation",
    response_model=List[BankTransactionResponse],
    summary="Transações pendentes de conciliação",
)
async def get_pending_reconciliation(
    bank_account_id: UUID,
    limit: int = Query(100, ge=1, le=500),
    repo: BankTransactionRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> List[BankTransactionResponse]:
    """Retorna transações pendentes de conciliação bancária."""
    transactions = await repo.get_pending_reconciliation(bank_account_id, limit)
    return [BankTransactionResponse.model_validate(t) for t in transactions]


@router.get(
    "/by-period",
    response_model=List[BankTransactionResponse],
    summary="Transações por período",
)
async def get_by_period(
    bank_account_id: UUID,
    start_date: date = Query(..., description="Data inicial"),
    end_date: date = Query(..., description="Data final"),
    repo: BankTransactionRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> List[BankTransactionResponse]:
    """Retorna transações em um período específico."""
    transactions = await repo.get_by_period(bank_account_id, start_date, end_date)
    return [BankTransactionResponse.model_validate(t) for t in transactions]


@router.get(
    "/summary",
    summary="Resumo de transações",
)
async def get_summary(
    bank_account_id: UUID,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    repo: BankTransactionRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Retorna resumo de transações por período."""
    filters = BankTransactionFilter(
        bank_account_id=bank_account_id,
        start_date=start_date,
        end_date=end_date,
    )
    transactions = await repo.list_with_filters(filters, skip=0, limit=10000)

    total_credits = Decimal("0")
    total_debits = Decimal("0")
    by_category = {}

    for tx in transactions:
        if tx.transaction_type == TransactionType.CREDITO:
            total_credits += tx.amount
        else:
            total_debits += tx.amount

        cat = tx.category.value
        if cat not in by_category:
            by_category[cat] = {"count": 0, "total": Decimal("0")}
        by_category[cat]["count"] += 1
        by_category[cat]["total"] += tx.amount

    return {
        "period": {"start": start_date, "end": end_date},
        "total_transactions": len(transactions),
        "total_credits": total_credits,
        "total_debits": total_debits,
        "net_flow": total_credits - total_debits,
        "by_category": by_category,
    }


@router.get(
    "/{transaction_id}",
    response_model=BankTransactionResponse,
    summary="Obter transação",
)
async def get_transaction(
    transaction_id: UUID,
    repo: BankTransactionRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> BankTransactionResponse:
    """Retorna transação pelo ID."""
    transaction = await repo.get_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada",
        )
    return BankTransactionResponse.model_validate(transaction)


@router.put(
    "/{transaction_id}",
    response_model=BankTransactionResponse,
    summary="Atualizar transação",
)
async def update_transaction(
    transaction_id: UUID,
    data: BankTransactionUpdate,
    repo: BankTransactionRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> BankTransactionResponse:
    """Atualiza transação bancária."""
    transaction = await repo.get_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada",
        )

    if transaction.reconciliation_status == ReconciliationStatus.CONCILIADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível alterar transação já conciliada",
        )

    update_data = data.model_dump(exclude_unset=True)
    updated = await repo.update(transaction_id, update_data)
    logger.info(f"Transação atualizada: {transaction_id} por {current_user.get('email')}")
    return BankTransactionResponse.model_validate(updated)


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir transação",
)
async def delete_transaction(
    transaction_id: UUID,
    repo: BankTransactionRepository = Depends(get_repository),
    account_repo: BankAccountRepository = Depends(get_account_repository),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> None:
    """Exclui transação bancária."""
    transaction = await repo.get_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada",
        )

    if transaction.reconciliation_status == ReconciliationStatus.CONCILIADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir transação já conciliada",
        )

    # Reverte saldo se transação estava efetivada
    if transaction.status == TransactionStatus.EFETIVADA:
        account = await account_repo.get_by_id(transaction.bank_account_id)
        if account:
            if transaction.transaction_type == TransactionType.CREDITO:
                account.update_balance(-transaction.amount)
            else:
                account.update_balance(transaction.amount)

    await repo.delete(transaction_id)
    await session.commit()
    logger.info(f"Transação excluída: {transaction_id} por {current_user.get('email')}")


# ==================== OPERAÇÕES ====================


@router.post(
    "/{transaction_id}/confirm",
    response_model=BankTransactionResponse,
    summary="Confirmar transação",
)
async def confirm_transaction(
    transaction_id: UUID,
    repo: BankTransactionRepository = Depends(get_repository),
    account_repo: BankAccountRepository = Depends(get_account_repository),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> BankTransactionResponse:
    """Confirma transação pendente."""
    transaction = await repo.get_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada",
        )

    if transaction.status != TransactionStatus.PENDENTE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas transações pendentes podem ser confirmadas",
        )

    # Atualiza status
    updated = await repo.update(transaction_id, {"status": TransactionStatus.EFETIVADA})

    # Atualiza saldo
    account = await account_repo.get_by_id(transaction.bank_account_id)
    if account:
        if transaction.transaction_type == TransactionType.CREDITO:
            account.update_balance(transaction.amount)
        else:
            account.update_balance(-transaction.amount)

    await session.commit()
    logger.info(f"Transação confirmada: {transaction_id} por {current_user.get('email')}")
    return BankTransactionResponse.model_validate(updated)


@router.post(
    "/{transaction_id}/cancel",
    response_model=BankTransactionResponse,
    summary="Cancelar transação",
)
async def cancel_transaction(
    transaction_id: UUID,
    reason: str = Query(..., min_length=5, max_length=500),
    repo: BankTransactionRepository = Depends(get_repository),
    account_repo: BankAccountRepository = Depends(get_account_repository),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> BankTransactionResponse:
    """Cancela transação."""
    transaction = await repo.get_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada",
        )

    if transaction.reconciliation_status == ReconciliationStatus.CONCILIADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível cancelar transação conciliada",
        )

    # Reverte saldo se estava efetivada
    if transaction.status == TransactionStatus.EFETIVADA:
        account = await account_repo.get_by_id(transaction.bank_account_id)
        if account:
            if transaction.transaction_type == TransactionType.CREDITO:
                account.update_balance(-transaction.amount)
            else:
                account.update_balance(transaction.amount)

    # Atualiza status
    updated = await repo.update(
        transaction_id,
        {
            "status": TransactionStatus.CANCELADA,
            "notes": f"{transaction.notes or ''}\nCancelamento: {reason}".strip(),
        },
    )

    await session.commit()
    logger.info(
        f"Transação cancelada: {transaction_id} por {current_user.get('email')}, "
        f"motivo: {reason}"
    )
    return BankTransactionResponse.model_validate(updated)


@router.post(
    "/{transaction_id}/reconcile",
    response_model=BankTransactionResponse,
    summary="Conciliar transação",
)
async def reconcile_transaction(
    transaction_id: UUID,
    statement_reference: Optional[str] = Query(None, max_length=100),
    repo: BankTransactionRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> BankTransactionResponse:
    """Marca transação como conciliada com extrato bancário."""
    transaction = await repo.get_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada",
        )

    if transaction.status != TransactionStatus.EFETIVADA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas transações efetivadas podem ser conciliadas",
        )

    update_data = {
        "reconciliation_status": ReconciliationStatus.CONCILIADO,
        "reconciled_at": date.today(),
    }
    if statement_reference:
        update_data["statement_reference"] = statement_reference

    updated = await repo.update(transaction_id, update_data)
    logger.info(f"Transação conciliada: {transaction_id} por {current_user.get('email')}")
    return BankTransactionResponse.model_validate(updated)


# ==================== IMPORTAÇÃO ====================


@router.post(
    "/import",
    summary="Importar transações de arquivo",
)
async def import_transactions(
    data: BankTransactionImport,
    repo: BankTransactionRepository = Depends(get_repository),
    account_repo: BankAccountRepository = Depends(get_account_repository),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Importa transações de extrato (OFX, CSV)."""
    # Verifica se conta existe
    account = await account_repo.get_by_id(data.bank_account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta bancária não encontrada",
        )

    created = 0
    duplicates = 0
    errors = []

    for i, tx_data in enumerate(data.transactions):
        try:
            # Verifica duplicidade por referência
            if tx_data.reference:
                existing = await repo.list_with_filters(
                    BankTransactionFilter(
                        bank_account_id=data.bank_account_id,
                    ),
                    skip=0,
                    limit=1,
                )
                if existing and any(t.statement_reference == tx_data.reference for t in existing):
                    duplicates += 1
                    continue

            # Cria transação
            await repo.create(
                {
                    "bank_account_id": data.bank_account_id,
                    "transaction_type": tx_data.transaction_type,
                    "category": tx_data.category or TransactionCategory.OUTROS,
                    "amount": tx_data.amount,
                    "description": tx_data.description,
                    "transaction_date": tx_data.transaction_date,
                    "statement_reference": tx_data.reference,
                    "status": TransactionStatus.EFETIVADA,
                    "reconciliation_status": ReconciliationStatus.PENDENTE,
                }
            )
            created += 1
        except Exception as e:
            errors.append({"index": i, "error": str(e)})

    await session.commit()

    logger.info(
        f"Importação de transações: {created} criadas, {duplicates} duplicadas, "
        f"{len(errors)} erros, por {current_user.get('email')}"
    )

    return {
        "success": True,
        "created": created,
        "duplicates": duplicates,
        "errors": errors[:10],  # Limita erros retornados
        "total_processed": len(data.transactions),
    }


@router.post(
    "/import/ofx",
    summary="Importar arquivo OFX",
)
async def import_ofx_file(
    bank_account_id: UUID = Query(...),
    file: UploadFile = File(..., description="Arquivo OFX"),
    repo: BankTransactionRepository = Depends(get_repository),
    account_repo: BankAccountRepository = Depends(get_account_repository),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Importa transações de arquivo OFX."""
    if not file.filename.lower().endswith(".ofx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo deve ser do tipo OFX",
        )

    # Verifica se conta existe
    account = await account_repo.get_by_id(bank_account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta bancária não encontrada",
        )

    try:
        content = await file.read()
        # Parse OFX (simplificado - em produção usar biblioteca ofxparse)
        transactions = _parse_ofx(content.decode("latin-1"))

        created = 0
        for tx in transactions:
            await repo.create(
                {
                    "bank_account_id": bank_account_id,
                    "transaction_type": tx["type"],
                    "category": TransactionCategory.OUTROS,
                    "amount": tx["amount"],
                    "description": tx["description"],
                    "transaction_date": tx["date"],
                    "statement_reference": tx["fitid"],
                    "status": TransactionStatus.EFETIVADA,
                    "reconciliation_status": ReconciliationStatus.PENDENTE,
                }
            )
            created += 1

        await session.commit()

        logger.info(
            f"Arquivo OFX importado: {created} transações, " f"por {current_user.get('email')}"
        )

        return {
            "success": True,
            "created": created,
            "filename": file.filename,
        }

    except Exception as e:
        logger.error(f"Erro ao importar OFX: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao processar arquivo OFX: {str(e)}",
        )


def _parse_ofx(content: str) -> List[dict]:
    """Parse simplificado de arquivo OFX."""
    import re
    from datetime import datetime

    transactions = []

    # Busca transações
    stmttrn_pattern = r"<STMTTRN>(.*?)</STMTTRN>"
    matches = re.findall(stmttrn_pattern, content, re.DOTALL)

    for match in matches:
        tx = {}

        # Tipo
        trntype = re.search(r"<TRNTYPE>(.*?)[\n<]", match)
        if trntype:
            tx["type"] = (
                TransactionType.CREDITO
                if trntype.group(1).strip() in ["CREDIT", "DEP"]
                else TransactionType.DEBITO
            )

        # Data
        dtposted = re.search(r"<DTPOSTED>(\d{8})", match)
        if dtposted:
            tx["date"] = datetime.strptime(dtposted.group(1), "%Y%m%d").date()

        # Valor
        trnamt = re.search(r"<TRNAMT>([-\d.]+)", match)
        if trnamt:
            tx["amount"] = abs(Decimal(trnamt.group(1)))

        # FITID
        fitid = re.search(r"<FITID>(.*?)[\n<]", match)
        if fitid:
            tx["fitid"] = fitid.group(1).strip()

        # Descrição
        memo = re.search(r"<MEMO>(.*?)[\n<]", match)
        name = re.search(r"<NAME>(.*?)[\n<]", match)
        tx["description"] = (
            (memo or name or type("", (), {"group": lambda s, x: "Transação OFX"})())
            .group(1)
            .strip()
        )

        if all(k in tx for k in ["type", "date", "amount", "fitid"]):
            transactions.append(tx)

    return transactions
