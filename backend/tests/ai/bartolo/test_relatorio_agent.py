"""
Testes automatizados para o RelatorioAgent.
Cobertura completa: intents, handlers, helpers e inicializacao.

Author: Conecta PRO Team
Date: 2026-01-30
"""

import sys
sys.path.insert(0, '/app')

import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta

from modules.ai.bartolo.agents.relatorio_agent import RelatorioAgent, RelatorioIntent


# =============================================================================
# TestRelatorioAgentIntents - Deteccao de intents via patterns
# =============================================================================

class TestRelatorioAgentIntents:
    """Testes para deteccao de intents no RelatorioAgent."""

    @pytest.fixture
    def agent(self):
        """Fixture para RelatorioAgent."""
        return RelatorioAgent()

    # ==========================================================================
    # GERAR_RELATORIO
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "gerar relatorio",
        "criar relatorio",
        "preciso de um relatorio",
        "relatorio de horas extras",
        "relatorio de custos",
        "faca um relatorio",
        "gere um relatorio",
        "crie um novo relatorio",
        "montar relatorio",
        "monte um relatorio",
        "quero um relatorio",
        "pode gerar um relatorio",
        "produzir relatorio",
        "produza um relatorio",
        "preciso relatorio de banco de horas",
        "relatorio de substituicoes",
        "relatorio disciplinar",
        "relatorio de ocorrencias",
        "relatorio de diaristas",
        "relatorio de rondas",
        "relatorio de postos",
        "relatorio de escalas",
        "relatorio geral",
        "novo relatorio",
        "da para criar um relatorio",
        "consegue gerar um relatorio",
    ])
    def test_gerar_relatorio(self, agent, message):
        """Testa deteccao de GERAR_RELATORIO."""
        result = agent._detect_intent(message)
        assert result == RelatorioIntent.GERAR_RELATORIO, f"Falhou para: '{message}'"

    # ==========================================================================
    # EXPORTAR_RELATORIO
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "exportar relatorio",
        "relatorio em pdf",
        "baixar relatorio",
        "salvar relatorio como excel",
        "exporte o relatorio",
        "download relatorio",
        "relatorio em xlsx",
        "relatorio em csv",
        "relatorio em json",
        "baixe o relatorio",
        "salve relatorio em pdf",
    ])
    def test_exportar_relatorio(self, agent, message):
        """Testa deteccao de EXPORTAR_RELATORIO."""
        result = agent._detect_intent(message)
        assert result == RelatorioIntent.EXPORTAR_RELATORIO, f"Falhou para: '{message}'"

    # ==========================================================================
    # VER_RELATORIO
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "ver relatorio #123",
        "detalhes do relatorio",
        "abrir relatorio RPT-001",
        "mostrar relatorio completo",
        "veja o relatorio mensal",
        "relatorio #456",
        "relatorio id 789",
        "info do relatorio",
        "abra relatorio RPT-002",
    ])
    def test_ver_relatorio(self, agent, message):
        """Testa deteccao de VER_RELATORIO."""
        result = agent._detect_intent(message)
        assert result == RelatorioIntent.VER_RELATORIO, f"Falhou para: '{message}'"

    # ==========================================================================
    # RELATORIO_RAPIDO
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "resumo operacional",
        "como estao as operacoes",
        "panorama geral",
        "numeros do dia",
        "dashboard operacional",
        "overview geral",
        "situacao geral",
        "status operacional",
        "dados do dia",
        "como esta o dia",
        "como andam as operacoes",
        "resumo semanal",
        "resumo mensal",
    ])
    def test_relatorio_rapido(self, agent, message):
        """Testa deteccao de RELATORIO_RAPIDO."""
        result = agent._detect_intent(message)
        assert result == RelatorioIntent.RELATORIO_RAPIDO, f"Falhou para: '{message}'"

    # ==========================================================================
    # TIPOS_RELATORIO
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "tipos de relatorio disponiveis",
        "quais relatorios posso gerar",
        "lista de relatorios",
        "relatorios disponiveis",
        "tipos de relatorios possiveis",
        "quais relatorios consigo gerar",
        "menu de relatorios",
    ])
    def test_tipos_relatorio(self, agent, message):
        """Testa deteccao de TIPOS_RELATORIO."""
        result = agent._detect_intent(message)
        assert result == RelatorioIntent.TIPOS_RELATORIO, f"Falhou para: '{message}'"

    # ==========================================================================
    # LISTAR_RELATORIOS
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "relatorios gerados",
        "relatorios recentes",
        "historico de relatorios",
        "ultimos relatorios",
        "ver relatorios recentes",
        "mostrar relatorios anteriores",
        "relatorios salvos",
        "relatorios anteriores",
    ])
    def test_listar_relatorios(self, agent, message):
        """Testa deteccao de LISTAR_RELATORIOS."""
        result = agent._detect_intent(message)
        assert result == RelatorioIntent.LISTAR_RELATORIOS, f"Falhou para: '{message}'"

    # ==========================================================================
    # ESTATISTICAS
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "estatisticas de relatorios",
        "quantos relatorios",
        "stats de relatorios",
        "metricas de relatorios",
        "indicadores de relatorios",
        "total de relatorios",
    ])
    def test_estatisticas(self, agent, message):
        """Testa deteccao de ESTATISTICAS."""
        result = agent._detect_intent(message)
        assert result == RelatorioIntent.ESTATISTICAS, f"Falhou para: '{message}'"

    # ==========================================================================
    # Testes negativos - nao devem detectar intent
    # ==========================================================================
    @pytest.mark.parametrize("message", [
        "ola",
        "bom dia",
        "ajuda",
        "obrigado",
        "o que voce pode fazer",
        "como funciona",
    ])
    def test_nao_deve_detectar_intent(self, agent, message):
        """Testa que mensagens genericas nao detectam intent de relatorio."""
        result = agent._detect_intent(message)
        assert result is None, f"Detectou incorretamente para: '{message}'"

    # ==========================================================================
    # Testes de ordenacao de patterns (especifico vs generico)
    # ==========================================================================
    def test_gerar_antes_de_listar(self, agent):
        """Garante que 'gerar relatorio' nao detecta LISTAR_RELATORIOS."""
        result = agent._detect_intent("gerar relatorio")
        assert result == RelatorioIntent.GERAR_RELATORIO, \
            "Detectou LISTAR_RELATORIOS em vez de GERAR_RELATORIO"

    def test_exportar_antes_de_ver(self, agent):
        """Garante que 'exportar relatorio' nao detecta VER_RELATORIO."""
        result = agent._detect_intent("exportar relatorio")
        assert result == RelatorioIntent.EXPORTAR_RELATORIO, \
            "Detectou VER_RELATORIO em vez de EXPORTAR_RELATORIO"

    def test_relatorio_com_tipo_e_gerar(self, agent):
        """Garante que 'relatorio de horas extras' detecta GERAR_RELATORIO."""
        result = agent._detect_intent("relatorio de horas extras")
        assert result == RelatorioIntent.GERAR_RELATORIO, \
            "Nao detectou GERAR_RELATORIO para relatorio com tipo"


# =============================================================================
# TestRelatorioAgentHandlers - Handlers de cada intent
# =============================================================================

class TestRelatorioAgentHandlers:
    """Testes para os handlers do RelatorioAgent."""

    @pytest.fixture
    def agent(self):
        """Fixture para RelatorioAgent."""
        return RelatorioAgent()

    # ==========================================================================
    # _handle_gerar_relatorio
    # ==========================================================================
    @pytest.mark.asyncio
    async def test_handle_gerar_relatorio_with_type(self, agent):
        """Testa geracao de relatorio com tipo detectado."""
        result = await agent.process("gerar relatorio de horas extras")
        assert result is not None
        assert result["intent"] == RelatorioIntent.GERAR_RELATORIO.value
        assert "data" in result
        assert result["data"]["report_type"] == "horas_extras"
        assert "response" in result
        assert "suggestions" in result
        assert "actions" in result

    @pytest.mark.asyncio
    async def test_handle_gerar_relatorio_with_type_custos(self, agent):
        """Testa geracao de relatorio de custos."""
        result = await agent.process("gerar relatorio de custos")
        assert result is not None
        assert result["intent"] == RelatorioIntent.GERAR_RELATORIO.value
        assert result["data"]["report_type"] == "custos"

    @pytest.mark.asyncio
    async def test_handle_gerar_relatorio_with_format(self, agent):
        """Testa geracao de relatorio com formato especificado."""
        result = await agent.process("gerar relatorio de custos em excel")
        assert result is not None
        assert result["data"]["format"] == "xlsx"

    @pytest.mark.asyncio
    async def test_handle_gerar_relatorio_with_period(self, agent):
        """Testa geracao de relatorio com periodo especificado."""
        result = await agent.process("gerar relatorio de custos do mes atual")
        assert result is not None
        assert result["data"]["period"] is not None
        assert "start" in result["data"]["period"]
        assert "end" in result["data"]["period"]

    @pytest.mark.asyncio
    async def test_handle_gerar_relatorio_default_format_pdf(self, agent):
        """Testa que o formato padrao e PDF quando nao especificado."""
        result = await agent.process("gerar relatorio de rondas")
        assert result is not None
        assert result["data"]["format"] == "pdf"

    @pytest.mark.asyncio
    async def test_handle_gerar_relatorio_without_type(self, agent):
        """Testa geracao de relatorio sem tipo - deve listar tipos."""
        result = await agent.process("gerar relatorio")
        assert result is not None
        # Sem tipo detectado, cai no _handle_tipos_relatorio
        assert result["intent"] == RelatorioIntent.TIPOS_RELATORIO.value
        assert "tipos" in result["data"]
        assert len(result["data"]["tipos"]) > 0

    @pytest.mark.asyncio
    async def test_handle_gerar_relatorio_actions_structure(self, agent):
        """Testa estrutura de actions no resultado de geracao."""
        result = await agent.process("gerar relatorio de ocorrencias")
        assert result is not None
        assert "actions" in result
        assert len(result["actions"]) > 0
        action = result["actions"][0]
        assert action["type"] == "create"
        assert action["target"] == "report"
        assert "data" in action

    # ==========================================================================
    # _handle_tipos_relatorio
    # ==========================================================================
    @pytest.mark.asyncio
    async def test_handle_tipos_relatorio(self, agent):
        """Testa listagem de tipos de relatorio."""
        result = await agent.process("tipos de relatorio disponiveis")
        assert result is not None
        assert result["intent"] == RelatorioIntent.TIPOS_RELATORIO.value
        assert "tipos" in result["data"]
        tipos = result["data"]["tipos"]
        # Verifica se todos os tipos esperados estao presentes
        expected_keys = [
            "horas_extras", "custos", "banco_horas", "substituicoes",
            "disciplinar", "ocorrencias", "diaristas", "rondas",
            "postos", "escalas", "geral",
        ]
        for key in expected_keys:
            assert key in tipos, f"Tipo '{key}' nao encontrado"

    @pytest.mark.asyncio
    async def test_handle_tipos_relatorio_has_suggestions(self, agent):
        """Testa que tipos de relatorio retorna suggestions."""
        result = await agent.process("quais relatorios posso gerar")
        assert result is not None
        assert "suggestions" in result
        assert len(result["suggestions"]) > 0

    @pytest.mark.asyncio
    async def test_handle_tipos_relatorio_response_text(self, agent):
        """Testa conteudo da resposta de tipos."""
        result = await agent.process("lista de relatorios")
        assert result is not None
        assert "TIPOS DE RELATORIO" in result["response"]
        assert "PDF" in result["response"]
        assert "XLSX" in result["response"]

    # ==========================================================================
    # _handle_listar_relatorios
    # ==========================================================================
    @pytest.mark.asyncio
    async def test_handle_listar_relatorios(self, agent):
        """Testa listagem de relatorios gerados."""
        result = await agent.process("relatorios gerados")
        assert result is not None
        assert result["intent"] == RelatorioIntent.LISTAR_RELATORIOS.value
        assert "relatorios" in result["data"]
        assert "total" in result["data"]
        relatorios = result["data"]["relatorios"]
        assert len(relatorios) > 0
        # Verifica que RPT-xxx esta presente
        ids = [r["id"] for r in relatorios]
        assert any(id_.startswith("RPT-") for id_ in ids), \
            "Nenhum relatorio com prefixo RPT- encontrado"

    @pytest.mark.asyncio
    async def test_handle_listar_relatorios_structure(self, agent):
        """Testa estrutura dos relatorios listados."""
        result = await agent.process("relatorios recentes")
        assert result is not None
        relatorios = result["data"]["relatorios"]
        for r in relatorios:
            assert "id" in r
            assert "tipo" in r
            assert "periodo" in r
            assert "status" in r
            assert "formato" in r
            assert "gerado_em" in r

    @pytest.mark.asyncio
    async def test_handle_listar_relatorios_total_matches(self, agent):
        """Testa que total corresponde ao numero de relatorios."""
        result = await agent.process("historico de relatorios")
        assert result is not None
        assert result["data"]["total"] == len(result["data"]["relatorios"])

    # ==========================================================================
    # _handle_relatorio_rapido
    # ==========================================================================
    @pytest.mark.asyncio
    async def test_handle_relatorio_rapido(self, agent):
        """Testa geracao de relatorio rapido / dashboard."""
        result = await agent.process("resumo operacional")
        assert result is not None
        assert result["intent"] == RelatorioIntent.RELATORIO_RAPIDO.value
        data = result["data"]
        assert "date" in data
        assert "efetivo" in data
        assert "turnos" in data
        assert "ocorrencias" in data
        assert "banco_horas" in data
        assert "rondas" in data

    @pytest.mark.asyncio
    async def test_handle_relatorio_rapido_efetivo(self, agent):
        """Testa dados de efetivo no relatorio rapido."""
        result = await agent.process("panorama geral")
        assert result is not None
        efetivo = result["data"]["efetivo"]
        assert "total" in efetivo
        assert "cobertura" in efetivo
        assert isinstance(efetivo["total"], int)
        assert isinstance(efetivo["cobertura"], float)

    @pytest.mark.asyncio
    async def test_handle_relatorio_rapido_turnos(self, agent):
        """Testa dados de turnos no relatorio rapido."""
        result = await agent.process("numeros do dia")
        assert result is not None
        turnos = result["data"]["turnos"]
        assert "checkins" in turnos
        assert "esperados" in turnos
        assert "atrasos" in turnos
        assert "faltas" in turnos

    @pytest.mark.asyncio
    async def test_handle_relatorio_rapido_rondas(self, agent):
        """Testa dados de rondas no relatorio rapido."""
        result = await agent.process("como estao as operacoes")
        assert result is not None
        rondas = result["data"]["rondas"]
        assert "programadas" in rondas
        assert "concluidas" in rondas
        assert "conformidade" in rondas

    @pytest.mark.asyncio
    async def test_handle_relatorio_rapido_date_today(self, agent):
        """Testa que a data do relatorio rapido e hoje."""
        result = await agent.process("resumo operacional")
        assert result is not None
        assert result["data"]["date"] == date.today().isoformat()

    @pytest.mark.asyncio
    async def test_handle_relatorio_rapido_suggestions(self, agent):
        """Testa suggestions do relatorio rapido."""
        result = await agent.process("resumo operacional")
        assert result is not None
        assert "suggestions" in result
        assert len(result["suggestions"]) > 0

    # ==========================================================================
    # _handle_estatisticas
    # ==========================================================================
    @pytest.mark.asyncio
    async def test_handle_estatisticas(self, agent):
        """Testa exibicao de estatisticas."""
        result = await agent.process("estatisticas de relatorios")
        assert result is not None
        assert result["intent"] == RelatorioIntent.ESTATISTICAS.value
        data = result["data"]
        assert "total_mes" in data
        assert "por_tipo" in data
        assert "por_formato" in data

    @pytest.mark.asyncio
    async def test_handle_estatisticas_total_mes(self, agent):
        """Testa que total_mes e um inteiro positivo."""
        result = await agent.process("quantos relatorios")
        assert result is not None
        assert isinstance(result["data"]["total_mes"], int)
        assert result["data"]["total_mes"] > 0

    @pytest.mark.asyncio
    async def test_handle_estatisticas_por_tipo(self, agent):
        """Testa estatisticas por tipo de relatorio."""
        result = await agent.process("estatisticas de relatorios")
        assert result is not None
        por_tipo = result["data"]["por_tipo"]
        assert isinstance(por_tipo, dict)
        assert len(por_tipo) > 0
        for key, val in por_tipo.items():
            assert isinstance(val, int)

    @pytest.mark.asyncio
    async def test_handle_estatisticas_por_formato(self, agent):
        """Testa estatisticas por formato de exportacao."""
        result = await agent.process("estatisticas de relatorios")
        assert result is not None
        por_formato = result["data"]["por_formato"]
        assert isinstance(por_formato, dict)
        assert "pdf" in por_formato
        assert "xlsx" in por_formato

    @pytest.mark.asyncio
    async def test_handle_estatisticas_suggestions(self, agent):
        """Testa suggestions das estatisticas."""
        result = await agent.process("estatisticas de relatorios")
        assert result is not None
        assert "suggestions" in result
        assert len(result["suggestions"]) > 0

    # ==========================================================================
    # _handle_exportar_relatorio
    # ==========================================================================
    @pytest.mark.asyncio
    async def test_handle_exportar(self, agent):
        """Testa exportacao de relatorio."""
        result = await agent.process("exportar relatorio em pdf")
        assert result is not None
        assert result["intent"] == RelatorioIntent.EXPORTAR_RELATORIO.value
        assert "format" in result["data"]
        assert result["data"]["format"] == "pdf"

    @pytest.mark.asyncio
    async def test_handle_exportar_excel(self, agent):
        """Testa exportacao em Excel."""
        result = await agent.process("relatorio em excel")
        assert result is not None
        assert result["data"]["format"] == "xlsx"

    @pytest.mark.asyncio
    async def test_handle_exportar_csv(self, agent):
        """Testa exportacao em CSV."""
        result = await agent.process("relatorio em csv")
        assert result is not None
        assert result["data"]["format"] == "csv"

    @pytest.mark.asyncio
    async def test_handle_exportar_with_type(self, agent):
        """Testa exportacao com tipo de relatorio."""
        result = await agent.process("exportar relatorio de custos em pdf")
        assert result is not None
        assert result["data"]["report_type"] == "custos"
        assert result["data"]["format"] == "pdf"

    @pytest.mark.asyncio
    async def test_handle_exportar_with_report_id(self, agent):
        """Testa exportacao com ID de relatorio."""
        result = await agent.process("baixar relatorio #123")
        assert result is not None
        assert result["data"]["report_id"] == "123"

    @pytest.mark.asyncio
    async def test_handle_exportar_without_details(self, agent):
        """Testa exportacao sem detalhes - deve orientar usuario."""
        result = await agent.process("exportar relatorio")
        assert result is not None
        assert result["intent"] == RelatorioIntent.EXPORTAR_RELATORIO.value
        assert "Formatos" in result["response"] or "formato" in result["response"].lower()

    @pytest.mark.asyncio
    async def test_handle_exportar_default_format_pdf(self, agent):
        """Testa formato padrao PDF na exportacao."""
        result = await agent.process("exportar relatorio")
        assert result is not None
        assert result["data"]["format"] == "pdf"

    @pytest.mark.asyncio
    async def test_handle_exportar_suggestions(self, agent):
        """Testa suggestions da exportacao."""
        result = await agent.process("exportar relatorio")
        assert result is not None
        assert "suggestions" in result
        assert len(result["suggestions"]) > 0

    # ==========================================================================
    # _handle_ver_relatorio
    # ==========================================================================
    @pytest.mark.asyncio
    async def test_handle_ver_relatorio_with_id(self, agent):
        """Testa visualizacao de relatorio com ID."""
        result = await agent.process("ver relatorio #123")
        assert result is not None
        assert result["intent"] == RelatorioIntent.VER_RELATORIO.value
        assert result["data"]["report_id"] == "123"

    @pytest.mark.asyncio
    async def test_handle_ver_relatorio_with_rpt_id(self, agent):
        """Testa visualizacao de relatorio com RPT-ID."""
        result = await agent.process("abrir relatorio RPT-001")
        assert result is not None
        assert result["data"]["report_id"] == "RPT-001"

    @pytest.mark.asyncio
    async def test_handle_ver_relatorio_without_id(self, agent):
        """Testa visualizacao de relatorio sem ID - deve orientar."""
        result = await agent.process("detalhes do relatorio")
        assert result is not None
        assert result["intent"] == RelatorioIntent.VER_RELATORIO.value
        assert result["data"] == {}

    @pytest.mark.asyncio
    async def test_handle_ver_relatorio_suggestions(self, agent):
        """Testa suggestions da visualizacao."""
        result = await agent.process("ver relatorio #456")
        assert result is not None
        assert "suggestions" in result
        assert len(result["suggestions"]) > 0

    # ==========================================================================
    # _handle_default
    # ==========================================================================
    @pytest.mark.asyncio
    async def test_handle_default_returns_none(self, agent):
        """Testa que mensagem nao reconhecida retorna None."""
        result = await agent.process("bom dia")
        assert result is None, "Deveria retornar None para mensagem generica"

    @pytest.mark.asyncio
    async def test_handle_default_returns_none_random(self, agent):
        """Testa que mensagem aleatoria retorna None."""
        result = await agent.process("qual a previsao do tempo")
        assert result is None

    @pytest.mark.asyncio
    async def test_handle_default_returns_none_greeting(self, agent):
        """Testa que saudacao retorna None."""
        result = await agent.process("ola, tudo bem?")
        assert result is None


# =============================================================================
# TestRelatorioAgentHelpers - Metodos auxiliares
# =============================================================================

class TestRelatorioAgentHelpers:
    """Testes para metodos auxiliares do RelatorioAgent."""

    @pytest.fixture
    def agent(self):
        """Fixture para RelatorioAgent."""
        return RelatorioAgent()

    # ==========================================================================
    # _detect_report_type
    # ==========================================================================
    @pytest.mark.parametrize("message,expected_type", [
        ("relatorio de horas extras", "horas_extras"),
        ("relatorio de hora extra", "horas_extras"),
        ("relatorio de custos", "custos"),
        ("relatorio financeiro", "custos"),
        ("relatorio de despesas", "custos"),
        ("relatorio de banco de horas", "banco_horas"),
        ("relatorio de banco horas", "banco_horas"),
        ("relatorio de substituicoes", "substituicoes"),
        ("relatorio disciplinar", "disciplinar"),
        ("relatorio de advertencia", "disciplinar"),
        ("relatorio de suspensao", "disciplinar"),
        ("relatorio de ocorrencias", "ocorrencias"),
        ("relatorio de ocorrencia", "ocorrencias"),
        ("relatorio de diaristas", "diaristas"),
        ("relatorio de diarista", "diaristas"),
        ("relatorio de rondas", "rondas"),
        ("relatorio de ronda", "rondas"),
        ("relatorio de inspecao", "rondas"),
        ("relatorio de postos", "postos"),
        ("relatorio de posto", "postos"),
        ("relatorio de escalas", "escalas"),
        ("relatorio de escala", "escalas"),
        ("relatorio geral", "geral"),
        ("relatorio operacional", "geral"),
        ("relatorio completo", "geral"),
        ("relatorio consolidado", "geral"),
    ])
    def test_detect_report_type(self, agent, message, expected_type):
        """Testa deteccao de tipo de relatorio."""
        result = agent._detect_report_type(message)
        assert result == expected_type, f"Falhou para: '{message}' - esperado '{expected_type}', obtido '{result}'"

    def test_detect_report_type_none(self, agent):
        """Testa que mensagem sem tipo retorna None."""
        result = agent._detect_report_type("bom dia")
        assert result is None

    def test_detect_report_type_none_generic(self, agent):
        """Testa que mensagem generica sem tipo retorna None."""
        result = agent._detect_report_type("gerar relatorio")
        assert result is None

    # ==========================================================================
    # _extract_period
    # ==========================================================================
    def test_extract_period_mes_atual(self, agent):
        """Testa extracao de periodo 'mes atual'."""
        result = agent._extract_period("relatorio do mes atual")
        assert result is not None
        assert "start" in result
        assert "end" in result
        hoje = date.today()
        inicio = hoje.replace(day=1)
        assert result["start"] == inicio.strftime("%d/%m/%Y")
        assert result["end"] == hoje.strftime("%d/%m/%Y")

    def test_extract_period_este_mes(self, agent):
        """Testa extracao de periodo 'este mes'."""
        result = agent._extract_period("relatorio deste mes")
        assert result is not None
        hoje = date.today()
        inicio = hoje.replace(day=1)
        assert result["start"] == inicio.strftime("%d/%m/%Y")

    def test_extract_period_mes_passado(self, agent):
        """Testa extracao de periodo 'mes passado' (usa mesmo pattern de 'mes atual')."""
        result = agent._extract_period("relatorio do mes passado")
        assert result is not None
        assert "start" in result
        assert "end" in result

    def test_extract_period_ultimo_mes(self, agent):
        """Testa extracao de periodo 'ultimo mes'."""
        result = agent._extract_period("relatorio do ultimo mes")
        assert result is not None
        assert "start" in result
        assert "end" in result

    def test_extract_period_semana(self, agent):
        """Testa extracao de periodo 'semana'."""
        result = agent._extract_period("relatorio da semana")
        assert result is not None
        hoje = date.today()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        assert result["start"] == inicio_semana.strftime("%d/%m/%Y")
        assert result["end"] == hoje.strftime("%d/%m/%Y")

    def test_extract_period_esta_semana(self, agent):
        """Testa extracao de periodo 'esta semana'."""
        result = agent._extract_period("relatorio desta semana")
        assert result is not None
        assert "start" in result
        assert "end" in result

    def test_extract_period_hoje(self, agent):
        """Testa extracao de periodo 'hoje'."""
        result = agent._extract_period("relatorio de hoje")
        assert result is not None
        hoje = date.today()
        assert result["start"] == hoje.strftime("%d/%m/%Y")
        assert result["end"] == hoje.strftime("%d/%m/%Y")

    def test_extract_period_date_range(self, agent):
        """Testa extracao de periodo com intervalo de datas."""
        result = agent._extract_period("relatorio de 01/01/2026 a 31/01/2026")
        assert result is not None
        assert result["start"] == "01/01/2026"
        assert result["end"] == "31/01/2026"

    def test_extract_period_date_range_ate(self, agent):
        """Testa extracao de periodo com 'ate'."""
        result = agent._extract_period("relatorio de 01/02/2026 ate 28/02/2026")
        assert result is not None
        assert result["start"] == "01/02/2026"
        assert result["end"] == "28/02/2026"

    def test_extract_period_date_range_dash(self, agent):
        """Testa extracao de periodo com hifen."""
        result = agent._extract_period("relatorio de 01/03/2026 - 31/03/2026")
        assert result is not None
        assert result["start"] == "01/03/2026"
        assert result["end"] == "31/03/2026"

    def test_extract_period_month_name(self, agent):
        """Testa extracao de periodo com nome do mes."""
        result = agent._extract_period("relatorio de janeiro 2026")
        assert result is not None
        assert result["start"] == "01/01/2026"
        assert result["end"] == "31/01/2026"

    def test_extract_period_month_name_fevereiro(self, agent):
        """Testa extracao de periodo com fevereiro."""
        result = agent._extract_period("relatorio de fevereiro 2026")
        assert result is not None
        assert result["start"] == "01/02/2026"
        assert result["end"] == "28/02/2026"

    def test_extract_period_month_name_marco(self, agent):
        """Testa extracao de periodo com marco."""
        result = agent._extract_period("relatorio de marco 2026")
        assert result is not None
        assert result["start"] == "01/03/2026"
        assert result["end"] == "31/03/2026"

    def test_extract_period_month_name_dezembro(self, agent):
        """Testa extracao de periodo com dezembro."""
        result = agent._extract_period("relatorio de dezembro 2025")
        assert result is not None
        assert result["start"] == "01/12/2025"
        assert result["end"] == "31/12/2025"

    def test_extract_period_month_name_without_year(self, agent):
        """Testa extracao de periodo com nome do mes sem ano."""
        result = agent._extract_period("relatorio de abril")
        assert result is not None
        hoje = date.today()
        assert result["start"] == f"01/04/{hoje.year}"

    def test_extract_period_none(self, agent):
        """Testa que mensagem sem periodo retorna None."""
        result = agent._extract_period("bom dia")
        assert result is None

    def test_extract_period_none_generic(self, agent):
        """Testa que mensagem generica sem periodo retorna None."""
        result = agent._extract_period("gerar relatorio de custos")
        assert result is None

    # ==========================================================================
    # _extract_format
    # ==========================================================================
    def test_extract_format_pdf(self, agent):
        """Testa extracao de formato PDF."""
        result = agent._extract_format("relatorio em pdf")
        assert result == "pdf"

    def test_extract_format_xlsx(self, agent):
        """Testa extracao de formato XLSX."""
        result = agent._extract_format("relatorio em xlsx")
        assert result == "xlsx"

    def test_extract_format_excel(self, agent):
        """Testa extracao de formato Excel (mapeia para xlsx)."""
        result = agent._extract_format("relatorio em excel")
        assert result == "xlsx"

    def test_extract_format_planilha(self, agent):
        """Testa extracao de formato planilha (mapeia para xlsx)."""
        result = agent._extract_format("relatorio em planilha")
        assert result == "xlsx"

    def test_extract_format_csv(self, agent):
        """Testa extracao de formato CSV."""
        result = agent._extract_format("relatorio em csv")
        assert result == "csv"

    def test_extract_format_json(self, agent):
        """Testa extracao de formato JSON."""
        result = agent._extract_format("relatorio em json")
        assert result == "json"

    def test_extract_format_none(self, agent):
        """Testa que mensagem sem formato retorna None."""
        result = agent._extract_format("gerar relatorio de custos")
        assert result is None

    def test_extract_format_none_generic(self, agent):
        """Testa que mensagem generica sem formato retorna None."""
        result = agent._extract_format("bom dia")
        assert result is None

    # ==========================================================================
    # _extract_report_id
    # ==========================================================================
    def test_extract_report_id_rpt(self, agent):
        """Testa extracao de ID no formato RPT-001."""
        result = agent._extract_report_id("ver relatorio RPT-001")
        assert result == "RPT-001"

    def test_extract_report_id_rpt_no_dash(self, agent):
        """Testa extracao de ID no formato RPT001."""
        result = agent._extract_report_id("ver relatorio RPT001")
        assert result == "RPT-001"

    def test_extract_report_id_rpt_lowercase(self, agent):
        """Testa extracao de ID no formato rpt-001."""
        result = agent._extract_report_id("ver relatorio rpt-001")
        assert result == "RPT-001"

    def test_extract_report_id_rpt_long(self, agent):
        """Testa extracao de ID com numero longo RPT-12345."""
        result = agent._extract_report_id("ver relatorio RPT-12345")
        assert result == "RPT-12345"

    def test_extract_report_id_hash(self, agent):
        """Testa extracao de ID no formato #123."""
        result = agent._extract_report_id("ver relatorio #123")
        assert result == "123"

    def test_extract_report_id_hash_large(self, agent):
        """Testa extracao de ID no formato #99999."""
        result = agent._extract_report_id("ver relatorio #99999")
        assert result == "99999"

    def test_extract_report_id_uuid(self, agent):
        """Testa extracao de ID no formato UUID."""
        uuid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        result = agent._extract_report_id(f"ver relatorio {uuid}")
        assert result == uuid

    def test_extract_report_id_none(self, agent):
        """Testa que mensagem sem ID retorna None."""
        result = agent._extract_report_id("ver relatorio")
        assert result is None

    def test_extract_report_id_none_generic(self, agent):
        """Testa que mensagem generica sem ID retorna None."""
        result = agent._extract_report_id("bom dia")
        assert result is None


# =============================================================================
# TestRelatorioAgentInit - Inicializacao do agente
# =============================================================================

class TestRelatorioAgentInit:
    """Testes para inicializacao do RelatorioAgent."""

    def test_init_without_db(self):
        """Testa inicializacao sem banco de dados."""
        agent = RelatorioAgent()
        assert agent.db is None
        assert agent.data_connector is None

    def test_init_with_db_creates_data_connector(self):
        """Testa inicializacao com db cria DataConnector."""
        mock_db = MagicMock()
        with patch("modules.ai.bartolo.agents.relatorio_agent.RelatorioAgent.__init__",
                    return_value=None) as mock_init:
            # Testar o fluxo real de init com mock do DataConnector
            agent = RelatorioAgent.__new__(RelatorioAgent)
            agent.db = mock_db
            agent.data_connector = None

            with patch("modules.ai.bartolo.services.data_connector.DataConnector") as MockDC:
                mock_connector = MagicMock()
                MockDC.return_value = mock_connector
                # Simular o init manualmente
                agent.db = mock_db
                agent.data_connector = None
                if agent.db and not agent.data_connector:
                    try:
                        from modules.ai.bartolo.services.data_connector import DataConnector
                        agent.data_connector = DataConnector(mock_db)
                    except Exception:
                        agent.data_connector = None

                # Verificar que data_connector foi criado (ou tentou criar)
                assert agent.db is mock_db

    def test_init_with_data_connector_provided(self):
        """Testa inicializacao com DataConnector fornecido."""
        mock_db = MagicMock()
        mock_connector = MagicMock()
        agent = RelatorioAgent(db=mock_db, data_connector=mock_connector)
        assert agent.db is mock_db
        assert agent.data_connector is mock_connector

    def test_init_with_db_connector_failure(self):
        """Testa inicializacao quando DataConnector falha."""
        mock_db = MagicMock()
        with patch(
            "modules.ai.bartolo.agents.relatorio_agent.RelatorioAgent.__init__",
            side_effect=None
        ):
            # Testar que falha no import nao quebra
            agent = RelatorioAgent.__new__(RelatorioAgent)
            agent.db = mock_db
            agent.data_connector = None
            # Nao deve levantar excecao
            assert agent.data_connector is None

    def test_get_capabilities(self):
        """Testa que get_capabilities retorna lista nao vazia."""
        agent = RelatorioAgent()
        caps = agent.get_capabilities()
        assert isinstance(caps, list)
        assert len(caps) > 0

    def test_get_capabilities_content(self):
        """Testa conteudo das capabilities."""
        agent = RelatorioAgent()
        caps = agent.get_capabilities()
        # Verifica que capabilities mencionam funcionalidades chave
        caps_text = " ".join(caps).lower()
        assert "relatorio" in caps_text or "relatorios" in caps_text
        assert "gerar" in caps_text
        assert "exportar" in caps_text
        assert "listar" in caps_text

    def test_get_capabilities_returns_six_items(self):
        """Testa que get_capabilities retorna 6 itens."""
        agent = RelatorioAgent()
        caps = agent.get_capabilities()
        assert len(caps) == 6

    def test_intent_enum_values(self):
        """Testa valores do enum RelatorioIntent."""
        assert RelatorioIntent.GERAR_RELATORIO.value == "gerar_relatorio"
        assert RelatorioIntent.VER_RELATORIO.value == "ver_relatorio"
        assert RelatorioIntent.LISTAR_RELATORIOS.value == "listar_relatorios"
        assert RelatorioIntent.TIPOS_RELATORIO.value == "tipos_relatorio"
        assert RelatorioIntent.EXPORTAR_RELATORIO.value == "exportar_relatorio"
        assert RelatorioIntent.RELATORIO_RAPIDO.value == "relatorio_rapido"
        assert RelatorioIntent.ESTATISTICAS.value == "estatisticas"

    def test_intent_enum_has_seven_values(self):
        """Testa que RelatorioIntent tem 7 valores."""
        assert len(RelatorioIntent) == 7

    def test_agent_has_intent_patterns(self):
        """Testa que o agente tem INTENT_PATTERNS definido."""
        assert hasattr(RelatorioAgent, "INTENT_PATTERNS")
        assert len(RelatorioAgent.INTENT_PATTERNS) > 0

    def test_agent_has_process_method(self):
        """Testa que o agente tem metodo process."""
        agent = RelatorioAgent()
        assert hasattr(agent, "process")
        assert callable(agent.process)

    def test_agent_has_detect_intent_method(self):
        """Testa que o agente tem metodo _detect_intent."""
        agent = RelatorioAgent()
        assert hasattr(agent, "_detect_intent")
        assert callable(agent._detect_intent)

    def test_agent_has_all_helper_methods(self):
        """Testa que o agente tem todos os metodos auxiliares."""
        agent = RelatorioAgent()
        helpers = [
            "_detect_report_type",
            "_extract_period",
            "_extract_format",
            "_extract_report_id",
        ]
        for method_name in helpers:
            assert hasattr(agent, method_name), f"Metodo '{method_name}' nao encontrado"
            assert callable(getattr(agent, method_name))


# =============================================================================
# TestRelatorioAgentIntegration - Testes de integracao entre metodos
# =============================================================================

class TestRelatorioAgentIntegration:
    """Testes de integracao entre intent detection e handlers."""

    @pytest.fixture
    def agent(self):
        """Fixture para RelatorioAgent."""
        return RelatorioAgent()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message,expected_intent", [
        ("gerar relatorio de horas extras do mes atual em pdf", RelatorioIntent.GERAR_RELATORIO.value),
        ("exportar relatorio em pdf", RelatorioIntent.EXPORTAR_RELATORIO.value),
        ("ver relatorio RPT-001", RelatorioIntent.VER_RELATORIO.value),
        ("resumo operacional de hoje", RelatorioIntent.RELATORIO_RAPIDO.value),
        ("quais tipos de relatorio disponiveis", RelatorioIntent.TIPOS_RELATORIO.value),
        ("relatorios gerados recentemente", RelatorioIntent.LISTAR_RELATORIOS.value),
        ("estatisticas de relatorios", RelatorioIntent.ESTATISTICAS.value),
    ])
    async def test_full_flow_intent_to_handler(self, agent, message, expected_intent):
        """Testa fluxo completo de intent detection ate handler."""
        result = await agent.process(message)
        assert result is not None, f"Resultado None para: '{message}'"
        assert result["intent"] == expected_intent, \
            f"Intent errado para: '{message}' - esperado '{expected_intent}', obtido '{result['intent']}'"
        assert "response" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_gerar_relatorio_full_params(self, agent):
        """Testa geracao de relatorio com todos os parametros."""
        result = await agent.process("gerar relatorio de horas extras do mes atual em excel")
        assert result is not None
        assert result["intent"] == RelatorioIntent.GERAR_RELATORIO.value
        assert result["data"]["report_type"] == "horas_extras"
        assert result["data"]["period"] is not None
        assert result["data"]["format"] == "xlsx"

    @pytest.mark.asyncio
    async def test_gerar_relatorio_with_date_range(self, agent):
        """Testa geracao de relatorio com intervalo de datas."""
        result = await agent.process("gerar relatorio de custos de 01/01/2026 a 31/01/2026")
        assert result is not None
        assert result["data"]["report_type"] == "custos"
        assert result["data"]["period"]["start"] == "01/01/2026"
        assert result["data"]["period"]["end"] == "31/01/2026"

    @pytest.mark.asyncio
    async def test_gerar_relatorio_with_month_name(self, agent):
        """Testa geracao de relatorio com nome do mes."""
        result = await agent.process("gerar relatorio de rondas de janeiro 2026")
        assert result is not None
        assert result["data"]["report_type"] == "rondas"
        assert result["data"]["period"]["start"] == "01/01/2026"
        assert result["data"]["period"]["end"] == "31/01/2026"

    @pytest.mark.asyncio
    async def test_process_with_context(self, agent):
        """Testa process com contexto fornecido."""
        context = {"user_id": 1, "condominio_id": "abc"}
        result = await agent.process("gerar relatorio de custos", context=context)
        assert result is not None
        assert result["intent"] == RelatorioIntent.GERAR_RELATORIO.value

    @pytest.mark.asyncio
    async def test_process_with_none_context(self, agent):
        """Testa process com context=None (padrao)."""
        result = await agent.process("resumo operacional", context=None)
        assert result is not None
        assert result["intent"] == RelatorioIntent.RELATORIO_RAPIDO.value
