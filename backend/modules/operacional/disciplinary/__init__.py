"""
Module: disciplinary
Description: Modulo de Medidas Administrativas (Disciplinares)
Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100

Este modulo fornece gestao completa de medidas disciplinares:
- Advertencias verbais e escritas
- Suspensoes
- Demissoes por justa causa
- Templates de documentos
- Assinaturas digitais
- Workflow de aprovacao
- Recomendacoes por IA

Estrutura modular:
- models/: Modelos SQLAlchemy para persistencia
- schemas/: Schemas Pydantic para validacao
- services/: Logica de negocio e IA
- controllers/: Endpoints FastAPI
- repositories/: Acesso a dados

Endpoints disponiveis:
- POST   /api/v1/operacional/medidas-administrativas
- GET    /api/v1/operacional/medidas-administrativas
- GET    /api/v1/operacional/medidas-administrativas/{id}
- PATCH  /api/v1/operacional/medidas-administrativas/{id}
- DELETE /api/v1/operacional/medidas-administrativas/{id}
- POST   /api/v1/operacional/medidas-administrativas/{id}/submeter
- POST   /api/v1/operacional/medidas-administrativas/{id}/aprovar
- POST   /api/v1/operacional/medidas-administrativas/{id}/rejeitar
- POST   /api/v1/operacional/medidas-administrativas/{id}/assinar
- POST   /api/v1/operacional/medidas-administrativas/{id}/recusar-assinatura
- GET    /api/v1/operacional/medidas-administrativas/funcionario/{employee_id}
- GET    /api/v1/operacional/medidas-administrativas/pendentes
- GET    /api/v1/operacional/medidas-administrativas/estatisticas
- GET    /api/v1/operacional/medidas-administrativas/templates
- POST   /api/v1/operacional/medidas-administrativas/templates
- GET    /api/v1/operacional/medidas-administrativas/templates/{id}
- POST   /api/v1/operacional/medidas-administrativas/gerar-documento
- POST   /api/v1/operacional/assinaturas/verificar
- GET    /api/v1/operacional/assinaturas/{id}
- GET    /api/v1/operacional/assinaturas/documento/{doc_id}
- POST   /api/v1/operacional/medidas-administrativas/ia/recomendar
- POST   /api/v1/operacional/medidas-administrativas/ia/validar-conformidade
- POST   /api/v1/operacional/medidas-administrativas/ia/verificar-proporcionalidade
"""

from fastapi import APIRouter

# Importa routers dos controllers
from .controllers import disciplinary_router

# Re-export models
from .models import (
    DigitalSignature,
    DisciplinaryAction,
    DisciplinaryActionStatus,
    DisciplinaryActionType,
    DisciplinaryTemplate,
    ReasonCategory,
    SignerType,
)

# Re-export repositories
from .repositories import (
    DisciplinaryRepository,
    SignatureRepository,
    TemplateRepository,
)

# Re-export schemas
from .schemas import (
    DisciplinaryActionCreate,
    DisciplinaryActionListResponse,
    DisciplinaryActionResponse,
    DisciplinaryActionUpdate,
    DisciplinaryFilter,
    SignatureCreate,
    SignatureResponse,
    TemplateCreate,
    TemplateResponse,
)

# Re-export services
from .services import (
    DisciplinaryAdvisor,
    DisciplinaryService,
    SignatureService,
    TemplateService,
    get_disciplinary_advisor,
    get_disciplinary_service,
    get_signature_service,
    get_template_service,
)

# Cria router principal
router = APIRouter()
router.include_router(disciplinary_router)

__all__ = [
    # Router
    "router",
    "disciplinary_router",
    # Models
    "DisciplinaryAction",
    "DisciplinaryActionType",
    "DisciplinaryActionStatus",
    "ReasonCategory",
    "DisciplinaryTemplate",
    "DigitalSignature",
    "SignerType",
    # Services
    "DisciplinaryService",
    "TemplateService",
    "SignatureService",
    "DisciplinaryAdvisor",
    "get_disciplinary_service",
    "get_template_service",
    "get_signature_service",
    "get_disciplinary_advisor",
    # Repositories
    "DisciplinaryRepository",
    "TemplateRepository",
    "SignatureRepository",
    # Schemas
    "DisciplinaryActionCreate",
    "DisciplinaryActionUpdate",
    "DisciplinaryActionResponse",
    "DisciplinaryActionListResponse",
    "DisciplinaryFilter",
    "TemplateCreate",
    "TemplateResponse",
    "SignatureCreate",
    "SignatureResponse",
]

__version__ = "1.0.0"
