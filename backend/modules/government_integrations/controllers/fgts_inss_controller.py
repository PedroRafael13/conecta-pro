"""
Controller para cálculos de FGTS e INSS.
"""

import logging
import sys

from fastapi import APIRouter, HTTPException, status

sys.path.insert(0, "/opt/conecta-pro")

from government_integrations import CalculoError

from ..schemas.common import StandardResponse
from ..schemas.fgts_inss import CalculoFGTSRequest, CalculoINSSRequest
from ..services.fgts_inss_service import FGTSINSSService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["FGTS/INSS"])


@router.post(
    "/fgts/calcular",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Calcula FGTS",
    description="Calcula valor de FGTS (8% ou rescisorio com multa 40%).",
)
async def calculate_fgts(request: CalculoFGTSRequest) -> StandardResponse:
    """
    Calcula FGTS.

    Args:
        request: Dados para cálculo.

    Returns:
        StandardResponse: Cálculo detalhado do FGTS.
    """
    try:
        resultado = FGTSINSSService.calcular_fgts(
            salario_base=request.salario_base,
            mes_referencia=request.mes_referencia,
            tipo_recolhimento=request.tipo_recolhimento,
            rescisao=request.rescisao,
        )

        return StandardResponse(
            success=True,
            message="FGTS calculado com sucesso",
            data=resultado,
        )

    except CalculoError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro no calculo: {str(e)}",
        )
    except Exception as e:
        logger.error("Erro ao calcular FGTS: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao calcular FGTS",
        )


@router.post(
    "/inss/calcular",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Calcula INSS",
    description="Calcula INSS com tabela progressiva 2026.",
)
async def calculate_inss(request: CalculoINSSRequest) -> StandardResponse:
    """
    Calcula INSS com tabela progressiva.

    Args:
        request: Dados para cálculo.

    Returns:
        StandardResponse: Cálculo detalhado do INSS.
    """
    try:
        resultado = FGTSINSSService.calcular_inss(
            salario_bruto=request.salario_bruto,
            categoria=request.categoria,
            mes_referencia=request.mes_referencia,
        )

        return StandardResponse(
            success=True,
            message="INSS calculado com sucesso",
            data=resultado,
        )

    except Exception as e:
        logger.error("Erro ao calcular INSS: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao calcular INSS",
        )


@router.get(
    "/inss/tabela",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Tabela INSS vigente",
    description="Retorna tabela progressiva do INSS 2026.",
)
async def get_inss_table() -> StandardResponse:
    """
    Retorna tabela INSS vigente.

    Returns:
        StandardResponse: Tabela progressiva.
    """
    return StandardResponse(
        success=True,
        message="Tabela INSS 2026",
        data=FGTSINSSService.get_tabela_inss(),
    )
