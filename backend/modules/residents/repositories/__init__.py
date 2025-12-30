"""Repositories do módulo de Moradores."""

from modules.residents.repositories.resident_repository import ResidentRepository
from modules.residents.repositories.vehicle_repository import VehicleRepository
from modules.residents.repositories.pet_repository import PetRepository
from modules.residents.repositories.dependent_repository import DependentRepository
from modules.residents.repositories.emergency_contact_repository import (
    EmergencyContactRepository,
)

__all__ = [
    "ResidentRepository",
    "VehicleRepository",
    "PetRepository",
    "DependentRepository",
    "EmergencyContactRepository",
]
