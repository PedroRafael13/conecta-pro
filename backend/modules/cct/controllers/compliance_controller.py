"""
Controller de Compliance — CCT 2026.

Endpoints para verificacao de conformidade geral e estabilidade.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.cct.models.cct_metadata import CCT_METADATA
from modules.cct.schemas.compliance_schemas import (
    ComplianceCheckRequest,
    StabilityCheckRequest,
)
from modules.cct.services.compliance_service import ComplianceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compliance", tags=["CCT — Compliance"])


@router.get("/metadata")
async def get_cct_metadata(
    current_user: CurrentActiveUser,
) -> Any:
    """Retorna metadados da CCT vigente."""
    return {
        "nome": CCT_METADATA.nome,
        "registro_mte": CCT_METADATA.registro_mte,
        "vigencia_inicio": CCT_METADATA.vigencia_inicio,
        "vigencia_fim": CCT_METADATA.vigencia_fim,
        "sindicato_laboral": CCT_METADATA.sindicato_laboral,
        "sindicato_laboral_cnpj": CCT_METADATA.sindicato_laboral_cnpj,
        "sindicato_patronal": CCT_METADATA.sindicato_patronal,
        "sindicato_patronal_cnpj": CCT_METADATA.sindicato_patronal_cnpj,
        "municipio": CCT_METADATA.municipio,
        "uf": CCT_METADATA.uf,
        "data_base": CCT_METADATA.data_base,
    }


@router.post("/verificar")
async def verificar_compliance(
    data: ComplianceCheckRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Executa verificacao de compliance CCT."""
    service = ComplianceService(db)

    if data.tipo_verificacao == "salarios":
        resultado = await service.verificar_compliance_salarios(data.periodo_referencia)
    else:
        resultado = await service.verificar_compliance_salarios(data.periodo_referencia)

    # Persistir resultado
    await service.registrar_verificacao(
        tipo=data.tipo_verificacao,
        periodo=data.periodo_referencia,
        resultado=resultado,
        empresa_id=data.empresa_id,
        executado_por=current_user.email if hasattr(current_user, "email") else None,
    )
    await db.commit()

    return resultado


@router.get("/resumo")
async def get_resumo_compliance(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    periodo: str = Query(..., description="Periodo YYYY-MM", pattern=r"^\d{4}-\d{2}$"),
    empresa_id: str | None = Query(None),
) -> Any:
    """Retorna resumo geral de compliance CCT."""
    service = ComplianceService(db)
    return await service.gerar_resumo_compliance(periodo, empresa_id)


@router.post("/estabilidade")
async def verificar_estabilidade(
    data: StabilityCheckRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Verifica estabilidade de um colaborador conforme CCT."""
    service = ComplianceService(db)
    return service.verificar_estabilidade(
        employee_id=data.employee_id,
        data_admissao=data.data_admissao,
        data_nascimento=data.data_nascimento,
        acidente_trabalho=data.acidente_trabalho,
        data_alta_inss=data.data_alta_inss,
        gestante=data.gestante,
        data_parto=data.data_parto,
    )
