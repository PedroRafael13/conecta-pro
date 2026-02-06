"""
AI Inventory Forecast Module - Sprint 43

Previsao inteligente de estoque usando Machine Learning.
Funcionalidades:
- Previsao de demanda por produto (7-90 dias)
- Ponto de reposicao automatico
- Analise de sazonalidade
- Sugestao de quantidade de compra
- Deteccao de tendencias
"""

from modules.ai.inventory_forecast.controllers.forecast_controller import router

__all__ = ["router"]
