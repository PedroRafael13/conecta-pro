"""Controller para períodos de folha de pagamento."""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth.dependencies import get_current_user, require_permissions
from modules.hr.payroll_integration.models import PeriodType, PeriodStatus
from modules.hr.payroll_integration.schemas import (
    PayrollPeriodCreate,
    PayrollPeriodUpdate,
    PayrollPeriodResponse,
    PayrollPeriodListResponse,
    PeriodCalculationRequest,
    PeriodCalculationResponse,
)
from modules.hr.payroll_integration.services import PayrollCalculationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/periods", tags=["Payroll Periods"])


@router.post(
    "/",
    response_model=PayrollPeriodResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar período de folha",
)
async def create_period(
    data: PayrollPeriodCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> PayrollPeriodResponse:
    """Cria um novo período de folha de pagamento."""
    try:
        service = PayrollCalculationService(db)
        period = await service.create_period(
            data=data,
            condominio_id=current_user["condominio_id"],
            user_id=current_user["id"],
        )
        logger.info("Período criado: %s por %s", period.code, current_user["email"])
        return PayrollPeriodResponse.model_validate(period)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Erro ao criar período: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar período",
        )


@router.get(
    "/",
    response_model=PayrollPeriodListResponse,
    summary="Listar períodos",
)
async def list_periods(
    year: Optional[int] = Query(None, description="Filtrar por ano"),
    period_type: Optional[PeriodType] = Query(None, description="Tipo de período"),
    period_status: Optional[PeriodStatus] = Query(None, description="Status"),
    page: int = Query(1, ge=1, description="Página"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> PayrollPeriodListResponse:
    """Lista períodos de folha com filtros."""
    try:
        service = PayrollCalculationService(db)
        periods, total = await service.list_periods(
            condominio_id=current_user["condominio_id"],
            year=year,
            period_type=period_type,
            status=period_status,
            page=page,
            page_size=page_size,
        )
        return PayrollPeriodListResponse(
            items=[PayrollPeriodResponse.model_validate(p) for p in periods],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )
    except Exception as e:
        logger.error("Erro ao listar períodos: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar períodos",
        )


@router.get(
    "/current",
    response_model=PayrollPeriodResponse,
    summary="Período atual",
)
async def get_current_period(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> PayrollPeriodResponse:
    """Retorna o período de folha atual (aberto ou mais recente)."""
    try:
        service = PayrollCalculationService(db)
        period = await service.get_current_period(current_user["condominio_id"])
        if not period:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum período encontrado",
            )
        return PayrollPeriodResponse.model_validate(period)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao buscar período atual: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar período",
        )


@router.get(
    "/{period_id}",
    response_model=PayrollPeriodResponse,
    summary="Buscar período",
)
async def get_period(
    period_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> PayrollPeriodResponse:
    """Busca período por ID."""
    try:
        service = PayrollCalculationService(db)
        period = await service.get_period(period_id)
        if not period:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Período não encontrado",
            )
        return PayrollPeriodResponse.model_validate(period)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao buscar período %s: %s", period_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar período",
        )


@router.put(
    "/{period_id}",
    response_model=PayrollPeriodResponse,
    summary="Atualizar período",
)
async def update_period(
    period_id: UUID,
    data: PayrollPeriodUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> PayrollPeriodResponse:
    """Atualiza período de folha."""
    try:
        service = PayrollCalculationService(db)
        period = await service.update_period(period_id, data)
        if not period:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Período não encontrado",
            )
        logger.info("Período atualizado: %s por %s", period.code, current_user["email"])
        return PayrollPeriodResponse.model_validate(period)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao atualizar período %s: %s", period_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar período",
        )


@router.post(
    "/{period_id}/calculate",
    response_model=PeriodCalculationResponse,
    summary="Calcular folha",
)
async def calculate_period(
    period_id: UUID,
    request: PeriodCalculationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> PeriodCalculationResponse:
    """Executa cálculo da folha de pagamento do período."""
    try:
        service = PayrollCalculationService(db)
        result = await service.calculate_period(
            period_id=period_id,
            condominio_id=current_user["condominio_id"],
            request=request,
            user_id=current_user["id"],
        )
        logger.info(
            "Folha calculada: período %s, %d funcionários por %s",
            period_id,
            result.employees_processed,
            current_user["email"],
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Erro ao calcular período %s: %s", period_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao calcular folha",
        )


@router.post(
    "/{period_id}/approve",
    response_model=PayrollPeriodResponse,
    summary="Aprovar período",
)
async def approve_period(
    period_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_permissions(["payroll:approve"])),
) -> PayrollPeriodResponse:
    """Aprova período de folha para fechamento."""
    try:
        service = PayrollCalculationService(db)
        period = await service.approve_period(
            period_id=period_id,
            user_id=current_user["id"],
        )
        logger.info("Período aprovado: %s por %s", period.code, current_user["email"])
        return PayrollPeriodResponse.model_validate(period)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Erro ao aprovar período %s: %s", period_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao aprovar período",
        )


@router.post(
    "/{period_id}/close",
    response_model=PayrollPeriodResponse,
    summary="Fechar período",
)
async def close_period(
    period_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_permissions(["payroll:close"])),
) -> PayrollPeriodResponse:
    """Fecha período de folha (não permite mais alterações)."""
    try:
        service = PayrollCalculationService(db)
        period = await service.close_period(
            period_id=period_id,
            user_id=current_user["id"],
        )
        logger.info("Período fechado: %s por %s", period.code, current_user["email"])
        return PayrollPeriodResponse.model_validate(period)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Erro ao fechar período %s: %s", period_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao fechar período",
        )


@router.post(
    "/{period_id}/reopen",
    response_model=PayrollPeriodResponse,
    summary="Reabrir período",
)
async def reopen_period(
    period_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_permissions(["payroll:reopen"])),
) -> PayrollPeriodResponse:
    """Reabre período fechado para correções."""
    try:
        service = PayrollCalculationService(db)
        period = await service.reopen_period(
            period_id=period_id,
            user_id=current_user["id"],
        )
        logger.info("Período reaberto: %s por %s", period.code, current_user["email"])
        return PayrollPeriodResponse.model_validate(period)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Erro ao reabrir período %s: %s", period_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao reabrir período",
        )


@router.delete(
    "/{period_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir período",
)
async def delete_period(
    period_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_permissions(["payroll:delete"])),
) -> None:
    """Exclui período de folha (apenas rascunhos)."""
    try:
        service = PayrollCalculationService(db)
        deleted = await service.delete_period(period_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Período não encontrado",
            )
        logger.info("Período excluído: %s por %s", period_id, current_user["email"])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao excluir período %s: %s", period_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao excluir período",
        )
