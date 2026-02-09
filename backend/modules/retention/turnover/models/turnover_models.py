"""
Models para Predicao de Turnover com IA.

Este modulo implementa os modelos de banco de dados para o sistema de
predicao de turnover, incluindo predicoes, fatores de risco e alertas.

Seguranca: Score NUNCA visivel para o funcionario.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class NivelRisco(StrEnum):
    """Niveis de risco de turnover."""

    BAIXO = "baixo"  # Score < 40
    MEDIO = "medio"  # Score 40-60
    ALTO = "alto"  # Score 60-80
    CRITICO = "critico"  # Score >= 80


class TipoAlerta(StrEnum):
    """Tipos de alerta de risco."""

    NOVO_RISCO = "novo_risco"  # Primeiro score >= 70
    AUMENTO_RISCO = "aumento_risco"  # Aumento significativo no score
    RISCO_CRITICO = "risco_critico"  # Score >= 80
    MUDANCA_NIVEL = "mudanca_nivel"  # Transicao de nivel


class CategoriaFator(StrEnum):
    """Categorias dos fatores de risco."""

    COMPORTAMENTAL = "comportamental"
    ENGAJAMENTO = "engajamento"
    OPERACIONAL = "operacional"
    CONTEXTUAL = "contextual"


class TurnoverPrediction(Base, TimestampMixin, SoftDeleteMixin):
    """
    Model para predicoes de turnover.

    Armazena o calculo de risco de turnover para cada funcionario,
    incluindo score, nivel e metadados do modelo utilizado.

    Atributos:
        id: Identificador unico da predicao
        funcionario_id: ID do funcionario avaliado
        condominium_id: ID do condominio/empresa
        data_calculo: Data/hora do calculo
        score_risco: Score de 0-100 indicando probabilidade de turnover
        nivel: Nivel categorico do risco (baixo, medio, alto, critico)
        modelo_versao: Versao do modelo de predicao utilizado
        features_usadas: Features utilizadas no calculo (JSONB)
        metricas_modelo: Metricas de confianca do modelo (JSONB)
        valido_ate: Data de validade da predicao
        recalculado: Indica se foi substituido por novo calculo
        calculado_por: Usuario que solicitou o calculo (None = sistema)
    """

    __tablename__ = "turnover_predictions"
    __table_args__ = (
        Index("idx_turnover_pred_funcionario", "funcionario_id"),
        Index("idx_turnover_pred_nivel", "nivel"),
        Index("idx_turnover_pred_score", "score_risco"),
        Index("idx_turnover_pred_data", "data_calculo"),
        Index("idx_turnover_pred_condominium", "condominium_id"),
        UniqueConstraint("funcionario_id", "data_calculo", name="uq_turnover_pred_funcionario_data"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Relacionamentos principais
    funcionario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    condominium_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Dados da predicao
    data_calculo: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    score_risco: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Score de risco de 0 a 100",
    )
    nivel: Mapped[NivelRisco] = mapped_column(
        Enum(NivelRisco),
        nullable=False,
    )

    # Metadados do modelo
    modelo_versao: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="heuristic_v1.0",
    )
    features_usadas: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    metricas_modelo: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Metricas de confianca: accuracy, precision, recall",
    )

    # Validade e status
    valido_ate: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    recalculado: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Auditoria
    calculado_por: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="Usuario que solicitou calculo (None = sistema automatico)",
    )

    # Relationships
    fatores: Mapped[list["RiskFactor"]] = relationship(
        "RiskFactor",
        back_populates="prediction",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="RiskFactor.contribuicao_score.desc()",
    )
    alertas: Mapped[list["RiskAlert"]] = relationship(
        "RiskAlert",
        back_populates="prediction",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<TurnoverPrediction(id={self.id}, "
            f"funcionario={self.funcionario_id}, "
            f"score={self.score_risco}, nivel={self.nivel.value})>"
        )

    @staticmethod
    def calcular_nivel(score: float) -> NivelRisco:
        """Determina o nivel de risco baseado no score."""
        if score < 40:
            return NivelRisco.BAIXO
        if score < 60:
            return NivelRisco.MEDIO
        if score < 80:
            return NivelRisco.ALTO
        return NivelRisco.CRITICO

    @property
    def is_alerta_necessario(self) -> bool:
        """Verifica se o score justifica alerta (threshold >= 70)."""
        return float(self.score_risco) >= 70.0

    @property
    def is_critico(self) -> bool:
        """Verifica se o risco e critico."""
        return self.nivel == NivelRisco.CRITICO

    @property
    def principais_fatores(self) -> list["RiskFactor"]:
        """Retorna os 3 principais fatores de risco."""
        return sorted(self.fatores, key=lambda f: f.contribuicao_score, reverse=True)[:3]

    def marcar_recalculado(self) -> None:
        """Marca a predicao como substituida por nova."""
        self.recalculado = True


class RiskFactor(Base, TimestampMixin):
    """
    Model para fatores de risco individuais.

    Cada fator representa uma caracteristica especifica que
    contribui para o score de risco do funcionario.

    Atributos:
        id: Identificador unico do fator
        prediction_id: ID da predicao associada
        nome: Nome identificador do fator (ex: faltas_ultimo_mes)
        categoria: Categoria do fator (comportamental, engajamento, etc)
        peso: Peso configurado do fator no modelo
        valor_atual: Valor atual da feature para o funcionario
        valor_normalizado: Valor normalizado (0-1) para calculo
        contribuicao_score: Contribuicao absoluta para o score final
        threshold_violado: Se o threshold foi violado
        descricao: Descricao legivel do fator
        recomendacao_acao: Acao recomendada para mitigar
        dados_brutos: Dados brutos utilizados no calculo
    """

    __tablename__ = "turnover_risk_factors"
    __table_args__ = (
        Index("idx_risk_factor_prediction", "prediction_id"),
        Index("idx_risk_factor_nome", "nome"),
        Index("idx_risk_factor_categoria", "categoria"),
        Index("idx_risk_factor_contribuicao", "contribuicao_score"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Relacionamento
    prediction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("turnover_predictions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Identificacao do fator
    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    categoria: Mapped[CategoriaFator] = mapped_column(
        Enum(CategoriaFator),
        nullable=False,
    )

    # Valores
    peso: Mapped[Decimal] = mapped_column(
        Numeric(4, 3),
        nullable=False,
        comment="Peso do fator no calculo (0 a 1)",
    )
    valor_atual: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
        comment="Valor bruto da feature",
    )
    valor_normalizado: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
        comment="Valor normalizado de 0 a 1",
    )
    contribuicao_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Contribuicao absoluta para o score final",
    )

    # Status
    threshold_violado: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Descricoes
    descricao: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    recomendacao_acao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Dados extras
    dados_brutos: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Dados brutos usados no calculo do fator",
    )

    # Relationship
    prediction: Mapped["TurnoverPrediction"] = relationship(
        "TurnoverPrediction",
        back_populates="fatores",
    )

    def __repr__(self) -> str:
        return f"<RiskFactor(nome={self.nome}, contribuicao={self.contribuicao_score})>"

    @property
    def is_critico(self) -> bool:
        """Verifica se o fator tem contribuicao critica (>= 10 pontos)."""
        return float(self.contribuicao_score) >= 10.0

    @property
    def is_significativo(self) -> bool:
        """Verifica se o fator tem contribuicao significativa (>= 5 pontos)."""
        return float(self.contribuicao_score) >= 5.0


class RiskAlert(Base, TimestampMixin):
    """
    Model para alertas de risco.

    Armazena alertas gerados quando um funcionario atinge
    determinados thresholds de risco.

    Atributos:
        id: Identificador unico do alerta
        funcionario_id: ID do funcionario
        prediction_id: ID da predicao que gerou o alerta
        condominium_id: ID do condominio/empresa
        tipo: Tipo do alerta (novo_risco, aumento_risco, risco_critico)
        score_atual: Score no momento do alerta
        score_anterior: Score da predicao anterior
        variacao_score: Diferenca entre scores
        nivel_atual: Nivel de risco atual
        nivel_anterior: Nivel de risco anterior
        titulo: Titulo do alerta
        mensagem: Mensagem detalhada do alerta
        enviado_para: Lista de usuarios que receberam o alerta
        visualizado: Se o alerta foi visualizado
        data_visualizacao: Data/hora da visualizacao
        visualizado_por: Usuario que visualizou
        acao_tomada: Descricao da acao tomada
        acao_por: Usuario que tomou a acao
        data_acao: Data/hora da acao
        prioridade: Nivel de prioridade (1-5)
        expira_em: Data de expiracao do alerta
    """

    __tablename__ = "turnover_risk_alerts"
    __table_args__ = (
        Index("idx_risk_alert_funcionario", "funcionario_id"),
        Index("idx_risk_alert_tipo", "tipo"),
        Index("idx_risk_alert_visualizado", "visualizado"),
        Index("idx_risk_alert_condominium", "condominium_id"),
        Index("idx_risk_alert_created", "created_at"),
        Index("idx_risk_alert_pendentes", "condominium_id", "visualizado", postgresql_where="visualizado = false"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Relacionamentos principais
    funcionario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    prediction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("turnover_predictions.id", ondelete="CASCADE"),
        nullable=False,
    )
    condominium_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Dados do alerta
    tipo: Mapped[TipoAlerta] = mapped_column(
        Enum(TipoAlerta),
        nullable=False,
    )
    score_atual: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )
    score_anterior: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    variacao_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    nivel_atual: Mapped[NivelRisco] = mapped_column(
        Enum(NivelRisco),
        nullable=False,
    )
    nivel_anterior: Mapped[NivelRisco | None] = mapped_column(
        Enum(NivelRisco),
        nullable=True,
    )

    # Conteudo
    titulo: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    mensagem: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Destinatarios
    enviado_para: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        comment="Lista de UUIDs dos usuarios notificados",
    )

    # Visualizacao
    visualizado: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    data_visualizacao: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    visualizado_por: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Acao tomada
    acao_tomada: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    acao_por: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    data_acao: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Metadados
    prioridade: Mapped[int] = mapped_column(
        default=3,
        nullable=False,
        comment="Prioridade de 1 (maxima) a 5 (minima)",
    )
    expira_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    dados_extras: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Relationship
    prediction: Mapped["TurnoverPrediction"] = relationship(
        "TurnoverPrediction",
        back_populates="alertas",
    )

    def __repr__(self) -> str:
        return f"<RiskAlert(id={self.id}, tipo={self.tipo.value}, visualizado={self.visualizado})>"

    def marcar_visualizado(self, usuario_id: uuid.UUID) -> None:
        """Marca o alerta como visualizado."""
        self.visualizado = True
        self.data_visualizacao = datetime.utcnow()
        self.visualizado_por = usuario_id

    def registrar_acao(self, acao: str, usuario_id: uuid.UUID) -> None:
        """Registra uma acao tomada sobre o alerta."""
        self.acao_tomada = acao
        self.acao_por = usuario_id
        self.data_acao = datetime.utcnow()
        if not self.visualizado:
            self.marcar_visualizado(usuario_id)

    @property
    def is_pendente(self) -> bool:
        """Verifica se o alerta esta pendente de visualizacao."""
        return not self.visualizado

    @property
    def is_expirado(self) -> bool:
        """Verifica se o alerta expirou."""
        if not self.expira_em:
            return False
        return datetime.utcnow() > self.expira_em

    @property
    def is_acao_pendente(self) -> bool:
        """Verifica se o alerta requer acao."""
        return self.visualizado and not self.acao_tomada

    @staticmethod
    def calcular_prioridade(tipo: TipoAlerta, score: float) -> int:
        """Calcula a prioridade baseada no tipo e score."""
        if tipo == TipoAlerta.RISCO_CRITICO or score >= 90:
            return 1
        if tipo == TipoAlerta.AUMENTO_RISCO and score >= 80:
            return 2
        if score >= 70:
            return 3
        if score >= 60:
            return 4
        return 5


class AuditLogTurnover(Base, TimestampMixin):
    """
    Model para log de auditoria de acessos ao sistema de turnover.

    Registra todos os acessos e operacoes relacionadas a
    dados sensiveis de predicao de turnover.

    Atributos:
        id: Identificador unico do log
        usuario_id: Usuario que realizou a acao
        condominium_id: Condominio do contexto
        acao: Tipo de acao realizada
        recurso: Tipo de recurso acessado
        recurso_id: ID do recurso acessado
        funcionario_id: ID do funcionario (quando aplicavel)
        detalhes: Detalhes da operacao
        ip_address: Endereco IP do usuario
        user_agent: User agent do navegador/cliente
    """

    __tablename__ = "turnover_audit_logs"
    __table_args__ = (
        Index("idx_audit_turnover_usuario", "usuario_id"),
        Index("idx_audit_turnover_acao", "acao"),
        Index("idx_audit_turnover_created", "created_at"),
        Index("idx_audit_turnover_funcionario", "funcionario_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Quem
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    condominium_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # O que
    acao: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="consulta_score, consulta_fatores, exportar_relatorio, etc",
    )
    recurso: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="prediction, alert, dashboard, relatorio",
    )
    recurso_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    funcionario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Detalhes
    detalhes: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Contexto tecnico
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<AuditLogTurnover(acao={self.acao}, recurso={self.recurso}, usuario={self.usuario_id})>"
