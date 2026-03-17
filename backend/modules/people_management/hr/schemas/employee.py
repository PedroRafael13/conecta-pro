"""
Schemas Pydantic para Employee no contexto do Departamento Pessoal.

Visão DP-específica do funcionário: dados pessoais, trabalhistas e financeiros.
"""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DPEmployeeRead(BaseModel):
    """Schema de leitura de Employee para o DP."""

    model_config = ConfigDict(from_attributes=True)

    id: str | UUID
    nome: str
    nome_social: str | None = None
    cpf: str | None = None
    rg: str | None = None
    email: str | None = None
    matricula: str | None = None
    cargo: str | None = None
    departamento: str | None = None
    status: str | None = None
    data_admissao: date | None = None
    data_demissao: date | None = None
    salario_base: float | None = None
    pis: str | None = None
    ctps: str | None = None
    ctps_serie: str | None = None
    telefone: str | None = None
    data_nascimento: date | None = None
    sexo: str | None = None
    estado_civil: str | None = None


class DPEmployeeList(BaseModel):
    """Schema para listagem paginada de Employees no DP."""

    model_config = ConfigDict(from_attributes=True)

    items: list[DPEmployeeRead]
    total: int
    page: int
    page_size: int
    total_pages: int


class DPEmployeeUpdate(BaseModel):
    """Schema para atualização de dados DP do Employee."""

    cargo: str | None = Field(None, max_length=100)
    departamento: str | None = Field(None, max_length=100)
    salario_base: float | None = None
    status: str | None = Field(None, max_length=50)
    data_demissao: date | None = None
    pis: str | None = Field(None, max_length=20)
    ctps: str | None = Field(None, max_length=20)
    ctps_serie: str | None = Field(None, max_length=10)
    banco: str | None = Field(None, max_length=50)
    agencia: str | None = Field(None, max_length=20)
    conta: str | None = Field(None, max_length=30)
    tipo_conta: str | None = Field(None, max_length=20)
