"""
Schemas PCMSO (NR-7) - Exames Medicos e ASO
===========================================

Schemas Pydantic para endpoints PCMSO.
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

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
    hora_agendamento: str | None = Field(
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
    riscos: list[str] = Field(
        default_factory=list,
        description="Riscos ocupacionais da funcao",
    )
    exames_complementares: list[str] = Field(
        default_factory=list,
        description="Exames complementares (hemograma, audiometria, etc)",
    )
    local_realizacao: str | None = Field(
        None,
        max_length=200,
        description="Local de realizacao do exame",
    )
    observacoes: str | None = Field(None, description="Observacoes adicionais")

    @field_validator("data_agendamento")
    @classmethod
    def validar_data_agendamento(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Data de agendamento nao pode ser no passado")
        return v


class MedicalExamUpdateRequest(BaseModel):
    """Request para atualizacao de exame medico."""

    data_agendamento: date | None = None
    hora_agendamento: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    local_realizacao: str | None = None
    status: str | None = Field(
        None,
        pattern=r"^(agendado|confirmado|realizado|cancelado|nao_compareceu)$",
    )
    data_realizacao: datetime | None = None
    observacoes: str | None = None


class MedicalExamResponse(BaseModel):
    """Response de exame medico."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    funcionario_id: UUID
    tipo_exame: str
    status: str
    funcao: str
    setor: str
    riscos: list[str]
    data_agendamento: date
    hora_agendamento: str | None = None
    data_realizacao: datetime | None = None
    local_realizacao: str | None = None
    exames_complementares: list[str]
    observacoes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    # Campos calculados
    esta_pendente: bool | None = None


class MedicalExamListResponse(BaseModel):
    """Response de lista de exames."""

    items: list[MedicalExamResponse]
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
    restricoes: list[str] | None = Field(
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

    @field_validator("restricoes")
    @classmethod
    def validar_restricoes(cls, v, info):
        resultado = info.data.get("resultado")
        if resultado == "apto_com_restricoes" and not v:
            raise ValueError("Restricoes sao obrigatorias para resultado 'apto_com_restricoes'")
        return v


class ASOUpdateRequest(BaseModel):
    """Request para atualizacao de ASO."""

    restricoes: list[str] | None = None
    assinatura_funcionario: bool | None = None
    cancelado: bool | None = None
    motivo_cancelamento: str | None = None


class ASOResponse(BaseModel):
    """Response de ASO."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    exame_id: UUID
    resultado: str
    restricoes: list[str]
    data_emissao: datetime
    validade_dias: int
    data_vencimento: date
    medico_responsavel: str
    crm: str
    uf_crm: str | None = None
    numero_aso: str | None = None
    documento_url: str | None = None
    assinatura_medico: bool
    assinatura_funcionario: bool
    data_assinatura_funcionario: datetime | None = None
    ativo: bool
    cancelado: bool
    motivo_cancelamento: str | None = None
    created_at: datetime

    # Campos calculados
    esta_vencido: bool | None = None
    dias_para_vencer: int | None = None


class ASOListResponse(BaseModel):
    """Response de lista de ASOs."""

    items: list[ASOResponse]
    total: int
    page: int = 1
    size: int = 20


class ASOVencimentoResponse(BaseModel):
    """Response para ASOs a vencer."""

    funcionario_id: UUID
    funcionario_nome: str | None = None
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
    codigo: str | None = Field(None, max_length=20, description="Codigo TUSS")
    laboratorio: str | None = Field(None, max_length=200)


class ComplementaryExamUpdateRequest(BaseModel):
    """Request para atualizacao de exame complementar."""

    data_realizacao: datetime | None = None
    laboratorio: str | None = None
    resultado: str | None = None
    resultado_arquivo_url: str | None = None
    valores_referencia: dict | None = None
    normal: bool | None = None
    status: str | None = None


class ComplementaryExamResponse(BaseModel):
    """Response de exame complementar."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    exame_principal_id: UUID
    nome: str
    codigo: str | None = None
    data_solicitacao: date
    data_realizacao: datetime | None = None
    laboratorio: str | None = None
    resultado: str | None = None
    resultado_arquivo_url: str | None = None
    valores_referencia: dict
    normal: bool | None = None
    status: str
    created_at: datetime
