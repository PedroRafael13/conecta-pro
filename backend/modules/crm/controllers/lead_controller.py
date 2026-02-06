"""
Controller (endpoints) para Lead.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from core.logging import logger
from modules.crm.models.lead import LeadSource, LeadStatus
from modules.crm.repositories.lead_repository import LeadRepository
from modules.crm.schemas.lead import (
    LeadCreate,
    LeadFilter,
    LeadListResponse,
    LeadResponse,
    LeadStats,
    LeadStatusUpdate,
    LeadUpdate,
)
from modules.crm.services.lead_service import lead_service

router = APIRouter(prefix="/leads", tags=["CRM - Leads"])


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    data: LeadCreate,
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """
    Cria um novo lead.

    Requer autenticação. O score é calculado automaticamente.
    """
    repo = LeadRepository(db)

    # Verificar se email já existe
    existing = await repo.get_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um lead com este email",
        )

    lead = await repo.create(data)
    logger.info(f"Lead criado por {current_user.email}: {lead.id}")

    return LeadResponse.model_validate(lead)


@router.get("", response_model=LeadListResponse)
async def list_leads(  # pylint: disable=too-many-locals
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Página atual"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    status_filter: Optional[LeadStatus] = Query(None, alias="status"),
    source: Optional[LeadSource] = None,
    assigned_to_id: Optional[str] = None,
    min_score: Optional[int] = Query(None, ge=0, le=100),
    max_score: Optional[int] = Query(None, ge=0, le=100),
    is_hot: Optional[bool] = None,
    company: Optional[str] = None,
    search: Optional[str] = None,
) -> LeadListResponse:
    """
    Lista leads com filtros e paginação.

    Suporta busca por nome, email ou empresa.
    """
    repo = LeadRepository(db)

    filters = LeadFilter(
        status=status_filter,
        source=source,
        assigned_to_id=assigned_to_id,
        min_score=min_score,
        max_score=max_score,
        is_hot=is_hot,
        company=company,
        search=search,
    )

    leads, total = await repo.list(filters=filters, page=page, page_size=page_size)

    total_pages = (total + page_size - 1) // page_size

    return LeadListResponse(
        items=[LeadResponse.model_validate(lead) for lead in leads],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=LeadStats)
async def get_lead_stats(
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
    assigned_to_id: Optional[str] = None,
) -> LeadStats:
    """
    Obtém estatísticas de leads.

    Pode filtrar por responsável.
    """
    repo = LeadRepository(db)
    return await repo.get_stats(assigned_to_id=assigned_to_id)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """
    Obtém um lead pelo ID.
    """
    repo = LeadRepository(db)
    lead = await repo.get_by_id(lead_id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead não encontrado",
        )

    return LeadResponse.model_validate(lead)


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    data: LeadUpdate,
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """
    Atualiza um lead.

    Apenas campos fornecidos são atualizados.
    O score é recalculado se necessário.
    """
    repo = LeadRepository(db)
    lead = await repo.update(lead_id, data)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead não encontrado",
        )

    logger.info(f"Lead atualizado por {current_user.email}: {lead.id}")
    return LeadResponse.model_validate(lead)


@router.patch("/{lead_id}/status", response_model=LeadResponse)
async def update_lead_status(
    lead_id: str,
    data: LeadStatusUpdate,
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """
    Atualiza o status de um lead.

    Registra a mudança nas notas e recalcula o score.
    """
    repo = LeadRepository(db)
    lead = await repo.update_status(lead_id, data.status, data.notes)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead não encontrado",
        )

    logger.info(
        f"Lead {lead.id} status alterado para {data.status.value} por {current_user.email}"
    )
    return LeadResponse.model_validate(lead)


@router.post("/{lead_id}/recalculate-score", response_model=LeadResponse)
async def recalculate_lead_score(
    lead_id: str,
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """
    Recalcula o score de um lead.

    Útil após atualizações manuais ou mudanças nos critérios.
    """
    repo = LeadRepository(db)
    lead = await repo.update_score(lead_id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead não encontrado",
        )

    return LeadResponse.model_validate(lead)


@router.get("/{lead_id}/recommended-action")
async def get_recommended_action(
    lead_id: str,
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Obtém ação recomendada para um lead.

    Baseado no score, status e histórico.
    """
    repo = LeadRepository(db)
    lead = await repo.get_by_id(lead_id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead não encontrado",
        )

    action = lead_service.get_recommended_action(lead)
    next_contact = lead_service.get_next_contact_date(lead)

    return {
        "lead_id": lead.id,
        "score": lead.score,
        "status": lead.status,
        "recommended_action": action,
        "next_contact_date": next_contact.isoformat() if next_contact else None,
    }


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: str,
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Remove um lead (soft delete).
    """
    repo = LeadRepository(db)
    deleted = await repo.delete(lead_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead não encontrado",
        )

    logger.info(f"Lead deletado por {current_user.email}: {lead_id}")
