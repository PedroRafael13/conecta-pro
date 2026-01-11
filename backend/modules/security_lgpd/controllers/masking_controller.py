"""
Controller de Mascaramento LGPD.
"""

import logging

from fastapi import APIRouter, HTTPException, status

from modules.security_lgpd.schemas.common import StandardResponse
from modules.security_lgpd.schemas.masking import MaskDataRequest
from modules.security_lgpd.services.masking_service import MaskingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/masking", tags=["LGPD - Mascaramento"])


@router.post(
    "/mask",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Mascara dados sensiveis",
    description="Aplica mascaramento em dados PII (CPF, email, telefone, etc).",
)
async def mask_data(request: MaskDataRequest) -> StandardResponse:
    """
    Mascara dados sensiveis de acordo com categoria.

    Args:
        request: Dados e configuracoes de mascaramento.

    Returns:
        StandardResponse: Dado mascarado.

    Raises:
        HTTPException: Se falhar o mascaramento.
    """
    try:
        service = MaskingService()
        result = service.mask(
            data=request.data,
            category=request.category,
            level=request.level,
        )

        logger.info(
            "Dado mascarado: categoria=%s, nivel=%s",
            request.category,
            request.level,
        )

        return StandardResponse(
            success=True,
            message="Dado mascarado com sucesso",
            data=result,
        )

    except ValueError as e:
        logger.warning("Erro de validacao no mascaramento: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de validacao: {str(e)}",
        )
    except Exception as e:
        logger.error("Erro ao mascarar dados: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao mascarar dados",
        )


@router.get(
    "/formats",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista formatos de mascaramento",
    description="Retorna categorias e niveis de mascaramento disponiveis.",
)
async def list_masking_formats() -> StandardResponse:
    """
    Lista formatos de mascaramento disponiveis.

    Returns:
        StandardResponse: Categorias e niveis disponiveis.
    """
    service = MaskingService()
    formats = service.get_formats()

    return StandardResponse(
        success=True,
        message="Formatos de mascaramento disponiveis",
        data=formats,
    )
