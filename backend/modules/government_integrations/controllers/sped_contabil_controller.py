"""
Controller REST para SPED Contábil (ECD).

Endpoints para operações do SPED Contábil.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import PlainTextResponse

from ..schemas.common import StandardResponse
from ..schemas.sped_contabil import (
    GerarArquivoRequest,
    CalcularSaldosRequest,
    AdicionarContaRequest,
    AdicionarLancamentoRequest,
    DefinirBalancoRequest,
    DefinirDRERequest,
)
from ..services.sped_contabil_service import (
    SPEDContabilService,
    get_sped_contabil_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sped-contabil", tags=["SPED Contabil"])


def get_service() -> SPEDContabilService:
    """Dependency para obter o service."""
    return get_sped_contabil_service()


@router.get(
    "/status",
    response_model=StandardResponse,
    summary="Status do SPED Contábil",
    description="Retorna o status da configuração do SPED Contábil"
)
async def get_status(
    service: SPEDContabilService = Depends(get_service)
) -> StandardResponse:
    """Retorna status da configuração."""
    try:
        status_data = service.validar_status()

        return StandardResponse(
            success=True,
            message="Status SPED Contábil obtido",
            data=status_data
        )

    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.get(
    "/blocos",
    response_model=StandardResponse,
    summary="Lista blocos",
    description="Retorna a lista de blocos do SPED Contábil"
)
async def listar_blocos(
    service: SPEDContabilService = Depends(get_service)
) -> StandardResponse:
    """Lista blocos do SPED."""
    try:
        blocos = service.listar_blocos()

        return StandardResponse(
            success=True,
            message="Blocos listados",
            data=blocos
        )

    except Exception as e:
        logger.error(f"Erro ao listar blocos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.get(
    "/tipos-ecd",
    response_model=StandardResponse,
    summary="Lista tipos de ECD",
    description="Retorna a lista de tipos de livros ECD"
)
async def listar_tipos_ecd(
    service: SPEDContabilService = Depends(get_service)
) -> StandardResponse:
    """Lista tipos de ECD."""
    try:
        tipos = service.listar_tipos_ecd()

        return StandardResponse(
            success=True,
            message="Tipos listados",
            data=tipos
        )

    except Exception as e:
        logger.error(f"Erro ao listar tipos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.get(
    "/contas",
    response_model=StandardResponse,
    summary="Lista contas",
    description="Retorna a lista de contas do plano de contas"
)
async def listar_contas(
    service: SPEDContabilService = Depends(get_service)
) -> StandardResponse:
    """Lista contas."""
    try:
        contas = service.listar_contas()

        return StandardResponse(
            success=True,
            message=f"{len(contas['contas'])} contas",
            data=contas
        )

    except Exception as e:
        logger.error(f"Erro ao listar contas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.get(
    "/lancamentos",
    response_model=StandardResponse,
    summary="Lista lançamentos",
    description="Retorna a lista de lançamentos contábeis"
)
async def listar_lancamentos(
    service: SPEDContabilService = Depends(get_service)
) -> StandardResponse:
    """Lista lançamentos."""
    try:
        lancamentos = service.listar_lancamentos()

        return StandardResponse(
            success=True,
            message=f"{len(lancamentos['lancamentos'])} lançamentos",
            data=lancamentos
        )

    except Exception as e:
        logger.error(f"Erro ao listar lançamentos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.post(
    "/conta",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar conta",
    description="Adiciona uma conta ao plano de contas"
)
async def adicionar_conta(
    request: AdicionarContaRequest,
    service: SPEDContabilService = Depends(get_service)
) -> StandardResponse:
    """Adiciona conta."""
    try:
        resultado = service.adicionar_conta(request.conta.model_dump())

        return StandardResponse(
            success=True,
            message=f"Conta {resultado['codigo']} adicionada",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao adicionar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.post(
    "/lancamento",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar lançamento",
    description="Adiciona um lançamento contábil"
)
async def adicionar_lancamento(
    request: AdicionarLancamentoRequest,
    service: SPEDContabilService = Depends(get_service)
) -> StandardResponse:
    """Adiciona lançamento."""
    try:
        resultado = service.adicionar_lancamento(request.lancamento.model_dump())

        return StandardResponse(
            success=True,
            message=f"Lançamento {resultado['numero']} adicionado",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao adicionar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.post(
    "/balanco",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Definir balanço",
    description="Define o balanço patrimonial"
)
async def definir_balanco(
    request: DefinirBalancoRequest,
    service: SPEDContabilService = Depends(get_service)
) -> StandardResponse:
    """Define balanço."""
    try:
        resultado = service.definir_balanco(request.balanco.model_dump())

        return StandardResponse(
            success=True,
            message=f"Balanço definido: Ativo R$ {resultado['total_ativo']}",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao definir: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.post(
    "/dre",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Definir DRE",
    description="Define a Demonstração do Resultado do Exercício"
)
async def definir_dre(
    request: DefinirDRERequest,
    service: SPEDContabilService = Depends(get_service)
) -> StandardResponse:
    """Define DRE."""
    try:
        resultado = service.definir_dre(request.dre.model_dump())

        return StandardResponse(
            success=True,
            message=f"DRE definida: Lucro R$ {resultado['lucro_liquido']}",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao definir: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.post(
    "/saldos",
    response_model=StandardResponse,
    summary="Calcular saldos",
    description="Calcula os saldos periódicos das contas"
)
async def calcular_saldos(
    request: CalcularSaldosRequest,
    service: SPEDContabilService = Depends(get_service)
) -> StandardResponse:
    """Calcula saldos."""
    try:
        resultado = service.calcular_saldos(
            periodo_inicio=request.periodo_inicio,
            periodo_fim=request.periodo_fim,
        )

        return StandardResponse(
            success=True,
            message=f"Saldos calculados: {resultado['total_contas']} contas",
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
    "/gerar",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar arquivo SPED",
    description="Gera o arquivo SPED Contábil"
)
async def gerar_arquivo(
    request: GerarArquivoRequest,
    service: SPEDContabilService = Depends(get_service)
) -> StandardResponse:
    """Gera arquivo SPED."""
    try:
        contas = [c.model_dump() for c in request.contas] if request.contas else None
        lancamentos = [l.model_dump() for l in request.lancamentos] if request.lancamentos else None
        balanco = request.balanco.model_dump() if request.balanco else None
        dre = request.dre.model_dump() if request.dre else None

        resultado = service.gerar_arquivo(
            ano_referencia=request.ano_referencia,
            periodo_inicio=request.periodo_inicio,
            periodo_fim=request.periodo_fim,
            numero_ordem=request.numero_ordem,
            contas=contas,
            lancamentos=lancamentos,
            balanco=balanco,
            dre=dre,
        )

        return StandardResponse(
            success=True,
            message=f"Arquivo gerado: {resultado['total_registros']} registros",
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


@router.post(
    "/gerar/download",
    response_class=PlainTextResponse,
    summary="Download arquivo SPED",
    description="Gera e retorna o arquivo SPED para download"
)
async def gerar_arquivo_download(
    request: GerarArquivoRequest,
    service: SPEDContabilService = Depends(get_service)
) -> PlainTextResponse:
    """Gera arquivo SPED para download."""
    try:
        contas = [c.model_dump() for c in request.contas] if request.contas else None
        lancamentos = [l.model_dump() for l in request.lancamentos] if request.lancamentos else None
        balanco = request.balanco.model_dump() if request.balanco else None
        dre = request.dre.model_dump() if request.dre else None

        resultado = service.gerar_arquivo(
            ano_referencia=request.ano_referencia,
            periodo_inicio=request.periodo_inicio,
            periodo_fim=request.periodo_fim,
            numero_ordem=request.numero_ordem,
            contas=contas,
            lancamentos=lancamentos,
            balanco=balanco,
            dre=dre,
        )

        filename = f"ECD_{request.ano_referencia}.txt"

        return PlainTextResponse(
            content=resultado["conteudo"],
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        logger.error(f"Erro no download: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


@router.delete(
    "/limpar",
    response_model=StandardResponse,
    summary="Limpar dados",
    description="Limpa todos os dados em memória"
)
async def limpar_dados(
    service: SPEDContabilService = Depends(get_service)
) -> StandardResponse:
    """Limpa dados em memória."""
    try:
        resultado = service.limpar_dados()

        return StandardResponse(
            success=True,
            message="Dados limpos",
            data=resultado
        )

    except Exception as e:
        logger.error(f"Erro ao limpar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )
