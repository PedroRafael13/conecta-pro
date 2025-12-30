"""
Módulo de Moradores (Residents) - Sprint 13.

Este módulo gerencia moradores e suas informações relacionadas:
- Residents: Moradores (proprietários, inquilinos, funcionários)
- Vehicles: Veículos dos moradores
- Pets: Animais de estimação
- Dependents: Dependentes e funcionários domésticos
- EmergencyContacts: Contatos de emergência

Features:
- CRUD completo para todas as entidades
- Gestão de bloqueios e inadimplência
- Controle de acesso (biometria, cartão, facial, QR code)
- Análise de perfil com IA
- Insights e dashboard com métricas
- Predição de risco de mudança (churn)
"""

from modules.residents.models import (
    Resident,
    ResidentVehicle,
    ResidentPet,
    ResidentDependent,
    ResidentEmergencyContact,
    ResidentStatus,
    ResidentType,
    VehicleStatus,
    VehicleType,
    PetStatus,
    PetType,
    PetSize,
    DependentStatus,
    RelationshipType,
    ContactRelationship,
)

from modules.residents.services import (
    ResidentService,
    VehicleService,
    PetService,
    DependentService,
    EmergencyContactService,
    ResidentAIService,
)

from modules.residents.controllers import (
    resident_router,
    vehicle_router,
    pet_router,
    dependent_router,
    emergency_contact_router,
    resident_ai_router,
)

__all__ = [
    # Models
    "Resident",
    "ResidentVehicle",
    "ResidentPet",
    "ResidentDependent",
    "ResidentEmergencyContact",
    # Enums
    "ResidentStatus",
    "ResidentType",
    "VehicleStatus",
    "VehicleType",
    "PetStatus",
    "PetType",
    "PetSize",
    "DependentStatus",
    "RelationshipType",
    "ContactRelationship",
    # Services
    "ResidentService",
    "VehicleService",
    "PetService",
    "DependentService",
    "EmergencyContactService",
    "ResidentAIService",
    # Routers
    "resident_router",
    "vehicle_router",
    "pet_router",
    "dependent_router",
    "emergency_contact_router",
    "resident_ai_router",
]
