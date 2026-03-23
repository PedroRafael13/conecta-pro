"""
Controller de Propostas - Licitacoes
====================================
"""

import logging
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from modules.bidding.schemas.proposal import (
    ProposalBDIResponse,
    ProposalCalculateBDI,
    ProposalCreate,
    ProposalLanceCreate,
    ProposalListResponse,
    ProposalResponse,
    ProposalUpdate,
)
from modules.bidding.services.proposal_service import ProposalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/proposals", tags=["Licitacoes - Propostas"])


@router.get("", response_model=ProposalListResponse)
async def list_proposals(
    tender_id: UUID | None = None,
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lista propostas com filtros."""
    service = ProposalService(db)
    return await service.list(tender_id, status, page, size)


@router.get("/estatisticas")
async def get_estatisticas(db: Session = Depends(get_db)):
    """Retorna estatisticas de propostas."""
    service = ProposalService(db)
    return await service.get_estatisticas()


@router.get("/vencedoras")
async def list_vencedoras(db: Session = Depends(get_db)):
    """Lista propostas vencedoras."""
    service = ProposalService(db)
    return await service.get_vencedoras()


@router.get("/tender/{tender_id}")
async def list_by_tender(tender_id: UUID, db: Session = Depends(get_db)):
    """Lista propostas de um edital especifico."""
    service = ProposalService(db)
    return await service.get_by_tender(tender_id)


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(proposal_id: UUID, db: Session = Depends(get_db)):
    """Busca proposta por ID."""
    service = ProposalService(db)
    proposal = await service.get(proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposta nao encontrada")
    return proposal


@router.post("", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
async def create_proposal(data: ProposalCreate, db: Session = Depends(get_db)):
    """Cria nova proposta."""
    service = ProposalService(db)
    return await service.create(data)


@router.put("/{proposal_id}", response_model=ProposalResponse)
async def update_proposal(proposal_id: UUID, data: ProposalUpdate, db: Session = Depends(get_db)):
    """Atualiza proposta."""
    service = ProposalService(db)
    proposal = await service.update(proposal_id, data)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proposta nao encontrada ou nao pode ser editada"
        )
    return proposal


@router.delete("/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_proposal(proposal_id: UUID, db: Session = Depends(get_db)):
    """Remove proposta."""
    service = ProposalService(db)
    if not await service.delete(proposal_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposta nao encontrada")


@router.post("/{proposal_id}/pronta", response_model=ProposalResponse)
async def marcar_pronta(proposal_id: UUID, db: Session = Depends(get_db)):
    """Marca proposta como pronta para envio."""
    service = ProposalService(db)
    try:
        proposal = await service.marcar_pronta(proposal_id)
        if not proposal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposta nao encontrada")
        return proposal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{proposal_id}/enviar", response_model=ProposalResponse)
async def enviar_proposta(proposal_id: UUID, db: Session = Depends(get_db)):
    """Envia proposta."""
    service = ProposalService(db)
    proposal = await service.enviar(proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Proposta nao pode ser enviada (verifique status)"
        )
    return proposal


@router.post("/{proposal_id}/resultado", response_model=ProposalResponse)
async def registrar_resultado(
    proposal_id: UUID,
    vencedora: bool,
    posicao: int | None = None,
    valor_final: float | None = None,
    db: Session = Depends(get_db),
):
    """Registra resultado da proposta."""
    service = ProposalService(db)
    valor = Decimal(str(valor_final)) if valor_final else None
    proposal = await service.registrar_resultado(proposal_id, vencedora, posicao, valor)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposta nao encontrada")
    return proposal


@router.post("/{proposal_id}/lance", response_model=ProposalResponse)
async def registrar_lance(proposal_id: UUID, data: ProposalLanceCreate, db: Session = Depends(get_db)):
    """Registra lance em pregao."""
    service = ProposalService(db)
    proposal = await service.registrar_lance(proposal_id, data.valor)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposta nao encontrada")
    return proposal


@router.post("/calcular-bdi", response_model=ProposalBDIResponse)
async def calcular_bdi(data: ProposalCalculateBDI, db: Session = Depends(get_db)):
    """Calcula BDI da proposta."""
    service = ProposalService(db)
    return await service.calcular_bdi(data)
