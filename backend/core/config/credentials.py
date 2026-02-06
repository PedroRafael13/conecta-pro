"""
Module: Credentials Manager
Description: Gerenciamento seguro de credenciais para integrações governamentais
Author: Conecta PRO Team
Date: 2026-01-16
"""

import logging
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Carrega credenciais do arquivo seguro
CREDENTIALS_FILE = Path("/opt/conecta-pro/credentials/.env.credentials")
if CREDENTIALS_FILE.exists():
    load_dotenv(CREDENTIALS_FILE)
    logger.info("Credenciais carregadas de %s", CREDENTIALS_FILE)

# Prefixo que indica valor criptografado
ENC_PREFIX = "ENC:"

# Cache da instância Fernet para evitar recriação
_fernet_instance = None


def _get_fernet():
    """Obtém instância Fernet para descriptografia."""
    global _fernet_instance
    if _fernet_instance is not None:
        return _fernet_instance

    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        return None

    try:
        from cryptography.fernet import Fernet

        _fernet_instance = Fernet(key.encode())
        return _fernet_instance
    except Exception as e:
        logger.error("ENCRYPTION_KEY inválida: %s", e)
        return None


def _decrypt_if_needed(value: str | None) -> str | None:
    """Descriptografa valor se tiver prefixo ENC:."""
    if not value or not value.startswith(ENC_PREFIX):
        return value

    fernet = _get_fernet()
    if not fernet:
        logger.error("Valor criptografado encontrado mas ENCRYPTION_KEY não configurada")
        return None

    try:
        encrypted_data = value[len(ENC_PREFIX) :]
        return fernet.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        logger.error("Falha ao descriptografar credencial: %s", e)
        return None


class CertificateCredentials(BaseModel):
    """Credenciais do certificado digital."""

    path: str | None = None
    password: str | None = None

    @property
    def is_configured(self) -> bool:
        """Verifica se certificado está configurado."""
        return bool(self.path and self.password and Path(self.path).exists())


class GovBRCredentials(BaseModel):
    """Credenciais do gov.br."""

    client_id: str | None = None
    client_secret: str | None = None

    @property
    def is_configured(self) -> bool:
        """Verifica se gov.br está configurado."""
        return bool(self.client_id and self.client_secret)


class GovernmentCredentials(BaseModel):
    """Todas as credenciais governamentais."""

    certificate: CertificateCredentials
    govbr: GovBRCredentials
    esocial_environment: str = "2"  # 1=Prod, 2=Homolog
    sefaz_environment: str = "2"  # 1=Prod, 2=Homolog


@lru_cache
def get_government_credentials() -> GovernmentCredentials:
    """
    Retorna credenciais governamentais do ambiente.
    Descriptografa automaticamente valores com prefixo ENC:.

    Returns:
        GovernmentCredentials: Credenciais carregadas.
    """
    return GovernmentCredentials(
        certificate=CertificateCredentials(
            path=os.getenv("CERTIFICATE_PATH"),
            password=_decrypt_if_needed(os.getenv("CERTIFICATE_PASSWORD")),
        ),
        govbr=GovBRCredentials(
            client_id=os.getenv("GOVBR_CLIENT_ID"),
            client_secret=_decrypt_if_needed(os.getenv("GOVBR_CLIENT_SECRET")),
        ),
        esocial_environment=os.getenv("ESOCIAL_ENVIRONMENT", "2"),
        sefaz_environment=os.getenv("SEFAZ_ENVIRONMENT", "2"),
    )


def get_certificate_path() -> str | None:
    """Retorna caminho do certificado."""
    return get_government_credentials().certificate.path


def get_certificate_password() -> str | None:
    """Retorna senha do certificado."""
    return get_government_credentials().certificate.password


def is_certificate_configured() -> bool:
    """Verifica se certificado está configurado."""
    return get_government_credentials().certificate.is_configured


def get_esocial_environment() -> str:
    """Retorna ambiente do eSocial (1=Prod, 2=Homolog)."""
    return get_government_credentials().esocial_environment


def get_sefaz_environment() -> str:
    """Retorna ambiente da SEFAZ (1=Prod, 2=Homolog)."""
    return get_government_credentials().sefaz_environment
