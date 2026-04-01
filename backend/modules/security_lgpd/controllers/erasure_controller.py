"""
Controller de Exclusao de Dados (Direito ao Esquecimento) LGPD.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Path, status

from core.auth.dependencies import get_current_user
from modules.security_lgpd.schemas.common import StandardResponse
from modules.security_lgpd.schemas.erasure import ErasureRequestSchema
from modules.security_lgpd.services.erasure_service import ErasureService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/erasure", tags=["LGPD - Direito ao Esquecimento"])


@router.post(
    "/request",
    response_model=StandardResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Solicita exclusao de dados (Art. 18 LGPD)",
    description="Inicia processo de exclusao de dados do titular.",
)
async def request_erasure(
    request: ErasureRequestSchema, current_user: dict = Depends(get_current_user)
) -> StandardResponse:
    """
    Solicita exclusao de dados (direito ao esquecimento).
    Args:
        request: Dados da solicitacao.
    Returns:
        StandardResponse: Confirmacao da solicitacao.
    """
    try:
        service = ErasureService()
        result = service.create_request(
            titular_id=str(request.titular_id),
            titular_email=request.titular_email,
            reason=request.reason,
            scope=request.scope,
        )
        logger.info(
            "Solicitacao de exclusao criada: titular=%s, escopo=%s",
            request.titular_id,
            request.scope,
        )
        return StandardResponse(
            success=True,
            message="Solicitacao de exclusao registrada. Processamento em ate 15 dias.",
            data=result,
        )
    except Exception as e:
        logger.error("Erro ao criar solicitacao de exclusao: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar solicitacao",
        )


@router.get(
    "/{request_id}/status",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta status de exclusao",
    description="Verifica status de uma solicitacao de exclusao.",
)
async def get_erasure_status(
    request_id: str = Path(..., description="ID da solicitacao"), current_user: dict = Depends(get_current_user)
) -> StandardResponse:
    """
    Consulta status de solicitacao de exclusao.
    Args:
        request_id: ID da solicitacao.
    Returns:
        StandardResponse: Status atual.
    """
    try:
        service = ErasureService()
        status_info = service.get_status(request_id)
        return StandardResponse(
            success=True,
            message="Status da solicitacao recuperado",
            data=status_info,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitacao nao encontrada",
        )
    except Exception as e:
        logger.error("Erro ao consultar status: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao consultar status",
        )
