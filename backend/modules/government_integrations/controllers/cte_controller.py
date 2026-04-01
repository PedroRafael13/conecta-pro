"""
Controller REST para CT-e (Conhecimento de Transporte Eletronico).

Endpoints para operacoes do CT-e.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse

from core.auth.dependencies import CurrentActiveUser

from ..schemas.common import StandardResponse
from ..schemas.cte import (
    CriarCTeRequest,
    GerarXMLRequest,
)
from ..services.cte_service import (
    CTeService,
    get_cte_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cte", tags=["CT-e"])


def get_service() -> CTeService:
    """Dependency para obter o service."""
    return get_cte_service()


@router.get(
    "/status",
    response_model=StandardResponse,
    summary="Status do CT-e",
    description="Retorna o status da configuracao do CT-e",
)
async def get_status(current_user: CurrentActiveUser, service: CTeService = Depends(get_service)) -> StandardResponse:
    """Retorna status da configuracao."""
    try:
        status_data = service.validar_status()

        return StandardResponse(success=True, message="Status CT-e obtido", data=status_data)

    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/criar",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar CT-e",
    description="Cria um novo CT-e",
)
async def criar_cte(
    request: CriarCTeRequest, current_user: CurrentActiveUser, service: CTeService = Depends(get_service)
) -> StandardResponse:
    """Cria um novo CT-e."""
    try:
        # Converte request para dict
        dados = request.model_dump()

        # Converte participantes
        if dados.get("remetente"):
            dados["remetente"] = request.remetente.model_dump() if request.remetente else None
        if dados.get("destinatario"):
            dados["destinatario"] = request.destinatario.model_dump() if request.destinatario else None
        if dados.get("expedidor"):
            dados["expedidor"] = request.expedidor.model_dump() if request.expedidor else None
        if dados.get("recebedor"):
            dados["recebedor"] = request.recebedor.model_dump() if request.recebedor else None

        # Converte NF referenciadas
        if request.nf_referenciadas:
            dados["nf_referenciadas"] = [nf.model_dump() for nf in request.nf_referenciadas]

        # Converte carga
        if request.carga:
            dados["carga"] = request.carga.model_dump()

        # Converte componentes de valor
        if request.componentes_valor:
            dados["componentes_valor"] = [c.model_dump() for c in request.componentes_valor]

        # Converte enums para string
        dados["modal"] = request.modal.value
        dados["tipo_servico"] = request.tipo_servico.value
        dados["tomador"] = request.tomador.value

        resultado = service.criar_cte(dados)

        return StandardResponse(
            success=True, message=f"CT-e {resultado['numero']}/{resultado['serie']} criado", data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar CT-e: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/gerar-xml",
    response_model=StandardResponse,
    summary="Gerar XML",
    description="Gera o XML do CT-e",
    status_code=201,
)
async def gerar_xml(
    request: GerarXMLRequest, current_user: CurrentActiveUser, service: CTeService = Depends(get_service)
) -> StandardResponse:
    """Gera XML do CT-e."""
    try:
        # Converte request para dict
        dados = request.model_dump()

        # Converte participantes
        if dados.get("remetente"):
            dados["remetente"] = request.remetente.model_dump() if request.remetente else None
        if dados.get("destinatario"):
            dados["destinatario"] = request.destinatario.model_dump() if request.destinatario else None
        if dados.get("expedidor"):
            dados["expedidor"] = request.expedidor.model_dump() if request.expedidor else None
        if dados.get("recebedor"):
            dados["recebedor"] = request.recebedor.model_dump() if request.recebedor else None

        # Converte NF referenciadas
        if request.nf_referenciadas:
            dados["nf_referenciadas"] = [nf.model_dump() for nf in request.nf_referenciadas]

        # Converte carga
        if request.carga:
            dados["carga"] = request.carga.model_dump()

        # Converte componentes de valor
        if request.componentes_valor:
            dados["componentes_valor"] = [c.model_dump() for c in request.componentes_valor]

        # Converte enums para string
        dados["modal"] = request.modal.value
        dados["tipo_servico"] = request.tipo_servico.value
        dados["tomador"] = request.tomador.value

        resultado = service.gerar_xml(dados)

        return StandardResponse(
            success=True, message=f"XML gerado para CT-e {resultado['numero']}/{resultado['serie']}", data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao gerar XML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/gerar-xml/download",
    response_class=PlainTextResponse,
    summary="Download XML",
    description="Gera e retorna o XML do CT-e para download",
    status_code=201,
)
async def gerar_xml_download(
    request: GerarXMLRequest, current_user: CurrentActiveUser, service: CTeService = Depends(get_service)
) -> PlainTextResponse:
    """Gera XML do CT-e para download."""
    try:
        # Converte request para dict
        dados = request.model_dump()

        # Converte enums para string
        dados["modal"] = request.modal.value
        dados["tipo_servico"] = request.tipo_servico.value
        dados["tomador"] = request.tomador.value

        resultado = service.gerar_xml(dados)

        filename = f"CTe_{resultado['numero']}_{resultado['serie']}.xml"

        return PlainTextResponse(
            content=resultado["xml"],
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error(f"Erro no download: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/consultar-status-servico",
    response_model=StandardResponse,
    summary="Consultar Status Servico",
    description="Consulta o status do servico CT-e na SEFAZ",
)
async def consultar_status_servico(
    current_user: CurrentActiveUser, service: CTeService = Depends(get_service)
) -> StandardResponse:
    """Consulta status do servico na SEFAZ."""
    try:
        resultado = service.consultar_status_servico()

        return StandardResponse(success=True, message=f"Status: {resultado['status']}", data=resultado)

    except Exception as e:
        logger.error(f"Erro ao consultar status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/modais",
    response_model=StandardResponse,
    summary="Listar Modais",
    description="Lista os modais de transporte disponiveis",
)
async def listar_modais(
    current_user: CurrentActiveUser, service: CTeService = Depends(get_service)
) -> StandardResponse:
    """Lista modais de transporte."""
    try:
        modais = service.listar_modais()

        return StandardResponse(success=True, message=f"{len(modais['modais'])} modais disponiveis", data=modais)

    except Exception as e:
        logger.error(f"Erro ao listar modais: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/tipos-servico",
    response_model=StandardResponse,
    summary="Listar Tipos de Servico",
    description="Lista os tipos de servico de transporte disponiveis",
)
async def listar_tipos_servico(
    current_user: CurrentActiveUser, service: CTeService = Depends(get_service)
) -> StandardResponse:
    """Lista tipos de servico."""
    try:
        tipos = service.listar_tipos_servico()

        return StandardResponse(
            success=True, message=f"{len(tipos['tipos_servico'])} tipos de servico disponiveis", data=tipos
        )

    except Exception as e:
        logger.error(f"Erro ao listar tipos de servico: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/listar", response_model=StandardResponse, summary="Listar CT-e", description="Lista todos os CT-e em cache"
)
async def listar_ctes(current_user: CurrentActiveUser, service: CTeService = Depends(get_service)) -> StandardResponse:
    """Lista CT-e em cache."""
    try:
        ctes = service.listar_ctes()

        return StandardResponse(success=True, message=f"{len(ctes['ctes'])} CT-e em cache", data=ctes)

    except Exception as e:
        logger.error(f"Erro ao listar CT-e: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/obter/{numero}",
    response_model=StandardResponse,
    summary="Obter CT-e",
    description="Obtem um CT-e especifico pelo numero",
)
async def obter_cte(
    numero: int, current_user: CurrentActiveUser, serie: int = 1, service: CTeService = Depends(get_service)
) -> StandardResponse:
    """Obtem CT-e pelo numero."""
    try:
        cte = service.obter_cte(numero, serie)

        if not cte:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"CT-e {numero}/{serie} nao encontrado")

        return StandardResponse(success=True, message=f"CT-e {numero}/{serie} obtido", data=cte)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter CT-e: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.delete(
    "/limpar", response_model=StandardResponse, summary="Limpar Cache", description="Limpa todos os CT-e em cache"
)
async def limpar_cache(current_user: CurrentActiveUser, service: CTeService = Depends(get_service)) -> StandardResponse:
    """Limpa cache de CT-e."""
    try:
        resultado = service.limpar_cache()

        return StandardResponse(success=True, message="Cache limpo", data=resultado)

    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")
