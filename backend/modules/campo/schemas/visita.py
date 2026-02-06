"""
Schemas de Visita - Modulo Campo
================================

Pydantic schemas para validacao e serializacao de Visitas.
"""

from datetime import date, time, datetime
from decimal import Decimal
from typing import Optional, List, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# ENUMS (importados do model)
# =============================================================================
from modules.campo.models.visita import (
    TipoVisita,
    StatusVisita,
    ResultadoVisita,
    TipoResponsavel,
    OrigemVisita,
)


# =============================================================================
# SCHEMAS AUXILIARES
# =============================================================================

class InteresseServico(BaseModel):
    """Schema para interesse em servico."""
    servico_id: Optional[UUID] = None
    nome: str
    interesse_nivel: int = Field(..., ge=1, le=5)


class NecessidadeItem(BaseModel):
    """Schema para necessidade identificada."""
    categoria: str
    descricao: str
    prioridade: int = Field(3, ge=1, le=5)
    estimativa_valor: Optional[Decimal] = None


class LevantamentoTecnico(BaseModel):
    """Schema para levantamento tecnico."""
    area_m2: Optional[float] = None
    pavimentos: Optional[int] = None
    cameras_existentes: Optional[int] = None
    pontos_acesso: Optional[int] = None
    necessidades: Optional[List[str]] = None
    infraestrutura_existente: Optional[str] = None
    observacoes_tecnicas: Optional[str] = None


class FotoVisita(BaseModel):
    """Schema para foto da visita."""
    url: str
    descricao: Optional[str] = None
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
    responsavel_nome: Optional[str] = Field(None, max_length=200)

    # Cliente existente (opcional)
    cliente_id: Optional[UUID] = None
    contrato_id: Optional[UUID] = None

    # Prospect (se nao for cliente)
    is_prospect: bool = False
    prospect_nome: Optional[str] = Field(None, max_length=200)
    prospect_empresa: Optional[str] = Field(None, max_length=200)
    prospect_cargo: Optional[str] = Field(None, max_length=100)
    prospect_telefone: Optional[str] = Field(None, max_length=20)
    prospect_celular: Optional[str] = Field(None, max_length=20)
    prospect_email: Optional[str] = Field(None, max_length=255)
    prospect_cnpj: Optional[str] = Field(None, max_length=20)
    prospect_cpf: Optional[str] = Field(None, max_length=15)

    # Lead/Oportunidade
    lead_id: Optional[UUID] = None
    oportunidade_id: Optional[UUID] = None

    # Localizacao
    endereco: str = Field(..., min_length=5, max_length=500)
    endereco_complemento: Optional[str] = Field(None, max_length=200)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    ponto_referencia: Optional[str] = Field(None, max_length=300)

    # Agendamento
    data_visita: date
    horario_inicio: time
    horario_fim: Optional[time] = None
    duracao_prevista_minutos: int = 60

    # Descricao
    objetivo: Optional[str] = None

    # Metadata
    tags: Optional[List[str]] = None


class VisitaUpdate(BaseModel):
    """Schema para atualizacao de Visita."""
    model_config = ConfigDict(from_attributes=True)

    tipo: Optional[TipoVisita] = None

    # Responsavel
    responsavel_id: Optional[UUID] = None
    responsavel_tipo: Optional[TipoResponsavel] = None

    # Prospect
    prospect_nome: Optional[str] = Field(None, max_length=200)
    prospect_empresa: Optional[str] = Field(None, max_length=200)
    prospect_telefone: Optional[str] = Field(None, max_length=20)
    prospect_celular: Optional[str] = Field(None, max_length=20)
    prospect_email: Optional[str] = Field(None, max_length=255)

    # Localizacao
    endereco: Optional[str] = Field(None, max_length=500)
    endereco_complemento: Optional[str] = Field(None, max_length=200)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    # Agendamento
    data_visita: Optional[date] = None
    horario_inicio: Optional[time] = None
    horario_fim: Optional[time] = None
    duracao_prevista_minutos: Optional[int] = None

    # Descricao
    objetivo: Optional[str] = None
    descricao_atendimento: Optional[str] = None
    observacoes: Optional[str] = None
    proximos_passos: Optional[str] = None

    # Levantamento
    levantamento: Optional[LevantamentoTecnico] = None
    necessidades_identificadas: Optional[List[NecessidadeItem]] = None

    # Metadata
    tags: Optional[List[str]] = None


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
    responsavel_nome: Optional[str] = None

    # Cliente
    cliente_id: Optional[UUID] = None
    contrato_id: Optional[UUID] = None

    # Prospect
    is_prospect: bool
    prospect_nome: Optional[str] = None
    prospect_empresa: Optional[str] = None
    prospect_telefone: Optional[str] = None
    prospect_email: Optional[str] = None

    # Lead/Oportunidade
    lead_id: Optional[UUID] = None
    oportunidade_id: Optional[UUID] = None

    # Localizacao
    endereco: str
    cidade: Optional[str] = None
    estado: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    # Agendamento
    data_visita: date
    horario_inicio: time
    horario_fim: Optional[time] = None
    duracao_prevista_minutos: Optional[int] = None

    # Confirmacao
    confirmada: bool = False
    confirmada_at: Optional[datetime] = None

    # Execucao
    checkin_at: Optional[datetime] = None
    checkout_at: Optional[datetime] = None
    duracao_real_minutos: Optional[int] = None

    # Resultado
    resultado: Optional[ResultadoVisita] = None
    objetivo: Optional[str] = None
    descricao_atendimento: Optional[str] = None
    proximos_passos: Optional[str] = None

    # Conversao
    interesse_nivel: Optional[int] = None
    proposta_gerada: bool = False
    proposta_id: Optional[UUID] = None
    proposta_valor: Optional[Decimal] = None
    contrato_fechado: bool = False

    # Levantamento
    levantamento: Optional[dict] = None
    necessidades_identificadas: Optional[List[Any]] = None

    # Fotos
    fotos: Optional[List[Any]] = None

    # Follow-up
    followup_agendado: bool = False
    followup_data: Optional[date] = None
    followup_tipo: Optional[str] = None

    # Reagendamento
    reagendamentos: int = 0

    # Metadata
    tags: Optional[List[str]] = None
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
    responsavel_nome: Optional[str] = None

    # Contato
    cliente_id: Optional[UUID] = None
    prospect_nome: Optional[str] = None
    prospect_empresa: Optional[str] = None

    # Local
    endereco: str
    cidade: Optional[str] = None

    # Agendamento
    data_visita: date
    horario_inicio: time
    confirmada: bool = False

    # Resultado
    resultado: Optional[ResultadoVisita] = None
    proposta_gerada: bool = False

    created_at: datetime


# =============================================================================
# ACTION SCHEMAS
# =============================================================================

class VisitaConfirmarRequest(BaseModel):
    """Schema para confirmar visita."""
    confirmado_por: Optional[str] = Field(None, max_length=100)


class VisitaCheckinRequest(BaseModel):
    """Schema para check-in."""
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class VisitaCheckoutRequest(BaseModel):
    """Schema para check-out."""
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class VisitaResultadoRequest(BaseModel):
    """Schema para registrar resultado."""
    resultado: ResultadoVisita
    descricao_atendimento: Optional[str] = None
    proximos_passos: Optional[str] = None


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
    servicos: Optional[List[InteresseServico]] = None


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
    estimativa_valor: Optional[Decimal] = None


class VisitaFollowupRequest(BaseModel):
    """Schema para agendar follow-up."""
    data: date
    tipo: str = Field(..., max_length=50)
    observacoes: Optional[str] = None


class VisitaFotoRequest(BaseModel):
    """Schema para adicionar foto."""
    url: str
    descricao: Optional[str] = None
    tipo: str = "geral"


# =============================================================================
# FILTER SCHEMAS
# =============================================================================

class VisitaFiltro(BaseModel):
    """Schema para filtros de busca de Visitas."""
    tipo: Optional[TipoVisita] = None
    status: Optional[StatusVisita] = None
    resultado: Optional[ResultadoVisita] = None
    origem: Optional[OrigemVisita] = None

    responsavel_id: Optional[UUID] = None
    responsavel_tipo: Optional[TipoResponsavel] = None
    cliente_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None

    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None

    cidade: Optional[str] = None
    estado: Optional[str] = None

    confirmada: Optional[bool] = None
    proposta_gerada: Optional[bool] = None
    contrato_fechado: Optional[bool] = None

    busca: Optional[str] = None  # Busca por numero, prospect, empresa


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class VisitaPaginatedResponse(BaseModel):
    """Response paginado de Visitas."""
    items: List[VisitaListItem]
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
    taxa_comparecimento: Optional[float] = None
    taxa_conversao_proposta: Optional[float] = None
    taxa_conversao_contrato: Optional[float] = None
    interesse_medio: Optional[float] = None
