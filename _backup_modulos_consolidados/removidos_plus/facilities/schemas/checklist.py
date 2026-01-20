"""
Schemas Pydantic para Checklist e ChecklistItem.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.facilities.models.checklist import ChecklistStatus, ItemStatus


class ChecklistItemBase(BaseModel):
    """Schema base para ChecklistItem."""

    order: int = Field(default=0, ge=0, description="Ordem de exibição")
    category: Optional[str] = Field(None, max_length=100, description="Categoria")
    subcategory: Optional[str] = Field(None, max_length=100, description="Subcategoria")
    question: str = Field(..., min_length=1, max_length=500, description="Pergunta/Descrição")
    description: Optional[str] = Field(None, max_length=1000, description="Descrição detalhada")
    help_text: Optional[str] = Field(None, max_length=500, description="Texto de ajuda")
    answer_type: str = Field(
        default="boolean",
        description="Tipo de resposta (boolean, text, number, select, photo)",
    )
    answer_options: Optional[List[str]] = Field(None, description="Opções (para select)")
    is_required: bool = Field(default=True, description="Obrigatório")
    weight: float = Field(default=1.0, ge=0, description="Peso na pontuação")
    requires_photo: bool = Field(default=False, description="Requer foto")
    requires_notes_on_fail: bool = Field(default=True, description="Requer observação se falhar")
    reference: Optional[str] = Field(None, max_length=255, description="Referência")
    norm_reference: Optional[str] = Field(None, max_length=100, description="Norma de referência")


class ChecklistItemCreate(ChecklistItemBase):
    """Schema para criação de ChecklistItem."""


class ChecklistItemUpdate(BaseModel):
    """Schema para atualização de ChecklistItem."""

    order: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    question: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    help_text: Optional[str] = Field(None, max_length=500)
    status: Optional[ItemStatus] = None
    answer: Optional[str] = Field(None, max_length=2000)
    notes: Optional[str] = Field(None, max_length=2000)
    photos: Optional[List[str]] = None
    is_required: Optional[bool] = None
    weight: Optional[float] = Field(None, ge=0)
    requires_photo: Optional[bool] = None
    requires_notes_on_fail: Optional[bool] = None
    is_active: Optional[bool] = None


class ChecklistItemAnswer(BaseModel):
    """Schema para responder um item do checklist."""

    status: ItemStatus = Field(..., description="Status da resposta")
    answer: Optional[str] = Field(None, max_length=2000, description="Resposta/Valor")
    notes: Optional[str] = Field(None, max_length=2000, description="Observações")
    photos: Optional[List[str]] = Field(None, description="Fotos")


class ChecklistItemResponse(BaseModel):
    """Schema de resposta para ChecklistItem."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    checklist_id: str
    order: int
    category: Optional[str]
    subcategory: Optional[str]
    question: str
    description: Optional[str]
    help_text: Optional[str]
    status: str
    answer: Optional[str]
    answer_type: str
    answer_options: Optional[List[str]]
    notes: Optional[str]
    photos: Optional[List[str]]
    is_required: bool
    weight: float
    requires_photo: bool
    requires_notes_on_fail: bool
    reference: Optional[str]
    norm_reference: Optional[str]
    answered_at: Optional[datetime]
    answered_by: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades calculadas
    is_answered: bool
    is_conforming: bool
    needs_attention: bool
    score_contribution: float


class ChecklistBase(BaseModel):
    """Schema base para Checklist."""

    name: str = Field(..., min_length=1, max_length=255, description="Nome")
    description: Optional[str] = Field(None, max_length=2000, description="Descrição")
    version: str = Field(default="1.0", max_length=10, description="Versão")
    is_template: bool = Field(default=False, description="É template")
    category: Optional[str] = Field(None, max_length=100, description="Categoria")
    area_id: Optional[str] = Field(None, description="ID da área")
    client_id: Optional[str] = Field(None, description="ID do cliente")
    notes: Optional[str] = Field(None, max_length=2000, description="Observações")
    tags: Optional[List[str]] = Field(None, description="Tags")


class ChecklistCreate(ChecklistBase):
    """Schema para criação de Checklist."""

    code: Optional[str] = Field(None, max_length=20, description="Código (auto-gerado se vazio)")
    template_id: Optional[str] = Field(None, description="ID do template base")
    inspection_id: Optional[str] = Field(None, description="ID da inspeção")
    items: Optional[List[ChecklistItemCreate]] = Field(None, description="Itens do checklist")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        """Valida e normaliza o código do checklist."""
        if v:
            return v.upper().strip()
        return v


class ChecklistUpdate(BaseModel):
    """Schema para atualização parcial de Checklist."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    version: Optional[str] = Field(None, max_length=10)
    status: Optional[ChecklistStatus] = None
    category: Optional[str] = Field(None, max_length=100)
    area_id: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=2000)
    general_observations: Optional[str] = Field(None, max_length=5000)
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ChecklistFill(BaseModel):
    """Schema para preenchimento de checklist."""

    items: List[ChecklistItemAnswer] = Field(..., description="Respostas dos itens")
    general_observations: Optional[str] = Field(None, max_length=5000)
    notes: Optional[str] = Field(None, max_length=2000)


class ChecklistResponse(BaseModel):
    """Schema de resposta para Checklist."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    description: Optional[str]
    version: str
    status: str
    is_template: bool
    category: Optional[str]
    area_id: Optional[str]
    inspection_id: Optional[str]
    template_id: Optional[str]
    client_id: Optional[str]
    total_items: int
    completed_items: int
    items_ok: int
    items_warning: int
    items_critical: int
    score: Optional[float]
    filled_by: Optional[str]
    filled_at: Optional[datetime]
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    notes: Optional[str]
    general_observations: Optional[str]
    tags: Optional[List[str]]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades calculadas
    is_completed: bool
    completion_rate: float
    compliance_rate: Optional[float]
    has_critical_items: bool

    # Items (opcional, para detalhes)
    items: Optional[List[ChecklistItemResponse]] = None


class ChecklistListResponse(BaseModel):
    """Schema para listagem paginada de Checklists."""

    items: List[ChecklistResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ChecklistFilter(BaseModel):
    """Schema para filtros de busca de Checklists."""

    search: Optional[str] = Field(None, description="Busca por nome ou código")
    status: Optional[ChecklistStatus] = None
    is_template: Optional[bool] = None
    category: Optional[str] = None
    area_id: Optional[str] = None
    client_id: Optional[str] = None
    inspection_id: Optional[str] = None
    filled_by: Optional[str] = None
    has_critical_items: Optional[bool] = None
    min_score: Optional[float] = Field(None, ge=0, le=100)
    max_score: Optional[float] = Field(None, ge=0, le=100)
    created_start: Optional[datetime] = None
    created_end: Optional[datetime] = None


class ChecklistStats(BaseModel):
    """Estatísticas de checklists."""

    total: int = Field(..., description="Total de checklists")
    templates: int = Field(..., description="Templates")
    by_status: Dict[str, int] = Field(..., description="Por status")
    by_category: Dict[str, int] = Field(..., description="Por categoria")
    avg_score: Optional[float] = Field(None, description="Pontuação média")
    avg_completion_rate: float = Field(..., description="Taxa média de preenchimento")
    with_critical_items: int = Field(..., description="Com itens críticos")
    completed_this_month: int = Field(..., description="Concluídos este mês")


class ChecklistClone(BaseModel):
    """Schema para clonar checklist."""

    name: str = Field(..., min_length=1, max_length=255, description="Nome do novo checklist")
    area_id: Optional[str] = Field(None, description="ID da área")
    inspection_id: Optional[str] = Field(None, description="ID da inspeção")
