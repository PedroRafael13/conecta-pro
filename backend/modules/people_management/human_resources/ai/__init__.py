"""
Modulos de IA para Recursos Humanos.

Exporta servicos de inteligencia artificial para:
- Scoring de candidatos (recrutamento)
- Predicao de turnover (retencao)
- Analise de clima organizacional
"""

from modules.people_management.human_resources.ai.candidate_scoring_ai import (
    CandidateScoringAI,
)
from modules.people_management.human_resources.ai.climate_analysis_ai import (
    ClimateAnalysisAI,
)
from modules.people_management.human_resources.ai.turnover_prediction_ai import (
    TurnoverPredictionAI,
)

__all__ = [
    "CandidateScoringAI",
    "TurnoverPredictionAI",
    "ClimateAnalysisAI",
]
