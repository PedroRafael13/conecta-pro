"""Controller de Ponto Eletronico — rotas FastAPI com persistencia no banco."""

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from core.database.session import get_db, get_sync_db_dependency

from ..schemas.dashboard_schemas import (
    AjusteRequest,
    BancoHorasResponse,
    ColaboradorSemEscalaResponse,
    DashboardPontoResponse,
    InconsistenciaResumoResponse,
    SyncSolidesRequest,
    SyncSolidesResponse,
)
from ..schemas.punch_schemas import (
    JustificationCreate,
    JustificationResponse,
    JustificationReview,
    MonthlyClosingResponse,
    PunchCreate,
    PunchResponse,
    PunchSyncRequest,
    PunchSyncResponse,
)
from ..services import dashboard_service
from ..services.punch_service import PunchService

router = APIRouter(prefix="/ponto", tags=["Ponto Eletronico"])


# ==================== BATIDA E ESPELHO (async, banco real) ====================


@router.post("/batida", response_model=PunchResponse, status_code=201)
async def registrar_batida(
    data: PunchCreate,
    db: AsyncSession = Depends(get_db),
) -> PunchResponse:
    """Registra uma batida de ponto (entrada, saida, almoco)."""
    service = PunchService(db)
    result = await service.registrar_batida(data)
    return PunchResponse(
        punch_id=result["punch_id"],
        employee_id=result["employee_id"],
        punch_type=result.get("punch_type"),
        punch_timestamp=result.get("punch_timestamp"),
        status=result.get("status"),
        facial_match=result.get("facial_match"),
        facial_confidence=result.get("facial_confidence"),
        dentro_geofence=result.get("dentro_geofence"),
        is_offline=result.get("is_offline", False),
        message="Ponto registrado com sucesso",
    )


@router.post("/sync", response_model=PunchSyncResponse)
async def sync_offline_punches(
    data: PunchSyncRequest,
    db: AsyncSession = Depends(get_db),
) -> PunchSyncResponse:
    """Sincroniza batidas feitas em modo offline."""
    service = PunchService(db)
    result = await service.sync_offline_punches(data.punches)
    return PunchSyncResponse(**result)


@router.get("/batidas/{employee_id}")
async def get_batidas_dia(
    employee_id: int,
    data: str = Query(..., description="Data no formato YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retorna batidas de um funcionario em um dia."""
    service = PunchService(db)
    batidas = await service.get_batidas_dia(employee_id, data)
    return {"employee_id": employee_id, "date": data, "punches": batidas}


@router.get("/espelho/{employee_id}")
async def get_espelho_mensal(
    employee_id: int,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retorna espelho de ponto mensal."""
    service = PunchService(db)
    return await service.get_espelho_mensal(employee_id, month, year)


@router.post("/justificativa", response_model=JustificationResponse, status_code=201)
async def criar_justificativa(
    data: JustificationCreate,
    db: AsyncSession = Depends(get_db),
) -> JustificationResponse:
    """Cria justificativa de atraso ou falta."""
    service = PunchService(db)
    result = await service.criar_justificativa(data)
    return JustificationResponse(
        justification_id=result["justification_id"],
        employee_id=result["employee_id"],
        type=result["type"],
        reason=result["reason"],
        category=result["category"],
        status=result["status"],
        created_at=result["created_at"],
    )


@router.put("/justificativa/{justification_id}/revisar")
async def revisar_justificativa(
    justification_id: str,
    data: JustificationReview,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Aprova ou rejeita uma justificativa."""
    service = PunchService(db)
    try:
        return await service.revisar_justificativa(
            justification_id,
            data.action,
            data.reviewer_id,
            data.notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/justificativas/pendentes")
async def get_justificativas_pendentes(
    employee_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Lista justificativas pendentes de aprovacao."""
    service = PunchService(db)
    return await service.get_justificativas_pendentes(employee_id)


@router.post("/fechamento", response_model=MonthlyClosingResponse)
async def fechar_mes(
    employee_id: int,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020),
    fechado_por: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> MonthlyClosingResponse:
    """Fecha o ponto mensal de um funcionario."""
    service = PunchService(db)
    result = await service.fechar_mes(employee_id, month, year, fechado_por)
    return MonthlyClosingResponse(**result)


# ==================== DASHBOARD E RELATORIOS (sync, dados reais) ====================


@router.get(
    "/dashboard",
    response_model=DashboardPontoResponse,
    summary="Dashboard gerencial do ponto",
)
def ponto_dashboard(
    db: Session = Depends(get_sync_db_dependency),
) -> DashboardPontoResponse:
    """Visao gerencial com dados reais: presenca, inconsistencias, banco de horas."""
    data = dashboard_service.get_dashboard(db)
    return DashboardPontoResponse(**data)


@router.get(
    "/relatorio/inconsistencias",
    response_model=InconsistenciaResumoResponse,
    summary="Relatorio de inconsistencias CCT",
)
def relatorio_inconsistencias(
    periodo_inicio: str | None = Query(None, description="YYYY-MM-DD"),
    periodo_fim: str | None = Query(None, description="YYYY-MM-DD"),
    db: Session = Depends(get_sync_db_dependency),
) -> InconsistenciaResumoResponse:
    """Analisa inconsistencias usando regras CCT 2026 SINDECOMPRESTS."""
    data = dashboard_service.get_inconsistencias(db, periodo_inicio, periodo_fim)
    return InconsistenciaResumoResponse(**data)


@router.get(
    "/banco-horas/{employee_id}",
    response_model=BancoHorasResponse,
    summary="Saldo banco de horas",
)
def banco_horas(
    employee_id: str,
    db: Session = Depends(get_sync_db_dependency),
) -> BancoHorasResponse:
    """Retorna saldo de banco de horas com prazo CCT (6 meses)."""
    data = dashboard_service.get_banco_horas(db, employee_id)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return BancoHorasResponse(**data)


@router.post(
    "/sincronizar-solides",
    response_model=SyncSolidesResponse,
    summary="Sincronizar ponto com Solides Tangerino",
)
def sincronizar_solides(
    request: SyncSolidesRequest = Body(default=SyncSolidesRequest()),
    db: Session = Depends(get_sync_db_dependency),
) -> SyncSolidesResponse:
    """Importa registros de ponto do Solides Tangerino."""
    data = dashboard_service.sync_solides_ponto(db, request.periodo_inicio, request.periodo_fim)
    return SyncSolidesResponse(**data)


@router.post("/ajuste", summary="Ajuste manual de ponto pelo DP")
def ajuste_ponto(
    request: AjusteRequest,
    db: Session = Depends(get_sync_db_dependency),
) -> dict[str, Any]:
    """Registra ajuste manual de ponto (somente DP)."""
    return dashboard_service.registrar_ajuste(db, request.model_dump())


@router.get(
    "/colaboradores-sem-escala",
    response_model=list[ColaboradorSemEscalaResponse],
    summary="Colaboradores sem escala definida",
)
def colaboradores_sem_escala(
    db: Session = Depends(get_sync_db_dependency),
) -> list[ColaboradorSemEscalaResponse]:
    """Lista colaboradores ativos sem escala — necessitam correcao."""
    items = dashboard_service.get_colaboradores_sem_escala(db)
    return [ColaboradorSemEscalaResponse(**i) for i in items]
