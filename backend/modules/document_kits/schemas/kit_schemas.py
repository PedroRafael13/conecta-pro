"""Schemas Pydantic para Kits Documentais."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.document_kits.models.document_kit import (
    KitType,
    KitStatus,
    ItemType,
    ItemPriority,
    AssignmentStatus,
    ItemStatusEnum,
    EntityType,
)


# === Document Kit Schemas ===


class DocumentKitBase(BaseModel):
    """Schema base para DocumentKit."""

    codigo: str = Field(..., min_length=1, max_length=50)
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=2000)
    tipo: KitType = Field(default=KitType.OUTRO)
    is_template: bool = Field(default=False)
    is_obrigatorio: bool = Field(default=True)
    prazo_dias: Optional[int] = Field(default=30, ge=1, le=365)
    permite_parcial: bool = Field(default=False)
    requer_aprovacao: bool = Field(default=True)
    entity_types: List[str] = Field(default_factory=list)
    departamentos: List[str] = Field(default_factory=list)
    cargos: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class DocumentKitCreate(DocumentKitBase):
    """Schema para criacao de DocumentKit."""

    condominio_id: UUID


class DocumentKitUpdate(BaseModel):
    """Schema para atualizacao de DocumentKit."""

    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=2000)
    tipo: Optional[KitType] = None
    status: Optional[KitStatus] = None
    is_obrigatorio: Optional[bool] = None
    prazo_dias: Optional[int] = Field(None, ge=1, le=365)
    permite_parcial: Optional[bool] = None
    requer_aprovacao: Optional[bool] = None
    entity_types: Optional[List[str]] = None
    departamentos: Optional[List[str]] = None
    cargos: Optional[List[str]] = None
    tags: Optional[List[str]] = None


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
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DocumentKitListResponse(BaseModel):
    """Schema de lista de DocumentKits."""

    items: List[DocumentKitResponse]
    total: int
    page: int
    page_size: int
    pages: int


# === Document Kit Item Schemas ===


class DocumentKitItemBase(BaseModel):
    """Schema base para DocumentKitItem."""

    codigo: str = Field(..., min_length=1, max_length=50)
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=2000)
    instrucoes: Optional[str] = Field(None, max_length=5000)
    tipo: ItemType = Field(default=ItemType.DOCUMENTO_PESSOAL)
    prioridade: ItemPriority = Field(default=ItemPriority.OBRIGATORIO)
    ordem: int = Field(default=0, ge=0)
    formatos_aceitos: List[str] = Field(default_factory=list)
    tamanho_max_mb: int = Field(default=10, ge=1, le=100)
    requer_validade: bool = Field(default=False)
    validade_minima_dias: Optional[int] = Field(None, ge=1, le=3650)
    requer_autenticacao: bool = Field(default=False)
    template_url: Optional[str] = Field(None, max_length=500)
    exemplo_url: Optional[str] = Field(None, max_length=500)
    tags: List[str] = Field(default_factory=list)

    @field_validator("formatos_aceitos")
    @classmethod
    def validate_formatos(cls, value: List[str]) -> List[str]:
        """Valida formatos aceitos."""
        formatos_validos = [
            "pdf", "jpg", "jpeg", "png", "gif", "doc", "docx",
            "xls", "xlsx", "txt", "zip", "rar"
        ]
        for formato in value:
            if formato.lower() not in formatos_validos:
                raise ValueError(f"Formato invalido: {formato}")
        return [f.lower() for f in value]


class DocumentKitItemCreate(DocumentKitItemBase):
    """Schema para criacao de DocumentKitItem."""

    kit_id: UUID
    condominio_id: UUID
    depende_de: Optional[UUID] = None


class DocumentKitItemUpdate(BaseModel):
    """Schema para atualizacao de DocumentKitItem."""

    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=2000)
    instrucoes: Optional[str] = Field(None, max_length=5000)
    tipo: Optional[ItemType] = None
    prioridade: Optional[ItemPriority] = None
    ordem: Optional[int] = Field(None, ge=0)
    is_ativo: Optional[bool] = None
    formatos_aceitos: Optional[List[str]] = None
    tamanho_max_mb: Optional[int] = Field(None, ge=1, le=100)
    requer_validade: Optional[bool] = None
    validade_minima_dias: Optional[int] = Field(None, ge=1, le=3650)
    requer_autenticacao: Optional[bool] = None
    template_url: Optional[str] = Field(None, max_length=500)
    exemplo_url: Optional[str] = Field(None, max_length=500)
    depende_de: Optional[UUID] = None
    tags: Optional[List[str]] = None


class DocumentKitItemResponse(DocumentKitItemBase):
    """Schema de resposta para DocumentKitItem."""

    id: UUID
    kit_id: UUID
    condominio_id: UUID
    is_ativo: bool
    depende_de: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# === Document Kit Assignment Schemas ===


class DocumentKitAssignmentBase(BaseModel):
    """Schema base para DocumentKitAssignment."""

    entity_type: EntityType
    entity_id: UUID
    entity_nome: Optional[str] = Field(None, max_length=200)
    data_limite: Optional[datetime] = None
    responsavel_id: Optional[UUID] = None
    observacoes: Optional[str] = Field(None, max_length=2000)


class DocumentKitAssignmentCreate(DocumentKitAssignmentBase):
    """Schema para criacao de DocumentKitAssignment."""

    kit_id: UUID
    condominio_id: UUID


class DocumentKitAssignmentUpdate(BaseModel):
    """Schema para atualizacao de DocumentKitAssignment."""

    status: Optional[AssignmentStatus] = None
    data_limite: Optional[datetime] = None
    responsavel_id: Optional[UUID] = None
    aprovador_id: Optional[UUID] = None
    observacoes: Optional[str] = Field(None, max_length=2000)
    motivo_reprovacao: Optional[str] = Field(None, max_length=2000)


class DocumentKitAssignmentResponse(DocumentKitAssignmentBase):
    """Schema de resposta para DocumentKitAssignment."""

    id: UUID
    kit_id: UUID
    condominio_id: UUID
    status: AssignmentStatus
    data_inicio: datetime
    data_conclusao: Optional[datetime] = None
    total_itens: int
    itens_pendentes: int
    itens_aprovados: int
    itens_reprovados: int
    percentual_completo: int
    aprovador_id: Optional[UUID] = None
    motivo_reprovacao: Optional[str] = None
    notificacoes_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# === Document Kit Item Status Schemas ===


class DocumentKitItemStatusBase(BaseModel):
    """Schema base para DocumentKitItemStatus."""

    arquivo_url: Optional[str] = Field(None, max_length=500)
    arquivo_nome: Optional[str] = Field(None, max_length=255)
    data_validade: Optional[datetime] = None


class DocumentKitItemStatusUpdate(BaseModel):
    """Schema para atualizacao de DocumentKitItemStatus."""

    status: Optional[ItemStatusEnum] = None
    arquivo_url: Optional[str] = Field(None, max_length=500)
    arquivo_nome: Optional[str] = Field(None, max_length=255)
    arquivo_tamanho: Optional[int] = None
    arquivo_tipo: Optional[str] = Field(None, max_length=100)
    data_validade: Optional[datetime] = None
    observacoes_analise: Optional[str] = Field(None, max_length=2000)
    motivo_reprovacao: Optional[str] = Field(None, max_length=2000)


class DocumentKitItemStatusResponse(DocumentKitItemStatusBase):
    """Schema de resposta para DocumentKitItemStatus."""

    id: UUID
    assignment_id: UUID
    item_id: UUID
    condominio_id: UUID
    status: ItemStatusEnum
    arquivo_tamanho: Optional[int] = None
    arquivo_tipo: Optional[str] = None
    is_vencido: bool
    analisado_por: Optional[UUID] = None
    analisado_at: Optional[datetime] = None
    observacoes_analise: Optional[str] = None
    motivo_reprovacao: Optional[str] = None
    tentativas: int
    enviado_por: Optional[UUID] = None
    enviado_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

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
    itens: List[dict]


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
    proximos_vencimentos: List[dict]
    alertas: List[str]


class KitSuggestionResponse(BaseModel):
    """Sugestao de kit para entidade."""

    kit_id: UUID
    kit_nome: str
    kit_tipo: KitType
    relevancia_score: float
    motivo: str
    itens_count: int
    prazo_sugerido_dias: int
