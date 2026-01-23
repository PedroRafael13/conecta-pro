"""
Schemas Pydantic para Occurrence (Ocorrência).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from modules.operacional.occurrences.models import (
    OccurrenceCategory,
    OccurrenceSeverity,
    OccurrenceStatus,
    OccurrenceType,
)


class AttachmentSchema(BaseModel):
    """Schema para anexo."""

    type: str = Field(..., description="Tipo do arquivo (image, video, document)")
    url: str = Field(..., description="URL do arquivo")
    name: str = Field(..., description="Nome do arquivo")
    size: Optional[int] = Field(None, description="Tamanho em bytes")
    uploaded_at: Optional[datetime] = Field(None, description="Data do upload")


class OccurrenceBase(BaseModel):
    """Schema base para Occurrence (registro disciplinar)."""

    title: str = Field(..., min_length=2, max_length=255, description="Título da infração")
    description: str = Field(..., min_length=10, description="Descrição do que foi encontrado")
    occurrence_type: OccurrenceType = Field(..., description="Tipo da infração")
    severity: OccurrenceSeverity = Field(..., description="Severidade (leve, moderada, grave, gravíssima)")
    category: OccurrenceCategory = Field(..., description="Categoria da infração")
    occurred_at: datetime = Field(..., description="Data/hora em que foi identificada")

    # Envolvidos (OBRIGATÓRIOS)
    employee_id: str = Field(..., description="ID do funcionário que cometeu a infração")
    post_id: str = Field(..., description="ID do posto onde ocorreu")

    # Opcionais
    patrol_round_id: Optional[str] = Field(None, description="ID da ronda relacionada")
    witnesses: Optional[str] = Field(None, description="Testemunhas da infração")


class OccurrenceCreate(OccurrenceBase):
    """Schema para criação de Occurrence."""

    pass


class OccurrenceUpdate(BaseModel):
    """Schema para atualização parcial de Occurrence."""

    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    occurrence_type: Optional[OccurrenceType] = None
    severity: Optional[OccurrenceSeverity] = None
    category: Optional[OccurrenceCategory] = None
    status: Optional[OccurrenceStatus] = None
    occurred_at: Optional[datetime] = None
    employee_id: Optional[str] = None
    post_id: Optional[str] = None
    patrol_round_id: Optional[str] = None
    witnesses: Optional[str] = None
    corrective_action: Optional[str] = None
    is_active: Optional[bool] = None


class OccurrenceResolve(BaseModel):
    """Schema para resolver uma ocorrência disciplinar."""

    corrective_action: str = Field(..., min_length=10, description="Ação corretiva aplicada (advertência, suspensão, etc)")
    resolution_notes: Optional[str] = Field(None, description="Notas adicionais sobre a resolução")


class OccurrenceResponse(BaseModel):
    """Schema de resposta para Occurrence."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    title: str
    description: str
    occurrence_type: str
    severity: str
    category: str
    status: str

    # Envolvidos
    employee_id: str  # Funcionário infrator
    inspector_id: str  # Gestor fiscalizador
    post_id: str  # Posto
    patrol_round_id: Optional[str]  # Ronda relacionada
    witnesses: Optional[str]  # Testemunhas

    # Datas
    occurred_at: datetime
    reported_at: datetime
    resolved_at: Optional[datetime]

    # Resolução
    corrective_action: Optional[str]  # Ação corretiva aplicada
    resolution_notes: Optional[str]
    resolved_by_id: Optional[str]

    # Evidências
    attachments: Optional[Dict[str, Any]]  # JSONB do banco

    # Controle
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades computadas
    is_resolved: bool
    is_severe: bool  # Se é grave/gravíssima
    resolution_time_hours: Optional[float]


class OccurrenceListResponse(BaseModel):
    """Schema de resposta para listagem de Occurrences."""

    items: List[OccurrenceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class OccurrenceFilter(BaseModel):
    """Schema para filtros de busca de Occurrences."""

    occurrence_type: Optional[OccurrenceType] = None
    severity: Optional[OccurrenceSeverity] = None
    category: Optional[OccurrenceCategory] = None
    status: Optional[OccurrenceStatus] = None
    employee_id: Optional[str] = None  # Filtrar por funcionário
    inspector_id: Optional[str] = None  # Filtrar por fiscalizador
    post_id: Optional[str] = None
    patrol_round_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None


class OccurrenceStats(BaseModel):
    """Schema para estatísticas de Occurrences."""

    total: int = 0
    by_status: Dict[str, int] = {}
    by_type: Dict[str, int] = {}
    by_severity: Dict[str, int] = {}
    by_category: Dict[str, int] = {}
    open: int = 0
    in_analysis: int = 0
    resolved: int = 0
    severe: int = 0  # Graves + gravíssimas
    by_employee: Dict[str, int] = {}  # Top funcionários com mais infrações
    avg_resolution_time_hours: Optional[float] = None
