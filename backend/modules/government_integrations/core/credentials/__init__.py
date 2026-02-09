"""
Sistema de Governança de Credenciais.

Implementa:
- Integração com HashiCorp Vault
- Gerenciamento de certificados digitais
- Rotação automática de credenciais
- Auditoria de acesso
- Modo simplificado via arquivo (sem Vault)
"""

from .certificate_manager import (
    CertificadoInfo,
    GerenciadorCertificados,
    TipoCertificado,
)
from .credential_provider import (
    CredencialGoverno,
    ProvedorCredenciais,
    TipoCredencial,
    get_credential_provider,
)
from .file_credential_provider import (
    FileCredentialConfig,
    FileCredentialProvider,
    get_file_credential_provider,
)
from .vault_client import (
    VaultClient,
    VaultConfig,
    get_vault_client,
)

__all__ = [
    # Vault
    "VaultClient",
    "VaultConfig",
    "get_vault_client",
    # Certificates
    "GerenciadorCertificados",
    "CertificadoInfo",
    "TipoCertificado",
    # Provider
    "ProvedorCredenciais",
    "CredencialGoverno",
    "TipoCredencial",
    "get_credential_provider",
    # File Provider (simplified)
    "FileCredentialProvider",
    "FileCredentialConfig",
    "get_file_credential_provider",
]
