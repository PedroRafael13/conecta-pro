"""
Pydantic schemas para o módulo CCT (people_management).
"""

import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

# =========================================================================
# CONVENÇÃO
# =========================================================================


class CCTConvencaoCreate(BaseModel):
    sindicato_trabalhadores: str = Field(..., max_length=200)
    sindicato_trabalhadores_cnpj: str | None = Field(None, max_length=20)
    sindicato_patronal: str = Field(..., max_length=200)
    sindicato_patronal_cnpj: str | None = Field(None, max_length=20)
    registro_mte: str | None = Field(None, max_length=50)
    data_inicio: date
    data_fim: date
    data_base: str | None = Field(None, max_length=5)
    municipio: str | None = Field(None, max_length=100)
    uf: str | None = Field(None, max_length=2)
    descricao: str | None = None
    is_vigente: bool = False


class CCTConvencaoUpdate(BaseModel):
    sindicato_trabalhadores: str | None = Field(None, max_length=200)
    sindicato_trabalhadores_cnpj: str | None = None
    sindicato_patronal: str | None = Field(None, max_length=200)
    sindicato_patronal_cnpj: str | None = None
    registro_mte: str | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    data_base: str | None = None
    municipio: str | None = None
    uf: str | None = None
    descricao: str | None = None
    is_vigente: bool | None = None
    is_active: bool | None = None


class CCTConvencaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sindicato_trabalhadores: str
    sindicato_trabalhadores_cnpj: str | None
    sindicato_patronal: str
    sindicato_patronal_cnpj: str | None
    registro_mte: str | None
    data_inicio: date
    data_fim: date
    data_base: str | None
    municipio: str | None
    uf: str | None
    descricao: str | None
    is_vigente: bool
    is_active: bool


# =========================================================================
# CARGO
# =========================================================================


class CCTCargoCreate(BaseModel):
    cargo_nome: str = Field(..., max_length=200)
    piso_salarial: Decimal = Field(..., gt=0)
    adicional_tipo: str | None = None
    adicional_noturno_percentual: Decimal = Field(default=Decimal("20.0"))
    adicional_periculosidade_percentual: Decimal = Field(default=Decimal("30.0"))
    adicional_insalubridade_percentual: Decimal = Field(default=Decimal("10.0"))
    horas_extras_percentual: Decimal = Field(default=Decimal("50.0"))
    horas_extras_noturnas_percentual: Decimal = Field(default=Decimal("100.0"))
    jornada_semanal_horas: int = Field(default=44, ge=1, le=60)


class CCTCargoUpdate(BaseModel):
    cargo_nome: str | None = Field(None, max_length=200)
    piso_salarial: Decimal | None = Field(None, gt=0)
    adicional_tipo: str | None = None
    adicional_noturno_percentual: Decimal | None = None
    adicional_periculosidade_percentual: Decimal | None = None
    adicional_insalubridade_percentual: Decimal | None = None
    horas_extras_percentual: Decimal | None = None
    horas_extras_noturnas_percentual: Decimal | None = None
    jornada_semanal_horas: int | None = None
    is_active: bool | None = None


class CCTCargoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    convencao_id: uuid.UUID
    cargo_nome: str
    piso_salarial: Decimal
    adicional_tipo: str | None
    adicional_noturno_percentual: Decimal
    adicional_periculosidade_percentual: Decimal
    adicional_insalubridade_percentual: Decimal
    horas_extras_percentual: Decimal
    horas_extras_noturnas_percentual: Decimal
    jornada_semanal_horas: int
    is_active: bool


# =========================================================================
# FERIADO
# =========================================================================


class CCTFeriadoCreate(BaseModel):
    data_feriado: date
    nome: str = Field(..., max_length=200)
    tipo: str = Field(..., pattern="^(nacional|estadual|municipal)$")


class CCTFeriadoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    convencao_id: uuid.UUID
    data_feriado: date
    nome: str
    tipo: str
    ano: int
    is_active: bool


# =========================================================================
# BENEFÍCIO
# =========================================================================


class CCTBeneficioCreate(BaseModel):
    tipo_beneficio: str = Field(..., max_length=50)
    valor_minimo: Decimal | None = None
    valor_empresa: Decimal | None = None
    desconto_maximo_percentual: Decimal | None = None
    desconto_percentual_sobre_salario: Decimal | None = None
    obrigatorio: bool = True
    observacao: str | None = None


class CCTBeneficioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    convencao_id: uuid.UUID
    tipo_beneficio: str
    valor_minimo: Decimal | None
    valor_empresa: Decimal | None
    desconto_maximo_percentual: Decimal | None
    desconto_percentual_sobre_salario: Decimal | None
    obrigatorio: bool
    observacao: str | None
    is_active: bool
