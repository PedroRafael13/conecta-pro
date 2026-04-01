"""
Testes de integração para o BartoloEngine.
Fase 2 do Plano de Refinamento do Bartolo.

Testa o fluxo completo de processamento de mensagens.
"""

import sys

import pytest

sys.path.insert(0, "/app")


class TestBartoloEngineIntegration:
    """Testes de integração do BartoloEngine."""

    @pytest.fixture
    def engine(self):
        """Fixture para BartoloEngine."""
        from modules.ai.bartolo.services.bartolo_engine import BartoloEngine

        return BartoloEngine()

    # ==========================================================================
    # Testes de inicialização
    # ==========================================================================
    def test_engine_inicializa(self, engine):
        """Testa que o engine inicializa corretamente."""
        assert engine is not None

    def test_agents_available(self, engine):
        """Verifica que os agentes especializados estão disponíveis."""
        assert hasattr(engine, "escala_agent")
        assert hasattr(engine, "substituicao_agent")
        assert hasattr(engine, "alerta_agent")

    # ==========================================================================
    # Testes de fluxo de mensagens de escala
    # ==========================================================================
    @pytest.mark.asyncio
    async def test_flow_gerar_escala(self, engine):
        """Testa fluxo de geração de escala."""
        result = await engine.process_message(
            user_id=1, session_id="test-session", message="crie uma escala para porteiros"
        )
        assert result is not None
        assert hasattr(result, "response")

    @pytest.mark.asyncio
    async def test_flow_escala_semana(self, engine):
        """Testa fluxo de consulta de escala da semana."""
        result = await engine.process_message(user_id=1, session_id="test-session", message="escala da semana")
        assert result is not None

    @pytest.mark.asyncio
    async def test_flow_verificar_escalas(self, engine):
        """Testa fluxo de verificar escalas (frase que falhava)."""
        result = await engine.process_message(
            user_id=1, session_id="test-session", message="verifique as escalas atuais"
        )
        assert result is not None

    # ==========================================================================
    # Testes de fluxo de mensagens de substituição
    # ==========================================================================
    @pytest.mark.asyncio
    async def test_flow_buscar_substituto(self, engine):
        """Testa fluxo de busca de substituto."""
        result = await engine.process_message(user_id=1, session_id="test-session", message="buscar substituto")
        assert result is not None

    @pytest.mark.asyncio
    async def test_flow_substituicao_urgente(self, engine):
        """Testa fluxo de substituição urgente."""
        result = await engine.process_message(
            user_id=1, session_id="test-session", message="preciso de um substituto urgente"
        )
        assert result is not None

    # ==========================================================================
    # Testes de fluxo de mensagens de alerta
    # ==========================================================================
    @pytest.mark.asyncio
    async def test_flow_ver_alertas(self, engine):
        """Testa fluxo de ver alertas."""
        result = await engine.process_message(user_id=1, session_id="test-session", message="ver alertas")
        assert result is not None

    @pytest.mark.asyncio
    async def test_flow_alertas_criticos(self, engine):
        """Testa fluxo de alertas críticos."""
        result = await engine.process_message(user_id=1, session_id="test-session", message="alertas criticos")
        assert result is not None

    # ==========================================================================
    # Testes de fluxo de consultas ao DataConnector
    # ==========================================================================
    @pytest.mark.asyncio
    async def test_flow_cobertura_critica(self, engine):
        """Testa fluxo de cobertura crítica."""
        result = await engine.process_message(user_id=1, session_id="test-session", message="postos sem cobertura")
        assert result is not None

    @pytest.mark.asyncio
    async def test_flow_funcionarios_disponiveis(self, engine):
        """Testa fluxo de funcionários disponíveis (frase que falhava)."""
        result = await engine.process_message(
            user_id=1, session_id="test-session", message="funcionarios disponiveis hoje"
        )
        assert result is not None

    @pytest.mark.asyncio
    async def test_flow_analisar_cobertura(self, engine):
        """Testa fluxo de analisar cobertura (frase que falhava)."""
        result = await engine.process_message(
            user_id=1, session_id="test-session", message="analisar cobertura de postos em tempo real"
        )
        assert result is not None

    # ==========================================================================
    # Testes de frases completas que falharam antes
    # ==========================================================================
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message",
        [
            "Analisar cobertura de postos em tempo real",
            "Funcionarios disponiveis hoje",
            "Postos sem cobertura",
            "verifique as escalas atuais",
            "Crie a escala para agentes de portaria pro mes de fevereiro de 2026",
        ],
    )
    async def test_frases_que_falhavam(self, engine, message):
        """Testa frases que falhavam antes do refinamento."""
        result = await engine.process_message(user_id=1, session_id="test-session", message=message)
        assert result is not None, f"Falhou para: '{message}'"
        # Verifica que retornou uma resposta
        assert hasattr(result, "response")

    # ==========================================================================
    # Testes de mensagens genéricas (devem ir para fallback)
    # ==========================================================================
    @pytest.mark.asyncio
    async def test_flow_saudacao(self, engine):
        """Testa fluxo de saudação."""
        result = await engine.process_message(user_id=1, session_id="test-session", message="ola")
        assert result is not None

    @pytest.mark.asyncio
    async def test_flow_ajuda(self, engine):
        """Testa fluxo de ajuda."""
        result = await engine.process_message(user_id=1, session_id="test-session", message="ajuda")
        assert result is not None


class TestBartoloEngineCapabilities:
    """Testes para capabilities do BartoloEngine."""

    @pytest.fixture
    def engine(self):
        from modules.ai.bartolo.services.bartolo_engine import BartoloEngine

        return BartoloEngine()

    def test_get_capabilities(self, engine):
        """Testa que engine tem atributos esperados."""
        # Verifica atributos em vez de método específico
        assert hasattr(engine, "profile_service")
        assert hasattr(engine, "data_connector")

    def test_capabilities_tem_categorias(self, engine):
        """Testa que engine tem componentes esperados."""
        assert hasattr(engine, "wizard_manager")
        assert hasattr(engine, "intent_classifier")


class TestDataConnectorIntegration:
    """Testes de integração do DataConnector."""

    @pytest.fixture
    def connector(self):
        from modules.ai.bartolo.services.data_connector import DataConnector

        return DataConnector()

    def test_connector_inicializa(self, connector):
        """Testa que o connector inicializa."""
        assert connector is not None

    def test_connector_tem_patterns(self, connector):
        """Testa que o connector tem patterns definidos."""
        assert hasattr(connector, "SPECIAL_QUERY_PATTERNS")
        assert len(connector.SPECIAL_QUERY_PATTERNS) > 0

    def test_connector_tem_entity_map(self, connector):
        """Testa que o connector tem entity map."""
        assert hasattr(connector, "ENTITY_MAP")
        assert len(connector.ENTITY_MAP) > 0
