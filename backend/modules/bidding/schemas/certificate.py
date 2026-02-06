"""
Schemas de Certidao - Licitacoes
================================
"""

from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from modules.bidding.models.certificate import CertificateType, CertificateStatus, CertificateSource


class CertificateBase(BaseModel):
    """Schema base para certidao."""
    tipo: str = Field(..., max_length=50)
    nome: str = Field(..., min_length=1, max_length=255)
    cnpj: str = Field(..., min_length=14, max_length=18)
    razao_social: Optional[str] = Field(None, max_length=255)


class CertificateCreate(CertificateBase):
    """Schema para criacao de certidao."""
    codigo_verificacao: Optional[str] = None
    data_emissao: Optional[datetime] = None
    data_validade: Optional[datetime] = None
    hora_emissao: Optional[str] = None

    situacao: Optional[str] = None
    texto_certidao: Optional[str] = None

    arquivo_url: Optional[str] = None
    arquivo_nome: Optional[str] = None

    fonte: str = Field(default=CertificateSource.MANUAL.value)
    obtencao_automatica: bool = Field(default=False)

    orgao_emissor: Optional[str] = None
    orgao_uf: Optional[str] = Field(None, max_length=2)
    orgao_url: Optional[str] = None

    metadados: dict = Field(default_factory=dict)
    observacoes: Optional[str] = None


class CertificateUpdate(BaseModel):
    """Schema para atualizacao de certidao."""
    nome: Optional[str] = None
    codigo_verificacao: Optional[str] = None
    data_emissao: Optional[datetime] = None
    data_validade: Optional[datetime] = None

    situacao: Optional[str] = None
    texto_certidao: Optional[str] = None

    arquivo_url: Optional[str] = None
    arquivo_nome: Optional[str] = None

    status: Optional[str] = None
    obtencao_automatica: Optional[bool] = None

    orgao_emissor: Optional[str] = None
    orgao_uf: Optional[str] = None
    orgao_url: Optional[str] = None

    metadados: Optional[dict] = None
    observacoes: Optional[str] = None


class CertificateResponse(CertificateBase):
    """Schema de resposta para certidao."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    ativo: bool

    codigo_verificacao: Optional[str] = None
    data_emissao: Optional[datetime] = None
    data_validade: Optional[datetime] = None
    hora_emissao: Optional[str] = None

    situacao: Optional[str] = None
    texto_certidao: Optional[str] = None
    observacoes_orgao: Optional[str] = None

    arquivo_url: Optional[str] = None
    arquivo_nome: Optional[str] = None
    arquivo_hash: Optional[str] = None

    fonte: str
    obtencao_automatica: bool
    ultima_tentativa: Optional[datetime] = None
    proxima_tentativa: Optional[datetime] = None
    tentativas_falha: int = 0
    erro_obtencao: Optional[str] = None

    alerta_enviado_30d: bool = False
    alerta_enviado_15d: bool = False
    alerta_enviado_7d: bool = False

    orgao_emissor: Optional[str] = None
    orgao_uf: Optional[str] = None
    orgao_url: Optional[str] = None

    metadados: dict = {}

    # Propriedades calculadas
    esta_valida: Optional[bool] = None
    dias_para_vencer: Optional[int] = None
    horas_para_vencer: Optional[int] = None
    esta_vencendo: Optional[bool] = None
    precisa_renovar: Optional[bool] = None
    pode_usar_licitacao: Optional[bool] = None

    observacoes: Optional[str] = None

    # Auditoria
    created_at: datetime
    updated_at: Optional[datetime] = None


class CertificateRenewRequest(BaseModel):
    """Schema para solicitacao de renovacao de certidao."""
    certificate_id: UUID
    forcar_renovacao: bool = Field(default=False)


class CertificateRenewResponse(BaseModel):
    """Resposta da renovacao de certidao."""
    certificate_id: UUID
    sucesso: bool
    mensagem: str
    nova_validade: Optional[datetime] = None
    arquivo_url: Optional[str] = None


class CertificateBulkStatusResponse(BaseModel):
    """Status consolidado de todas as certidoes."""
    total: int
    validas: int
    vencendo: int
    vencidas: int
    pendentes: int
    com_erro: int

    certidoes: List[CertificateResponse]

    # Resumo por tipo
    por_tipo: dict = {}

    # Alertas
    alertas: List[str] = []


class CertificateTypeInfo(BaseModel):
    """Informacoes sobre tipo de certidao."""
    tipo: str
    nome: str
    descricao: str
    orgao_emissor: str
    url_emissao: Optional[str] = None
    validade_padrao_dias: int
    renovacao_automatica_disponivel: bool
    obrigatoria: bool = True


class CertificateTypesResponse(BaseModel):
    """Lista de tipos de certidao disponiveis."""
    tipos: List[CertificateTypeInfo]


class CertificateListResponse(BaseModel):
    """Schema de lista de certidoes com paginacao."""
    items: List[CertificateResponse]
    total: int
    page: int
    size: int
    resumo: CertificateBulkStatusResponse
