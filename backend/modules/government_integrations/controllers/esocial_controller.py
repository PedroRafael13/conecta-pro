"""
Controller para integrações com eSocial.
"""

import logging

from fastapi import APIRouter, HTTPException, Path, status

from ..schemas.common import StandardResponse
from ..schemas.esocial import ESocialEventRequest
from ..services.esocial_service import ESocialService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/esocial", tags=["eSocial"])


@router.post(
    "/evento",
    response_model=StandardResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Envia evento eSocial",
    description="Transmite evento para o eSocial (S-2200, S-2299, S-2220, etc).",
)
async def send_esocial_event(request: ESocialEventRequest) -> StandardResponse:
    """
    Envia evento para o eSocial.

    Args:
        request: Dados do evento.

    Returns:
        StandardResponse: Protocolo de transmissão.

    Raises:
        HTTPException: Se falhar a transmissão.
    """
    try:
        resultado = ESocialService.enviar_evento(
            tipo_evento=request.tipo_evento,
            funcionario_id=str(request.funcionario_id),
            dados=request.dados,
            ambiente=request.ambiente,
        )

        return StandardResponse(
            success=True,
            message="Evento eSocial enviado para processamento",
            data=resultado,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados invalidos: {str(e)}",
        )
    except Exception as e:
        logger.error("Erro ao enviar evento eSocial: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao enviar evento",
        )


@router.get(
    "/consultar/{protocolo}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta status de evento eSocial",
    description="Consulta status de processamento de evento pelo protocolo.",
)
async def get_esocial_status(
    protocolo: str = Path(..., min_length=5, description="Protocolo do evento"),
) -> StandardResponse:
    """
    Consulta status de evento eSocial.

    Args:
        protocolo: Protocolo de transmissão.

    Returns:
        StandardResponse: Status do evento.
    """
    try:
        resultado = ESocialService.consultar_status(protocolo)

        return StandardResponse(
            success=True,
            message="Status recuperado",
            data=resultado,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protocolo nao encontrado",
        )
    except Exception as e:
        logger.error("Erro ao consultar status: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao consultar status",
        )


@router.get(
    "/eventos-suportados",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista eventos eSocial suportados",
    description="Retorna lista de eventos eSocial que o sistema suporta.",
)
async def list_esocial_events() -> StandardResponse:
    """
    Lista eventos eSocial suportados.

    Returns:
        StandardResponse: Lista de eventos.
    """
    return StandardResponse(
        success=True,
        message="Eventos eSocial suportados",
        data=ESocialService.listar_eventos_suportados(),
    )
