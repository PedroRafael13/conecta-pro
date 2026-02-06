"""
Schemas PCMSO (NR-7) - Exames Medicos e ASO
===========================================

Schemas Pydantic para endpoints PCMSO.
"""

from datetime import datetime, date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator

from modules.health_occupational.models.pcmso import ExamType, ExamStatus, FitnessResult


# ==============================================================================
# Medical Exam Schemas
# ==============================================================================

class MedicalExamRequest(BaseModel):
    """Request para agendamento de exame medico."""

    funcionario_id: UUID = Field(..., description="UUID do funcionario")
    tipo_exame: str = Field(
        ...,
        description="Tipo do exame",
        pattern=r"^(admissional|periodico|retorno_trabalho|mudanca_funcao|demissional)$",
    )
    data_agendamento: date = Field(..., description="Data do agendamento")
    hora_agendamento: Optional[str] = Field(
        None,
        pattern=r"^\d{2}:\d{2}$",
        description="Hora do agendamento (HH:MM)",
    )
    funcao: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Funcao do funcionario",
    )
    setor: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Setor de trabalho",
    )
    riscos: List[str] = Field(
        default_factory=list,
        description="Riscos ocupacionais da funcao",
    )
    exames_complementares: List[str] = Field(
        default_factory=list,
        description="Exames complementares (hemograma, audiometria, etc)",
    )
    local_realizacao: Optional[str] = Field(
        None,
        max_length=200,
        description="Local de realizacao do exame",
    )
    observacoes: Optional[str] = Field(None, description="Observacoes adicionais")

    @field_validator('data_agendamento')
    @classmethod
    def validar_data_agendamento(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Data de agendamento nao pode ser no passado")
        return v


class MedicalExamUpdateRequest(BaseModel):
    """Request para atualizacao de exame medico."""

    data_agendamento: Optional[date] = None
    hora_agendamento: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    local_realizacao: Optional[str] = None
    status: Optional[str] = Field(
        None,
        pattern=r"^(agendado|confirmado|realizado|cancelado|nao_compareceu)$",
    )
    data_realizacao: Optional[datetime] = None
    observacoes: Optional[str] = None


class MedicalExamResponse(BaseModel):
    """Response de exame medico."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    funcionario_id: UUID
    tipo_exame: str
    status: str
    funcao: str
    setor: str
    riscos: List[str]
    data_agendamento: date
    hora_agendamento: Optional[str] = None
    data_realizacao: Optional[datetime] = None
    local_realizacao: Optional[str] = None
    exames_complementares: List[str]
    observacoes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Campos calculados
    esta_pendente: Optional[bool] = None


class MedicalExamListResponse(BaseModel):
    """Response de lista de exames."""
    items: List[MedicalExamResponse]
    total: int
    page: int = 1
    size: int = 20


# ==============================================================================
# ASO Schemas
# ==============================================================================

class ASORequest(BaseModel):
    """Request para emissao de ASO."""

    exame_id: UUID = Field(..., description="ID do exame realizado")
    resultado: str = Field(
        ...,
        description="Resultado do exame",
        pattern=r"^(apto|inapto|apto_com_restricoes)$",
    )
    restricoes: Optional[List[str]] = Field(
        default=None,
        description="Restricoes (se apto com restricoes)",
    )
    validade_dias: int = Field(
        default=365,
        ge=30,
        le=730,
        description="Validade do ASO em dias",
    )
    medico_responsavel: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nome do medico responsavel",
    )
    crm: str = Field(
        ...,
        min_length=4,
        max_length=20,
        description="CRM do medico",
    )
    uf_crm: str = Field(
        default="AM",
        min_length=2,
        max_length=2,
        description="UF do CRM",
    )

    @field_validator('restricoes')
    @classmethod
    def validar_restricoes(cls, v, info):
        resultado = info.data.get('resultado')
        if resultado == 'apto_com_restricoes' and not v:
            raise ValueError("Restricoes sao obrigatorias para resultado 'apto_com_restricoes'")
        return v


class ASOUpdateRequest(BaseModel):
    """Request para atualizacao de ASO."""

    restricoes: Optional[List[str]] = None
    assinatura_funcionario: Optional[bool] = None
    cancelado: Optional[bool] = None
    motivo_cancelamento: Optional[str] = None


class ASOResponse(BaseModel):
    """Response de ASO."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    exame_id: UUID
    resultado: str
    restricoes: List[str]
    data_emissao: datetime
    validade_dias: int
    data_vencimento: date
    medico_responsavel: str
    crm: str
    uf_crm: Optional[str] = None
    numero_aso: Optional[str] = None
    documento_url: Optional[str] = None
    assinatura_medico: bool
    assinatura_funcionario: bool
    data_assinatura_funcionario: Optional[datetime] = None
    ativo: bool
    cancelado: bool
    motivo_cancelamento: Optional[str] = None
    created_at: datetime

    # Campos calculados
    esta_vencido: Optional[bool] = None
    dias_para_vencer: Optional[int] = None


class ASOListResponse(BaseModel):
    """Response de lista de ASOs."""
    items: List[ASOResponse]
    total: int
    page: int = 1
    size: int = 20


class ASOVencimentoResponse(BaseModel):
    """Response para ASOs a vencer."""
    funcionario_id: UUID
    funcionario_nome: Optional[str] = None
    aso_id: UUID
    data_vencimento: date
    dias_para_vencer: int
    tipo_exame: str


# ==============================================================================
# Complementary Exam Schemas
# ==============================================================================

class ComplementaryExamRequest(BaseModel):
    """Request para exame complementar."""

    exame_principal_id: UUID = Field(..., description="ID do exame principal")
    nome: str = Field(..., min_length=2, max_length=100, description="Nome do exame")
    codigo: Optional[str] = Field(None, max_length=20, description="Codigo TUSS")
    laboratorio: Optional[str] = Field(None, max_length=200)


class ComplementaryExamUpdateRequest(BaseModel):
    """Request para atualizacao de exame complementar."""

    data_realizacao: Optional[datetime] = None
    laboratorio: Optional[str] = None
    resultado: Optional[str] = None
    resultado_arquivo_url: Optional[str] = None
    valores_referencia: Optional[dict] = None
    normal: Optional[bool] = None
    status: Optional[str] = None


class ComplementaryExamResponse(BaseModel):
    """Response de exame complementar."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    exame_principal_id: UUID
    nome: str
    codigo: Optional[str] = None
    data_solicitacao: date
    data_realizacao: Optional[datetime] = None
    laboratorio: Optional[str] = None
    resultado: Optional[str] = None
    resultado_arquivo_url: Optional[str] = None
    valores_referencia: dict
    normal: Optional[bool] = None
    status: str
    created_at: datetime
