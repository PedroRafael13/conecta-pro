"""
Controller REST para SPED Fiscal (EFD ICMS/IPI).

Endpoints para operações do SPED Fiscal.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse

from core.auth.dependencies import CurrentActiveUser

from ..schemas.common import StandardResponse
from ..schemas.sped_fiscal import (
    AdicionarDocumentoRequest,
    AdicionarInventarioRequest,
    AdicionarParticipanteRequest,
    AdicionarProdutoRequest,
    CalcularApuracaoRequest,
    GerarArquivoRequest,
)
from ..services.sped_fiscal_service import (
    SPEDFiscalService,
    get_sped_fiscal_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sped-fiscal", tags=["SPED Fiscal"])


def get_service() -> SPEDFiscalService:
    """Dependency para obter o service."""
    return get_sped_fiscal_service()


@router.get(
    "/status",
    response_model=StandardResponse,
    summary="Status do SPED Fiscal",
    description="Retorna o status da configuração do SPED Fiscal",
)
async def get_status(
    current_user: CurrentActiveUser, service: SPEDFiscalService = Depends(get_service)
) -> StandardResponse:
    """Retorna status da configuração."""
    try:
        status_data = service.validar_status()

        return StandardResponse(success=True, message="Status SPED Fiscal obtido", data=status_data)

    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/blocos",
    response_model=StandardResponse,
    summary="Lista blocos",
    description="Retorna a lista de blocos do SPED Fiscal",
)
async def listar_blocos(
    current_user: CurrentActiveUser, service: SPEDFiscalService = Depends(get_service)
) -> StandardResponse:
    """Lista blocos do SPED."""
    try:
        blocos = service.listar_blocos()

        return StandardResponse(success=True, message="Blocos listados", data=blocos)

    except Exception as e:
        logger.error(f"Erro ao listar blocos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/participantes",
    response_model=StandardResponse,
    summary="Lista participantes",
    description="Retorna a lista de participantes cadastrados",
)
async def listar_participantes(
    current_user: CurrentActiveUser, service: SPEDFiscalService = Depends(get_service)
) -> StandardResponse:
    """Lista participantes."""
    try:
        participantes = service.listar_participantes()

        return StandardResponse(
            success=True, message=f"{len(participantes['participantes'])} participantes", data=participantes
        )

    except Exception as e:
        logger.error(f"Erro ao listar participantes: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/produtos",
    response_model=StandardResponse,
    summary="Lista produtos",
    description="Retorna a lista de produtos cadastrados",
)
async def listar_produtos(
    current_user: CurrentActiveUser, service: SPEDFiscalService = Depends(get_service)
) -> StandardResponse:
    """Lista produtos."""
    try:
        produtos = service.listar_produtos()

        return StandardResponse(success=True, message=f"{len(produtos['produtos'])} produtos", data=produtos)

    except Exception as e:
        logger.error(f"Erro ao listar produtos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/documentos",
    response_model=StandardResponse,
    summary="Lista documentos",
    description="Retorna a lista de documentos cadastrados",
)
async def listar_documentos(
    current_user: CurrentActiveUser, service: SPEDFiscalService = Depends(get_service)
) -> StandardResponse:
    """Lista documentos."""
    try:
        documentos = service.listar_documentos()

        return StandardResponse(success=True, message=f"{len(documentos['documentos'])} documentos", data=documentos)

    except Exception as e:
        logger.error(f"Erro ao listar documentos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/participante",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar participante",
    description="Adiciona um participante ao cadastro",
)
async def adicionar_participante(
    current_user: CurrentActiveUser,
    request: AdicionarParticipanteRequest,
    service: SPEDFiscalService = Depends(get_service),
) -> StandardResponse:
    """Adiciona participante."""
    try:
        resultado = service.adicionar_participante(request.participante.model_dump())

        return StandardResponse(success=True, message=f"Participante {resultado['codigo']} adicionado", data=resultado)

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao adicionar: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/produto",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar produto",
    description="Adiciona um produto ao cadastro",
)
async def adicionar_produto(
    current_user: CurrentActiveUser, request: AdicionarProdutoRequest, service: SPEDFiscalService = Depends(get_service)
) -> StandardResponse:
    """Adiciona produto."""
    try:
        resultado = service.adicionar_produto(request.produto.model_dump())

        return StandardResponse(success=True, message=f"Produto {resultado['codigo']} adicionado", data=resultado)

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao adicionar: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/documento",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar documento",
    description="Adiciona um documento fiscal",
)
async def adicionar_documento(
    current_user: CurrentActiveUser,
    request: AdicionarDocumentoRequest,
    service: SPEDFiscalService = Depends(get_service),
) -> StandardResponse:
    """Adiciona documento fiscal."""
    try:
        resultado = service.adicionar_documento(request.documento.model_dump())

        return StandardResponse(success=True, message=f"Documento {resultado['numero']} adicionado", data=resultado)

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao adicionar: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/inventario",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar item inventário",
    description="Adiciona um item ao inventário",
)
async def adicionar_inventario(
    current_user: CurrentActiveUser,
    request: AdicionarInventarioRequest,
    service: SPEDFiscalService = Depends(get_service),
) -> StandardResponse:
    """Adiciona item ao inventário."""
    try:
        resultado = service.adicionar_inventario(request.item.model_dump())

        return StandardResponse(success=True, message=f"Item {resultado['codigo_item']} adicionado", data=resultado)

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao adicionar: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/apuracao",
    response_model=StandardResponse,
    summary="Calcular apuração",
    description="Calcula a apuração de ICMS do período",
)
async def calcular_apuracao(
    current_user: CurrentActiveUser, request: CalcularApuracaoRequest, service: SPEDFiscalService = Depends(get_service)
) -> StandardResponse:
    """Calcula apuração ICMS."""
    try:
        documentos = [d.model_dump() for d in request.documentos]

        resultado = service.calcular_apuracao(
            periodo=request.periodo,
            documentos=documentos,
        )

        return StandardResponse(
            success=True,
            message=f"Apuração {request.periodo}: Saldo devedor R$ {resultado['saldo_devedor']}",
            data=resultado,
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro na apuração: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/gerar",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar arquivo SPED",
    description="Gera o arquivo SPED Fiscal",
)
async def gerar_arquivo(
    current_user: CurrentActiveUser, request: GerarArquivoRequest, service: SPEDFiscalService = Depends(get_service)
) -> StandardResponse:
    """Gera arquivo SPED."""
    try:
        participantes = [p.model_dump() for p in request.participantes] if request.participantes else None
        produtos = [p.model_dump() for p in request.produtos] if request.produtos else None
        documentos = [d.model_dump() for d in request.documentos] if request.documentos else None
        inventario = [i.model_dump() for i in request.inventario] if request.inventario else None

        resultado = service.gerar_arquivo(
            periodo_inicio=request.periodo_inicio,
            periodo_fim=request.periodo_fim,
            finalidade=request.finalidade.value,
            participantes=participantes,
            produtos=produtos,
            documentos=documentos,
            inventario=inventario,
        )

        return StandardResponse(
            success=True, message=f"Arquivo gerado: {resultado['total_registros']} registros", data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro na geração: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/gerar/download",
    response_class=PlainTextResponse,
    summary="Download arquivo SPED",
    description="Gera e retorna o arquivo SPED para download",
)
async def gerar_arquivo_download(
    current_user: CurrentActiveUser, request: GerarArquivoRequest, service: SPEDFiscalService = Depends(get_service)
) -> PlainTextResponse:
    """Gera arquivo SPED para download."""
    try:
        participantes = [p.model_dump() for p in request.participantes] if request.participantes else None
        produtos = [p.model_dump() for p in request.produtos] if request.produtos else None
        documentos = [d.model_dump() for d in request.documentos] if request.documentos else None
        inventario = [i.model_dump() for i in request.inventario] if request.inventario else None

        resultado = service.gerar_arquivo(
            periodo_inicio=request.periodo_inicio,
            periodo_fim=request.periodo_fim,
            finalidade=request.finalidade.value,
            participantes=participantes,
            produtos=produtos,
            documentos=documentos,
            inventario=inventario,
        )

        filename = f"SPED_{request.periodo_inicio}_{request.periodo_fim}.txt"

        return PlainTextResponse(
            content=resultado["conteudo"],
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error(f"Erro no download: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.delete(
    "/limpar", response_model=StandardResponse, summary="Limpar dados", description="Limpa todos os dados em memória"
)
async def limpar_dados(
    current_user: CurrentActiveUser, service: SPEDFiscalService = Depends(get_service)
) -> StandardResponse:
    """Limpa dados em memória."""
    try:
        resultado = service.limpar_dados()

        return StandardResponse(success=True, message="Dados limpos", data=resultado)

    except Exception as e:
        logger.error(f"Erro ao limpar: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")
