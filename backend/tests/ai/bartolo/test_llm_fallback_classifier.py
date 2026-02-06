"""
Testes para o LLM Fallback Classifier.
Fase 3 do Plano de Refinamento do Bartolo.
"""

import pytest
import sys
sys.path.insert(0, '/app')

from modules.ai.bartolo.services.llm_fallback_classifier import (
    LLMFallbackClassifier,
    FallbackResult,
    FallbackIntentCategory,
    INTENT_MAPPING,
)


class TestLLMFallbackClassifierInit:
    """Testes de inicialização do LLMFallbackClassifier."""

    def test_init_sem_provider(self):
        """Testa inicialização sem LLM provider."""
        classifier = LLMFallbackClassifier()
        assert classifier is not None
        assert classifier.llm_provider is None

    def test_init_com_provider_mock(self):
        """Testa inicialização com provider mock."""
        mock_provider = object()
        classifier = LLMFallbackClassifier(llm_provider=mock_provider)
        assert classifier.llm_provider == mock_provider

    def test_set_llm_provider(self):
        """Testa definição do provider após inicialização."""
        classifier = LLMFallbackClassifier()
        mock_provider = object()
        classifier.set_llm_provider(mock_provider)
        assert classifier.llm_provider == mock_provider


class TestFallbackResultDataclass:
    """Testes para o dataclass FallbackResult."""

    def test_fallback_result_creation(self):
        """Testa criação de FallbackResult."""
        result = FallbackResult(
            intent=FallbackIntentCategory.ESCALA_GERAR,
            confidence=0.9,
            reasoning="Usuário quer criar escala",
            agent_type="escala",
            agent_intent="gerar_escala",
        )
        assert result.intent == FallbackIntentCategory.ESCALA_GERAR
        assert result.confidence == 0.9
        assert result.agent_type == "escala"
        assert result.from_cache is False

    def test_fallback_result_to_dict(self):
        """Testa conversão para dicionário."""
        result = FallbackResult(
            intent=FallbackIntentCategory.DATA_COBERTURA,
            confidence=0.85,
            reasoning="Consulta de cobertura",
            agent_type="data",
            agent_intent="cobertura_critica",
        )
        d = result.to_dict()
        assert d["intent"] == "data_cobertura"
        assert d["confidence"] == 0.85
        assert d["agent_type"] == "data"


class TestIntentMapping:
    """Testes para o mapeamento de intents."""

    def test_escala_intents_mapeados(self):
        """Verifica que intents de escala estão mapeados."""
        assert FallbackIntentCategory.ESCALA_GERAR in INTENT_MAPPING
        assert FallbackIntentCategory.ESCALA_CONSULTAR in INTENT_MAPPING
        assert FallbackIntentCategory.ESCALA_OTIMIZAR in INTENT_MAPPING
        assert FallbackIntentCategory.ESCALA_VALIDAR in INTENT_MAPPING

    def test_substituicao_intents_mapeados(self):
        """Verifica que intents de substituição estão mapeados."""
        assert FallbackIntentCategory.SUBSTITUICAO_BUSCAR in INTENT_MAPPING
        assert FallbackIntentCategory.SUBSTITUICAO_URGENTE in INTENT_MAPPING

    def test_alerta_intents_mapeados(self):
        """Verifica que intents de alerta estão mapeados."""
        assert FallbackIntentCategory.ALERTA_VER in INTENT_MAPPING
        assert FallbackIntentCategory.ALERTA_CRITICO in INTENT_MAPPING

    def test_data_intents_mapeados(self):
        """Verifica que intents de data estão mapeados."""
        assert FallbackIntentCategory.DATA_COBERTURA in INTENT_MAPPING
        assert FallbackIntentCategory.DATA_FUNCIONARIOS in INTENT_MAPPING

    def test_mapping_structure(self):
        """Verifica estrutura do mapeamento."""
        for intent, mapping in INTENT_MAPPING.items():
            assert isinstance(mapping, tuple)
            assert len(mapping) == 2
            assert isinstance(mapping[0], str)  # agent_type
            assert isinstance(mapping[1], str)  # agent_intent


class TestCacheOperations:
    """Testes para operações de cache."""

    def test_cache_key_generation(self):
        """Testa geração de chave de cache."""
        classifier = LLMFallbackClassifier()
        key1 = classifier._get_cache_key("Crie uma escala")
        key2 = classifier._get_cache_key("crie uma escala")  # Diferente case
        key3 = classifier._get_cache_key("Crie uma escala!")  # Com pontuação

        # Devem ser iguais após normalização
        assert key1 == key2
        assert key1 == key3

    def test_cache_key_different_messages(self):
        """Testa que mensagens diferentes geram keys diferentes."""
        classifier = LLMFallbackClassifier()
        key1 = classifier._get_cache_key("Crie uma escala")
        key2 = classifier._get_cache_key("Ver alertas")

        assert key1 != key2

    def test_save_and_get_from_cache(self):
        """Testa salvar e recuperar do cache."""
        classifier = LLMFallbackClassifier()

        result = FallbackResult(
            intent=FallbackIntentCategory.ESCALA_GERAR,
            confidence=0.9,
            reasoning="Test",
        )

        classifier._save_to_cache("test message", result)
        cached = classifier._get_from_cache("test message")

        assert cached is not None
        assert cached.intent == FallbackIntentCategory.ESCALA_GERAR
        assert cached.from_cache is True

    def test_clear_cache(self):
        """Testa limpeza do cache."""
        classifier = LLMFallbackClassifier()

        result = FallbackResult(
            intent=FallbackIntentCategory.ALERTA_VER,
            confidence=0.8,
            reasoning="Test",
        )

        classifier._save_to_cache("test", result)
        assert classifier._get_from_cache("test") is not None

        classifier.clear_cache()
        assert classifier._get_from_cache("test") is None

    def test_cache_stats(self):
        """Testa estatísticas do cache."""
        classifier = LLMFallbackClassifier()

        result = FallbackResult(
            intent=FallbackIntentCategory.GREETING,
            confidence=0.95,
            reasoning="Test",
        )

        classifier._save_to_cache("msg1", result)
        classifier._save_to_cache("msg2", result)

        stats = classifier.get_cache_stats()
        assert stats["total_entries"] == 2
        assert stats["valid_entries"] == 2


class TestShouldUseFallback:
    """Testes para decisão de usar fallback."""

    def test_should_use_fallback_low_confidence(self):
        """Testa que fallback é usado com baixa confiança."""
        classifier = LLMFallbackClassifier()
        assert classifier.should_use_fallback(0.3) is True
        assert classifier.should_use_fallback(0.5) is True
        assert classifier.should_use_fallback(0.59) is True

    def test_should_not_use_fallback_high_confidence(self):
        """Testa que fallback NÃO é usado com alta confiança."""
        classifier = LLMFallbackClassifier()
        assert classifier.should_use_fallback(0.6) is False
        assert classifier.should_use_fallback(0.7) is False
        assert classifier.should_use_fallback(0.9) is False
        assert classifier.should_use_fallback(1.0) is False

    def test_threshold_customization(self):
        """Testa customização do threshold."""
        classifier = LLMFallbackClassifier()
        classifier.CONFIDENCE_THRESHOLD = 0.8

        assert classifier.should_use_fallback(0.7) is True
        assert classifier.should_use_fallback(0.8) is False


class TestParseResponse:
    """Testes para parsing de resposta do LLM."""

    def test_parse_valid_json(self):
        """Testa parsing de JSON válido."""
        classifier = LLMFallbackClassifier()

        response = '{"intent": "escala_gerar", "confidence": 0.9, "reasoning": "quer criar"}'
        result = classifier._parse_llm_response(response)

        assert result.intent == FallbackIntentCategory.ESCALA_GERAR
        assert result.confidence == 0.9
        assert result.reasoning == "quer criar"

    def test_parse_json_with_text_around(self):
        """Testa parsing de JSON com texto ao redor."""
        classifier = LLMFallbackClassifier()

        response = 'Aqui está a classificação: {"intent": "alerta_ver", "confidence": 0.85, "reasoning": "ver alertas"} fim.'
        result = classifier._parse_llm_response(response)

        assert result.intent == FallbackIntentCategory.ALERTA_VER
        assert result.confidence == 0.85

    def test_parse_invalid_json(self):
        """Testa parsing de JSON inválido."""
        classifier = LLMFallbackClassifier()

        response = 'not a json response'
        result = classifier._parse_llm_response(response)

        assert result.intent == FallbackIntentCategory.UNKNOWN
        assert result.confidence == 0.3

    def test_parse_unknown_intent(self):
        """Testa parsing com intent desconhecido."""
        classifier = LLMFallbackClassifier()

        response = '{"intent": "intent_nao_existe", "confidence": 0.8, "reasoning": "test"}'
        result = classifier._parse_llm_response(response)

        assert result.intent == FallbackIntentCategory.UNKNOWN

    def test_parse_sets_agent_mapping(self):
        """Testa que parsing define mapeamento de agente."""
        classifier = LLMFallbackClassifier()

        response = '{"intent": "substituicao_urgente", "confidence": 0.9, "reasoning": "urgente"}'
        result = classifier._parse_llm_response(response)

        assert result.agent_type == "substituicao"
        assert result.agent_intent == "urgente"

    def test_parse_confidence_bounds(self):
        """Testa que confidence é limitado entre 0 e 1."""
        classifier = LLMFallbackClassifier()

        # Confidence > 1
        response = '{"intent": "greeting", "confidence": 1.5, "reasoning": "test"}'
        result = classifier._parse_llm_response(response)
        assert result.confidence == 1.0

        # Confidence < 0
        response = '{"intent": "greeting", "confidence": -0.5, "reasoning": "test"}'
        result = classifier._parse_llm_response(response)
        assert result.confidence == 0.0


class TestBuildPrompt:
    """Testes para construção de prompts."""

    def test_build_user_prompt_simple(self):
        """Testa construção de prompt simples."""
        classifier = LLMFallbackClassifier()

        prompt = classifier._build_user_prompt("Crie uma escala")

        assert "Crie uma escala" in prompt
        assert "Classifique" in prompt

    def test_build_user_prompt_with_context(self):
        """Testa construção de prompt com contexto."""
        classifier = LLMFallbackClassifier()

        context = {
            "role": "supervisor",
            "recent_intents": ["escala_consultar", "data_cobertura"],
        }
        prompt = classifier._build_user_prompt("Ver postos", context)

        assert "Ver postos" in prompt
        assert "supervisor" in prompt
        assert "escala_consultar" in prompt


class TestClassifyWithoutProvider:
    """Testes de classificação sem LLM provider."""

    @pytest.mark.asyncio
    async def test_classify_without_provider(self):
        """Testa classificação sem provider configurado."""
        classifier = LLMFallbackClassifier()

        result = await classifier.classify("Crie uma escala")

        assert result.intent == FallbackIntentCategory.UNKNOWN
        assert result.confidence == 0.3
        assert "não disponível" in result.reasoning.lower()


class TestFallbackIntentCategories:
    """Testes para categorias de intent."""

    def test_all_categories_defined(self):
        """Verifica que todas as categorias estão definidas."""
        # Escalas
        assert hasattr(FallbackIntentCategory, 'ESCALA_GERAR')
        assert hasattr(FallbackIntentCategory, 'ESCALA_CONSULTAR')
        assert hasattr(FallbackIntentCategory, 'ESCALA_OTIMIZAR')
        assert hasattr(FallbackIntentCategory, 'ESCALA_VALIDAR')

        # Substituições
        assert hasattr(FallbackIntentCategory, 'SUBSTITUICAO_BUSCAR')
        assert hasattr(FallbackIntentCategory, 'SUBSTITUICAO_URGENTE')
        assert hasattr(FallbackIntentCategory, 'SUBSTITUICAO_HISTORICO')

        # Alertas
        assert hasattr(FallbackIntentCategory, 'ALERTA_VER')
        assert hasattr(FallbackIntentCategory, 'ALERTA_CRITICO')
        assert hasattr(FallbackIntentCategory, 'ALERTA_RESOLVER')

        # Data
        assert hasattr(FallbackIntentCategory, 'DATA_COBERTURA')
        assert hasattr(FallbackIntentCategory, 'DATA_FUNCIONARIOS')
        assert hasattr(FallbackIntentCategory, 'DATA_POSTOS')
        assert hasattr(FallbackIntentCategory, 'DATA_RESUMO')
        assert hasattr(FallbackIntentCategory, 'DATA_KPIS')

        # Genéricas
        assert hasattr(FallbackIntentCategory, 'UNKNOWN')
        assert hasattr(FallbackIntentCategory, 'GREETING')

    def test_categories_are_strings(self):
        """Verifica que categorias são strings."""
        for category in FallbackIntentCategory:
            assert isinstance(category.value, str)


class TestSystemPrompt:
    """Testes para o prompt do sistema."""

    def test_system_prompt_contains_categories(self):
        """Verifica que o prompt contém as categorias."""
        prompt = LLMFallbackClassifier.CLASSIFIER_SYSTEM_PROMPT

        assert "escala_gerar" in prompt
        assert "substituicao_urgente" in prompt
        assert "alerta_critico" in prompt
        assert "data_cobertura" in prompt

    def test_system_prompt_has_json_format(self):
        """Verifica que o prompt especifica formato JSON."""
        prompt = LLMFallbackClassifier.CLASSIFIER_SYSTEM_PROMPT

        assert "JSON" in prompt
        assert "intent" in prompt
        assert "confidence" in prompt
        assert "reasoning" in prompt
