"""
Cliente HashiCorp Vault para Gerenciamento de Secrets.

Fornece acesso seguro a credenciais e certificados.
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

try:
    import hvac
    from hvac.exceptions import VaultError

    HVAC_AVAILABLE = True
except ImportError:
    HVAC_AVAILABLE = False
    hvac = None

    class VaultError(Exception):
        pass

    class InvalidPathError(Exception):
        """Erro quando caminho não é encontrado no Vault."""

        pass


logger = logging.getLogger(__name__)


@dataclass
class VaultConfig:
    """Configuração do Vault."""

    url: str = "http://localhost:8200"
    token: str | None = None
    role_id: str | None = None
    secret_id: str | None = None
    namespace: str | None = None
    mount_point: str = "secret"
    verify_ssl: bool = True

    # Paths padrão
    path_certificados: str = "government/certificates"
    path_credenciais: str = "government/credentials"
    path_config: str = "government/config"

    @classmethod
    def from_env(cls) -> "VaultConfig":
        """Cria configuração a partir de variáveis de ambiente."""
        return cls(
            url=os.getenv("VAULT_ADDR", "http://localhost:8200"),
            token=os.getenv("VAULT_TOKEN"),
            role_id=os.getenv("VAULT_ROLE_ID"),
            secret_id=os.getenv("VAULT_SECRET_ID"),
            namespace=os.getenv("VAULT_NAMESPACE"),
            verify_ssl=os.getenv("VAULT_SKIP_VERIFY", "").lower() != "true",
        )


class VaultClient:
    """
    Cliente para interação com HashiCorp Vault.

    Suporta:
    - Autenticação por token ou AppRole
    - KV secrets engine v2
    - Cache local de secrets
    - Renovação automática de token
    """

    def __init__(self, config: VaultConfig | None = None):
        if not HVAC_AVAILABLE:
            logger.warning("hvac não instalado. VaultClient não estará funcional.")
        self.config = config or VaultConfig.from_env()
        self._client = None
        self._cache: dict[str, dict] = {}
        self._cache_expiry: dict[str, datetime] = {}
        self._lock = asyncio.Lock()

    async def _get_client(self):
        """Obtém cliente Vault autenticado."""
        if not HVAC_AVAILABLE:
            raise VaultError("Biblioteca hvac não instalada")
        if self._client is not None and self._client.is_authenticated():
            return self._client

        async with self._lock:
            # Double-check após obter lock
            if self._client is not None and self._client.is_authenticated():
                return self._client

            self._client = hvac.Client(
                url=self.config.url,
                token=self.config.token,
                namespace=self.config.namespace,
                verify=self.config.verify_ssl,
            )

            # Se não tem token, tentar AppRole
            if not self.config.token and self.config.role_id:
                try:
                    response = self._client.auth.approle.login(
                        role_id=self.config.role_id,
                        secret_id=self.config.secret_id,
                    )
                    self._client.token = response["auth"]["client_token"]
                    logger.info("Autenticado no Vault via AppRole")
                except Exception as e:
                    logger.error(f"Falha na autenticação AppRole: {e}")
                    raise

            if not self._client.is_authenticated():
                raise VaultError("Não foi possível autenticar no Vault")

            return self._client

    async def ler_secret(self, path: str, use_cache: bool = True, cache_ttl: int = 300) -> dict[str, Any] | None:
        """
        Lê um secret do Vault.

        Args:
            path: Caminho do secret
            use_cache: Se deve usar cache
            cache_ttl: TTL do cache em segundos

        Returns:
            Dados do secret ou None se não encontrado
        """
        cache_key = f"{self.config.mount_point}/{path}"

        # Verificar cache
        if use_cache and cache_key in self._cache:
            if datetime.utcnow() < self._cache_expiry.get(cache_key, datetime.min):
                logger.debug(f"Cache hit para secret: {path}")
                return self._cache[cache_key]

        try:
            client = await self._get_client()
            response = client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=self.config.mount_point,
            )

            data = response.get("data", {}).get("data", {})

            # Atualizar cache
            if use_cache:
                self._cache[cache_key] = data
                self._cache_expiry[cache_key] = datetime.utcnow() + timedelta(seconds=cache_ttl)

            logger.debug(f"Secret lido: {path}")
            return data

        except InvalidPathError:
            logger.warning(f"Secret não encontrado: {path}")
            return None

        except Exception as e:
            logger.error(f"Erro ao ler secret {path}: {e}")
            raise

    async def escrever_secret(self, path: str, data: dict[str, Any], cas: int | None = None) -> bool:
        """
        Escreve um secret no Vault.

        Args:
            path: Caminho do secret
            data: Dados a escrever
            cas: Check-and-set version (para escrita condicional)

        Returns:
            True se escrito com sucesso
        """
        try:
            client = await self._get_client()
            client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=data,
                cas=cas,
                mount_point=self.config.mount_point,
            )

            # Invalidar cache
            cache_key = f"{self.config.mount_point}/{path}"
            self._cache.pop(cache_key, None)
            self._cache_expiry.pop(cache_key, None)

            logger.info(f"Secret escrito: {path}")
            return True

        except Exception as e:
            logger.error(f"Erro ao escrever secret {path}: {e}")
            return False

    async def deletar_secret(self, path: str) -> bool:
        """Deleta um secret do Vault."""
        try:
            client = await self._get_client()
            client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=path,
                mount_point=self.config.mount_point,
            )

            # Limpar cache
            cache_key = f"{self.config.mount_point}/{path}"
            self._cache.pop(cache_key, None)
            self._cache_expiry.pop(cache_key, None)

            logger.info(f"Secret deletado: {path}")
            return True

        except Exception as e:
            logger.error(f"Erro ao deletar secret {path}: {e}")
            return False

    async def listar_secrets(self, path: str) -> list[str]:
        """Lista secrets em um path."""
        try:
            client = await self._get_client()
            response = client.secrets.kv.v2.list_secrets(
                path=path,
                mount_point=self.config.mount_point,
            )
            return response.get("data", {}).get("keys", [])

        except InvalidPathError:
            return []

        except Exception as e:
            logger.error(f"Erro ao listar secrets em {path}: {e}")
            return []

    # Métodos específicos para integrações governamentais

    async def obter_certificado(self, tenant_id: str, tipo: str = "e-cnpj") -> dict[str, Any] | None:
        """
        Obtém certificado digital do tenant.

        Args:
            tenant_id: ID do tenant
            tipo: Tipo do certificado (e-cnpj, e-cpf, nfe)

        Returns:
            Dicionário com pfx_base64, senha, validade
        """
        path = f"{self.config.path_certificados}/{tenant_id}/{tipo}"
        return await self.ler_secret(path, cache_ttl=60)

    async def salvar_certificado(
        self, tenant_id: str, tipo: str, pfx_base64: str, senha: str, validade: datetime, metadata: dict | None = None
    ) -> bool:
        """
        Salva certificado digital no Vault.

        Args:
            tenant_id: ID do tenant
            tipo: Tipo do certificado
            pfx_base64: Certificado em base64
            senha: Senha do certificado
            validade: Data de validade
            metadata: Metadados adicionais

        Returns:
            True se salvo com sucesso
        """
        path = f"{self.config.path_certificados}/{tenant_id}/{tipo}"
        data = {
            "pfx_base64": pfx_base64,
            "senha": senha,
            "validade": validade.isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            **(metadata or {}),
        }
        return await self.escrever_secret(path, data)

    async def obter_credencial_servico(self, tenant_id: str, servico: str) -> dict[str, Any] | None:
        """
        Obtém credencial para um serviço governamental.

        Args:
            tenant_id: ID do tenant
            servico: Nome do serviço (esocial, fgts, nfse, etc)

        Returns:
            Dicionário com credenciais específicas do serviço
        """
        path = f"{self.config.path_credenciais}/{tenant_id}/{servico}"
        return await self.ler_secret(path, cache_ttl=300)

    async def salvar_credencial_servico(self, tenant_id: str, servico: str, credenciais: dict[str, Any]) -> bool:
        """
        Salva credencial de serviço no Vault.

        Args:
            tenant_id: ID do tenant
            servico: Nome do serviço
            credenciais: Dados da credencial

        Returns:
            True se salvo com sucesso
        """
        path = f"{self.config.path_credenciais}/{tenant_id}/{servico}"
        data = {
            **credenciais,
            "updated_at": datetime.utcnow().isoformat(),
        }
        return await self.escrever_secret(path, data)

    async def listar_certificados_tenant(self, tenant_id: str) -> list[str]:
        """Lista certificados de um tenant."""
        path = f"{self.config.path_certificados}/{tenant_id}"
        return await self.listar_secrets(path)

    async def listar_credenciais_tenant(self, tenant_id: str) -> list[str]:
        """Lista credenciais de um tenant."""
        path = f"{self.config.path_credenciais}/{tenant_id}"
        return await self.listar_secrets(path)

    async def obter_config_global(self, chave: str) -> dict[str, Any] | None:
        """Obtém configuração global do sistema."""
        path = f"{self.config.path_config}/{chave}"
        return await self.ler_secret(path)

    async def healthcheck(self) -> dict[str, Any]:
        """Verifica saúde da conexão com Vault."""
        try:
            client = await self._get_client()
            status = client.sys.read_health_status(method="GET")

            return {
                "status": "ok",
                "initialized": status.get("initialized", False),
                "sealed": status.get("sealed", True),
                "version": status.get("version", "unknown"),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def limpar_cache(self):
        """Limpa todo o cache local."""
        self._cache.clear()
        self._cache_expiry.clear()
        logger.info("Cache do Vault limpo")


# Instância singleton
_vault_client_instance: VaultClient | None = None


def get_vault_client() -> VaultClient:
    """Obtém instância do cliente Vault."""
    global _vault_client_instance
    if _vault_client_instance is None:
        _vault_client_instance = VaultClient()
    return _vault_client_instance
