"""
Schemas de Visita - Modulo Campo
================================

Pydantic schemas para validacao e serializacao de Visitas.
"""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# ENUMS (importados do model)
# =============================================================================
from modules.campo.models.visita import (
    OrigemVisita,
    ResultadoVisita,
    StatusVisita,
    TipoResponsavel,
    TipoVisita,
)

# =============================================================================
# SCHEMAS AUXILIARES
# =============================================================================


class InteresseServico(BaseModel):
    """Schema para interesse em servico."""

    servico_id: UUID | None = None
    nome: str
    interesse_nivel: int = Field(..., ge=1, le=5)


class NecessidadeItem(BaseModel):
    """Schema para necessidade identificada."""

    categoria: str
    descricao: str
    prioridade: int = Field(3, ge=1, le=5)
    estimativa_valor: Decimal | None = None


class LevantamentoTecnico(BaseModel):
    """Schema para levantamento tecnico."""

    area_m2: float | None = None
    pavimentos: int | None = None
    cameras_existentes: int | None = None
    pontos_acesso: int | None = None
    necessidades: list[str] | None = None
    infraestrutura_existente: str | None = None
    observacoes_tecnicas: str | None = None


class FotoVisita(BaseModel):
    """Schema para foto da visita."""

    url: str
    descricao: str | None = None
    tipo: str = "geral"


# =============================================================================
# CREATE SCHEMAS
# =============================================================================


class VisitaCreate(BaseModel):
    """Schema para criacao de Visita."""

    model_config = ConfigDict(from_attributes=True)

    # Classificacao
    tipo: TipoVisita = TipoVisita.COMERCIAL
    origem: OrigemVisita = OrigemVisita.LEAD

    # Responsavel
    responsavel_id: UUID
    responsavel_tipo: TipoResponsavel = TipoResponsavel.VENDEDOR
    responsavel_nome: str | None = Field(None, max_length=200)

    # Cliente existente (opcional)
    cliente_id: UUID | None = None
    contrato_id: UUID | None = None

    # Prospect (se nao for cliente)
    is_prospect: bool = False
    prospect_nome: str | None = Field(None, max_length=200)
    prospect_empresa: str | None = Field(None, max_length=200)
    prospect_cargo: str | None = Field(None, max_length=100)
    prospect_telefone: str | None = Field(None, max_length=20)
    prospect_celular: str | None = Field(None, max_length=20)
    prospect_email: str | None = Field(None, max_length=255)
    prospect_cnpj: str | None = Field(None, max_length=20)
    prospect_cpf: str | None = Field(None, max_length=15)

    # Lead/Oportunidade
    lead_id: UUID | None = None
    oportunidade_id: UUID | None = None

    # Localizacao
    endereco: str = Field(..., min_length=5, max_length=500)
    endereco_complemento: str | None = Field(None, max_length=200)
    bairro: str | None = Field(None, max_length=100)
    cidade: str | None = Field(None, max_length=100)
    estado: str | None = Field(None, max_length=2)
    cep: str | None = Field(None, max_length=10)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    ponto_referencia: str | None = Field(None, max_length=300)

    # Agendamento
    data_visita: date
    horario_inicio: time
    horario_fim: time | None = None
    duracao_prevista_minutos: int = 60

    # Descricao
    objetivo: str | None = None

    # Metadata
    tags: list[str] | None = None


class VisitaUpdate(BaseModel):
    """Schema para atualizacao de Visita."""

    model_config = ConfigDict(from_attributes=True)

    tipo: TipoVisita | None = None

    # Responsavel
    responsavel_id: UUID | None = None
    responsavel_tipo: TipoResponsavel | None = None

    # Prospect
    prospect_nome: str | None = Field(None, max_length=200)
    prospect_empresa: str | None = Field(None, max_length=200)
    prospect_telefone: str | None = Field(None, max_length=20)
    prospect_celular: str | None = Field(None, max_length=20)
    prospect_email: str | None = Field(None, max_length=255)

    # Localizacao
    endereco: str | None = Field(None, max_length=500)
    endereco_complemento: str | None = Field(None, max_length=200)
    bairro: str | None = Field(None, max_length=100)
    cidade: str | None = Field(None, max_length=100)
    estado: str | None = Field(None, max_length=2)
    cep: str | None = Field(None, max_length=10)
    latitude: Decimal | None = None
    longitude: Decimal | None = None

    # Agendamento
    data_visita: date | None = None
    horario_inicio: time | None = None
    horario_fim: time | None = None
    duracao_prevista_minutos: int | None = None

    # Descricao
    objetivo: str | None = None
    descricao_atendimento: str | None = None
    observacoes: str | None = None
    proximos_passos: str | None = None

    # Levantamento
    levantamento: LevantamentoTecnico | None = None
    necessidades_identificadas: list[NecessidadeItem] | None = None

    # Metadata
    tags: list[str] | None = None


# =============================================================================
# READ SCHEMAS
# =============================================================================


class VisitaRead(BaseModel):
    """Schema completo de leitura de Visita."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    numero: str
    tipo: TipoVisita
    status: StatusVisita
    origem: OrigemVisita

    # Responsavel
    responsavel_id: UUID
    responsavel_tipo: TipoResponsavel
    responsavel_nome: str | None = None

    # Cliente
    cliente_id: UUID | None = None
    contrato_id: UUID | None = None

    # Prospect
    is_prospect: bool
    prospect_nome: str | None = None
    prospect_empresa: str | None = None
    prospect_telefone: str | None = None
    prospect_email: str | None = None

    # Lead/Oportunidade
    lead_id: UUID | None = None
    oportunidade_id: UUID | None = None

    # Localizacao
    endereco: str
    cidade: str | None = None
    estado: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None

    # Agendamento
    data_visita: date
    horario_inicio: time
    horario_fim: time | None = None
    duracao_prevista_minutos: int | None = None

    # Confirmacao
    confirmada: bool = False
    confirmada_at: datetime | None = None

    # Execucao
    checkin_at: datetime | None = None
    checkout_at: datetime | None = None
    duracao_real_minutos: int | None = None

    # Resultado
    resultado: ResultadoVisita | None = None
    objetivo: str | None = None
    descricao_atendimento: str | None = None
    proximos_passos: str | None = None

    # Conversao
    interesse_nivel: int | None = None
    proposta_gerada: bool = False
    proposta_id: UUID | None = None
    proposta_valor: Decimal | None = None
    contrato_fechado: bool = False

    # Levantamento
    levantamento: dict | None = None
    necessidades_identificadas: list[Any] | None = None

    # Fotos
    fotos: list[Any] | None = None

    # Follow-up
    followup_agendado: bool = False
    followup_data: date | None = None
    followup_tipo: str | None = None

    # Reagendamento
    reagendamentos: int = 0

    # Metadata
    tags: list[str] | None = None
    created_at: datetime
    updated_at: datetime
    is_active: bool


class VisitaListItem(BaseModel):
    """Schema resumido para listagem de Visitas."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    numero: str
    tipo: TipoVisita
    status: StatusVisita

    responsavel_id: UUID
    responsavel_nome: str | None = None

    # Contato
    cliente_id: UUID | None = None
    prospect_nome: str | None = None
    prospect_empresa: str | None = None

    # Local
    endereco: str
    cidade: str | None = None

    # Agendamento
    data_visita: date
    horario_inicio: time
    confirmada: bool = False

    # Resultado
    resultado: ResultadoVisita | None = None
    proposta_gerada: bool = False

    created_at: datetime


# =============================================================================
# ACTION SCHEMAS
# =============================================================================


class VisitaConfirmarRequest(BaseModel):
    """Schema para confirmar visita."""

    confirmado_por: str | None = Field(None, max_length=100)


class VisitaCheckinRequest(BaseModel):
    """Schema para check-in."""

    latitude: Decimal | None = None
    longitude: Decimal | None = None


class VisitaCheckoutRequest(BaseModel):
    """Schema para check-out."""

    latitude: Decimal | None = None
    longitude: Decimal | None = None


class VisitaResultadoRequest(BaseModel):
    """Schema para registrar resultado."""

    resultado: ResultadoVisita
    descricao_atendimento: str | None = None
    proximos_passos: str | None = None


class VisitaCancelarRequest(BaseModel):
    """Schema para cancelar visita."""

    motivo: str = Field(..., min_length=5, max_length=300)


class VisitaReagendarRequest(BaseModel):
    """Schema para reagendar visita."""

    nova_data: date
    novo_horario: time
    motivo: str = Field(..., min_length=5, max_length=300)


class VisitaInteresseRequest(BaseModel):
    """Schema para registrar interesse."""

    nivel: int = Field(..., ge=1, le=5)
    servicos: list[InteresseServico] | None = None


class VisitaPropostaRequest(BaseModel):
    """Schema para vincular proposta."""

    proposta_id: UUID
    valor: Decimal


class VisitaLevantamentoRequest(BaseModel):
    """Schema para registrar levantamento tecnico."""

    dados: LevantamentoTecnico


class VisitaNecessidadeRequest(BaseModel):
    """Schema para adicionar necessidade."""

    categoria: str
    descricao: str
    prioridade: int = Field(3, ge=1, le=5)
    estimativa_valor: Decimal | None = None


class VisitaFollowupRequest(BaseModel):
    """Schema para agendar follow-up."""

    data: date
    tipo: str = Field(..., max_length=50)
    observacoes: str | None = None


class VisitaFotoRequest(BaseModel):
    """Schema para adicionar foto."""

    url: str
    descricao: str | None = None
    tipo: str = "geral"


# =============================================================================
# FILTER SCHEMAS
# =============================================================================


class VisitaFiltro(BaseModel):
    """Schema para filtros de busca de Visitas."""

    tipo: TipoVisita | None = None
    status: StatusVisita | None = None
    resultado: ResultadoVisita | None = None
    origem: OrigemVisita | None = None

    responsavel_id: UUID | None = None
    responsavel_tipo: TipoResponsavel | None = None
    cliente_id: UUID | None = None
    lead_id: UUID | None = None

    data_inicio: date | None = None
    data_fim: date | None = None

    cidade: str | None = None
    estado: str | None = None

    confirmada: bool | None = None
    proposta_gerada: bool | None = None
    contrato_fechado: bool | None = None

    busca: str | None = None  # Busca por numero, prospect, empresa


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class VisitaPaginatedResponse(BaseModel):
    """Response paginado de Visitas."""

    items: list[VisitaListItem]
    total: int
    page: int
    page_size: int
    pages: int


class VisitaDashboardStats(BaseModel):
    """Estatisticas para dashboard de Visitas."""

    total_agendadas: int = 0
    total_confirmadas: int = 0
    total_realizadas_hoje: int = 0
    total_realizadas_mes: int = 0
    total_canceladas_mes: int = 0
    taxa_comparecimento: float | None = None
    taxa_conversao_proposta: float | None = None
    taxa_conversao_contrato: float | None = None
    interesse_medio: float | None = None
