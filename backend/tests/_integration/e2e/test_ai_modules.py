"""
Testes E2E - Módulos de IA.

Testa os endpoints dos módulos de Inteligência Artificial.
Rotas seguem padrão: /api/v1/ai/{module}/{module}/
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAIChatbot:
    """Testes do módulo AI Chatbot."""

    async def test_chatbot_endpoint_removed(self, client: AsyncClient):
        """Verifica que o endpoint do chatbot Bartolo foi removido."""
        response = await client.get("/api/v1/ai/bartolo/modules")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestAIOCR:
    """Testes do módulo AI OCR."""

    async def test_ocr_scans_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de OCR scans existe."""
        response = await client.get("/api/v1/ai/ocr/ocr/scans")
        assert response.status_code in [200, 401, 403, 422]

    async def test_ocr_templates_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de templates OCR existe."""
        response = await client.get("/api/v1/ai/ocr/ocr/templates")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestAIReportGenerator:
    """Testes do módulo AI Report Generator."""

    @pytest.mark.xfail(reason="Bug: sync query com AsyncSession no repository")
    async def test_reports_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de relatórios IA existe."""
        response = await client.get("/api/v1/ai/reports/reports")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestAISentiment:
    """Testes do módulo AI Sentiment Analysis."""

    async def test_sentiment_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de análise de sentimento existe."""
        response = await client.get("/api/v1/ai/sentiment/sentiment/analyses")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestAIFraudDetection:
    """Testes do módulo AI Fraud Detection."""

    async def test_fraud_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de detecção de fraude existe."""
        response = await client.get("/api/v1/ai/fraud/fraud/rules")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestAIContractAnalysis:
    """Testes do módulo AI Contract Analysis."""

    async def test_contracts_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de análise de contratos existe."""
        response = await client.get("/api/v1/ai/contracts/contract-analysis/analyses")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestAIKnowledgeBase:
    """Testes do módulo AI Knowledge Base."""

    async def test_kb_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint da base de conhecimento existe."""
        response = await client.get("/api/v1/ai/knowledge-base/knowledge-base/")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestAIEmailAssistant:
    """Testes do módulo AI Email Assistant."""

    async def test_email_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint do assistente de email existe."""
        response = await client.get("/api/v1/ai/email/email-assistant/emails")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestAIVoiceRecognition:
    """Testes do módulo AI Voice Recognition."""

    async def test_voice_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de reconhecimento de voz existe."""
        response = await client.get("/api/v1/ai/voice/voice/recordings")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestAIWorkflowOptimizer:
    """Testes do módulo AI Workflow Optimizer."""

    async def test_workflows_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint do otimizador de workflows existe."""
        response = await client.get("/api/v1/ai/workflows/workflow-optimizer/workflows")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestAIDataQuality:
    """Testes do módulo AI Data Quality."""

    @pytest.mark.xfail(reason="Bug: sync query com AsyncSession no repository")
    async def test_data_quality_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de qualidade de dados existe."""
        response = await client.get("/api/v1/ai/data-quality/data-quality/checks")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestAIMeetingAssistant:
    """Testes do módulo AI Meeting Assistant."""

    async def test_meetings_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint do assistente de reuniões existe."""
        response = await client.get("/api/v1/ai/meetings/meeting-assistant/meetings")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestAISignature:
    """Testes do módulo AI Signature Recognition."""

    async def test_signature_health_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de health signature existe."""
        response = await client.get("/api/v1/ai/signatures/signature/health")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestAIForecast:
    """Testes do módulo AI Inventory Forecast."""

    async def test_forecast_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de previsão de inventário existe."""
        response = await client.get("/api/v1/ai/forecast/inventory-forecast/forecasts")
        assert response.status_code in [200, 401, 403, 422]
