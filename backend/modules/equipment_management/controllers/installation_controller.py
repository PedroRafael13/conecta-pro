"""Controller para EquipmentInstallation."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.equipment_management.schemas.installation import (
    InstallationCreate,
    InstallationFilter,
    InstallationListResponse,
    InstallationResponse,
    InstallationUpdate,
)
from modules.equipment_management.services.installation_service import (
    InstallationService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/installations", tags=["Installations"])


async def get_service(db: AsyncSession = Depends(get_db)) -> InstallationService:
    """Dependency para obter o service."""
    return InstallationService(db)


@router.post("", response_model=InstallationResponse, status_code=status.HTTP_201_CREATED)
async def create_installation(
    data: InstallationCreate,
    current_user: CurrentActiveUser,
    service: InstallationService = Depends(get_service),
) -> InstallationResponse:
    """Cria uma nova instalação."""
    try:
        return await service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar instalação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar instalação",
        )


@router.get("", response_model=InstallationListResponse)
async def list_installations(
    current_user: CurrentActiveUser,
    search: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    client_id: str | None = Query(None),
    technician_id: str | None = Query(None),
    priority: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    is_overdue: bool | None = Query(None),
    has_acceptance: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: InstallationService = Depends(get_service),
) -> InstallationListResponse:
    """Lista instalações com filtros."""
    filters = InstallationFilter(
        search=search,
        status=status_filter,
        client_id=client_id,
        technician_id=technician_id,
        priority=priority,
        date_from=date_from,
        date_to=date_to,
        is_overdue=is_overdue,
        has_acceptance=has_acceptance,
    )
    return await service.list_with_filters(filters, page, page_size)


@router.get("/overdue", response_model=list[InstallationResponse])
async def get_overdue(
    current_user: CurrentActiveUser,
    service: InstallationService = Depends(get_service),
) -> list[InstallationResponse]:
    """Lista instalações atrasadas."""
    return await service.get_overdue()


@router.get("/pending-acceptance", response_model=list[InstallationResponse])
async def get_pending_acceptance(
    current_user: CurrentActiveUser,
    service: InstallationService = Depends(get_service),
) -> list[InstallationResponse]:
    """Lista instalações aguardando aceite."""
    return await service.get_pending_acceptance()


@router.get("/by-date/{date}", response_model=list[InstallationResponse])
async def get_by_date(
    date: datetime,
    current_user: CurrentActiveUser,
    service: InstallationService = Depends(get_service),
) -> list[InstallationResponse]:
    """Lista instalações agendadas para uma data."""
    return await service.get_scheduled_for_date(date)


@router.get("/by-client/{client_id}", response_model=list[InstallationResponse])
async def get_by_client(
    client_id: str,
    current_user: CurrentActiveUser,
    service: InstallationService = Depends(get_service),
) -> list[InstallationResponse]:
    """Lista instalações de um cliente."""
    return await service.get_by_client(client_id)


@router.get("/by-technician/{technician_id}", response_model=list[InstallationResponse])
async def get_by_technician(
    technician_id: str,
    current_user: CurrentActiveUser,
    include_completed: bool = Query(False),
    service: InstallationService = Depends(get_service),
) -> list[InstallationResponse]:
    """Lista instalações de um técnico."""
    return await service.get_by_technician(technician_id, include_completed)


@router.get("/technician-schedule/{technician_id}", response_model=list[InstallationResponse])
async def get_technician_schedule(
    technician_id: str,
    date: datetime,
    current_user: CurrentActiveUser,
    service: InstallationService = Depends(get_service),
) -> list[InstallationResponse]:
    """Obtém agenda do técnico para uma data."""
    return await service.get_technician_schedule(technician_id, date)


@router.get("/stats")
async def get_stats(
    date_from: datetime,
    date_to: datetime,
    current_user: CurrentActiveUser,
    service: InstallationService = Depends(get_service),
) -> dict:
    """Estatísticas de instalações por período."""
    return await service.get_stats_by_period(date_from, date_to)


@router.get("/code/{code}", response_model=InstallationResponse)
async def get_by_code(
    code: str,
    current_user: CurrentActiveUser,
    service: InstallationService = Depends(get_service),
) -> InstallationResponse:
    """Busca instalação por código."""
    installation = await service.get_by_code(code)
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instalação não encontrada",
        )
    return installation


@router.get("/{installation_id}", response_model=InstallationResponse)
async def get_installation(
    installation_id: str,
    current_user: CurrentActiveUser,
    service: InstallationService = Depends(get_service),
) -> InstallationResponse:
    """Busca instalação por ID."""
    installation = await service.get_by_id(installation_id)
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instalação não encontrada",
        )
    return installation


@router.put("/{installation_id}", response_model=InstallationResponse)
async def update_installation(
    installation_id: str,
    data: InstallationUpdate,
    current_user: CurrentActiveUser,
    service: InstallationService = Depends(get_service),
) -> InstallationResponse:
    """Atualiza uma instalação."""
    installation = await service.update(installation_id, data)
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instalação não encontrada",
        )
    return installation


@router.delete("/{installation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_installation(
    installation_id: str,
    current_user: CurrentActiveUser,
    service: InstallationService = Depends(get_service),
) -> None:
    """Remove uma instalação (soft delete)."""
    result = await service.delete(installation_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instalação não encontrada",
        )


@router.post("/{installation_id}/start", response_model=InstallationResponse, status_code=201)
async def start_installation(
    installation_id: str,
    current_user: CurrentActiveUser,
    service: InstallationService = Depends(get_service),
) -> InstallationResponse:
    """Inicia uma instalação."""
    installation = await service.start(installation_id)
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instalação não encontrada",
        )
    return installation


@router.post("/{installation_id}/complete", response_model=InstallationResponse, status_code=201)
async def complete_installation(
    installation_id: str,
    current_user: CurrentActiveUser,
    technical_report: str | None = None,
    service: InstallationService = Depends(get_service),
) -> InstallationResponse:
    """Conclui uma instalação."""
    installation = await service.complete(installation_id, technical_report)
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instalação não encontrada",
        )
    return installation


@router.post("/{installation_id}/cancel", response_model=InstallationResponse, status_code=201)
async def cancel_installation(
    installation_id: str,
    reason: str,
    current_user: CurrentActiveUser,
    service: InstallationService = Depends(get_service),
) -> InstallationResponse:
    """Cancela uma instalação."""
    installation = await service.cancel(installation_id, reason)
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instalação não encontrada",
        )
    return installation


@router.post("/{installation_id}/reschedule", response_model=InstallationResponse, status_code=201)
async def reschedule_installation(
    installation_id: str,
    new_date: datetime,
    current_user: CurrentActiveUser,
    reason: str | None = None,
    service: InstallationService = Depends(get_service),
) -> InstallationResponse:
    """Reagenda uma instalação."""
    installation = await service.reschedule(installation_id, new_date, reason)
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instalação não encontrada",
        )
    return installation


@router.post("/{installation_id}/accept", response_model=InstallationResponse, status_code=201)
async def accept_installation(
    installation_id: str,
    accepted_by: str,
    current_user: CurrentActiveUser,
    service: InstallationService = Depends(get_service),
) -> InstallationResponse:
    """Registra aceite do cliente."""
    installation = await service.accept_by_client(installation_id, accepted_by)
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instalação não encontrada",
        )
    return installation


@router.post("/{installation_id}/photo", response_model=InstallationResponse, status_code=201)
async def add_photo(
    installation_id: str,
    photo_url: str,
    current_user: CurrentActiveUser,
    photo_type: str = "after",
    service: InstallationService = Depends(get_service),
) -> InstallationResponse:
    """Adiciona foto à instalação."""
    installation = await service.add_photo(installation_id, photo_url, photo_type)
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instalação não encontrada",
        )
    return installation


@router.post("/{installation_id}/assign-technician", response_model=InstallationResponse, status_code=201)
async def assign_technician(
    installation_id: str,
    technician_id: str,
    technician_name: str,
    current_user: CurrentActiveUser,
    service: InstallationService = Depends(get_service),
) -> InstallationResponse:
    """Atribui técnico à instalação."""
    installation = await service.assign_technician(installation_id, technician_id, technician_name)
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instalação não encontrada",
        )
    return installation
