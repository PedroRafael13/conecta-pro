"""
Gov.br - Plataforma de Login Único do Governo Federal.

Portal: https://www.gov.br/governodigital/pt-br/conta-gov-br
Documentação: https://manual-roteiro-integracao-login-unico.servicos.gov.br/

O Gov.br é a plataforma de autenticação única do governo federal,
usada para acessar diversos serviços digitais.

Níveis de conta:
- Bronze: Cadastro básico (auto-cadastro)
- Prata: Validação biométrica (bancos, TSE) ou certificado digital
- Ouro: Validação biométrica (INSS, TSE) ou certificado digital de pessoa física

Fluxo OAuth2:
1. Redireciona para Gov.br
2. Usuário autentica
3. Gov.br redireciona com código de autorização
4. Sistema troca código por tokens
5. Usa access_token para acessar APIs
"""

import logging
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class NivelAutenticacao(str, Enum):
    """Nível de autenticação Gov.br."""
    BRONZE = "1"
    PRATA = "2"
    OURO = "3"


class TipoDocumento(str, Enum):
    """Tipo de documento de identidade."""
    CNH = "cnh"
    RG = "rg"
    PASSAPORTE = "passaporte"
    TITULO_ELEITOR = "titulo_eleitor"
    CTPS = "ctps"


@dataclass
class UsuarioGovBr:
    """Dados do usuário autenticado via Gov.br."""
    cpf: str
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    foto: Optional[str] = None  # URL ou Base64
    nivel_autenticacao: NivelAutenticacao = NivelAutenticacao.BRONZE

    # Dados adicionais
    data_nascimento: Optional[str] = None
    nome_mae: Optional[str] = None
    cnpj_vinculados: List[str] = field(default_factory=list)

    # Empresas (se solicitado scope empresas)
    empresas: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TokenGovBr:
    """Tokens OAuth2 do Gov.br."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 0
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    id_token: Optional[str] = None

    # Metadados
    data_obtencao: datetime = field(default_factory=datetime.now)

    @property
    def expiracao(self) -> datetime:
        return self.data_obtencao + timedelta(seconds=self.expires_in)

    @property
    def expirado(self) -> bool:
        return datetime.now() >= self.expiracao


class GovBrManager:
    """
    Gerenciador de integração com Gov.br.

    Implementa fluxo OAuth2 Authorization Code com PKCE.
    """

    # URLs Gov.br
    URL_PRODUCAO = "https://sso.acesso.gov.br"
    URL_STAGING = "https://sso.staging.acesso.gov.br"

    # Endpoints
    ENDPOINT_AUTHORIZE = "/authorize"
    ENDPOINT_TOKEN = "/token"
    ENDPOINT_USERINFO = "/userinfo"
    ENDPOINT_LOGOUT = "/logout"
    ENDPOINT_JWKS = "/jwks"

    # Scopes disponíveis
    SCOPES = {
        "openid": "Identificação básica",
        "email": "E-mail do usuário",
        "phone": "Telefone do usuário",
        "profile": "Perfil completo",
        "govbr_empresa": "Vínculos com empresas",
        "govbr_confiabilidades": "Nível de confiabilidade",
    }

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        ambiente: str = "producao",
    ):
        """
        Inicializa o gerenciador.

        Args:
            client_id: ID do cliente OAuth2
            client_secret: Secret do cliente
            redirect_uri: URI de redirecionamento
            ambiente: 'producao' ou 'staging'
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.ambiente = ambiente
        self.base_url = self.URL_PRODUCAO if ambiente == "producao" else self.URL_STAGING

        # PKCE
        self._code_verifier: Optional[str] = None
        self._code_challenge: Optional[str] = None
        self._state: Optional[str] = None
        self._nonce: Optional[str] = None

    def gerar_url_autorizacao(
        self,
        scopes: Optional[List[str]] = None,
        nivel_minimo: Optional[NivelAutenticacao] = None,
    ) -> Dict[str, str]:
        """
        Gera URL de autorização para redirecionamento.

        Args:
            scopes: Scopes solicitados
            nivel_minimo: Nível mínimo de autenticação requerido

        Returns:
            Dict com URL e parâmetros de verificação
        """
        # Gera PKCE
        self._code_verifier = self._gerar_code_verifier()
        self._code_challenge = self._gerar_code_challenge(self._code_verifier)
        self._state = secrets.token_urlsafe(32)
        self._nonce = secrets.token_urlsafe(32)

        # Scopes
        if scopes is None:
            scopes = ["openid", "email", "profile", "govbr_empresa"]

        scope_str = " ".join(scopes)

        # Parâmetros
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": scope_str,
            "state": self._state,
            "nonce": self._nonce,
            "code_challenge": self._code_challenge,
            "code_challenge_method": "S256",
        }

        # Nível mínimo
        if nivel_minimo:
            params["acr_values"] = f"urn:brasil:gov:br:1#nivel_{nivel_minimo.value}"

        url = f"{self.base_url}{self.ENDPOINT_AUTHORIZE}?{urlencode(params)}"

        logger.info("Gerada URL de autorização Gov.br")

        return {
            "url": url,
            "state": self._state,
            "nonce": self._nonce,
            "code_verifier": self._code_verifier,
        }

    def trocar_codigo_por_token(
        self,
        code: str,
        state: str,
        code_verifier: Optional[str] = None,
    ) -> TokenGovBr:
        """
        Troca código de autorização por tokens.

        Args:
            code: Código de autorização
            state: State recebido no callback
            code_verifier: Code verifier PKCE

        Returns:
            Tokens OAuth2
        """
        # Valida state
        if self._state and state != self._state:
            raise ValueError("State inválido - possível ataque CSRF")

        verifier = code_verifier or self._code_verifier
        if not verifier:
            raise ValueError("Code verifier não disponível")

        # Parâmetros da requisição
        params = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "code_verifier": verifier,
        }

        # Autenticação do cliente
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        url = f"{self.base_url}{self.ENDPOINT_TOKEN}"

        logger.info("Trocando código por token Gov.br")

        # Na implementação real, faria a requisição HTTP
        # Aqui retorna um token simulado para estrutura
        return TokenGovBr(
            access_token="",
            token_type="Bearer",
            expires_in=3600,
            scope=" ".join(["openid", "email", "profile"]),
        )

    def obter_dados_usuario(self, token: TokenGovBr) -> UsuarioGovBr:
        """
        Obtém dados do usuário autenticado.

        Args:
            token: Token de acesso

        Returns:
            Dados do usuário
        """
        if token.expirado:
            raise ValueError("Token expirado")

        headers = {
            "Authorization": f"{token.token_type} {token.access_token}",
        }

        url = f"{self.base_url}{self.ENDPOINT_USERINFO}"

        logger.info("Obtendo dados do usuário Gov.br")

        # Na implementação real, faria a requisição HTTP
        # Aqui retorna estrutura vazia
        return UsuarioGovBr(
            cpf="",
            nome="",
        )

    def renovar_token(self, refresh_token: str) -> TokenGovBr:
        """
        Renova o access_token usando o refresh_token.

        Args:
            refresh_token: Refresh token

        Returns:
            Novos tokens
        """
        params = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        url = f"{self.base_url}{self.ENDPOINT_TOKEN}"

        logger.info("Renovando token Gov.br")

        return TokenGovBr(
            access_token="",
            token_type="Bearer",
            expires_in=3600,
        )

    def gerar_url_logout(
        self,
        id_token: str,
        post_logout_redirect_uri: Optional[str] = None,
    ) -> str:
        """
        Gera URL de logout do Gov.br.

        Args:
            id_token: ID Token do usuário
            post_logout_redirect_uri: URI de redirecionamento após logout

        Returns:
            URL de logout
        """
        params = {
            "id_token_hint": id_token,
        }

        if post_logout_redirect_uri:
            params["post_logout_redirect_uri"] = post_logout_redirect_uri

        url = f"{self.base_url}{self.ENDPOINT_LOGOUT}?{urlencode(params)}"

        logger.info("Gerada URL de logout Gov.br")
        return url

    def validar_token(self, token: TokenGovBr) -> Dict[str, Any]:
        """
        Valida o token de acesso.

        Args:
            token: Token a validar

        Returns:
            Resultado da validação
        """
        return {
            "valido": not token.expirado,
            "expiracao": token.expiracao.isoformat() if token.expires_in else None,
            "scopes": token.scope.split() if token.scope else [],
        }

    def obter_empresas_vinculadas(self, token: TokenGovBr) -> List[Dict[str, Any]]:
        """
        Obtém empresas vinculadas ao CPF (requer scope govbr_empresa).

        Args:
            token: Token de acesso com scope govbr_empresa

        Returns:
            Lista de empresas vinculadas
        """
        if "govbr_empresa" not in (token.scope or ""):
            raise ValueError("Token não possui scope govbr_empresa")

        logger.info("Consultando empresas vinculadas via Gov.br")

        return []

    def _gerar_code_verifier(self) -> str:
        """Gera code verifier para PKCE."""
        return secrets.token_urlsafe(64)[:128]

    def _gerar_code_challenge(self, verifier: str) -> str:
        """Gera code challenge a partir do verifier."""
        digest = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
