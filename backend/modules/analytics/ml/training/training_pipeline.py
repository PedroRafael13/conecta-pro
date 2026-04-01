"""Pipeline de treinamento de modelos ML."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

import numpy as np
import pandas as pd
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    cross_val_score,
    train_test_split,
)
from sklearn.preprocessing import LabelEncoder, StandardScaler

from modules.analytics.ml.registry.model_registry import (
    ModelFramework,
    ModelMetrics,
    ModelRegistry,
    ModelType,
)

logger = logging.getLogger(__name__)


class ValidationStrategy(Enum):
    """Estratégias de validação."""

    HOLDOUT = "holdout"
    KFOLD = "kfold"
    STRATIFIED_KFOLD = "stratified_kfold"
    TIME_SERIES_SPLIT = "time_series_split"


class SearchStrategy(Enum):
    """Estratégias de busca de hiperparâmetros."""

    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN = "bayesian"
    NONE = "none"


@dataclass
class DataSplit:
    """Divisão de dados para treinamento."""

    x_train: pd.DataFrame
    x_val: pd.DataFrame
    x_test: pd.DataFrame
    y_train: pd.Series
    y_val: pd.Series
    y_test: pd.Series

    @property
    def train_size(self) -> int:
        return len(self.x_train)

    @property
    def val_size(self) -> int:
        return len(self.x_val)

    @property
    def test_size(self) -> int:
        return len(self.x_test)


@dataclass
class TrainingConfig:
    """Configuração de treinamento."""

    model_name: str
    model_type: ModelType
    framework: ModelFramework
    target_column: str
    feature_columns: list[str]
    test_size: float = 0.2
    val_size: float = 0.1
    validation_strategy: ValidationStrategy = ValidationStrategy.HOLDOUT
    search_strategy: SearchStrategy = SearchStrategy.NONE
    cv_folds: int = 5
    random_state: int = 42
    scale_features: bool = True
    handle_missing: str = "drop"  # drop, mean, median, mode
    handle_categorical: str = "label_encode"  # label_encode, one_hot
    hyperparameter_grid: dict[str, list] = field(default_factory=dict)
    early_stopping: bool = False
    early_stopping_rounds: int = 10
    metrics: list[str] = field(default_factory=lambda: ["accuracy"])


@dataclass
class TrainingResult:
    """Resultado do treinamento."""

    id: UUID
    model_name: str
    version: str
    status: str  # success, failed
    metrics: ModelMetrics
    best_params: dict[str, Any]
    training_time_seconds: float
    data_info: dict[str, Any]
    validation_scores: list[float]
    feature_importance: dict[str, float] | None = None
    error_message: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class TrainingPipeline:
    """
    Pipeline completo de treinamento de ML.

    Funcionalidades:
    - Pré-processamento automático
    - Divisão de dados
    - Cross-validation
    - Hyperparameter tuning
    - Feature importance
    - Registro automático de modelos
    """

    def __init__(
        self,
        model_registry: ModelRegistry | None = None,
    ) -> None:
        """
        Inicializa o pipeline.

        Args:
            model_registry: Registry para salvar modelos
        """
        self.model_registry = model_registry or ModelRegistry()
        self._scalers: dict[str, StandardScaler] = {}
        self._encoders: dict[str, LabelEncoder] = {}

    def prepare_data(
        self,
        df: pd.DataFrame,
        config: TrainingConfig,
    ) -> DataSplit:
        """
        Prepara dados para treinamento.

        Args:
            df: DataFrame com dados
            config: Configuração de treinamento

        Returns:
            DataSplit com dados divididos
        """
        logger.info(f"Preparando dados para {config.model_name}")

        # Copiar para não modificar original
        df = df.copy()

        # Tratar valores missing
        df = self._handle_missing(df, config)

        # Separar features e target
        x_features = df[config.feature_columns].copy()
        y_target = df[config.target_column].copy()

        # Tratar categorias
        x_features = self._handle_categorical(x_features, config)

        # Escalar features
        if config.scale_features:
            x_features = self._scale_features(x_features, config.model_name)

        # Dividir dados
        x_temp, x_test, y_temp, y_test = train_test_split(
            x_features,
            y_target,
            test_size=config.test_size,
            random_state=config.random_state,
            stratify=y_target if config.model_type == ModelType.CLASSIFICATION else None,
        )

        # Dividir treino e validação
        val_ratio = config.val_size / (1 - config.test_size)
        x_train, x_val, y_train, y_val = train_test_split(
            x_temp,
            y_temp,
            test_size=val_ratio,
            random_state=config.random_state,
            stratify=y_temp if config.model_type == ModelType.CLASSIFICATION else None,
        )

        logger.info(f"Dados preparados - Train: {len(x_train)}, Val: {len(x_val)}, Test: {len(x_test)}")

        return DataSplit(
            x_train=x_train,
            x_val=x_val,
            x_test=x_test,
            y_train=y_train,
            y_val=y_val,
            y_test=y_test,
        )

    def train(
        self,
        model: Any,
        data: DataSplit,
        config: TrainingConfig,
        version: str = "1.0.0",
        auto_register: bool = True,
    ) -> TrainingResult:
        """
        Treina um modelo.

        Args:
            model: Modelo sklearn-compatible
            data: Dados divididos
            config: Configuração
            version: Versão do modelo
            auto_register: Registrar automaticamente no registry

        Returns:
            TrainingResult com métricas e informações
        """
        start_time = datetime.utcnow()
        logger.info(f"Iniciando treinamento: {config.model_name} v{version}")

        try:
            # Hyperparameter tuning
            if config.search_strategy != SearchStrategy.NONE:
                model, best_params = self._tune_hyperparameters(model, data, config)
            else:
                best_params = {}

            # Cross-validation
            cv_scores = self._cross_validate(model, data, config)

            # Treinar modelo final
            model.fit(data.x_train, data.y_train)

            # Calcular métricas
            metrics = self._calculate_metrics(model, data, config)

            # Feature importance
            feature_importance = self._get_feature_importance(model, config.feature_columns)

            training_time = (datetime.utcnow() - start_time).total_seconds()

            # Criar resultado
            result = TrainingResult(
                id=uuid4(),
                model_name=config.model_name,
                version=version,
                status="success",
                metrics=metrics,
                best_params=best_params,
                training_time_seconds=training_time,
                data_info={
                    "train_size": data.train_size,
                    "val_size": data.val_size,
                    "test_size": data.test_size,
                    "n_features": len(config.feature_columns),
                },
                validation_scores=cv_scores,
                feature_importance=feature_importance,
            )

            # Registrar modelo
            if auto_register:
                self.model_registry.register_model(
                    model=model,
                    name=config.model_name,
                    version=version,
                    model_type=config.model_type,
                    framework=config.framework,
                    description=f"Treinado em {datetime.utcnow().isoformat()}",
                    metrics=metrics,
                    hyperparameters=best_params or model.get_params(),
                    feature_names=config.feature_columns,
                    target_column=config.target_column,
                )

            logger.info(f"Treinamento concluído: {config.model_name} v{version} ({training_time:.2f}s)")
            return result

        except Exception as e:
            logger.error(f"Erro no treinamento: {e}")
            return TrainingResult(
                id=uuid4(),
                model_name=config.model_name,
                version=version,
                status="failed",
                metrics=ModelMetrics(),
                best_params={},
                training_time_seconds=(datetime.utcnow() - start_time).total_seconds(),
                data_info={},
                validation_scores=[],
                error_message=str(e),
            )

    def train_with_automl(
        self,
        df: pd.DataFrame,
        config: TrainingConfig,
        models: list[tuple[str, Any]],
        version: str = "1.0.0",
    ) -> list[TrainingResult]:
        """
        Treina múltiplos modelos e compara.

        Args:
            df: DataFrame com dados
            config: Configuração base
            models: Lista de (nome, modelo)
            version: Versão base

        Returns:
            Lista de resultados ordenados por performance
        """
        results = []
        data = self.prepare_data(df, config)

        for model_name, model in models:
            # Criar config específica
            model_config = TrainingConfig(
                model_name=f"{config.model_name}_{model_name}",
                model_type=config.model_type,
                framework=config.framework,
                target_column=config.target_column,
                feature_columns=config.feature_columns,
                validation_strategy=config.validation_strategy,
                cv_folds=config.cv_folds,
                random_state=config.random_state,
            )

            result = self.train(
                model=model,
                data=data,
                config=model_config,
                version=version,
                auto_register=False,  # Registrar só o melhor
            )
            results.append((result, model))

        # Ordenar por métrica principal
        primary_metric = config.metrics[0] if config.metrics else "accuracy"
        results.sort(
            key=lambda x: getattr(x[0].metrics, primary_metric, 0) or 0,
            reverse=True,
        )

        # Registrar melhor modelo
        if results and results[0][0].status == "success":
            best_result, best_model = results[0]
            self.model_registry.register_model(
                model=best_model,
                name=config.model_name,
                version=version,
                model_type=config.model_type,
                framework=config.framework,
                description=f"Melhor modelo de {len(models)} testados",
                metrics=best_result.metrics,
                feature_names=config.feature_columns,
                target_column=config.target_column,
            )

        return [r for r, _ in results]

    def _handle_missing(
        self,
        df: pd.DataFrame,
        config: TrainingConfig,
    ) -> pd.DataFrame:
        """Trata valores missing."""
        if config.handle_missing == "drop":
            return df.dropna()
        elif config.handle_missing == "mean":
            return df.fillna(df.mean(numeric_only=True))
        elif config.handle_missing == "median":
            return df.fillna(df.median(numeric_only=True))
        elif config.handle_missing == "mode":
            return df.fillna(df.mode().iloc[0])
        return df

    def _handle_categorical(
        self,
        features: pd.DataFrame,
        config: TrainingConfig,
    ) -> pd.DataFrame:
        """Trata variáveis categóricas."""
        categorical_cols = features.select_dtypes(include=["object", "category"]).columns

        if len(categorical_cols) == 0:
            return features

        if config.handle_categorical == "label_encode":
            for col in categorical_cols:
                if col not in self._encoders:
                    self._encoders[col] = LabelEncoder()
                    features[col] = self._encoders[col].fit_transform(features[col].astype(str))
                else:
                    features[col] = self._encoders[col].transform(features[col].astype(str))
        elif config.handle_categorical == "one_hot":
            features = pd.get_dummies(features, columns=categorical_cols)

        return features

    def _scale_features(
        self,
        features: pd.DataFrame,
        model_name: str,
    ) -> pd.DataFrame:
        """Escala features numéricas."""
        numeric_cols = features.select_dtypes(include=[np.number]).columns

        if model_name not in self._scalers:
            self._scalers[model_name] = StandardScaler()
            features[numeric_cols] = self._scalers[model_name].fit_transform(features[numeric_cols])
        else:
            features[numeric_cols] = self._scalers[model_name].transform(features[numeric_cols])

        return features

    def _tune_hyperparameters(
        self,
        model: Any,
        data: DataSplit,
        config: TrainingConfig,
    ) -> tuple[Any, dict]:
        """Otimiza hiperparâmetros."""
        if not config.hyperparameter_grid:
            return model, {}

        logger.info("Iniciando hyperparameter tuning...")

        if config.search_strategy == SearchStrategy.GRID_SEARCH:
            search = GridSearchCV(
                model,
                config.hyperparameter_grid,
                cv=config.cv_folds,
                scoring="accuracy" if config.model_type == ModelType.CLASSIFICATION else "neg_mean_squared_error",
                n_jobs=-1,
            )
        elif config.search_strategy == SearchStrategy.RANDOM_SEARCH:
            search = RandomizedSearchCV(
                model,
                config.hyperparameter_grid,
                n_iter=20,
                cv=config.cv_folds,
                scoring="accuracy" if config.model_type == ModelType.CLASSIFICATION else "neg_mean_squared_error",
                n_jobs=-1,
                random_state=config.random_state,
            )
        else:
            return model, {}

        search.fit(data.x_train, data.y_train)
        logger.info(f"Melhores parâmetros: {search.best_params_}")

        return search.best_estimator_, search.best_params_

    def _cross_validate(
        self,
        model: Any,
        data: DataSplit,
        config: TrainingConfig,
    ) -> list[float]:
        """Executa cross-validation."""
        scoring = "accuracy" if config.model_type == ModelType.CLASSIFICATION else "neg_mean_squared_error"

        scores = cross_val_score(
            model,
            data.x_train,
            data.y_train,
            cv=config.cv_folds,
            scoring=scoring,
        )

        logger.info(f"CV Scores: {scores.mean():.4f} (+/- {scores.std():.4f})")
        return scores.tolist()

    def _calculate_metrics(
        self,
        model: Any,
        data: DataSplit,
        config: TrainingConfig,
    ) -> ModelMetrics:
        """Calcula métricas do modelo."""
        from sklearn.metrics import (
            accuracy_score,
            f1_score,
            log_loss,
            mean_absolute_error,
            mean_squared_error,
            precision_score,
            r2_score,
            recall_score,
            roc_auc_score,
        )

        y_pred = model.predict(data.x_test)
        metrics = ModelMetrics()

        if config.model_type == ModelType.CLASSIFICATION:
            metrics.accuracy = accuracy_score(data.y_test, y_pred)
            metrics.precision = precision_score(data.y_test, y_pred, average="weighted", zero_division=0)
            metrics.recall = recall_score(data.y_test, y_pred, average="weighted", zero_division=0)
            metrics.f1_score = f1_score(data.y_test, y_pred, average="weighted", zero_division=0)

            # AUC-ROC para binário
            if hasattr(model, "predict_proba") and len(np.unique(data.y_test)) == 2:
                y_proba = model.predict_proba(data.x_test)[:, 1]
                metrics.auc_roc = roc_auc_score(data.y_test, y_proba)
                metrics.log_loss = log_loss(data.y_test, y_proba)

        elif config.model_type == ModelType.REGRESSION:
            metrics.mse = mean_squared_error(data.y_test, y_pred)
            metrics.rmse = np.sqrt(metrics.mse)
            metrics.mae = mean_absolute_error(data.y_test, y_pred)
            metrics.r2 = r2_score(data.y_test, y_pred)

        return metrics

    def _get_feature_importance(
        self,
        model: Any,
        feature_names: list[str],
    ) -> dict[str, float] | None:
        """Extrai importância das features."""
        importance = None

        if hasattr(model, "feature_importances_"):
            importance = model.feature_importances_
        elif hasattr(model, "coef_"):
            importance = np.abs(model.coef_).flatten()

        if importance is not None and len(importance) == len(feature_names):
            # Normalizar
            importance = importance / importance.sum()
            return dict(zip(feature_names, importance.tolist(), strict=False))

        return None

    def get_scaler(self, model_name: str) -> StandardScaler | None:
        """Obtém scaler usado no treinamento."""
        return self._scalers.get(model_name)

    def get_encoder(self, column: str) -> LabelEncoder | None:
        """Obtém encoder usado no treinamento."""
        return self._encoders.get(column)


# Funções utilitárias para criação rápida de modelos
def create_classification_pipeline(
    model_name: str,
    target_column: str,
    feature_columns: list[str],
) -> TrainingConfig:
    """Cria config para classificação."""
    return TrainingConfig(
        model_name=model_name,
        model_type=ModelType.CLASSIFICATION,
        framework=ModelFramework.SKLEARN,
        target_column=target_column,
        feature_columns=feature_columns,
        metrics=["accuracy", "precision", "recall", "f1_score"],
    )


def create_regression_pipeline(
    model_name: str,
    target_column: str,
    feature_columns: list[str],
) -> TrainingConfig:
    """Cria config para regressão."""
    return TrainingConfig(
        model_name=model_name,
        model_type=ModelType.REGRESSION,
        framework=ModelFramework.SKLEARN,
        target_column=target_column,
        feature_columns=feature_columns,
        metrics=["mse", "rmse", "mae", "r2"],
    )
