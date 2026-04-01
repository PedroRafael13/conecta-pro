"""
Schemas Pydantic para o modulo de Medidas Administrativas.

Define todas as validacoes de entrada e saida para:
- DisciplinaryAction (medidas disciplinares)
- DisciplinaryTemplate (templates de documentos)
- DigitalSignature (assinaturas digitais)
- Workflow (submissao, aprovacao, assinatura)
- AI Advisor (recomendacoes)

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

import re
from datetime import date, datetime
from enum import StrEnum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# =============================================================================
# ENUMS
# =============================================================================


class DisciplinaryActionType(StrEnum):
    """Tipo de medida disciplinar conforme CLT."""

    ADVERTENCIA_VERBAL = "advertencia_verbal"
    ADVERTENCIA_ESCRITA = "advertencia_escrita"
    SUSPENSAO = "suspensao"
    DEMISSAO_JUSTA_CAUSA = "demissao_justa_causa"


class DisciplinaryActionStatus(StrEnum):
    """Status do fluxo da medida disciplinar."""

    RASCUNHO = "rascunho"
    PENDENTE_APROVACAO = "pendente_aprovacao"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    PENDENTE_ASSINATURA = "pendente_assinatura"
    ASSINADA = "assinada"
    RECUSADA_ASSINATURA = "recusada_assinatura"
    APLICADA = "aplicada"
    CANCELADA = "cancelada"


class ReasonCategory(StrEnum):
    """Categoria do motivo da medida disciplinar conforme CLT Art. 482."""

    FALTA = "falta"
    ATRASO = "atraso"
    INSUBORDINACAO = "insubordinacao"
    INDISCIPLINA = "indisciplina"
    DANO_PATRIMONIO = "dano_patrimonio"
    NEGLIGENCIA = "negligencia"
    EMBRIAGUEZ = "embriaguez"
    ABANDONO_EMPREGO = "abandono_emprego"
    ATO_IMPROBIDADE = "ato_improbidade"
    VIOLACAO_SEGREDO = "violacao_segredo"
    DESISTENCIA_HABITUAL = "desistencia_habitual"
    OFENSA_FISICA = "ofensa_fisica"
    OFENSA_MORAL = "ofensa_moral"
    JOGOS_AZAR = "jogos_azar"
    PERDA_HABILITACAO = "perda_habilitacao"
    OUTROS = "outros"


class SignerType(StrEnum):
    """Tipo de signatario."""

    EMPLOYEE = "employee"
    SUPERVISOR = "supervisor"
    HR = "hr"
    WITNESS = "witness"
    MANAGER = "manager"
    DIRECTOR = "director"


# =============================================================================
# DISCIPLINARY ACTION SCHEMAS
# =============================================================================


class DisciplinaryActionBase(BaseModel):
    """Schema base para DisciplinaryAction."""

    action_type: DisciplinaryActionType = Field(
        ...,
        description="Tipo da medida disciplinar",
    )
    employee_id: str = Field(
        ...,
        description="ID do funcionario (UUID)",
    )
    employee_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome completo do funcionario",
    )
    employee_cpf: str = Field(
        ...,
        min_length=11,
        max_length=14,
        description="CPF do funcionario",
    )
    employee_position: str | None = Field(
        None,
        max_length=100,
        description="Cargo do funcionario",
    )
    employee_admission_date: date | None = Field(
        None,
        description="Data de admissao",
    )
    post_id: str | None = Field(
        None,
        description="ID do posto onde ocorreu",
    )
    client_id: str | None = Field(
        None,
        description="ID do cliente",
    )
    reason_category: ReasonCategory = Field(
        ...,
        description="Categoria do motivo",
    )
    reason_description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Descricao detalhada do motivo",
    )
    occurrence_id: str | None = Field(
        None,
        description="ID da ocorrencia relacionada",
    )
    incident_date: date = Field(
        ...,
        description="Data do incidente",
    )

    @field_validator("employee_cpf")
    @classmethod
    def validate_cpf(cls, v: str) -> str:
        """Valida e formata CPF."""
        # Remove caracteres nao numericos
        digits = re.sub(r"\D", "", v)
        if len(digits) != 11:
            raise ValueError("CPF deve ter 11 digitos")
        # Formata como XXX.XXX.XXX-XX
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"

    @field_validator("incident_date")
    @classmethod
    def validate_incident_date(cls, v: date) -> date:
        """Valida que data do incidente nao e futura."""
        if v > date.today():
            raise ValueError("Data do incidente nao pode ser futura")
        return v


class DisciplinaryActionCreate(DisciplinaryActionBase):
    """Schema para criacao de DisciplinaryAction."""

    # Campos opcionais para suspensao
    suspension_start_date: date | None = Field(
        None,
        description="Data inicio da suspensao",
    )
    suspension_end_date: date | None = Field(
        None,
        description="Data fim da suspensao",
    )
    suspension_days: int | None = Field(
        None,
        ge=1,
        le=30,
        description="Dias de suspensao (max 30 CLT)",
    )

    # Testemunhas
    witness_1_name: str | None = Field(
        None,
        max_length=255,
        description="Nome da primeira testemunha",
    )
    witness_1_cpf: str | None = Field(
        None,
        description="CPF da primeira testemunha",
    )
    witness_2_name: str | None = Field(
        None,
        max_length=255,
        description="Nome da segunda testemunha",
    )
    witness_2_cpf: str | None = Field(
        None,
        description="CPF da segunda testemunha",
    )

    # Template
    document_template_id: str | None = Field(
        None,
        description="ID do template para gerar documento",
    )

    # Configuracao
    requires_approval: bool = Field(
        default=True,
        description="Se requer aprovacao de superior",
    )

    @model_validator(mode="after")
    def validate_suspension_fields(self) -> "DisciplinaryActionCreate":
        """Valida campos de suspensao."""
        if self.action_type == DisciplinaryActionType.SUSPENSAO:
            if not self.suspension_days:
                raise ValueError("Suspensao requer numero de dias")
            if self.suspension_days > 30:
                raise ValueError("Suspensao nao pode exceder 30 dias (CLT)")
            if self.suspension_start_date and self.suspension_end_date:
                if self.suspension_end_date <= self.suspension_start_date:
                    raise ValueError("Data fim deve ser posterior a data inicio")
        return self

    @field_validator("witness_1_cpf", "witness_2_cpf")
    @classmethod
    def validate_witness_cpf(cls, v: str | None) -> str | None:
        """Valida e formata CPF de testemunha."""
        if v is None:
            return v
        digits = re.sub(r"\D", "", v)
        if len(digits) != 11:
            raise ValueError("CPF deve ter 11 digitos")
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


class DisciplinaryActionUpdate(BaseModel):
    """Schema para atualizacao parcial de DisciplinaryAction."""

    action_type: DisciplinaryActionType | None = None
    reason_category: ReasonCategory | None = None
    reason_description: str | None = Field(None, min_length=10, max_length=5000)
    incident_date: date | None = None
    post_id: str | None = None
    client_id: str | None = None
    occurrence_id: str | None = None
    suspension_start_date: date | None = None
    suspension_end_date: date | None = None
    suspension_days: int | None = Field(None, ge=1, le=30)
    witness_1_name: str | None = Field(None, max_length=255)
    witness_1_cpf: str | None = None
    witness_2_name: str | None = Field(None, max_length=255)
    witness_2_cpf: str | None = None
    document_template_id: str | None = None
    requires_approval: bool | None = None


class DisciplinaryActionResponse(BaseModel):
    """Schema de resposta para DisciplinaryAction."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    tenant_id: str
    action_type: str
    status: str
    employee_id: str
    employee_name: str
    employee_cpf: str
    employee_position: str | None
    employee_admission_date: date | None
    post_id: str | None
    client_id: str | None
    reason_category: str
    reason_description: str
    occurrence_id: str | None
    incident_date: date
    application_date: date | None
    suspension_start_date: date | None
    suspension_end_date: date | None
    suspension_days: int | None
    witness_1_name: str | None
    witness_1_cpf: str | None
    witness_2_name: str | None
    witness_2_cpf: str | None
    requires_approval: bool
    approved_by_id: str | None
    approved_at: datetime | None
    approval_notes: str | None
    rejected_by_id: str | None
    rejected_at: datetime | None
    rejection_reason: str | None
    employee_signed_at: datetime | None
    employee_refused_sign: bool
    supervisor_signed_at: datetime | None
    hr_signed_at: datetime | None
    employee_acknowledged: bool
    acknowledged_at: datetime | None
    previous_warnings_count: int
    previous_suspensions_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: str | None

    # Campos calculados
    type_display_name: str
    status_display_name: str
    can_be_edited: bool
    can_be_submitted: bool
    can_be_approved: bool
    can_be_signed: bool


class DisciplinaryActionDetailResponse(DisciplinaryActionResponse):
    """Schema de resposta detalhada incluindo documento e assinaturas."""

    document_text: str | None
    document_hash: str | None
    document_template_id: str | None

    # Assinaturas expandidas (quando carregadas)
    employee_signature: Optional["SignatureResponse"] = None
    supervisor_signature: Optional["SignatureResponse"] = None
    hr_signature: Optional["SignatureResponse"] = None


class DisciplinaryActionListResponse(BaseModel):
    """Schema para listagem paginada de DisciplinaryActions."""

    items: list[DisciplinaryActionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DisciplinaryFilter(BaseModel):
    """Schema para filtros de busca de DisciplinaryActions."""

    action_type: DisciplinaryActionType | None = None
    status: DisciplinaryActionStatus | None = None
    reason_category: ReasonCategory | None = None
    employee_id: str | None = None
    post_id: str | None = None
    client_id: str | None = None
    incident_date_from: date | None = None
    incident_date_to: date | None = None
    created_at_from: datetime | None = None
    created_at_to: datetime | None = None
    search: str | None = Field(
        None,
        description="Busca por codigo, nome do funcionario ou descricao",
    )


class DisciplinaryStats(BaseModel):
    """Estatisticas de medidas disciplinares."""

    total: int
    by_type: dict[str, int]
    by_status: dict[str, int]
    by_reason_category: dict[str, int]
    pending_approval: int
    pending_signature: int
    applied_this_month: int
    applied_this_year: int
    employees_with_warnings: int
    employees_with_suspensions: int


# =============================================================================
# WORKFLOW SCHEMAS
# =============================================================================


class SubmitForApprovalRequest(BaseModel):
    """Request para submeter medida para aprovacao."""

    notes: str | None = Field(
        None,
        max_length=500,
        description="Notas adicionais para o aprovador",
    )


class ApproveRequest(BaseModel):
    """Request para aprovar medida disciplinar."""

    notes: str | None = Field(
        None,
        max_length=500,
        description="Notas da aprovacao",
    )
    application_date: date | None = Field(
        None,
        description="Data de aplicacao (default: hoje)",
    )


class RejectRequest(BaseModel):
    """Request para rejeitar medida disciplinar."""

    reason: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Motivo da rejeicao",
    )


class SignRequest(BaseModel):
    """Request para assinar documento."""

    signer_type: SignerType = Field(
        ...,
        description="Tipo de signatario",
    )
    signature_data: str = Field(
        ...,
        min_length=100,
        description="Dados da assinatura em Base64",
    )
    ip_address: str | None = Field(
        None,
        description="IP de onde foi assinado",
    )
    user_agent: str | None = Field(
        None,
        max_length=500,
        description="User-Agent do navegador",
    )
    latitude: float | None = Field(
        None,
        ge=-90,
        le=90,
        description="Latitude",
    )
    longitude: float | None = Field(
        None,
        ge=-180,
        le=180,
        description="Longitude",
    )
    geolocation_accuracy: float | None = Field(
        None,
        ge=0,
        description="Precisao da geolocalizacao em metros",
    )


class RefuseSignRequest(BaseModel):
    """Request para registrar recusa de assinatura."""

    # Testemunhas obrigatorias para advertencia escrita
    witness_1_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome da primeira testemunha",
    )
    witness_1_cpf: str = Field(
        ...,
        description="CPF da primeira testemunha",
    )
    witness_2_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome da segunda testemunha",
    )
    witness_2_cpf: str = Field(
        ...,
        description="CPF da segunda testemunha",
    )

    @field_validator("witness_1_cpf", "witness_2_cpf")
    @classmethod
    def validate_cpf(cls, v: str) -> str:
        """Valida e formata CPF."""
        digits = re.sub(r"\D", "", v)
        if len(digits) != 11:
            raise ValueError("CPF deve ter 11 digitos")
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


class GenerateDocumentRequest(BaseModel):
    """Request para gerar documento a partir de template."""

    template_id: str | None = Field(
        None,
        description="ID do template (usa padrao se nao informado)",
    )
    extra_context: dict[str, Any] | None = Field(
        None,
        description="Contexto adicional para placeholders",
    )


class GenerateDocumentResponse(BaseModel):
    """Response da geracao de documento."""

    document_text: str
    document_hash: str
    template_id: str
    generated_at: datetime
    placeholders_used: list[str]


# =============================================================================
# TEMPLATE SCHEMAS
# =============================================================================


class TemplateBase(BaseModel):
    """Schema base para DisciplinaryTemplate."""

    action_type: DisciplinaryActionType = Field(
        ...,
        description="Tipo de medida que este template atende",
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome do template",
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="Descricao do template",
    )
    content: str = Field(
        ...,
        min_length=100,
        description="Conteudo do template com placeholders {{...}}",
    )
    is_default: bool = Field(
        default=False,
        description="Se e o template padrao para este tipo",
    )


class TemplateCreate(TemplateBase):
    """Schema para criacao de Template."""

    pass


class TemplateUpdate(BaseModel):
    """Schema para atualizacao de Template."""

    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = Field(None, max_length=500)
    content: str | None = Field(None, min_length=100)
    is_default: bool | None = None
    is_active: bool | None = None


class TemplateResponse(BaseModel):
    """Schema de resposta para Template."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    action_type: str
    name: str
    description: str | None
    content: str
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: str | None

    # Campos calculados
    placeholder_list: list[str]


class TemplateListResponse(BaseModel):
    """Schema para listagem de Templates."""

    items: list[TemplateResponse]
    total: int


# =============================================================================
# SIGNATURE SCHEMAS
# =============================================================================


class SignatureBase(BaseModel):
    """Schema base para DigitalSignature."""

    signer_type: SignerType = Field(
        ...,
        description="Tipo de signatario",
    )
    document_type: str = Field(
        ...,
        description="Tipo do documento",
    )
    document_id: str = Field(
        ...,
        description="ID do documento",
    )
    signature_data: str = Field(
        ...,
        min_length=100,
        description="Dados da assinatura em Base64",
    )


class SignatureCreate(SignatureBase):
    """Schema para criacao de Signature."""

    signer_id: str = Field(
        ...,
        description="ID do usuario que assina",
    )
    signer_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome do signatario",
    )
    signer_cpf: str | None = Field(
        None,
        description="CPF do signatario",
    )
    signer_email: str | None = Field(
        None,
        max_length=255,
        description="Email do signatario",
    )
    signature_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="Hash SHA-256 do documento",
    )
    ip_address: str | None = None
    user_agent: str | None = Field(None, max_length=500)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    geolocation_accuracy: float | None = Field(None, ge=0)


class SignatureResponse(BaseModel):
    """Schema de resposta para Signature."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    signer_id: str
    signer_type: str
    signer_name: str
    signer_cpf: str | None
    signer_email: str | None
    document_type: str
    document_id: str
    signature_hash: str
    ip_address: str | None
    user_agent: str | None
    latitude: float | None
    longitude: float | None
    geolocation_accuracy: float | None
    is_valid: bool
    validated_at: datetime | None
    invalidated_at: datetime | None
    invalidation_reason: str | None
    created_at: datetime

    # Campos calculados
    has_geolocation: bool
    signer_type_display_name: str


class SignatureVerifyRequest(BaseModel):
    """Request para verificar assinatura."""

    signature_id: str = Field(
        ...,
        description="ID da assinatura",
    )
    document_content: str = Field(
        ...,
        description="Conteudo atual do documento para verificar hash",
    )


class SignatureVerifyResponse(BaseModel):
    """Response da verificacao de assinatura."""

    is_valid: bool
    hash_matches: bool
    signature_date: datetime
    signer_name: str
    signer_type: str
    message: str


# =============================================================================
# AI ADVISOR SCHEMAS
# =============================================================================


class RecommendationRequest(BaseModel):
    """Request para obter recomendacao de medida."""

    employee_id: str = Field(
        ...,
        description="ID do funcionario",
    )
    reason_category: ReasonCategory = Field(
        ...,
        description="Categoria do motivo",
    )
    reason_description: str = Field(
        ...,
        min_length=10,
        description="Descricao do incidente",
    )
    incident_date: date = Field(
        ...,
        description="Data do incidente",
    )


class RecommendationResponse(BaseModel):
    """Response com recomendacao de medida."""

    recommended_action: DisciplinaryActionType
    confidence_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Score de confianca (0-1)",
    )
    reasoning: str
    previous_warnings: int
    previous_suspensions: int
    last_incident_date: date | None
    alternative_actions: list[DisciplinaryActionType]
    legal_references: list[str]


class LegalComplianceRequest(BaseModel):
    """Request para validar conformidade legal."""

    action_type: DisciplinaryActionType
    reason_category: ReasonCategory
    reason_description: str
    incident_date: date
    application_date: date
    suspension_days: int | None = None
    previous_warnings: int = 0
    previous_suspensions: int = 0


class LegalComplianceResponse(BaseModel):
    """Response da validacao de conformidade legal."""

    is_compliant: bool
    issues: list[str]
    warnings: list[str]
    recommendations: list[str]
    clt_articles: list[str]


class ProportionalityCheckRequest(BaseModel):
    """Request para verificar proporcionalidade."""

    action_type: DisciplinaryActionType
    reason_category: ReasonCategory
    previous_warnings: int
    previous_suspensions: int
    employee_tenure_days: int


class ProportionalityCheckResponse(BaseModel):
    """Response da verificacao de proporcionalidade."""

    is_proportional: bool
    score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Score de proporcionalidade (0-1)",
    )
    analysis: str
    suggested_action: DisciplinaryActionType | None
    reasoning: str


# =============================================================================
# REBUILD MODELS COM FORWARD REFERENCES
# =============================================================================

# Necessario para resolver forward references entre classes
DisciplinaryActionDetailResponse.model_rebuild()
