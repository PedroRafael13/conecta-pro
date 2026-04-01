"""
Models SQLAlchemy para o módulo de Onboarding Digital.

Este módulo define as entidades de banco de dados para gerenciamento
do processo de integração de novos funcionários, incluindo checklists,
etapas e acompanhamento de progresso.

Classes:
    StepType: Enum com tipos de etapas do onboarding
    ProgressStatus: Enum com status de progresso das etapas
    OnboardingChecklist: Modelo de checklist de onboarding
    OnboardingStep: Modelo de etapa do onboarding
    OnboardingProgress: Modelo de progresso do funcionário
"""

import uuid
from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    pass  # Para evitar imports circulares


class StepType(StrEnum):
    """
    Tipos de etapa do processo de onboarding.

    Attributes:
        DOCUMENTO: Entrega ou assinatura de documentos
        TREINAMENTO: Participação em treinamentos
        FEEDBACK: Sessões de feedback com supervisor
        TAREFA: Tarefas específicas a serem realizadas
        INTEGRACAO: Atividades de integração com a equipe
        CONFIGURACAO: Configurações de acesso e sistemas
        AVALIACAO: Avaliações de conhecimento
    """

    DOCUMENTO = "documento"
    TREINAMENTO = "treinamento"
    FEEDBACK = "feedback"
    TAREFA = "tarefa"
    INTEGRACAO = "integracao"
    CONFIGURACAO = "configuracao"
    AVALIACAO = "avaliacao"


class ProgressStatus(StrEnum):
    """
    Status de progresso de uma etapa do onboarding.

    Attributes:
        PENDENTE: Etapa ainda não iniciada
        EM_ANDAMENTO: Etapa em execução
        CONCLUIDO: Etapa finalizada com sucesso
        ATRASADO: Etapa passou da data prevista
        CANCELADO: Etapa foi cancelada
        BLOQUEADO: Etapa bloqueada por dependência
    """

    PENDENTE = "pendente"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDO = "concluido"
    ATRASADO = "atrasado"
    CANCELADO = "cancelado"
    BLOQUEADO = "bloqueado"


class OnboardingChecklist(Base):
    """
    Modelo de checklist de onboarding.

    Define um template de checklist que pode ser associado a cargos
    específicos ou ser genérico para toda a organização.

    Attributes:
        id: Identificador único UUID
        nome: Nome do checklist
        descricao: Descrição detalhada do checklist
        cargo_id: ID do cargo associado (opcional)
        departamento: Departamento associado (opcional)
        condominium_id: ID do condomínio/empresa
        dias_duracao_total: Duração total esperada em dias
        is_active: Se o checklist está ativo
        is_default: Se é o checklist padrão
        metadata: Dados adicionais em JSON
        created_at: Data de criação
        updated_at: Data de atualização
        deleted_at: Data de exclusão (soft delete)
        etapas: Relacionamento com as etapas do checklist
    """

    __tablename__ = "onboarding_checklists"
    __table_args__ = (
        UniqueConstraint(
            "nome",
            "condominium_id",
            name="uq_onboarding_checklist_nome_condominium",
        ),
        CheckConstraint(
            "dias_duracao_total >= 1",
            name="ck_onboarding_checklist_duracao_minima",
        ),
        {"schema": "retention"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único do checklist",
    )
    nome: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="Nome do checklist de onboarding",
    )
    descricao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descrição detalhada do checklist",
    )
    cargo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID do cargo associado (FK externa)",
    )
    departamento: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Departamento associado ao checklist",
    )
    condominium_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="ID do condomínio/empresa (FK externa)",
    )
    dias_duracao_total: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=90,
        comment="Duração total esperada do onboarding em dias",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Indica se o checklist está ativo",
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Indica se é o checklist padrão do condomínio",
    )
    metadata_info: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Metadados adicionais em formato JSON",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Data e hora de criação do registro",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Data e hora da última atualização",
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Data e hora da exclusão lógica",
    )

    # Relationships
    etapas: Mapped[list["OnboardingStep"]] = relationship(
        "OnboardingStep",
        back_populates="checklist",
        cascade="all, delete-orphan",
        order_by="OnboardingStep.ordem",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Representação textual do objeto."""
        return f"<OnboardingChecklist(id={self.id}, nome='{self.nome}')>"

    def soft_delete(self) -> None:
        """Realiza exclusão lógica do checklist."""
        self.deleted_at = datetime.utcnow()
        self.is_active = False

    def restore(self) -> None:
        """Restaura um checklist excluído."""
        self.deleted_at = None
        self.is_active = True

    @property
    def total_etapas(self) -> int:
        """Retorna o número total de etapas do checklist."""
        return len(self.etapas) if self.etapas else 0

    @property
    def etapas_obrigatorias(self) -> int:
        """Retorna o número de etapas obrigatórias."""
        if not self.etapas:
            return 0
        return sum(1 for etapa in self.etapas if etapa.obrigatorio)


class OnboardingStep(Base):
    """
    Modelo de etapa do processo de onboarding.

    Define uma etapa específica dentro de um checklist de onboarding,
    com informações sobre prazo, tipo e obrigatoriedade.

    Attributes:
        id: Identificador único UUID
        checklist_id: ID do checklist pai
        nome: Nome da etapa
        descricao: Descrição detalhada da etapa
        dias_apos_admissao: Dias após admissão para conclusão
        tipo: Tipo da etapa (documento, treinamento, etc)
        obrigatorio: Se a etapa é obrigatória
        ordem: Ordem de exibição da etapa
        responsavel_padrao_id: ID do responsável padrão
        recursos: Lista de recursos necessários
        instrucoes: Instruções detalhadas para execução
        link_material: Link para material de apoio
        tempo_estimado_minutos: Tempo estimado em minutos
        permite_pular: Se permite pular a etapa
        notificar_supervisor: Se deve notificar o supervisor
        notificar_rh: Se deve notificar o RH
        metadata: Dados adicionais em JSON
        created_at: Data de criação
        updated_at: Data de atualização
        checklist: Relacionamento com o checklist pai
        progressos: Relacionamento com os progressos
    """

    __tablename__ = "onboarding_steps"
    __table_args__ = (
        UniqueConstraint(
            "checklist_id",
            "ordem",
            name="uq_onboarding_step_checklist_ordem",
        ),
        CheckConstraint(
            "dias_apos_admissao >= 0",
            name="ck_onboarding_step_dias_positivos",
        ),
        CheckConstraint(
            "ordem >= 1",
            name="ck_onboarding_step_ordem_minima",
        ),
        CheckConstraint(
            "tempo_estimado_minutos >= 0",
            name="ck_onboarding_step_tempo_positivo",
        ),
        {"schema": "retention"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único da etapa",
    )
    checklist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "retention.onboarding_checklists.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
        comment="ID do checklist pai",
    )
    nome: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nome da etapa do onboarding",
    )
    descricao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descrição detalhada da etapa",
    )
    dias_apos_admissao: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Dias após admissão para conclusão da etapa",
    )
    tipo: Mapped[StepType] = mapped_column(
        Enum(StepType, name="step_type_enum", schema="retention"),
        nullable=False,
        default=StepType.TAREFA,
        index=True,
        comment="Tipo da etapa do onboarding",
    )
    obrigatorio: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Indica se a etapa é obrigatória",
    )
    ordem: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Ordem de exibição da etapa no checklist",
    )
    responsavel_padrao_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID do responsável padrão pela etapa (FK externa)",
    )
    recursos: Mapped[list[str] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Lista de recursos necessários para a etapa",
    )
    instrucoes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Instruções detalhadas para execução da etapa",
    )
    link_material: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Link para material de apoio",
    )
    tempo_estimado_minutos: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=60,
        comment="Tempo estimado para conclusão em minutos",
    )
    permite_pular: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Indica se a etapa pode ser pulada",
    )
    notificar_supervisor: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Notificar supervisor ao concluir/atrasar",
    )
    notificar_rh: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Notificar RH ao concluir/atrasar",
    )
    dependencia_step_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "retention.onboarding_steps.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        comment="ID da etapa que deve ser concluída antes",
    )
    metadata_info: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Metadados adicionais em formato JSON",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Data e hora de criação do registro",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Data e hora da última atualização",
    )

    # Relationships
    checklist: Mapped["OnboardingChecklist"] = relationship(
        "OnboardingChecklist",
        back_populates="etapas",
    )
    progressos: Mapped[list["OnboardingProgress"]] = relationship(
        "OnboardingProgress",
        back_populates="step",
        cascade="all, delete-orphan",
    )
    dependencia: Mapped[Optional["OnboardingStep"]] = relationship(
        "OnboardingStep",
        remote_side=[id],  # noqa: A003
        foreign_keys=[dependencia_step_id],
    )

    def __repr__(self) -> str:
        """Representação textual do objeto."""
        return f"<OnboardingStep(id={self.id}, nome='{self.nome}', ordem={self.ordem})>"

    @property
    def tem_dependencia(self) -> bool:
        """Verifica se a etapa tem dependência de outra."""
        return self.dependencia_step_id is not None


class OnboardingProgress(Base):
    """
    Modelo de progresso do onboarding de um funcionário.

    Registra o acompanhamento de cada etapa do onboarding para
    um funcionário específico, incluindo status, datas e observações.

    Attributes:
        id: Identificador único UUID
        funcionario_id: ID do funcionário
        checklist_id: ID do checklist associado
        step_id: ID da etapa
        status: Status atual do progresso
        data_prevista: Data prevista para conclusão
        data_inicio: Data de início da etapa
        data_conclusao: Data de conclusão efetiva
        observacoes: Observações sobre o progresso
        supervisor_id: ID do supervisor responsável
        responsavel_id: ID do responsável pela execução
        notificacoes_enviadas: Contador de notificações
        ultima_notificacao_at: Data da última notificação
        evidencia_url: URL da evidência de conclusão
        avaliacao_nota: Nota de avaliação (se aplicável)
        avaliacao_comentario: Comentário da avaliação
        metadata: Dados adicionais em JSON
        created_at: Data de criação
        updated_at: Data de atualização
        step: Relacionamento com a etapa
    """

    __tablename__ = "onboarding_progress"
    __table_args__ = (
        UniqueConstraint(
            "funcionario_id",
            "step_id",
            name="uq_onboarding_progress_funcionario_step",
        ),
        CheckConstraint(
            "notificacoes_enviadas >= 0",
            name="ck_onboarding_progress_notif_positivas",
        ),
        CheckConstraint(
            "avaliacao_nota IS NULL OR (avaliacao_nota >= 0 AND avaliacao_nota <= 10)",
            name="ck_onboarding_progress_nota_valida",
        ),
        {"schema": "retention"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único do progresso",
    )
    funcionario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="ID do funcionário em onboarding (FK externa)",
    )
    checklist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "retention.onboarding_checklists.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
        comment="ID do checklist associado",
    )
    step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "retention.onboarding_steps.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
        comment="ID da etapa do onboarding",
    )
    status: Mapped[ProgressStatus] = mapped_column(
        Enum(ProgressStatus, name="progress_status_enum", schema="retention"),
        nullable=False,
        default=ProgressStatus.PENDENTE,
        index=True,
        comment="Status atual do progresso da etapa",
    )
    data_prevista: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Data prevista para conclusão da etapa",
    )
    data_inicio: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data e hora de início da etapa",
    )
    data_conclusao: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data e hora de conclusão da etapa",
    )
    observacoes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observações sobre o progresso da etapa",
    )
    supervisor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID do supervisor responsável (FK externa)",
    )
    responsavel_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID do responsável pela execução (FK externa)",
    )
    notificacoes_enviadas: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Quantidade de notificações enviadas",
    )
    ultima_notificacao_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data e hora da última notificação enviada",
    )
    evidencia_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="URL da evidência de conclusão da etapa",
    )
    avaliacao_nota: Mapped[float | None] = mapped_column(
        nullable=True,
        comment="Nota de avaliação da etapa (0-10)",
    )
    avaliacao_comentario: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Comentário da avaliação da etapa",
    )
    metadata_info: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Metadados adicionais em formato JSON",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Data e hora de criação do registro",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Data e hora da última atualização",
    )

    # Relationships
    step: Mapped["OnboardingStep"] = relationship(
        "OnboardingStep",
        back_populates="progressos",
    )
    checklist: Mapped["OnboardingChecklist"] = relationship(
        "OnboardingChecklist",
        foreign_keys=[checklist_id],
    )

    def __repr__(self) -> str:
        """Representação textual do objeto."""
        return f"<OnboardingProgress(id={self.id}, funcionario_id={self.funcionario_id}, status='{self.status.value}')>"

    def iniciar(self) -> None:
        """Marca a etapa como em andamento."""
        if self.status == ProgressStatus.PENDENTE:
            self.status = ProgressStatus.EM_ANDAMENTO
            self.data_inicio = datetime.utcnow()

    def concluir(self, observacoes: str | None = None) -> None:
        """
        Marca a etapa como concluída.

        Args:
            observacoes: Observações opcionais sobre a conclusão
        """
        self.status = ProgressStatus.CONCLUIDO
        self.data_conclusao = datetime.utcnow()
        if observacoes:
            self.observacoes = observacoes

    def marcar_atrasado(self) -> None:
        """Marca a etapa como atrasada."""
        if self.status not in (ProgressStatus.CONCLUIDO, ProgressStatus.CANCELADO):
            self.status = ProgressStatus.ATRASADO

    def cancelar(self, motivo: str | None = None) -> None:
        """
        Cancela a etapa.

        Args:
            motivo: Motivo do cancelamento
        """
        self.status = ProgressStatus.CANCELADO
        if motivo:
            self.observacoes = f"CANCELADO: {motivo}"

    def registrar_notificacao(self) -> None:
        """Registra o envio de uma notificação."""
        self.notificacoes_enviadas += 1
        self.ultima_notificacao_at = datetime.utcnow()

    def avaliar(self, nota: float, comentario: str | None = None) -> None:
        """
        Registra avaliação da etapa.

        Args:
            nota: Nota de 0 a 10
            comentario: Comentário opcional da avaliação

        Raises:
            ValueError: Se a nota for inválida
        """
        if not 0 <= nota <= 10:
            raise ValueError("A nota deve estar entre 0 e 10")
        self.avaliacao_nota = nota
        if comentario:
            self.avaliacao_comentario = comentario

    @property
    def dias_restantes(self) -> int:
        """Calcula dias restantes até a data prevista."""
        if self.status == ProgressStatus.CONCLUIDO:
            return 0
        delta = self.data_prevista - date.today()
        return delta.days

    @property
    def esta_atrasado(self) -> bool:
        """Verifica se a etapa está atrasada."""
        if self.status == ProgressStatus.CONCLUIDO:
            return False
        return date.today() > self.data_prevista

    @property
    def tempo_execucao_dias(self) -> int | None:
        """Calcula o tempo de execução em dias."""
        if self.data_inicio and self.data_conclusao:
            delta = self.data_conclusao - self.data_inicio
            return delta.days
        return None
