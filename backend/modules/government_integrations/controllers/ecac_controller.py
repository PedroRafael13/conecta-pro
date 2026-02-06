"""
Controller REST para e-CAC - Centro Virtual de Atendimento ao Contribuinte.

Endpoints para acesso aos servicos do e-CAC da Receita Federal.
"""

import logging
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import JSONResponse

from ..schemas.common import StandardResponse
from ..schemas.ecac import (
    ConsultaSituacaoFiscalRequest,
    ConsultaDebitosRequest,
    ConsultaDeclaracoesRequest,
    EmitirCertidaoRequest,
    ValidarCertidaoRequest,
    ConsultaParcelamentosRequest,
    SimularParcelamentoRequest,
    ConsultaProcessosRequest,
    SituacaoFiscalResponse,
    CertidaoResponse,
    ValidacaoCertidaoResponse,
    DeclaracaoResponse,
    ParcelamentoResponse,
    SimulacaoParcelamentoResponse,
    ProcessoResponse,
    DebitoFiscalResponse,
    StatusEcacResponse,
    TipoDeclaracaoEnum,
    SituacaoDebitoEnum,
    SituacaoProcessoEnum,
)
from ..services.ecac_service import EcacService, get_ecac_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ecac", tags=["e-CAC"])


def get_service() -> EcacService:
    """Dependency para obter o service."""
    return get_ecac_service()


@router.get(
    "/status",
    response_model=StandardResponse,
    summary="Status do e-CAC",
    description="Retorna o status da configuracao e conexao do e-CAC"
)
async def get_status(
    service: EcacService = Depends(get_service)
) -> StandardResponse:
    """Retorna status da configuracao e-CAC."""
    try:
        status_data = service.validar_status()

        return StandardResponse(
            success=True,
            message="Status e-CAC obtido com sucesso",
            data=status_data
        )

    except Exception as e:
        logger.error(f"Erro ao obter status e-CAC: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter status: {str(e)}"
        )


@router.get(
    "/situacao-fiscal",
    response_model=StandardResponse,
    summary="Consulta situacao fiscal",
    description="Consulta a situacao fiscal do contribuinte no e-CAC"
)
async def consultar_situacao_fiscal(
    cpf_cnpj: Optional[str] = Query(
        None,
        description="CPF ou CNPJ (opcional, usa o configurado)"
    ),
    service: EcacService = Depends(get_service)
) -> StandardResponse:
    """Consulta situacao fiscal do contribuinte."""
    try:
        # Limpa formatacao se fornecido
        if cpf_cnpj:
            cpf_cnpj = cpf_cnpj.replace(".", "").replace("/", "").replace("-", "")

        resultado = service.consultar_situacao_fiscal(cpf_cnpj=cpf_cnpj)

        return StandardResponse(
            success=True,
            message="Situacao fiscal consultada com sucesso",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao situacao fiscal: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao consultar situacao fiscal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar situacao fiscal: {str(e)}"
        )


@router.get(
    "/debitos",
    response_model=StandardResponse,
    summary="Consulta debitos",
    description="Consulta debitos fiscais do contribuinte"
)
async def consultar_debitos(
    situacao: Optional[SituacaoDebitoEnum] = Query(
        None,
        description="Filtro por situacao do debito"
    ),
    competencia_inicio: Optional[str] = Query(
        None,
        pattern=r"^\d{4}-\d{2}$",
        description="Competencia inicial (YYYY-MM)"
    ),
    competencia_fim: Optional[str] = Query(
        None,
        pattern=r"^\d{4}-\d{2}$",
        description="Competencia final (YYYY-MM)"
    ),
    service: EcacService = Depends(get_service)
) -> StandardResponse:
    """Consulta debitos fiscais."""
    try:
        resultado = service.consultar_debitos(
            situacao=situacao.value if situacao else None,
            competencia_inicio=competencia_inicio,
            competencia_fim=competencia_fim,
        )

        return StandardResponse(
            success=True,
            message=f"Debitos consultados: {resultado['quantidade']} encontrados",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao consulta debitos: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao consultar debitos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar debitos: {str(e)}"
        )


@router.get(
    "/declaracoes",
    response_model=StandardResponse,
    summary="Consulta declaracoes",
    description="Consulta declaracoes transmitidas no e-CAC"
)
async def consultar_declaracoes(
    tipo: TipoDeclaracaoEnum = Query(
        ...,
        description="Tipo de declaracao"
    ),
    exercicio_inicio: int = Query(
        ...,
        ge=2000,
        le=2100,
        description="Exercicio inicial"
    ),
    exercicio_fim: Optional[int] = Query(
        None,
        ge=2000,
        le=2100,
        description="Exercicio final"
    ),
    service: EcacService = Depends(get_service)
) -> StandardResponse:
    """Consulta declaracoes transmitidas."""
    try:
        resultado = service.consultar_declaracoes(
            tipo=tipo.value,
            exercicio_inicio=exercicio_inicio,
            exercicio_fim=exercicio_fim,
        )

        return StandardResponse(
            success=True,
            message=f"Declaracoes consultadas: {resultado['quantidade']} encontradas",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao consulta declaracoes: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao consultar declaracoes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar declaracoes: {str(e)}"
        )


@router.post(
    "/certidao",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Emitir certidao",
    description="Emite certidao fiscal (CND/CPEN) via e-CAC"
)
async def emitir_certidao(
    request: EmitirCertidaoRequest,
    service: EcacService = Depends(get_service)
) -> StandardResponse:
    """Emite certidao fiscal."""
    try:
        resultado = service.emitir_certidao(
            finalidade=request.finalidade,
            cpf_cnpj=request.cpf_cnpj,
        )

        return StandardResponse(
            success=True,
            message=f"Certidao {resultado['tipo'].upper()} emitida com sucesso",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao emissao certidao: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao emitir certidao: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao emitir certidao: {str(e)}"
        )


@router.post(
    "/validar-certidao",
    response_model=StandardResponse,
    summary="Validar certidao",
    description="Valida autenticidade de uma certidao fiscal"
)
async def validar_certidao(
    request: ValidarCertidaoRequest,
    service: EcacService = Depends(get_service)
) -> StandardResponse:
    """Valida autenticidade de certidao."""
    try:
        resultado = service.validar_certidao(
            numero=request.numero,
            codigo_controle=request.codigo_controle,
        )

        mensagem = (
            "Certidao valida" if resultado["valida"]
            else "Certidao invalida ou nao encontrada"
        )

        return StandardResponse(
            success=True,
            message=mensagem,
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao validar certidao: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao validar certidao: {str(e)}"
        )


@router.get(
    "/parcelamentos",
    response_model=StandardResponse,
    summary="Consulta parcelamentos",
    description="Consulta parcelamentos ativos do contribuinte"
)
async def consultar_parcelamentos(
    situacao: Optional[str] = Query(
        None,
        description="Filtro por situacao (ativo, encerrado)"
    ),
    service: EcacService = Depends(get_service)
) -> StandardResponse:
    """Consulta parcelamentos ativos."""
    try:
        resultado = service.consultar_parcelamentos(situacao=situacao)

        return StandardResponse(
            success=True,
            message=f"Parcelamentos consultados: {resultado['quantidade']} encontrados",
            data=resultado
        )

    except Exception as e:
        logger.error(f"Erro ao consultar parcelamentos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar parcelamentos: {str(e)}"
        )


@router.post(
    "/simular-parcelamento",
    response_model=StandardResponse,
    summary="Simular parcelamento",
    description="Simula parcelamento de debitos fiscais"
)
async def simular_parcelamento(
    request: SimularParcelamentoRequest,
    service: EcacService = Depends(get_service)
) -> StandardResponse:
    """Simula parcelamento de debitos."""
    try:
        resultado = service.simular_parcelamento(
            debitos=request.debitos,
            quantidade_parcelas=request.quantidade_parcelas,
        )

        return StandardResponse(
            success=True,
            message=f"Simulacao de parcelamento em {request.quantidade_parcelas}x realizada",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao simulacao: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao simular parcelamento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao simular parcelamento: {str(e)}"
        )


@router.get(
    "/processos",
    response_model=StandardResponse,
    summary="Consulta processos",
    description="Consulta processos digitais (e-Processo) do contribuinte"
)
async def consultar_processos(
    situacao: Optional[SituacaoProcessoEnum] = Query(
        None,
        description="Filtro por situacao do processo"
    ),
    numero_processo: Optional[str] = Query(
        None,
        description="Numero especifico do processo"
    ),
    service: EcacService = Depends(get_service)
) -> StandardResponse:
    """Consulta processos digitais."""
    try:
        resultado = service.consultar_processos(
            situacao=situacao.value if situacao else None,
            numero_processo=numero_processo,
        )

        return StandardResponse(
            success=True,
            message=f"Processos consultados: {resultado['quantidade']} encontrados",
            data=resultado
        )

    except Exception as e:
        logger.error(f"Erro ao consultar processos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar processos: {str(e)}"
        )
