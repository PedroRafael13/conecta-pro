"""
Gerenciador de Certificados Digitais.

Gerencia certificados A1/A3 para assinatura de documentos fiscais.
"""

import base64
import logging
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

from .vault_client import VaultClient, get_vault_client

logger = logging.getLogger(__name__)


class TipoCertificado(Enum):
    """Tipos de certificado digital."""

    E_CNPJ = "e-cnpj"
    E_CPF = "e-cpf"
    NF_E = "nf-e"
    CT_E = "ct-e"


@dataclass
class CertificadoInfo:
    """Informações de um certificado."""

    tenant_id: str
    tipo: TipoCertificado
    subject: str
    issuer: str
    serial_number: str
    validade_inicio: datetime
    validade_fim: datetime
    dias_restantes: int
    cnpj_cpf: str | None
    razao_social: str | None
    valido: bool
    alerta_expiracao: bool  # True se < 30 dias


class GerenciadorCertificados:
    """
    Gerencia certificados digitais para integrações governamentais.

    Responsabilidades:
    - Armazenar certificados no Vault
    - Validar certificados
    - Alertar sobre expiração
    - Fornecer certificados para assinatura
    """

    # Dias para alertar antes da expiração
    DIAS_ALERTA_EXPIRACAO = 30

    def __init__(self, vault_client: VaultClient | None = None):
        self.vault = vault_client or get_vault_client()

    async def importar_certificado(
        self, tenant_id: str, tipo: TipoCertificado, pfx_bytes: bytes, senha: str, metadata: dict | None = None
    ) -> CertificadoInfo:
        """
        Importa e armazena um certificado PFX.

        Args:
            tenant_id: ID do tenant
            tipo: Tipo do certificado
            pfx_bytes: Bytes do arquivo PFX
            senha: Senha do certificado
            metadata: Metadados adicionais

        Returns:
            Informações do certificado importado

        Raises:
            ValueError: Se certificado inválido ou expirado
        """
        # Validar e extrair informações
        info = self._extrair_info_certificado(pfx_bytes, senha, tenant_id, tipo)

        if not info.valido:
            raise ValueError("Certificado expirado ou inválido")

        # Converter para base64
        pfx_base64 = base64.b64encode(pfx_bytes).decode("utf-8")

        # Salvar no Vault
        sucesso = await self.vault.salvar_certificado(
            tenant_id=tenant_id,
            tipo=tipo.value,
            pfx_base64=pfx_base64,
            senha=senha,
            validade=info.validade_fim,
            metadata={
                "subject": info.subject,
                "issuer": info.issuer,
                "serial_number": info.serial_number,
                "cnpj_cpf": info.cnpj_cpf,
                "razao_social": info.razao_social,
                **(metadata or {}),
            },
        )

        if not sucesso:
            raise RuntimeError("Falha ao salvar certificado no Vault")

        logger.info(f"Certificado importado: {tenant_id}/{tipo.value} (válido até {info.validade_fim.date()})")

        return info

    def _extrair_info_certificado(
        self, pfx_bytes: bytes, senha: str, tenant_id: str, tipo: TipoCertificado
    ) -> CertificadoInfo:
        """Extrai informações de um certificado PFX."""
        try:
            # Carregar PFX
            private_key, certificate, chain = pkcs12.load_key_and_certificates(
                pfx_bytes,
                senha.encode("utf-8"),
                default_backend(),
            )

            if certificate is None:
                raise ValueError("Certificado não encontrado no PFX")

            # Extrair informações
            subject = certificate.subject.rfc4514_string()
            issuer = certificate.issuer.rfc4514_string()
            serial = format(certificate.serial_number, "X")
            validade_inicio = certificate.not_valid_before_utc
            validade_fim = certificate.not_valid_after_utc

            # Calcular dias restantes
            agora = datetime.utcnow()
            dias_restantes = (validade_fim.replace(tzinfo=None) - agora).days

            # Tentar extrair CNPJ/CPF e razão social do subject
            cnpj_cpf = self._extrair_cnpj_cpf(subject)
            razao_social = self._extrair_razao_social(subject)

            # Verificar validade
            valido = dias_restantes > 0

            return CertificadoInfo(
                tenant_id=tenant_id,
                tipo=tipo,
                subject=subject,
                issuer=issuer,
                serial_number=serial,
                validade_inicio=validade_inicio.replace(tzinfo=None),
                validade_fim=validade_fim.replace(tzinfo=None),
                dias_restantes=dias_restantes,
                cnpj_cpf=cnpj_cpf,
                razao_social=razao_social,
                valido=valido,
                alerta_expiracao=dias_restantes <= self.DIAS_ALERTA_EXPIRACAO,
            )

        except Exception as e:
            logger.error(f"Erro ao extrair info do certificado: {e}")
            raise ValueError(f"Certificado inválido: {e}")

    def _extrair_cnpj_cpf(self, subject: str) -> str | None:
        """Extrai CNPJ ou CPF do subject do certificado."""
        import re

        # Padrão para CNPJ no subject (comum em certificados ICP-Brasil)
        # Formato: CN=NOME:12345678000123
        match = re.search(r":(\d{14})(?:\D|$)", subject)
        if match:
            return match.group(1)

        # Padrão para CPF
        match = re.search(r":(\d{11})(?:\D|$)", subject)
        if match:
            return match.group(1)

        # Tentar extrair de campo específico
        match = re.search(r"2\.16\.76\.1\.3\.3=(\d+)", subject)
        if match:
            return match.group(1)

        return None

    def _extrair_razao_social(self, subject: str) -> str | None:
        """Extrai razão social do subject do certificado."""
        import re

        # Formato típico: CN=RAZAO SOCIAL:CNPJ
        match = re.search(r"CN=([^,:]+)", subject)
        if match:
            nome = match.group(1).strip()
            # Remover sufixos comuns
            nome = re.sub(r":\d+$", "", nome)
            return nome

        return None

    async def obter_certificado(self, tenant_id: str, tipo: TipoCertificado) -> tuple[bytes | None, str | None]:
        """
        Obtém certificado PFX e senha.

        Args:
            tenant_id: ID do tenant
            tipo: Tipo do certificado

        Returns:
            Tupla (pfx_bytes, senha) ou (None, None) se não encontrado
        """
        dados = await self.vault.obter_certificado(tenant_id, tipo.value)

        if not dados:
            logger.warning(f"Certificado não encontrado: {tenant_id}/{tipo.value}")
            return None, None

        pfx_base64 = dados.get("pfx_base64")
        senha = dados.get("senha")

        if not pfx_base64 or not senha:
            logger.error(f"Dados incompletos do certificado: {tenant_id}/{tipo.value}")
            return None, None

        pfx_bytes = base64.b64decode(pfx_base64)
        return pfx_bytes, senha

    async def obter_info_certificado(self, tenant_id: str, tipo: TipoCertificado) -> CertificadoInfo | None:
        """Obtém informações de um certificado sem retornar a chave privada."""
        pfx_bytes, senha = await self.obter_certificado(tenant_id, tipo)

        if not pfx_bytes:
            return None

        try:
            return self._extrair_info_certificado(pfx_bytes, senha, tenant_id, tipo)
        except Exception as e:
            logger.error(f"Erro ao obter info do certificado: {e}")
            return None

    async def listar_certificados(self, tenant_id: str) -> list[CertificadoInfo]:
        """Lista todos os certificados de um tenant."""
        tipos = await self.vault.listar_certificados_tenant(tenant_id)
        certificados = []

        for tipo_str in tipos:
            tipo_str = tipo_str.rstrip("/")
            try:
                tipo = TipoCertificado(tipo_str)
                info = await self.obter_info_certificado(tenant_id, tipo)
                if info:
                    certificados.append(info)
            except ValueError:
                logger.warning(f"Tipo de certificado desconhecido: {tipo_str}")

        return certificados

    async def verificar_expiracao(self, tenant_id: str | None = None) -> list[CertificadoInfo]:
        """
        Verifica certificados próximos da expiração.

        Args:
            tenant_id: Se fornecido, verifica apenas este tenant

        Returns:
            Lista de certificados com alerta de expiração
        """
        alertas = []

        if tenant_id:
            certificados = await self.listar_certificados(tenant_id)
            alertas.extend([c for c in certificados if c.alerta_expiracao])
        else:
            # TODO: Implementar varredura de todos os tenants
            # Isso requer listar todos os tenants do sistema
            pass

        return alertas

    async def deletar_certificado(self, tenant_id: str, tipo: TipoCertificado) -> bool:
        """Remove um certificado do Vault."""
        path = f"government/certificates/{tenant_id}/{tipo.value}"
        return await self.vault.deletar_secret(path)

    async def criar_contexto_ssl(self, tenant_id: str, tipo: TipoCertificado) -> Any | None:
        """
        Cria contexto SSL com certificado do tenant.

        Útil para conexões HTTPS que requerem certificado cliente.

        Args:
            tenant_id: ID do tenant
            tipo: Tipo do certificado

        Returns:
            ssl.SSLContext configurado ou None
        """
        import ssl

        pfx_bytes, senha = await self.obter_certificado(tenant_id, tipo)
        if not pfx_bytes:
            return None

        try:
            # Carregar PFX
            private_key, certificate, chain = pkcs12.load_key_and_certificates(
                pfx_bytes,
                senha.encode("utf-8"),
                default_backend(),
            )

            # Criar arquivos temporários
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pem") as cert_file:
                cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
                cert_file.write(cert_pem)
                cert_path = cert_file.name

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pem") as key_file:
                key_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
                key_file.write(key_pem)
                key_path = key_file.name

            # Criar contexto SSL
            ctx = ssl.create_default_context()
            ctx.load_cert_chain(cert_path, key_path)

            # Limpar arquivos temporários
            os.unlink(cert_path)
            os.unlink(key_path)

            return ctx

        except Exception as e:
            logger.error(f"Erro ao criar contexto SSL: {e}")
            return None

    async def assinar_xml(self, tenant_id: str, tipo: TipoCertificado, xml_content: str) -> str | None:
        """
        Assina XML com certificado digital.

        Args:
            tenant_id: ID do tenant
            tipo: Tipo do certificado
            xml_content: Conteúdo XML a assinar

        Returns:
            XML assinado ou None se falhar
        """
        pfx_bytes, senha = await self.obter_certificado(tenant_id, tipo)
        if not pfx_bytes:
            return None

        try:
            # Importar signxml (opcional - pode não estar instalado)
            from signxml import XMLSigner, methods

            # Carregar certificado
            private_key, certificate, chain = pkcs12.load_key_and_certificates(
                pfx_bytes,
                senha.encode("utf-8"),
                default_backend(),
            )

            # Criar assinador
            signer = XMLSigner(
                method=methods.enveloped,
                signature_algorithm="rsa-sha256",
                digest_algorithm="sha256",
            )

            # Assinar
            from lxml import etree

            root = etree.fromstring(xml_content.encode("utf-8"))
            signed_root = signer.sign(
                root,
                key=private_key,
                cert=certificate,
            )

            return etree.tostring(signed_root, encoding="unicode")

        except ImportError:
            logger.error("signxml não instalado para assinatura de XML")
            return None

        except Exception as e:
            logger.error(f"Erro ao assinar XML: {e}")
            return None

    def gerar_relatorio_certificados(self, certificados: list[CertificadoInfo]) -> dict[str, Any]:
        """Gera relatório de status dos certificados."""
        total = len(certificados)
        validos = [c for c in certificados if c.valido]
        expirados = [c for c in certificados if not c.valido]
        alertas = [c for c in certificados if c.alerta_expiracao and c.valido]

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "resumo": {
                "total": total,
                "validos": len(validos),
                "expirados": len(expirados),
                "com_alerta": len(alertas),
            },
            "expirados": [
                {
                    "tenant_id": c.tenant_id,
                    "tipo": c.tipo.value,
                    "validade_fim": c.validade_fim.isoformat(),
                }
                for c in expirados
            ],
            "alertas": [
                {
                    "tenant_id": c.tenant_id,
                    "tipo": c.tipo.value,
                    "dias_restantes": c.dias_restantes,
                    "validade_fim": c.validade_fim.isoformat(),
                }
                for c in alertas
            ],
        }
