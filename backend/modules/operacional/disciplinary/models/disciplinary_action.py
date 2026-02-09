"""
Model DisciplinaryAction - Medida Administrativa/Disciplinar.

Este modelo representa todas as medidas disciplinares aplicadas a funcionarios:
- Advertencia Verbal
- Advertencia Escrita
- Suspensao
- Demissao por Justa Causa

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    from .digital_signature import DigitalSignature
    from .disciplinary_template import DisciplinaryTemplate


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


class DisciplinaryAction(Base):
    """
    Modelo de Medida Administrativa/Disciplinar.

    Representa uma medida disciplinar aplicada a um funcionario,
    seguindo as normas da CLT e com workflow completo de aprovacao
    e assinaturas digitais.

    Attributes:
        id: Identificador unico UUID
        code: Codigo unico da medida (ADV-2026-00001, SUS-2026-00001)
        tenant_id: ID do tenant (multi-tenancy)
        action_type: Tipo da medida (advertencia, suspensao, etc)
        status: Status atual no workflow
        employee_id: ID do funcionario
        employee_name: Nome do funcionario (snapshot)
        employee_cpf: CPF do funcionario (snapshot)
        employee_position: Cargo do funcionario (snapshot)
        employee_admission_date: Data admissao (snapshot)
        post_id: ID do posto onde ocorreu
        client_id: ID do cliente
        reason_category: Categoria do motivo
        reason_description: Descricao detalhada do motivo
        occurrence_id: ID da ocorrencia relacionada (opcional)
        incident_date: Data do incidente
        application_date: Data de aplicacao da medida
        suspension_start_date: Inicio da suspensao (se aplicavel)
        suspension_end_date: Fim da suspensao (se aplicavel)
        suspension_days: Dias de suspensao (max 30 CLT)
        document_text: Texto completo do documento
        document_template_id: Template usado
        document_hash: Hash SHA-256 do documento
        witness_1_name, witness_1_cpf: Primeira testemunha
        witness_2_name, witness_2_cpf: Segunda testemunha
        requires_approval: Se requer aprovacao superior
        approved_by_id: Quem aprovou
        approved_at: Quando foi aprovado
        approval_notes: Notas da aprovacao
        employee_signature_id: Assinatura do funcionario
        employee_signed_at: Quando funcionario assinou
        employee_refused_sign: Se funcionario recusou assinar
        refusal_witness_1, refusal_witness_2: Testemunhas da recusa
        supervisor_signature_id: Assinatura do supervisor
        hr_signature_id: Assinatura do RH
        employee_acknowledged: Se funcionario tomou ciencia
        acknowledged_at: Quando tomou ciencia
        previous_warnings_count: Qtd advertencias anteriores (snapshot)
        previous_suspensions_count: Qtd suspensoes anteriores (snapshot)
        ai_recommendation: Recomendacao da IA
        extra_data: Metadados adicionais
        is_active: Se registro esta ativo (soft delete)
        created_at: Data criacao
        updated_at: Data ultima atualizacao
        created_by: Usuario que criou
    """

    __tablename__ = "disciplinary_actions"

    # === Identificacao ===
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Codigo unico (ADV-2026-00001)",
    )
    tenant_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
        comment="ID do tenant para multi-tenancy",
    )

    # === Tipo e Status ===
    action_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
        comment="Tipo: advertencia_verbal, advertencia_escrita, suspensao, demissao_justa_causa",
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default=DisciplinaryActionStatus.RASCUNHO.value,
        nullable=False,
        index=True,
        comment="Status do workflow",
    )

    # === Dados do Funcionario (Snapshot) ===
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
        comment="ID do funcionario",
    )
    employee_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nome completo do funcionario (snapshot)",
    )
    employee_cpf: Mapped[str] = mapped_column(
        String(14),
        nullable=False,
        comment="CPF do funcionario (snapshot)",
    )
    employee_position: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Cargo do funcionario (snapshot)",
    )
    employee_admission_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="Data de admissao (snapshot)",
    )

    # === Local ===
    post_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
        comment="ID do posto onde ocorreu",
    )
    client_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
        comment="ID do cliente",
    )

    # === Motivo ===
    reason_category: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
        comment="Categoria do motivo (falta, atraso, insubordinacao, etc)",
    )
    reason_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Descricao detalhada do motivo",
    )
    occurrence_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        comment="ID da ocorrencia relacionada",
    )

    # === Datas ===
    incident_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Data do incidente que gerou a medida",
    )
    application_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="Data de aplicacao efetiva da medida",
    )

    # === Suspensao (se aplicavel) ===
    suspension_start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="Data inicio da suspensao",
    )
    suspension_end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="Data fim da suspensao",
    )
    suspension_days: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Quantidade de dias de suspensao (max 30 CLT)",
    )

    # === Documento ===
    document_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Texto completo do documento gerado",
    )
    document_template_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("disciplinary_templates.id"),
        nullable=True,
        comment="Template utilizado para gerar documento",
    )
    document_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="Hash SHA-256 do documento no momento da assinatura",
    )

    # === Testemunhas ===
    witness_1_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Nome da primeira testemunha",
    )
    witness_1_cpf: Mapped[str | None] = mapped_column(
        String(14),
        nullable=True,
        comment="CPF da primeira testemunha",
    )
    witness_2_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Nome da segunda testemunha",
    )
    witness_2_cpf: Mapped[str | None] = mapped_column(
        String(14),
        nullable=True,
        comment="CPF da segunda testemunha",
    )

    # === Aprovacao ===
    requires_approval: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Se requer aprovacao de superior",
    )
    approved_by_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        comment="ID de quem aprovou",
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Data/hora da aprovacao",
    )
    approval_notes: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Observacoes da aprovacao",
    )
    rejected_by_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        comment="ID de quem rejeitou",
    )
    rejected_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Data/hora da rejeicao",
    )
    rejection_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Motivo da rejeicao",
    )

    # === Assinaturas do Funcionario ===
    employee_signature_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("digital_signatures.id"),
        nullable=True,
        comment="ID da assinatura digital do funcionario",
    )
    employee_signed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Data/hora que funcionario assinou",
    )
    employee_refused_sign: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Se funcionario recusou assinar",
    )
    refusal_witness_1_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Nome testemunha 1 da recusa de assinatura",
    )
    refusal_witness_1_cpf: Mapped[str | None] = mapped_column(
        String(14),
        nullable=True,
        comment="CPF testemunha 1 da recusa",
    )
    refusal_witness_2_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Nome testemunha 2 da recusa de assinatura",
    )
    refusal_witness_2_cpf: Mapped[str | None] = mapped_column(
        String(14),
        nullable=True,
        comment="CPF testemunha 2 da recusa",
    )

    # === Outras Assinaturas ===
    supervisor_signature_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("digital_signatures.id"),
        nullable=True,
        comment="ID da assinatura do supervisor",
    )
    supervisor_signed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Data/hora que supervisor assinou",
    )
    hr_signature_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("digital_signatures.id"),
        nullable=True,
        comment="ID da assinatura do RH",
    )
    hr_signed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Data/hora que RH assinou",
    )

    # === Ciencia ===
    employee_acknowledged: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Se funcionario tomou ciencia",
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Data/hora que tomou ciencia",
    )

    # === Historico (Snapshot) ===
    previous_warnings_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Quantidade de advertencias anteriores no momento",
    )
    previous_suspensions_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Quantidade de suspensoes anteriores no momento",
    )

    # === IA e Metadados ===
    ai_recommendation: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Recomendacao da IA para esta medida",
    )
    extra_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Metadados adicionais",
    )

    # === Controle ===
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Se registro esta ativo (soft delete)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="Data de criacao",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Data ultima atualizacao",
    )
    created_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        comment="ID do usuario que criou",
    )

    # === Relacionamentos ===
    template: Mapped[Optional["DisciplinaryTemplate"]] = relationship(
        "DisciplinaryTemplate",
        foreign_keys=[document_template_id],
        lazy="selectin",
    )
    employee_signature: Mapped[Optional["DigitalSignature"]] = relationship(
        "DigitalSignature",
        foreign_keys=[employee_signature_id],
        lazy="selectin",
    )
    supervisor_signature: Mapped[Optional["DigitalSignature"]] = relationship(
        "DigitalSignature",
        foreign_keys=[supervisor_signature_id],
        lazy="selectin",
    )
    hr_signature: Mapped[Optional["DigitalSignature"]] = relationship(
        "DigitalSignature",
        foreign_keys=[hr_signature_id],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Representacao string do objeto."""
        return f"<DisciplinaryAction {self.code} - {self.action_type} - {self.status}>"

    @property
    def action_type_enum(self) -> DisciplinaryActionType:
        """Retorna o tipo como enum."""
        return DisciplinaryActionType(self.action_type)

    @property
    def status_enum(self) -> DisciplinaryActionStatus:
        """Retorna o status como enum."""
        return DisciplinaryActionStatus(self.status)

    @property
    def reason_category_enum(self) -> ReasonCategory:
        """Retorna a categoria do motivo como enum."""
        return ReasonCategory(self.reason_category)

    @property
    def is_warning(self) -> bool:
        """Verifica se e uma advertencia."""
        return self.action_type in [
            DisciplinaryActionType.ADVERTENCIA_VERBAL.value,
            DisciplinaryActionType.ADVERTENCIA_ESCRITA.value,
        ]

    @property
    def is_suspension(self) -> bool:
        """Verifica se e uma suspensao."""
        return self.action_type == DisciplinaryActionType.SUSPENSAO.value

    @property
    def is_termination(self) -> bool:
        """Verifica se e uma demissao por justa causa."""
        return self.action_type == DisciplinaryActionType.DEMISSAO_JUSTA_CAUSA.value

    @property
    def can_be_edited(self) -> bool:
        """Verifica se pode ser editado."""
        return self.status in [
            DisciplinaryActionStatus.RASCUNHO.value,
            DisciplinaryActionStatus.REJEITADA.value,
        ]

    @property
    def can_be_submitted(self) -> bool:
        """Verifica se pode ser submetido para aprovacao."""
        return self.status == DisciplinaryActionStatus.RASCUNHO.value

    @property
    def can_be_approved(self) -> bool:
        """Verifica se pode ser aprovado."""
        return self.status == DisciplinaryActionStatus.PENDENTE_APROVACAO.value

    @property
    def can_be_signed(self) -> bool:
        """Verifica se pode ser assinado."""
        return self.status in [
            DisciplinaryActionStatus.APROVADA.value,
            DisciplinaryActionStatus.PENDENTE_ASSINATURA.value,
        ]

    @property
    def requires_witnesses_for_refusal(self) -> bool:
        """Verifica se advertencia escrita requer testemunhas em caso de recusa."""
        return self.action_type == DisciplinaryActionType.ADVERTENCIA_ESCRITA.value

    @property
    def type_display_name(self) -> str:
        """Retorna nome de exibicao do tipo."""
        display_names = {
            DisciplinaryActionType.ADVERTENCIA_VERBAL.value: "Advertencia Verbal",
            DisciplinaryActionType.ADVERTENCIA_ESCRITA.value: "Advertencia Escrita",
            DisciplinaryActionType.SUSPENSAO.value: "Suspensao",
            DisciplinaryActionType.DEMISSAO_JUSTA_CAUSA.value: "Demissao por Justa Causa",
        }
        return display_names.get(self.action_type, self.action_type)

    @property
    def status_display_name(self) -> str:
        """Retorna nome de exibicao do status."""
        display_names = {
            DisciplinaryActionStatus.RASCUNHO.value: "Rascunho",
            DisciplinaryActionStatus.PENDENTE_APROVACAO.value: "Pendente Aprovacao",
            DisciplinaryActionStatus.APROVADA.value: "Aprovada",
            DisciplinaryActionStatus.REJEITADA.value: "Rejeitada",
            DisciplinaryActionStatus.PENDENTE_ASSINATURA.value: "Pendente Assinatura",
            DisciplinaryActionStatus.ASSINADA.value: "Assinada",
            DisciplinaryActionStatus.RECUSADA_ASSINATURA.value: "Recusada Assinatura",
            DisciplinaryActionStatus.APLICADA.value: "Aplicada",
            DisciplinaryActionStatus.CANCELADA.value: "Cancelada",
        }
        return display_names.get(self.status, self.status)
