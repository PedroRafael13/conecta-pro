"""
Schemas de Documento da Empresa - Licitacoes
=============================================
"""

from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from modules.bidding.models.company_document import DocumentType, DocumentStatus


class CompanyDocumentBase(BaseModel):
    """Schema base para documento da empresa."""
    tipo: str = Field(..., max_length=50)
    nome: str = Field(..., min_length=1, max_length=255)
    descricao: Optional[str] = None
    numero: Optional[str] = Field(None, max_length=100)
    orgao_emissor: Optional[str] = Field(None, max_length=255)


class CompanyDocumentCreate(CompanyDocumentBase):
    """Schema para criacao de documento."""
    data_emissao: Optional[date] = None
    data_validade: Optional[date] = None
    arquivo_url: Optional[str] = None
    arquivo_nome: Optional[str] = None
    arquivo_tamanho: Optional[int] = None
    certidao_automatica: bool = Field(default=False)
    observacoes: Optional[str] = None
    metadados: dict = Field(default_factory=dict)


class CompanyDocumentUpdate(BaseModel):
    """Schema para atualizacao de documento."""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = None
    numero: Optional[str] = None
    data_emissao: Optional[date] = None
    data_validade: Optional[date] = None
    arquivo_url: Optional[str] = None
    arquivo_nome: Optional[str] = None
    arquivo_tamanho: Optional[int] = None
    status: Optional[str] = None
    certidao_automatica: Optional[bool] = None
    orgao_emissor: Optional[str] = None
    observacoes: Optional[str] = None
    metadados: Optional[dict] = None


class CompanyDocumentResponse(CompanyDocumentBase):
    """Schema de resposta para documento."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    ativo: bool

    # Datas
    data_emissao: Optional[date] = None
    data_validade: Optional[date] = None

    # Arquivo
    arquivo_url: Optional[str] = None
    arquivo_nome: Optional[str] = None
    arquivo_tamanho: Optional[int] = None

    # Renovacao
    certidao_automatica: bool
    ultima_verificacao: Optional[datetime] = None
    ultima_renovacao: Optional[datetime] = None
    erro_renovacao: Optional[str] = None

    # Metadados
    metadados: dict = {}
    observacoes: Optional[str] = None

    # Propriedades calculadas
    esta_valido: Optional[bool] = None
    dias_para_vencer: Optional[int] = None
    esta_vencendo: Optional[bool] = None

    # Auditoria
    created_at: datetime
    updated_at: Optional[datetime] = None


class DocumentExpiringResponse(BaseModel):
    """Resposta para documentos vencendo."""
    documentos_vencendo: List[CompanyDocumentResponse]
    documentos_vencidos: List[CompanyDocumentResponse]
    total_vencendo: int
    total_vencidos: int
    dias_alerta: int


class DocumentTypeInfo(BaseModel):
    """Informacoes sobre tipo de documento."""
    tipo: str
    nome: str
    descricao: str
    renovacao_automatica_disponivel: bool
    validade_padrao_dias: Optional[int] = None
    obrigatorio_licitacao: bool = True


class DocumentTypesResponse(BaseModel):
    """Lista de tipos de documento disponiveis."""
    tipos: List[DocumentTypeInfo]
