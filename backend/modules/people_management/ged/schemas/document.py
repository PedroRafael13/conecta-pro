"""
Schemas Pydantic para KitDocument (Documentos do Kit).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from modules.people_management.ged.models.kit_document import DocumentType, SourceModule


class DocumentBase(BaseModel):
    """Campos compartilhados para documentos do kit."""

    kit_id: str = Field(..., description="ID do kit documental")
    employee_id: str | None = Field(None, description="ID do funcionário (nulo para docs da empresa)")
    document_type: DocumentType = Field(..., description="Tipo do documento")
    document_name: str = Field(..., min_length=1, max_length=500, description="Nome de exibição")
    source_module: SourceModule = Field(
        default=SourceModule.MANUAL,
        description="Módulo de origem (dp, rh, fiscal, operacoes, manual)",
    )
    source_record_id: str | None = Field(None, description="ID do registro de origem")
    notes: str | None = Field(None, description="Observações")


class DocumentCreate(DocumentBase):
    """Schema para criação de documento no kit."""

    file_path: str | None = Field(None, description="Caminho do arquivo no storage")
    file_size_bytes: int | None = Field(None, ge=0, description="Tamanho em bytes")
    mime_type: str = Field("application/pdf", max_length=100, description="MIME type")
    auto_generated: bool = Field(False, description="Se gerado automaticamente por integração")


class DocumentUpdate(BaseModel):
    """Schema para atualização parcial de documento."""

    document_name: str | None = Field(None, min_length=1, max_length=500)
    document_type: DocumentType | None = None
    file_path: str | None = None
    file_size_bytes: int | None = Field(None, ge=0)
    mime_type: str | None = Field(None, max_length=100)
    notes: str | None = None


class DocumentUpload(BaseModel):
    """Schema para upload manual de documento.

    Usado em conjunto com UploadFile do FastAPI — os metadados
    vêm neste schema enquanto o arquivo vem no form-data.
    """

    kit_id: str = Field(..., description="ID do kit documental")
    employee_id: str | None = Field(None, description="ID do funcionário (opcional)")
    document_type: DocumentType = Field(..., description="Tipo do documento")
    document_name: str | None = Field(
        None, max_length=500, description="Nome customizado (usa nome do arquivo se vazio)"
    )
    notes: str | None = Field(None, description="Observações")


class DocumentSignatureRequest(BaseModel):
    """Schema para solicitar assinatura de documento."""

    signer_id: str = Field(..., description="ID do funcionário que está assinando")
    signature_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="Hash SHA-256 do conteúdo do arquivo",
    )
    notes: str | None = Field(None, description="Observações sobre a assinatura")


class DocumentResponse(BaseModel):
    """Schema de resposta para documento do kit."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    kit_id: str
    employee_id: str | None = None
    employee_name: str | None = Field(None, description="Nome do funcionário (denormalizado)")
    document_type: str
    document_name: str
    file_path: str | None = None
    file_size_bytes: int | None = None
    file_size_display: str | None = Field(None, description="Tamanho legível (ex: 1.2 MB)")
    mime_type: str | None = None
    is_signed: bool = False
    signed_at: datetime | None = None
    signed_by: str | None = None
    signature_hash: str | None = None
    source_module: str = "manual"
    source_record_id: str | None = None
    auto_generated: bool = False
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DocumentListResponse(BaseModel):
    """Schema de listagem paginada de documentos."""

    items: list[DocumentResponse]
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    pages: int = Field(..., ge=0, description="Total de páginas")
    signed_count: int = Field(0, description="Quantidade de documentos assinados")
    unsigned_count: int = Field(0, description="Quantidade de documentos não assinados")
