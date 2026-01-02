"""Controller para clientes/devedores do contas a receber."""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_session
from modules.financial.models.customer import CustomerStatus, CustomerType
from modules.financial.repositories.receivable_repository import CustomerRepository
from modules.financial.schemas.receivable import (
    CustomerCreate,
    CustomerFilter,
    CustomerResponse,
    CustomerUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["Clientes (Contas a Receber)"])


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> CustomerRepository:
    """Retorna instancia do repository."""
    return CustomerRepository(session)


@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar cliente",
)
async def create_customer(
    data: CustomerCreate,
    repo: CustomerRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> CustomerResponse:
    """Cria um novo cliente/devedor."""
    try:
        customer = await repo.create(data, UUID(current_user["id"]))
        return CustomerResponse.model_validate(customer)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar cliente: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar cliente",
        )


@router.get(
    "/",
    response_model=List[CustomerResponse],
    summary="Listar clientes",
)
async def list_customers(
    condominio_id: UUID,
    search: Optional[str] = Query(None, description="Busca no nome ou documento"),
    customer_type: Optional[str] = Query(None, alias="type", description="Tipo"),
    status_filter: Optional[str] = Query(None, alias="status", description="Status"),
    has_debt: Optional[bool] = Query(None, description="Com divida ativa"),
    is_overdue: Optional[bool] = Query(None, description="Com divida vencida"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    repo: CustomerRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
):
    """Lista clientes com filtros."""
    filters = CustomerFilter(
        search=search,
        customer_type=CustomerType(customer_type) if customer_type else None,
        status=CustomerStatus(status_filter) if status_filter else None,
        has_debt=has_debt,
        is_overdue=is_overdue,
    )

    customers = await repo.list(condominio_id, filters, skip, limit)
    return [CustomerResponse.model_validate(c) for c in customers]


@router.get(
    "/debtors",
    response_model=List[CustomerResponse],
    summary="Listar devedores",
)
async def list_debtors(
    condominio_id: UUID,
    only_overdue: bool = Query(False, description="Apenas com divida vencida"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    repo: CustomerRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
):
    """Lista clientes com divida ativa."""
    customers = await repo.get_debtors(condominio_id, only_overdue, skip, limit)
    return [CustomerResponse.model_validate(c) for c in customers]


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Buscar cliente",
)
async def get_customer(
    customer_id: UUID,
    repo: CustomerRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> CustomerResponse:
    """Busca cliente por ID."""
    customer = await repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado",
        )
    return CustomerResponse.model_validate(customer)


@router.get(
    "/document/{document}",
    response_model=CustomerResponse,
    summary="Buscar cliente por documento",
)
async def get_customer_by_document(
    document: str,
    repo: CustomerRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> CustomerResponse:
    """Busca cliente por CPF/CNPJ."""
    customer = await repo.get_by_document(document)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado",
        )
    return CustomerResponse.model_validate(customer)


@router.get(
    "/morador/{morador_id}",
    response_model=CustomerResponse,
    summary="Buscar cliente por morador",
)
async def get_customer_by_morador(
    morador_id: UUID,
    repo: CustomerRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> CustomerResponse:
    """Busca cliente pelo ID do morador."""
    customer = await repo.get_by_morador(morador_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado",
        )
    return CustomerResponse.model_validate(customer)


@router.get(
    "/unidade/{unidade_id}",
    response_model=List[CustomerResponse],
    summary="Buscar clientes por unidade",
)
async def get_customers_by_unidade(
    unidade_id: UUID,
    repo: CustomerRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
):
    """Busca clientes de uma unidade."""
    customers = await repo.get_by_unidade(unidade_id)
    return [CustomerResponse.model_validate(c) for c in customers]


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Atualizar cliente",
)
async def update_customer(
    customer_id: UUID,
    data: CustomerUpdate,
    repo: CustomerRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> CustomerResponse:
    """Atualiza um cliente."""
    try:
        customer = await repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente nao encontrado",
            )

        customer = await repo.update(customer, data)
        return CustomerResponse.model_validate(customer)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir cliente",
)
async def delete_customer(
    customer_id: UUID,
    repo: CustomerRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
):
    """Exclui um cliente (soft delete)."""
    customer = await repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado",
        )

    if customer.total_debt > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cliente com divida ativa nao pode ser excluido",
        )

    await repo.delete(customer)


@router.post(
    "/{customer_id}/block",
    response_model=CustomerResponse,
    summary="Bloquear cliente",
)
async def block_customer(
    customer_id: UUID,
    reason: str = Query(..., min_length=5, description="Motivo do bloqueio"),
    repo: CustomerRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> CustomerResponse:
    """Bloqueia um cliente."""
    customer = await repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado",
        )

    customer.block(reason)
    await repo.session.commit()
    return CustomerResponse.model_validate(customer)


@router.post(
    "/{customer_id}/unblock",
    response_model=CustomerResponse,
    summary="Desbloquear cliente",
)
async def unblock_customer(
    customer_id: UUID,
    repo: CustomerRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> CustomerResponse:
    """Desbloqueia um cliente."""
    customer = await repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado",
        )

    customer.unblock()
    await repo.session.commit()
    return CustomerResponse.model_validate(customer)


@router.get(
    "/{customer_id}/debt-summary",
    summary="Resumo de divida do cliente",
)
async def get_customer_debt_summary(
    customer_id: UUID,
    repo: CustomerRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
):
    """Retorna resumo completo de divida do cliente."""
    customer = await repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado",
        )

    return {
        "customer_id": str(customer_id),
        "customer_name": customer.name,
        "total_debt": float(customer.total_debt),
        "overdue_debt": float(customer.overdue_debt),
        "status": customer.status,
        "is_blocked": customer.status == CustomerStatus.BLOQUEADO.value,
        "block_reason": (
            customer.notes if customer.status == CustomerStatus.BLOQUEADO.value else None
        ),
    }
