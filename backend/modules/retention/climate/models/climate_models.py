"""
Models SQLAlchemy para Pesquisa de Clima Operacional.

Este modulo define as tabelas para:
- ClimateSurvey: Pesquisas de clima configuradas
- ClimateResponse: Respostas individuais (anonimizadas)
- ClimateScore: Scores agregados por entidade e periodo
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base


class SurveyFrequency(StrEnum):
    """Frequencia de aplicacao da pesquisa."""

    SEMANAL = "semanal"
    QUINZENAL = "quinzenal"
    MENSAL = "mensal"


class QuestionType(StrEnum):
    """Tipo de pergunta da pesquisa."""

    ESCALA = "escala"  # 1-4
    TEXTO = "texto"  # Resposta aberta
    MULTIPLA_ESCOLHA = "multipla_escolha"


class ClimateDimension(StrEnum):
    """Dimensoes avaliadas na pesquisa de clima."""

    SATISFACAO = "satisfacao"
    LIDERANCA = "lideranca"
    OPERACIONAL = "operacional"
    CARREIRA = "carreira"
    ENPS = "enps"
    AMBIENTE = "ambiente"
    COMUNICACAO = "comunicacao"
    RECONHECIMENTO = "reconhecimento"


class EntityType(StrEnum):
    """Tipo de entidade para agregacao de scores."""

    FUNCIONARIO = "funcionario"
    POSTO = "posto"
    EQUIPE = "equipe"
    EMPRESA = "empresa"
    CLIENTE = "cliente"


class AlertSeverity(StrEnum):
    """Severidade de alertas de clima."""

    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class ClimateSurvey(Base):
    """
    Modelo de Pesquisa de Clima.

    Armazena a configuracao de pesquisas de clima organizacional,
    incluindo perguntas, frequencia e status.

    Attributes:
        id: Identificador unico UUID
        nome: Nome da pesquisa
        descricao: Descricao detalhada
        perguntas: Lista de perguntas em formato JSONB
        frequencia: Frequencia de aplicacao (semanal, quinzenal, mensal)
        ativo: Se a pesquisa esta ativa
        data_inicio: Data de inicio da pesquisa
        data_fim: Data de termino (opcional)
        empresa_id: ID da empresa proprietaria
    """

    __tablename__ = "climate_surveys"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    nome: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )
    descricao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    perguntas: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        comment="Lista de perguntas: [{id, texto, tipo, dimensao, ordem}]",
    )
    frequencia: Mapped[str] = mapped_column(
        String(20),
        default=SurveyFrequency.MENSAL.value,
        nullable=False,
    )
    ativo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    data_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    data_fim: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    empresa_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    total_respostas: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    score_medio: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Relationships
    responses: Mapped[list["ClimateResponse"]] = relationship(
        "ClimateResponse",
        back_populates="survey",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ClimateSurvey {self.nome} ({self.id[:8]})>"

    @property
    def is_active(self) -> bool:
        """Verifica se a pesquisa esta ativa e dentro do periodo."""
        if not self.ativo:
            return False
        now = datetime.now()
        if self.data_fim and now > self.data_fim:
            return False
        return True

    @property
    def total_perguntas(self) -> int:
        """Retorna total de perguntas."""
        return len(self.perguntas) if self.perguntas else 0


class ClimateResponse(Base):
    """
    Modelo de Resposta de Pesquisa de Clima.

    Armazena respostas individuais de forma ANONIMIZADA.
    O funcionario_hash e um hash do ID para garantir anonimato
    mas permitir deteccao de respostas duplicadas.

    Attributes:
        id: Identificador unico UUID
        survey_id: ID da pesquisa respondida
        funcionario_hash: Hash SHA-256 do funcionario_id + salt
        posto_id: ID do posto (para agregacao)
        equipe_id: ID da equipe (para agregacao)
        empresa_id: ID da empresa
        data_resposta: Data/hora da resposta
        respostas: Respostas em formato JSONB {pergunta_id: valor}
        score_calculado: Score normalizado 0-100
        tempo_resposta_segundos: Tempo para responder
    """

    __tablename__ = "climate_responses"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    survey_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("climate_surveys.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    funcionario_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="SHA-256 hash do funcionario_id para anonimato",
    )
    posto_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    equipe_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    empresa_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    cliente_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    periodo: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
        index=True,
        comment="Periodo no formato YYYY-MM",
    )
    data_resposta: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    respostas: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Respostas: {pergunta_id: valor (1-4)}",
    )
    comentarios: Mapped[dict[str, str] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Comentarios opcionais: {pergunta_id: texto}",
    )
    score_calculado: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        index=True,
    )
    scores_por_dimensao: Mapped[dict[str, float]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Scores por dimensao: {dimensao: score 0-100}",
    )
    tempo_resposta_segundos: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    is_complete: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    ip_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="Hash do IP para deteccao de fraude",
    )
    user_agent_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    # Relationships
    survey: Mapped["ClimateSurvey"] = relationship(
        "ClimateSurvey",
        back_populates="responses",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ClimateResponse {self.id[:8]} score={self.score_calculado:.1f}>"

    @property
    def is_valid(self) -> bool:
        """Verifica se a resposta e valida."""
        if not self.respostas:
            return False
        # Tempo minimo de 30 segundos para evitar respostas aleatorias
        if self.tempo_resposta_segundos < 30:
            return False
        return True


class ClimateScore(Base):
    """
    Modelo de Score Agregado de Clima.

    Armazena scores calculados e agregados por entidade e periodo.
    Usado para dashboards e analises de tendencia.

    Attributes:
        id: Identificador unico UUID
        entidade_tipo: Tipo (funcionario, posto, equipe, empresa)
        entidade_id: ID da entidade
        periodo: Periodo no formato YYYY-MM
        score: Score geral 0-100
        scores_dimensao: Scores por dimensao
        tendencia: Variacao percentual vs periodo anterior
        total_respostas: Quantidade de respostas no periodo
        fatores_positivos: Lista de pontos fortes
        fatores_negativos: Lista de pontos de atencao
        enps_score: Score eNPS (-100 a 100)
    """

    __tablename__ = "climate_scores"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    entidade_tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )
    entidade_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )
    entidade_nome: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    empresa_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    periodo: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
        index=True,
        comment="Periodo no formato YYYY-MM",
    )
    score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        index=True,
    )
    scores_dimensao: Mapped[dict[str, float]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Scores por dimensao: {dimensao: score 0-100}",
    )
    tendencia: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        comment="Variacao percentual vs periodo anterior",
    )
    total_respostas: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    taxa_participacao: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        comment="Percentual de funcionarios que responderam",
    )
    fatores_positivos: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    fatores_negativos: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    enps_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        comment="eNPS: -100 a +100",
    )
    enps_promotores: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    enps_neutros: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    enps_detratores: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    alertas: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        comment="Alertas gerados: [{tipo, mensagem, severidade}]",
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    calculado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ClimateScore {self.entidade_tipo}:{self.entidade_id[:8]} {self.periodo} score={self.score:.1f}>"

    @property
    def classificacao(self) -> str:
        """Retorna classificacao baseada no score."""
        if self.score >= 80:
            return "excelente"
        if self.score >= 65:
            return "bom"
        if self.score >= 50:
            return "regular"
        if self.score >= 35:
            return "atencao"
        return "critico"

    @property
    def has_alert(self) -> bool:
        """Verifica se tem alertas."""
        return len(self.alertas) > 0 if self.alertas else False


class ClimateAlert(Base):
    """
    Modelo de Alerta de Clima.

    Armazena alertas gerados quando ha quedas significativas
    ou scores abaixo do threshold.

    Attributes:
        id: Identificador unico
        entidade_tipo: Tipo da entidade com problema
        entidade_id: ID da entidade
        tipo_alerta: Tipo do alerta (queda, score_baixo, etc)
        severidade: Nivel de severidade
        mensagem: Descricao do alerta
        score_atual: Score que gerou o alerta
        score_anterior: Score do periodo anterior
        variacao: Variacao percentual
        resolvido: Se o alerta foi resolvido
    """

    __tablename__ = "climate_alerts"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    empresa_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    entidade_tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )
    entidade_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )
    entidade_nome: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    periodo: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
        index=True,
    )
    tipo_alerta: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    dimensao: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    severidade: Mapped[str] = mapped_column(
        String(20),
        default=AlertSeverity.MEDIA.value,
        nullable=False,
        index=True,
    )
    mensagem: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    score_atual: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    score_anterior: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    variacao: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    resolvido: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    resolvido_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resolvido_por: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    notas_resolucao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ClimateAlert {self.tipo_alerta} {self.severidade} ({self.id[:8]})>"
