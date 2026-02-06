"""Tests para IntentClassifier."""

import pytest

from modules.ai.conversation.models.chat_message import IntentCategory
from modules.ai.conversation.services.intent_classifier import (
    IntentClassifier,
    IntentResult,
)


@pytest.fixture
def classifier():
    """Retorna instancia do classificador."""
    return IntentClassifier()


class TestIntentClassifier:
    """Testes do classificador de intencoes."""

    def test_classify_greeting_oi(self, classifier):
        """Testa classificacao de saudacao 'oi'."""
        result = classifier.classify("oi")

        assert isinstance(result, IntentResult)
        assert result.intent == IntentCategory.GREETING
        assert result.confidence > 0.5
        assert "oi" in result.keywords_matched

    def test_classify_greeting_bom_dia(self, classifier):
        """Testa classificacao de saudacao 'bom dia'."""
        result = classifier.classify("Bom dia!")

        assert result.intent == IntentCategory.GREETING
        assert result.confidence > 0.5

    def test_classify_greeting_ola(self, classifier):
        """Testa classificacao de saudacao 'ola'."""
        result = classifier.classify("Olá, tudo bem?")

        assert result.intent == IntentCategory.GREETING

    def test_classify_farewell(self, classifier):
        """Testa classificacao de despedida."""
        result = classifier.classify("Tchau, ate mais!")

        assert result.intent == IntentCategory.FAREWELL
        assert result.confidence > 0.5

    def test_classify_help_navigation(self, classifier):
        """Testa classificacao de ajuda com navegacao."""
        result = classifier.classify("Como faço para acessar o módulo de CRM?")

        assert result.intent == IntentCategory.HELP_NAVIGATION

    def test_classify_data_query(self, classifier):
        """Testa classificacao de consulta de dados."""
        result = classifier.classify("Mostre todos os clientes cadastrados")

        assert result.intent == IntentCategory.DATA_QUERY

    def test_classify_data_query_quantos(self, classifier):
        """Testa consulta com 'quantos'."""
        result = classifier.classify("Quantos leads temos este mês?")

        assert result.intent == IntentCategory.DATA_QUERY

    def test_classify_action_request_criar(self, classifier):
        """Testa requisicao de acao 'criar'."""
        result = classifier.classify("Criar um novo lead para João Silva")

        assert result.intent == IntentCategory.ACTION_REQUEST
        assert "criar" in result.keywords_matched

    def test_classify_action_request_deletar(self, classifier):
        """Testa requisicao de acao 'deletar'."""
        result = classifier.classify("Deletar o registro selecionado")

        assert result.intent == IntentCategory.ACTION_REQUEST

    def test_classify_analysis_request(self, classifier):
        """Testa requisicao de analise."""
        result = classifier.classify("Gere um relatório de vendas do mês")

        assert result.intent == IntentCategory.ANALYSIS_REQUEST

    def test_classify_troubleshooting(self, classifier):
        """Testa classificacao de problema."""
        result = classifier.classify("O sistema está dando erro ao salvar")

        assert result.intent == IntentCategory.TROUBLESHOOTING

    def test_classify_troubleshooting_help(self, classifier):
        """Testa pedido de ajuda."""
        result = classifier.classify("Preciso de ajuda, não consigo acessar")

        assert result.intent == IntentCategory.TROUBLESHOOTING

    def test_classify_general_conversation(self, classifier):
        """Testa conversa geral (sem intent especifico)."""
        result = classifier.classify("Hoje está um dia bonito")

        assert result.intent == IntentCategory.GENERAL_CONVERSATION
        assert result.confidence <= 0.5

    def test_extract_email_entity(self, classifier):
        """Testa extracao de entidade email."""
        result = classifier.classify("O email do cliente é joao@empresa.com")

        assert "email" in result.entities
        assert result.entities["email"] == "joao@empresa.com"

    def test_extract_phone_entity(self, classifier):
        """Testa extracao de entidade telefone."""
        result = classifier.classify("O telefone é 11 99999-8888")

        assert "phone" in result.entities

    def test_extract_cpf_entity(self, classifier):
        """Testa extracao de entidade CPF."""
        result = classifier.classify("CPF do cliente: 123.456.789-00")

        assert "cpf" in result.entities

    def test_extract_cnpj_entity(self, classifier):
        """Testa extracao de entidade CNPJ."""
        result = classifier.classify("O CNPJ da empresa é 12.345.678/0001-90")

        assert "cnpj" in result.entities

    def test_extract_money_entity(self, classifier):
        """Testa extracao de valor monetario."""
        result = classifier.classify("O valor total é R$ 1.500,00")

        assert "money" in result.entities

    def test_extract_module_entity(self, classifier):
        """Testa extracao de modulo."""
        result = classifier.classify("Abra o módulo de CRM")

        assert "module" in result.entities
        assert result.entities["module"] == "crm"

    def test_normalize_text_accents(self, classifier):
        """Testa normalizacao de acentos."""
        normalized = classifier._normalize_text("Olá, como está você?")

        assert "ola" in normalized
        assert "esta" in normalized
        assert "voce" in normalized

    def test_normalize_text_uppercase(self, classifier):
        """Testa normalizacao de maiusculas."""
        normalized = classifier._normalize_text("OLÁ MUNDO")

        assert normalized == "ola mundo"

    def test_intent_description(self, classifier):
        """Testa descricao de intencoes."""
        desc = classifier.get_intent_description(IntentCategory.GREETING)
        assert desc == "Saudacao"

        desc = classifier.get_intent_description(IntentCategory.DATA_QUERY)
        assert desc == "Consulta de dados e informacoes"

    @pytest.mark.asyncio
    async def test_classify_async(self, classifier):
        """Testa versao assincrona."""
        result = await classifier.classify_async("Oi, bom dia!")

        assert result.intent == IntentCategory.GREETING

    def test_context_boost(self, classifier):
        """Testa boost de confianca com contexto."""
        result_no_context = classifier.classify("Abra o módulo de vendas")
        result_with_context = classifier.classify(
            "Abra o módulo de vendas",
            context={"module": "crm"},
        )

        # Com contexto compativel, confianca pode ser maior
        assert result_with_context.confidence >= result_no_context.confidence - 0.1

    def test_multiple_intents_picks_highest(self, classifier):
        """Testa que multiplas intencoes selecionam a maior."""
        # Mensagem com caracteristicas de multiplas intencoes
        result = classifier.classify("Oi, pode criar um novo cliente para mim?")

        # Deve pegar uma das intencoes validas
        assert result.intent in [
            IntentCategory.GREETING,
            IntentCategory.ACTION_REQUEST,
        ]
        assert result.confidence > 0


class TestIntentResult:
    """Testes do dataclass IntentResult."""

    def test_intent_result_creation(self):
        """Testa criacao do resultado."""
        result = IntentResult(
            intent=IntentCategory.GREETING,
            confidence=0.95,
            keywords_matched=["oi", "ola"],
            entities={"email": "test@test.com"},
        )

        assert result.intent == IntentCategory.GREETING
        assert result.confidence == 0.95
        assert len(result.keywords_matched) == 2
        assert "email" in result.entities
