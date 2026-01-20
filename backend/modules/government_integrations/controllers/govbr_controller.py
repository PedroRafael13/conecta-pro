"""
Controller REST para Gov.br - Plataforma de Login Unico do Governo Federal.

Endpoints para autenticacao OAuth2/OIDC com Gov.br.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import JSONResponse

from ..schemas.common import StandardResponse
from ..schemas.govbr import (
    GerarUrlAutorizacaoRequest,
    TrocarCodigoRequest,
    RenovarTokenRequest,
    ObterDadosUsuarioRequest,
    ValidarTokenRequest,
    GerarUrlLogoutRequest,
    ObterEmpresasRequest,
    NivelAutenticacaoEnum,
    AmbienteGovBrEnum,
    UrlAutorizacaoResponse,
    TokenGovBrResponse,
    UsuarioGovBrResponse,
    ValidacaoTokenResponse,
    StatusGovBrResponse,
)
from ..services.govbr_service import GovBrService, get_govbr_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/govbr", tags=["Gov.br - Autenticacao"])


def get_service() -> GovBrService:
    """Dependency para obter o service."""
    return get_govbr_service()


@router.get(
    "/status",
    response_model=StandardResponse,
    summary="Status do Gov.br",
    description="Retorna o status da configuracao e conexao do Gov.br"
)
async def get_status(
    service: GovBrService = Depends(get_service)
) -> StandardResponse:
    """Retorna status da configuracao Gov.br."""
    try:
        status_data = service.validar_status()

        return StandardResponse(
            success=True,
            message="Status Gov.br obtido com sucesso",
            data=status_data
        )

    except Exception as e:
        logger.error(f"Erro ao obter status Gov.br: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter status: {str(e)}"
        )


@router.post(
    "/autorizar",
    response_model=StandardResponse,
    summary="Gerar URL de autorizacao",
    description="Gera URL OAuth2 para redirecionar o usuario ao Gov.br"
)
async def gerar_url_autorizacao(
    request: GerarUrlAutorizacaoRequest,
    service: GovBrService = Depends(get_service)
) -> StandardResponse:
    """Gera URL de autorizacao OAuth2."""
    try:
        resultado = service.gerar_url_autorizacao(
            scopes=request.scopes,
            nivel_minimo=request.nivel_minimo.value if request.nivel_minimo else None,
        )

        return StandardResponse(
            success=True,
            message="URL de autorizacao gerada com sucesso",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao ao gerar URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao gerar URL de autorizacao: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar URL: {str(e)}"
        )


@router.get(
    "/autorizar",
    response_model=StandardResponse,
    summary="Gerar URL de autorizacao (GET)",
    description="Gera URL OAuth2 via GET com parametros opcionais"
)
async def gerar_url_autorizacao_get(
    scopes: Optional[str] = Query(
        None,
        description="Scopes separados por virgula (ex: openid,email,profile)"
    ),
    nivel_minimo: Optional[NivelAutenticacaoEnum] = Query(
        None,
        description="Nivel minimo de autenticacao"
    ),
    service: GovBrService = Depends(get_service)
) -> StandardResponse:
    """Gera URL de autorizacao OAuth2 via GET."""
    try:
        scopes_list = scopes.split(",") if scopes else None

        resultado = service.gerar_url_autorizacao(
            scopes=scopes_list,
            nivel_minimo=nivel_minimo.value if nivel_minimo else None,
        )

        return StandardResponse(
            success=True,
            message="URL de autorizacao gerada com sucesso",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao ao gerar URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao gerar URL de autorizacao: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar URL: {str(e)}"
        )


@router.post(
    "/callback",
    response_model=StandardResponse,
    summary="Processar callback OAuth2",
    description="Troca codigo de autorizacao por tokens"
)
async def processar_callback(
    request: TrocarCodigoRequest,
    service: GovBrService = Depends(get_service)
) -> StandardResponse:
    """Processa callback OAuth2 e troca codigo por tokens."""
    try:
        resultado = service.trocar_codigo_por_token(
            code=request.code,
            state=request.state,
            code_verifier=request.code_verifier,
        )

        return StandardResponse(
            success=True,
            message="Autenticacao Gov.br realizada com sucesso",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao no callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao processar callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar callback: {str(e)}"
        )


@router.get(
    "/callback",
    response_model=StandardResponse,
    summary="Processar callback OAuth2 (GET)",
    description="Processa callback via GET (redirect do Gov.br)"
)
async def processar_callback_get(
    code: str = Query(..., description="Codigo de autorizacao"),
    state: str = Query(..., description="State para validacao CSRF"),
    service: GovBrService = Depends(get_service)
) -> StandardResponse:
    """Processa callback OAuth2 via GET."""
    try:
        resultado = service.trocar_codigo_por_token(
            code=code,
            state=state,
        )

        return StandardResponse(
            success=True,
            message="Autenticacao Gov.br realizada com sucesso",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao no callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao processar callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar callback: {str(e)}"
        )


@router.post(
    "/renovar-token",
    response_model=StandardResponse,
    summary="Renovar token",
    description="Renova access_token usando refresh_token"
)
async def renovar_token(
    request: RenovarTokenRequest,
    service: GovBrService = Depends(get_service)
) -> StandardResponse:
    """Renova token de acesso."""
    try:
        resultado = service.renovar_token(
            refresh_token=request.refresh_token,
        )

        return StandardResponse(
            success=True,
            message="Token renovado com sucesso",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao ao renovar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao renovar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao renovar token: {str(e)}"
        )


@router.post(
    "/usuario",
    response_model=StandardResponse,
    summary="Obter dados do usuario",
    description="Obtem dados do usuario autenticado via access_token"
)
async def obter_dados_usuario(
    request: ObterDadosUsuarioRequest,
    service: GovBrService = Depends(get_service)
) -> StandardResponse:
    """Obtem dados do usuario autenticado."""
    try:
        resultado = service.obter_dados_usuario(
            access_token=request.access_token,
        )

        return StandardResponse(
            success=True,
            message="Dados do usuario obtidos com sucesso",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao ao obter usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao obter dados do usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter dados: {str(e)}"
        )


@router.post(
    "/validar-token",
    response_model=StandardResponse,
    summary="Validar token",
    description="Valida se o access_token ainda e valido"
)
async def validar_token(
    request: ValidarTokenRequest,
    service: GovBrService = Depends(get_service)
) -> StandardResponse:
    """Valida token de acesso."""
    try:
        resultado = service.validar_token(
            access_token=request.access_token,
            token_type=request.token_type,
            expires_in=request.expires_in,
            scope=request.scope,
        )

        mensagem = "Token valido" if resultado["valido"] else "Token invalido ou expirado"

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
        logger.error(f"Erro ao validar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao validar token: {str(e)}"
        )


@router.post(
    "/logout",
    response_model=StandardResponse,
    summary="Gerar URL de logout",
    description="Gera URL para logout federado do Gov.br"
)
async def gerar_url_logout(
    request: GerarUrlLogoutRequest,
    service: GovBrService = Depends(get_service)
) -> StandardResponse:
    """Gera URL de logout."""
    try:
        resultado = service.gerar_url_logout(
            id_token=request.id_token,
            post_logout_redirect_uri=request.post_logout_redirect_uri,
        )

        return StandardResponse(
            success=True,
            message="URL de logout gerada com sucesso",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao ao gerar logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao gerar URL de logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar logout: {str(e)}"
        )


@router.post(
    "/empresas",
    response_model=StandardResponse,
    summary="Obter empresas vinculadas",
    description="Obtem empresas vinculadas ao CPF (requer scope govbr_empresa)"
)
async def obter_empresas_vinculadas(
    request: ObterEmpresasRequest,
    service: GovBrService = Depends(get_service)
) -> StandardResponse:
    """Obtem empresas vinculadas ao CPF."""
    try:
        resultado = service.obter_empresas_vinculadas(
            access_token=request.access_token,
            token_type=request.token_type,
            scope=request.scope,
        )

        return StandardResponse(
            success=True,
            message=f"Empresas obtidas: {resultado['quantidade']} encontradas",
            data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validacao ao obter empresas: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao obter empresas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter empresas: {str(e)}"
        )


@router.get(
    "/scopes",
    response_model=StandardResponse,
    summary="Listar scopes disponiveis",
    description="Lista todos os scopes OAuth2 disponiveis no Gov.br"
)
async def listar_scopes(
    service: GovBrService = Depends(get_service)
) -> StandardResponse:
    """Lista scopes disponiveis."""
    try:
        scopes = service.manager.SCOPES

        return StandardResponse(
            success=True,
            message=f"{len(scopes)} scopes disponiveis",
            data={
                "scopes": scopes,
                "quantidade": len(scopes),
            }
        )

    except Exception as e:
        logger.error(f"Erro ao listar scopes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar scopes: {str(e)}"
        )


@router.post(
    "/limpar-pendentes",
    response_model=StandardResponse,
    summary="Limpar autenticacoes pendentes",
    description="Limpa autenticacoes pendentes expiradas (uso interno)"
)
async def limpar_pendentes(
    max_age_minutes: int = Query(
        default=15,
        ge=1,
        le=60,
        description="Idade maxima em minutos"
    ),
    service: GovBrService = Depends(get_service)
) -> StandardResponse:
    """Limpa autenticacoes pendentes expiradas."""
    try:
        removidas = service.limpar_autenticacoes_pendentes(max_age_minutes)

        return StandardResponse(
            success=True,
            message=f"{removidas} autenticacoes pendentes removidas",
            data={
                "removidas": removidas,
                "max_age_minutes": max_age_minutes,
            }
        )

    except Exception as e:
        logger.error(f"Erro ao limpar pendentes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao limpar: {str(e)}"
        )
