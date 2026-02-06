"""
Controller para integrações com Receita Federal.
"""

import logging

from fastapi import APIRouter, HTTPException, status

from ..schemas.common import StandardResponse
from ..schemas.receita_federal import (
    ConsultaCNPJRequest,
    ConsultaCPFRequest,
    ValidateDocumentRequest,
)
from ..services.receita_federal_service import ReceitaFederalApiService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/receita", tags=["Receita Federal"])


@router.post(
    "/validar-documento",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Valida CPF ou CNPJ",
    description="Valida se documento esta correto (digitos verificadores).",
)
async def validate_document(request: ValidateDocumentRequest) -> StandardResponse:
    """
    Valida CPF ou CNPJ.

    Args:
        request: Dados do documento.

    Returns:
        StandardResponse: Resultado da validação.
    """
    try:
        resultado = ReceitaFederalApiService.validar_documento(
            documento=request.documento,
            tipo=request.tipo,
        )

        return StandardResponse(
            success=True,
            message=f"{request.tipo.upper()} {'valido' if resultado['valido'] else 'invalido'}",
            data=resultado,
        )

    except Exception as e:
        logger.error("Erro ao validar documento: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao validar documento",
        )


@router.post(
    "/consultar-cpf",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta situacao cadastral de CPF",
    description="Consulta situacao cadastral de CPF na Receita Federal.",
)
async def consult_cpf(request: ConsultaCPFRequest) -> StandardResponse:
    """
    Consulta CPF na Receita Federal.

    Args:
        request: Dados para consulta.

    Returns:
        StandardResponse: Dados do CPF.

    Raises:
        HTTPException: Se falhar a consulta.
    """
    try:
        resultado = ReceitaFederalApiService.consultar_cpf(
            cpf=request.cpf,
            data_nascimento=request.data_nascimento,
        )

        return StandardResponse(
            success=True,
            message="Consulta realizada com sucesso",
            data=resultado,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Erro ao consultar CPF: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao consultar CPF",
        )


@router.post(
    "/consultar-cnpj",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta CNPJ na Receita Federal",
    description="Retorna dados cadastrais completos do CNPJ.",
)
async def consult_cnpj(request: ConsultaCNPJRequest) -> StandardResponse:
    """
    Consulta CNPJ na Receita Federal.

    Args:
        request: Dados para consulta.

    Returns:
        StandardResponse: Dados do CNPJ.

    Raises:
        HTTPException: Se falhar a consulta.
    """
    try:
        resultado = ReceitaFederalApiService.consultar_cnpj(cnpj=request.cnpj)

        return StandardResponse(
            success=True,
            message="Consulta realizada com sucesso",
            data=resultado,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Erro ao consultar CNPJ: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao consultar CNPJ",
        )
