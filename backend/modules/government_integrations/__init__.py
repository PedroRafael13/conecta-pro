"""
Module: government_integrations

DEPRECATED: Use 'modules.fiscal_contabil' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.

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

import warnings

warnings.warn(
    "Importing from 'modules.government_integrations' is deprecated. "
    "Use 'modules.fiscal_contabil' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from .controllers import router as government_integrations_router  # noqa: E402

# Re-export schemas para compatibilidade
from .schemas import (  # noqa: E402
    CalculoFGTSRequest,
    CalculoINSSRequest,
    ConsultaCNPJRequest,
    ConsultaCPFRequest,
    ESocialEventRequest,
    NFERequest,
    StandardResponse,
    ValidateDocumentRequest,
)

# Re-export services
from .services import (  # noqa: E402
    ESocialService,
    FGTSINSSService,
    ReceitaFederalApiService,
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
