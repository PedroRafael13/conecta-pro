"""
Controller de Contratos Publicos - Licitacoes
=============================================
"""

import logging
from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.bidding.schemas.contract import (
    ContractAddendumCreate,
    ContractListResponse,
    ContractReadjustRequest,
    ContractReadjustResponse,
    PublicContractCreate,
    PublicContractResponse,
    PublicContractUpdate,
)
from modules.bidding.services.contract_service import ContractService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contracts", tags=["Licitacoes - Contratos"])


@router.get("", response_model=ContractListResponse)
async def list_contracts(
    current_user: CurrentActiveUser,
    orgao_cnpj: str | None = None,
    status: str | None = None,
    vigente: bool | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lista contratos com filtros."""
    service = ContractService(db)
    return await service.list(orgao_cnpj, status, vigente, page, size)


@router.get("/dashboard")
async def get_dashboard(current_user: CurrentActiveUser, db: Session = Depends(get_db)):
    """Retorna dados para dashboard de contratos."""
    service = ContractService(db)
    return await service.get_dashboard()


@router.get("/vigentes", response_model=list[PublicContractResponse])
async def list_vigentes(current_user: CurrentActiveUser, db: Session = Depends(get_db)):
    """Lista contratos vigentes."""
    service = ContractService(db)
    return await service.get_vigentes()


@router.get("/vencendo", response_model=list[PublicContractResponse])
async def list_vencendo(
    current_user: CurrentActiveUser, dias: int = Query(default=90, ge=1, le=365), db: Session = Depends(get_db)
):
    """Lista contratos vencendo nos proximos X dias."""
    service = ContractService(db)
    return await service.get_expiring(dias)


@router.get("/{contract_id}", response_model=PublicContractResponse)
async def get_contract(contract_id: UUID, current_user: CurrentActiveUser, db: Session = Depends(get_db)):
    """Busca contrato por ID."""
    service = ContractService(db)
    contract = await service.get(contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato nao encontrado")
    return contract


@router.post("", response_model=PublicContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(data: PublicContractCreate, current_user: CurrentActiveUser, db: Session = Depends(get_db)):
    """Cria novo contrato."""
    service = ContractService(db)
    try:
        return await service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{contract_id}", response_model=PublicContractResponse)
async def update_contract(
    contract_id: UUID, data: PublicContractUpdate, current_user: CurrentActiveUser, db: Session = Depends(get_db)
):
    """Atualiza contrato."""
    service = ContractService(db)
    contract = await service.update(contract_id, data)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato nao encontrado")
    return contract


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(contract_id: UUID, current_user: CurrentActiveUser, db: Session = Depends(get_db)):
    """Remove contrato."""
    service = ContractService(db)
    if not await service.delete(contract_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato nao encontrado")


@router.post("/{contract_id}/aditivo", response_model=PublicContractResponse, status_code=201)
async def add_aditivo(
    contract_id: UUID, data: ContractAddendumCreate, current_user: CurrentActiveUser, db: Session = Depends(get_db)
):
    """Adiciona aditivo ao contrato."""
    service = ContractService(db)
    contract = await service.add_addendum(contract_id, data)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato nao encontrado")
    return contract


@router.post("/{contract_id}/reajuste/calcular", response_model=ContractReadjustResponse)
async def calcular_reajuste(
    contract_id: UUID, data: ContractReadjustRequest, current_user: CurrentActiveUser, db: Session = Depends(get_db)
):
    """Calcula reajuste do contrato."""
    service = ContractService(db)
    result = await service.calcular_reajuste(contract_id, data)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato nao encontrado")
    return result


@router.post("/{contract_id}/reajuste/aplicar", response_model=PublicContractResponse)
async def aplicar_reajuste(
    current_user: CurrentActiveUser,
    contract_id: UUID,
    percentual: float,
    data_aplicacao: date | None = None,
    db: Session = Depends(get_db),
):
    """Aplica reajuste ao contrato."""
    service = ContractService(db)
    contract = await service.aplicar_reajuste(contract_id, Decimal(str(percentual)), data_aplicacao)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato nao encontrado")
    return contract


# Medicoes
@router.get("/{contract_id}/medicoes")
async def list_medicoes(contract_id: UUID, current_user: CurrentActiveUser, db: Session = Depends(get_db)):
    """Lista medicoes de um contrato."""
    service = ContractService(db)
    return await service.get_measurements(contract_id)


@router.post("/{contract_id}/medicoes", status_code=201)
async def add_medicao(
    contract_id: UUID,
    competencia: str,
    periodo_inicio: date,
    periodo_fim: date,
    valor_bruto: float,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """Adiciona medicao ao contrato."""
    service = ContractService(db)
    return await service.add_measurement(
        contract_id, competencia, periodo_inicio, periodo_fim, Decimal(str(valor_bruto))
    )


@router.post("/medicoes/{measurement_id}/aprovar")
async def aprovar_medicao(
    measurement_id: UUID,
    aprovador: str,
    current_user: CurrentActiveUser,
    cargo: str | None = None,
    observacoes: str | None = None,
    db: Session = Depends(get_db),
):
    """Aprova uma medicao."""
    service = ContractService(db)
    result = await service.approve_measurement(measurement_id, aprovador, cargo, observacoes)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicao nao encontrada")
    return result
