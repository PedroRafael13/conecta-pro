"""Testes para o Model Registry."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime

from sklearn.linear_model import LogisticRegression

from modules.analytics.ml.registry.model_registry import (
    ModelRegistry,
    ModelVersion,
    ModelMetadata,
    ModelMetrics,
    ModelStage,
    ModelType,
    ModelFramework,
)


@pytest.fixture
def temp_storage():
    """Diretório temporário para storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def registry(temp_storage):
    """Instância do ModelRegistry."""
    return ModelRegistry(storage_path=temp_storage)


@pytest.fixture
def sample_model():
    """Modelo sklearn de exemplo."""
    model = LogisticRegression()
    # Treinar com dados dummy
    import numpy as np
    X = np.random.randn(100, 5)
    y = np.random.randint(0, 2, 100)
    model.fit(X, y)
    return model


class TestModelRegistration:
    """Testes de registro de modelos."""

    def test_register_model_creates_version(
        self,
        registry,
        sample_model,
    ):
        """Deve criar versão ao registrar modelo."""
        # Act
        version = registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
            description="Test model",
        )

        # Assert
        assert isinstance(version, ModelVersion)
        assert version.model_name == "test_model"
        assert version.version == "1.0.0"
        assert version.stage == ModelStage.DEVELOPMENT

    def test_register_model_saves_file(
        self,
        registry,
        sample_model,
        temp_storage,
    ):
        """Deve salvar arquivo do modelo."""
        # Act
        version = registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
        )

        # Assert
        model_path = Path(version.model_path)
        assert model_path.exists()

    def test_register_model_with_metrics(
        self,
        registry,
        sample_model,
    ):
        """Deve armazenar métricas."""
        # Arrange
        metrics = ModelMetrics(
            accuracy=0.85,
            precision=0.82,
            recall=0.88,
        )

        # Act
        version = registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
            metrics=metrics,
        )

        # Assert
        assert version.metrics.accuracy == 0.85
        assert version.metrics.precision == 0.82

    def test_register_model_with_hyperparameters(
        self,
        registry,
        sample_model,
    ):
        """Deve armazenar hiperparâmetros."""
        # Arrange
        hyperparameters = {"C": 1.0, "max_iter": 100}

        # Act
        version = registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
            hyperparameters=hyperparameters,
        )

        # Assert
        assert version.metadata.hyperparameters == hyperparameters

    def test_register_multiple_versions(
        self,
        registry,
        sample_model,
    ):
        """Deve permitir múltiplas versões."""
        # Act
        v1 = registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
        )
        v2 = registry.register_model(
            model=sample_model,
            name="test_model",
            version="2.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
        )

        # Assert
        versions = registry.list_versions("test_model")
        assert len(versions) == 2


class TestModelRetrieval:
    """Testes de recuperação de modelos."""

    def test_get_model_by_version(
        self,
        registry,
        sample_model,
    ):
        """Deve recuperar modelo por versão."""
        # Arrange
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
        )

        # Act
        loaded_model = registry.get_model("test_model", version="1.0.0")

        # Assert
        assert loaded_model is not None
        assert hasattr(loaded_model, "predict")

    def test_get_model_version_info(
        self,
        registry,
        sample_model,
    ):
        """Deve recuperar informações da versão."""
        # Arrange
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
        )

        # Act
        version_info = registry.get_model_version("test_model", "1.0.0")

        # Assert
        assert version_info is not None
        assert version_info.version == "1.0.0"

    def test_get_nonexistent_model_returns_none(self, registry):
        """Deve retornar None para modelo inexistente."""
        model = registry.get_model("nonexistent")
        assert model is None

    def test_get_production_model(
        self,
        registry,
        sample_model,
    ):
        """Deve recuperar modelo em produção."""
        # Arrange
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
        )
        registry.promote_model("test_model", "1.0.0", ModelStage.PRODUCTION)

        # Act
        prod_model = registry.get_production_model("test_model")

        # Assert
        assert prod_model is not None


class TestModelPromotion:
    """Testes de promoção de modelos."""

    def test_promote_to_staging(
        self,
        registry,
        sample_model,
    ):
        """Deve promover para staging."""
        # Arrange
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
        )

        # Act
        success = registry.promote_model(
            "test_model",
            "1.0.0",
            ModelStage.STAGING,
        )

        # Assert
        assert success
        version = registry.get_model_version("test_model", "1.0.0")
        assert version.stage == ModelStage.STAGING

    def test_promote_to_production(
        self,
        registry,
        sample_model,
    ):
        """Deve promover para produção."""
        # Arrange
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
        )

        # Act
        success = registry.promote_model(
            "test_model",
            "1.0.0",
            ModelStage.PRODUCTION,
        )

        # Assert
        assert success
        version = registry.get_model_version("test_model", "1.0.0")
        assert version.stage == ModelStage.PRODUCTION

    def test_promote_archives_previous_production(
        self,
        registry,
        sample_model,
    ):
        """Deve arquivar versão anterior de produção."""
        # Arrange
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
        )
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="2.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
        )
        registry.promote_model("test_model", "1.0.0", ModelStage.PRODUCTION)

        # Act
        registry.promote_model("test_model", "2.0.0", ModelStage.PRODUCTION)

        # Assert
        v1 = registry.get_model_version("test_model", "1.0.0")
        v2 = registry.get_model_version("test_model", "2.0.0")
        assert v1.stage == ModelStage.ARCHIVED
        assert v2.stage == ModelStage.PRODUCTION


class TestVersionComparison:
    """Testes de comparação de versões."""

    def test_compare_versions_metrics(
        self,
        registry,
        sample_model,
    ):
        """Deve comparar métricas entre versões."""
        # Arrange
        metrics_v1 = ModelMetrics(accuracy=0.80, precision=0.78)
        metrics_v2 = ModelMetrics(accuracy=0.85, precision=0.82)

        registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
            metrics=metrics_v1,
        )
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="2.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
            metrics=metrics_v2,
        )

        # Act
        comparison = registry.compare_versions("test_model", "1.0.0", "2.0.0")

        # Assert
        assert "metrics_comparison" in comparison
        assert comparison["metrics_comparison"]["accuracy"]["improved"]

    def test_compare_versions_hyperparameters(
        self,
        registry,
        sample_model,
    ):
        """Deve comparar hiperparâmetros entre versões."""
        # Arrange
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
            hyperparameters={"C": 1.0},
        )
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="2.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
            hyperparameters={"C": 2.0},
        )

        # Act
        comparison = registry.compare_versions("test_model", "1.0.0", "2.0.0")

        # Assert
        assert "hyperparameter_diff" in comparison
        assert "C" in comparison["hyperparameter_diff"]["changed"]


class TestModelDeletion:
    """Testes de deleção de modelos."""

    def test_delete_version_soft_delete(
        self,
        registry,
        sample_model,
    ):
        """Deve fazer soft delete."""
        # Arrange
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
        )

        # Act
        success = registry.delete_version("test_model", "1.0.0")

        # Assert
        assert success
        version = registry.get_model_version("test_model", "1.0.0")
        assert not version.is_active
        assert version.stage == ModelStage.ARCHIVED

    def test_delete_production_requires_force(
        self,
        registry,
        sample_model,
    ):
        """Deve exigir force para deletar produção."""
        # Arrange
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
        )
        registry.promote_model("test_model", "1.0.0", ModelStage.PRODUCTION)

        # Act
        success_without_force = registry.delete_version(
            "test_model", "1.0.0", force=False
        )
        success_with_force = registry.delete_version(
            "test_model", "1.0.0", force=True
        )

        # Assert
        assert not success_without_force
        assert success_with_force


class TestBestModel:
    """Testes de seleção do melhor modelo."""

    def test_get_best_model_by_accuracy(
        self,
        registry,
        sample_model,
    ):
        """Deve retornar modelo com melhor accuracy."""
        # Arrange
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
            metrics=ModelMetrics(accuracy=0.80),
        )
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="2.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
            metrics=ModelMetrics(accuracy=0.90),
        )

        # Act
        best = registry.get_best_model("test_model", metric="accuracy")

        # Assert
        assert best is not None
        assert best.version == "2.0.0"

    def test_get_best_model_lower_is_better(
        self,
        registry,
        sample_model,
    ):
        """Deve retornar modelo com menor erro."""
        # Arrange
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.REGRESSION,
            framework=ModelFramework.SKLEARN,
            metrics=ModelMetrics(mse=100),
        )
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="2.0.0",
            model_type=ModelType.REGRESSION,
            framework=ModelFramework.SKLEARN,
            metrics=ModelMetrics(mse=50),
        )

        # Act
        best = registry.get_best_model(
            "test_model",
            metric="mse",
            higher_is_better=False,
        )

        # Assert
        assert best is not None
        assert best.version == "2.0.0"


class TestModelLineage:
    """Testes de lineage do modelo."""

    def test_get_model_lineage(
        self,
        registry,
        sample_model,
    ):
        """Deve retornar lineage do modelo."""
        # Arrange
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
            feature_names=["f1", "f2", "f3"],
            author="test_user",
        )

        # Act
        lineage = registry.get_model_lineage("test_model", "1.0.0")

        # Assert
        assert lineage["model_name"] == "test_model"
        assert lineage["version"] == "1.0.0"
        assert lineage["features_used"] == ["f1", "f2", "f3"]
        assert lineage["author"] == "test_user"


class TestExperimentLogging:
    """Testes de logging de experimentos."""

    def test_log_experiment(self, registry):
        """Deve criar experimento."""
        # Act
        experiment = registry.log_experiment(
            name="experiment_1",
            model_name="test_model",
            parameters={"learning_rate": 0.01},
            description="Test experiment",
        )

        # Assert
        assert experiment is not None
        assert experiment.name == "experiment_1"
        assert experiment.status == "running"

    def test_log_metrics_to_experiment(self, registry):
        """Deve adicionar métricas ao experimento."""
        # Arrange
        experiment = registry.log_experiment(
            name="experiment_1",
            model_name="test_model",
            parameters={},
        )

        # Act
        registry.log_metrics(str(experiment.id), {"accuracy": 0.85})

        # Assert
        # Verificar que as métricas foram adicionadas
        assert "accuracy" in experiment.metrics

    def test_end_experiment(self, registry):
        """Deve finalizar experimento."""
        # Arrange
        experiment = registry.log_experiment(
            name="experiment_1",
            model_name="test_model",
            parameters={},
        )

        # Act
        registry.end_experiment(str(experiment.id), status="completed")

        # Assert
        assert experiment.status == "completed"
        assert experiment.end_time is not None
