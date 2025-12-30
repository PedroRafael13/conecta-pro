"""Schemas para ResidentPet."""

from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.residents.models.pet import PetType, PetSize, PetStatus


# ========== Base Schemas ==========


class PetBase(BaseModel):
    """Schema base para Pet."""

    name: str = Field(..., min_length=1, max_length=100)
    pet_type: PetType
    breed: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=50)
    size: Optional[PetSize] = None
    weight_kg: Optional[float] = Field(None, ge=0, le=200)
    birth_date: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)


class PetCreate(PetBase):
    """Schema para criação de Pet."""

    resident_id: UUID
    microchip_number: Optional[str] = Field(None, max_length=50)
    registration_number: Optional[str] = Field(None, max_length=50)

    is_vaccinated: bool = False
    vaccination_date: Optional[date] = None
    vaccination_expiry: Optional[date] = None
    is_neutered: bool = False

    has_special_needs: bool = False
    special_needs_description: Optional[str] = None
    veterinarian_name: Optional[str] = Field(None, max_length=200)
    veterinarian_phone: Optional[str] = Field(None, max_length=20)

    is_aggressive: bool = False
    aggression_notes: Optional[str] = None
    is_noisy: bool = False
    behavior_notes: Optional[str] = None

    can_use_common_areas: bool = True
    allowed_areas: Optional[list[str]] = None

    photo_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class PetUpdate(BaseModel):
    """Schema para atualização de Pet."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    pet_type: Optional[PetType] = None
    status: Optional[PetStatus] = None
    breed: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=50)
    size: Optional[PetSize] = None
    weight_kg: Optional[float] = Field(None, ge=0, le=200)
    birth_date: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)

    microchip_number: Optional[str] = Field(None, max_length=50)
    registration_number: Optional[str] = Field(None, max_length=50)

    is_vaccinated: Optional[bool] = None
    vaccination_date: Optional[date] = None
    vaccination_expiry: Optional[date] = None
    is_neutered: Optional[bool] = None

    has_special_needs: Optional[bool] = None
    special_needs_description: Optional[str] = None
    veterinarian_name: Optional[str] = Field(None, max_length=200)
    veterinarian_phone: Optional[str] = Field(None, max_length=20)

    is_aggressive: Optional[bool] = None
    aggression_notes: Optional[str] = None
    is_noisy: Optional[bool] = None
    behavior_notes: Optional[str] = None

    can_use_common_areas: Optional[bool] = None
    allowed_areas: Optional[list[str]] = None

    photo_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class PetResponse(BaseModel):
    """Schema de resposta para Pet."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    resident_id: UUID
    name: str
    pet_type: PetType
    status: PetStatus

    breed: Optional[str] = None
    color: Optional[str] = None
    size: Optional[PetSize] = None
    weight_kg: Optional[float] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None

    microchip_number: Optional[str] = None
    registration_number: Optional[str] = None

    is_vaccinated: bool
    vaccination_date: Optional[date] = None
    vaccination_expiry: Optional[date] = None
    is_neutered: bool

    has_special_needs: bool
    special_needs_description: Optional[str] = None
    veterinarian_name: Optional[str] = None
    veterinarian_phone: Optional[str] = None

    is_aggressive: bool
    aggression_notes: Optional[str] = None
    is_noisy: bool
    behavior_notes: Optional[str] = None

    can_use_common_areas: bool
    allowed_areas: Optional[list[str]] = None

    photo_url: Optional[str] = None

    registration_date: date
    deactivation_date: Optional[date] = None

    is_active: bool
    age: Optional[int] = None
    age_months: Optional[int] = None
    vaccination_status: str
    full_description: str

    notes: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None


# ========== Action Schemas ==========


class PetUpdateVaccination(BaseModel):
    """Schema para atualizar vacinação."""

    vaccination_date: date
    expiry_date: date


# ========== Filter Schemas ==========


class PetFilter(BaseModel):
    """Schema para filtros de busca."""

    resident_id: Optional[UUID] = None
    pet_type: Optional[PetType] = None
    status: Optional[PetStatus] = None
    breed: Optional[str] = None
    size: Optional[PetSize] = None
    is_vaccinated: Optional[bool] = None
    is_neutered: Optional[bool] = None
    is_aggressive: Optional[bool] = None
    can_use_common_areas: Optional[bool] = None
    condominium_id: Optional[str] = None


# ========== List Response ==========


class PetListResponse(BaseModel):
    """Schema de resposta para lista de Pets."""

    items: list[PetResponse]
    total: int
    page: int
    page_size: int
    pages: int = 0


# ========== Stats ==========


class PetStats(BaseModel):
    """Estatísticas de pets."""

    total: int = 0
    active: int = 0
    by_type: dict = {}
    by_size: dict = {}
    vaccinated: int = 0
    not_vaccinated: int = 0
    vaccination_expiring: int = 0
    neutered: int = 0
    aggressive: int = 0
    with_special_needs: int = 0
