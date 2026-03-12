"""
Operations AI — Modulos de inteligencia artificial para operacoes.

Inclui:
- ScaleOptimizerAI: Otimizacao de escalas com scoring multi-fator
- OccurrenceClassifierAI: Classificacao automatica de ocorrencias
"""

from .occurrence_classifier_ai import OccurrenceClassifierAI
from .scale_optimizer_ai import ScaleOptimizerAI

__all__ = [
    "ScaleOptimizerAI",
    "OccurrenceClassifierAI",
]
