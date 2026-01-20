"""AI Fraud Detection Module - Sprint 45

Sistema de deteccao de fraudes usando IA para identificar
transacoes suspeitas, padroes anomalos e comportamentos de risco.
"""

from modules.ai.fraud_detection.controllers.fraud_controller import router

__all__ = ["router"]
