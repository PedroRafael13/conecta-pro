"""
Bartolo - Assistente Inteligente do Conecta PRO.

O Bartolo e o assistente virtual oficial do Conecta PRO.
Ele conhece todos os modulos do sistema, entende o perfil de cada usuario
e oferece assistencia guiada para todas as operacoes.

Funcionalidades:
- Conhecimento completo de todos os 28+ modulos
- Consciencia do perfil e permissoes do usuario
- Assistencia guiada (wizards) para processos complexos
- Integracao com Knowledge Base (RAG)
- Consulta a dados reais do sistema
- Aprendizado continuo com feedback
- Personalidade consistente e humanizada

Autor: Conecta PRO Team
Sprint: Bartolo v1.0
"""

from modules.ai.bartolo.config.identity import (
    BARTOLO_IDENTITY,
    BARTOLO_PERSONALITY,
    BartoloConfig,
)
from modules.ai.bartolo.config.modules import (
    MODULE_PROMPTS,
    MODULE_CAPABILITIES,
    get_module_prompt,
)
from modules.ai.bartolo.config.user_profiles import (
    USER_PROFILES,
    get_profile_context,
)
from modules.ai.bartolo.services.bartolo_engine import BartoloEngine
from modules.ai.bartolo.services.profile_service import ProfileService
from modules.ai.bartolo.services.data_connector import DataConnector
from modules.ai.bartolo.services.learning_service import LearningService
from modules.ai.bartolo.wizards.wizard_manager import WizardManager
from modules.ai.bartolo.controllers.bartolo_controller import bartolo_router

__all__ = [
    # Config
    "BARTOLO_IDENTITY",
    "BARTOLO_PERSONALITY",
    "BartoloConfig",
    "MODULE_PROMPTS",
    "MODULE_CAPABILITIES",
    "get_module_prompt",
    "USER_PROFILES",
    "get_profile_context",
    # Services
    "BartoloEngine",
    "ProfileService",
    "DataConnector",
    "LearningService",
    # Wizards
    "WizardManager",
    # Controller
    "bartolo_router",
]
