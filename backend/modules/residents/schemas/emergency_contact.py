"""Schemas para ResidentEmergencyContact."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, EmailStr

from modules.residents.models.emergency_contact import ContactRelationship


# ========== Base Schemas ==========


class EmergencyContactBase(BaseModel):
    """Schema base para EmergencyContact."""

    name: str = Field(..., min_length=2, max_length=200)
    relationship: ContactRelationship = ContactRelationship.FAMILIAR
    relationship_description: Optional[str] = Field(None, max_length=100)
    phone: str = Field(..., min_length=8, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None


class EmergencyContactCreate(EmergencyContactBase):
    """Schema para criação de EmergencyContact."""

    resident_id: UUID
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    priority: int = Field(1, ge=1, le=10)
    is_primary: bool = False
    notes: Optional[str] = None


class EmergencyContactUpdate(BaseModel):
    """Schema para atualização de EmergencyContact."""

    name: Optional[str] = Field(None, min_length=2, max_length=200)
    relationship: Optional[ContactRelationship] = None
    relationship_description: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    priority: Optional[int] = Field(None, ge=1, le=10)
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class EmergencyContactResponse(BaseModel):
    """Schema de resposta para EmergencyContact."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    resident_id: UUID
    name: str
    relationship: ContactRelationship
    relationship_description: Optional[str] = None

    phone: str
    phone_secondary: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None

    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

    priority: int
    is_primary: bool
    is_active: bool

    full_contact_info: str
    relationship_display: str

    notes: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None


# ========== Filter Schemas ==========


class EmergencyContactFilter(BaseModel):
    """Schema para filtros de busca."""

    resident_id: Optional[UUID] = None
    relationship: Optional[ContactRelationship] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


# ========== List Response ==========


class EmergencyContactListResponse(BaseModel):
    """Schema de resposta para lista de EmergencyContacts."""

    items: list[EmergencyContactResponse]
    total: int
    page: int
    page_size: int
    pages: int = 0
