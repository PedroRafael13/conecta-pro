"""Controller para endpoints de KPIs."""

import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db
from modules.hr.analytics_dashboard.models import KPICategory
from modules.hr.analytics_dashboard.repositories import KPIRepository
from modules.hr.analytics_dashboard.schemas import (
    KPIDashboardResponse,
    KPIDefinitionCreate,
    KPIDefinitionResponse,
    KPIDefinitionUpdate,
    KPIHistoryResponse,
    KPIValueResponse,
)
from modules.hr.analytics_dashboard.services import KPICalculatorService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/kpis", tags=["KPIs"])


@router.get("", response_model=list[KPIDefinitionResponse])
async def list_kpis(
    category: KPICategory | None = Query(None),
    featured_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Lista definições de KPIs."""
    repo = KPIRepository(db)
    kpis, _total = await repo.list_kpis(
        condominio_id=current_user["condominio_id"],
        category=category,
        featured_only=featured_only,
        page=page,
        page_size=page_size,
    )
    return kpis


@router.post("", response_model=KPIDefinitionResponse, status_code=status.HTTP_201_CREATED)
async def create_kpi(
    data: KPIDefinitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Cria nova definição de KPI."""
    repo = KPIRepository(db)

    # Verificar se código já existe
    existing = await repo.get_kpi_by_code(data.code, current_user["condominio_id"])
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"KPI com código {data.code} já existe",
        )

    kpi = await repo.create_kpi(
        data=data,
        condominio_id=current_user["condominio_id"],
        created_by=current_user.id,
    )
    return kpi


@router.get("/categories")
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Lista categorias de KPI com contagem."""
    repo = KPIRepository(db)
    grouped = await repo.list_kpis_by_category(
        condominio_id=current_user["condominio_id"],
    )

    return [
        {
            "category": cat,
            "count": len(kpis),
            "kpi_codes": [k.code for k in kpis],
        }
        for cat, kpis in grouped.items()
    ]


@router.get("/codes")
async def list_kpi_codes(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Lista códigos de KPI disponíveis."""
    repo = KPIRepository(db)
    codes = await repo.get_kpi_codes(
        condominio_id=current_user["condominio_id"],
    )
    return {"codes": codes}


@router.get("/dashboard", response_model=KPIDashboardResponse)
async def get_kpi_dashboard(
    kpi_codes: str | None = Query(None, description="Códigos separados por vírgula"),
    period_start: datetime | None = Query(None),
    period_end: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Obtém dashboard de KPIs."""
    service = KPICalculatorService(db)

    codes = kpi_codes.split(",") if kpi_codes else None

    kpis = await service.calculate_dashboard_kpis(
        condominio_id=current_user["condominio_id"],
        kpi_codes=codes,
        period_start=period_start,
        period_end=period_end,
    )

    return KPIDashboardResponse(
        kpis=kpis,
        period_start=period_start or datetime.utcnow(),
        period_end=period_end or datetime.utcnow(),
        condominio_id=current_user["condominio_id"],
        computed_at=datetime.utcnow(),
    )


@router.get("/{kpi_code}", response_model=KPIDefinitionResponse)
async def get_kpi(
    kpi_code: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Obtém definição de KPI por código."""
    repo = KPIRepository(db)
    kpi = await repo.get_kpi_by_code(
        code=kpi_code.upper(),
        condominio_id=current_user["condominio_id"],
    )
    if not kpi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"KPI {kpi_code} não encontrado",
        )
    return kpi


@router.patch("/{kpi_id}", response_model=KPIDefinitionResponse)
async def update_kpi(
    kpi_id: UUID,
    data: KPIDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),  # pylint: disable=unused-argument
):
    """Atualiza definição de KPI."""
    repo = KPIRepository(db)
    kpi = await repo.update_kpi(kpi_id, data)
    if not kpi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KPI não encontrado ou é de sistema",
        )
    return kpi


@router.delete("/{kpi_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kpi(
    kpi_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),  # pylint: disable=unused-argument
):
    """Deleta KPI personalizado."""
    repo = KPIRepository(db)
    deleted = await repo.delete_kpi(kpi_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KPI não encontrado ou é de sistema",
        )


@router.get("/{kpi_code}/value", response_model=KPIValueResponse)
async def get_kpi_value(
    kpi_code: str,
    period_start: datetime | None = Query(None),
    period_end: datetime | None = Query(None),
    force_refresh: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Calcula e retorna valor atual do KPI."""
    service = KPICalculatorService(db)

    try:
        value = await service.calculate_kpi(
            kpi_code=kpi_code.upper(),
            condominio_id=current_user["condominio_id"],
            period_start=period_start,
            period_end=period_end,
            use_cache=not force_refresh,
        )
        return value
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{kpi_code}/history", response_model=KPIHistoryResponse)
async def get_kpi_history(
    kpi_code: str,
    period_start: datetime = Query(...),
    period_end: datetime = Query(...),
    granularity: str = Query("daily", regex="^(hourly|daily|weekly|monthly)$"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Obtém histórico de valores do KPI."""
    service = KPICalculatorService(db)
    repo = KPIRepository(db)

    kpi = await repo.get_kpi_by_code(kpi_code.upper(), current_user["condominio_id"])
    if not kpi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"KPI {kpi_code} não encontrado",
        )

    try:
        data_points = await service.get_kpi_history(
            kpi_code=kpi_code.upper(),
            condominio_id=current_user["condominio_id"],
            period_start=period_start,
            period_end=period_end,
            granularity=granularity,
        )

        # Calcular estatísticas
        values = [p.value for p in data_points]
        statistics = {
            "min": min(values) if values else 0,
            "max": max(values) if values else 0,
            "avg": sum(values) / len(values) if values else 0,
            "count": len(values),
        }

        return KPIHistoryResponse(
            kpi_code=kpi.code,
            kpi_name=kpi.name,
            granularity=granularity,
            data_points=data_points,
            statistics=statistics,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{kpi_code}/customize", response_model=KPIDefinitionResponse)
async def customize_kpi(
    kpi_code: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Cria cópia personalizável de um KPI de sistema."""
    repo = KPIRepository(db)
    kpi = await repo.clone_kpi_for_condominio(
        kpi_code=kpi_code.upper(),
        condominio_id=current_user["condominio_id"],
        created_by=current_user.id,
    )
    if not kpi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"KPI {kpi_code} não encontrado",
        )
    return kpi


@router.post("/{kpi_id}/feature", status_code=status.HTTP_204_NO_CONTENT)
async def toggle_featured(
    kpi_id: UUID,
    featured: bool = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),  # pylint: disable=unused-argument
):
    """Alterna destaque de um KPI."""
    repo = KPIRepository(db)
    kpi = await repo.set_featured(kpi_id, featured)
    if not kpi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KPI não encontrado",
        )


@router.post("/seed-defaults")
async def seed_default_kpis(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Cria KPIs padrão (admin only)."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem executar esta ação",
        )

    repo = KPIRepository(db)
    created = await repo.seed_default_kpis()
    return {"created": created, "message": f"{created} KPIs padrão criados"}
