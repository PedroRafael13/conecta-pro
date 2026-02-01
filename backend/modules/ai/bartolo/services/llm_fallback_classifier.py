"""
LLM Fallback Classifier - Classificador de intenção com fallback para LLM.

Fase 3 do Plano de Refinamento do Bartolo.

Usado quando o classificador regex (IntentClassifier) retorna baixa confiança.
Chama um LLM com um mini-prompt otimizado para classificação de intenções.
"""

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class FallbackIntentCategory(str, Enum):
    """Categorias de intenção para o fallback classifier."""

    # Operações de escala
    ESCALA_GERAR = "escala_gerar"
    ESCALA_CONSULTAR = "escala_consultar"
    ESCALA_OTIMIZAR = "escala_otimizar"
    ESCALA_VALIDAR = "escala_validar"

    # Substituições
    SUBSTITUICAO_BUSCAR = "substituicao_buscar"
    SUBSTITUICAO_URGENTE = "substituicao_urgente"
    SUBSTITUICAO_HISTORICO = "substituicao_historico"

    # Alertas
    ALERTA_VER = "alerta_ver"
    ALERTA_CRITICO = "alerta_critico"
    ALERTA_RESOLVER = "alerta_resolver"

    # Consultas de dados
    DATA_COBERTURA = "data_cobertura"
    DATA_FUNCIONARIOS = "data_funcionarios"
    DATA_POSTOS = "data_postos"
    DATA_RESUMO = "data_resumo"
    DATA_KPIS = "data_kpis"

    # Genéricas
    HELP_NAVIGATION = "help_navigation"
    ACTION_REQUEST = "action_request"
    ANALYSIS_REQUEST = "analysis_request"
    GENERAL_CONVERSATION = "general_conversation"
    GREETING = "greeting"
    UNKNOWN = "unknown"


# Mapeamento de categorias do fallback para categorias do sistema
INTENT_MAPPING = {
    FallbackIntentCategory.ESCALA_GERAR: ("escala", "gerar_escala"),
    FallbackIntentCategory.ESCALA_CONSULTAR: ("escala", "escala_semana"),
    FallbackIntentCategory.ESCALA_OTIMIZAR: ("escala", "otimizar_escala"),
    FallbackIntentCategory.ESCALA_VALIDAR: ("escala", "validar_escala"),
    FallbackIntentCategory.SUBSTITUICAO_BUSCAR: ("substituicao", "buscar_substituto"),
    FallbackIntentCategory.SUBSTITUICAO_URGENTE: ("substituicao", "urgente"),
    FallbackIntentCategory.SUBSTITUICAO_HISTORICO: ("substituicao", "historico"),
    FallbackIntentCategory.ALERTA_VER: ("alerta", "ver_alertas"),
    FallbackIntentCategory.ALERTA_CRITICO: ("alerta", "alertas_criticos"),
    FallbackIntentCategory.ALERTA_RESOLVER: ("alerta", "resolver"),
    FallbackIntentCategory.DATA_COBERTURA: ("data", "cobertura_critica"),
    FallbackIntentCategory.DATA_FUNCIONARIOS: ("data", "funcionarios_trabalhando"),
    FallbackIntentCategory.DATA_POSTOS: ("data", "operacao_geral"),
    FallbackIntentCategory.DATA_RESUMO: ("data", "daily_summary"),
    FallbackIntentCategory.DATA_KPIS: ("data", "kpis"),
}


@dataclass
class FallbackResult:
    """Resultado do classificador de fallback."""

    intent: FallbackIntentCategory
    confidence: float
    reasoning: str
    agent_type: str | None = None  # escala, substituicao, alerta, data, None
    agent_intent: str | None = None  # intent específico do agente
    from_cache: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "agent_type": self.agent_type,
            "agent_intent": self.agent_intent,
            "from_cache": self.from_cache,
        }


class LLMFallbackClassifier:
    """
    Classificador de intenção com fallback para LLM.

    Usado quando o classificador regex tem baixa confiança.
    Implementa cache para reduzir chamadas ao LLM.
    """

    # Threshold de confiança para usar fallback
    CONFIDENCE_THRESHOLD = 0.6

    # TTL do cache em segundos (24 horas)
    CACHE_TTL = 86400

    # Prompt do sistema para classificação
    CLASSIFIER_SYSTEM_PROMPT = """Você é um classificador de intenções para o Bartolo, um assistente IA de gestão operacional de segurança patrimonial.

CONTEXTO DO SISTEMA:
- Gestão de escalas de trabalho (12x36, 5x2, 6x1)
- Substituições de funcionários
- Alertas operacionais (cobertura, atrasos, documentos)
- Consultas de dados (funcionários, postos, métricas)

CATEGORIAS DE INTENÇÃO (escolha EXATAMENTE uma):

ESCALAS:
- escala_gerar: Criar/montar/gerar nova escala
- escala_consultar: Ver/consultar escala existente (semana, mês)
- escala_otimizar: Melhorar/otimizar/reduzir custo de escala
- escala_validar: Verificar/validar/checar escala (conflitos, CLT)

SUBSTITUIÇÕES:
- substituicao_buscar: Buscar/encontrar substituto
- substituicao_urgente: Substituição urgente/emergência
- substituicao_historico: Histórico de substituições

ALERTAS:
- alerta_ver: Ver/listar alertas
- alerta_critico: Alertas críticos/urgentes
- alerta_resolver: Resolver um alerta

CONSULTAS DE DADOS:
- data_cobertura: Cobertura de postos, postos descobertos
- data_funcionarios: Funcionários disponíveis, trabalhando, de folga
- data_postos: Informações sobre postos
- data_resumo: Resumo do dia, dashboard
- data_kpis: KPIs, métricas, indicadores

OUTRAS:
- help_navigation: Ajuda, navegação no sistema
- action_request: Ação genérica (criar, editar, deletar algo)
- analysis_request: Análise, relatório
- general_conversation: Conversa geral
- greeting: Saudação (oi, bom dia, etc)
- unknown: Não conseguiu classificar

REGRAS:
1. Responda APENAS com JSON válido
2. Confidence deve ser entre 0.0 e 1.0
3. Reasoning deve ser curto (máx 50 palavras)
4. Prefira categorias específicas (escala_, substituicao_, alerta_, data_) sobre genéricas

FORMATO DE RESPOSTA:
{"intent": "categoria", "confidence": 0.85, "reasoning": "explicação breve"}"""

    def __init__(self, llm_provider=None):
        """
        Inicializa o classificador.

        Args:
            llm_provider: Provedor de LLM (opcional, pode ser injetado depois)
        """
        self.llm_provider = llm_provider
        self._cache: dict[str, tuple[FallbackResult, datetime]] = {}

    def set_llm_provider(self, llm_provider):
        """Define o provedor de LLM."""
        self.llm_provider = llm_provider

    def _get_cache_key(self, message: str) -> str:
        """Gera chave de cache para a mensagem."""
        # Normaliza a mensagem
        normalized = message.lower().strip()
        # Remove acentos e caracteres especiais
        normalized = re.sub(r"[^\w\s]", "", normalized)
        # Hash para key compacta
        return hashlib.md5(normalized.encode(), usedforsecurity=False).hexdigest()  # noqa: S324

    def _get_from_cache(self, message: str) -> FallbackResult | None:
        """Busca resultado no cache."""
        cache_key = self._get_cache_key(message)

        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            # Verifica TTL
            if datetime.utcnow() - timestamp < timedelta(seconds=self.CACHE_TTL):
                result.from_cache = True
                logger.debug(f"LLM Fallback cache hit: {message[:50]}...")
                return result
            else:
                # Cache expirado
                del self._cache[cache_key]

        return None

    def _save_to_cache(self, message: str, result: FallbackResult):
        """Salva resultado no cache."""
        cache_key = self._get_cache_key(message)
        self._cache[cache_key] = (result, datetime.utcnow())

        # Limpeza periódica do cache (mantém apenas últimas 1000 entradas)
        if len(self._cache) > 1000:
            # Remove entradas mais antigas
            sorted_items = sorted(
                self._cache.items(),
                key=lambda x: x[1][1],  # Ordena por timestamp
                reverse=True,
            )
            self._cache = dict(sorted_items[:800])

    def _build_user_prompt(self, message: str, context: dict | None = None) -> str:
        """Constrói o prompt do usuário para classificação."""
        prompt = f'Classifique a intenção desta mensagem:\n\n"{message}"'

        if context:
            if context.get("role"):
                prompt += f"\n\nContexto: Usuário é {context['role']}"
            if context.get("recent_intents"):
                prompt += f"\nIntenções recentes: {', '.join(context['recent_intents'][:3])}"

        return prompt

    def _parse_llm_response(self, response: str) -> FallbackResult:
        """Parseia a resposta do LLM."""
        try:
            # Tenta extrair JSON da resposta
            # O LLM pode retornar com texto antes/depois do JSON
            json_match = re.search(r"\{[^{}]*\}", response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)

            intent_str = data.get("intent", "unknown")
            confidence = float(data.get("confidence", 0.5))
            reasoning = data.get("reasoning", "")

            # Valida e converte intent
            try:
                intent = FallbackIntentCategory(intent_str)
            except ValueError:
                logger.warning(f"Intent desconhecido do LLM: {intent_str}")
                intent = FallbackIntentCategory.UNKNOWN

            # Limita confidence entre 0 e 1
            confidence = max(0.0, min(1.0, confidence))

            # Busca mapeamento para agente
            agent_type = None
            agent_intent = None
            if intent in INTENT_MAPPING:
                agent_type, agent_intent = INTENT_MAPPING[intent]

            return FallbackResult(
                intent=intent,
                confidence=confidence,
                reasoning=reasoning,
                agent_type=agent_type,
                agent_intent=agent_intent,
            )

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Erro ao parsear resposta do LLM: {e}, resposta: {response[:200]}")
            return FallbackResult(
                intent=FallbackIntentCategory.UNKNOWN,
                confidence=0.3,
                reasoning=f"Erro ao parsear resposta: {str(e)[:50]}",
            )

    async def classify(
        self,
        message: str,
        regex_confidence: float = 0.0,
        context: dict | None = None,
    ) -> FallbackResult:
        """
        Classifica a intenção da mensagem usando LLM.

        Args:
            message: Mensagem do usuário
            regex_confidence: Confiança do classificador regex (para logging)
            context: Contexto adicional (role, recent_intents, etc)

        Returns:
            FallbackResult com intenção classificada
        """
        # 1. Verifica cache
        cached = self._get_from_cache(message)
        if cached:
            return cached

        # 2. Verifica se LLM provider está disponível
        if not self.llm_provider:
            logger.warning("LLM Provider não configurado para fallback classifier")
            return FallbackResult(
                intent=FallbackIntentCategory.UNKNOWN,
                confidence=0.3,
                reasoning="LLM Provider não disponível",
            )

        # 3. Chama LLM
        try:
            logger.info(f"LLM Fallback classifier chamado (regex_conf={regex_confidence:.2f}): {message[:50]}...")

            user_prompt = self._build_user_prompt(message, context)

            # Usa modelo mais leve para classificação
            response = await self.llm_provider.generate(
                system_prompt=self.CLASSIFIER_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.1,  # Baixa temperatura para respostas consistentes
                max_tokens=150,  # Resposta curta
            )

            # 4. Parseia resposta (response é LLMResponse, extrair .content)
            result = self._parse_llm_response(response.content)

            # 5. Salva no cache
            self._save_to_cache(message, result)

            logger.info(f"LLM Fallback result: {result.intent.value} (conf={result.confidence:.2f})")

            return result

        except Exception as e:
            logger.error(f"Erro no LLM Fallback classifier: {e}")
            return FallbackResult(
                intent=FallbackIntentCategory.UNKNOWN,
                confidence=0.3,
                reasoning=f"Erro: {str(e)[:50]}",
            )

    def should_use_fallback(self, regex_confidence: float) -> bool:
        """
        Verifica se deve usar o fallback LLM.

        Args:
            regex_confidence: Confiança do classificador regex

        Returns:
            True se deve usar fallback
        """
        return regex_confidence < self.CONFIDENCE_THRESHOLD

    def clear_cache(self):
        """Limpa o cache."""
        self._cache.clear()
        logger.info("LLM Fallback cache cleared")

    def get_cache_stats(self) -> dict[str, Any]:
        """Retorna estatísticas do cache."""
        now = datetime.utcnow()
        valid_entries = sum(1 for _, (_, ts) in self._cache.items() if now - ts < timedelta(seconds=self.CACHE_TTL))
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self._cache) - valid_entries,
        }
