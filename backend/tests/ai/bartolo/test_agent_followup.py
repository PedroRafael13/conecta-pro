"""
Testes para detecção de follow-up no BartoloEngine.

Verifica que o engine detecta quando a última interação foi com um
agente especializado e roteia follow-up de volta para o mesmo agente.
"""

import pytest
import sys
sys.path.insert(0, '/app')

from unittest.mock import AsyncMock, MagicMock, patch
from modules.ai.bartolo.services.bartolo_engine import BartoloEngine


def _make_context_mock(messages):
    """Cria mock de ConversationContext com messages."""
    ctx = MagicMock()
    ctx.messages = messages
    return ctx


class TestFollowupDetection:
    """Testes para _check_agent_followup no BartoloEngine."""

    @pytest.fixture
    def engine(self):
        """Fixture para BartoloEngine com mocks."""
        engine = BartoloEngine.__new__(BartoloEngine)
        engine.context_manager = AsyncMock()
        engine.escala_agent = MagicMock()
        engine.substituicao_agent = MagicMock()
        engine.alerta_agent = MagicMock()
        engine.specialized_agents_map = {
            "escala": "escala",
            "substituicao": "substituicao",
            "alerta": "alerta",
        }
        return engine

    @pytest.mark.asyncio
    async def test_followup_detected_with_agent_context(self, engine):
        """Testa que follow-up é detectado quando há contexto de agente."""
        engine.context_manager.get_context = AsyncMock(return_value=_make_context_mock([
            {
                "role": "user",
                "content": "gere uma escala para porteiros",
                "metadata": {"intent": "gerar_escala"},
            },
            {
                "role": "assistant",
                "content": "Qual tipo de escala deseja?",
                "metadata": {
                    "model": "specialized_agent",
                    "agent_type": "escala",
                    "agent_intent": "gerar_escala",
                },
            },
        ]))

        followup_response = {
            "response": "Escala 12x36 selecionada.",
            "intent": "gerar_escala",
            "data": {"scale_type": "12x36"},
            "suggestions": ["Confirmar"],
        }
        engine.escala_agent.process_followup = AsyncMock(return_value=followup_response)

        result = await engine._check_agent_followup(1, "session-1", "12x36")

        assert result is not None
        assert result["response"] == "Escala 12x36 selecionada."
        engine.escala_agent.process_followup.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_followup_without_agent_context(self, engine):
        """Testa que não detecta follow-up sem contexto de agente."""
        engine.context_manager.get_context = AsyncMock(return_value=_make_context_mock([
            {
                "role": "user",
                "content": "bom dia",
                "metadata": {},
            },
            {
                "role": "assistant",
                "content": "Bom dia! Como posso ajudar?",
                "metadata": {"model": "claude-3-haiku"},
            },
        ]))

        result = await engine._check_agent_followup(1, "session-1", "12x36")
        assert result is None

    @pytest.mark.asyncio
    async def test_no_followup_empty_history(self, engine):
        """Testa que não detecta follow-up com histórico vazio."""
        engine.context_manager.get_context = AsyncMock(return_value=_make_context_mock([]))

        result = await engine._check_agent_followup(1, "session-1", "12x36")
        assert result is None

    @pytest.mark.asyncio
    async def test_no_followup_none_context(self, engine):
        """Testa que não detecta follow-up com contexto None."""
        engine.context_manager.get_context = AsyncMock(return_value=None)

        result = await engine._check_agent_followup(1, "session-1", "12x36")
        assert result is None

    @pytest.mark.asyncio
    async def test_followup_falls_through_to_process(self, engine):
        """Testa que se process_followup retorna None, tenta process normal."""
        engine.context_manager.get_context = AsyncMock(return_value=_make_context_mock([
            {
                "role": "assistant",
                "content": "Qual tipo de escala?",
                "metadata": {
                    "model": "specialized_agent",
                    "agent_type": "escala",
                    "agent_intent": "gerar_escala",
                },
            },
        ]))

        engine.escala_agent.process_followup = AsyncMock(return_value=None)
        engine.escala_agent.process = AsyncMock(return_value={
            "response": "Resposta do process normal",
            "intent": "escala_semana",
        })

        result = await engine._check_agent_followup(1, "session-1", "ver escalas")

        assert result is not None
        assert result["response"] == "Resposta do process normal"

    @pytest.mark.asyncio
    async def test_followup_error_handling(self, engine):
        """Testa que erros no follow-up são tratados graciosamente."""
        engine.context_manager.get_context = AsyncMock(
            side_effect=Exception("DB error")
        )

        result = await engine._check_agent_followup(1, "session-1", "12x36")
        assert result is None


class TestWizardFuzzyMatching:
    """Testes para fuzzy matching no wizard CHOICE."""

    def test_fuzzy_match_validates_substring(self):
        """Testa que substring parcial é aceita na validação."""
        from modules.ai.bartolo.wizards.base_wizard import BaseWizard, WizardStep, StepType

        step = WizardStep(
            id="tipo_escala",
            name="Tipo de Escala",
            description="Selecione o tipo",
            step_type=StepType.CHOICE,
            question="Qual tipo?",
            options=["12x36 Diurno", "12x36 Noturno", "5x2 Comercial", "6x1 Operacional"],
        )

        class TestWizard(BaseWizard):
            def get_wizard_type(self): return "test"
            def get_wizard_name(self): return "Test"
            def get_wizard_description(self): return "Test"
            def _setup_steps(self): self.steps = [step]
            async def process_result(self, data): return {}

        wizard = TestWizard(user_id=1, session_id="test")

        error = wizard._validate_input(step, "12x36")
        assert error is None, f"Deveria aceitar fuzzy match '12x36', mas retornou: {error}"

        error = wizard._validate_input(step, "5x2")
        assert error is None, f"Deveria aceitar fuzzy match '5x2', mas retornou: {error}"

    def test_fuzzy_match_processes_correct_option(self):
        """Testa que _process_value retorna a opção correta no fuzzy match."""
        from modules.ai.bartolo.wizards.base_wizard import BaseWizard, WizardStep, StepType

        step = WizardStep(
            id="tipo_escala",
            name="Tipo de Escala",
            description="Selecione o tipo",
            step_type=StepType.CHOICE,
            question="Qual tipo?",
            options=["12x36 Diurno", "12x36 Noturno", "5x2 Comercial"],
        )

        class TestWizard(BaseWizard):
            def get_wizard_type(self): return "test"
            def get_wizard_name(self): return "Test"
            def get_wizard_description(self): return "Test"
            def _setup_steps(self): self.steps = [step]
            async def process_result(self, data): return {}

        wizard = TestWizard(user_id=1, session_id="test")

        result = wizard._process_value(step, "12x36")
        assert result == "12x36 Diurno", f"Esperado '12x36 Diurno', obtido '{result}'"

        result = wizard._process_value(step, "5x2")
        assert result == "5x2 Comercial", f"Esperado '5x2 Comercial', obtido '{result}'"

    def test_short_input_rejected(self):
        """Testa que inputs muito curtos não fazem fuzzy match."""
        from modules.ai.bartolo.wizards.base_wizard import BaseWizard, WizardStep, StepType

        step = WizardStep(
            id="test",
            name="Test",
            description="Test",
            step_type=StepType.CHOICE,
            question="Qual?",
            options=["12x36 Diurno", "5x2 Comercial"],
        )

        class TestWizard(BaseWizard):
            def get_wizard_type(self): return "test"
            def get_wizard_name(self): return "Test"
            def get_wizard_description(self): return "Test"
            def _setup_steps(self): self.steps = [step]
            async def process_result(self, data): return {}

        wizard = TestWizard(user_id=1, session_id="test")

        error = wizard._validate_input(step, "ab")
        assert error is not None, "Deveria rejeitar input muito curto"
