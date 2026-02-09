"""
Gerenciador de Certificados Digitais A1
Sprint 33: Integrações Governamentais

Suporte a certificados A1 (.pfx/.p12) para:
- eSocial
- SEFAZ (NF-e, NFC-e, CT-e)
- Receita Federal
"""

import base64
import hashlib
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Optional

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

# OpenSSL.crypto está depreciado para PKCS12, usamos cryptography diretamente

logger = logging.getLogger(__name__)


class CertificateType(StrEnum):
    """Tipos de certificado digital."""

    A1 = "A1"  # Arquivo .pfx/.p12
    A3 = "A3"  # Token/Smartcard (não implementado ainda)


class CertificateStatus(StrEnum):
    """Status do certificado."""

    VALID = "valid"
    EXPIRED = "expired"
    EXPIRING_SOON = "expiring_soon"  # < 30 dias
    REVOKED = "revoked"
    INVALID = "invalid"


@dataclass
class CertificateInfo:
    """Informações do certificado digital."""

    # Identificação
    serial_number: str
    thumbprint: str  # SHA-1 fingerprint

    # Subject (titular)
    subject_cn: str  # Common Name
    subject_cpf_cnpj: str | None = None
    subject_organization: str | None = None
    subject_ou: str | None = None

    # Issuer (emissor)
    issuer_cn: str = ""
    issuer_organization: str | None = None

    # Validade
    valid_from: datetime = field(default_factory=datetime.utcnow)
    valid_until: datetime = field(default_factory=datetime.utcnow)

    # Tipo e status
    certificate_type: CertificateType = CertificateType.A1
    status: CertificateStatus = CertificateStatus.VALID

    # Metadados
    key_size: int = 2048
    signature_algorithm: str = "sha256WithRSAEncryption"

    @property
    def days_until_expiry(self) -> int:
        """Dias até expiração."""
        delta = self.valid_until - datetime.utcnow()
        return max(0, delta.days)

    @property
    def is_valid(self) -> bool:
        """Verifica se está válido."""
        now = datetime.utcnow()
        return self.valid_from <= now <= self.valid_until

    @property
    def is_expiring_soon(self) -> bool:
        """Verifica se expira em menos de 30 dias."""
        return self.days_until_expiry < 30

    @property
    def cpf_cnpj(self) -> str | None:
        """Alias para subject_cpf_cnpj (compatibilidade)."""
        return self.subject_cpf_cnpj

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return {
            "serial_number": self.serial_number,
            "thumbprint": self.thumbprint,
            "subject_cn": self.subject_cn,
            "subject_cpf_cnpj": self.subject_cpf_cnpj,
            "subject_organization": self.subject_organization,
            "issuer_cn": self.issuer_cn,
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat(),
            "days_until_expiry": self.days_until_expiry,
            "is_valid": self.is_valid,
            "certificate_type": self.certificate_type.value,
            "status": self.status.value,
            "key_size": self.key_size,
        }


class CertificateManager:
    """
    Gerenciador de certificados digitais A1.

    Responsável por:
    - Carregar certificados .pfx/.p12
    - Extrair informações do certificado
    - Fornecer chave privada para assinatura
    - Validar certificados
    """

    def __init__(self, pfx_path: str | None = None, pfx_data: bytes | None = None, password: str | None = None):
        """
        Inicializa o gerenciador.

        Args:
            pfx_path: Caminho para arquivo .pfx/.p12
            pfx_data: Bytes do certificado (alternativa ao path)
            password: Senha do certificado
        """
        self._pfx_path = pfx_path
        self._pfx_data = pfx_data
        self._password = password.encode() if password else None

        # Cryptography objects (API moderna)
        self._x509_cert: x509.Certificate | None = None
        self._private_key_crypto: rsa.RSAPrivateKey | None = None
        self._additional_certs: list = []

        # Info cache
        self._info: CertificateInfo | None = None
        self._loaded = False

    def load(self) -> bool:
        """
        Carrega o certificado.

        Returns:
            True se carregou com sucesso

        Raises:
            ValueError: Se certificado ou senha inválidos
        """
        if self._loaded:
            return True

        try:
            # Obter dados do certificado
            if self._pfx_data:
                pfx_bytes = self._pfx_data
            elif self._pfx_path:
                with open(self._pfx_path, "rb") as f:
                    pfx_bytes = f.read()
            else:
                raise ValueError("Certificado não especificado (pfx_path ou pfx_data)")

            # Carregar PKCS12 com cryptography (API moderna)
            # self._password já é bytes (convertido no __init__)
            password_bytes = self._password
            self._private_key_crypto, self._x509_cert, additional_certs = pkcs12.load_key_and_certificates(
                pfx_bytes, password_bytes, default_backend()
            )

            if not self._x509_cert or not self._private_key_crypto:
                raise ValueError("Certificado ou chave privada não encontrados no arquivo")

            # Salvar certs adicionais (cadeia)
            self._additional_certs = additional_certs or []

            # Extrair informações
            self._info = self._extract_info()
            self._loaded = True

            logger.info(
                f"Certificado carregado: {self._info.subject_cn} "
                f"(válido até {self._info.valid_until.strftime('%d/%m/%Y')})"
            )

            return True

        except ValueError as e:
            logger.error(f"Erro ao carregar certificado (senha incorreta?): {e}")
            raise ValueError(f"Erro ao carregar certificado: {e}")
        except Exception as e:
            logger.error(f"Erro ao carregar certificado: {e}")
            raise ValueError(f"Erro ao carregar certificado: {e}")

    def _extract_info(self) -> CertificateInfo:
        """Extrai informações do certificado."""
        cert = self._x509_cert

        # Subject
        subject = cert.subject
        subject_cn = self._get_name_attribute(subject, NameOID.COMMON_NAME)
        subject_org = self._get_name_attribute(subject, NameOID.ORGANIZATION_NAME)
        subject_ou = self._get_name_attribute(subject, NameOID.ORGANIZATIONAL_UNIT_NAME)

        # Extrair CPF/CNPJ do CN ou OU
        cpf_cnpj = self._extract_cpf_cnpj(subject_cn, subject_ou)

        # Issuer
        issuer = cert.issuer
        issuer_cn = self._get_name_attribute(issuer, NameOID.COMMON_NAME)
        issuer_org = self._get_name_attribute(issuer, NameOID.ORGANIZATION_NAME)

        # Thumbprint (SHA-1)
        thumbprint = cert.fingerprint(hashes.SHA1()).hex().upper()  # noqa: S303

        # Serial number
        serial = format(cert.serial_number, "X")

        # Validade
        valid_from = cert.not_valid_before_utc if hasattr(cert, "not_valid_before_utc") else cert.not_valid_before
        valid_until = cert.not_valid_after_utc if hasattr(cert, "not_valid_after_utc") else cert.not_valid_after

        # Converter para datetime naive se necessário
        if hasattr(valid_from, "replace"):
            valid_from = valid_from.replace(tzinfo=None)
            valid_until = valid_until.replace(tzinfo=None)

        # Key size
        public_key = cert.public_key()
        key_size = public_key.key_size if hasattr(public_key, "key_size") else 2048

        # Status
        now = datetime.utcnow()
        if now > valid_until:
            status = CertificateStatus.EXPIRED
        elif (valid_until - now).days < 30:
            status = CertificateStatus.EXPIRING_SOON
        elif now < valid_from:
            status = CertificateStatus.INVALID
        else:
            status = CertificateStatus.VALID

        return CertificateInfo(
            serial_number=serial,
            thumbprint=thumbprint,
            subject_cn=subject_cn or "Unknown",
            subject_cpf_cnpj=cpf_cnpj,
            subject_organization=subject_org,
            subject_ou=subject_ou,
            issuer_cn=issuer_cn or "Unknown",
            issuer_organization=issuer_org,
            valid_from=valid_from,
            valid_until=valid_until,
            certificate_type=CertificateType.A1,
            status=status,
            key_size=key_size,
        )

    def _get_name_attribute(self, name: x509.Name, oid) -> str | None:
        """Extrai atributo do nome X.509."""
        try:
            attrs = name.get_attributes_for_oid(oid)
            return attrs[0].value if attrs else None
        except Exception:
            return None

    def _extract_cpf_cnpj(self, cn: str | None, ou: str | None) -> str | None:
        """Extrai CPF ou CNPJ do certificado."""
        import re

        # Padrões para CPF e CNPJ
        cpf_pattern = r"\d{11}"
        cnpj_pattern = r"\d{14}"

        # Tentar extrair do CN
        if cn:
            # Formato comum: "NOME:12345678901" ou "NOME - 12345678901234"
            match = re.search(cnpj_pattern, cn)
            if match:
                return match.group()
            match = re.search(cpf_pattern, cn)
            if match:
                return match.group()

        # Tentar extrair do OU
        if ou:
            match = re.search(cnpj_pattern, ou)
            if match:
                return match.group()
            match = re.search(cpf_pattern, ou)
            if match:
                return match.group()

        return None

    @property
    def info(self) -> CertificateInfo:
        """Retorna informações do certificado."""
        if not self._loaded:
            self.load()
        return self._info

    @property
    def certificate(self) -> x509.Certificate:
        """Retorna certificado (alias para x509_certificate)."""
        if not self._loaded:
            self.load()
        return self._x509_cert

    @property
    def private_key(self) -> rsa.RSAPrivateKey:
        """Retorna chave privada (alias para private_key_crypto)."""
        if not self._loaded:
            self.load()
        return self._private_key_crypto

    @property
    def x509_certificate(self) -> x509.Certificate:
        """Retorna certificado cryptography."""
        if not self._loaded:
            self.load()
        return self._x509_cert

    @property
    def private_key_crypto(self) -> rsa.RSAPrivateKey:
        """Retorna chave privada cryptography."""
        if not self._loaded:
            self.load()
        return self._private_key_crypto

    def get_certificate_pem(self) -> bytes:
        """Retorna certificado em formato PEM."""
        if not self._loaded:
            self.load()
        return self._x509_cert.public_bytes(serialization.Encoding.PEM)

    def get_certificate_der(self) -> bytes:
        """Retorna certificado em formato DER."""
        if not self._loaded:
            self.load()
        return self._x509_cert.public_bytes(serialization.Encoding.DER)

    def get_certificate_base64(self) -> str:
        """Retorna certificado em base64 (para XML)."""
        der = self.get_certificate_der()
        return base64.b64encode(der).decode("ascii")

    def get_private_key_pem(self) -> bytes:
        """Retorna chave privada em formato PEM."""
        if not self._loaded:
            self.load()
        return self._private_key_crypto.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

    def sign_data(self, data: bytes, algorithm: str = "sha256") -> bytes:
        """
        Assina dados com a chave privada.

        Args:
            data: Dados a assinar
            algorithm: Algoritmo de hash (sha1, sha256, sha384, sha512)

        Returns:
            Assinatura em bytes
        """
        if not self._loaded:
            self.load()

        # Mapear algoritmo
        hash_algs = {
            "sha1": hashes.SHA1(),  # noqa: S303
            "sha256": hashes.SHA256(),
            "sha384": hashes.SHA384(),
            "sha512": hashes.SHA512(),
        }

        hash_alg = hash_algs.get(algorithm.lower(), hashes.SHA256())

        # Assinar com RSA PKCS1v15
        signature = self._private_key_crypto.sign(data, padding.PKCS1v15(), hash_alg)

        return signature

    def sign_data_base64(self, data: bytes, algorithm: str = "sha256") -> str:
        """Assina dados e retorna em base64."""
        signature = self.sign_data(data, algorithm)
        return base64.b64encode(signature).decode("ascii")

    def verify_signature(self, data: bytes, signature: bytes, algorithm: str = "sha256") -> bool:
        """
        Verifica assinatura.

        Args:
            data: Dados originais
            signature: Assinatura a verificar
            algorithm: Algoritmo de hash usado

        Returns:
            True se assinatura válida
        """
        if not self._loaded:
            self.load()

        hash_algs = {
            "sha1": hashes.SHA1(),  # noqa: S303
            "sha256": hashes.SHA256(),
            "sha384": hashes.SHA384(),
            "sha512": hashes.SHA512(),
        }

        hash_alg = hash_algs.get(algorithm.lower(), hashes.SHA256())

        try:
            public_key = self._x509_cert.public_key()
            public_key.verify(signature, data, padding.PKCS1v15(), hash_alg)
            return True
        except Exception:
            return False

    def validate(self) -> tuple[bool, str]:
        """
        Valida o certificado.

        Returns:
            Tupla (válido, mensagem)
        """
        if not self._loaded:
            try:
                self.load()
            except Exception as e:
                return False, f"Erro ao carregar certificado: {e}"

        info = self._info

        if info.status == CertificateStatus.EXPIRED:
            return False, f"Certificado expirado em {info.valid_until.strftime('%d/%m/%Y')}"

        if info.status == CertificateStatus.INVALID:
            return False, "Certificado ainda não é válido"

        if info.status == CertificateStatus.EXPIRING_SOON:
            return True, f"Certificado válido, mas expira em {info.days_until_expiry} dias"

        return True, "Certificado válido"

    def get_certificate_for_request(self) -> tuple[str, str]:
        """
        Retorna tupla (cert_path, key_path) para uso em requisições HTTP.

        Cria arquivos temporários PEM para uso com httpx/requests.
        Os arquivos são criados em /tmp e devem ser limpos pelo chamador.

        Returns:
            Tupla (cert_pem_path, key_pem_path)
        """
        import tempfile

        if not self._loaded:
            self.load()

        # Criar diretório temporário para os arquivos
        temp_dir = tempfile.mkdtemp(prefix="cert_")

        # Salvar certificado PEM
        cert_path = os.path.join(temp_dir, "cert.pem")
        with open(cert_path, "wb") as f:
            f.write(self.get_certificate_pem())

        # Salvar chave privada PEM
        key_path = os.path.join(temp_dir, "key.pem")
        with open(key_path, "wb") as f:
            f.write(self.get_private_key_pem())

        logger.debug(f"Certificado temporário criado em {temp_dir}")

        return (cert_path, key_path)


class CertificateStore:
    """
    Armazena e gerencia múltiplos certificados.

    Útil para empresas com múltiplos certificados (filiais, etc.)
    """

    def __init__(self, storage_path: str | None = None):
        """
        Inicializa o store.

        Args:
            storage_path: Diretório para armazenar certificados
        """
        self._storage_path = storage_path or "/opt/conecta-pro/certificates"
        self._certificates: dict[str, CertificateManager] = {}

    def add_certificate(self, identifier: str, pfx_data: bytes, password: str) -> CertificateInfo:
        """
        Adiciona certificado ao store.

        Args:
            identifier: Identificador único (ex: CNPJ)
            pfx_data: Bytes do arquivo .pfx
            password: Senha do certificado

        Returns:
            Informações do certificado
        """
        manager = CertificateManager(pfx_data=pfx_data, password=password)
        manager.load()

        self._certificates[identifier] = manager

        # Salvar em disco (opcional)
        if self._storage_path:
            self._save_certificate(identifier, pfx_data, password)

        return manager.info

    def add(self, identifier: str, manager: "CertificateManager") -> str:
        """
        Adiciona CertificateManager ja carregado ao store.

        Args:
            identifier: Identificador unico
            manager: CertificateManager ja carregado

        Returns:
            Identificador do certificado
        """
        self._certificates[identifier] = manager
        return identifier

    def get_certificate(self, identifier: str) -> Optional["CertificateManager"]:
        """Retorna certificado pelo identificador."""
        return self._certificates.get(identifier)

    def get(self, identifier: str) -> Optional["CertificateManager"]:
        """Alias para get_certificate."""
        return self.get_certificate(identifier)

    def remove_certificate(self, identifier: str) -> bool:
        """Remove certificado do store."""
        if identifier in self._certificates:
            del self._certificates[identifier]

            # Remover do disco
            if self._storage_path:
                self._delete_certificate_file(identifier)

            return True
        return False

    def remove(self, identifier: str) -> bool:
        """Alias para remove_certificate."""
        return self.remove_certificate(identifier)

    def list_certificates(self) -> dict[str, CertificateInfo]:
        """Lista todos os certificados."""
        return {identifier: manager.info for identifier, manager in self._certificates.items()}

    def list_all(self):
        """Alias para listar certificados como items."""
        return self._certificates.items()

    def _save_certificate(self, identifier: str, pfx_data: bytes, password: str):
        """Salva certificado em disco (criptografado)."""
        # TODO: Implementar criptografia adicional para armazenamento
        path = Path(self._storage_path)
        path.mkdir(parents=True, exist_ok=True)

        cert_path = path / f"{identifier}.pfx"
        with open(cert_path, "wb") as f:
            f.write(pfx_data)

        # Salvar hash da senha (não a senha em si)
        meta_path = path / f"{identifier}.meta"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        with open(meta_path, "w") as f:
            f.write(password_hash)

    def _delete_certificate_file(self, identifier: str):
        """Remove arquivos do certificado."""
        path = Path(self._storage_path)

        cert_path = path / f"{identifier}.pfx"
        meta_path = path / f"{identifier}.meta"

        if cert_path.exists():
            cert_path.unlink()
        if meta_path.exists():
            meta_path.unlink()
