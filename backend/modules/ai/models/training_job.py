"""TrainingJob Model - Jobs de Treinamento de Modelos.

Sprint 34 - AI Predictions.
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class TrainingStatus(str, enum.Enum):
    """Status do job de treinamento."""

    QUEUED = "QUEUED"  # Na fila
    PREPARING = "PREPARING"  # Preparando dados
    TRAINING = "TRAINING"  # Treinando
    VALIDATING = "VALIDATING"  # Validando
    COMPLETED = "COMPLETED"  # Concluido
    FAILED = "FAILED"  # Falhou
    CANCELLED = "CANCELLED"  # Cancelado
    TIMEOUT = "TIMEOUT"  # Timeout


class TrainingJob(Base):
    """Job de treinamento de modelo."""

    __tablename__ = "ai_training_jobs"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Modelo
    model_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_ml_models.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Identificacao
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Status
    status = Column(
        Enum(TrainingStatus, name="trainingstatus", create_type=True),
        nullable=False,
        default=TrainingStatus.QUEUED,
        index=True,
    )

    # Configuracao
    config = Column(JSONB, nullable=True)
    # Ex: {"epochs": 100, "batch_size": 32, "early_stopping": true}

    hyperparameters = Column(JSONB, nullable=True)
    # Ex: {"learning_rate": 0.001, "n_estimators": 100}

    # Dataset
    feature_store_id = Column(UUID(as_uuid=True), nullable=True)
    training_data_path = Column(String(500), nullable=True)
    training_samples = Column(Integer, nullable=True)
    validation_split = Column(Float, default=0.2, nullable=True)
    test_split = Column(Float, default=0.1, nullable=True)

    # Cross-validation
    cv_folds = Column(Integer, nullable=True)  # Ex: 5 para 5-fold CV
    cv_results = Column(JSONB, nullable=True)
    # Ex: {"fold_scores": [0.9, 0.92, 0.88, 0.91, 0.89], "mean": 0.9, "std": 0.015}

    # Progresso
    current_epoch = Column(Integer, nullable=True)
    total_epochs = Column(Integer, nullable=True)
    progress_percent = Column(Float, default=0, nullable=False)

    # Metricas durante treinamento
    training_loss = Column(Float, nullable=True)
    validation_loss = Column(Float, nullable=True)
    training_history = Column(JSONB, nullable=True)
    # Ex: {"loss": [0.5, 0.3, 0.2], "val_loss": [0.6, 0.4, 0.3]}

    # Metricas finais
    final_metrics = Column(JSONB, nullable=True)
    # Ex: {"accuracy": 0.95, "f1": 0.93, "auc_roc": 0.97}

    # Artefatos
    output_model_path = Column(String(500), nullable=True)
    output_model_size = Column(Integer, nullable=True)
    artifacts_path = Column(String(500), nullable=True)
    # Ex: plots, confusion matrix, feature importance

    # Recursos
    compute_type = Column(String(50), nullable=True)
    # Ex: "cpu", "gpu", "distributed"
    worker_count = Column(Integer, default=1, nullable=True)
    memory_limit_gb = Column(Float, nullable=True)
    gpu_memory_limit_gb = Column(Float, nullable=True)

    # Tempo
    queued_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    timeout_seconds = Column(Integer, default=3600, nullable=True)

    # Erro
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)

    # Flags
    active = Column(Boolean, default=True, nullable=False)
    is_scheduled = Column(Boolean, default=False, nullable=False)
    is_auto_retrain = Column(Boolean, default=False, nullable=False)

    # Agendamento
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    cron_expression = Column(String(100), nullable=True)
    # Ex: "0 0 * * 0" (todo domingo a meia-noite)

    # Retry
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=True)

    # Tags
    tags = Column(ARRAY(String), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    cancelled_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    model = relationship("MLModel", back_populates="training_jobs")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<TrainingJob {self.name} ({self.status.value})>"

    @property
    def is_running(self) -> bool:
        """Verifica se esta rodando."""
        return self.status in [
            TrainingStatus.PREPARING,
            TrainingStatus.TRAINING,
            TrainingStatus.VALIDATING,
        ]

    @property
    def is_completed(self) -> bool:
        """Verifica se completou."""
        return self.status == TrainingStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Verifica se falhou."""
        return self.status in [TrainingStatus.FAILED, TrainingStatus.TIMEOUT]

    @property
    def can_retry(self) -> bool:
        """Verifica se pode tentar novamente."""
        return self.is_failed and self.retry_count < (self.max_retries or 3)

    @property
    def elapsed_seconds(self) -> Optional[int]:
        """Retorna tempo decorrido."""
        if not self.started_at:
            return None
        end = self.completed_at or datetime.utcnow()
        return int((end - self.started_at).total_seconds())

    def start(self) -> None:
        """Inicia o job."""
        self.status = TrainingStatus.PREPARING
        self.started_at = datetime.utcnow()

    def start_training(self) -> None:
        """Muda para status de treinamento."""
        self.status = TrainingStatus.TRAINING

    def start_validation(self) -> None:
        """Muda para status de validacao."""
        self.status = TrainingStatus.VALIDATING

    def complete(
        self,
        metrics: dict,
        model_path: Optional[str] = None,
        model_size: Optional[int] = None,
    ) -> None:
        """Completa o job com sucesso.

        Args:
            metrics: Metricas finais.
            model_path: Caminho do modelo treinado.
            model_size: Tamanho do modelo em bytes.
        """
        self.status = TrainingStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.final_metrics = metrics
        self.progress_percent = 100

        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())

        if model_path:
            self.output_model_path = model_path
        if model_size:
            self.output_model_size = model_size

    def fail(self, error_message: str, traceback: Optional[str] = None) -> None:
        """Marca o job como falho.

        Args:
            error_message: Mensagem de erro.
            traceback: Traceback completo.
        """
        self.status = TrainingStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        self.error_traceback = traceback

        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())

    def timeout(self) -> None:
        """Marca o job como timeout."""
        self.status = TrainingStatus.TIMEOUT
        self.completed_at = datetime.utcnow()
        self.error_message = f"Job exceeded timeout of {self.timeout_seconds} seconds"

    def cancel(self, user_id: Optional[str] = None) -> None:
        """Cancela o job.

        Args:
            user_id: ID do usuario que cancelou.
        """
        self.status = TrainingStatus.CANCELLED
        self.completed_at = datetime.utcnow()
        if user_id:
            self.cancelled_by = user_id

    def update_progress(
        self,
        current_epoch: int,
        total_epochs: int,
        training_loss: Optional[float] = None,
        validation_loss: Optional[float] = None,
    ) -> None:
        """Atualiza progresso.

        Args:
            current_epoch: Epoca atual.
            total_epochs: Total de epocas.
            training_loss: Loss de treinamento.
            validation_loss: Loss de validacao.
        """
        self.current_epoch = current_epoch
        self.total_epochs = total_epochs
        self.progress_percent = (current_epoch / total_epochs) * 100

        if training_loss is not None:
            self.training_loss = training_loss
        if validation_loss is not None:
            self.validation_loss = validation_loss

        # Atualiza historico
        if not self.training_history:
            self.training_history = {"loss": [], "val_loss": []}
        if training_loss is not None:
            self.training_history["loss"].append(training_loss)
        if validation_loss is not None:
            self.training_history["val_loss"].append(validation_loss)

    def increment_retry(self) -> None:
        """Incrementa contador de retry."""
        self.retry_count = (self.retry_count or 0) + 1
        self.status = TrainingStatus.QUEUED
        self.error_message = None
        self.error_traceback = None
