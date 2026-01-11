"""
Module: government_integrations
Description: API Controllers para Integracoes Governamentais
Author: Conecta PRO Team
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: Legislacao fiscal e trabalhista brasileira

Estrutura modular:
- controllers/: Endpoints REST organizados por domínio
- services/: Lógica de negócio
- schemas/: Schemas Pydantic para validação
- models/: Models SQLAlchemy (preparado para expansão)
- repositories/: Acesso a dados (preparado para expansão)

Domínios:
- Receita Federal: Validação e consulta CPF/CNPJ
- FGTS/INSS: Cálculos trabalhistas
- eSocial: Transmissão de eventos
- SEFAZ: Emissão de NFe/NFCe
"""

from .controllers import router as government_integrations_router

# Re-export schemas para compatibilidade
from .schemas import (
    StandardResponse,
    ValidateDocumentRequest,
    ConsultaCPFRequest,
    ConsultaCNPJRequest,
    CalculoFGTSRequest,
    CalculoINSSRequest,
    ESocialEventRequest,
    NFERequest,
)

# Re-export services
from .services import (
    ReceitaFederalApiService,
    FGTSINSSService,
    ESocialService,
    SEFAZService,
)

__all__ = [
    # Router principal
    "government_integrations_router",
    # Schemas
    "StandardResponse",
    "ValidateDocumentRequest",
    "ConsultaCPFRequest",
    "ConsultaCNPJRequest",
    "CalculoFGTSRequest",
    "CalculoINSSRequest",
    "ESocialEventRequest",
    "NFERequest",
    # Services
    "ReceitaFederalApiService",
    "FGTSINSSService",
    "ESocialService",
    "SEFAZService",
]

__version__ = "1.0.0"
