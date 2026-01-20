"""
Controller REST para DCTFWeb.

Endpoints para geração e transmissão de DCTFWeb.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends

from ..schemas.common import StandardResponse
from ..schemas.dctfweb import (
    CriarDeclaracaoRequest,
    ImportarESocialRequest,
    ImportarReinfRequest,
    ConsolidarDeclaracaoRequest,
    GerarDarfsRequest,
    TransmitirDeclaracaoRequest,
)
from ..services.dctfweb_service import DCTFWebService, get_dctfweb_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dctfweb", tags=["DCTFWeb"])


def get_service() -> DCTFWebService:
    """Dependency para obter o service."""
    return get_dctfweb_service()


@router.get(
    "/status",
    response_model=StandardResponse,
    summary="Status do DCTFWeb",
    description="Retorna o status da configuração DCTFWeb"
)
async def get_status(
    service: DCTFWebService = Depends(get_service)
) -> StandardResponse:
    """Retorna status da configuração."""
    try:
        status_data = service.validar_status()

        return StandardResponse(
            success=True,
            message="Status DCTFWeb obtido com sucesso",
            data=status_data
        )

    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter status: {str(e)}"
        )


@router.get(
    "/codigos-receita",
    response_model=StandardResponse,
    summary="Lista códigos de receita",
    description="Retorna a lista de códigos de receita disponíveis"
)
async def listar_codigos_receita(
    service: DCTFWebService = Depends(get_service)
) -> StandardResponse:
    """Lista códigos de receita."""
    try:
        codigos = service.listar_codigos_receita()

        return StandardResponse(
            success=True,
            message="Códigos de receita listados",
            data=codigos
        )

    except Exception as e:
        logger.error(f"Erro ao listar códigos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.get(
    "/tipos-declaracao",
    response_model=StandardResponse,
    summary="Lista tipos de declaração",
    description="Retorna a lista de tipos de declaração DCTFWeb"
)
async def listar_tipos_declaracao(
    service: DCTFWebService = Depends(get_service)
) -> StandardResponse:
    """Lista tipos de declaração."""
    try:
        tipos = service.listar_tipos_declaracao()

        return StandardResponse(
            success=True,
            message="Tipos de declaração listados",
            data=tipos
        )

    except Exception as e:
        logger.error(f"Erro ao listar tipos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.get(
    "/tipos-credito",
    response_model=StandardResponse,
    summary="Lista tipos de crédito",
    description="Retorna a lista de tipos de crédito vinculáveis"
)
async def listar_tipos_credito(
    service: DCTFWebService = Depends(get_service)
) -> StandardResponse:
    """Lista tipos de crédito."""
    try:
        tipos = service.listar_tipos_credito()

        return StandardResponse(
            success=True,
            message="Tipos de crédito listados",
            data=tipos
        )

    except Exception as e:
        logger.error(f"Erro ao listar tipos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.post(
    "/criar",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar declaração",
    description="Cria uma nova declaração DCTFWeb"
)
async def criar_declaracao(
    request: CriarDeclaracaoRequest,
    service: DCTFWebService = Depends(get_service)
) -> StandardResponse:
    """Cria nova declaração."""
    try:
        resultado = service.criar_declaracao(
            periodo_apuracao=request.periodo_apuracao,
            tipo=request.tipo.value,
        )

        return StandardResponse(
            success=True,
            message=f"DCTFWeb criada para período {request.periodo_apuracao}",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao criar declaração: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.post(
    "/importar-esocial",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Importar eSocial",
    description="Cria declaração e importa dados do eSocial"
)
async def importar_esocial(
    request: ImportarESocialRequest,
    service: DCTFWebService = Depends(get_service)
) -> StandardResponse:
    """Importa dados do eSocial."""
    try:
        dados = request.dados_esocial.model_dump(exclude_none=True)

        resultado = service.importar_esocial(
            periodo_apuracao=request.periodo_apuracao,
            dados_esocial=dados,
        )

        return StandardResponse(
            success=True,
            message="Dados eSocial importados para DCTFWeb",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao importar eSocial: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.post(
    "/importar-reinf",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Importar EFD-Reinf",
    description="Cria declaração e importa dados da EFD-Reinf"
)
async def importar_reinf(
    request: ImportarReinfRequest,
    service: DCTFWebService = Depends(get_service)
) -> StandardResponse:
    """Importa dados da EFD-Reinf."""
    try:
        dados = request.dados_reinf.model_dump(exclude_none=True)

        # Converte retencoes para formato esperado
        if "retencoes_tomados" in dados:
            dados["retencoes_tomados"] = [
                r for r in dados["retencoes_tomados"]
            ]

        resultado = service.importar_reinf(
            periodo_apuracao=request.periodo_apuracao,
            dados_reinf=dados,
        )

        return StandardResponse(
            success=True,
            message="Dados EFD-Reinf importados para DCTFWeb",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao importar EFD-Reinf: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.post(
    "/consolidar",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Consolidar declaração",
    description="Consolida declaração com dados do eSocial e EFD-Reinf"
)
async def consolidar_declaracao(
    request: ConsolidarDeclaracaoRequest,
    service: DCTFWebService = Depends(get_service)
) -> StandardResponse:
    """Consolida declaração."""
    try:
        dados_esocial = (
            request.dados_esocial.model_dump(exclude_none=True)
            if request.dados_esocial else None
        )
        dados_reinf = (
            request.dados_reinf.model_dump(exclude_none=True)
            if request.dados_reinf else None
        )

        resultado = service.consolidar_declaracao(
            periodo_apuracao=request.periodo_apuracao,
            dados_esocial=dados_esocial,
            dados_reinf=dados_reinf,
        )

        return StandardResponse(
            success=True,
            message="DCTFWeb consolidada com sucesso",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao consolidar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.post(
    "/gerar-darfs",
    response_model=StandardResponse,
    summary="Gerar DARFs",
    description="Gera DARFs para a declaração"
)
async def gerar_darfs(
    request: GerarDarfsRequest,
    service: DCTFWebService = Depends(get_service)
) -> StandardResponse:
    """Gera DARFs."""
    try:
        dados_esocial = (
            request.dados_esocial.model_dump(exclude_none=True)
            if request.dados_esocial else None
        )
        dados_reinf = (
            request.dados_reinf.model_dump(exclude_none=True)
            if request.dados_reinf else None
        )

        resultado = service.gerar_darfs(
            periodo_apuracao=request.periodo_apuracao,
            dados_esocial=dados_esocial,
            dados_reinf=dados_reinf,
            data_vencimento=request.data_vencimento,
        )

        return StandardResponse(
            success=True,
            message=f"Gerados {resultado['quantidade_darfs']} DARFs",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao gerar DARFs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.post(
    "/transmitir",
    response_model=StandardResponse,
    summary="Transmitir declaração",
    description="Transmite a declaração DCTFWeb"
)
async def transmitir_declaracao(
    request: TransmitirDeclaracaoRequest,
    service: DCTFWebService = Depends(get_service)
) -> StandardResponse:
    """Transmite declaração."""
    try:
        dados_esocial = (
            request.dados_esocial.model_dump(exclude_none=True)
            if request.dados_esocial else None
        )
        dados_reinf = (
            request.dados_reinf.model_dump(exclude_none=True)
            if request.dados_reinf else None
        )

        resultado = service.transmitir(
            periodo_apuracao=request.periodo_apuracao,
            dados_esocial=dados_esocial,
            dados_reinf=dados_reinf,
        )

        return StandardResponse(
            success=True,
            message=f"DCTFWeb transmitida: {resultado['numero_recibo']}",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao transmitir: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.get(
    "/consultar/{periodo_apuracao}",
    response_model=StandardResponse,
    summary="Consultar declaração",
    description="Consulta declaração DCTFWeb por período"
)
async def consultar_declaracao(
    periodo_apuracao: str,
    service: DCTFWebService = Depends(get_service)
) -> StandardResponse:
    """Consulta declaração por período."""
    try:
        resultado = service.consultar(periodo_apuracao)

        return StandardResponse(
            success=True,
            message=f"Consulta período {periodo_apuracao}",
            data=resultado
        )

    except Exception as e:
        logger.error(f"Erro ao consultar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )
