"""
Estratégias de autenticação para conectores.
Sprint 33: Integration Framework
"""

import base64
import httpx
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from modules.integrations.connectors.base.exceptions import (
    AuthenticationError,
    TokenExpiredError,
)

logger = logging.getLogger(__name__)


class AuthStrategy(ABC):
    """Interface abstrata para estratégias de autenticação."""

    @abstractmethod
    async def authenticate(self, client: httpx.AsyncClient) -> None:
        """
        Aplica autenticação ao cliente HTTP.

        Args:
            client: Cliente httpx para aplicar headers/auth
        """
        pass

    @abstractmethod
    async def refresh_if_needed(self, client: httpx.AsyncClient) -> bool:
        """
        Atualiza credenciais se necessário.

        Args:
            client: Cliente httpx

        Returns:
            True se houve refresh, False se não foi necessário
        """
        pass

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """Retorna headers de autenticação."""
        pass

    @abstractmethod
    def is_expired(self) -> bool:
        """Verifica se as credenciais expiraram."""
        pass


@dataclass
class APIKeyAuth(AuthStrategy):
    """
    Autenticação via API Key.
    Suporta header ou query parameter.
    """
    api_key: str
    header_name: str = "Authorization"
    header_prefix: str = "Bearer"
    use_query_param: bool = False
    query_param_name: str = "api_key"

    async def authenticate(self, client: httpx.AsyncClient) -> None:
        """Aplica API key ao cliente."""
        if not self.api_key:
            raise AuthenticationError("API key não configurada")

        if self.use_query_param:
            # API key como query parameter
            client.params = client.params.merge({self.query_param_name: self.api_key})
        else:
            # API key como header
            if self.header_prefix:
                value = f"{self.header_prefix} {self.api_key}"
            else:
                value = self.api_key
            client.headers[self.header_name] = value

        logger.debug(f"APIKeyAuth: Autenticação aplicada via {self.header_name}")

    async def refresh_if_needed(self, client: httpx.AsyncClient) -> bool:
        """API keys não expiram normalmente."""
        return False

    def get_headers(self) -> Dict[str, str]:
        """Retorna headers de autenticação."""
        if self.use_query_param:
            return {}

        if self.header_prefix:
            value = f"{self.header_prefix} {self.api_key}"
        else:
            value = self.api_key

        return {self.header_name: value}

    def is_expired(self) -> bool:
        """API keys não expiram."""
        return False


@dataclass
class BasicAuth(AuthStrategy):
    """Autenticação Basic (username:password)."""
    username: str
    password: str

    def _get_basic_token(self) -> str:
        """Gera token Basic."""
        credentials = f"{self.username}:{self.password}"
        return base64.b64encode(credentials.encode()).decode()

    async def authenticate(self, client: httpx.AsyncClient) -> None:
        """Aplica Basic auth ao cliente."""
        if not self.username or not self.password:
            raise AuthenticationError("Username ou password não configurados")

        client.headers["Authorization"] = f"Basic {self._get_basic_token()}"
        logger.debug("BasicAuth: Autenticação aplicada")

    async def refresh_if_needed(self, client: httpx.AsyncClient) -> bool:
        """Basic auth não expira."""
        return False

    def get_headers(self) -> Dict[str, str]:
        """Retorna headers de autenticação."""
        return {"Authorization": f"Basic {self._get_basic_token()}"}

    def is_expired(self) -> bool:
        """Basic auth não expira."""
        return False


@dataclass
class OAuth2ClientCredentials(AuthStrategy):
    """
    Autenticação OAuth2 Client Credentials.
    Gerencia tokens automaticamente com refresh.
    """
    client_id: str
    client_secret: str
    token_url: str
    scopes: Optional[List[str]] = None
    extra_params: Optional[Dict[str, str]] = None

    # Estado do token (gerenciado internamente)
    _access_token: Optional[str] = None
    _refresh_token: Optional[str] = None
    _expires_at: Optional[datetime] = None
    _token_type: str = "Bearer"

    async def authenticate(self, client: httpx.AsyncClient) -> None:
        """Obtém token e aplica ao cliente."""
        if not self._access_token or self.is_expired():
            await self._fetch_token()

        client.headers["Authorization"] = f"{self._token_type} {self._access_token}"
        logger.debug("OAuth2ClientCredentials: Token aplicado")

    async def _fetch_token(self) -> None:
        """Obtém novo token do servidor de autorização."""
        if not self.client_id or not self.client_secret:
            raise AuthenticationError("client_id ou client_secret não configurados")

        if not self.token_url:
            raise AuthenticationError("token_url não configurado")

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        if self.scopes:
            data["scope"] = " ".join(self.scopes)

        if self.extra_params:
            data.update(self.extra_params)

        logger.debug(f"OAuth2: Obtendo token de {self.token_url}")

        async with httpx.AsyncClient() as http_client:
            try:
                response = await http_client.post(
                    self.token_url,
                    data=data,
                    timeout=30.0
                )

                if response.status_code != 200:
                    raise AuthenticationError(
                        f"Falha ao obter token: {response.status_code}",
                        details={"response": response.text}
                    )

                token_data = response.json()
                self._parse_token_response(token_data)

                logger.info("OAuth2: Token obtido com sucesso")

            except httpx.RequestError as e:
                raise AuthenticationError(
                    f"Erro de conexão ao obter token: {str(e)}"
                )

    def _parse_token_response(self, data: Dict[str, Any]) -> None:
        """Parseia resposta do token."""
        self._access_token = data.get("access_token")
        if not self._access_token:
            raise AuthenticationError("Token não retornado na resposta")

        self._refresh_token = data.get("refresh_token")
        self._token_type = data.get("token_type", "Bearer")

        # Calcular expiração
        expires_in = data.get("expires_in", 3600)
        # Reduz 5 minutos para refresh proativo
        self._expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 300)

    async def refresh_if_needed(self, client: httpx.AsyncClient) -> bool:
        """Atualiza token se necessário."""
        if not self.is_expired():
            return False

        logger.info("OAuth2: Token expirado, renovando...")

        if self._refresh_token:
            try:
                await self._refresh_access_token()
            except AuthenticationError:
                # Se refresh falhar, tenta obter novo token
                await self._fetch_token()
        else:
            await self._fetch_token()

        # Atualiza header do cliente
        client.headers["Authorization"] = f"{self._token_type} {self._access_token}"
        return True

    async def _refresh_access_token(self) -> None:
        """Usa refresh token para obter novo access token."""
        if not self._refresh_token:
            raise TokenExpiredError("Refresh token não disponível")

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                self.token_url,
                data=data,
                timeout=30.0
            )

            if response.status_code != 200:
                raise AuthenticationError(
                    f"Falha ao renovar token: {response.status_code}"
                )

            token_data = response.json()
            self._parse_token_response(token_data)

            logger.info("OAuth2: Token renovado com sucesso")

    def get_headers(self) -> Dict[str, str]:
        """Retorna headers de autenticação."""
        if not self._access_token:
            return {}
        return {"Authorization": f"{self._token_type} {self._access_token}"}

    def is_expired(self) -> bool:
        """Verifica se token expirou."""
        if not self._access_token or not self._expires_at:
            return True
        return datetime.utcnow() >= self._expires_at

    def get_token(self) -> Optional[str]:
        """Retorna access token atual."""
        return self._access_token

    def set_tokens(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        token_type: str = "Bearer"
    ) -> None:
        """Define tokens manualmente (útil para carregar do banco)."""
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._expires_at = expires_at
        self._token_type = token_type


@dataclass
class OAuth2AuthorizationCode(AuthStrategy):
    """
    Autenticação OAuth2 Authorization Code.
    Para fluxos que requerem autorização do usuário.
    """
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    redirect_uri: str
    scopes: Optional[List[str]] = None

    # Estado do token
    _access_token: Optional[str] = None
    _refresh_token: Optional[str] = None
    _expires_at: Optional[datetime] = None
    _token_type: str = "Bearer"

    def get_authorization_url(self, state: str) -> str:
        """
        Gera URL de autorização para o usuário.

        Args:
            state: Estado para CSRF protection

        Returns:
            URL para redirecionar o usuário
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state,
        }

        if self.scopes:
            params["scope"] = " ".join(self.scopes)

        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.authorization_url}?{query}"

    async def exchange_code(self, code: str) -> None:
        """
        Troca código de autorização por tokens.

        Args:
            code: Código recebido após autorização
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
        }

        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                self.token_url,
                data=data,
                timeout=30.0
            )

            if response.status_code != 200:
                raise AuthenticationError(
                    f"Falha ao trocar código: {response.status_code}",
                    details={"response": response.text}
                )

            token_data = response.json()
            self._access_token = token_data.get("access_token")
            self._refresh_token = token_data.get("refresh_token")
            self._token_type = token_data.get("token_type", "Bearer")

            expires_in = token_data.get("expires_in", 3600)
            self._expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 300)

            logger.info("OAuth2 AuthCode: Tokens obtidos com sucesso")

    async def authenticate(self, client: httpx.AsyncClient) -> None:
        """Aplica token ao cliente."""
        if not self._access_token:
            raise AuthenticationError(
                "Token não disponível. Execute exchange_code primeiro."
            )

        if self.is_expired():
            await self.refresh_if_needed(client)

        client.headers["Authorization"] = f"{self._token_type} {self._access_token}"

    async def refresh_if_needed(self, client: httpx.AsyncClient) -> bool:
        """Atualiza token se expirado."""
        if not self.is_expired():
            return False

        if not self._refresh_token:
            raise TokenExpiredError("Token expirado e refresh token não disponível")

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                self.token_url,
                data=data,
                timeout=30.0
            )

            if response.status_code != 200:
                raise TokenExpiredError("Falha ao renovar token")

            token_data = response.json()
            self._access_token = token_data.get("access_token")
            self._refresh_token = token_data.get("refresh_token", self._refresh_token)
            self._token_type = token_data.get("token_type", "Bearer")

            expires_in = token_data.get("expires_in", 3600)
            self._expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 300)

        client.headers["Authorization"] = f"{self._token_type} {self._access_token}"
        return True

    def get_headers(self) -> Dict[str, str]:
        """Retorna headers de autenticação."""
        if not self._access_token:
            return {}
        return {"Authorization": f"{self._token_type} {self._access_token}"}

    def is_expired(self) -> bool:
        """Verifica se token expirou."""
        if not self._access_token or not self._expires_at:
            return True
        return datetime.utcnow() >= self._expires_at

    def set_tokens(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> None:
        """Define tokens manualmente."""
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._expires_at = expires_at
