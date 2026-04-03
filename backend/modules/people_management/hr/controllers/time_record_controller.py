"""
Controller de Ponto Eletronico (Time Records) — Departamento Pessoal.

Endpoints completos para gestao de registros de ponto:
- Listagem com filtros e paginacao
- Clock-in / Clock-out
- Lancamento manual (admin/DP)
- Atualizacao e justificativa
- Resumo mensal por funcionario
- Registros diarios
"""

import logging
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.people_management.hr.schemas.time_record import (
    ClockInRequest,
    ClockOutRequest,
    DailyRecordsResponse,
    MonthlySummaryResponse,
    TimeRecordCreate,
    TimeRecordListResponse,
    TimeRecordResponse,
    TimeRecordUpdate,
)
from modules.people_management.hr.services.time_record_service import TimeRecordService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/time-records", tags=["DP - Ponto Eletrônico"])


@router.get("", summary="Listar Registros de Ponto", response_model=TimeRecordListResponse)
async def list_time_records(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    employee_id: str | None = Query(None, description="Filtro por funcionário"),
    date_from: date | None = Query(None, description="Data inicial (YYYY-MM-DD)"),
    date_to: date | None = Query(None, description="Data final (YYYY-MM-DD)"),
    status: str | None = Query(None, description="regular|falta|atestado|feriado|compensacao|inconsistencia"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Any:
    """Lista registros de ponto com filtros e paginação."""
    service = TimeRecordService(db)
    return await service.list_records(
        employee_id=employee_id,
        date_from=date_from,
        date_to=date_to,
        status=status,
        page=page,
        page_size=page_size,
    )


@router.get("/daily/{record_date}", summary="Registros do Dia", response_model=DailyRecordsResponse)
async def get_daily_records(
    record_date: date,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna todos os registros de ponto de um dia específico."""
    service = TimeRecordService(db)
    return await service.get_daily(record_date)


@router.get("/employee/{employee_id}/summary", summary="Resumo Mensal de Ponto", response_model=MonthlySummaryResponse)
async def get_employee_summary(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    month: int = Query(..., ge=1, le=12, description="Mês (1-12)"),
    year: int = Query(..., ge=2020, description="Ano"),
) -> Any:
    """Retorna resumo mensal de ponto de um funcionário (horas, extras, faltas)."""
    service = TimeRecordService(db)
    return await service.get_summary(employee_id, month, year)


@router.post("/clock-in", summary="Batida de Entrada", response_model=TimeRecordResponse, status_code=201)
async def clock_in(
    data: ClockInRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Registra batida de entrada (clock-in) para um funcionário."""
    service = TimeRecordService(db)
    result = await service.clock_in(
        employee_id=data.employee_id,
        location_lat=data.location_lat,
        location_lng=data.location_lng,
        posto_id=data.posto_id,
        device_type=data.device_type,
        notes=data.notes,
        created_by=str(current_user.id),
    )
    await db.commit()
    return result


@router.post("/clock-out/{record_id}", summary="Batida de Saída", response_model=TimeRecordResponse, status_code=201)
async def clock_out(
    record_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    data: ClockOutRequest | None = None,
) -> Any:
    """Registra batida de saída (clock-out) vinculada a uma entrada."""
    service = TimeRecordService(db)
    try:
        result = await service.clock_out(
            record_id=record_id,
            location_lat=data.location_lat if data else None,
            location_lng=data.location_lng if data else None,
            notes=data.notes if data else None,
            created_by=str(current_user.id),
        )
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", summary="Lançamento Manual de Ponto", response_model=TimeRecordResponse, status_code=201)
async def create_manual_record(
    data: TimeRecordCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Cria lançamento manual de ponto (uso por admin/DP)."""
    service = TimeRecordService(db)
    result = await service.create_manual(
        data=data.model_dump(),
        created_by=str(current_user.id),
    )
    await db.commit()
    return result


@router.get("/{record_id}", summary="Buscar Registro de Ponto", response_model=TimeRecordResponse)
async def get_time_record(
    record_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna detalhes de um registro de ponto."""
    service = TimeRecordService(db)
    record = await service.get_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro de ponto não encontrado")
    return record


@router.patch("/{record_id}", summary="Atualizar/Justificar Registro", response_model=TimeRecordResponse)
async def update_time_record(
    record_id: str,
    data: TimeRecordUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Atualiza/justifica um registro de ponto."""
    service = TimeRecordService(db)
    record = await service.update_record(
        record_id=record_id,
        data=data.model_dump(exclude_unset=True),
        updated_by=str(current_user.id),
    )
    if not record:
        raise HTTPException(status_code=404, detail="Registro de ponto não encontrado")
    await db.commit()
    return record
