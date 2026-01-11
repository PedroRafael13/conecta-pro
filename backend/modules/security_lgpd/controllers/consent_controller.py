"""
Controller de Consentimento LGPD.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Query, status

from modules.security_lgpd.schemas.common import StandardResponse
from modules.security_lgpd.schemas.consent import ConsentRequest
from modules.security_lgpd.services.consent_service import ConsentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/consent", tags=["LGPD - Consentimento"])


@router.post(
    "/register",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra consentimento LGPD",
    description="Registra consentimento do titular conforme Art. 7 LGPD.",
)
async def register_consent(request: ConsentRequest) -> StandardResponse:
    """
    Registra consentimento de titular de dados.

    Args:
        request: Dados do consentimento.

    Returns:
        StandardResponse: Confirmacao do registro.

    Raises:
        HTTPException: Se falhar o registro.
    """
    try:
        service = ConsentService()
        result = service.register_consent(
            titular_id=str(request.titular_id),
            titular_email=request.titular_email,
            purpose=request.purpose,
            legal_basis=request.legal_basis,
            description=request.description,
            expiration_days=request.expiration_days,
        )

        logger.info(
            "Consentimento registrado: titular=%s, finalidade=%s",
            request.titular_id,
            request.purpose,
        )

        return StandardResponse(
            success=True,
            message="Consentimento registrado com sucesso",
            data=result,
        )

    except ValueError as e:
        logger.warning("Erro de validacao no consentimento: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de validacao: {str(e)}",
        )
    except Exception as e:
        logger.error("Erro ao registrar consentimento: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao registrar consentimento",
        )


@router.get(
    "/{titular_id}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta consentimentos de titular",
    description="Retorna todos os consentimentos de um titular.",
)
async def get_consents(
    titular_id: UUID = Path(..., description="UUID do titular"),
) -> StandardResponse:
    """
    Consulta consentimentos de um titular.

    Args:
        titular_id: UUID do titular.

    Returns:
        StandardResponse: Lista de consentimentos.
    """
    try:
        service = ConsentService()
        result = service.get_consents_by_titular(str(titular_id))

        return StandardResponse(
            success=True,
            message=f"Encontrados {result['total']} consentimentos",
            data=result,
        )

    except Exception as e:
        logger.error("Erro ao consultar consentimentos: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao consultar consentimentos",
        )


@router.delete(
    "/{consent_id}/revoke",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoga consentimento",
    description="Revoga um consentimento especifico.",
)
async def revoke_consent(
    consent_id: str = Path(..., description="ID do consentimento"),
    reason: str = Query(..., min_length=5, description="Motivo da revogacao"),
) -> StandardResponse:
    """
    Revoga um consentimento.

    Args:
        consent_id: ID do consentimento.
        reason: Motivo da revogacao.

    Returns:
        StandardResponse: Confirmacao da revogacao.
    """
    try:
        service = ConsentService()
        result = service.revoke_consent(consent_id, reason)

        logger.info("Consentimento revogado: %s", consent_id)

        return StandardResponse(
            success=True,
            message="Consentimento revogado com sucesso",
            data=result,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consentimento nao encontrado: {str(e)}",
        )
    except Exception as e:
        logger.error("Erro ao revogar consentimento: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao revogar consentimento",
        )


@router.get(
    "/purposes/list",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista finalidades de consentimento",
    description="Retorna finalidades de consentimento disponiveis.",
)
async def list_purposes() -> StandardResponse:
    """
    Lista finalidades de consentimento disponiveis.

    Returns:
        StandardResponse: Lista de finalidades.
    """
    service = ConsentService()
    purposes = service.list_purposes()

    return StandardResponse(
        success=True,
        message="Finalidades de consentimento disponiveis",
        data={"purposes": purposes},
    )


@router.get(
    "/legal-bases/list",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista bases legais LGPD",
    description="Retorna bases legais LGPD disponiveis.",
)
async def list_legal_bases() -> StandardResponse:
    """
    Lista bases legais LGPD disponiveis.

    Returns:
        StandardResponse: Lista de bases legais.
    """
    service = ConsentService()
    bases = service.list_legal_bases()

    return StandardResponse(
        success=True,
        message="Bases legais LGPD disponiveis",
        data={"legal_bases": bases},
    )
