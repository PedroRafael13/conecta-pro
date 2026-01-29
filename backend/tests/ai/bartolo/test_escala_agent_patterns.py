"""
Testes automatizados para patterns do EscalaAgent.
Fase 2 do Plano de Refinamento do Bartolo.
"""

import pytest
import sys
sys.path.insert(0, '/app')

from modules.ai.bartolo.agents.escala_agent import EscalaAgent, EscalaIntent


class TestEscalaAgentPatterns:
    """Testes para detecção de patterns no EscalaAgent."""

    @pytest.fixture
    def agent(self):
        """Fixture para EscalaAgent."""
        return EscalaAgent()

    # ==========================================================================
    # ESCALA_SEMANA - Consulta escala da semana
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "escala da semana",
        "escala desta semana",
        "ver escala da semana",
        "mostrar escala da semana",
        "proximos 7 dias",
        "proximo 7 dias",
        "proximos sete dias",
        "verificar as escalas atuais",
        "verificar escalas",
        "ver as escalas",
        "mostrar escalas",
        "listar escalas",
        "escalas atuais",
        "escalas existentes",
        "escalas ativas",
        "quais as escalas",
        "quais escalas",
    ])
    def test_escala_semana(self, agent, message):
        """Testa detecção de ESCALA_SEMANA."""
        result = agent._detect_intent(message)
        assert result == EscalaIntent.ESCALA_SEMANA, f"Falhou para: '{message}'"

    # ==========================================================================
    # ESCALA_MES - Consulta escala do mês
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "escala do mes",
        "escala deste mes",
        "ver escala do mes",
        "mostrar escala do mes",
        "escala de janeiro",
        "escala de fevereiro",
        "escala de marco",
        "escala de abril",
        "escala de maio",
        "escala de junho",
        "escala de julho",
        "escala de agosto",
        "escala de setembro",
        "escala de outubro",
        "escala de novembro",
        "escala de dezembro",
        "escalas de fevereiro",
        "proximos 30 dias",
        "proximos trinta dias",
    ])
    def test_escala_mes(self, agent, message):
        """Testa detecção de ESCALA_MES."""
        result = agent._detect_intent(message)
        assert result == EscalaIntent.ESCALA_MES, f"Falhou para: '{message}'"

    # ==========================================================================
    # CALCULAR_CUSTO - Custo da escala
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "custo da escala",
        "valor da escala",
        "preco da escala",
        "quanto custa a escala",
        "quanto vai custar a escala",
        "calcular custo",
        "calcule o custo",
        "estimar custo",
        "estime o custo",
        "simular custo",
        "simule valor",
        "previsao de custo",
        "estimativa de custo",
    ])
    def test_calcular_custo(self, agent, message):
        """Testa detecção de CALCULAR_CUSTO."""
        result = agent._detect_intent(message)
        assert result == EscalaIntent.CALCULAR_CUSTO, f"Falhou para: '{message}'"

    # ==========================================================================
    # OTIMIZAR_ESCALA - Otimização de escala
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "otimizar escala",
        "otimize a escala",
        "melhorar escala",
        "melhore a escala",
        "ajustar escala",
        "ajuste a escala",
        "refinar escala",
        "refine a escala",
        "reduzir custo da escala",
        "reduzir hora extra da escala",
        "diminuir custo da escala",
        "escala mais eficiente",
        "escala mais barata",
        "escala otimizada",
        "deixar a escala mais eficiente",
        "tornar a escala mais barata",
    ])
    def test_otimizar_escala(self, agent, message):
        """Testa detecção de OTIMIZAR_ESCALA."""
        result = agent._detect_intent(message)
        assert result == EscalaIntent.OTIMIZAR_ESCALA, f"Falhou para: '{message}'"

    # ==========================================================================
    # VALIDAR_ESCALA - Validação de escala
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "validar escala",
        "valide a escala",
        "verificar escala",
        "verifique a escala",
        "checar escala",
        "cheque a escala",
        "conferir escala",
        "confira a escala",
        "escala esta correta",
        "escala esta certa",
        "escala esta ok",
        "escala esta valida",
        "tem algum problema na escala",
        "tem algum erro na escala",
        "ha conflito na escala",
        "analisar a escala",
        "analise a escala",
        "escala esta dentro da CLT",
        "escala esta dentro da lei",
    ])
    def test_validar_escala(self, agent, message):
        """Testa detecção de VALIDAR_ESCALA."""
        result = agent._detect_intent(message)
        assert result == EscalaIntent.VALIDAR_ESCALA, f"Falhou para: '{message}'"

    # ==========================================================================
    # PUBLICAR_ESCALA - Publicação de escala
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "publicar escala",
        "publique a escala",
        "aprovar escala",
        "aprove a escala",
        "liberar escala",
        "libere a escala",
        "ativar escala",
        "ative a escala",
        "colocar escala em vigor",
        "por escala em producao",
        "disponibilizar a escala",
        "divulgar a escala",
    ])
    def test_publicar_escala(self, agent, message):
        """Testa detecção de PUBLICAR_ESCALA."""
        result = agent._detect_intent(message)
        assert result == EscalaIntent.PUBLICAR_ESCALA, f"Falhou para: '{message}'"

    # ==========================================================================
    # LISTAR_CONFLITOS - Conflitos na escala
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "conflitos na escala",
        "conflitos da escala",
        "conflito de escala",
        "escala com conflitos",
        "escala com conflito",
        "problemas na escala",
        "problema na escala",
        "erros na escala",
        "erro na escala",
        "sobreposicao de horario",
        "sobreposicao de turno",
        "choque de horario",
        "choque de turno",
        "funcionario em dois postos",
        "funcionario em 2 postos",
        "colaborador em dois lugares",
    ])
    def test_listar_conflitos(self, agent, message):
        """Testa detecção de LISTAR_CONFLITOS."""
        result = agent._detect_intent(message)
        assert result == EscalaIntent.LISTAR_CONFLITOS, f"Falhou para: '{message}'"

    # ==========================================================================
    # GERAR_ESCALA - Geração de escala (mais genérico, por último)
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        # Imperativo
        "gerar escala",
        "gere a escala",
        "gere uma escala",
        "criar escala",
        "crie escala",
        "crie a escala",
        "crie uma escala",
        "cria escala",
        "montar escala",
        "monte a escala",
        "fazer escala",
        "faca a escala",
        "faz escala",
        "elaborar escala",
        "elabore a escala",
        # Com contexto
        "nova escala",
        "escala para porteiros",
        "escala para vigilantes",
        "preciso de uma escala",
        "quero uma escala",
        "montar grade",
        "criar programacao",
        # Solicitações indiretas
        "pode gerar uma escala",
        "consegue criar uma escala",
        "da para montar uma escala",
        "preciso de uma nova escala",
        "precisamos de escala",
        "queremos uma escala",
        "me ajuda a criar a escala",
        "ajude a montar escala",
    ])
    def test_gerar_escala(self, agent, message):
        """Testa detecção de GERAR_ESCALA."""
        result = agent._detect_intent(message)
        assert result == EscalaIntent.GERAR_ESCALA, f"Falhou para: '{message}'"

    # ==========================================================================
    # Testes de frases completas do usuário
    # ==========================================================================
    @pytest.mark.parametrize("message,expected_intent", [
        # Frases reais que falharam antes
        ("Crie a escala para agentes de portaria pro mes de fevereiro de 2026 considerando os turnos de 12x36 e 5x2", EscalaIntent.GERAR_ESCALA),
        ("verifique as escalas atuais", EscalaIntent.ESCALA_SEMANA),
        ("gere escala para o proximo mes", EscalaIntent.GERAR_ESCALA),
        ("preciso montar a escala de março", EscalaIntent.ESCALA_MES),
        ("qual o custo estimado da escala", EscalaIntent.CALCULAR_CUSTO),
        ("tem conflito na escala de janeiro", EscalaIntent.LISTAR_CONFLITOS),
        ("pode publicar a escala do setor A", EscalaIntent.PUBLICAR_ESCALA),
        ("otimize a escala para reduzir horas extras", EscalaIntent.OTIMIZAR_ESCALA),
        ("me mostra a escala dessa semana", EscalaIntent.ESCALA_SEMANA),
        ("quero ver as escalas ativas", EscalaIntent.ESCALA_SEMANA),
    ])
    def test_frases_completas(self, agent, message, expected_intent):
        """Testa frases completas que o usuário pode digitar."""
        result = agent._detect_intent(message)
        assert result == expected_intent, f"Falhou para: '{message}' - esperado {expected_intent}, obtido {result}"

    # ==========================================================================
    # Testes de ordenação de patterns (específico vs genérico)
    # ==========================================================================
    def test_escala_semana_antes_de_gerar(self, agent):
        """Garante que 'escala da semana' não detecta GERAR_ESCALA."""
        result = agent._detect_intent("escala da semana")
        assert result == EscalaIntent.ESCALA_SEMANA, "Detectou GERAR_ESCALA em vez de ESCALA_SEMANA"

    def test_escala_mes_antes_de_gerar(self, agent):
        """Garante que 'escala do mes' não detecta GERAR_ESCALA."""
        result = agent._detect_intent("escala do mes")
        assert result == EscalaIntent.ESCALA_MES, "Detectou GERAR_ESCALA em vez de ESCALA_MES"

    def test_escalas_atuais_nao_e_gerar(self, agent):
        """Garante que 'escalas atuais' não detecta GERAR_ESCALA."""
        result = agent._detect_intent("escalas atuais")
        assert result == EscalaIntent.ESCALA_SEMANA, "Detectou incorretamente"

    # ==========================================================================
    # Testes negativos - não devem detectar intent
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "ola",
        "bom dia",
        "ajuda",
        "o que voce pode fazer",
        "como funciona",
        "obrigado",
    ])
    def test_nao_deve_detectar_intent(self, agent, message):
        """Testa que mensagens genéricas não detectam intent de escala."""
        result = agent._detect_intent(message)
        assert result is None, f"Detectou incorretamente para: '{message}'"


class TestEscalaAgentProcess:
    """Testes para o método process do EscalaAgent."""

    @pytest.fixture
    def agent(self):
        return EscalaAgent()

    @pytest.mark.asyncio
    async def test_process_gerar_escala(self, agent):
        """Testa processamento de geração de escala."""
        result = await agent.process("gere uma escala")
        assert result is not None
        assert "intent" in result
        assert result["intent"] == EscalaIntent.GERAR_ESCALA.value

    @pytest.mark.asyncio
    async def test_process_escala_semana(self, agent):
        """Testa processamento de escala da semana."""
        result = await agent.process("escala da semana")
        assert result is not None
        assert "intent" in result
        assert result["intent"] == EscalaIntent.ESCALA_SEMANA.value

    @pytest.mark.asyncio
    async def test_process_default_returns_none(self, agent):
        """Testa que mensagens genéricas retornam None."""
        result = await agent.process("bom dia")
        assert result is None, "Deveria retornar None para mensagem genérica"
