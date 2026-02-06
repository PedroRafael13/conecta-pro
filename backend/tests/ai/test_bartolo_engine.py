"""
Testes do BartoloEngine - Motor Principal do Bartolo.

Testa especificamente:
- Bug #2: _is_query_intent() permite consultas com wizard ativo
- Bug #5: process_message() retorna dados direto sem LLM
- Fluxo de processamento de mensagens
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

# Importação condicional
try:
    from modules.ai.bartolo.services.bartolo_engine import BartoloEngine, BartoloResponse

    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False

pytestmark = pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Módulo Bartolo não disponível")


class TestIsQueryIntent:
    """Testes para _is_query_intent() - Bug #2 fix.

    Este método decide se a mensagem é consulta (bypass wizard)
    ou resposta ao wizard ativo.
    """

    def setup_method(self):
        with patch.multiple(
            "modules.ai.bartolo.services.bartolo_engine",
            LLMProvider=MagicMock,
            ContextManager=MagicMock,
            IntentClassifier=MagicMock,
        ):
            self.engine = BartoloEngine()

    # =====================================================================
    # CONSULTAS - Deve retornar True
    # =====================================================================

    def test_pergunta_quais_funcionarios(self):
        """'Quais funcionários...' é consulta."""
        assert self.engine._is_query_intent("Quais funcionários estão escalados para o turno da noite?") is True

    def test_pergunta_quantos(self):
        """'Quantos...' é consulta."""
        assert self.engine._is_query_intent("Quantos funcionários estão trabalhando?") is True

    def test_pergunta_quem(self):
        """'Quem...' é consulta."""
        assert self.engine._is_query_intent("Quem está de folga hoje?") is True

    def test_pergunta_com_interrogacao(self):
        """Qualquer mensagem com ? é consulta."""
        assert self.engine._is_query_intent("O turno começa às 22h?") is True

    def test_verbo_mostrar(self):
        """'Mostrar...' é consulta."""
        assert self.engine._is_query_intent("Mostrar escala de hoje") is True

    def test_verbo_listar(self):
        """'Listar...' é consulta."""
        assert self.engine._is_query_intent("Listar postos ativos") is True

    def test_verbo_ver(self):
        """'Ver...' é consulta."""
        assert self.engine._is_query_intent("Ver funcionários do turno noturno") is True

    def test_verbo_verificar(self):
        """'Verificar...' é consulta."""
        assert self.engine._is_query_intent("Verificar escalas pendentes") is True

    def test_verbo_consultar(self):
        """'Consultar...' é consulta."""
        assert self.engine._is_query_intent("Consultar banco de horas") is True

    def test_verbo_buscar(self):
        """'Buscar...' é consulta."""
        assert self.engine._is_query_intent("Buscar funcionário KALEL") is True

    def test_verbo_checar(self):
        """'Checar...' é consulta."""
        assert self.engine._is_query_intent("Checar ocorrências de hoje") is True

    def test_verbo_conferir(self):
        """'Conferir...' é consulta."""
        assert self.engine._is_query_intent("Conferir atrasos do dia") is True

    def test_existe(self):
        """'Existe...' é consulta."""
        assert self.engine._is_query_intent("Existe algum alerta?") is True

    def test_tem(self):
        """'Tem...' é consulta."""
        assert self.engine._is_query_intent("Tem funcionário sem escala?") is True

    def test_skill_command(self):
        """Comandos com / são sempre consultas."""
        assert self.engine._is_query_intent("/escala visualizar") is True

    def test_verbo_criar_e_consulta(self):
        """'Criar...' é ação (tratada como consulta pelo engine)."""
        assert self.engine._is_query_intent("Criar nova escala") is True

    def test_frase_longa_e_consulta(self):
        """Frases com 4+ palavras são tratadas como consulta."""
        assert self.engine._is_query_intent("preciso saber os funcionários escalados hoje") is True

    # =====================================================================
    # RESPOSTAS AO WIZARD - Deve retornar False
    # =====================================================================

    def test_resposta_sim(self):
        """'sim' é resposta ao wizard."""
        assert self.engine._is_query_intent("sim") is False

    def test_resposta_nao(self):
        """'não' é resposta ao wizard."""
        assert self.engine._is_query_intent("não") is False

    def test_resposta_ok(self):
        """'ok' é resposta ao wizard."""
        assert self.engine._is_query_intent("ok") is False

    def test_resposta_continuar(self):
        """'continuar' é resposta ao wizard."""
        assert self.engine._is_query_intent("continuar") is False

    def test_resposta_rotina(self):
        """'rotina' é resposta ao wizard (tipo de ronda)."""
        assert self.engine._is_query_intent("rotina") is False

    def test_resposta_programada(self):
        """'programada' é resposta ao wizard."""
        assert self.engine._is_query_intent("programada") is False

    def test_resposta_noturna(self):
        """'noturna' é resposta ao wizard."""
        assert self.engine._is_query_intent("noturna") is False

    def test_resposta_urgente_curta(self):
        """'urgente' é resposta ao wizard."""
        assert self.engine._is_query_intent("urgente") is False

    def test_resposta_normal(self):
        """'normal' é resposta ao wizard."""
        assert self.engine._is_query_intent("normal") is False


class TestProcessMessageDataConnector:
    """Testa process_message() retornando dados direto sem LLM - Bug #5 fix."""

    def setup_method(self):
        with patch.multiple(
            "modules.ai.bartolo.services.bartolo_engine",
            LLMProvider=MagicMock,
            ContextManager=MagicMock,
            IntentClassifier=MagicMock,
        ):
            self.engine = BartoloEngine()

    @pytest.mark.asyncio
    async def test_data_query_retorna_direto_sem_llm(self):
        """Quando data_connector retorna dados, bypassa LLM."""
        # Mock profile_service
        mock_context = MagicMock()
        mock_context.role = None
        mock_context.name = "Test User"
        self.engine.profile_service.get_user_context = AsyncMock(return_value=mock_context)
        self.engine.profile_service.set_db = MagicMock()

        # Mock data_connector que retorna dados
        mock_data_result = {
            "entity": "funcionarios",
            "query_type": "list",
            "total_count": 9,
            "data": ["FUNC1", "FUNC2"],
            "message": "Encontrei 9 funcionários:\n- FUNC1\n- FUNC2",
        }

        with patch.object(self.engine, "_check_data_query", new_callable=AsyncMock, return_value=mock_data_result):
            # Mock intent classifier
            mock_intent = MagicMock()
            mock_intent.intent.value = "query"
            mock_intent.confidence = 0.8
            mock_intent.entities = {}
            self.engine.intent_classifier.classify = MagicMock(return_value=mock_intent)

            # Mock LLM fallback
            self.engine.llm_fallback_classifier.should_use_fallback = MagicMock(return_value=False)

            # Mock context manager para followup
            self.engine.context_manager.get_context = AsyncMock(return_value=MagicMock(messages=[]))

            result = await self.engine.process_message(
                user_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                session_id="test-session",
                message="Quais funcionários estão no turno da noite?",
            )

            assert isinstance(result, BartoloResponse)
            assert result.model_used == "data_connector"
            assert result.data_results is not None
            assert result.data_results["total_count"] == 9
            assert "Encontrei 9 funcionários" in result.response

    @pytest.mark.asyncio
    async def test_query_com_wizard_ativo_nao_vai_pro_wizard(self):
        """Bug #2: Consulta com wizard ativo não vai pro wizard."""
        mock_context = MagicMock()
        mock_context.role = None
        mock_context.name = "Test"
        self.engine.profile_service.get_user_context = AsyncMock(return_value=mock_context)
        self.engine.profile_service.set_db = MagicMock()

        # Simula wizard ativo
        self.engine.wizard_manager.has_active_wizard = MagicMock(return_value=True)
        self.engine.wizard_manager.process_input = MagicMock(return_value=None)

        mock_data_result = {
            "entity": "funcionarios",
            "query_type": "list",
            "total_count": 5,
            "data": ["A", "B", "C", "D", "E"],
            "message": "Encontrei 5 funcionários",
        }

        with patch.object(self.engine, "_check_data_query", new_callable=AsyncMock, return_value=mock_data_result):
            mock_intent = MagicMock()
            mock_intent.intent.value = "query"
            mock_intent.confidence = 0.8
            mock_intent.entities = {}
            self.engine.intent_classifier.classify = MagicMock(return_value=mock_intent)
            self.engine.llm_fallback_classifier.should_use_fallback = MagicMock(return_value=False)
            self.engine.context_manager.get_context = AsyncMock(return_value=MagicMock(messages=[]))

            result = await self.engine.process_message(
                user_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                session_id="test-session",
                message="Quais funcionários estão trabalhando agora?",
            )

            # Deve retornar dados, não resposta de wizard
            assert result.model_used == "data_connector"
            assert "Encontrei 5 funcionários" in result.response


class TestBartoloResponseStructure:
    """Testa estrutura da BartoloResponse."""

    def test_response_campos_obrigatorios(self):
        """BartoloResponse tem todos os campos."""
        response = BartoloResponse(
            message_id=uuid4(),
            session_id="test",
            response="Teste",
        )
        assert response.message_id is not None
        assert response.session_id == "test"
        assert response.response == "Teste"
        assert response.processing_time_ms == 0
        assert response.bartolo_mood == "professional"
        assert response.suggestions == []
        assert response.actions == []

    def test_response_com_data_results(self):
        """BartoloResponse com data_results."""
        response = BartoloResponse(
            message_id=uuid4(),
            session_id="test",
            response="Dados",
            data_results={"total_count": 10},
            model_used="data_connector",
        )
        assert response.data_results["total_count"] == 10
        assert response.model_used == "data_connector"
