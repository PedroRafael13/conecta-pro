"""
Testes automatizados para patterns do AlertaAgent.
Fase 2 do Plano de Refinamento do Bartolo.
"""

import pytest
import sys
sys.path.insert(0, '/app')

from modules.ai.bartolo.agents.alerta_agent import AlertaAgent, AlertaIntent


class TestAlertaAgentPatterns:
    """Testes para detecção de patterns no AlertaAgent."""

    @pytest.fixture
    def agent(self):
        """Fixture para AlertaAgent."""
        return AlertaAgent()

    # ==========================================================================
    # RESOLVER - Resolver alerta (deve vir ANTES de VER_ALERTAS)
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "resolver alerta",
        "resolva o alerta",
        "tratar alerta",
        "trate o alerta",
        "fechar alerta",
        "encerrar alerta",
        "solucionar problema",
        "solucionar alerta",
        "solucione o problema",
        "cuidar alerta",
        "atender alerta",
    ])
    def test_resolver(self, agent, message):
        """Testa detecção de RESOLVER."""
        result = agent._detect_intent(message)
        assert result == AlertaIntent.RESOLVER, f"Falhou para: '{message}'"

    # ==========================================================================
    # VER_ALERTAS - Listar alertas
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "ver alertas",
        "veja os alertas",
        "mostrar alertas",
        "mostre os alertas",
        "listar alertas",
        "liste os alertas",
        "quais alertas",
        "quantos alertas",
        "alertas do dia",
        "alertas do sistema",
        "alertas hoje",
        "notificacoes pendentes",
        "notificacoes",
        "tem algum alerta",
        "ha alerta",
    ])
    def test_ver_alertas(self, agent, message):
        """Testa detecção de VER_ALERTAS."""
        result = agent._detect_intent(message)
        assert result == AlertaIntent.VER_ALERTAS, f"Falhou para: '{message}'"

    # ==========================================================================
    # ALERTAS_CRITICOS - Apenas críticos
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "alertas criticos",
        "alerta critico",
        "alertas urgentes",
        "alertas importantes",
        "criticos primeiro",
        "urgentes primeiro",
        "mais graves",
        "mais serios",
        "mais importantes",
        "emergencia",
        "prioridade maxima",
        "prioridade alta",
    ])
    def test_alertas_criticos(self, agent, message):
        """Testa detecção de ALERTAS_CRITICOS."""
        result = agent._detect_intent(message)
        assert result == AlertaIntent.ALERTAS_CRITICOS, f"Falhou para: '{message}'"

    # ==========================================================================
    # COBERTURA - Alertas de cobertura
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "alertas de cobertura",
        "alerta de cobertura",
        "problemas com postos",
        "alertas com postos",
        "postos sem cobertura",
        "postos descobertos",
        "postos criticos",
        "cobertura critica",
        "cobertura baixa",
    ])
    def test_cobertura(self, agent, message):
        """Testa detecção de COBERTURA."""
        result = agent._detect_intent(message)
        assert result == AlertaIntent.COBERTURA, f"Falhou para: '{message}'"

    # ==========================================================================
    # DOCUMENTOS - Documentos vencendo
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "documentos vencendo",
        "documentos vencidos",
        "docs vencendo",
        "docs expirando",
        "alertas de documentos",
        "alertas de docs",
        "vencimento de documentos",
        "vencimento de docs",
        "validade de documentos",
        "CNV vencendo",
        "ASO vencido",
        "NR vencendo",
        "documentos a vencer",
    ])
    def test_documentos(self, agent, message):
        """Testa detecção de DOCUMENTOS."""
        result = agent._detect_intent(message)
        assert result == AlertaIntent.DOCUMENTOS, f"Falhou para: '{message}'"

    # ==========================================================================
    # ATRASOS - Alertas de atrasos
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "alertas de atrasos",
        "alerta de atraso",
        "funcionarios atrasados",
        "equipe atrasada",
        "atrasos de hoje",
        "atrasos do dia",
        "sem check-in",
        "sem checkin",
        "quem chegou atrasado",
        "quem nao chegou",
    ])
    def test_atrasos(self, agent, message):
        """Testa detecção de ATRASOS."""
        result = agent._detect_intent(message)
        assert result == AlertaIntent.ATRASOS, f"Falhou para: '{message}'"

    # ==========================================================================
    # URGENTE - Atenção urgente
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "urgente atencao",
        "urgente atenção",
        "precisa de atencao",
        "precisamos de atenção",
        "atencao imediata",
        "atenção urgente",
        "agora precisa",
        "ja precisamos",
    ])
    def test_urgente(self, agent, message):
        """Testa detecção de URGENTE."""
        result = agent._detect_intent(message)
        assert result == AlertaIntent.URGENTE, f"Falhou para: '{message}'"

    # ==========================================================================
    # IGNORAR - Dispensar alerta
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "ignorar alerta",
        "ignore o alerta",
        "dispensar alerta",
        "dispense o alerta",
        "deixar para depois",
        "deixe para depois",
        "nao e urgente",
        "não é importante",
        "adiar alerta",
        "adie o alerta",
    ])
    def test_ignorar(self, agent, message):
        """Testa detecção de IGNORAR."""
        result = agent._detect_intent(message)
        assert result == AlertaIntent.IGNORAR, f"Falhou para: '{message}'"

    # ==========================================================================
    # Testes de frases completas do usuário
    # ==========================================================================
    @pytest.mark.parametrize("message,expected_intent", [
        ("me mostre todos os alertas do sistema", AlertaIntent.VER_ALERTAS),
        ("quais sao os alertas criticos agora", AlertaIntent.ALERTAS_CRITICOS),
        ("resolver o alerta de cobertura do posto Centro", AlertaIntent.RESOLVER),
        ("documentos que estao vencendo essa semana", AlertaIntent.DOCUMENTOS),
        ("quem esta atrasado hoje", AlertaIntent.ATRASOS),
        ("preciso de atencao imediata nos problemas", AlertaIntent.URGENTE),
        ("ignore esse alerta por enquanto", AlertaIntent.IGNORAR),
        ("postos com problemas de cobertura", AlertaIntent.COBERTURA),
    ])
    def test_frases_completas(self, agent, message, expected_intent):
        """Testa frases completas que o usuário pode digitar."""
        result = agent._detect_intent(message)
        assert result == expected_intent, f"Falhou para: '{message}' - esperado {expected_intent}, obtido {result}"

    # ==========================================================================
    # Teste de ordenação (RESOLVER antes de VER_ALERTAS)
    # ==========================================================================
    def test_resolver_antes_de_ver_alertas(self, agent):
        """Garante que 'resolver alerta' não detecta VER_ALERTAS."""
        result = agent._detect_intent("resolver o alerta")
        assert result == AlertaIntent.RESOLVER, "Detectou VER_ALERTAS em vez de RESOLVER"

    # ==========================================================================
    # Testes negativos - não devem detectar intent
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "ola",
        "bom dia",
        "ajuda",
        "obrigado",
    ])
    def test_nao_deve_detectar_intent(self, agent, message):
        """Testa que mensagens genéricas não detectam intent."""
        result = agent._detect_intent(message)
        assert result is None, f"Detectou incorretamente para: '{message}'"


class TestAlertaAgentProcess:
    """Testes para o método process do AlertaAgent."""

    @pytest.fixture
    def agent(self):
        return AlertaAgent()

    @pytest.mark.asyncio
    async def test_process_ver_alertas(self, agent):
        """Testa processamento de ver alertas."""
        result = await agent.process("ver alertas")
        assert result is not None
        assert "intent" in result
        assert result["intent"] == AlertaIntent.VER_ALERTAS.value

    @pytest.mark.asyncio
    async def test_process_criticos(self, agent):
        """Testa processamento de alertas críticos."""
        result = await agent.process("alertas criticos")
        assert result is not None
        assert "intent" in result
        assert result["intent"] == AlertaIntent.ALERTAS_CRITICOS.value

    @pytest.mark.asyncio
    async def test_process_default_returns_none(self, agent):
        """Testa que mensagens genéricas retornam None."""
        result = await agent.process("bom dia")
        assert result is None, "Deveria retornar None para mensagem genérica"
