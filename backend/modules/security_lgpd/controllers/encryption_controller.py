"""
Controller de Criptografia LGPD.
"""

import logging

from fastapi import APIRouter, HTTPException, status

from modules.security_lgpd.schemas.common import StandardResponse
from modules.security_lgpd.schemas.encryption import (
    DecryptDataRequest,
    EncryptDataRequest,
)
from modules.security_lgpd.services.encryption_service import EncryptionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/encryption", tags=["LGPD - Criptografia"])


@router.post(
    "/encrypt",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Criptografa dados sensiveis",
    description="Criptografa dados usando AES-256-GCM ou outros algoritmos suportados.",
)
async def encrypt_data(request: EncryptDataRequest) -> StandardResponse:
    """
    Criptografa dados sensiveis usando algoritmo especificado.

    Args:
        request: Dados e configuracoes de criptografia.

    Returns:
        StandardResponse: Dados criptografados em base64.

    Raises:
        HTTPException: Se falhar a criptografia.
    """
    try:
        service = EncryptionService()
        result = service.encrypt(
            data=request.data,
            algorithm=request.algorithm,
            key_id=request.key_id,
        )

        logger.info("Dados criptografados com sucesso usando %s", request.algorithm)

        return StandardResponse(
            success=True,
            message="Dados criptografados com sucesso",
            data=result,
        )

    except ValueError as e:
        logger.warning("Algoritmo invalido: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Algoritmo invalido: {str(e)}",
        )
    except Exception as e:
        logger.error("Erro ao criptografar: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criptografar dados",
        )


@router.post(
    "/decrypt",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Descriptografa dados",
    description="Descriptografa dados previamente criptografados.",
)
async def decrypt_data(request: DecryptDataRequest) -> StandardResponse:
    """
    Descriptografa dados previamente criptografados.

    Args:
        request: Dados criptografados e chave.

    Returns:
        StandardResponse: Dados descriptografados.

    Raises:
        HTTPException: Se falhar a descriptografia.
    """
    try:
        service = EncryptionService()
        result = service.decrypt(
            encrypted_data=request.encrypted_data,
            key_id=request.key_id,
        )

        return StandardResponse(
            success=True,
            message="Descriptografia requer key management configurado",
            data=result,
        )

    except Exception as e:
        logger.error("Erro ao descriptografar: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao descriptografar dados",
        )


@router.get(
    "/algorithms",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista algoritmos de criptografia",
    description="Retorna algoritmos de criptografia disponiveis.",
)
async def list_algorithms() -> StandardResponse:
    """
    Lista algoritmos de criptografia disponiveis.

    Returns:
        StandardResponse: Lista de algoritmos.
    """
    service = EncryptionService()
    algorithms = service.list_algorithms()

    return StandardResponse(
        success=True,
        message="Algoritmos de criptografia disponiveis",
        data={"algorithms": algorithms},
    )
