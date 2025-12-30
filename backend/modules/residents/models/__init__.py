"""Models do módulo de Moradores."""

from modules.residents.models.resident import (
    Resident,
    ResidentType,
    ResidentStatus,
    DocumentType,
    Gender,
    MaritalStatus,
    AccessMethod,
)
from modules.residents.models.vehicle import (
    ResidentVehicle,
    VehicleType,
    VehicleStatus,
    FuelType,
)
from modules.residents.models.pet import (
    ResidentPet,
    PetType,
    PetSize,
    PetStatus,
)
from modules.residents.models.dependent import (
    ResidentDependent,
    RelationshipType,
    DependentStatus,
    DependentDocumentType,
)
from modules.residents.models.emergency_contact import (
    ResidentEmergencyContact,
    ContactRelationship,
)

__all__ = [
    # Models
    "Resident",
    "ResidentVehicle",
    "ResidentPet",
    "ResidentDependent",
    "ResidentEmergencyContact",
    # Resident Enums
    "ResidentType",
    "ResidentStatus",
    "DocumentType",
    "Gender",
    "MaritalStatus",
    "AccessMethod",
    # Vehicle Enums
    "VehicleType",
    "VehicleStatus",
    "FuelType",
    # Pet Enums
    "PetType",
    "PetSize",
    "PetStatus",
    # Dependent Enums
    "RelationshipType",
    "DependentStatus",
    "DependentDocumentType",
    # Emergency Contact Enums
    "ContactRelationship",
]
