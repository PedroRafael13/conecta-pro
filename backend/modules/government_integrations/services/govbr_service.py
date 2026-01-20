"""
Service para Gov.br - Plataforma de Login Unico do Governo Federal.

Camada de servico para operacoes de autenticacao Gov.br.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from ..core.govbr import (
    GovBrManager,
    NivelAutenticacao,
    TipoDocumento,
    UsuarioGovBr,
    TokenGovBr,
)

logger = logging.getLogger(__name__)


class GovBrService:
    """Service para operacoes de autenticacao Gov.br."""

    def __init__(self):
        """Inicializa o service."""
        self.client_id = os.getenv("GOVBR_CLIENT_ID", "")
        self.client_secret = os.getenv("GOVBR_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv(
            "GOVBR_REDIRECT_URI",
            "https://app.conectaplus.com.br/auth/govbr/callback"
        )
        self.ambiente = os.getenv("GOVBR_AMBIENTE", "producao")

        # Armazenamento temporario de code_verifier (em producao, usar Redis ou sessao)
        self._pending_auth: Dict[str, Dict[str, str]] = {}

        self.manager = GovBrManager(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            ambiente=self.ambiente,
        )

        logger.info(
            f"Gov.br Service inicializado - Ambiente: {self.ambiente}, "
            f"Client ID configurado: {bool(self.client_id)}"
        )

    def gerar_url_autorizacao(
        self,
        scopes: Optional[List[str]] = None,
        nivel_minimo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gera URL de autorizacao OAuth2 para redirecionar o usuario.

        Args:
            scopes: Scopes OAuth2 solicitados
            nivel_minimo: Nivel minimo de autenticacao ('1', '2', '3')

        Returns:
            Dict com URL e parametros de verificacao
        """
        # Converte nivel minimo se fornecido
        nivel_enum = None
        if nivel_minimo:
            try:
                nivel_enum = NivelAutenticacao(nivel_minimo)
            except ValueError:
                logger.warning(f"Nivel de autenticacao invalido: {nivel_minimo}")

        resultado = self.manager.gerar_url_autorizacao(
            scopes=scopes,
            nivel_minimo=nivel_enum,
        )

        # Armazena code_verifier para uso no callback
        state = resultado["state"]
        self._pending_auth[state] = {
            "code_verifier": resultado["code_verifier"],
            "nonce": resultado["nonce"],
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"URL de autorizacao Gov.br gerada - State: {state[:8]}...")

        return {
            "url": resultado["url"],
            "state": resultado["state"],
            "nonce": resultado["nonce"],
            "code_verifier": resultado["code_verifier"],
        }

    def trocar_codigo_por_token(
        self,
        code: str,
        state: str,
        code_verifier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Troca codigo de autorizacao por tokens OAuth2.

        Args:
            code: Codigo de autorizacao recebido no callback
            state: State para validacao CSRF
            code_verifier: Code verifier PKCE (opcional se armazenado)

        Returns:
            Dict com tokens OAuth2
        """
        # Recupera code_verifier armazenado se nao fornecido
        verifier = code_verifier
        if not verifier and state in self._pending_auth:
            verifier = self._pending_auth[state].get("code_verifier")
            # Remove dados pendentes apos uso
            del self._pending_auth[state]

        if not verifier:
            raise ValueError("Code verifier nao encontrado - state invalido ou expirado")

        token = self.manager.trocar_codigo_por_token(
            code=code,
            state=state,
            code_verifier=verifier,
        )

        logger.info("Codigo trocado por token Gov.br com sucesso")

        return {
            "access_token": token.access_token,
            "token_type": token.token_type,
            "expires_in": token.expires_in,
            "refresh_token": token.refresh_token,
            "scope": token.scope,
            "id_token": token.id_token,
            "data_obtencao": token.data_obtencao.isoformat(),
        }

    def obter_dados_usuario(
        self,
        access_token: str,
        token_type: str = "Bearer",
        expires_in: int = 3600,
        scope: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Obtem dados do usuario autenticado.

        Args:
            access_token: Token de acesso
            token_type: Tipo do token
            expires_in: Tempo de expiracao
            scope: Scopes do token

        Returns:
            Dict com dados do usuario
        """
        token = TokenGovBr(
            access_token=access_token,
            token_type=token_type,
            expires_in=expires_in,
            scope=scope,
        )

        usuario = self.manager.obter_dados_usuario(token)

        logger.info(f"Dados do usuario Gov.br obtidos - CPF: {usuario.cpf[:3]}***")

        return {
            "cpf": usuario.cpf,
            "nome": usuario.nome,
            "email": usuario.email,
            "telefone": usuario.telefone,
            "foto": usuario.foto,
            "nivel_autenticacao": usuario.nivel_autenticacao.value,
            "data_nascimento": usuario.data_nascimento,
            "nome_mae": usuario.nome_mae,
            "cnpj_vinculados": usuario.cnpj_vinculados,
            "empresas": usuario.empresas,
        }

    def renovar_token(
        self,
        refresh_token: str,
    ) -> Dict[str, Any]:
        """
        Renova access_token usando refresh_token.

        Args:
            refresh_token: Refresh token

        Returns:
            Dict com novos tokens
        """
        token = self.manager.renovar_token(refresh_token)

        logger.info("Token Gov.br renovado com sucesso")

        return {
            "access_token": token.access_token,
            "token_type": token.token_type,
            "expires_in": token.expires_in,
            "refresh_token": token.refresh_token,
            "scope": token.scope,
            "id_token": token.id_token,
            "data_obtencao": token.data_obtencao.isoformat(),
        }

    def validar_token(
        self,
        access_token: str,
        token_type: str = "Bearer",
        expires_in: int = 0,
        scope: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Valida token de acesso.

        Args:
            access_token: Token a validar
            token_type: Tipo do token
            expires_in: Tempo de expiracao
            scope: Scopes do token

        Returns:
            Dict com resultado da validacao
        """
        token = TokenGovBr(
            access_token=access_token,
            token_type=token_type,
            expires_in=expires_in,
            scope=scope,
        )

        resultado = self.manager.validar_token(token)

        logger.info(f"Token Gov.br validado - Valido: {resultado['valido']}")

        return {
            "valido": resultado["valido"],
            "expiracao": resultado.get("expiracao"),
            "scopes": resultado.get("scopes", []),
        }

    def gerar_url_logout(
        self,
        id_token: str,
        post_logout_redirect_uri: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gera URL de logout do Gov.br.

        Args:
            id_token: ID Token do usuario
            post_logout_redirect_uri: URI de redirecionamento apos logout

        Returns:
            Dict com URL de logout
        """
        url = self.manager.gerar_url_logout(
            id_token=id_token,
            post_logout_redirect_uri=post_logout_redirect_uri,
        )

        logger.info("URL de logout Gov.br gerada")

        return {
            "url": url,
            "post_logout_redirect_uri": post_logout_redirect_uri,
        }

    def obter_empresas_vinculadas(
        self,
        access_token: str,
        token_type: str = "Bearer",
        scope: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Obtem empresas vinculadas ao CPF do usuario.

        Args:
            access_token: Token de acesso com scope govbr_empresa
            token_type: Tipo do token
            scope: Scopes do token

        Returns:
            Dict com lista de empresas
        """
        token = TokenGovBr(
            access_token=access_token,
            token_type=token_type,
            expires_in=3600,  # Valor padrao
            scope=scope,
        )

        empresas = self.manager.obter_empresas_vinculadas(token)

        logger.info(f"Empresas vinculadas obtidas: {len(empresas)}")

        return {
            "quantidade": len(empresas),
            "empresas": empresas,
            "data_consulta": datetime.now().isoformat(),
        }

    def validar_status(self) -> Dict[str, Any]:
        """
        Valida status da configuracao Gov.br.

        Returns:
            Dict com status da configuracao
        """
        return {
            "ambiente": self.ambiente,
            "url": self.manager.base_url,
            "client_id_configurado": bool(self.client_id),
            "redirect_uri": self.redirect_uri,
            "scopes_disponiveis": list(self.manager.SCOPES.keys()),
            "servicos": [
                "Autenticacao OAuth2/OIDC",
                "Login com PKCE",
                "Obtencao de dados do usuario",
                "Renovacao de tokens",
                "Logout federado",
                "Consulta de empresas vinculadas",
            ],
        }

    def limpar_autenticacoes_pendentes(self, max_age_minutes: int = 15) -> int:
        """
        Limpa autenticacoes pendentes antigas.

        Args:
            max_age_minutes: Idade maxima em minutos

        Returns:
            Quantidade de entradas removidas
        """
        now = datetime.now()
        to_remove = []

        for state, data in self._pending_auth.items():
            try:
                timestamp = datetime.fromisoformat(data["timestamp"])
                age_minutes = (now - timestamp).total_seconds() / 60
                if age_minutes > max_age_minutes:
                    to_remove.append(state)
            except (KeyError, ValueError):
                to_remove.append(state)

        for state in to_remove:
            del self._pending_auth[state]

        if to_remove:
            logger.info(f"Removidas {len(to_remove)} autenticacoes pendentes expiradas")

        return len(to_remove)


# Singleton
_govbr_service: Optional[GovBrService] = None


def get_govbr_service() -> GovBrService:
    """Retorna instancia singleton do service."""
    global _govbr_service
    if _govbr_service is None:
        _govbr_service = GovBrService()
    return _govbr_service
