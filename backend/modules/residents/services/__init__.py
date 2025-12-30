"""Services do módulo de Moradores."""

from modules.residents.services.resident_service import ResidentService
from modules.residents.services.vehicle_service import VehicleService
from modules.residents.services.pet_service import PetService
from modules.residents.services.dependent_service import DependentService
from modules.residents.services.emergency_contact_service import EmergencyContactService
from modules.residents.services.resident_ai_service import ResidentAIService

__all__ = [
    "ResidentService",
    "VehicleService",
    "PetService",
    "DependentService",
    "EmergencyContactService",
    "ResidentAIService",
]
