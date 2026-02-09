"""
Schemas de Certidao - Licitacoes
================================
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.bidding.models.certificate import CertificateSource


class CertificateBase(BaseModel):
    """Schema base para certidao."""

    tipo: str = Field(..., max_length=50)
    nome: str = Field(..., min_length=1, max_length=255)
    cnpj: str = Field(..., min_length=14, max_length=18)
    razao_social: str | None = Field(None, max_length=255)


class CertificateCreate(CertificateBase):
    """Schema para criacao de certidao."""

    codigo_verificacao: str | None = None
    data_emissao: datetime | None = None
    data_validade: datetime | None = None
    hora_emissao: str | None = None

    situacao: str | None = None
    texto_certidao: str | None = None

    arquivo_url: str | None = None
    arquivo_nome: str | None = None

    fonte: str = Field(default=CertificateSource.MANUAL.value)
    obtencao_automatica: bool = Field(default=False)

    orgao_emissor: str | None = None
    orgao_uf: str | None = Field(None, max_length=2)
    orgao_url: str | None = None

    metadados: dict = Field(default_factory=dict)
    observacoes: str | None = None


class CertificateUpdate(BaseModel):
    """Schema para atualizacao de certidao."""

    nome: str | None = None
    codigo_verificacao: str | None = None
    data_emissao: datetime | None = None
    data_validade: datetime | None = None

    situacao: str | None = None
    texto_certidao: str | None = None

    arquivo_url: str | None = None
    arquivo_nome: str | None = None

    status: str | None = None
    obtencao_automatica: bool | None = None

    orgao_emissor: str | None = None
    orgao_uf: str | None = None
    orgao_url: str | None = None

    metadados: dict | None = None
    observacoes: str | None = None


class CertificateResponse(CertificateBase):
    """Schema de resposta para certidao."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    ativo: bool

    codigo_verificacao: str | None = None
    data_emissao: datetime | None = None
    data_validade: datetime | None = None
    hora_emissao: str | None = None

    situacao: str | None = None
    texto_certidao: str | None = None
    observacoes_orgao: str | None = None

    arquivo_url: str | None = None
    arquivo_nome: str | None = None
    arquivo_hash: str | None = None

    fonte: str
    obtencao_automatica: bool
    ultima_tentativa: datetime | None = None
    proxima_tentativa: datetime | None = None
    tentativas_falha: int = 0
    erro_obtencao: str | None = None

    alerta_enviado_30d: bool = False
    alerta_enviado_15d: bool = False
    alerta_enviado_7d: bool = False

    orgao_emissor: str | None = None
    orgao_uf: str | None = None
    orgao_url: str | None = None

    metadados: dict = {}

    # Propriedades calculadas
    esta_valida: bool | None = None
    dias_para_vencer: int | None = None
    horas_para_vencer: int | None = None
    esta_vencendo: bool | None = None
    precisa_renovar: bool | None = None
    pode_usar_licitacao: bool | None = None

    observacoes: str | None = None

    # Auditoria
    created_at: datetime
    updated_at: datetime | None = None


class CertificateRenewRequest(BaseModel):
    """Schema para solicitacao de renovacao de certidao."""

    certificate_id: UUID
    forcar_renovacao: bool = Field(default=False)


class CertificateRenewResponse(BaseModel):
    """Resposta da renovacao de certidao."""

    certificate_id: UUID
    sucesso: bool
    mensagem: str
    nova_validade: datetime | None = None
    arquivo_url: str | None = None


class CertificateBulkStatusResponse(BaseModel):
    """Status consolidado de todas as certidoes."""

    total: int
    validas: int
    vencendo: int
    vencidas: int
    pendentes: int
    com_erro: int

    certidoes: list[CertificateResponse]

    # Resumo por tipo
    por_tipo: dict = {}

    # Alertas
    alertas: list[str] = []


class CertificateTypeInfo(BaseModel):
    """Informacoes sobre tipo de certidao."""

    tipo: str
    nome: str
    descricao: str
    orgao_emissor: str
    url_emissao: str | None = None
    validade_padrao_dias: int
    renovacao_automatica_disponivel: bool
    obrigatoria: bool = True


class CertificateTypesResponse(BaseModel):
    """Lista de tipos de certidao disponiveis."""

    tipos: list[CertificateTypeInfo]


class CertificateListResponse(BaseModel):
    """Schema de lista de certidoes com paginacao."""

    items: list[CertificateResponse]
    total: int
    page: int
    size: int
    resumo: CertificateBulkStatusResponse
