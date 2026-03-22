"""
Controller PPRA/PGR (NR-9) - Programa de Prevencao de Riscos Ambientais
=======================================================================

Endpoints REST para mapeamento de riscos ocupacionais.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from core.database.session import get_sync_db_dependency
from modules.health_occupational.schemas.common import StandardResponse
from modules.health_occupational.schemas.ppra import (
    ControlMeasureRequest,
    ControlMeasureResponse,
    ControlMeasureUpdateRequest,
    OccupationalRiskResponse,
    RiskMappingRequest,
    RiskMappingResponse,
    RiskMappingUpdateRequest,
)
from modules.health_occupational.services.ppra_service import PPRAService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ppra", tags=["PPRA/PGR - Riscos Ocupacionais (NR-9)"])


# Dependency para obter o service com DB session
def get_ppra_service(db: Session = Depends(get_sync_db_dependency)) -> PPRAService:
    """Retorna instancia do PPRAService com DB session."""
    return PPRAService(db=db)


# ==============================================================================
# Risk Mapping Endpoints
# ==============================================================================


@router.post(
    "/mapeamento",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria mapeamento de riscos",
    description="Registra mapeamento de riscos ocupacionais de um setor.",
)
async def create_risk_mapping(
    request: RiskMappingRequest,
    service: PPRAService = Depends(get_ppra_service),
) -> StandardResponse:
    """
    Cria mapeamento de riscos ocupacionais.

    Args:
        request: Dados do mapeamento.
        service: Service de PPRA.

    Returns:
        StandardResponse: Mapeamento criado.

    Raises:
        HTTPException: Se falhar a criacao.
    """
    try:
        mapping = service.create_mapping(request)

        logger.info(
            "Mapeamento de riscos criado: setor=%s, nivel=%s",
            request.setor,
            mapping.nivel_risco_geral,
        )

        return StandardResponse(
            success=True,
            message="Mapeamento de riscos criado com sucesso",
            data={
                "mapping_id": str(mapping.id),
                "setor": request.setor,
                "funcoes": request.funcoes,
                "total_riscos": len(mapping.riscos),
                "nivel_risco_setor": mapping.nivel_risco_geral,
                "avaliador": request.avaliador,
                "data_avaliacao": mapping.data_avaliacao.isoformat(),
            },
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de validacao: {str(e)}",
        )
    except Exception as e:
        logger.error("Erro ao criar mapeamento: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar mapeamento",
        )


@router.get(
    "/mapeamento/{mapping_id}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca mapeamento por ID",
)
async def get_mapping(
    mapping_id: UUID,
    service: PPRAService = Depends(get_ppra_service),
) -> StandardResponse:
    """Busca mapeamento por ID."""
    try:
        mapping = service.get_mapping(mapping_id)
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mapeamento nao encontrado",
            )

        return StandardResponse(
            success=True,
            message="Mapeamento encontrado",
            data=RiskMappingResponse.model_validate(mapping).model_dump(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao buscar mapeamento: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno",
        )


@router.patch(
    "/mapeamento/{mapping_id}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualiza mapeamento de riscos",
)
async def update_mapping(
    mapping_id: UUID,
    request: RiskMappingUpdateRequest,
    service: PPRAService = Depends(get_ppra_service),
) -> StandardResponse:
    """Atualiza mapeamento de riscos."""
    try:
        mapping = service.update_mapping(mapping_id, request)
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mapeamento nao encontrado",
            )

        return StandardResponse(
            success=True,
            message="Mapeamento atualizado",
            data={
                "mapping_id": str(mapping.id),
                "versao": mapping.versao,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao atualizar mapeamento: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno",
        )


@router.get(
    "/mapeamentos",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista mapeamentos de risco",
)
async def list_mappings(
    setor: str | None = Query(None, description="Filtrar por setor"),
    ativo: bool | None = Query(True, description="Filtrar por status"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    service: PPRAService = Depends(get_ppra_service),
) -> StandardResponse:
    """Lista mapeamentos de risco."""
    try:
        result = service.list_mappings(
            setor=setor,
            ativo=ativo,
            page=page,
            size=size,
        )

        return StandardResponse(
            success=True,
            message=f"Encontrados {result['total']} mapeamentos",
            data={
                "mapeamentos": [RiskMappingResponse.model_validate(m).model_dump() for m in result["items"]],
                "total": result["total"],
                "page": result["page"],
                "size": result["size"],
            },
        )

    except Exception as e:
        logger.error("Erro ao listar mapeamentos: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno",
        )


# ==============================================================================
# Risk Consultation Endpoints
# ==============================================================================


@router.get(
    "/riscos/{setor}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta riscos por setor",
    description="Retorna riscos mapeados de um setor.",
)
async def get_sector_risks(
    setor: str = Path(..., min_length=2, description="Nome do setor"),
    service: PPRAService = Depends(get_ppra_service),
) -> StandardResponse:
    """Consulta riscos de um setor."""
    try:
        risks = service.get_sector_risks(setor)

        return StandardResponse(
            success=True,
            message=f"Riscos do setor {setor}",
            data={
                "setor": setor,
                "riscos": [OccupationalRiskResponse.model_validate(r).model_dump() for r in risks],
                "total": len(risks),
                "nivel_geral": service.calculate_sector_risk(setor),
            },
        )

    except Exception as e:
        logger.error("Erro ao consultar riscos: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao consultar riscos",
        )


@router.get(
    "/riscos/funcao/{funcao}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta riscos por funcao",
    description="Retorna riscos associados a uma funcao.",
)
async def get_function_risks(
    funcao: str = Path(..., min_length=2, description="Nome da funcao"),
    service: PPRAService = Depends(get_ppra_service),
) -> StandardResponse:
    """Consulta riscos de uma funcao."""
    try:
        risks = service.get_function_risks(funcao)
        epis = service.get_recommended_epis(funcao)

        return StandardResponse(
            success=True,
            message=f"Riscos da funcao {funcao}",
            data={
                "funcao": funcao,
                "riscos": [OccupationalRiskResponse.model_validate(r).model_dump() for r in risks],
                "total": len(risks),
                "epis_recomendados": epis,
            },
        )

    except Exception as e:
        logger.error("Erro ao consultar riscos da funcao: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao consultar riscos",
        )


# ==============================================================================
# Control Measure Endpoints
# ==============================================================================


@router.post(
    "/medidas-controle",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adiciona medida de controle",
)
async def add_control_measure(
    request: ControlMeasureRequest,
    service: PPRAService = Depends(get_ppra_service),
) -> StandardResponse:
    """Adiciona medida de controle."""
    try:
        measure = service.add_control_measure(request)

        return StandardResponse(
            success=True,
            message="Medida de controle adicionada",
            data={
                "measure_id": str(measure.id),
                "tipo": measure.tipo,
                "status": measure.status,
            },
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Erro ao adicionar medida: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno",
        )


@router.patch(
    "/medidas-controle/{measure_id}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualiza medida de controle",
)
async def update_control_measure(
    measure_id: UUID,
    request: ControlMeasureUpdateRequest,
    service: PPRAService = Depends(get_ppra_service),
) -> StandardResponse:
    """Atualiza medida de controle."""
    try:
        measure = service.update_control_measure(measure_id, request)
        if not measure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medida nao encontrada",
            )

        return StandardResponse(
            success=True,
            message="Medida atualizada",
            data=ControlMeasureResponse.model_validate(measure).model_dump(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao atualizar medida: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno",
        )


@router.get(
    "/mapeamento/{mapping_id}/medidas-controle",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista medidas de controle de um mapeamento",
)
async def list_control_measures(
    mapping_id: UUID,
    status_filter: str | None = Query(None, description="Filtrar por status"),
    service: PPRAService = Depends(get_ppra_service),
) -> StandardResponse:
    """Lista medidas de controle de um mapeamento."""
    try:
        measures = service.list_control_measures(mapping_id, status=status_filter)

        return StandardResponse(
            success=True,
            message=f"Encontradas {len(measures)} medidas",
            data={
                "mapeamento_id": str(mapping_id),
                "medidas": [ControlMeasureResponse.model_validate(m).model_dump() for m in measures],
                "total": len(measures),
            },
        )

    except Exception as e:
        logger.error("Erro ao listar medidas: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno",
        )


# ==============================================================================
# Reference Data Endpoints
# ==============================================================================


@router.get(
    "/categorias",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista categorias de risco",
    description="Retorna categorias de risco conforme NR-9.",
)
async def list_risk_categories(
    service: PPRAService = Depends(get_ppra_service),
) -> StandardResponse:
    """Lista categorias de risco ocupacional."""
    data = service.get_risk_categories()

    return StandardResponse(
        success=True,
        message="Categorias de risco ocupacional",
        data=data,
    )


# ==============================================================================
# Statistics Endpoint
# ==============================================================================


@router.get(
    "/estatisticas",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Estatisticas do PPRA",
)
async def get_statistics(
    service: PPRAService = Depends(get_ppra_service),
) -> StandardResponse:
    """Retorna estatisticas do PPRA."""
    try:
        stats = service.get_statistics()

        return StandardResponse(
            success=True,
            message="Estatisticas do PPRA",
            data=stats,
        )

    except Exception as e:
        logger.error("Erro ao obter estatisticas: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno",
        )
