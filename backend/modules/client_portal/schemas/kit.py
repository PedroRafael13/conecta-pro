"""
Schemas de kits documentais do Portal do Cliente.

Define os modelos de response para visualizacao de kits
e documentos pelo cliente externo.
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PortalDocumentResponse(BaseModel):
    """Response de um documento individual dentro de um kit."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID do documento")
    document_type: str = Field(..., description="Tipo do documento")
    document_name: str = Field(..., description="Nome de exibicao do documento")
    file_size_bytes: int | None = Field(None, description="Tamanho do arquivo em bytes")
    mime_type: str | None = Field(None, description="MIME type do arquivo")
    is_signed: bool = Field(default=False, description="Se o documento foi assinado")
    created_at: datetime = Field(..., description="Data de inclusao no kit")


class PortalKitResponse(BaseModel):
    """Response de um kit documental para o portal do cliente."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID do kit")
    client_id: str = Field(..., description="UUID do cliente")
    reference_month: date = Field(..., description="Mes de referencia do kit")
    status: str = Field(..., description="Status do kit")
    total_employees: int = Field(default=0, description="Total de funcionarios")
    total_documents: int = Field(default=0, description="Total de documentos")
    documents_signed: int = Field(default=0, description="Documentos assinados")
    completion_percentage: Decimal = Field(
        default=Decimal("0.00"),
        description="Percentual de completude",
    )
    sent_at: datetime | None = Field(None, description="Data de envio ao cliente")
    sent_method: str | None = Field(None, description="Metodo de envio")
    zip_file_path: str | None = Field(None, description="Caminho do ZIP consolidado")
    google_drive_link: str | None = Field(None, description="Link do Google Drive")
    notes: str | None = Field(None, description="Observacoes do kit")
    created_at: datetime = Field(..., description="Data de criacao")
    updated_at: datetime = Field(..., description="Data da ultima atualizacao")
    documents: list[PortalDocumentResponse] = Field(
        default_factory=list,
        description="Documentos do kit",
    )


class PortalKitListResponse(BaseModel):
    """Response paginada de kits para o portal do cliente."""

    model_config = ConfigDict(from_attributes=True)

    items: list[PortalKitResponse] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1)
    page_size: int = Field(default=20)
    pages: int = Field(default=0)
