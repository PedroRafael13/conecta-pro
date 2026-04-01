"""
Schemas de Documento da Empresa - Licitacoes
=============================================
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompanyDocumentBase(BaseModel):
    """Schema base para documento da empresa."""

    tipo: str = Field(..., max_length=50)
    nome: str = Field(..., min_length=1, max_length=255)
    descricao: str | None = None
    numero: str | None = Field(None, max_length=100)
    orgao_emissor: str | None = Field(None, max_length=255)


class CompanyDocumentCreate(CompanyDocumentBase):
    """Schema para criacao de documento."""

    data_emissao: date | None = None
    data_validade: date | None = None
    arquivo_url: str | None = None
    arquivo_nome: str | None = None
    arquivo_tamanho: int | None = None
    certidao_automatica: bool = Field(default=False)
    observacoes: str | None = None
    metadados: dict = Field(default_factory=dict)


class CompanyDocumentUpdate(BaseModel):
    """Schema para atualizacao de documento."""

    nome: str | None = Field(None, min_length=1, max_length=255)
    descricao: str | None = None
    numero: str | None = None
    data_emissao: date | None = None
    data_validade: date | None = None
    arquivo_url: str | None = None
    arquivo_nome: str | None = None
    arquivo_tamanho: int | None = None
    status: str | None = None
    certidao_automatica: bool | None = None
    orgao_emissor: str | None = None
    observacoes: str | None = None
    metadados: dict | None = None


class CompanyDocumentResponse(CompanyDocumentBase):
    """Schema de resposta para documento."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    ativo: bool

    # Datas
    data_emissao: date | None = None
    data_validade: date | None = None

    # Arquivo
    arquivo_url: str | None = None
    arquivo_nome: str | None = None
    arquivo_tamanho: int | None = None

    # Renovacao
    certidao_automatica: bool
    ultima_verificacao: datetime | None = None
    ultima_renovacao: datetime | None = None
    erro_renovacao: str | None = None

    # Metadados
    metadados: dict = {}
    observacoes: str | None = None

    # Propriedades calculadas
    esta_valido: bool | None = None
    dias_para_vencer: int | None = None
    esta_vencendo: bool | None = None

    # Auditoria
    created_at: datetime
    updated_at: datetime | None = None


class DocumentExpiringResponse(BaseModel):
    """Resposta para documentos vencendo."""

    documentos_vencendo: list[CompanyDocumentResponse]
    documentos_vencidos: list[CompanyDocumentResponse]
    total_vencendo: int
    total_vencidos: int
    dias_alerta: int


class DocumentTypeInfo(BaseModel):
    """Informacoes sobre tipo de documento."""

    tipo: str
    nome: str
    descricao: str
    renovacao_automatica_disponivel: bool
    validade_padrao_dias: int | None = None
    obrigatorio_licitacao: bool = True


class DocumentTypesResponse(BaseModel):
    """Lista de tipos de documento disponiveis."""

    tipos: list[DocumentTypeInfo]
