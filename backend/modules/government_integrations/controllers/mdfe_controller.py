"""
Controller REST para MDF-e (Manifesto Eletronico de Documentos Fiscais).

Endpoints para operacoes do MDF-e.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse

from ..schemas.common import StandardResponse
from ..schemas.mdfe import (
    CriarMDFeRequest,
    EncerrarMDFeRequest,
    GerarXMLRequest,
    IncluirCondutorRequest,
)
from ..services.mdfe_service import (
    MDFeService,
    get_mdfe_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mdfe", tags=["MDF-e"])


def get_service() -> MDFeService:
    """Dependency para obter o service."""
    return get_mdfe_service()


@router.get(
    "/status",
    response_model=StandardResponse,
    summary="Status do MDF-e",
    description="Retorna o status da configuracao do modulo MDF-e",
)
async def get_status(service: MDFeService = Depends(get_service)) -> StandardResponse:
    """Retorna status da configuracao."""
    try:
        status_data = service.validar_status()

        return StandardResponse(success=True, message="Status MDF-e obtido", data=status_data)

    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/criar",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar MDF-e",
    description="Cria um novo Manifesto Eletronico de Documentos Fiscais",
)
async def criar_mdfe(request: CriarMDFeRequest, service: MDFeService = Depends(get_service)) -> StandardResponse:
    """Cria um novo MDF-e."""
    try:
        dados = request.model_dump()

        # Converte Enums para strings
        dados["modal"] = request.modal.value
        dados["tipo_emitente"] = request.tipo_emitente.value

        # Converte veiculo_tracao
        if request.veiculo_tracao:
            dados["veiculo_tracao"]["tipo_rodado"] = request.veiculo_tracao.tipo_rodado.value
            dados["veiculo_tracao"]["tipo_carroceria"] = request.veiculo_tracao.tipo_carroceria.value

        # Converte reboques
        if request.reboques:
            for i, reboque in enumerate(request.reboques):
                dados["reboques"][i]["tipo_carroceria"] = reboque.tipo_carroceria.value

        resultado = service.criar_mdfe(dados)

        return StandardResponse(success=True, message=f"MDF-e {resultado['numero']} criado com sucesso", data=resultado)

    except ValueError as e:
        logger.warning(f"Erro de validacao: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar MDF-e: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/gerar-xml",
    response_model=StandardResponse,
    summary="Gerar XML",
    description="Gera o XML do MDF-e para envio a SEFAZ",
)
async def gerar_xml(request: GerarXMLRequest, service: MDFeService = Depends(get_service)) -> StandardResponse:
    """Gera XML do MDF-e."""
    try:
        resultado = service.gerar_xml(request.mdfe_id)

        return StandardResponse(success=True, message=f"XML gerado para MDF-e {resultado['numero']}", data=resultado)

    except ValueError as e:
        logger.warning(f"Erro de validacao: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao gerar XML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/gerar-xml/download",
    response_class=PlainTextResponse,
    summary="Download XML",
    description="Gera e retorna o XML do MDF-e para download",
)
async def gerar_xml_download(
    request: GerarXMLRequest, service: MDFeService = Depends(get_service)
) -> PlainTextResponse:
    """Gera XML do MDF-e para download."""
    try:
        resultado = service.gerar_xml(request.mdfe_id)

        filename = f"MDFe_{resultado['numero']}.xml"

        return PlainTextResponse(
            content=resultado["xml"],
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Erro no download: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/encerrar",
    response_model=StandardResponse,
    summary="Encerrar MDF-e",
    description="Gera evento de encerramento do MDF-e autorizado",
)
async def encerrar_mdfe(request: EncerrarMDFeRequest, service: MDFeService = Depends(get_service)) -> StandardResponse:
    """Encerra o MDF-e."""
    try:
        dados = request.model_dump()
        resultado = service.encerrar_mdfe(dados)

        return StandardResponse(success=True, message="Evento de encerramento gerado para MDF-e", data=resultado)

    except ValueError as e:
        logger.warning(f"Erro de validacao: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao encerrar: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/incluir-condutor",
    response_model=StandardResponse,
    summary="Incluir condutor",
    description="Gera evento de inclusao de condutor no MDF-e autorizado",
)
async def incluir_condutor(
    request: IncluirCondutorRequest, service: MDFeService = Depends(get_service)
) -> StandardResponse:
    """Inclui condutor no MDF-e."""
    try:
        dados = {
            "chave": request.chave,
            "condutor": request.condutor.model_dump(),
        }
        resultado = service.incluir_condutor(dados)

        return StandardResponse(success=True, message="Evento de inclusao de condutor gerado", data=resultado)

    except ValueError as e:
        logger.warning(f"Erro de validacao: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao incluir condutor: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/consultar-status-servico",
    response_model=StandardResponse,
    summary="Status do servico SEFAZ",
    description="Consulta status do servico MDF-e na SEFAZ",
)
async def consultar_status_servico(service: MDFeService = Depends(get_service)) -> StandardResponse:
    """Consulta status do servico."""
    try:
        resultado = service.consultar_status_servico()

        return StandardResponse(success=True, message=f"Status do servico: {resultado['status']}", data=resultado)

    except Exception as e:
        logger.error(f"Erro ao consultar status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/nao-encerrados",
    response_model=StandardResponse,
    summary="MDF-e nao encerrados",
    description="Lista MDF-e autorizados que ainda nao foram encerrados",
)
async def consultar_nao_encerrados(service: MDFeService = Depends(get_service)) -> StandardResponse:
    """Consulta MDF-e nao encerrados."""
    try:
        resultado = service.consultar_nao_encerrados()

        return StandardResponse(success=True, message=f"{resultado['quantidade']} MDF-e nao encerrados", data=resultado)

    except Exception as e:
        logger.error(f"Erro ao consultar nao encerrados: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/modais",
    response_model=StandardResponse,
    summary="Lista modais de transporte",
    description="Retorna os modais de transporte disponiveis para MDF-e",
)
async def listar_modais(service: MDFeService = Depends(get_service)) -> StandardResponse:
    """Lista modais de transporte."""
    try:
        resultado = service.listar_modais()

        return StandardResponse(success=True, message="Modais de transporte listados", data=resultado)

    except Exception as e:
        logger.error(f"Erro ao listar modais: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/tipos-emitente",
    response_model=StandardResponse,
    summary="Lista tipos de emitente",
    description="Retorna os tipos de emitente disponiveis para MDF-e",
)
async def listar_tipos_emitente(service: MDFeService = Depends(get_service)) -> StandardResponse:
    """Lista tipos de emitente."""
    try:
        resultado = service.listar_tipos_emitente()

        return StandardResponse(success=True, message="Tipos de emitente listados", data=resultado)

    except Exception as e:
        logger.error(f"Erro ao listar tipos de emitente: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/tipos-carroceria",
    response_model=StandardResponse,
    summary="Lista tipos de carroceria",
    description="Retorna os tipos de carroceria disponiveis para MDF-e",
)
async def listar_tipos_carroceria(service: MDFeService = Depends(get_service)) -> StandardResponse:
    """Lista tipos de carroceria."""
    try:
        resultado = service.listar_tipos_carroceria()

        return StandardResponse(success=True, message="Tipos de carroceria listados", data=resultado)

    except Exception as e:
        logger.error(f"Erro ao listar tipos de carroceria: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/listar", response_model=StandardResponse, summary="Lista MDF-e", description="Lista todos os MDF-e em memoria"
)
async def listar_mdfes(service: MDFeService = Depends(get_service)) -> StandardResponse:
    """Lista MDF-e."""
    try:
        resultado = service.listar_mdfes()

        return StandardResponse(success=True, message=f"{resultado['quantidade']} MDF-e encontrados", data=resultado)

    except Exception as e:
        logger.error(f"Erro ao listar MDF-e: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get("/{mdfe_id}", response_model=StandardResponse, summary="Buscar MDF-e", description="Busca um MDF-e pelo ID")
async def buscar_mdfe(mdfe_id: str, service: MDFeService = Depends(get_service)) -> StandardResponse:
    """Busca MDF-e pelo ID."""
    try:
        resultado = service.buscar_mdfe(mdfe_id)

        if not resultado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"MDF-e nao encontrado: {mdfe_id}")

        return StandardResponse(success=True, message=f"MDF-e {resultado['numero']} encontrado", data=resultado)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar MDF-e: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.delete(
    "/limpar", response_model=StandardResponse, summary="Limpar dados", description="Limpa todos os MDF-e em memoria"
)
async def limpar_dados(service: MDFeService = Depends(get_service)) -> StandardResponse:
    """Limpa dados em memoria."""
    try:
        resultado = service.limpar_dados()

        return StandardResponse(success=True, message="Dados limpos", data=resultado)

    except Exception as e:
        logger.error(f"Erro ao limpar: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")
