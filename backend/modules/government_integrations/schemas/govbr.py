"""
Schemas para Gov.br - Plataforma de Login Unico do Governo Federal.

Pydantic models para validacao de entrada/saida da API de autenticacao Gov.br.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class NivelAutenticacaoEnum(StrEnum):
    """Nivel de autenticacao Gov.br."""

    BRONZE = "1"
    PRATA = "2"
    OURO = "3"


class TipoDocumentoEnum(StrEnum):
    """Tipo de documento de identidade."""

    CNH = "cnh"
    RG = "rg"
    PASSAPORTE = "passaporte"
    TITULO_ELEITOR = "titulo_eleitor"
    CTPS = "ctps"


class AmbienteGovBrEnum(StrEnum):
    """Ambiente do Gov.br."""

    PRODUCAO = "producao"
    STAGING = "staging"


# ============== Request Schemas ==============


class GerarUrlAutorizacaoRequest(BaseModel):
    """Request para gerar URL de autorizacao OAuth2."""

    scopes: list[str] | None = Field(
        default=None, description="Scopes OAuth2 solicitados (openid, email, profile, govbr_empresa, etc.)"
    )
    nivel_minimo: NivelAutenticacaoEnum | None = Field(
        default=None, description="Nivel minimo de autenticacao requerido"
    )

    class Config:
        json_schema_extra = {
            "example": {"scopes": ["openid", "email", "profile", "govbr_empresa"], "nivel_minimo": "2"}
        }


class TrocarCodigoRequest(BaseModel):
    """Request para trocar codigo de autorizacao por tokens."""

    code: str = Field(..., min_length=1, description="Codigo de autorizacao recebido no callback")
    state: str = Field(..., min_length=1, description="State recebido no callback para validacao CSRF")
    code_verifier: str | None = Field(default=None, description="Code verifier PKCE (se nao armazenado no servidor)")

    class Config:
        json_schema_extra = {
            "example": {"code": "abc123def456", "state": "random_state_string", "code_verifier": "pkce_verifier_string"}
        }


class RenovarTokenRequest(BaseModel):
    """Request para renovar access_token usando refresh_token."""

    refresh_token: str = Field(..., min_length=1, description="Refresh token para renovacao")

    class Config:
        json_schema_extra = {"example": {"refresh_token": "refresh_token_string"}}


class ObterDadosUsuarioRequest(BaseModel):
    """Request para obter dados do usuario autenticado."""

    access_token: str = Field(..., min_length=1, description="Access token do usuario")

    class Config:
        json_schema_extra = {"example": {"access_token": "access_token_string"}}


class ValidarTokenRequest(BaseModel):
    """Request para validar token de acesso."""

    access_token: str = Field(..., min_length=1, description="Access token a validar")
    token_type: str = Field(default="Bearer", description="Tipo do token")
    expires_in: int = Field(default=0, ge=0, description="Tempo de expiracao em segundos")
    scope: str | None = Field(default=None, description="Scopes do token")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "access_token_string",
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": "openid email profile",
            }
        }


class GerarUrlLogoutRequest(BaseModel):
    """Request para gerar URL de logout."""

    id_token: str = Field(..., min_length=1, description="ID Token do usuario")
    post_logout_redirect_uri: str | None = Field(default=None, description="URI de redirecionamento apos logout")

    class Config:
        json_schema_extra = {
            "example": {
                "id_token": "id_token_string",
                "post_logout_redirect_uri": "https://app.example.com/logout-callback",
            }
        }


class ObterEmpresasRequest(BaseModel):
    """Request para obter empresas vinculadas ao CPF."""

    access_token: str = Field(..., min_length=1, description="Access token com scope govbr_empresa")
    token_type: str = Field(default="Bearer", description="Tipo do token")
    scope: str | None = Field(default=None, description="Scopes do token (deve incluir govbr_empresa)")

    class Config:
        json_schema_extra = {
            "example": {"access_token": "access_token_string", "token_type": "Bearer", "scope": "openid govbr_empresa"}
        }


# ============== Response Schemas ==============


class UrlAutorizacaoResponse(BaseModel):
    """Response com URL de autorizacao gerada."""

    url: str = Field(..., description="URL para redirecionar o usuario")
    state: str = Field(..., description="State para validacao no callback")
    nonce: str = Field(..., description="Nonce para validacao do ID token")
    code_verifier: str = Field(..., description="Code verifier PKCE (armazenar no servidor)")


class TokenGovBrResponse(BaseModel):
    """Response com tokens OAuth2."""

    access_token: str = Field(..., description="Token de acesso")
    token_type: str = Field(default="Bearer", description="Tipo do token")
    expires_in: int = Field(default=0, description="Tempo de expiracao em segundos")
    refresh_token: str | None = Field(default=None, description="Token para renovacao")
    scope: str | None = Field(default=None, description="Scopes concedidos")
    id_token: str | None = Field(default=None, description="ID Token JWT")
    data_obtencao: str = Field(..., description="Data/hora de obtencao do token")


class UsuarioGovBrResponse(BaseModel):
    """Response com dados do usuario autenticado."""

    cpf: str = Field(..., description="CPF do usuario")
    nome: str = Field(..., description="Nome completo")
    email: str | None = Field(default=None, description="E-mail")
    telefone: str | None = Field(default=None, description="Telefone")
    foto: str | None = Field(default=None, description="URL ou Base64 da foto")
    nivel_autenticacao: str = Field(..., description="Nivel de autenticacao (1=Bronze, 2=Prata, 3=Ouro)")
    data_nascimento: str | None = Field(default=None, description="Data de nascimento")
    nome_mae: str | None = Field(default=None, description="Nome da mae")
    cnpj_vinculados: list[str] = Field(default_factory=list, description="CNPJs vinculados")
    empresas: list[dict[str, Any]] = Field(default_factory=list, description="Empresas vinculadas")


class ValidacaoTokenResponse(BaseModel):
    """Response da validacao de token."""

    valido: bool = Field(..., description="Se o token e valido")
    expiracao: str | None = Field(default=None, description="Data/hora de expiracao")
    scopes: list[str] = Field(default_factory=list, description="Scopes do token")


class EmpresaVinculadaResponse(BaseModel):
    """Empresa vinculada ao CPF."""

    cnpj: str = Field(..., description="CNPJ da empresa")
    razao_social: str = Field(..., description="Razao social")
    nome_fantasia: str | None = Field(default=None, description="Nome fantasia")
    participacao: str | None = Field(default=None, description="Tipo de participacao")
    data_entrada: str | None = Field(default=None, description="Data de entrada na empresa")


class StatusGovBrResponse(BaseModel):
    """Response de status do Gov.br."""

    ambiente: str = Field(..., description="Ambiente configurado (producao/staging)")
    url: str = Field(..., description="URL base do Gov.br")
    client_id_configurado: bool = Field(..., description="Se client_id esta configurado")
    redirect_uri: str = Field(..., description="URI de redirecionamento configurada")
    scopes_disponiveis: list[str] = Field(..., description="Scopes disponiveis")
    servicos: list[str] = Field(..., description="Servicos disponiveis")
