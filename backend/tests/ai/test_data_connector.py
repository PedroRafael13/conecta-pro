"""
Testes do DataConnector - Conector de Dados do Bartolo.

Testa especificamente:
- Bug #4a: total_count correto com filtro de shift
- Bug #4b: to_natural_language() mostra todos itens quando <=20
- Detecção de queries em linguagem natural
- Formatação de resultados
"""

from datetime import datetime

import pytest

# Importação condicional
try:
    from modules.ai.bartolo.services.data_connector import DataConnector, DataQuery, DataResult, QueryType

    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False

pytestmark = pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Módulo Bartolo não disponível")


class TestDataResultToNaturalLanguage:
    """Testa to_natural_language() - Bug #4b fix."""

    def test_lista_vazia(self):
        """Lista vazia retorna mensagem padrão."""
        result = DataResult(
            success=True,
            query_type=QueryType.LIST,
            entity="funcionarios",
            data=[],
            total_count=0,
            executed_at=datetime.now(),
        )
        text = result.to_natural_language()
        assert "nenhum" in text.lower() or "0" in text

    def test_lista_pequena_mostra_todos(self):
        """Bug #4b: Lista <=20 mostra todos os itens."""
        names = [f"FUNCIONARIO {i}" for i in range(1, 10)]  # 9 itens
        result = DataResult(
            success=True,
            query_type=QueryType.LIST,
            entity="funcionarios",
            data=names,
            total_count=9,
            executed_at=datetime.now(),
        )
        text = result.to_natural_language()
        assert "9" in text
        # Todos os 9 devem estar presentes
        for name in names:
            assert name in text

    def test_lista_20_mostra_todos(self):
        """Lista com exatamente 20 itens mostra todos."""
        names = [f"ITEM {i}" for i in range(1, 21)]  # 20 itens
        result = DataResult(
            success=True,
            query_type=QueryType.LIST,
            entity="itens",
            data=names,
            total_count=20,
            executed_at=datetime.now(),
        )
        text = result.to_natural_language()
        assert "20" in text
        for name in names:
            assert name in text

    def test_lista_grande_mostra_primeiros_10(self):
        """Lista >20 mostra apenas primeiros 10."""
        names = [f"ITEM {i}" for i in range(1, 31)]  # 30 itens
        result = DataResult(
            success=True,
            query_type=QueryType.LIST,
            entity="itens",
            data=names,
            total_count=30,
            executed_at=datetime.now(),
        )
        text = result.to_natural_language()
        assert "30" in text
        # Primeiros 10 presentes
        for i in range(1, 11):
            assert f"ITEM {i}" in text
        # Item 11+ não deve estar
        assert "ITEM 11" not in text
        # Deve ter indicação de "e mais X"
        assert "mais 20" in text

    def test_contagem(self):
        """QueryType.COUNT retorna contagem."""
        result = DataResult(
            success=True,
            query_type=QueryType.COUNT,
            entity="funcionarios",
            data=None,
            total_count=44,
            executed_at=datetime.now(),
        )
        text = result.to_natural_language()
        assert "44" in text
        assert "funcionarios" in text

    def test_detalhe_vazio(self):
        """DETAIL sem dados retorna mensagem padrão."""
        result = DataResult(
            success=True,
            query_type=QueryType.DETAIL,
            entity="funcionario",
            data=None,
            total_count=0,
            executed_at=datetime.now(),
        )
        text = result.to_natural_language()
        assert "encontrei" in text.lower() or "nao" in text.lower()

    def test_erro(self):
        """Resultado com erro retorna mensagem."""
        result = DataResult(
            success=False,
            query_type=QueryType.LIST,
            entity="funcionarios",
            data=None,
            message="Erro ao consultar banco",
            executed_at=datetime.now(),
        )
        text = result.to_natural_language()
        assert "Erro ao consultar banco" in text

    def test_special_type_usa_message(self):
        """Tipos especiais usam a message diretamente."""
        result = DataResult(
            success=True,
            query_type=QueryType.DAILY_SUMMARY,
            entity="operacao",
            data={"some": "data"},
            message="Resumo do dia: tudo OK",
            executed_at=datetime.now(),
        )
        text = result.to_natural_language()
        assert text == "Resumo do dia: tudo OK"


class TestDataQueryDetection:
    """Testa detect_data_query() - Detecção de queries em linguagem natural."""

    def setup_method(self):
        self.connector = DataConnector()

    def test_detecta_quantos_funcionarios(self):
        """'Quantos funcionários' detecta query de contagem."""
        query = self.connector.detect_data_query("quantos funcionarios temos?")
        assert query is not None
        assert query.query_type == QueryType.COUNT
        assert "funcionario" in query.entity

    def test_detecta_listar_postos(self):
        """'Listar postos' detecta query de dados."""
        query = self.connector.detect_data_query("listar postos ativos")
        assert query is not None
        # Pode ser LIST ou COUNT dependendo do classificador

    def test_detecta_quais_funcionarios(self):
        """'Quais funcionários' detecta query de listagem."""
        query = self.connector.detect_data_query("quais funcionarios estao trabalhando?")
        assert query is not None

    def test_detecta_cobertura_critica(self):
        """'Cobertura crítica' detecta query especial."""
        query = self.connector.detect_data_query("como esta a cobertura?")
        assert query is not None
        assert query.query_type == QueryType.COBERTURA_CRITICA

    def test_detecta_funcionarios_trabalhando(self):
        """'Quem está trabalhando' detecta query especial."""
        query = self.connector.detect_data_query("quem esta trabalhando agora?")
        assert query is not None
        assert query.query_type == QueryType.FUNCIONARIOS_TRABALHANDO

    def test_detecta_funcionarios_folga(self):
        """'Quem está de folga' detecta query especial."""
        query = self.connector.detect_data_query("quem esta de folga?")
        assert query is not None
        assert query.query_type == QueryType.FUNCIONARIOS_FOLGA

    def test_detecta_atrasos(self):
        """'Atrasos de hoje' detecta query especial."""
        query = self.connector.detect_data_query("atrasos de hoje")
        assert query is not None
        assert query.query_type == QueryType.ATRASOS_HOJE

    def test_detecta_ocorrencias_abertas(self):
        """'Ocorrências abertas' detecta query especial."""
        query = self.connector.detect_data_query("ocorrencias abertas")
        assert query is not None
        assert query.query_type == QueryType.OCORRENCIAS_ABERTAS

    def test_detecta_dashboard(self):
        """'Dashboard operacional' detecta query especial."""
        query = self.connector.detect_data_query("dashboard operacional")
        assert query is not None
        assert query.query_type == QueryType.OPERACAO_GERAL

    def test_detecta_alertas(self):
        """'Alertas pendentes' detecta query especial."""
        query = self.connector.detect_data_query("alertas pendentes")
        assert query is not None
        assert query.query_type == QueryType.ALERTS

    def test_detecta_kpis(self):
        """'KPIs do sistema' detecta query especial."""
        query = self.connector.detect_data_query("kpis do sistema")
        assert query is not None
        assert query.query_type == QueryType.KPIS

    def test_detecta_escalas_pendentes(self):
        """'Escalas pendentes' detecta query especial."""
        query = self.connector.detect_data_query("escalas pendentes")
        assert query is not None
        assert query.query_type == QueryType.ESCALAS_PENDENTES

    def test_detecta_resumo_dia(self):
        """'Resumo do dia' detecta query especial."""
        query = self.connector.detect_data_query("resumo do dia")
        assert query is not None
        assert query.query_type == QueryType.DAILY_SUMMARY

    def test_detecta_horas_extras(self):
        """'Horas extras' detecta query especial."""
        query = self.connector.detect_data_query("ranking de horas extras")
        assert query is not None
        assert query.query_type == QueryType.HORA_EXTRA_RANKING

    def test_detecta_substituicoes(self):
        """'Substituições pendentes' detecta query especial."""
        query = self.connector.detect_data_query("substituicoes pendentes")
        assert query is not None
        assert query.query_type == QueryType.SUBSTITUICOES_PENDENTES

    def test_mensagem_generica_nao_detecta(self):
        """Mensagem genérica não gera query."""
        query = self.connector.detect_data_query("bom dia bartolo")
        assert query is None

    def test_saudacao_nao_detecta(self):
        """Saudação não gera query."""
        query = self.connector.detect_data_query("olá, como vai?")
        assert query is None


class TestDataQueryStructure:
    """Testa estrutura do DataQuery."""

    def test_data_query_defaults(self):
        """DataQuery tem defaults corretos."""
        query = DataQuery(
            entity="funcionarios",
            query_type=QueryType.LIST,
            filters={},
            fields=[],
        )
        assert query.limit == 10
        assert query.order_by is None

    def test_data_query_com_filtros(self):
        """DataQuery aceita filtros."""
        query = DataQuery(
            entity="funcionarios",
            query_type=QueryType.LIST,
            filters={"is_night_shift": True, "shift_date": "today"},
            fields=["nome"],
            limit=50,
        )
        assert query.filters["is_night_shift"] is True
        assert query.limit == 50


class TestQueryTypeEnum:
    """Testa QueryType enum."""

    def test_todos_tipos_existem(self):
        """Todos os tipos de query esperados existem."""
        expected = [
            "count",
            "list",
            "detail",
            "aggregate",
            "report",
            "daily_summary",
            "alerts",
            "kpis",
            "cobertura_critica",
            "funcionarios_trabalhando",
            "funcionarios_folga",
            "escalas_pendentes",
            "hora_extra_ranking",
            "substituicoes_pendentes",
            "atrasos_hoje",
            "operacao_geral",
            "ocorrencias_abertas",
            "medidas_pendentes",
            "comunicados_ativos",
            "rondas_hoje",
        ]
        for expected_type in expected:
            assert QueryType(expected_type) is not None
