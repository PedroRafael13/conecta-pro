"""
Controller REST para Simples Nacional.

Endpoints para cálculos e operações do Simples Nacional.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends

from ..schemas.common import StandardResponse
from ..schemas.simples_nacional import (
    SimularCalculoRequest,
    CalcularPGDASDRequest,
    GerarDASRequest,
    CalcularFatorRRequest,
)
from ..services.simples_nacional_service import (
    SimplesNacionalService,
    get_simples_nacional_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simples-nacional", tags=["Simples Nacional"])


def get_service() -> SimplesNacionalService:
    """Dependency para obter o service."""
    return get_simples_nacional_service()


@router.get(
    "/status",
    response_model=StandardResponse,
    summary="Status do Simples Nacional",
    description="Retorna o status da configuração"
)
async def get_status(
    service: SimplesNacionalService = Depends(get_service)
) -> StandardResponse:
    """Retorna status da configuração."""
    try:
        status_data = service.validar_status()

        return StandardResponse(
            success=True,
            message="Status Simples Nacional obtido",
            data=status_data
        )

    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.get(
    "/opcao",
    response_model=StandardResponse,
    summary="Consultar opção",
    description="Consulta a situação da opção pelo Simples Nacional"
)
async def consultar_opcao(
    service: SimplesNacionalService = Depends(get_service)
) -> StandardResponse:
    """Consulta situação da opção."""
    try:
        resultado = service.consultar_opcao()

        return StandardResponse(
            success=True,
            message="Opção consultada",
            data=resultado
        )

    except Exception as e:
        logger.error(f"Erro ao consultar opção: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.get(
    "/anexos",
    response_model=StandardResponse,
    summary="Lista anexos",
    description="Retorna a lista de anexos do Simples Nacional"
)
async def listar_anexos(
    service: SimplesNacionalService = Depends(get_service)
) -> StandardResponse:
    """Lista anexos disponíveis."""
    try:
        anexos = service.listar_anexos()

        return StandardResponse(
            success=True,
            message="Anexos listados",
            data=anexos
        )

    except Exception as e:
        logger.error(f"Erro ao listar anexos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.get(
    "/tipos-receita",
    response_model=StandardResponse,
    summary="Lista tipos de receita",
    description="Retorna a lista de tipos de receita"
)
async def listar_tipos_receita(
    service: SimplesNacionalService = Depends(get_service)
) -> StandardResponse:
    """Lista tipos de receita."""
    try:
        tipos = service.listar_tipos_receita()

        return StandardResponse(
            success=True,
            message="Tipos de receita listados",
            data=tipos
        )

    except Exception as e:
        logger.error(f"Erro ao listar tipos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.get(
    "/tabela-aliquotas/{anexo}",
    response_model=StandardResponse,
    summary="Tabela de alíquotas",
    description="Retorna a tabela de alíquotas de um anexo"
)
async def obter_tabela_aliquotas(
    anexo: str,
    service: SimplesNacionalService = Depends(get_service)
) -> StandardResponse:
    """Retorna tabela de alíquotas."""
    try:
        if anexo not in ["I", "II", "III", "IV", "V"]:
            raise ValueError(f"Anexo inválido: {anexo}")

        tabela = service.obter_tabela_aliquotas(anexo)

        return StandardResponse(
            success=True,
            message=f"Tabela do Anexo {anexo}",
            data=tabela
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao obter tabela: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.get(
    "/pendencias",
    response_model=StandardResponse,
    summary="Consultar pendências",
    description="Consulta pendências no Simples Nacional"
)
async def consultar_pendencias(
    service: SimplesNacionalService = Depends(get_service)
) -> StandardResponse:
    """Consulta pendências."""
    try:
        pendencias = service.consultar_pendencias()

        return StandardResponse(
            success=True,
            message="Pendências consultadas",
            data=pendencias
        )

    except Exception as e:
        logger.error(f"Erro ao consultar pendências: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.post(
    "/simular",
    response_model=StandardResponse,
    summary="Simular cálculo",
    description="Simula o cálculo do Simples Nacional"
)
async def simular_calculo(
    request: SimularCalculoRequest,
    service: SimplesNacionalService = Depends(get_service)
) -> StandardResponse:
    """Simula cálculo do Simples."""
    try:
        resultado = service.simular_calculo(
            receita_mensal=str(request.receita_mensal),
            rbt12=str(request.rbt12),
            folha_12_meses=str(request.folha_12_meses) if request.folha_12_meses else None,
        )

        return StandardResponse(
            success=True,
            message="Simulação realizada",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro na simulação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.post(
    "/fator-r",
    response_model=StandardResponse,
    summary="Calcular Fator R",
    description="Calcula o Fator R e determina o anexo aplicável"
)
async def calcular_fator_r(
    request: CalcularFatorRRequest,
    service: SimplesNacionalService = Depends(get_service)
) -> StandardResponse:
    """Calcula Fator R."""
    try:
        resultado = service.calcular_fator_r(
            folha_12_meses=str(request.folha_12_meses),
            rbt12=str(request.rbt12),
        )

        return StandardResponse(
            success=True,
            message="Fator R calculado",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro no cálculo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.post(
    "/pgdasd",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Calcular PGDAS-D",
    description="Calcula o PGDAS-D (declaração mensal)"
)
async def calcular_pgdasd(
    request: CalcularPGDASDRequest,
    service: SimplesNacionalService = Depends(get_service)
) -> StandardResponse:
    """Calcula PGDAS-D."""
    try:
        receitas = [r.model_dump() for r in request.receitas]

        resultado = service.calcular_pgdasd(
            competencia=request.competencia,
            receitas=receitas,
            rbt12=str(request.rbt12),
            folha_12_meses=str(request.folha_12_meses) if request.folha_12_meses else None,
        )

        return StandardResponse(
            success=True,
            message=f"PGDAS-D calculado: R$ {resultado['valor_devido']}",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro no cálculo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.post(
    "/das",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar DAS",
    description="Gera o DAS (guia de pagamento)"
)
async def gerar_das(
    request: GerarDASRequest,
    service: SimplesNacionalService = Depends(get_service)
) -> StandardResponse:
    """Gera DAS."""
    try:
        receitas = [r.model_dump() for r in request.receitas]

        resultado = service.gerar_das(
            competencia=request.competencia,
            receitas=receitas,
            rbt12=str(request.rbt12),
            folha_12_meses=str(request.folha_12_meses) if request.folha_12_meses else None,
            data_vencimento=request.data_vencimento,
        )

        return StandardResponse(
            success=True,
            message=f"DAS gerado: R$ {resultado['das']['valor_total']}",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro na geração: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )
