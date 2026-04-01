"""
Schemas Pydantic para GedDocumentKit (Kit Documental).
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.people_management.ged.models.document_kit import KitSendMethod, KitStatus


class KitBase(BaseModel):
    """Campos compartilhados para kits documentais."""

    client_id: str = Field(..., description="ID do cliente (ged_clients)")
    reference_month: date = Field(..., description="Mês de referência (primeiro dia do mês)")
    notes: str | None = Field(None, description="Observações")

    @field_validator("reference_month")
    @classmethod
    def normalize_to_first_day(cls, v: date) -> date:
        """Normaliza a data para o primeiro dia do mês."""
        return v.replace(day=1)


class KitCreate(KitBase):
    """Schema para criação de kit documental."""

    total_employees: int = Field(0, ge=0, description="Qtde de funcionários alocados no mês")


class KitUpdate(BaseModel):
    """Schema para atualização parcial de kit documental."""

    notes: str | None = None
    total_employees: int | None = Field(None, ge=0)
    total_documents: int | None = Field(None, ge=0)
    zip_file_path: str | None = None
    google_drive_link: str | None = None


class KitStatusUpdate(BaseModel):
    """Schema para atualização de status do kit."""

    status: KitStatus = Field(..., description="Novo status do kit")
    sent_method: KitSendMethod | None = Field(None, description="Método de envio (obrigatório se status=ENVIADO)")
    sent_to: str | None = Field(None, max_length=500, description="Destinatário do envio")
    approved_by: str | None = Field(None, max_length=255, description="Nome de quem aprovou")
    notes: str | None = Field(None, description="Observações sobre a mudança de status")

    @field_validator("sent_method")
    @classmethod
    def validate_send_method_required(cls, v: KitSendMethod | None, info) -> KitSendMethod | None:
        """Valida que sent_method é informado quando status é ENVIADO."""
        data = info.data
        if data.get("status") == KitStatus.ENVIADO and v is None:
            raise ValueError("Método de envio é obrigatório quando o status é ENVIADO")
        return v


class DocumentsSummary(BaseModel):
    """Resumo de documentos dentro de um kit."""

    total: int = 0
    signed: int = 0
    unsigned: int = 0
    by_type: dict[str, int] = Field(default_factory=dict)


class KitResponse(BaseModel):
    """Schema de resposta para kit documental."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    client_id: str
    client_name: str | None = Field(None, description="Nome do cliente (denormalizado)")
    reference_month: date
    status: str
    total_employees: int = 0
    total_documents: int = 0
    documents_signed: int = 0
    completion_percentage: Decimal = Decimal("0.00")
    sent_at: datetime | None = None
    sent_method: str | None = None
    sent_to: str | None = None
    approved_at: datetime | None = None
    approved_by: str | None = None
    zip_file_path: str | None = None
    google_drive_link: str | None = None
    notes: str | None = None
    documents_summary: DocumentsSummary | None = None
    created_at: datetime
    updated_at: datetime


class KitListResponse(BaseModel):
    """Schema de listagem paginada de kits documentais."""

    items: list[KitResponse]
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    pages: int = Field(..., ge=0, description="Total de páginas")


class KitStatusCount(BaseModel):
    """Contagem de kits por status."""

    status: str
    count: int


class KitSummary(BaseModel):
    """Resumo geral dos kits para dashboard."""

    total_kits: int = 0
    by_status: list[KitStatusCount] = Field(default_factory=list)
    total_clients: int = 0
    kits_pending_send: int = Field(0, description="Kits completos ainda não enviados")
    kits_pending_approval: int = Field(0, description="Kits enviados aguardando aprovação")
    average_completion: Decimal = Field(
        Decimal("0.00"),
        description="Percentual médio de completude dos kits em montagem",
    )
    reference_month: date | None = Field(None, description="Mês de referência do resumo")
