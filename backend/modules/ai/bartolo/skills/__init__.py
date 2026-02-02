"""
Skills do Bartolo Operacional
"""

from typing import TYPE_CHECKING, Optional

from .alerta_skill import AlertaSkill
from .banco_horas_skill import BancoHorasSkill
from .base_skill import BaseSkill
from .cobertura_skill import CoberturaSkill
from .comunicado_skill import ComunicadoSkill
from .diarista_skill import DiaristaSkill
from .disciplinar_skill import DisciplinarSkill
from .escala_skill import EscalaSkill
from .ocorrencia_skill import OcorrenciaSkill
from .openclaw_skill import OpenClawSkill
from .posto_skill import PostoSkill
from .ronda_skill import RondaSkill
from .substituto_skill import SubstitutoSkill

if TYPE_CHECKING:
    from modules.ai.bartolo.services.data_connector import DataConnector

__all__ = [
    "BaseSkill",
    "EscalaSkill",
    "CoberturaSkill",
    "SubstitutoSkill",
    "AlertaSkill",
    "OcorrenciaSkill",
    "DisciplinarSkill",
    "RondaSkill",
    "DiaristaSkill",
    "ComunicadoSkill",
    "BancoHorasSkill",
    "PostoSkill",
    "OpenClawSkill",
]

# Registry de skills disponiveis
SKILL_REGISTRY = {
    "escala": EscalaSkill,
    "cobertura": CoberturaSkill,
    "substituto": SubstitutoSkill,
    "alerta": AlertaSkill,
    "ocorrencia": OcorrenciaSkill,
    "disciplinar": DisciplinarSkill,
    "ronda": RondaSkill,
    "diarista": DiaristaSkill,
    "comunicado": ComunicadoSkill,
    "banco_horas": BancoHorasSkill,
    "posto": PostoSkill,
    "openclaw": OpenClawSkill,
}


def get_skill(name: str, data_connector: Optional["DataConnector"] = None) -> BaseSkill:
    """Retorna instancia da skill pelo nome.

    Args:
        name: Nome da skill (ex: 'escala', 'cobertura')
        data_connector: DataConnector para dados reais. Se None, usa fallback estatico.
    """
    skill_class = SKILL_REGISTRY.get(name)
    if skill_class:
        return skill_class(data_connector=data_connector)
    return None


def list_skills() -> list:
    """Lista todas as skills disponiveis"""
    return list(SKILL_REGISTRY.keys())
