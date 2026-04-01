"""
Clients Module - Services
Sprint 30: Cadastro de Clientes/Condomínios
"""

from modules.clients.services.client_ai_service import ClientAIService
from modules.clients.services.client_service import ClientService

__all__ = ["ClientService", "ClientAIService"]
