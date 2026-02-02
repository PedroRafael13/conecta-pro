"""
Schemas Pydantic para Employee (Funcionário).
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, EmailStr, validator
import re


class EmployeeBase(BaseModel):
    """Schema base para Employee."""

    nome: str = Field(..., min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    matricula: Optional[str] = Field(None, max_length=50)
    cpf: Optional[str] = Field(None, max_length=14)
    cargo: Optional[str] = Field(None, max_length=100)
    departamento: Optional[str] = Field(None, max_length=100)
    telefone: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(default="Ativo", max_length=50)

    @validator('cpf')
    def validar_cpf(cls, v):  # noqa: N805
        """Valida formato de CPF."""
        if v is None:
            return v
        # Remove caracteres não numéricos
        cpf = re.sub(r'\D', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return cpf

    @validator('telefone')
    def validar_telefone(cls, v):  # noqa: N805
        """Valida formato de telefone."""
        if v is None:
            return v
        # Remove caracteres não numéricos
        telefone = re.sub(r'\D', '', v)
        if len(telefone) < 10 or len(telefone) > 11:
            raise ValueError('Telefone deve ter 10 ou 11 dígitos')
        return telefone


class EmployeeCreate(EmployeeBase):
    """Schema para criação de Employee."""

    # Campos obrigatórios na criação
    nome: str = Field(..., min_length=1, max_length=200, description="Nome completo do funcionário")
    email: EmailStr = Field(..., description="Email corporativo único")
    matricula: str = Field(..., min_length=1, max_length=50, description="Matrícula única")

    # Campos opcionais
    data_admissao: Optional[str] = None
    pis: Optional[str] = None


class EmployeeUpdate(BaseModel):
    """Schema para atualização de Employee."""

    cargo: Optional[str] = Field(None, max_length=100)
    departamento: Optional[str] = Field(None, max_length=100)
    telefone: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None

    @validator('telefone')
    def validar_telefone(cls, v):  # noqa: N805
        """Valida formato de telefone."""
        if v is None:
            return v
        telefone = re.sub(r'\D', '', v)
        if len(telefone) < 10 or len(telefone) > 11:
            raise ValueError('Telefone deve ter 10 ou 11 dígitos')
        return telefone


class EmployeeResponse(BaseModel):
    """Schema de resposta para Employee."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    email: Optional[str] = None
    matricula: Optional[str] = None
    cargo: Optional[str] = None
    departamento: Optional[str] = None
    status: Optional[str] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None


class EmployeeListResponse(BaseModel):
    """Schema para listagem paginada de Employees."""

    items: List[EmployeeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== INTEGRAÇÃO SOLIDES DP ====================


class SolidesEmployeeResponse(BaseModel):
    """Schema de resposta para funcionario do Solides DP."""

    id: str
    nome: str
    email: Optional[str] = None
    matricula: Optional[str] = None
    cargo: Optional[str] = None
    departamento: Optional[str] = None
    status: Optional[str] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    data_admissao: Optional[str] = None
    pis: Optional[str] = None


class SolidesEmployeeListResponse(BaseModel):
    """Schema para listagem de funcionarios do Solides."""

    items: List[SolidesEmployeeResponse]
    total: int
    source: str = "solides"
