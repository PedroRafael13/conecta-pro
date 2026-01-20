"""
Module: Credentials Manager
Description: Gerenciamento seguro de credenciais para integrações governamentais
Author: Conecta PRO Team
Date: 2026-01-16
"""

import os
from pathlib import Path
from typing import Optional
from functools import lru_cache
import logging

from pydantic import BaseModel
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Carrega credenciais do arquivo seguro
CREDENTIALS_FILE = Path("/opt/conecta-pro/credentials/.env.credentials")
if CREDENTIALS_FILE.exists():
    load_dotenv(CREDENTIALS_FILE)
    logger.info("Credenciais carregadas de %s", CREDENTIALS_FILE)


class CertificateCredentials(BaseModel):
    """Credenciais do certificado digital."""
    path: Optional[str] = None
    password: Optional[str] = None

    @property
    def is_configured(self) -> bool:
        """Verifica se certificado está configurado."""
        return bool(self.path and self.password and Path(self.path).exists())


class GovBRCredentials(BaseModel):
    """Credenciais do gov.br."""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

    @property
    def is_configured(self) -> bool:
        """Verifica se gov.br está configurado."""
        return bool(self.client_id and self.client_secret)


class GovernmentCredentials(BaseModel):
    """Todas as credenciais governamentais."""
    certificate: CertificateCredentials
    govbr: GovBRCredentials
    esocial_environment: str = "2"  # 1=Prod, 2=Homolog
    sefaz_environment: str = "2"    # 1=Prod, 2=Homolog


@lru_cache()
def get_government_credentials() -> GovernmentCredentials:
    """
    Retorna credenciais governamentais do ambiente.

    Returns:
        GovernmentCredentials: Credenciais carregadas.
    """
    return GovernmentCredentials(
        certificate=CertificateCredentials(
            path=os.getenv("CERTIFICATE_PATH"),
            password=os.getenv("CERTIFICATE_PASSWORD"),
        ),
        govbr=GovBRCredentials(
            client_id=os.getenv("GOVBR_CLIENT_ID"),
            client_secret=os.getenv("GOVBR_CLIENT_SECRET"),
        ),
        esocial_environment=os.getenv("ESOCIAL_ENVIRONMENT", "2"),
        sefaz_environment=os.getenv("SEFAZ_ENVIRONMENT", "2"),
    )


def get_certificate_path() -> Optional[str]:
    """Retorna caminho do certificado."""
    return get_government_credentials().certificate.path


def get_certificate_password() -> Optional[str]:
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
