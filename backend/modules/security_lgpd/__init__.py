"""
Module: security_lgpd
Description: Modulo de Seguranca e Compliance LGPD
Author: Conecta PRO Team
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: LGPD - Lei Geral de Protecao de Dados (Lei 13.709/2018)

Este modulo fornece:
- Criptografia e mascaramento de dados sensiveis
- Gerenciamento de consentimento LGPD
- Direito ao esquecimento (data erasure)
- Avaliacao de impacto de privacidade (PIA/DPIA)
- Auditoria com hash chain

Estrutura modular:
- models/: Modelos SQLAlchemy para persistencia
- schemas/: Schemas Pydantic para validacao
- services/: Logica de negocio
- controllers/: Endpoints FastAPI
- repositories/: Acesso a dados
"""

from fastapi import APIRouter

from modules.security_lgpd.controllers.audit_controller import router as audit_router
from modules.security_lgpd.controllers.consent_controller import router as consent_router

# Importa routers dos controllers
from modules.security_lgpd.controllers.encryption_controller import router as encryption_router
from modules.security_lgpd.controllers.erasure_controller import router as erasure_router
from modules.security_lgpd.controllers.masking_controller import router as masking_router
from modules.security_lgpd.controllers.pia_controller import router as pia_router
from modules.security_lgpd.controllers.status_controller import router as status_router

# Cria router principal que agrega todos os sub-routers
security_lgpd_router = APIRouter(prefix="/lgpd", tags=["Security - LGPD Compliance"])

# Inclui todos os sub-routers
security_lgpd_router.include_router(encryption_router)
security_lgpd_router.include_router(masking_router)
security_lgpd_router.include_router(consent_router)
security_lgpd_router.include_router(erasure_router)
security_lgpd_router.include_router(pia_router)
security_lgpd_router.include_router(audit_router)
security_lgpd_router.include_router(status_router)

# Exporta tambem o router antigo para compatibilidade
router = security_lgpd_router

__all__ = [
    # Router principal
    "security_lgpd_router",
    "router",
    # Routers individuais
    "encryption_router",
    "masking_router",
    "consent_router",
    "erasure_router",
    "pia_router",
    "audit_router",
    "status_router",
]

__version__ = "1.0.0"
