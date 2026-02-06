"""MLModel Model - Modelos de Machine Learning.

Sprint 34 - AI Predictions.
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class ModelType(str, enum.Enum):
    """Tipo de modelo."""

    CLASSIFICATION = "CLASSIFICATION"  # Classificacao
    REGRESSION = "REGRESSION"  # Regressao
    CLUSTERING = "CLUSTERING"  # Clusterizacao
    ANOMALY_DETECTION = "ANOMALY_DETECTION"  # Deteccao de anomalias
    TIME_SERIES = "TIME_SERIES"  # Series temporais
    RECOMMENDATION = "RECOMMENDATION"  # Recomendacao
    NLP = "NLP"  # Processamento de linguagem natural
    RANKING = "RANKING"  # Ranking/scoring


class ModelStatus(str, enum.Enum):
    """Status do modelo."""

    DRAFT = "DRAFT"  # Rascunho
    TRAINING = "TRAINING"  # Em treinamento
    VALIDATING = "VALIDATING"  # Em validacao
    READY = "READY"  # Pronto para uso
    DEPLOYED = "DEPLOYED"  # Em producao
    DEPRECATED = "DEPRECATED"  # Deprecado
    FAILED = "FAILED"  # Falhou no treinamento
    ARCHIVED = "ARCHIVED"  # Arquivado


class MLModel(Base):
    """Modelo de Machine Learning registrado."""

    __tablename__ = "ai_ml_models"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=False, default="1.0.0")

    # Tipo e Status
    model_type = Column(
        Enum(ModelType, name="modeltype", create_type=True),
        nullable=False,
        index=True,
    )
    status = Column(
        Enum(ModelStatus, name="modelstatus", create_type=True),
        nullable=False,
        default=ModelStatus.DRAFT,
        index=True,
    )

    # Algoritmo
    algorithm = Column(String(100), nullable=False)  # Ex: XGBoost, RandomForest, LSTM
    framework = Column(String(50), nullable=True)  # Ex: scikit-learn, tensorflow, pytorch
    library_version = Column(String(50), nullable=True)  # Ex: 1.2.3

    # Hiperparametros
    hyperparameters = Column(JSONB, nullable=True)
    # Ex: {"n_estimators": 100, "max_depth": 10, "learning_rate": 0.1}

    # Features
    feature_store_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    input_features = Column(ARRAY(String), nullable=True)
    target_variable = Column(String(100), nullable=True)
    feature_preprocessing = Column(
        JSONB, nullable=True
    )  # Ex: {"age": "normalize", "city": "one_hot"}

    # Artefatos
    model_path = Column(String(500), nullable=True)  # Caminho do arquivo do modelo
    model_size_bytes = Column(Integer, nullable=True)
    checksum = Column(String(64), nullable=True)  # SHA-256

    # Metricas de treinamento
    training_metrics = Column(JSONB, nullable=True)
    # Ex: {"accuracy": 0.95, "precision": 0.93, "recall": 0.92, "f1": 0.925}

    # Metricas de validacao
    validation_metrics = Column(JSONB, nullable=True)
    # Ex: {"auc_roc": 0.94, "log_loss": 0.15}

    # Metricas de producao
    production_metrics = Column(JSONB, nullable=True)
    # Ex: {"avg_latency_ms": 50, "predictions_per_day": 1000}

    # Dataset de treinamento
    training_dataset_id = Column(UUID(as_uuid=True), nullable=True)
    training_samples = Column(Integer, nullable=True)
    validation_samples = Column(Integer, nullable=True)
    test_samples = Column(Integer, nullable=True)

    # Thresholds
    prediction_threshold = Column(Float, default=0.5, nullable=True)
    confidence_threshold = Column(Float, default=0.7, nullable=True)

    # Uso
    total_predictions = Column(Integer, default=0, nullable=False)
    successful_predictions = Column(Integer, default=0, nullable=False)
    failed_predictions = Column(Integer, default=0, nullable=False)
    avg_prediction_time_ms = Column(Integer, nullable=True)

    # Drift e retraining
    last_drift_check = Column(DateTime(timezone=True), nullable=True)
    drift_score = Column(Float, nullable=True)
    drift_detected = Column(Boolean, default=False, nullable=False)
    retrain_scheduled = Column(DateTime(timezone=True), nullable=True)

    # Flags
    active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    auto_retrain = Column(Boolean, default=False, nullable=False)

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
    trained_at = Column(DateTime(timezone=True), nullable=True)
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    deprecated_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    predictions = relationship(
        "Prediction",
        back_populates="model",
        lazy="dynamic",
    )
    training_jobs = relationship(
        "TrainingJob",
        back_populates="model",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<MLModel {self.name} v{self.version} ({self.status.value})>"

    @property
    def is_ready(self) -> bool:
        """Verifica se esta pronto para uso."""
        return self.status in [ModelStatus.READY, ModelStatus.DEPLOYED]

    @property
    def is_deployed(self) -> bool:
        """Verifica se esta em producao."""
        return self.status == ModelStatus.DEPLOYED

    @property
    def success_rate(self) -> float:
        """Calcula taxa de sucesso."""
        if not self.total_predictions:
            return 0.0
        return (self.successful_predictions / self.total_predictions) * 100

    @property
    def failure_rate(self) -> float:
        """Calcula taxa de falha."""
        if not self.total_predictions:
            return 0.0
        return (self.failed_predictions / self.total_predictions) * 100

    @property
    def needs_retraining(self) -> bool:
        """Verifica se precisa retreinamento."""
        if self.drift_detected:
            return True
        if self.retrain_scheduled and self.retrain_scheduled <= datetime.utcnow():
            return True
        return False

    def start_training(self) -> None:
        """Inicia treinamento."""
        self.status = ModelStatus.TRAINING

    def complete_training(
        self,
        metrics: dict,
        model_path: Optional[str] = None,
        model_size: Optional[int] = None,
    ) -> None:
        """Completa treinamento.

        Args:
            metrics: Metricas de treinamento.
            model_path: Caminho do arquivo do modelo.
            model_size: Tamanho em bytes.
        """
        self.status = ModelStatus.READY
        self.training_metrics = metrics
        self.trained_at = datetime.utcnow()
        if model_path:
            self.model_path = model_path
        if model_size:
            self.model_size_bytes = model_size

    def fail_training(self) -> None:
        """Marca falha no treinamento."""
        self.status = ModelStatus.FAILED

    def deploy(self) -> None:
        """Faz deploy do modelo."""
        self.status = ModelStatus.DEPLOYED
        self.deployed_at = datetime.utcnow()

    def deprecate(self) -> None:
        """Depreca o modelo."""
        self.status = ModelStatus.DEPRECATED
        self.deprecated_at = datetime.utcnow()
        self.active = False

    def archive(self) -> None:
        """Arquiva o modelo."""
        self.status = ModelStatus.ARCHIVED
        self.active = False

    def record_prediction(
        self,
        success: bool,
        prediction_time_ms: Optional[int] = None,
    ) -> None:
        """Registra predicao.

        Args:
            success: Se foi sucesso.
            prediction_time_ms: Tempo de predicao em ms.
        """
        self.total_predictions = (self.total_predictions or 0) + 1

        if success:
            self.successful_predictions = (self.successful_predictions or 0) + 1
        else:
            self.failed_predictions = (self.failed_predictions or 0) + 1

        # Atualiza media de tempo
        if prediction_time_ms is not None:
            current_avg = self.avg_prediction_time_ms or 0
            total = self.total_predictions
            self.avg_prediction_time_ms = int(
                ((current_avg * (total - 1)) + prediction_time_ms) / total
            )

    def update_drift(self, drift_score: float, threshold: float = 0.3) -> bool:
        """Atualiza score de drift.

        Args:
            drift_score: Score de drift (0-1).
            threshold: Threshold para detectar drift.

        Returns:
            True se drift foi detectado.
        """
        self.last_drift_check = datetime.utcnow()
        self.drift_score = drift_score
        self.drift_detected = drift_score >= threshold
        return self.drift_detected

    def increment_version(self) -> str:
        """Incrementa versao do modelo.

        Returns:
            Nova versao.
        """
        parts = self.version.split(".")
        if len(parts) == 3:
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            patch += 1
            self.version = f"{major}.{minor}.{patch}"
        else:
            self.version = "1.0.1"
        return self.version
