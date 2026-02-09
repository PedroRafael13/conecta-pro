"""Configuracoes do Bartolo."""

from modules.ai.bartolo.config.identity import (
    BARTOLO_IDENTITY,
    BARTOLO_PERSONALITY,
    BartoloConfig,
)
from modules.ai.bartolo.config.modules import (
    MODULE_CAPABILITIES,
    MODULE_PROMPTS,
    get_module_prompt,
)
from modules.ai.bartolo.config.user_profiles import (
    USER_PROFILES,
    get_profile_context,
)

__all__ = [
    "BARTOLO_IDENTITY",
    "BARTOLO_PERSONALITY",
    "BartoloConfig",
    "MODULE_PROMPTS",
    "MODULE_CAPABILITIES",
    "get_module_prompt",
    "USER_PROFILES",
    "get_profile_context",
]
