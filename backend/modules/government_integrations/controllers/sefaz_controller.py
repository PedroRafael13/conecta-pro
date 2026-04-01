"""
Controller para integrações com SEFAZ (NFe/NFCe).
"""

import logging

from fastapi import APIRouter, HTTPException, Path, status

from core.auth.dependencies import CurrentActiveUser

from ..schemas.common import StandardResponse
from ..schemas.sefaz import NFERequest
from ..services.sefaz_service import SEFAZService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sefaz", tags=["SEFAZ"])


@router.post(
    "/nfe/emitir",
    response_model=StandardResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Emite NFe/NFCe",
    description="Emite Nota Fiscal Eletronica layout 4.00.",
)
async def emit_nfe(current_user: CurrentActiveUser, request: NFERequest) -> StandardResponse:
    """
    Emite NFe ou NFCe.

    Args:
        request: Dados da nota fiscal.

    Returns:
        StandardResponse: Dados da emissão.

    Raises:
        HTTPException: Se falhar a emissão.
    """
    try:
        resultado = SEFAZService.emitir_nfe(
            tipo=request.tipo,
            destinatario=request.destinatario,
            produtos=request.produtos,
            pagamento=request.pagamento,
            observacoes=request.observacoes,
        )

        return StandardResponse(
            success=True,
            message="Nota fiscal enviada para autorizacao",
            data=resultado,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados invalidos: {str(e)}",
        )
    except Exception as e:
        logger.error("Erro ao emitir NFe: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao emitir nota fiscal",
        )


@router.get(
    "/nfe/consultar/{chave_acesso}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta NFe por chave",
    description="Consulta situacao de NFe pela chave de acesso.",
)
async def get_nfe_status(
    current_user: CurrentActiveUser,
    chave_acesso: str = Path(
        ...,
        min_length=44,
        max_length=44,
        description="Chave de acesso (44 digitos)",
    ),
) -> StandardResponse:
    """
    Consulta NFe pela chave de acesso.

    Args:
        chave_acesso: Chave de acesso da NFe.

    Returns:
        StandardResponse: Dados da NFe.
    """
    try:
        resultado = SEFAZService.consultar_nfe(chave_acesso)

        return StandardResponse(
            success=True,
            message="NFe encontrada",
            data=resultado,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NFe nao encontrada",
        )
    except Exception as e:
        logger.error("Erro ao consultar NFe: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao consultar NFe",
        )
