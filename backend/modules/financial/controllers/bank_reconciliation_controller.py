"""Controller para conciliação bancária."""

import csv
import io
import logging
from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_session
from modules.financial.models import (
    ReconciliationPeriodType,
    ReconciliationStatus,
    TransactionCategory,
    TransactionStatus,
    TransactionType,
)
from modules.financial.repositories import (
    BankAccountRepository,
    BankReconciliationRepository,
    BankTransactionRepository,
)
from modules.financial.schemas import (
    BankReconciliationCreate,
    BankReconciliationResponse,
    BankReconciliationUpdate,
    ReconciliationAdjustment,
    ReconciliationItemMatch,
    StatementImport,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bank-reconciliations", tags=["Conciliação Bancária"])


def get_repository(session: AsyncSession = Depends(get_session)) -> BankReconciliationRepository:
    """Retorna instância do BankReconciliationRepository."""
    return BankReconciliationRepository(session)


def get_account_repository(session: AsyncSession = Depends(get_session)) -> BankAccountRepository:
    """Retorna instância do BankAccountRepository."""
    return BankAccountRepository(session)


def get_transaction_repository(
    session: AsyncSession = Depends(get_session),
) -> BankTransactionRepository:
    """Retorna instância do BankTransactionRepository."""
    return BankTransactionRepository(session)


# ==================== CRUD ====================


@router.post(
    "",
    response_model=BankReconciliationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar conciliação",
)
async def create_reconciliation(
    data: BankReconciliationCreate,
    repo: BankReconciliationRepository = Depends(get_repository),
    account_repo: BankAccountRepository = Depends(get_account_repository),
    current_user: dict = Depends(get_current_user),
) -> BankReconciliationResponse:
    """Cria nova conciliação bancária."""
    # Verifica se conta existe
    account = await account_repo.get_by_id(data.bank_account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta bancária não encontrada",
        )

    # Verifica se já existe conciliação em andamento
    in_progress = await repo.get_in_progress(data.bank_account_id)
    if in_progress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe conciliação em andamento para esta conta",
        )

    try:
        reconciliation = await repo.create(data.model_dump())
        logger.info(f"Conciliação criada: {reconciliation.id} por {current_user.get('email')}")
        return BankReconciliationResponse.model_validate(reconciliation)
    except Exception as e:
        logger.error(f"Erro ao criar conciliação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar conciliação",
        )


@router.get(
    "",
    response_model=list[BankReconciliationResponse],
    summary="Listar conciliações",
)
async def list_reconciliations(
    bank_account_id: UUID,
    reconciliation_status: ReconciliationStatus | None = Query(None),
    period_type: ReconciliationPeriodType | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    repo: BankReconciliationRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[BankReconciliationResponse]:
    """Lista conciliações com filtros."""
    reconciliations = await repo.list(bank_account_id=bank_account_id, skip=skip, limit=limit)
    return [BankReconciliationResponse.model_validate(r) for r in reconciliations]


@router.get(
    "/in-progress",
    response_model=BankReconciliationResponse | None,
    summary="Conciliação em andamento",
)
async def get_in_progress(
    bank_account_id: UUID,
    repo: BankReconciliationRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> BankReconciliationResponse | None:
    """Retorna conciliação em andamento para a conta."""
    reconciliation = await repo.get_in_progress(bank_account_id)
    if reconciliation:
        return BankReconciliationResponse.model_validate(reconciliation)
    return None


@router.get(
    "/{reconciliation_id}",
    response_model=BankReconciliationResponse,
    summary="Obter conciliação",
)
async def get_reconciliation(
    reconciliation_id: UUID,
    repo: BankReconciliationRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> BankReconciliationResponse:
    """Retorna conciliação pelo ID."""
    reconciliation = await repo.get_by_id(reconciliation_id)
    if not reconciliation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conciliação não encontrada",
        )
    return BankReconciliationResponse.model_validate(reconciliation)


@router.put(
    "/{reconciliation_id}",
    response_model=BankReconciliationResponse,
    summary="Atualizar conciliação",
)
async def update_reconciliation(
    reconciliation_id: UUID,
    data: BankReconciliationUpdate,
    repo: BankReconciliationRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> BankReconciliationResponse:
    """Atualiza conciliação bancária."""
    reconciliation = await repo.get_by_id(reconciliation_id)
    if not reconciliation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conciliação não encontrada",
        )

    if reconciliation.status == ReconciliationStatus.CONCLUIDA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível alterar conciliação concluída",
        )

    update_data = data.model_dump(exclude_unset=True)
    updated = await repo.update(reconciliation_id, update_data)
    logger.info(f"Conciliação atualizada: {reconciliation_id} por {current_user.get('email')}")
    return BankReconciliationResponse.model_validate(updated)


@router.delete(
    "/{reconciliation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir conciliação",
)
async def delete_reconciliation(
    reconciliation_id: UUID,
    repo: BankReconciliationRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> None:
    """Exclui conciliação bancária."""
    reconciliation = await repo.get_by_id(reconciliation_id)
    if not reconciliation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conciliação não encontrada",
        )

    if reconciliation.status == ReconciliationStatus.CONCLUIDA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir conciliação concluída",
        )

    await repo.delete(reconciliation_id)
    logger.info(f"Conciliação excluída: {reconciliation_id} por {current_user.get('email')}")


# ==================== OPERAÇÕES ====================


@router.post("/{reconciliation_id}/import-statement", summary="Importar extrato", status_code=201)
async def import_statement(
    reconciliation_id: UUID,
    data: StatementImport,
    repo: BankReconciliationRepository = Depends(get_repository),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Importa extrato bancário para conciliação."""
    reconciliation = await repo.get_by_id(reconciliation_id)
    if not reconciliation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conciliação não encontrada",
        )

    if reconciliation.status == ReconciliationStatus.CONCLUIDA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conciliação já foi concluída",
        )

    # Processa itens do extrato
    total_credits = Decimal("0")
    total_debits = Decimal("0")
    items_count = 0

    for item in data.items:
        if item.amount > 0:
            total_credits += item.amount
        else:
            total_debits += abs(item.amount)
        items_count += 1

    # Atualiza conciliação
    update_data = {
        "statement_balance": data.closing_balance,
        "statement_date": data.statement_date,
        "statement_source": data.source,
        "import_filename": data.filename,
        "status": ReconciliationStatus.EM_ANDAMENTO,
        "total_statement_items": items_count,
        "statement_credits": total_credits,
        "statement_debits": total_debits,
    }

    # Armazena itens do extrato no metadata
    statement_items = [
        {
            "date": str(item.date),
            "description": item.description,
            "amount": str(item.amount),
            "reference": item.reference,
            "reconciled": False,
        }
        for item in data.items
    ]
    update_data["metadata"] = {"statement_items": statement_items}

    await repo.update(reconciliation_id, update_data)
    await session.commit()

    logger.info(
        f"Extrato importado para conciliação {reconciliation_id}: {items_count} itens, por {current_user.get('email')}"
    )

    return {
        "success": True,
        "items_imported": items_count,
        "total_credits": total_credits,
        "total_debits": total_debits,
        "closing_balance": data.closing_balance,
    }


@router.post("/{reconciliation_id}/match", summary="Conciliar item", status_code=201)
async def match_item(
    reconciliation_id: UUID,
    data: ReconciliationItemMatch,
    repo: BankReconciliationRepository = Depends(get_repository),
    tx_repo: BankTransactionRepository = Depends(get_transaction_repository),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Vincula item do extrato com transação do sistema."""
    reconciliation = await repo.get_by_id(reconciliation_id)
    if not reconciliation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conciliação não encontrada",
        )

    # Verifica transação
    transaction = await tx_repo.get_by_id(data.transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada",
        )

    # Atualiza transação como conciliada
    await tx_repo.update(
        data.transaction_id,
        {
            "reconciliation_status": ReconciliationStatus.CONCILIADO,
            "reconciliation_id": reconciliation_id,
            "reconciled_at": date.today(),
            "statement_reference": data.statement_reference,
        },
    )

    # Atualiza progresso da conciliação
    reconciliation.items_reconciled = (reconciliation.items_reconciled or 0) + 1
    reconciliation.update_progress()

    await session.commit()

    logger.info(
        f"Item conciliado: transação {data.transaction_id} "
        f"com referência {data.statement_reference}, por {current_user.get('email')}"
    )

    return {
        "success": True,
        "transaction_id": str(data.transaction_id),
        "statement_reference": data.statement_reference,
        "progress": reconciliation.progress_percentage,
    }


@router.post("/{reconciliation_id}/adjustment", summary="Criar ajuste", status_code=201)
async def create_adjustment(
    reconciliation_id: UUID,
    data: ReconciliationAdjustment,
    repo: BankReconciliationRepository = Depends(get_repository),
    tx_repo: BankTransactionRepository = Depends(get_transaction_repository),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Cria lançamento de ajuste para diferença de conciliação."""
    reconciliation = await repo.get_by_id(reconciliation_id)
    if not reconciliation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conciliação não encontrada",
        )

    # Cria transação de ajuste
    tx = await tx_repo.create(
        {
            "bank_account_id": reconciliation.bank_account_id,
            "transaction_type": data.transaction_type,
            "category": TransactionCategory.AJUSTE,
            "amount": data.amount,
            "description": f"Ajuste de conciliação: {data.description}",
            "transaction_date": date.today(),
            "status": TransactionStatus.EFETIVADA,
            "reconciliation_status": ReconciliationStatus.CONCILIADO,
            "reconciliation_id": reconciliation_id,
            "reconciled_at": date.today(),
        }
    )

    # Atualiza saldo da conta
    local_account_repo = BankAccountRepository(session)
    account = await local_account_repo.get_by_id(reconciliation.bank_account_id)
    if account:
        if data.transaction_type == TransactionType.CREDITO:
            account.update_balance(data.amount)
        else:
            account.update_balance(-data.amount)

    # Atualiza total de ajustes na conciliação
    reconciliation.total_adjustments = (reconciliation.total_adjustments or Decimal("0")) + data.amount

    await session.commit()

    logger.info(
        f"Ajuste criado na conciliação {reconciliation_id}: "
        f"{data.amount} ({data.transaction_type.value}), por {current_user.get('email')}"
    )

    return {
        "success": True,
        "adjustment_transaction_id": str(tx.id),
        "amount": data.amount,
        "type": data.transaction_type.value,
    }


@router.post(
    "/{reconciliation_id}/complete",
    response_model=BankReconciliationResponse,
    summary="Finalizar conciliação",
    status_code=201,
)
async def complete_reconciliation(
    reconciliation_id: UUID,
    repo: BankReconciliationRepository = Depends(get_repository),
    account_repo: BankAccountRepository = Depends(get_account_repository),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> BankReconciliationResponse:
    """Finaliza conciliação bancária."""
    reconciliation = await repo.get_by_id(reconciliation_id)
    if not reconciliation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conciliação não encontrada",
        )

    if reconciliation.status == ReconciliationStatus.CONCLUIDA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conciliação já está concluída",
        )

    # Verifica saldo da conta vs extrato
    account = await account_repo.get_by_id(reconciliation.bank_account_id)
    if account and reconciliation.statement_balance:
        difference = account.current_balance - reconciliation.statement_balance
        if abs(difference) > Decimal("0.01"):
            # Há diferença não conciliada
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Diferença de R$ {difference:.2f} não conciliada. Crie ajustes ou concilie mais itens.",
            )

    # Atualiza status
    reconciliation.complete()

    # Atualiza saldo conciliado da conta
    if account and reconciliation.statement_balance:
        account.last_reconciled_balance = reconciliation.statement_balance
        account.last_reconciliation_date = date.today()

    await session.commit()

    logger.info(f"Conciliação finalizada: {reconciliation_id} por {current_user.get('email')}")
    return BankReconciliationResponse.model_validate(reconciliation)


@router.post(
    "/{reconciliation_id}/reopen",
    response_model=BankReconciliationResponse,
    summary="Reabrir conciliação",
    status_code=201,
)
async def reopen_reconciliation(
    reconciliation_id: UUID,
    reason: str = Query(..., min_length=5, max_length=500),
    repo: BankReconciliationRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> BankReconciliationResponse:
    """Reabre conciliação concluída."""
    reconciliation = await repo.get_by_id(reconciliation_id)
    if not reconciliation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conciliação não encontrada",
        )

    if reconciliation.status != ReconciliationStatus.CONCLUIDA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas conciliações concluídas podem ser reabertas",
        )

    updated = await repo.update(
        reconciliation_id,
        {
            "status": ReconciliationStatus.EM_ANDAMENTO,
            "completed_at": None,
            "notes": f"{reconciliation.notes or ''}\nReaberta: {reason}".strip(),
        },
    )

    logger.info(f"Conciliação reaberta: {reconciliation_id} por {current_user.get('email')}, motivo: {reason}")
    return BankReconciliationResponse.model_validate(updated)


# ==================== RELATÓRIOS ====================


@router.get(
    "/{reconciliation_id}/details",
    summary="Detalhes da conciliação",
)
async def get_reconciliation_details(
    reconciliation_id: UUID,
    repo: BankReconciliationRepository = Depends(get_repository),
    tx_repo: BankTransactionRepository = Depends(get_transaction_repository),
    account_repo: BankAccountRepository = Depends(get_account_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Retorna detalhes completos da conciliação."""
    reconciliation = await repo.get_by_id(reconciliation_id)
    if not reconciliation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conciliação não encontrada",
        )

    # Busca conta
    account = await account_repo.get_by_id(reconciliation.bank_account_id)

    # Busca transações do período
    transactions = await tx_repo.get_by_period(
        reconciliation.bank_account_id,
        reconciliation.period_start,
        reconciliation.period_end,
    )

    # Separa conciliadas e pendentes
    reconciled = [t for t in transactions if t.reconciliation_status == ReconciliationStatus.CONCILIADO]
    pending = [t for t in transactions if t.reconciliation_status == ReconciliationStatus.PENDENTE]

    # Calcula totais
    total_reconciled = sum(t.amount for t in reconciled)
    total_pending = sum(t.amount for t in pending)

    return {
        "reconciliation": BankReconciliationResponse.model_validate(reconciliation),
        "account": {
            "id": str(account.id) if account else None,
            "name": account.name if account else None,
            "current_balance": account.current_balance if account else None,
        },
        "summary": {
            "total_transactions": len(transactions),
            "reconciled_count": len(reconciled),
            "pending_count": len(pending),
            "total_reconciled_amount": total_reconciled,
            "total_pending_amount": total_pending,
            "difference": (
                (account.current_balance - reconciliation.statement_balance)
                if account and reconciliation.statement_balance
                else None
            ),
        },
        "pending_transactions": [
            {
                "id": str(t.id),
                "date": str(t.transaction_date),
                "description": t.description,
                "amount": t.amount,
                "type": t.transaction_type.value,
            }
            for t in pending[:50]  # Limita retorno
        ],
    }


@router.get(
    "/{reconciliation_id}/export",
    summary="Exportar conciliação",
)
async def export_reconciliation(
    reconciliation_id: UUID,
    export_format: str = Query("json", enum=["json", "csv"]),
    repo: BankReconciliationRepository = Depends(get_repository),
    tx_repo: BankTransactionRepository = Depends(get_transaction_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Exporta dados da conciliação."""
    reconciliation = await repo.get_by_id(reconciliation_id)
    if not reconciliation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conciliação não encontrada",
        )

    transactions = await tx_repo.get_by_period(
        reconciliation.bank_account_id,
        reconciliation.period_start,
        reconciliation.period_end,
    )

    if export_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Data", "Descrição", "Tipo", "Valor", "Status Conciliação", "Referência"])

        for tx in transactions:
            writer.writerow(
                [
                    str(tx.transaction_date),
                    tx.description,
                    tx.transaction_type.value,
                    str(tx.amount),
                    tx.reconciliation_status.value,
                    tx.statement_reference or "",
                ]
            )

        return {
            "format": "csv",
            "content": output.getvalue(),
            "filename": f"conciliacao_{reconciliation_id}.csv",
        }

    # JSON
    return {
        "format": "json",
        "reconciliation": BankReconciliationResponse.model_validate(reconciliation).model_dump(),
        "transactions": [
            {
                "id": str(tx.id),
                "date": str(tx.transaction_date),
                "description": tx.description,
                "type": tx.transaction_type.value,
                "amount": str(tx.amount),
                "reconciliation_status": tx.reconciliation_status.value,
                "reference": tx.statement_reference,
            }
            for tx in transactions
        ],
    }
