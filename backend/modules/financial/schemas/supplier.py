"""Schemas para fornecedores."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from modules.financial.models.supplier import (
    PaymentTerms,
    SupplierCategory,
    SupplierStatus,
    SupplierType,
)


class SupplierBase(BaseModel):
    """Base para fornecedor."""

    name: str = Field(..., min_length=2, max_length=200)
    trade_name: Optional[str] = Field(None, max_length=200)
    supplier_type: SupplierType = SupplierType.PESSOA_JURIDICA
    category: Optional[SupplierCategory] = None
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    state_registration: Optional[str] = Field(None, max_length=20)
    municipal_registration: Optional[str] = Field(None, max_length=20)
    cnae: Optional[str] = Field(None, max_length=10)

    # Contato
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=200)

    # Contato principal
    contact_name: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_position: Optional[str] = Field(None, max_length=50)

    # Endereço
    address_street: Optional[str] = Field(None, max_length=200)
    address_number: Optional[str] = Field(None, max_length=20)
    address_complement: Optional[str] = Field(None, max_length=100)
    address_neighborhood: Optional[str] = Field(None, max_length=100)
    address_city: Optional[str] = Field(None, max_length=100)
    address_state: Optional[str] = Field(None, max_length=2)
    address_zip: Optional[str] = Field(None, max_length=10)

    # Dados bancários
    bank_code: Optional[str] = Field(None, max_length=10)
    bank_name: Optional[str] = Field(None, max_length=100)
    bank_agency: Optional[str] = Field(None, max_length=10)
    bank_agency_digit: Optional[str] = Field(None, max_length=2)
    bank_account: Optional[str] = Field(None, max_length=20)
    bank_account_digit: Optional[str] = Field(None, max_length=2)
    bank_account_type: Optional[str] = Field(None, max_length=20)
    pix_key: Optional[str] = Field(None, max_length=100)
    pix_key_type: Optional[str] = Field(None, max_length=20)

    # Condições comerciais
    payment_terms: PaymentTerms = PaymentTerms.DIAS_30
    payment_terms_days: Optional[str] = None
    credit_limit: Optional[str] = None
    discount_percentage: Optional[str] = None

    # Retenções fiscais
    withhold_iss: bool = False
    withhold_ir: bool = False
    withhold_pis: bool = False
    withhold_cofins: bool = False
    withhold_csll: bool = False
    withhold_inss: bool = False

    # Tags e observações
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class SupplierCreate(SupplierBase):
    """Schema para criação de fornecedor."""

    condominio_id: UUID


class SupplierUpdate(BaseModel):
    """Schema para atualização de fornecedor."""

    name: Optional[str] = Field(None, min_length=2, max_length=200)
    trade_name: Optional[str] = Field(None, max_length=200)
    supplier_type: Optional[SupplierType] = None
    category: Optional[SupplierCategory] = None
    status: Optional[SupplierStatus] = None
    cpf_cnpj: Optional[str] = Field(None, max_length=18)

    # Contato
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=200)

    # Contato principal
    contact_name: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_position: Optional[str] = Field(None, max_length=50)

    # Endereço
    address_street: Optional[str] = Field(None, max_length=200)
    address_number: Optional[str] = Field(None, max_length=20)
    address_complement: Optional[str] = Field(None, max_length=100)
    address_neighborhood: Optional[str] = Field(None, max_length=100)
    address_city: Optional[str] = Field(None, max_length=100)
    address_state: Optional[str] = Field(None, max_length=2)
    address_zip: Optional[str] = Field(None, max_length=10)

    # Dados bancários
    bank_code: Optional[str] = Field(None, max_length=10)
    bank_name: Optional[str] = Field(None, max_length=100)
    bank_agency: Optional[str] = Field(None, max_length=10)
    bank_account: Optional[str] = Field(None, max_length=20)
    pix_key: Optional[str] = Field(None, max_length=100)
    pix_key_type: Optional[str] = Field(None, max_length=20)

    # Condições comerciais
    payment_terms: Optional[PaymentTerms] = None
    credit_limit: Optional[str] = None
    discount_percentage: Optional[str] = None

    # Retenções fiscais
    withhold_iss: Optional[bool] = None
    withhold_ir: Optional[bool] = None
    withhold_pis: Optional[bool] = None
    withhold_cofins: Optional[bool] = None
    withhold_csll: Optional[bool] = None
    withhold_inss: Optional[bool] = None

    # Tags e observações
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class SupplierResponse(SupplierBase):
    """Schema de resposta para fornecedor."""

    id: UUID
    condominio_id: UUID
    code: Optional[str] = None
    status: SupplierStatus
    is_qualified: bool = False
    qualified_at: Optional[datetime] = None
    is_blocked: bool = False
    blocked_reason: Optional[str] = None
    blocked_at: Optional[datetime] = None
    rating: Optional[str] = None
    rating_count: str = "0"
    full_address: Optional[str] = None
    bank_info: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:  # pylint: disable=too-few-public-methods
        """Configuração do schema."""

        from_attributes = True


class SupplierListResponse(BaseModel):
    """Schema de lista de fornecedores."""

    id: UUID
    code: Optional[str] = None
    name: str
    trade_name: Optional[str] = None
    supplier_type: str
    category: Optional[str] = None
    status: str
    cpf_cnpj: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_qualified: bool = False
    is_blocked: bool = False
    rating: Optional[str] = None

    class Config:  # pylint: disable=too-few-public-methods
        """Configuração do schema."""

        from_attributes = True


class SupplierFilter(BaseModel):
    """Filtros para busca de fornecedores."""

    search: Optional[str] = None  # Busca em nome, cpf_cnpj, email
    supplier_type: Optional[SupplierType] = None
    category: Optional[SupplierCategory] = None
    status: Optional[SupplierStatus] = None
    is_qualified: Optional[bool] = None
    is_blocked: Optional[bool] = None
    city: Optional[str] = None
    state: Optional[str] = None
    tags: Optional[List[str]] = None


class SupplierStats(BaseModel):
    """Estatísticas de fornecedores."""

    total: int = 0
    ativos: int = 0
    inativos: int = 0
    bloqueados: int = 0
    qualificados: int = 0
    por_tipo: dict = Field(default_factory=dict)
    por_categoria: dict = Field(default_factory=dict)


class SupplierBlockRequest(BaseModel):
    """Request para bloquear fornecedor."""

    reason: str = Field(..., min_length=5, max_length=500)


class SupplierQualifyRequest(BaseModel):
    """Request para qualificar fornecedor."""

    notes: Optional[str] = Field(None, max_length=500)
