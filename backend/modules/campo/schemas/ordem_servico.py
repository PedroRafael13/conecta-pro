"""
Schemas de Ordem de Servico - Modulo Campo
==========================================

Pydantic schemas para validacao e serializacao de OS.
"""

from datetime import date, time, datetime
from decimal import Decimal
from typing import Optional, List, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator


# =============================================================================
# ENUMS (importados do model)
# =============================================================================
from modules.campo.models.ordem_servico import (
    TipoOS,
    StatusOS,
    PrioridadeOS,
    OrigemOS,
)


# =============================================================================
# SCHEMAS BASE
# =============================================================================

class MaterialItem(BaseModel):
    """Schema para item de material."""
    id: Optional[UUID] = None
    nome: str
    codigo: Optional[str] = None
    quantidade: int = 1
    valor_unitario: Optional[Decimal] = None
    baixa_estoque: bool = False


class FotoItem(BaseModel):
    """Schema para foto."""
    url: str
    descricao: Optional[str] = None
    timestamp: Optional[datetime] = None


class DocumentoItem(BaseModel):
    """Schema para documento."""
    url: str
    nome: str
    tipo: Optional[str] = None
    timestamp: Optional[datetime] = None


# =============================================================================
# CREATE SCHEMAS
# =============================================================================

class OrdemServicoCreate(BaseModel):
    """Schema para criacao de OS."""
    model_config = ConfigDict(from_attributes=True)

    # Classificacao
    tipo: TipoOS = TipoOS.MANUTENCAO_CORRETIVA
    prioridade: PrioridadeOS = PrioridadeOS.NORMAL
    origem: OrigemOS = OrigemOS.CLIENTE

    # Cliente
    cliente_id: UUID
    contrato_id: Optional[UUID] = None
    contato_nome: Optional[str] = Field(None, max_length=200)
    contato_telefone: Optional[str] = Field(None, max_length=20)
    contato_email: Optional[str] = Field(None, max_length=255)

    # Localizacao
    endereco_servico: str = Field(..., min_length=5, max_length=500)
    endereco_complemento: Optional[str] = Field(None, max_length=200)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    ponto_referencia: Optional[str] = Field(None, max_length=300)

    # Agendamento
    data_agendada: Optional[date] = None
    horario_inicio_previsto: Optional[time] = None
    horario_fim_previsto: Optional[time] = None
    duracao_estimada_minutos: int = 60
    janela_atendimento: Optional[str] = Field(None, max_length=50)

    # Tecnico
    tecnico_id: Optional[UUID] = None
    tecnico_auxiliar_id: Optional[UUID] = None

    # Descricao
    titulo: Optional[str] = Field(None, max_length=300)
    descricao: Optional[str] = None
    problema_relatado: Optional[str] = None
    instrucoes_cliente: Optional[str] = None

    # Equipamento
    equipamento_id: Optional[UUID] = None
    equipamento_tipo: Optional[str] = Field(None, max_length=100)
    equipamento_modelo: Optional[str] = Field(None, max_length=100)
    equipamento_serie: Optional[str] = Field(None, max_length=100)

    # Checklist
    checklist_template_id: Optional[UUID] = None

    # Materiais previstos
    materiais_previstos: Optional[List[MaterialItem]] = None

    # Financeiro
    valor_mao_obra: Optional[Decimal] = None
    valor_deslocamento: Optional[Decimal] = None
    is_cobrado: bool = True
    is_garantia: bool = False
    is_cortesia: bool = False
    motivo_isencao: Optional[str] = Field(None, max_length=300)

    # SLA
    sla_horas: Optional[int] = None

    # Integracao
    ticket_origem_id: Optional[str] = Field(None, max_length=100)
    ticket_sistema: Optional[str] = Field(None, max_length=50)

    # Metadata
    tags: Optional[List[str]] = None


class OrdemServicoUpdate(BaseModel):
    """Schema para atualizacao de OS."""
    model_config = ConfigDict(from_attributes=True)

    tipo: Optional[TipoOS] = None
    prioridade: Optional[PrioridadeOS] = None

    # Contato
    contato_nome: Optional[str] = Field(None, max_length=200)
    contato_telefone: Optional[str] = Field(None, max_length=20)
    contato_email: Optional[str] = Field(None, max_length=255)

    # Localizacao
    endereco_servico: Optional[str] = Field(None, max_length=500)
    endereco_complemento: Optional[str] = Field(None, max_length=200)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    ponto_referencia: Optional[str] = Field(None, max_length=300)

    # Agendamento
    data_agendada: Optional[date] = None
    horario_inicio_previsto: Optional[time] = None
    horario_fim_previsto: Optional[time] = None
    duracao_estimada_minutos: Optional[int] = None
    janela_atendimento: Optional[str] = Field(None, max_length=50)

    # Tecnico
    tecnico_id: Optional[UUID] = None
    tecnico_auxiliar_id: Optional[UUID] = None

    # Descricao
    titulo: Optional[str] = Field(None, max_length=300)
    descricao: Optional[str] = None
    problema_relatado: Optional[str] = None
    solucao_aplicada: Optional[str] = None
    observacoes_internas: Optional[str] = None
    instrucoes_cliente: Optional[str] = None

    # Equipamento
    equipamento_id: Optional[UUID] = None

    # Checklist
    checklist_template_id: Optional[UUID] = None
    checklist_respostas: Optional[dict] = None

    # Materiais
    materiais_previstos: Optional[List[MaterialItem]] = None
    materiais_utilizados: Optional[List[MaterialItem]] = None

    # Financeiro
    valor_mao_obra: Optional[Decimal] = None
    valor_materiais: Optional[Decimal] = None
    valor_deslocamento: Optional[Decimal] = None
    valor_adicional: Optional[Decimal] = None
    descricao_adicional: Optional[str] = Field(None, max_length=300)
    valor_desconto: Optional[Decimal] = None
    motivo_desconto: Optional[str] = Field(None, max_length=300)

    # SLA
    sla_horas: Optional[int] = None

    # Metadata
    tags: Optional[List[str]] = None


# =============================================================================
# READ SCHEMAS
# =============================================================================

class OrdemServicoRead(BaseModel):
    """Schema completo de leitura de OS."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    numero: str
    tipo: TipoOS
    status: StatusOS
    prioridade: PrioridadeOS
    origem: OrigemOS

    # Cliente
    cliente_id: UUID
    contrato_id: Optional[UUID] = None
    contato_nome: Optional[str] = None
    contato_telefone: Optional[str] = None
    contato_email: Optional[str] = None

    # Localizacao
    endereco_servico: str
    endereco_complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    # Agendamento
    data_abertura: datetime
    data_agendada: Optional[date] = None
    horario_inicio_previsto: Optional[time] = None
    horario_fim_previsto: Optional[time] = None
    duracao_estimada_minutos: Optional[int] = None

    # Execucao
    tecnico_id: Optional[UUID] = None
    tecnico_auxiliar_id: Optional[UUID] = None
    checkin_at: Optional[datetime] = None
    checkout_at: Optional[datetime] = None
    data_conclusao: Optional[datetime] = None
    tempo_execucao_minutos: Optional[int] = None

    # Descricao
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    problema_relatado: Optional[str] = None
    solucao_aplicada: Optional[str] = None

    # Equipamento
    equipamento_id: Optional[UUID] = None
    equipamento_tipo: Optional[str] = None

    # Checklist
    checklist_template_id: Optional[UUID] = None
    checklist_concluido: bool = False

    # Materiais
    materiais_previstos: Optional[List[Any]] = None
    materiais_utilizados: Optional[List[Any]] = None

    # Financeiro
    valor_mao_obra: Optional[Decimal] = None
    valor_materiais: Optional[Decimal] = None
    valor_deslocamento: Optional[Decimal] = None
    valor_total: Optional[Decimal] = None
    is_cobrado: bool = True
    faturado: bool = False

    # Avaliacao
    avaliacao_nota: Optional[int] = None
    avaliacao_comentario: Optional[str] = None

    # Assinatura
    assinatura_cliente_url: Optional[str] = None
    assinatura_cliente_nome: Optional[str] = None

    # Fotos
    fotos_antes: Optional[List[Any]] = None
    fotos_depois: Optional[List[Any]] = None

    # SLA
    sla_horas: Optional[int] = None
    sla_vencimento: Optional[datetime] = None
    sla_cumprido: Optional[bool] = None

    # Reagendamento
    reagendamentos: int = 0

    # Metadata
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool


class OrdemServicoListItem(BaseModel):
    """Schema resumido para listagem de OS."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    numero: str
    tipo: TipoOS
    status: StatusOS
    prioridade: PrioridadeOS

    cliente_id: UUID
    endereco_servico: str
    cidade: Optional[str] = None

    data_agendada: Optional[date] = None
    horario_inicio_previsto: Optional[time] = None

    tecnico_id: Optional[UUID] = None

    titulo: Optional[str] = None

    valor_total: Optional[Decimal] = None
    avaliacao_nota: Optional[int] = None

    sla_vencimento: Optional[datetime] = None

    created_at: datetime


# =============================================================================
# ACTION SCHEMAS
# =============================================================================

class OSAgendarRequest(BaseModel):
    """Schema para agendar OS."""
    data_agendada: date
    horario_inicio_previsto: time
    horario_fim_previsto: Optional[time] = None
    tecnico_id: Optional[UUID] = None


class OSCheckinRequest(BaseModel):
    """Schema para check-in."""
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class OSCheckoutRequest(BaseModel):
    """Schema para check-out."""
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class OSConcluirRequest(BaseModel):
    """Schema para concluir OS."""
    solucao_aplicada: Optional[str] = None
    observacoes: Optional[str] = None


class OSCancelarRequest(BaseModel):
    """Schema para cancelar OS."""
    motivo: str = Field(..., min_length=5, max_length=500)


class OSReagendarRequest(BaseModel):
    """Schema para reagendar OS."""
    nova_data: date
    motivo: str = Field(..., min_length=5, max_length=300)


class OSAvaliacaoRequest(BaseModel):
    """Schema para registrar avaliacao."""
    nota: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = None


class OSAssinaturaRequest(BaseModel):
    """Schema para registrar assinatura."""
    url: str
    nome: str
    documento: Optional[str] = None


class OSFotoRequest(BaseModel):
    """Schema para adicionar foto."""
    tipo: str = Field(..., pattern="^(antes|durante|depois)$")
    url: str
    descricao: Optional[str] = None


# =============================================================================
# FILTER/SEARCH SCHEMAS
# =============================================================================

class OSFiltro(BaseModel):
    """Schema para filtros de busca de OS."""
    tipo: Optional[TipoOS] = None
    status: Optional[StatusOS] = None
    prioridade: Optional[PrioridadeOS] = None
    origem: Optional[OrigemOS] = None

    cliente_id: Optional[UUID] = None
    contrato_id: Optional[UUID] = None
    tecnico_id: Optional[UUID] = None

    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None

    cidade: Optional[str] = None
    estado: Optional[str] = None

    sla_vencido: Optional[bool] = None
    avaliado: Optional[bool] = None
    faturado: Optional[bool] = None

    busca: Optional[str] = None  # Busca por numero, titulo, descricao


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class OSPaginatedResponse(BaseModel):
    """Response paginado de OS."""
    items: List[OrdemServicoListItem]
    total: int
    page: int
    page_size: int
    pages: int


class OSDashboardStats(BaseModel):
    """Estatisticas para dashboard de OS."""
    total_abertas: int = 0
    total_agendadas: int = 0
    total_em_andamento: int = 0
    total_concluidas_hoje: int = 0
    total_concluidas_mes: int = 0
    total_atrasadas: int = 0
    tempo_medio_atendimento_minutos: Optional[float] = None
    avaliacao_media: Optional[float] = None
    taxa_primeira_resolucao: Optional[float] = None
