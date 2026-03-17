"""
Controller de Beneficios — CCT 2026.

Endpoints para beneficios obrigatorios, validacao e taxa negocial.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.cct.schemas.benefits_schemas import (
    BenefitConfigCreate,
    BenefitsValidationRequest,
)
from modules.cct.services.benefits_service import BenefitsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/beneficios", tags=["CCT — Beneficios"])


@router.get("/")
async def get_beneficios_cct(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna lista completa de beneficios da CCT 2026."""
    service = BenefitsService(db)
    return service.get_beneficios_cct()


@router.post("/validar")
async def validar_beneficios(
    data: BenefitsValidationRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Valida beneficios de um colaborador contra obrigatorios CCT."""
    service = BenefitsService(db)
    return service.validar_beneficios(
        employee_id=data.employee_id,
        salario_base=data.salario_base,
        beneficios_ativos=data.beneficios_ativos,
        valor_vr_dia=data.valor_vr_dia,
        desconto_vt_percentual=data.desconto_vt_percentual,
    )


@router.get("/taxa-negocial")
async def get_taxa_negocial(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    mes: int | None = Query(None, ge=1, le=12),
) -> Any:
    """Retorna informacoes da taxa negocial sindical 2026."""
    service = BenefitsService(db)
    return service.get_taxa_negocial(mes)


@router.post("/config", status_code=201)
async def criar_config_beneficio(
    data: BenefitConfigCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Cria configuracao de beneficio por empresa."""
    service = BenefitsService(db)
    config = await service.criar_config_beneficio(data.model_dump())
    await db.commit()
    return config


@router.get("/config")
async def listar_configs_beneficios(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    empresa_id: str | None = Query(None),
) -> Any:
    """Lista configuracoes de beneficios ativas."""
    service = BenefitsService(db)
    configs = await service.listar_configs_beneficios(empresa_id)
    return {"items": list(configs), "total": len(configs)}
