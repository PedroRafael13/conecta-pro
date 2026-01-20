"""
Provedor de Credenciais para Serviços Governamentais.

Fornece credenciais unificadas para diferentes serviços.
"""

from datetime import datetime
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum
import logging

from .vault_client import VaultClient, get_vault_client
from .certificate_manager import (
    GerenciadorCertificados,
    CertificadoInfo,
    TipoCertificado,
)

logger = logging.getLogger(__name__)


class TipoCredencial(Enum):
    """Tipos de credencial por serviço."""
    # SEFAZ - usa certificado digital
    SEFAZ_NFE = "sefaz_nfe"
    SEFAZ_CTE = "sefaz_cte"
    SEFAZ_MDFE = "sefaz_mdfe"

    # eSocial - certificado + código de acesso
    ESOCIAL = "esocial"

    # FGTS Digital
    FGTS_DIGITAL = "fgts_digital"

    # NFS-e - varia por município
    NFSE_NACIONAL = "nfse_nacional"
    NFSE_MUNICIPAL = "nfse_municipal"

    # SPED
    SPED = "sped"

    # Receita Federal
    RECEITA_FEDERAL = "receita_federal"


@dataclass
class CredencialGoverno:
    """Credencial para acesso a serviço governamental."""
    tenant_id: str
    servico: TipoCredencial
    tipo_autenticacao: str  # "certificado", "usuario_senha", "token", "oauth"

    # Certificado (se aplicável)
    certificado_tipo: Optional[TipoCertificado] = None
    certificado_info: Optional[CertificadoInfo] = None

    # Usuário/senha (se aplicável)
    usuario: Optional[str] = None
    senha: Optional[str] = None

    # Token (se aplicável)
    token: Optional[str] = None
    token_expiracao: Optional[datetime] = None

    # OAuth (se aplicável)
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

    # Metadados
    ambiente: str = "producao"  # producao, homologacao
    codigo_municipio: Optional[str] = None  # Para NFS-e municipal
    inscricao_municipal: Optional[str] = None

    # Validação
    valida: bool = True
    erro: Optional[str] = None
    ultima_validacao: Optional[datetime] = None


class ProvedorCredenciais:
    """
    Provê credenciais unificadas para serviços governamentais.

    Abstrai a complexidade de diferentes métodos de autenticação.
    """

    # Mapeamento de serviço para tipo de certificado
    CERTIFICADO_POR_SERVICO = {
        TipoCredencial.SEFAZ_NFE: TipoCertificado.E_CNPJ,
        TipoCredencial.SEFAZ_CTE: TipoCertificado.E_CNPJ,
        TipoCredencial.SEFAZ_MDFE: TipoCertificado.E_CNPJ,
        TipoCredencial.ESOCIAL: TipoCertificado.E_CNPJ,
        TipoCredencial.FGTS_DIGITAL: TipoCertificado.E_CNPJ,
        TipoCredencial.SPED: TipoCertificado.E_CNPJ,
    }

    # Tipo de autenticação por serviço
    TIPO_AUTENTICACAO = {
        TipoCredencial.SEFAZ_NFE: "certificado",
        TipoCredencial.SEFAZ_CTE: "certificado",
        TipoCredencial.SEFAZ_MDFE: "certificado",
        TipoCredencial.ESOCIAL: "certificado",
        TipoCredencial.FGTS_DIGITAL: "certificado",
        TipoCredencial.NFSE_NACIONAL: "certificado",
        TipoCredencial.NFSE_MUNICIPAL: "usuario_senha",  # Varia por município
        TipoCredencial.SPED: "certificado",
        TipoCredencial.RECEITA_FEDERAL: "certificado",
    }

    def __init__(
        self,
        vault_client: Optional[VaultClient] = None,
        cert_manager: Optional[GerenciadorCertificados] = None
    ):
        self.vault = vault_client or get_vault_client()
        self.cert_manager = cert_manager or GerenciadorCertificados(self.vault)

    async def obter_credencial(
        self,
        tenant_id: str,
        servico: TipoCredencial,
        ambiente: str = "producao",
        codigo_municipio: Optional[str] = None
    ) -> CredencialGoverno:
        """
        Obtém credencial para um serviço.

        Args:
            tenant_id: ID do tenant
            servico: Serviço governamental
            ambiente: producao ou homologacao
            codigo_municipio: Código IBGE para NFS-e municipal

        Returns:
            CredencialGoverno preenchida
        """
        tipo_auth = self.TIPO_AUTENTICACAO.get(servico, "certificado")

        credencial = CredencialGoverno(
            tenant_id=tenant_id,
            servico=servico,
            tipo_autenticacao=tipo_auth,
            ambiente=ambiente,
            codigo_municipio=codigo_municipio,
        )

        try:
            if tipo_auth == "certificado":
                await self._carregar_certificado(credencial)

            elif tipo_auth == "usuario_senha":
                await self._carregar_usuario_senha(credencial)

            elif tipo_auth == "token":
                await self._carregar_token(credencial)

            elif tipo_auth == "oauth":
                await self._carregar_oauth(credencial)

            # Carregar dados adicionais específicos do serviço
            await self._carregar_dados_servico(credencial)

            credencial.ultima_validacao = datetime.utcnow()

        except Exception as e:
            logger.error(f"Erro ao obter credencial {servico.value}: {e}")
            credencial.valida = False
            credencial.erro = str(e)

        return credencial

    async def _carregar_certificado(self, credencial: CredencialGoverno):
        """Carrega informações do certificado."""
        tipo_cert = self.CERTIFICADO_POR_SERVICO.get(credencial.servico)

        if not tipo_cert:
            credencial.valida = False
            credencial.erro = "Tipo de certificado não configurado para serviço"
            return

        credencial.certificado_tipo = tipo_cert

        # Obter info do certificado (sem chave privada)
        info = await self.cert_manager.obter_info_certificado(
            credencial.tenant_id,
            tipo_cert
        )

        if not info:
            credencial.valida = False
            credencial.erro = "Certificado não encontrado"
            return

        credencial.certificado_info = info

        if not info.valido:
            credencial.valida = False
            credencial.erro = "Certificado expirado"

        elif info.alerta_expiracao:
            logger.warning(
                f"Certificado próximo da expiração: {credencial.tenant_id} "
                f"({info.dias_restantes} dias)"
            )

    async def _carregar_usuario_senha(self, credencial: CredencialGoverno):
        """Carrega credenciais de usuário/senha."""
        # Path depende do serviço e município
        servico_key = credencial.servico.value
        if credencial.codigo_municipio:
            servico_key = f"{servico_key}/{credencial.codigo_municipio}"

        dados = await self.vault.obter_credencial_servico(
            credencial.tenant_id,
            servico_key
        )

        if not dados:
            credencial.valida = False
            credencial.erro = "Credenciais não encontradas"
            return

        credencial.usuario = dados.get("usuario")
        credencial.senha = dados.get("senha")
        credencial.inscricao_municipal = dados.get("inscricao_municipal")

        if not credencial.usuario or not credencial.senha:
            credencial.valida = False
            credencial.erro = "Credenciais incompletas"

    async def _carregar_token(self, credencial: CredencialGoverno):
        """Carrega token de acesso."""
        dados = await self.vault.obter_credencial_servico(
            credencial.tenant_id,
            credencial.servico.value
        )

        if not dados:
            credencial.valida = False
            credencial.erro = "Token não encontrado"
            return

        credencial.token = dados.get("token")
        expiracao = dados.get("token_expiracao")
        if expiracao:
            credencial.token_expiracao = datetime.fromisoformat(expiracao)

            # Verificar se token expirou
            if credencial.token_expiracao < datetime.utcnow():
                credencial.valida = False
                credencial.erro = "Token expirado"

    async def _carregar_oauth(self, credencial: CredencialGoverno):
        """Carrega credenciais OAuth."""
        dados = await self.vault.obter_credencial_servico(
            credencial.tenant_id,
            credencial.servico.value
        )

        if not dados:
            credencial.valida = False
            credencial.erro = "Configuração OAuth não encontrada"
            return

        credencial.client_id = dados.get("client_id")
        credencial.client_secret = dados.get("client_secret")
        credencial.access_token = dados.get("access_token")
        credencial.refresh_token = dados.get("refresh_token")

        expiracao = dados.get("token_expiracao")
        if expiracao:
            credencial.token_expiracao = datetime.fromisoformat(expiracao)

    async def _carregar_dados_servico(self, credencial: CredencialGoverno):
        """Carrega dados adicionais específicos do serviço."""
        # Dados comuns a todos os serviços
        dados = await self.vault.obter_credencial_servico(
            credencial.tenant_id,
            f"{credencial.servico.value}/config"
        )

        if dados:
            credencial.inscricao_municipal = dados.get(
                "inscricao_municipal",
                credencial.inscricao_municipal
            )

    async def salvar_credencial_usuario_senha(
        self,
        tenant_id: str,
        servico: TipoCredencial,
        usuario: str,
        senha: str,
        codigo_municipio: Optional[str] = None,
        inscricao_municipal: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Salva credenciais de usuário/senha.

        Args:
            tenant_id: ID do tenant
            servico: Serviço governamental
            usuario: Nome de usuário
            senha: Senha
            codigo_municipio: Código IBGE (para NFS-e)
            inscricao_municipal: Inscrição municipal
            metadata: Dados adicionais

        Returns:
            True se salvo com sucesso
        """
        servico_key = servico.value
        if codigo_municipio:
            servico_key = f"{servico_key}/{codigo_municipio}"

        dados = {
            "usuario": usuario,
            "senha": senha,
            "inscricao_municipal": inscricao_municipal,
            **(metadata or {}),
        }

        return await self.vault.salvar_credencial_servico(
            tenant_id,
            servico_key,
            dados
        )

    async def salvar_token(
        self,
        tenant_id: str,
        servico: TipoCredencial,
        token: str,
        expiracao: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Salva token de acesso."""
        dados = {
            "token": token,
            "token_expiracao": expiracao.isoformat() if expiracao else None,
            **(metadata or {}),
        }

        return await self.vault.salvar_credencial_servico(
            tenant_id,
            servico.value,
            dados
        )

    async def salvar_oauth(
        self,
        tenant_id: str,
        servico: TipoCredencial,
        client_id: str,
        client_secret: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_expiracao: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Salva configuração OAuth."""
        dados = {
            "client_id": client_id,
            "client_secret": client_secret,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_expiracao": token_expiracao.isoformat() if token_expiracao else None,
            **(metadata or {}),
        }

        return await self.vault.salvar_credencial_servico(
            tenant_id,
            servico.value,
            dados
        )

    async def validar_credencial(
        self,
        tenant_id: str,
        servico: TipoCredencial,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Valida uma credencial.

        Args:
            tenant_id: ID do tenant
            servico: Serviço governamental
            **kwargs: Argumentos adicionais (ambiente, codigo_municipio)

        Returns:
            Resultado da validação
        """
        credencial = await self.obter_credencial(tenant_id, servico, **kwargs)

        resultado = {
            "valida": credencial.valida,
            "servico": servico.value,
            "tipo_autenticacao": credencial.tipo_autenticacao,
            "erro": credencial.erro,
        }

        if credencial.certificado_info:
            resultado["certificado"] = {
                "tipo": credencial.certificado_tipo.value,
                "valido": credencial.certificado_info.valido,
                "dias_restantes": credencial.certificado_info.dias_restantes,
                "validade_fim": credencial.certificado_info.validade_fim.isoformat(),
                "alerta_expiracao": credencial.certificado_info.alerta_expiracao,
            }

        if credencial.token_expiracao:
            resultado["token_expiracao"] = credencial.token_expiracao.isoformat()

        return resultado

    async def listar_credenciais_tenant(
        self,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Lista todas as credenciais configuradas para um tenant."""
        credenciais = []

        # Listar certificados
        certificados = await self.cert_manager.listar_certificados(tenant_id)
        for cert in certificados:
            credenciais.append({
                "tipo": "certificado",
                "servico": cert.tipo.value,
                "valido": cert.valido,
                "expiracao": cert.validade_fim.isoformat(),
                "dias_restantes": cert.dias_restantes,
            })

        # Listar outras credenciais
        servicos = await self.vault.listar_credenciais_tenant(tenant_id)
        for servico in servicos:
            servico = servico.rstrip("/")
            if servico not in [c.tipo.value for c in certificados]:
                dados = await self.vault.obter_credencial_servico(
                    tenant_id, servico
                )
                if dados:
                    credenciais.append({
                        "tipo": "servico",
                        "servico": servico,
                        "configurado": True,
                        "updated_at": dados.get("updated_at"),
                    })

        return credenciais

    async def remover_credencial(
        self,
        tenant_id: str,
        servico: TipoCredencial,
        codigo_municipio: Optional[str] = None
    ) -> bool:
        """Remove credencial de um serviço."""
        servico_key = servico.value
        if codigo_municipio:
            servico_key = f"{servico_key}/{codigo_municipio}"

        path = f"government/credentials/{tenant_id}/{servico_key}"
        return await self.vault.deletar_secret(path)


# Instância singleton
_credential_provider_instance: Optional[ProvedorCredenciais] = None


def get_credential_provider() -> "ProvedorCredenciais":
    """
    Obtém instância do provedor de credenciais.

    Primeiro tenta usar FileCredentialProvider (modo simplificado),
    depois faz fallback para ProvedorCredenciais com Vault.
    """
    global _credential_provider_instance
    if _credential_provider_instance is None:
        # Tentar usar FileCredentialProvider primeiro (modo simplificado)
        try:
            from .file_credential_provider import get_file_credential_provider
            file_provider = get_file_credential_provider()
            # Verificar se o certificado existe
            from pathlib import Path
            if Path(file_provider.config.cert_path).exists():
                logger.info("Usando FileCredentialProvider (modo simplificado)")
                _credential_provider_instance = file_provider
                return _credential_provider_instance
        except Exception as e:
            logger.debug(f"FileCredentialProvider não disponível: {e}")

        # Fallback para Vault
        logger.info("Usando ProvedorCredenciais com Vault")
        _credential_provider_instance = ProvedorCredenciais()
    return _credential_provider_instance
