"""
Testes automatizados para patterns do SubstituicaoAgent.
Fase 2 do Plano de Refinamento do Bartolo.
"""

import pytest
import sys
sys.path.insert(0, '/app')

from modules.ai.bartolo.agents.substituicao_agent import SubstituicaoAgent, SubstituicaoIntent


class TestSubstituicaoAgentPatterns:
    """Testes para detecção de patterns no SubstituicaoAgent."""

    @pytest.fixture
    def agent(self):
        """Fixture para SubstituicaoAgent."""
        return SubstituicaoAgent()

    # ==========================================================================
    # BUSCAR_SUBSTITUTO - Buscar substituto
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "buscar substituto",
        "busque um substituto",
        "encontrar substituto",
        "encontre um substituto",
        "achar substituto",
        "ache um substituto",
        "preciso de substituto",
        "precisamos de um substituto",
        "quem pode cobrir",
        "quem consegue substituir",
        "tem alguem para cobrir",
        "tem alguem para substituir",
        "ha alguem para cobrir",
        "arranjar substituto",
        "arrumar um substituto",
        "conseguir substituto",
        "alguem para cobrir",
        "funcionario para cobrir",
    ])
    def test_buscar_substituto(self, agent, message):
        """Testa detecção de BUSCAR_SUBSTITUTO."""
        result = agent._detect_intent(message)
        assert result == SubstituicaoIntent.BUSCAR_SUBSTITUTO, f"Falhou para: '{message}'"

    # ==========================================================================
    # URGENTE - Substituição urgente
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "substituto urgente",
        "substituto emergencia",
        "substituto agora",
        "substituto imediato",
        "urgente preciso substituto",
        "emergencia substituto",
        "cobrir urgente",
        "cobrir agora",
        "substituir imediato",
        "faltou e preciso",
        "nao veio e precisamos",
        "emergencia de cobertura",
        "urgente cobertura",
        "posto sem ninguem agora",
        "posto sem cobertura urgente",
    ])
    def test_urgente(self, agent, message):
        """Testa detecção de URGENTE."""
        result = agent._detect_intent(message)
        assert result == SubstituicaoIntent.URGENTE, f"Falhou para: '{message}'"

    # ==========================================================================
    # CONFIRMAR - Confirmar substituição
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "confirmar substituicao",
        "confirme a substituicao",
        "aprovar substituicao",
        "aprove a substituicao",
        "aceitar o substituto",
        "aceite o substituto",
        "ok para a substituicao",
        "sim para a substituicao",
        "aprovado para substituicao",
    ])
    def test_confirmar(self, agent, message):
        """Testa detecção de CONFIRMAR."""
        result = agent._detect_intent(message)
        assert result == SubstituicaoIntent.CONFIRMAR, f"Falhou para: '{message}'"

    # ==========================================================================
    # CANCELAR - Cancelar substituição
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "cancelar substituicao",
        "cancele a substituicao",
        "recusar substituicao",
        "recuse a substituicao",
        "nao quero mais o substituto",
        "não preciso mais do substituto",
        "desistir da substituicao",
        "desista da substituicao",
    ])
    def test_cancelar(self, agent, message):
        """Testa detecção de CANCELAR."""
        result = agent._detect_intent(message)
        assert result == SubstituicaoIntent.CANCELAR, f"Falhou para: '{message}'"

    # ==========================================================================
    # PENDENTES - Substituições pendentes
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "substituicoes pendentes",
        "substituicao pendente",
        "trocas pendentes",
        "troca pendente",
        "coberturas pendentes",
        "cobertura pendente",
        "aguardando aprovacao",
        "aguardando confirmacao",
        "esperando aprovacao",
        "listar substituicoes pendentes",
        "ver pendentes",
        "mostrar pendentes",
    ])
    def test_pendentes(self, agent, message):
        """Testa detecção de PENDENTES."""
        result = agent._detect_intent(message)
        assert result == SubstituicaoIntent.PENDENTES, f"Falhou para: '{message}'"

    # ==========================================================================
    # HISTORICO - Histórico de substituições
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "historico de substituicoes",
        "historico de substituicao",
        "substituicoes anteriores",
        "substituicoes passadas",
        "substituicoes recentes",
        "ultimas substituicoes",
        "ultima substituicao",
        "ver historico",
        "mostrar historico",
    ])
    def test_historico(self, agent, message):
        """Testa detecção de HISTORICO."""
        result = agent._detect_intent(message)
        assert result == SubstituicaoIntent.HISTORICO, f"Falhou para: '{message}'"

    # ==========================================================================
    # CUSTO - Custo da substituição
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "custo da substituicao",
        "custo substituicao",
        "quanto custa a substituicao",
        "quanto custou a substituicao",
        "valor da substituicao",
        "preco da substituicao",
        "calcular custo da substituicao",
        "calcule o custo da cobertura",
    ])
    def test_custo(self, agent, message):
        """Testa detecção de CUSTO."""
        result = agent._detect_intent(message)
        assert result == SubstituicaoIntent.CUSTO, f"Falhou para: '{message}'"

    # ==========================================================================
    # DISPONIBILIDADE - Verificar disponibilidade
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "verificar disponibilidade",
        "ver disponibilidade",
        "checar disponibilidade",
        "quem esta disponivel para cobrir",
        "quem ta disponivel para substituir",
        "funcionarios disponiveis",
        "funcionarios livres",
        "colaboradores disponiveis",
        "quem esta livre",
        "quem ta livre",
    ])
    def test_disponibilidade(self, agent, message):
        """Testa detecção de DISPONIBILIDADE."""
        result = agent._detect_intent(message)
        assert result == SubstituicaoIntent.DISPONIBILIDADE, f"Falhou para: '{message}'"

    # ==========================================================================
    # Testes de frases completas do usuário
    # ==========================================================================
    @pytest.mark.parametrize("message,expected_intent", [
        ("preciso de um substituto para o turno da manha", SubstituicaoIntent.BUSCAR_SUBSTITUTO),
        ("urgente! funcionario faltou e preciso cobrir o posto", SubstituicaoIntent.URGENTE),
        ("quais substituicoes estao pendentes de aprovacao", SubstituicaoIntent.PENDENTES),
        ("qual foi o custo das substituicoes do mes passado", SubstituicaoIntent.CUSTO),
        ("mostre o historico de substituicoes do setor A", SubstituicaoIntent.HISTORICO),
        ("confirme a substituicao do Joao pelo Pedro", SubstituicaoIntent.CONFIRMAR),
        ("quem esta disponivel para cobrir amanha", SubstituicaoIntent.DISPONIBILIDADE),
    ])
    def test_frases_completas(self, agent, message, expected_intent):
        """Testa frases completas que o usuário pode digitar."""
        result = agent._detect_intent(message)
        assert result == expected_intent, f"Falhou para: '{message}' - esperado {expected_intent}, obtido {result}"

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


class TestSubstituicaoAgentProcess:
    """Testes para o método process do SubstituicaoAgent."""

    @pytest.fixture
    def agent(self):
        return SubstituicaoAgent()

    @pytest.mark.asyncio
    async def test_process_buscar_substituto(self, agent):
        """Testa processamento de busca de substituto."""
        result = await agent.process("buscar substituto")
        assert result is not None
        assert "intent" in result
        assert result["intent"] == SubstituicaoIntent.BUSCAR_SUBSTITUTO.value

    @pytest.mark.asyncio
    async def test_process_urgente(self, agent):
        """Testa processamento de substituição urgente."""
        result = await agent.process("substituto urgente")
        assert result is not None
        assert "intent" in result
        assert result["intent"] == SubstituicaoIntent.URGENTE.value

    @pytest.mark.asyncio
    async def test_process_default_returns_none(self, agent):
        """Testa que mensagens genéricas retornam None."""
        result = await agent.process("bom dia")
        assert result is None, "Deveria retornar None para mensagem genérica"
