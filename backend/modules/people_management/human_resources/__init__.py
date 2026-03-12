"""
Modulo de Recursos Humanos (RH) - Conecta PRO.

Modulo agregador que centraliza funcionalidades de gestao de pessoas:
- Recrutamento e Selecao (re-exportado de recruitment)
- Treinamento e Desenvolvimento (novo)
- Avaliacao de Desempenho (novo)
- Plano de Carreira (novo)
- Clima Organizacional (re-exportado de retention/climate)
- Predicao de Turnover (re-exportado de retention/turnover)
- Onboarding Digital (re-exportado de retention/onboarding)
- IA para RH (candidate scoring, turnover prediction, climate analysis)
"""

from modules.people_management.human_resources.aggregator import router

__all__ = ["router"]
