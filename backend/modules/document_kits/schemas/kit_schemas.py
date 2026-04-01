"""Schemas Pydantic para Kits Documentais."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.document_kits.models.document_kit import (
    AssignmentStatus,
    EntityType,
    ItemPriority,
    ItemStatusEnum,
    ItemType,
    KitStatus,
    KitType,
)

# === Document Kit Schemas ===


class DocumentKitBase(BaseModel):
    """Schema base para DocumentKit."""

    codigo: str = Field(..., min_length=1, max_length=50)
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: str | None = Field(None, max_length=2000)
    tipo: KitType = Field(default=KitType.OUTRO)
    is_template: bool = Field(default=False)
    is_obrigatorio: bool = Field(default=True)
    prazo_dias: int | None = Field(default=30, ge=1, le=365)
    permite_parcial: bool = Field(default=False)
    requer_aprovacao: bool = Field(default=True)
    entity_types: list[str] = Field(default_factory=list)
    departamentos: list[str] = Field(default_factory=list)
    cargos: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class DocumentKitCreate(DocumentKitBase):
    """Schema para criacao de DocumentKit."""

    condominio_id: UUID


class DocumentKitUpdate(BaseModel):
    """Schema para atualizacao de DocumentKit."""

    nome: str | None = Field(None, min_length=1, max_length=200)
    descricao: str | None = Field(None, max_length=2000)
    tipo: KitType | None = None
    status: KitStatus | None = None
    is_obrigatorio: bool | None = None
    prazo_dias: int | None = Field(None, ge=1, le=365)
    permite_parcial: bool | None = None
    requer_aprovacao: bool | None = None
    entity_types: list[str] | None = None
    departamentos: list[str] | None = None
    cargos: list[str] | None = None
    tags: list[str] | None = None


class DocumentKitResponse(DocumentKitBase):
    """Schema de resposta para DocumentKit."""

    id: UUID
    condominio_id: UUID
    status: KitStatus
    total_itens: int
    itens_obrigatorios: int
    uso_count: int
    versao: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DocumentKitListResponse(BaseModel):
    """Schema de lista de DocumentKits."""

    items: list[DocumentKitResponse]
    total: int
    page: int
    page_size: int
    pages: int


# === Document Kit Item Schemas ===


class DocumentKitItemBase(BaseModel):
    """Schema base para DocumentKitItem."""

    codigo: str = Field(..., min_length=1, max_length=50)
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: str | None = Field(None, max_length=2000)
    instrucoes: str | None = Field(None, max_length=5000)
    tipo: ItemType = Field(default=ItemType.DOCUMENTO_PESSOAL)
    prioridade: ItemPriority = Field(default=ItemPriority.OBRIGATORIO)
    ordem: int = Field(default=0, ge=0)
    formatos_aceitos: list[str] = Field(default_factory=list)
    tamanho_max_mb: int = Field(default=10, ge=1, le=100)
    requer_validade: bool = Field(default=False)
    validade_minima_dias: int | None = Field(None, ge=1, le=3650)
    requer_autenticacao: bool = Field(default=False)
    template_url: str | None = Field(None, max_length=500)
    exemplo_url: str | None = Field(None, max_length=500)
    tags: list[str] = Field(default_factory=list)

    @field_validator("formatos_aceitos")
    @classmethod
    def validate_formatos(cls, value: list[str]) -> list[str]:
        """Valida formatos aceitos."""
        formatos_validos = ["pdf", "jpg", "jpeg", "png", "gif", "doc", "docx", "xls", "xlsx", "txt", "zip", "rar"]
        for formato in value:
            if formato.lower() not in formatos_validos:
                raise ValueError(f"Formato invalido: {formato}")
        return [f.lower() for f in value]


class DocumentKitItemCreate(DocumentKitItemBase):
    """Schema para criacao de DocumentKitItem."""

    kit_id: UUID
    condominio_id: UUID
    depende_de: UUID | None = None


class DocumentKitItemUpdate(BaseModel):
    """Schema para atualizacao de DocumentKitItem."""

    nome: str | None = Field(None, min_length=1, max_length=200)
    descricao: str | None = Field(None, max_length=2000)
    instrucoes: str | None = Field(None, max_length=5000)
    tipo: ItemType | None = None
    prioridade: ItemPriority | None = None
    ordem: int | None = Field(None, ge=0)
    is_ativo: bool | None = None
    formatos_aceitos: list[str] | None = None
    tamanho_max_mb: int | None = Field(None, ge=1, le=100)
    requer_validade: bool | None = None
    validade_minima_dias: int | None = Field(None, ge=1, le=3650)
    requer_autenticacao: bool | None = None
    template_url: str | None = Field(None, max_length=500)
    exemplo_url: str | None = Field(None, max_length=500)
    depende_de: UUID | None = None
    tags: list[str] | None = None


class DocumentKitItemResponse(DocumentKitItemBase):
    """Schema de resposta para DocumentKitItem."""

    id: UUID
    kit_id: UUID
    condominio_id: UUID
    is_ativo: bool
    depende_de: UUID | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# === Document Kit Assignment Schemas ===


class DocumentKitAssignmentBase(BaseModel):
    """Schema base para DocumentKitAssignment."""

    entity_type: EntityType
    entity_id: UUID
    entity_nome: str | None = Field(None, max_length=200)
    data_limite: datetime | None = None
    responsavel_id: UUID | None = None
    observacoes: str | None = Field(None, max_length=2000)


class DocumentKitAssignmentCreate(DocumentKitAssignmentBase):
    """Schema para criacao de DocumentKitAssignment."""

    kit_id: UUID
    condominio_id: UUID


class DocumentKitAssignmentUpdate(BaseModel):
    """Schema para atualizacao de DocumentKitAssignment."""

    status: AssignmentStatus | None = None
    data_limite: datetime | None = None
    responsavel_id: UUID | None = None
    aprovador_id: UUID | None = None
    observacoes: str | None = Field(None, max_length=2000)
    motivo_reprovacao: str | None = Field(None, max_length=2000)


class DocumentKitAssignmentResponse(DocumentKitAssignmentBase):
    """Schema de resposta para DocumentKitAssignment."""

    id: UUID
    kit_id: UUID
    condominio_id: UUID
    status: AssignmentStatus
    data_inicio: datetime
    data_conclusao: datetime | None = None
    total_itens: int
    itens_pendentes: int
    itens_aprovados: int
    itens_reprovados: int
    percentual_completo: int
    aprovador_id: UUID | None = None
    motivo_reprovacao: str | None = None
    notificacoes_count: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# === Document Kit Item Status Schemas ===


class DocumentKitItemStatusBase(BaseModel):
    """Schema base para DocumentKitItemStatus."""

    arquivo_url: str | None = Field(None, max_length=500)
    arquivo_nome: str | None = Field(None, max_length=255)
    data_validade: datetime | None = None


class DocumentKitItemStatusUpdate(BaseModel):
    """Schema para atualizacao de DocumentKitItemStatus."""

    status: ItemStatusEnum | None = None
    arquivo_url: str | None = Field(None, max_length=500)
    arquivo_nome: str | None = Field(None, max_length=255)
    arquivo_tamanho: int | None = None
    arquivo_tipo: str | None = Field(None, max_length=100)
    data_validade: datetime | None = None
    observacoes_analise: str | None = Field(None, max_length=2000)
    motivo_reprovacao: str | None = Field(None, max_length=2000)


class DocumentKitItemStatusResponse(DocumentKitItemStatusBase):
    """Schema de resposta para DocumentKitItemStatus."""

    id: UUID
    assignment_id: UUID
    item_id: UUID
    condominio_id: UUID
    status: ItemStatusEnum
    arquivo_tamanho: int | None = None
    arquivo_tipo: str | None = None
    is_vencido: bool
    analisado_por: UUID | None = None
    analisado_at: datetime | None = None
    observacoes_analise: str | None = None
    motivo_reprovacao: str | None = None
    tentativas: int
    enviado_por: UUID | None = None
    enviado_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# === Stats and Analytics Schemas ===


class KitStatsResponse(BaseModel):
    """Estatisticas de kits."""

    total_kits: int
    kits_ativos: int
    kits_inativos: int
    total_assignments: int
    assignments_pendentes: int
    assignments_completos: int
    assignments_vencidos: int
    taxa_conclusao: float
    tempo_medio_conclusao_dias: float
    por_tipo: dict
    por_status: dict


class AssignmentProgressResponse(BaseModel):
    """Progresso de uma atribuicao."""

    assignment_id: UUID
    kit_nome: str
    entity_nome: str
    status: AssignmentStatus
    total_itens: int
    itens_pendentes: int
    itens_enviados: int
    itens_em_analise: int
    itens_aprovados: int
    itens_reprovados: int
    percentual_completo: int
    dias_restantes: int
    is_vencido: bool
    itens: list[dict]


class KitComplianceResponse(BaseModel):
    """Conformidade de kits por entidade."""

    entity_type: EntityType
    entity_id: UUID
    entity_nome: str
    total_kits_atribuidos: int
    kits_completos: int
    kits_pendentes: int
    kits_vencidos: int
    taxa_conformidade: float
    documentos_vencidos: int
    proximos_vencimentos: list[dict]
    alertas: list[str]


class KitSuggestionResponse(BaseModel):
    """Sugestao de kit para entidade."""

    kit_id: UUID
    kit_nome: str
    kit_tipo: KitType
    relevancia_score: float
    motivo: str
    itens_count: int
    prazo_sugerido_dias: int
