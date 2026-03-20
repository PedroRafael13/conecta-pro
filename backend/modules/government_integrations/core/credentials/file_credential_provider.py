"""
Provedor de Credenciais baseado em Arquivo (sem Vault).

Versão simplificada que lê certificados e credenciais diretamente
do sistema de arquivos, útil para ambientes de desenvolvimento ou
quando o Vault não está disponível.
"""

import logging
import os
import ssl
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from OpenSSL import crypto

from .certificate_manager import (
    CertificadoInfo,
    TipoCertificado,
)
from .credential_provider import (
    CredencialGoverno,
    TipoCredencial,
)

logger = logging.getLogger(__name__)


@dataclass
class FileCredentialConfig:
    """Configuração do provedor de credenciais baseado em arquivo."""

    # Paths
    cert_path: str = "/opt/conecta-pro/credentials/certificates/certificado.pfx"
    cert_password: str = ""
    cert_pem_path: str = "/opt/conecta-pro/credentials/certificates/a1_cert.pem"
    key_pem_path: str = "/opt/conecta-pro/credentials/certificates/a1_key.pem"

    # Informações do tenant (fixo para instalação single-tenant)
    tenant_id: str = "default"
    cnpj: str = "35710481000103"
    razao_social: str = "JORDAN SANTOS DE JESUS LTDA"

    # Ambiente
    ambiente: str = "producao"  # producao ou homologacao

    @classmethod
    def from_env(cls) -> "FileCredentialConfig":
        """Cria configuração a partir de variáveis de ambiente."""
        cert_password = os.getenv("CERTIFICATE_PASSWORD", "")
        if not cert_password:
            raise RuntimeError("CERTIFICATE_PASSWORD nao definida. Defina em .env antes de iniciar o servidor.")
        return cls(
            cert_path=os.getenv("CERTIFICATE_PATH", "/opt/conecta-pro/credentials/certificates/certificado.pfx"),
            cert_password=cert_password,
            cert_pem_path=os.getenv("CERT_PEM_PATH", "/opt/conecta-pro/credentials/certificates/a1_cert.pem"),
            key_pem_path=os.getenv("KEY_PEM_PATH", "/opt/conecta-pro/credentials/certificates/a1_key.pem"),
            cnpj=os.getenv("EMPRESA_CNPJ", "35710481000103"),
            razao_social=os.getenv("EMPRESA_RAZAO_SOCIAL", "JORDAN SANTOS DE JESUS LTDA"),
            ambiente=os.getenv("SEFAZ_ENVIRONMENT", "1") == "1" and "producao" or "homologacao",
        )


class FileCredentialProvider:
    """
    Provedor de credenciais que lê diretamente de arquivos.

    Substitui o Vault para instalações simplificadas.
    """

    def __init__(self, config: FileCredentialConfig | None = None):
        self.config = config or FileCredentialConfig.from_env()
        self._cert_info: CertificadoInfo | None = None
        self._ssl_context: ssl.SSLContext | None = None

    async def obter_credencial(
        self, tenant_id: str, servico: TipoCredencial, ambiente: str = "producao", codigo_municipio: str | None = None
    ) -> CredencialGoverno:
        """
        Obtém credencial para um serviço.

        Args:
            tenant_id: ID do tenant (ignorado em single-tenant)
            servico: Serviço governamental
            ambiente: producao ou homologacao
            codigo_municipio: Código IBGE para NFS-e municipal

        Returns:
            CredencialGoverno preenchida
        """
        # Determinar tipo de autenticação
        tipo_auth = self._get_tipo_autenticacao(servico)

        credencial = CredencialGoverno(
            tenant_id=self.config.tenant_id,
            servico=servico,
            tipo_autenticacao=tipo_auth,
            ambiente=ambiente or self.config.ambiente,
            codigo_municipio=codigo_municipio,
        )

        try:
            if tipo_auth == "certificado":
                await self._carregar_certificado(credencial)
            else:
                # Para outros tipos, marcar como não configurado
                credencial.valida = False
                credencial.erro = f"Tipo de autenticação '{tipo_auth}' não suportado em modo arquivo"

            credencial.ultima_validacao = datetime.utcnow()

        except Exception as e:
            logger.error(f"Erro ao obter credencial {servico.value}: {e}")
            credencial.valida = False
            credencial.erro = str(e)

        return credencial

    def _get_tipo_autenticacao(self, servico: TipoCredencial) -> str:
        """Retorna tipo de autenticação para um serviço."""
        # Todos os serviços principais usam certificado
        servicos_certificado = [
            TipoCredencial.SEFAZ_NFE,
            TipoCredencial.SEFAZ_CTE,
            TipoCredencial.SEFAZ_MDFE,
            TipoCredencial.ESOCIAL,
            TipoCredencial.FGTS_DIGITAL,
            TipoCredencial.NFSE_NACIONAL,
            TipoCredencial.SPED,
            TipoCredencial.RECEITA_FEDERAL,
        ]

        if servico in servicos_certificado:
            return "certificado"
        elif servico == TipoCredencial.NFSE_MUNICIPAL:
            return "usuario_senha"
        else:
            return "certificado"

    async def _carregar_certificado(self, credencial: CredencialGoverno):
        """Carrega informações do certificado do arquivo."""
        # Verificar se arquivos PEM existem
        if not Path(self.config.cert_pem_path).exists():
            await self._extrair_certificado_pfx()

        # Carregar info do certificado
        if self._cert_info is None:
            self._cert_info = await self._ler_info_certificado()

        credencial.certificado_info = self._cert_info
        credencial.certificado_tipo = TipoCertificado.E_CNPJ

        if not self._cert_info.valido:
            credencial.valida = False
            credencial.erro = "Certificado expirado"
        elif self._cert_info.alerta_expiracao:
            logger.warning(f"Certificado próximo da expiração: {self._cert_info.dias_restantes} dias")

    async def _extrair_certificado_pfx(self):
        """Extrai certificado e chave do arquivo PFX."""
        logger.info("Extraindo certificado PFX para PEM...")

        try:
            # Ler arquivo PFX
            with open(self.config.cert_path, "rb") as f:
                pfx_data = f.read()

            # Carregar PFX
            pfx = crypto.load_pkcs12(pfx_data, self.config.cert_password.encode())

            # Extrair certificado
            cert = pfx.get_certificate()
            cert_pem = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)

            # Extrair chave privada
            key = pfx.get_privatekey()
            key_pem = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)

            # Salvar arquivos PEM
            Path(self.config.cert_pem_path).parent.mkdir(parents=True, exist_ok=True)

            with open(self.config.cert_pem_path, "wb") as f:
                f.write(cert_pem)
            os.chmod(self.config.cert_pem_path, 0o600)

            with open(self.config.key_pem_path, "wb") as f:
                f.write(key_pem)
            os.chmod(self.config.key_pem_path, 0o600)

            logger.info("Certificado extraído com sucesso")

        except Exception as e:
            logger.error(f"Erro ao extrair certificado PFX: {e}")
            raise

    async def _ler_info_certificado(self) -> CertificadoInfo:
        """Lê informações do certificado PEM."""
        try:
            with open(self.config.cert_pem_path, "rb") as f:
                cert_data = f.read()

            cert = x509.load_pem_x509_certificate(cert_data, default_backend())

            # Extrair informações do subject
            subject = cert.subject
            cn = None
            for attr in subject:
                if attr.oid == x509.oid.NameOID.COMMON_NAME:
                    cn = attr.value
                    break

            # Extrair CNPJ do CN (formato: "RAZAO SOCIAL:CNPJ")
            cnpj = None
            razao_social = None
            if cn and ":" in cn:
                parts = cn.rsplit(":", 1)
                razao_social = parts[0]
                cnpj = parts[1] if len(parts) > 1 else None

            # Calcular dias restantes
            validade_fim = cert.not_valid_after_utc if hasattr(cert, "not_valid_after_utc") else cert.not_valid_after
            validade_inicio = (
                cert.not_valid_before_utc if hasattr(cert, "not_valid_before_utc") else cert.not_valid_before
            )

            # Fazer timezone-aware se necessário
            agora = datetime.utcnow()
            if validade_fim.tzinfo is not None:
                agora = datetime.now(UTC)

            dias_restantes = (validade_fim - agora).days

            return CertificadoInfo(
                tenant_id=self.config.tenant_id,
                tipo=TipoCertificado.E_CNPJ,
                subject=cn or self.config.razao_social,
                issuer=str(cert.issuer),
                serial_number=format(cert.serial_number, "X"),
                validade_inicio=validade_inicio,
                validade_fim=validade_fim,
                dias_restantes=dias_restantes,
                cnpj_cpf=cnpj or self.config.cnpj,
                razao_social=razao_social or self.config.razao_social,
                valido=dias_restantes > 0,
                alerta_expiracao=dias_restantes <= 30,
            )

        except Exception as e:
            logger.error(f"Erro ao ler info do certificado: {e}")
            raise

    def get_ssl_context(self) -> ssl.SSLContext:
        """
        Obtém contexto SSL configurado com o certificado.

        Usado para conexões HTTPS com autenticação mútua (mTLS).
        """
        if self._ssl_context is not None:
            return self._ssl_context

        self._ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self._ssl_context.load_cert_chain(
            certfile=self.config.cert_pem_path,
            keyfile=self.config.key_pem_path,
        )
        # Desabilitar verificação para alguns serviços governamentais com certificados problemáticos
        self._ssl_context.check_hostname = False
        self._ssl_context.verify_mode = ssl.CERT_NONE

        return self._ssl_context

    def get_cert_files(self) -> tuple[str, str]:
        """Retorna paths dos arquivos de certificado e chave."""
        return self.config.cert_pem_path, self.config.key_pem_path

    async def validar_credencial(self, tenant_id: str, servico: TipoCredencial, **kwargs) -> dict[str, Any]:
        """Valida uma credencial."""
        credencial = await self.obter_credencial(tenant_id, servico, **kwargs)

        resultado = {
            "valida": credencial.valida,
            "servico": servico.value,
            "tipo_autenticacao": credencial.tipo_autenticacao,
            "erro": credencial.erro,
        }

        if credencial.certificado_info:
            resultado["certificado"] = {
                "cnpj": credencial.certificado_info.cnpj_cpf,
                "razao_social": credencial.certificado_info.razao_social,
                "valido": credencial.certificado_info.valido,
                "dias_restantes": credencial.certificado_info.dias_restantes,
                "validade_fim": credencial.certificado_info.validade_fim.isoformat(),
                "alerta_expiracao": credencial.certificado_info.alerta_expiracao,
            }

        return resultado


# Singleton
_file_provider_instance: FileCredentialProvider | None = None


def get_file_credential_provider() -> FileCredentialProvider:
    """Obtém instância do provedor de credenciais baseado em arquivo."""
    global _file_provider_instance
    if _file_provider_instance is None:
        _file_provider_instance = FileCredentialProvider()
    return _file_provider_instance
