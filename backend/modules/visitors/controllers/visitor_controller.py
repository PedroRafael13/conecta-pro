"""Controller para Visitor."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from modules.visitors.models.visitor import VisitorStatus, VisitorType
from modules.visitors.schemas.visitor import (
    VisitorBlock,
    VisitorCreate,
    VisitorFilter,
    VisitorListResponse,
    VisitorResponse,
    VisitorSearch,
    VisitorStats,
    VisitorUpdate,
)
from modules.visitors.services.visitor_service import VisitorService
from modules.visitors.services.visitor_ai_service import VisitorAIService

router = APIRouter(prefix="/visitors", tags=["Visitors"])


# ========== CRUD ==========


@router.post("/", response_model=VisitorResponse, status_code=status.HTTP_201_CREATED)
async def create_visitor(
    data: VisitorCreate,
    session: AsyncSession = Depends(get_session),
):
    """Cria um novo visitante."""
    service = VisitorService(session)
    return await service.create(data)


@router.get("/", response_model=VisitorListResponse)
async def list_visitors(
    name: Optional[str] = None,
    visitor_type: Optional[VisitorType] = None,
    visitor_status: Optional[VisitorStatus] = Query(None, alias="status"),
    document_number: Optional[str] = None,
    cpf: Optional[str] = None,
    phone: Optional[str] = None,
    company_name: Optional[str] = None,
    vehicle_plate: Optional[str] = None,
    condominium_id: Optional[str] = None,
    is_blocked: Optional[bool] = None,
    has_vehicle: Optional[bool] = None,
    has_biometric: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_by: str = "created_at",
    order_desc: bool = True,
    session: AsyncSession = Depends(get_session),
):
    """Lista visitantes com filtros."""
    filters = VisitorFilter(
        name=name,
        visitor_type=visitor_type,
        status=visitor_status,
        document_number=document_number,
        cpf=cpf,
        phone=phone,
        company_name=company_name,
        vehicle_plate=vehicle_plate,
        condominium_id=condominium_id,
        is_blocked=is_blocked,
        has_vehicle=has_vehicle,
        has_biometric=has_biometric,
    )
    service = VisitorService(session)
    return await service.list(filters, page, page_size, order_by, order_desc)


@router.get("/search", response_model=list[VisitorResponse])
async def search_visitors(
    query: str = Query(..., min_length=2),
    condominium_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
):
    """Busca visitantes por termo."""
    service = VisitorService(session)
    return await service.search(query, condominium_id, limit)


@router.get("/stats", response_model=VisitorStats)
async def get_visitor_stats(
    condominium_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    session: AsyncSession = Depends(get_session),
):
    """Retorna estatísticas de visitantes."""
    service = VisitorService(session)
    return await service.get_stats(condominium_id, date_from)


@router.get("/blocked", response_model=VisitorListResponse)
async def get_blocked_visitors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Lista visitantes bloqueados."""
    service = VisitorService(session)
    return await service.get_blocked(page, page_size)


@router.get("/vip", response_model=VisitorListResponse)
async def get_vip_visitors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Lista visitantes VIP."""
    service = VisitorService(session)
    return await service.get_vip(page, page_size)


@router.get("/frequent", response_model=VisitorListResponse)
async def get_frequent_visitors(
    min_visits: int = Query(10, ge=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Lista visitantes frequentes."""
    service = VisitorService(session)
    return await service.get_frequent(min_visits, page, page_size)


@router.get("/by-condominium/{condominium_id}", response_model=VisitorListResponse)
async def get_visitors_by_condominium(
    condominium_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Lista visitantes de um condomínio."""
    service = VisitorService(session)
    return await service.get_by_condominium(condominium_id, page, page_size)


@router.get("/by-cpf/{cpf}", response_model=VisitorResponse)
async def get_visitor_by_cpf(
    cpf: str,
    session: AsyncSession = Depends(get_session),
):
    """Busca visitante por CPF."""
    service = VisitorService(session)
    visitor = await service.get_by_cpf(cpf)
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitante não encontrado",
        )
    return visitor


@router.get("/by-plate/{plate}", response_model=VisitorResponse)
async def get_visitor_by_plate(
    plate: str,
    session: AsyncSession = Depends(get_session),
):
    """Busca visitante por placa."""
    service = VisitorService(session)
    visitor = await service.get_by_plate(plate)
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitante não encontrado",
        )
    return visitor


@router.get("/by-code/{code}", response_model=VisitorResponse)
async def get_visitor_by_code(
    code: str,
    session: AsyncSession = Depends(get_session),
):
    """Busca visitante por código."""
    service = VisitorService(session)
    visitor = await service.get_by_code(code)
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitante não encontrado",
        )
    return visitor


@router.get("/{visitor_id}", response_model=VisitorResponse)
async def get_visitor(
    visitor_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Busca visitante por ID."""
    service = VisitorService(session)
    visitor = await service.get_by_id(visitor_id)
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitante não encontrado",
        )
    return visitor


@router.put("/{visitor_id}", response_model=VisitorResponse)
async def update_visitor(
    visitor_id: UUID,
    data: VisitorUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Atualiza um visitante."""
    service = VisitorService(session)
    visitor = await service.update(visitor_id, data)
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitante não encontrado",
        )
    return visitor


@router.delete("/{visitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_visitor(
    visitor_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Deleta um visitante."""
    service = VisitorService(session)
    if not await service.delete(visitor_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitante não encontrado",
        )


# ========== Ações ==========


@router.post("/{visitor_id}/block", response_model=VisitorResponse)
async def block_visitor(
    visitor_id: UUID,
    data: VisitorBlock,
    session: AsyncSession = Depends(get_session),
):
    """Bloqueia um visitante."""
    service = VisitorService(session)
    visitor = await service.block(visitor_id, data)
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitante não encontrado",
        )
    return visitor


@router.post("/{visitor_id}/unblock", response_model=VisitorResponse)
async def unblock_visitor(
    visitor_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Desbloqueia um visitante."""
    service = VisitorService(session)
    visitor = await service.unblock(visitor_id)
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitante não encontrado",
        )
    return visitor


@router.post("/{visitor_id}/set-vip", response_model=VisitorResponse)
async def set_visitor_vip(
    visitor_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Define visitante como VIP."""
    service = VisitorService(session)
    visitor = await service.set_vip(visitor_id)
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitante não encontrado",
        )
    return visitor


@router.post("/{visitor_id}/generate-qr", response_model=dict)
async def generate_qr_code(
    visitor_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Gera QR Code para visitante."""
    service = VisitorService(session)
    qr_code = await service.generate_qr_code(visitor_id)
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitante não encontrado",
        )
    return {"qr_code": qr_code}


# ========== IA ==========


@router.get("/{visitor_id}/pattern", response_model=dict)
async def analyze_visitor_pattern(
    visitor_id: UUID,
    days: int = Query(90, ge=7, le=365),
    session: AsyncSession = Depends(get_session),
):
    """Analisa padrões de visita de um visitante."""
    service = VisitorAIService(session)
    return await service.analyze_visitor_pattern(visitor_id, days)


@router.get("/{visitor_id}/suggest-authorization/{condominium_id}", response_model=dict)
async def suggest_authorization_type(
    visitor_id: UUID,
    condominium_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Sugere tipo de autorização para visitante."""
    service = VisitorAIService(session)
    return await service.suggest_authorization_type(visitor_id, condominium_id)


@router.get("/ai/trends/{condominium_id}", response_model=dict)
async def analyze_condominium_trends(
    condominium_id: str,
    days: int = Query(30, ge=7, le=365),
    session: AsyncSession = Depends(get_session),
):
    """Analisa tendências de visitantes do condomínio."""
    service = VisitorAIService(session)
    return await service.analyze_condominium_trends(condominium_id, days)


@router.get("/ai/anomalies/{condominium_id}", response_model=list[dict])
async def detect_anomalies(
    condominium_id: str,
    hours: int = Query(24, ge=1, le=168),
    session: AsyncSession = Depends(get_session),
):
    """Detecta anomalias nos acessos."""
    service = VisitorAIService(session)
    return await service.detect_anomalies(condominium_id, hours)


@router.get("/ai/peak-hours/{condominium_id}", response_model=dict)
async def get_peak_hours(
    condominium_id: str,
    days: int = Query(30, ge=7, le=365),
    session: AsyncSession = Depends(get_session),
):
    """Retorna horários de pico."""
    service = VisitorAIService(session)
    return await service.get_peak_hours(condominium_id, days)
