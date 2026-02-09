"""
Sistema de Auditoria e Compliance LGPD.

Implementa:
- Audit trail para todas as operações
- Mascaramento de dados sensíveis
- Controle de acesso a dados pessoais
- Relatórios de compliance
"""

from .audit_logger import (
    AuditEvent,
    AuditLogger,
    TipoEvento,
    get_audit_logger,
)
from .data_masking import (
    MascaradorDados,
    TipoDadoSensivel,
    mascarar_cnpj,
    mascarar_cpf,
    mascarar_email,
)
from .lgpd_compliance import (
    ConsentimentoStatus,
    ControleLGPD,
    SolicitacaoTitular,
    get_lgpd_control,
)

__all__ = [
    # Audit
    "AuditLogger",
    "AuditEvent",
    "TipoEvento",
    "get_audit_logger",
    # Masking
    "MascaradorDados",
    "TipoDadoSensivel",
    "mascarar_cpf",
    "mascarar_cnpj",
    "mascarar_email",
    # LGPD
    "ControleLGPD",
    "ConsentimentoStatus",
    "SolicitacaoTitular",
    "get_lgpd_control",
]
