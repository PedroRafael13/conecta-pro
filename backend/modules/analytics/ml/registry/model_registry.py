"""Model Registry para versionamento e gerenciamento de modelos ML."""

import hashlib
import json
import logging
import pickle
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from uuid import UUID, uuid4

import numpy as np

logger = logging.getLogger(__name__)


class ModelStage(Enum):
    """Estágios do ciclo de vida do modelo."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class ModelType(Enum):
    """Tipos de modelos suportados."""

    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    RECOMMENDATION = "recommendation"
    NLP = "nlp"
    CUSTOM = "custom"


class ModelFramework(Enum):
    """Frameworks de ML suportados."""

    SKLEARN = "sklearn"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    PROPHET = "prophet"
    STATSMODELS = "statsmodels"
    CUSTOM = "custom"


@dataclass
class ModelMetrics:
    """Métricas de performance do modelo."""

    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    auc_roc: Optional[float] = None
    auc_pr: Optional[float] = None
    mse: Optional[float] = None
    rmse: Optional[float] = None
    mae: Optional[float] = None
    r2: Optional[float] = None
    log_loss: Optional[float] = None
    custom_metrics: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None and key != "custom_metrics":
                result[key] = value
        result.update(self.custom_metrics)
        return result


@dataclass
class ModelMetadata:
    """Metadados do modelo."""

    name: str
    description: str
    model_type: ModelType
    framework: ModelFramework
    version: str
    tags: list[str] = field(default_factory=list)
    hyperparameters: dict[str, Any] = field(default_factory=dict)
    feature_names: list[str] = field(default_factory=list)
    target_column: Optional[str] = None
    training_data_info: dict[str, Any] = field(default_factory=dict)
    author: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ModelVersion:
    """Versão de um modelo."""

    id: UUID
    model_name: str
    version: str
    stage: ModelStage
    metadata: ModelMetadata
    metrics: ModelMetrics
    model_path: Optional[str] = None
    model_hash: Optional[str] = None
    artifact_uri: Optional[str] = None
    run_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    promoted_at: Optional[datetime] = None
    promoted_by: Optional[str] = None
    description: str = ""
    is_active: bool = True


@dataclass
class ModelExperiment:
    """Experimento de treinamento."""

    id: UUID
    name: str
    description: str
    model_name: str
    status: str  # running, completed, failed
    parameters: dict[str, Any]
    metrics: dict[str, float]
    artifacts: list[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    tags: list[str] = field(default_factory=list)


class ModelRegistry:
    """
    Registry central para modelos de ML.

    Funcionalidades:
    - Versionamento de modelos
    - Gerenciamento de estágios (dev, staging, prod)
    - Armazenamento de métricas e metadados
    - Comparação entre versões
    - Rollback
    """

    # Diretório base para armazenamento
    DEFAULT_STORAGE_PATH = "/opt/conecta-pro/data/models"

    def __init__(
        self,
        storage_path: Optional[str] = None,
    ) -> None:
        """
        Inicializa o Model Registry.

        Args:
            storage_path: Caminho para armazenamento de modelos
        """
        self.storage_path = Path(storage_path or self.DEFAULT_STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Registros em memória (em produção seria banco de dados)
        self._models: dict[str, dict[str, ModelVersion]] = {}
        self._experiments: dict[str, ModelExperiment] = {}
        self._production_models: dict[str, str] = {}  # model_name -> version

    def register_model(
        self,
        model: Any,
        name: str,
        version: str,
        model_type: ModelType,
        framework: ModelFramework,
        description: str = "",
        metrics: Optional[ModelMetrics] = None,
        hyperparameters: Optional[dict] = None,
        feature_names: Optional[list[str]] = None,
        target_column: Optional[str] = None,
        tags: Optional[list[str]] = None,
        author: Optional[str] = None,
    ) -> ModelVersion:
        """
        Registra um novo modelo ou versão.

        Args:
            model: Objeto do modelo treinado
            name: Nome do modelo
            version: Versão semântica (ex: 1.0.0)
            model_type: Tipo do modelo
            framework: Framework utilizado
            description: Descrição do modelo
            metrics: Métricas de performance
            hyperparameters: Hiperparâmetros utilizados
            feature_names: Nomes das features
            target_column: Coluna target
            tags: Tags para categorização
            author: Autor do modelo

        Returns:
            ModelVersion criado
        """
        # Criar diretório do modelo
        model_dir = self.storage_path / name / version
        model_dir.mkdir(parents=True, exist_ok=True)

        # Salvar modelo
        model_path = model_dir / "model.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model, f)

        # Calcular hash do modelo
        model_hash = self._calculate_model_hash(model_path)

        # Criar metadados
        metadata = ModelMetadata(
            name=name,
            description=description,
            model_type=model_type,
            framework=framework,
            version=version,
            tags=tags or [],
            hyperparameters=hyperparameters or {},
            feature_names=feature_names or [],
            target_column=target_column,
            author=author,
        )

        # Criar versão
        model_version = ModelVersion(
            id=uuid4(),
            model_name=name,
            version=version,
            stage=ModelStage.DEVELOPMENT,
            metadata=metadata,
            metrics=metrics or ModelMetrics(),
            model_path=str(model_path),
            model_hash=model_hash,
            artifact_uri=str(model_dir),
            description=description,
        )

        # Salvar metadados
        self._save_metadata(model_dir, model_version)

        # Registrar
        if name not in self._models:
            self._models[name] = {}
        self._models[name][version] = model_version

        logger.info(f"Modelo registrado: {name} v{version}")
        return model_version

    def get_model(
        self,
        name: str,
        version: Optional[str] = None,
        stage: Optional[ModelStage] = None,
    ) -> Optional[Any]:
        """
        Carrega um modelo do registry.

        Args:
            name: Nome do modelo
            version: Versão específica (se None, usa production ou latest)
            stage: Estágio do modelo

        Returns:
            Modelo carregado ou None
        """
        model_version = self.get_model_version(name, version, stage)
        if not model_version or not model_version.model_path:
            return None

        try:
            with open(model_version.model_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            return None

    def get_model_version(
        self,
        name: str,
        version: Optional[str] = None,
        stage: Optional[ModelStage] = None,
    ) -> Optional[ModelVersion]:
        """
        Obtém informações de uma versão do modelo.

        Args:
            name: Nome do modelo
            version: Versão específica
            stage: Estágio do modelo

        Returns:
            ModelVersion ou None
        """
        if name not in self._models:
            return None

        # Se versão específica
        if version:
            return self._models[name].get(version)

        # Se estágio específico
        if stage:
            for v in self._models[name].values():
                if v.stage == stage and v.is_active:
                    return v

        # Production primeiro
        if name in self._production_models:
            prod_version = self._production_models[name]
            return self._models[name].get(prod_version)

        # Latest
        versions = list(self._models[name].values())
        if versions:
            return sorted(versions, key=lambda x: x.created_at, reverse=True)[0]

        return None

    def promote_model(
        self,
        name: str,
        version: str,
        target_stage: ModelStage,
        promoted_by: str = "system",
    ) -> bool:
        """
        Promove modelo para um novo estágio.

        Args:
            name: Nome do modelo
            version: Versão a promover
            target_stage: Estágio destino
            promoted_by: Quem promoveu

        Returns:
            True se sucesso
        """
        model_version = self.get_model_version(name, version)
        if not model_version:
            logger.error(f"Modelo não encontrado: {name} v{version}")
            return False

        old_stage = model_version.stage
        model_version.stage = target_stage
        model_version.promoted_at = datetime.utcnow()
        model_version.promoted_by = promoted_by

        # Se promovendo para produção
        if target_stage == ModelStage.PRODUCTION:
            # Arquivar versão anterior de produção
            if name in self._production_models:
                old_version = self._production_models[name]
                if old_version != version:
                    old_model = self._models[name].get(old_version)
                    if old_model:
                        old_model.stage = ModelStage.ARCHIVED

            self._production_models[name] = version

        logger.info(
            f"Modelo promovido: {name} v{version} "
            f"{old_stage.value} -> {target_stage.value}"
        )
        return True

    def rollback_model(
        self,
        name: str,
        target_version: str,
    ) -> bool:
        """
        Faz rollback para versão anterior.

        Args:
            name: Nome do modelo
            target_version: Versão para rollback

        Returns:
            True se sucesso
        """
        return self.promote_model(name, target_version, ModelStage.PRODUCTION)

    def compare_versions(
        self,
        name: str,
        version1: str,
        version2: str,
    ) -> dict[str, Any]:
        """
        Compara duas versões de um modelo.

        Args:
            name: Nome do modelo
            version1: Primeira versão
            version2: Segunda versão

        Returns:
            Comparação detalhada
        """
        v1 = self.get_model_version(name, version1)
        v2 = self.get_model_version(name, version2)

        if not v1 or not v2:
            return {"error": "Versão não encontrada"}

        # Comparar métricas
        metrics_comparison = {}
        v1_metrics = v1.metrics.to_dict()
        v2_metrics = v2.metrics.to_dict()

        all_metrics = set(v1_metrics.keys()) | set(v2_metrics.keys())
        for metric in all_metrics:
            val1 = v1_metrics.get(metric)
            val2 = v2_metrics.get(metric)
            if val1 is not None and val2 is not None:
                diff = val2 - val1
                pct_change = (diff / val1 * 100) if val1 != 0 else 0
                metrics_comparison[metric] = {
                    version1: val1,
                    version2: val2,
                    "diff": diff,
                    "pct_change": round(pct_change, 2),
                    "improved": diff > 0,
                }

        # Comparar hiperparâmetros
        hp1 = v1.metadata.hyperparameters
        hp2 = v2.metadata.hyperparameters
        hp_diff = {
            "added": {k: v for k, v in hp2.items() if k not in hp1},
            "removed": {k: v for k, v in hp1.items() if k not in hp2},
            "changed": {
                k: {"old": hp1[k], "new": hp2[k]}
                for k in hp1
                if k in hp2 and hp1[k] != hp2[k]
            },
        }

        return {
            "model_name": name,
            "versions": [version1, version2],
            "metrics_comparison": metrics_comparison,
            "hyperparameter_diff": hp_diff,
            "feature_diff": {
                version1: len(v1.metadata.feature_names),
                version2: len(v2.metadata.feature_names),
            },
            "recommendation": self._get_comparison_recommendation(metrics_comparison),
        }

    def list_models(self) -> list[dict[str, Any]]:
        """Lista todos os modelos registrados."""
        models = []
        for name, versions in self._models.items():
            prod_version = self._production_models.get(name)
            latest = sorted(
                versions.values(), key=lambda x: x.created_at, reverse=True
            )[0]

            models.append({
                "name": name,
                "total_versions": len(versions),
                "production_version": prod_version,
                "latest_version": latest.version,
                "model_type": latest.metadata.model_type.value,
                "framework": latest.metadata.framework.value,
                "created_at": latest.created_at.isoformat(),
            })

        return models

    def list_versions(
        self,
        name: str,
        stage: Optional[ModelStage] = None,
    ) -> list[dict[str, Any]]:
        """Lista versões de um modelo."""
        if name not in self._models:
            return []

        versions = []
        for version, model_version in self._models[name].items():
            if stage and model_version.stage != stage:
                continue

            versions.append({
                "version": version,
                "stage": model_version.stage.value,
                "metrics": model_version.metrics.to_dict(),
                "created_at": model_version.created_at.isoformat(),
                "is_active": model_version.is_active,
                "is_production": version == self._production_models.get(name),
            })

        return sorted(versions, key=lambda x: x["created_at"], reverse=True)

    def delete_version(
        self,
        name: str,
        version: str,
        force: bool = False,
    ) -> bool:
        """
        Deleta uma versão do modelo.

        Args:
            name: Nome do modelo
            version: Versão a deletar
            force: Forçar deleção mesmo se em produção

        Returns:
            True se sucesso
        """
        model_version = self.get_model_version(name, version)
        if not model_version:
            return False

        # Verificar se está em produção
        if model_version.stage == ModelStage.PRODUCTION and not force:
            logger.error("Não é possível deletar modelo em produção sem force=True")
            return False

        # Soft delete
        model_version.is_active = False
        model_version.stage = ModelStage.ARCHIVED

        if self._production_models.get(name) == version:
            del self._production_models[name]

        logger.info(f"Modelo arquivado: {name} v{version}")
        return True

    def get_production_model(self, name: str) -> Optional[Any]:
        """Obtém modelo em produção."""
        return self.get_model(name, stage=ModelStage.PRODUCTION)

    def log_experiment(
        self,
        name: str,
        model_name: str,
        parameters: dict[str, Any],
        description: str = "",
        tags: Optional[list[str]] = None,
    ) -> ModelExperiment:
        """
        Inicia log de um experimento.

        Args:
            name: Nome do experimento
            model_name: Nome do modelo
            parameters: Parâmetros do experimento
            description: Descrição
            tags: Tags

        Returns:
            Experimento criado
        """
        experiment = ModelExperiment(
            id=uuid4(),
            name=name,
            description=description,
            model_name=model_name,
            status="running",
            parameters=parameters,
            metrics={},
            artifacts=[],
            start_time=datetime.utcnow(),
            tags=tags or [],
        )

        self._experiments[str(experiment.id)] = experiment
        logger.info(f"Experimento iniciado: {name}")
        return experiment

    def log_metrics(
        self,
        experiment_id: str,
        metrics: dict[str, float],
    ) -> None:
        """Registra métricas de um experimento."""
        if experiment_id in self._experiments:
            self._experiments[experiment_id].metrics.update(metrics)

    def end_experiment(
        self,
        experiment_id: str,
        status: str = "completed",
    ) -> None:
        """Finaliza um experimento."""
        if experiment_id in self._experiments:
            exp = self._experiments[experiment_id]
            exp.status = status
            exp.end_time = datetime.utcnow()
            logger.info(f"Experimento finalizado: {exp.name} - {status}")

    def get_best_model(
        self,
        name: str,
        metric: str = "accuracy",
        higher_is_better: bool = True,
    ) -> Optional[ModelVersion]:
        """
        Obtém o melhor modelo baseado em uma métrica.

        Args:
            name: Nome do modelo
            metric: Métrica para comparação
            higher_is_better: Se maior é melhor

        Returns:
            Melhor versão do modelo
        """
        if name not in self._models:
            return None

        best_version = None
        best_value = float("-inf") if higher_is_better else float("inf")

        for version in self._models[name].values():
            if not version.is_active:
                continue

            metrics = version.metrics.to_dict()
            if metric in metrics:
                value = metrics[metric]
                if higher_is_better and value > best_value:
                    best_value = value
                    best_version = version
                elif not higher_is_better and value < best_value:
                    best_value = value
                    best_version = version

        return best_version

    def _calculate_model_hash(self, model_path: Path) -> str:
        """Calcula hash do arquivo do modelo."""
        hasher = hashlib.sha256()
        with open(model_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _save_metadata(self, model_dir: Path, model_version: ModelVersion) -> None:
        """Salva metadados do modelo em JSON."""
        metadata_path = model_dir / "metadata.json"

        metadata = {
            "id": str(model_version.id),
            "model_name": model_version.model_name,
            "version": model_version.version,
            "stage": model_version.stage.value,
            "description": model_version.description,
            "model_hash": model_version.model_hash,
            "metadata": {
                "name": model_version.metadata.name,
                "description": model_version.metadata.description,
                "model_type": model_version.metadata.model_type.value,
                "framework": model_version.metadata.framework.value,
                "version": model_version.metadata.version,
                "tags": model_version.metadata.tags,
                "hyperparameters": model_version.metadata.hyperparameters,
                "feature_names": model_version.metadata.feature_names,
                "target_column": model_version.metadata.target_column,
                "author": model_version.metadata.author,
                "created_at": model_version.metadata.created_at.isoformat(),
            },
            "metrics": model_version.metrics.to_dict(),
            "created_at": model_version.created_at.isoformat(),
        }

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def _get_comparison_recommendation(
        self,
        metrics_comparison: dict[str, dict],
    ) -> str:
        """Gera recomendação baseada na comparação de métricas."""
        improvements = 0
        regressions = 0

        for metric_info in metrics_comparison.values():
            if metric_info.get("improved"):
                improvements += 1
            else:
                regressions += 1

        if improvements > regressions:
            return "A versão mais recente apresenta melhorias significativas"
        elif regressions > improvements:
            return "A versão mais recente apresenta regressões - avaliar rollback"
        else:
            return "Performance similar entre versões"

    def get_model_lineage(self, name: str, version: str) -> dict[str, Any]:
        """
        Obtém lineage do modelo (histórico de transformações).

        Args:
            name: Nome do modelo
            version: Versão

        Returns:
            Informações de lineage
        """
        model_version = self.get_model_version(name, version)
        if not model_version:
            return {}

        return {
            "model_name": name,
            "version": version,
            "created_at": model_version.created_at.isoformat(),
            "training_data": model_version.metadata.training_data_info,
            "features_used": model_version.metadata.feature_names,
            "hyperparameters": model_version.metadata.hyperparameters,
            "framework": model_version.metadata.framework.value,
            "author": model_version.metadata.author,
            "stage_history": self._get_stage_history(name, version),
        }

    def _get_stage_history(self, name: str, version: str) -> list[dict]:
        """Obtém histórico de estágios (simplificado)."""
        model_version = self.get_model_version(name, version)
        if not model_version:
            return []

        history = [
            {
                "stage": ModelStage.DEVELOPMENT.value,
                "timestamp": model_version.created_at.isoformat(),
                "by": model_version.metadata.author or "system",
            }
        ]

        if model_version.promoted_at:
            history.append({
                "stage": model_version.stage.value,
                "timestamp": model_version.promoted_at.isoformat(),
                "by": model_version.promoted_by or "system",
            })

        return history


# Instância global
model_registry = ModelRegistry()
