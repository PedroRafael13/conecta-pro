"""Wizards do Bartolo - Assistencia Guiada."""

from modules.ai.bartolo.wizards.admissao_wizard import AdmissaoWizard
from modules.ai.bartolo.wizards.banco_horas_wizard import BancoHorasWizard
from modules.ai.bartolo.wizards.base_wizard import BaseWizard, WizardState, WizardStep
from modules.ai.bartolo.wizards.comunicado_wizard import ComunicadoWizard
from modules.ai.bartolo.wizards.diarista_wizard import DiaristaWizard
from modules.ai.bartolo.wizards.disciplinar_wizard import DisciplinarWizard
from modules.ai.bartolo.wizards.escala_wizard import EscalaWizard
from modules.ai.bartolo.wizards.ocorrencia_wizard import OcorrenciaWizard
from modules.ai.bartolo.wizards.posto_wizard import PostoWizard
from modules.ai.bartolo.wizards.proposta_wizard import PropostaComercialWizard
from modules.ai.bartolo.wizards.ronda_wizard import RondaWizard
from modules.ai.bartolo.wizards.wizard_manager import WizardManager

__all__ = [
    "WizardManager",
    "BaseWizard",
    "WizardStep",
    "WizardState",
    "PropostaComercialWizard",
    "AdmissaoWizard",
    "OcorrenciaWizard",
    "DisciplinarWizard",
    "RondaWizard",
    "BancoHorasWizard",
    "EscalaWizard",
    "PostoWizard",
    "DiaristaWizard",
    "ComunicadoWizard",
]
