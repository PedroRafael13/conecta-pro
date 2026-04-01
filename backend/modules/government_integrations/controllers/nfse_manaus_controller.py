"""
Controller para NFS-e Manaus.

Endpoints REST para emissão, consulta e cancelamento de NFS-e.
Prefeitura de Manaus - Padrão ABRASF 2.04
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path, Query, status

from core.auth.dependencies import CurrentActiveUser

from ..schemas.common import StandardResponse
from ..schemas.nfse_manaus import (
    CancelarNFSeRequest,
    CancelarNFSeResponse,
    EmitirNFSeRequest,
    EmitirNFSeResponse,
    SubstituirNFSeRequest,
    ValidarConexaoResponse,
)
from ..services.nfse_manaus_service import get_nfse_manaus_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nfse-manaus", tags=["NFS-e Manaus"])


@router.post(
    "/emitir",
    response_model=StandardResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Emite NFS-e",
    description="Emite Nota Fiscal de Serviços Eletronica via RPS para Prefeitura de Manaus.",
)
async def emitir_nfse(current_user: CurrentActiveUser, request: EmitirNFSeRequest) -> StandardResponse:
    """
    Emite NFS-e através de RPS.

    O RPS (Recibo Provisório de Serviço) é convertido em NFS-e pelo WebService
    da Prefeitura de Manaus.

    Args:
        request: Dados para emissão (tomador, serviço, competência).

    Returns:
        StandardResponse com dados da NFS-e emitida.

    Raises:
        HTTPException 400: Dados inválidos.
        HTTPException 500: Erro de comunicação com WebService.
    """
    try:
        service = get_nfse_manaus_service()

        resultado = service.emitir_nfse(
            tomador_data=request.tomador.model_dump(),
            servico_data=request.servico.model_dump(),
            competencia=request.competencia,
            natureza_operacao=request.natureza_operacao.value,
            optante_simples=request.optante_simples,
        )

        response_data = EmitirNFSeResponse(
            numero_rps=resultado.get("numero_rps"),
            numero_lote=resultado.get("numero_lote"),
            numero_nfse=resultado.get("numero_nfse"),
            codigo_verificacao=resultado.get("codigo_verificacao"),
            protocolo=resultado.get("protocolo"),
            status=resultado.get("status", "pendente"),
            mensagem=resultado.get("mensagem"),
            data_emissao=datetime.now(),
            valor_servicos=request.servico.valor_servicos,
            valor_iss=request.servico.valor_servicos * request.servico.aliquota_iss,
            tomador_cpf_cnpj=request.tomador.cpf_cnpj,
        )

        return StandardResponse(
            success=True,
            message="NFS-e enviada para processamento",
            data=response_data.model_dump(),
        )

    except ValueError as e:
        logger.warning(f"Dados inválidos para emissão NFS-e: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados inválidos: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Erro ao emitir NFS-e: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao emitir NFS-e",
        )


@router.get(
    "/consultar/rps/{numero_rps}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta NFS-e por RPS",
    description="Consulta NFS-e pelo número do RPS.",
)
async def consultar_nfse_por_rps(
    current_user: CurrentActiveUser,
    numero_rps: str = Path(..., description="Número do RPS"),
    serie: str = Query(default="RPS", description="Série do RPS"),
    tipo: str = Query(default="1", description="Tipo do RPS"),
) -> StandardResponse:
    """
    Consulta NFS-e pelo número do RPS.

    Útil para verificar se o RPS já foi convertido em NFS-e.

    Args:
        numero_rps: Número do RPS enviado.
        serie: Série do RPS (padrão: "RPS").
        tipo: Tipo do RPS (padrão: "1" = RPS).

    Returns:
        StandardResponse com dados da NFS-e.
    """
    try:
        service = get_nfse_manaus_service()

        resultado = service.consultar_nfse_por_rps(numero_rps, serie, tipo)

        return StandardResponse(
            success=True,
            message="Consulta realizada",
            data=resultado,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NFS-e não encontrada: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Erro ao consultar NFS-e por RPS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao consultar NFS-e",
        )


@router.get(
    "/consultar/numero/{numero_nfse}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta NFS-e por número",
    description="Consulta NFS-e pelo número da nota.",
)
async def consultar_nfse_por_numero(
    current_user: CurrentActiveUser,
    numero_nfse: str = Path(..., description="Número da NFS-e"),
) -> StandardResponse:
    """
    Consulta NFS-e pelo número da nota.

    Args:
        numero_nfse: Número da NFS-e.

    Returns:
        StandardResponse com dados da NFS-e.
    """
    try:
        service = get_nfse_manaus_service()

        resultado = service.consultar_nfse_por_numero(numero_nfse)

        return StandardResponse(
            success=True,
            message="Consulta realizada",
            data=resultado,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NFS-e não encontrada",
        )
    except Exception as e:
        logger.error(f"Erro ao consultar NFS-e: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao consultar NFS-e",
        )


@router.post(
    "/cancelar",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancela NFS-e",
    description="Cancela uma NFS-e emitida.",
)
async def cancelar_nfse(current_user: CurrentActiveUser, request: CancelarNFSeRequest) -> StandardResponse:
    """
    Cancela uma NFS-e.

    O cancelamento deve ser feito em até 90 dias da emissão.
    Após esse prazo, deve-se usar a substituição.

    Args:
        request: Dados do cancelamento (número, código, motivo).

    Returns:
        StandardResponse com resultado do cancelamento.
    """
    try:
        service = get_nfse_manaus_service()

        resultado = service.cancelar_nfse(
            numero_nfse=request.numero_nfse,
            codigo_cancelamento=request.codigo_cancelamento.value,
            motivo=request.motivo,
        )

        response_data = CancelarNFSeResponse(
            numero_nfse=request.numero_nfse,
            status=resultado.get("status", "erro"),
            data_cancelamento=datetime.now() if resultado.get("status") == "cancelado" else None,
            protocolo=resultado.get("protocolo"),
            mensagem=resultado.get("mensagem"),
        )

        return StandardResponse(
            success=resultado.get("status") in ["cancelado", "simulado"],
            message="Cancelamento processado",
            data=response_data.model_dump(),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro no cancelamento: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Erro ao cancelar NFS-e: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao cancelar NFS-e",
        )


@router.post(
    "/substituir",
    response_model=StandardResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Substitui NFS-e",
    description="Substitui uma NFS-e por outra.",
)
async def substituir_nfse(current_user: CurrentActiveUser, request: SubstituirNFSeRequest) -> StandardResponse:
    """
    Substitui uma NFS-e.

    A NFS-e original é cancelada e uma nova é emitida vinculada.

    Args:
        request: Dados da substituição (nota original e novos dados).

    Returns:
        StandardResponse com dados da nova NFS-e.
    """
    try:
        service = get_nfse_manaus_service()

        resultado = service.substituir_nfse(
            numero_nfse_substituida=request.numero_nfse_substituida,
            tomador_data=request.tomador.model_dump(),
            servico_data=request.servico.model_dump(),
        )

        return StandardResponse(
            success=resultado.get("status") in ["substituida", "simulado"],
            message="Substituição processada",
            data=resultado,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro na substituição: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Erro ao substituir NFS-e: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao substituir NFS-e",
        )


@router.get(
    "/lote/{numero_lote}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta situação do lote",
    description="Consulta a situação de processamento de um lote de RPS.",
)
async def consultar_lote(
    current_user: CurrentActiveUser,
    numero_lote: str = Path(..., description="Número/protocolo do lote"),
) -> StandardResponse:
    """
    Consulta situação de um lote de RPS.

    Útil para verificar se o lote foi processado com sucesso.

    Args:
        numero_lote: Número ou protocolo do lote.

    Returns:
        StandardResponse com situação do lote.
    """
    try:
        service = get_nfse_manaus_service()

        resultado = service.consultar_situacao_lote(numero_lote)

        return StandardResponse(
            success=True,
            message="Consulta de lote realizada",
            data=resultado,
        )

    except Exception as e:
        logger.error(f"Erro ao consultar lote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao consultar lote",
        )


@router.get(
    "/status",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Valida conexão com WebService",
    description="Verifica conexão com WebService da Prefeitura de Manaus e status do certificado.",
)
async def validar_conexao(current_user: CurrentActiveUser) -> StandardResponse:
    """
    Valida conexão com WebService.

    Verifica:
    - Conectividade HTTP com o WebService
    - Validade do certificado digital
    - Configurações do ambiente

    Returns:
        StandardResponse com status da conexão.
    """
    try:
        service = get_nfse_manaus_service()

        resultado = service.validar_conexao()

        response_data = ValidarConexaoResponse(
            ambiente=resultado.get("ambiente", ""),
            cnpj=resultado.get("cnpj", ""),
            url_base=resultado.get("url_base", ""),
            conexao_http=resultado.get("conexao_http", False),
            http_status=resultado.get("http_status"),
            certificado_configurado=resultado.get("certificado_configurado", False),
            certificado_valido=resultado.get("certificado_valido"),
            certificado_expira=resultado.get("certificado_expira"),
            mensagem=resultado.get("erro_http"),
        )

        return StandardResponse(
            success=resultado.get("conexao_http", False),
            message="Validação de conexão concluída",
            data=response_data.model_dump(),
        )

    except Exception as e:
        logger.error(f"Erro ao validar conexão: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao validar conexão",
        )


@router.get(
    "/codigos-servico",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista códigos de serviço",
    description="Lista códigos de serviço comuns para vigilância/segurança.",
)
async def listar_codigos_servico(current_user: CurrentActiveUser) -> StandardResponse:
    """
    Lista códigos de serviço disponíveis.

    Retorna os códigos da Lista de Serviços (LC 116) mais usados
    para o setor de vigilância e segurança.

    Returns:
        StandardResponse com lista de códigos.
    """
    codigos = [
        {
            "codigo": "11.02",
            "descricao": "Vigilância, segurança ou monitoramento de bens, pessoas e semoventes",
            "aliquota_sugerida": "5%",
        },
        {
            "codigo": "11.03",
            "descricao": "Escolta, inclusive de veículos e cargas",
            "aliquota_sugerida": "5%",
        },
        {
            "codigo": "11.04",
            "descricao": "Armazenamento, depósito, carga, descarga, arrumação e guarda de bens",
            "aliquota_sugerida": "5%",
        },
        {
            "codigo": "11.05",
            "descricao": "Serviços de transporte de valores",
            "aliquota_sugerida": "5%",
        },
        {
            "codigo": "17.01",
            "descricao": "Assessoria ou consultoria de qualquer natureza",
            "aliquota_sugerida": "5%",
        },
        {
            "codigo": "17.02",
            "descricao": "Análise, exame, pesquisa, coleta, compilação e fornecimento de dados",
            "aliquota_sugerida": "5%",
        },
    ]

    return StandardResponse(
        success=True,
        message="Códigos de serviço disponíveis",
        data={"codigos": codigos},
    )
