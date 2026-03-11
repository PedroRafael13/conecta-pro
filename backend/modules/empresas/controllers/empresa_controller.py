"""Controller para o módulo de Empresas (Multi-CNPJ)."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import CurrentActiveUser, get_tenant_id
from core.database import get_db
from modules.empresas.schemas.empresa_schemas import (
    EmpresaCreate,
    EmpresaListResponse,
    EmpresaResponse,
    EmpresaUpdate,
    LiminarCreate,
    LiminarResponse,
    LiminarUpdate,
    SimulacaoRegime,
    SugestaoEmpresaFaturamento,
)
from modules.empresas.services import empresa_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/empresas", tags=["Empresas - Multi-CNPJ"])


# ===================================================================
# REQUEST BODIES AUXILIARES
# ===================================================================


class SimularRegimeBody(BaseModel):
    novo_regime: str
    faturamento_anual: float


# ===================================================================
# EMPRESA ENDPOINTS
# ===================================================================


@router.post(
    "/",
    response_model=EmpresaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar empresa",
)
async def criar_empresa(
    dados: EmpresaCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> EmpresaResponse:
    """Cria uma nova empresa (CNPJ) para o grupo empresarial."""
    try:
        condominio_id = UUID(get_tenant_id(current_user))
        return await empresa_service.criar_empresa(db, dados, condominio_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao criar empresa: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar empresa",
        ) from exc


@router.get(
    "/",
    response_model=list[EmpresaListResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar empresas",
)
async def listar_empresas(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    status_filtro: str | None = Query(None, alias="status", description="Filtrar por status"),
) -> list[EmpresaListResponse]:
    """Lista todas as empresas do grupo empresarial."""
    try:
        condominio_id = UUID(get_tenant_id(current_user))
        return await empresa_service.listar_empresas(db, condominio_id, status_filtro=status_filtro)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao listar empresas: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar empresas",
        ) from exc


@router.get(
    "/sugerir/{tipo_servico}",
    response_model=SugestaoEmpresaFaturamento,
    status_code=status.HTTP_200_OK,
    summary="Sugerir empresa para tipo de serviço",
)
async def sugerir_empresa_para_servico(
    tipo_servico: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> SugestaoEmpresaFaturamento:
    """Sugere qual empresa deve faturar um determinado tipo de serviço."""
    try:
        condominio_id = UUID(get_tenant_id(current_user))
        return await empresa_service.sugerir_empresa_para_servico(db, tipo_servico, condominio_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao sugerir empresa: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao sugerir empresa",
        ) from exc


@router.get(
    "/{empresa_id}",
    response_model=EmpresaResponse,
    status_code=status.HTTP_200_OK,
    summary="Obter empresa",
)
async def obter_empresa(
    empresa_id: UUID,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> EmpresaResponse:
    """Retorna detalhes completos de uma empresa, incluindo liminares."""
    try:
        condominio_id = UUID(get_tenant_id(current_user))
        return await empresa_service.obter_empresa(db, empresa_id, condominio_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao obter empresa: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter empresa",
        ) from exc


@router.patch(
    "/{empresa_id}",
    response_model=EmpresaResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar empresa",
)
async def atualizar_empresa(
    empresa_id: UUID,
    dados: EmpresaUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> EmpresaResponse:
    """Atualiza dados de uma empresa."""
    try:
        condominio_id = UUID(get_tenant_id(current_user))
        return await empresa_service.atualizar_empresa(db, empresa_id, dados, condominio_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao atualizar empresa: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar empresa",
        ) from exc


@router.post(
    "/{empresa_id}/simular-regime",
    response_model=SimulacaoRegime,
    status_code=status.HTTP_200_OK,
    summary="Simular mudança de regime tributário",
)
async def simular_mudanca_regime(
    empresa_id: UUID,
    body: SimularRegimeBody,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> SimulacaoRegime:
    """Simula a carga tributária em outro regime e calcula a economia potencial."""
    try:
        condominio_id = UUID(get_tenant_id(current_user))
        return await empresa_service.simular_mudanca_regime(
            db, empresa_id, body.novo_regime, body.faturamento_anual, condominio_id
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao simular regime: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao simular regime tributário",
        ) from exc


# ===================================================================
# LIMINARES ENDPOINTS
# ===================================================================


@router.post(
    "/{empresa_id}/liminares",
    response_model=LiminarResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar liminar",
)
async def cadastrar_liminar(
    empresa_id: UUID,
    dados: LiminarCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> LiminarResponse:
    """Cadastra uma liminar judicial para a empresa."""
    try:
        condominio_id = UUID(get_tenant_id(current_user))
        return await empresa_service.cadastrar_liminar(db, empresa_id, dados, condominio_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao cadastrar liminar: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao cadastrar liminar",
        ) from exc


@router.get(
    "/{empresa_id}/liminares",
    response_model=list[LiminarResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar liminares",
)
async def listar_liminares(
    empresa_id: UUID,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> list[LiminarResponse]:
    """Lista todas as liminares de uma empresa."""
    try:
        condominio_id = UUID(get_tenant_id(current_user))
        return await empresa_service.listar_liminares(db, empresa_id, condominio_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao listar liminares: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar liminares",
        ) from exc


@router.get(
    "/{empresa_id}/liminares/ativas",
    response_model=list[LiminarResponse],
    status_code=status.HTTP_200_OK,
    summary="Verificar liminares ativas",
)
async def verificar_liminares_ativas(
    empresa_id: UUID,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> list[LiminarResponse]:
    """Retorna apenas as liminares com status CONCEDIDA (em vigor)."""
    try:
        condominio_id = UUID(get_tenant_id(current_user))
        return await empresa_service.verificar_liminares_ativas(db, empresa_id, condominio_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao verificar liminares ativas: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao verificar liminares ativas",
        ) from exc


@router.patch(
    "/{empresa_id}/liminares/{liminar_id}",
    response_model=LiminarResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar liminar",
)
async def atualizar_liminar(
    empresa_id: UUID,
    liminar_id: UUID,
    dados: LiminarUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> LiminarResponse:
    """Atualiza dados de uma liminar (ex: mudar status para CONCEDIDA)."""
    try:
        condominio_id = UUID(get_tenant_id(current_user))
        return await empresa_service.atualizar_liminar(db, empresa_id, liminar_id, dados, condominio_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao atualizar liminar: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar liminar",
        ) from exc
