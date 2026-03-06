"""
Enhanced Action Detector com IA e fuzzy matching.

Melhora a detecção de ações com:
- Fuzzy matching para typos
- Expansão de sinônimos
- Fallback LLM para casos complexos
- Melhor extração de parâmetros

Author: Conecta PRO Team
Date: 2026-02-02
"""

import logging
import re
from difflib import SequenceMatcher
from typing import Any

from .action_detector import ActionDetector
from .action_schemas import ActionRequest
from .action_types import ActionType

logger = logging.getLogger(__name__)


class EnhancedActionDetector(ActionDetector):
    """Detector de ações com suporte a linguagem natural avançado."""

    # Sinônimos comuns para verbos de ação
    VERB_SYNONYMS = {
        "criar": ["fazer", "gerar", "montar", "adicionar", "incluir", "cadastrar"],
        "atualizar": ["editar", "modificar", "alterar", "mudar", "trocar"],
        "deletar": ["excluir", "remover", "apagar", "desativar", "eliminar"],
        "aprovar": ["autorizar", "confirmar", "aceitar", "validar"],
        "rejeitar": ["recusar", "negar", "reprovar", "desaprovar"],
        "enviar": ["mandar", "disparar", "transmitir", "encaminhar"],
        "ver": ["consultar", "mostrar", "exibir", "visualizar", "listar"],
        "iniciar": ["começar", "ativar", "ligar", "startar"],
        "parar": ["encerrar", "finalizar", "desligar", "terminar"],
    }

    # Entidades comuns e suas variações
    ENTITY_VARIANTS = {
        "escala": ["escalação", "planilha", "grade", "quadro"],
        "funcionário": ["funcionario", "colaborador", "empregado", "trabalhador", "func"],
        "posto": ["local", "unidade", "base", "condominio", "condomínio"],
        "ronda": ["inspeção", "inspecao", "vistoria", "patrulha"],
        "ocorrência": ["ocorrencia", "incidente", "evento", "problema"],
        "relatório": ["relatorio", "report", "dashboard"],
    }

    def __init__(self, llm_provider: Any | None = None, fuzzy_threshold: float = 0.8):
        """
        Initialize enhanced detector.

        Args:
            llm_provider: Provider LLM para fallback (opcional)
            fuzzy_threshold: Threshold para fuzzy matching (0-1)
        """
        super().__init__()
        self.llm_provider = llm_provider
        self.fuzzy_threshold = fuzzy_threshold
        self._expanded_patterns = self._expand_patterns_with_synonyms()

    def _expand_patterns_with_synonyms(self) -> dict:
        """Expande patterns com sinônimos para melhor cobertura."""
        expanded = {}

        for action_type, patterns in self.ACTION_PATTERNS.items():
            expanded_list = list(patterns)  # Copiar originais

            for pattern in patterns:
                # Expandir verbos
                for verb, synonyms in self.VERB_SYNONYMS.items():
                    if verb in pattern:
                        for synonym in synonyms:
                            new_pattern = pattern.replace(verb, synonym)
                            if new_pattern not in expanded_list:
                                expanded_list.append(new_pattern)

                # Expandir entidades
                for entity, variants in self.ENTITY_VARIANTS.items():
                    if entity in pattern:
                        for variant in variants:
                            new_pattern = pattern.replace(entity, variant)
                            if new_pattern not in expanded_list:
                                expanded_list.append(new_pattern)

            expanded[action_type] = expanded_list

        logger.info(f"Patterns expandidos: {sum(len(p) for p in expanded.values())} total")
        return expanded

    def detect(self, message: str, user_id: str, session_id: str) -> ActionRequest | None:
        """
        Detecta ação com suporte avançado a NLP.

        Tenta em ordem:
        1. Pattern matching exato (super())
        2. Pattern matching com fuzzy
        3. Fallback LLM (se disponível)

        Args:
            message: Mensagem do usuário
            user_id: ID do usuário
            session_id: ID da sessão

        Returns:
            ActionRequest se detectou, None caso contrário
        """
        # 1. Tentar detecção padrão primeiro (mais rápido)
        result = super().detect(message, user_id, session_id)
        if result and result.confidence >= 0.8:
            return result

        # 2. Tentar com patterns expandidos
        fuzzy_result = self._detect_with_fuzzy(message, user_id, session_id)
        if fuzzy_result:
            return fuzzy_result

        # 3. Fallback LLM se disponível
        if self.llm_provider:
            llm_result = self._detect_with_llm(message, user_id, session_id)
            if llm_result:
                return llm_result

        return result  # Retornar resultado original mesmo que baixa confiança

    def _detect_with_fuzzy(self, message: str, user_id: str, session_id: str) -> ActionRequest | None:
        """
        Detecta com fuzzy matching para tolerar typos.

        Args:
            message: Mensagem do usuário
            user_id: ID do usuário
            session_id: ID da sessão

        Returns:
            ActionRequest ou None
        """
        message_lower = message.lower()
        best_match = None
        best_score = 0.0
        best_action_type = None

        for action_type, patterns in self._expanded_patterns.items():
            for pattern in patterns:
                # Extrair palavras-chave do pattern
                keywords = self._extract_keywords_from_pattern(pattern)

                for keyword in keywords:
                    # Fuzzy match cada palavra da mensagem
                    for word in message_lower.split():
                        similarity = SequenceMatcher(None, keyword, word).ratio()

                        if similarity >= self.fuzzy_threshold and similarity > best_score:
                            best_score = similarity
                            best_action_type = action_type
                            best_match = pattern

        if best_match and best_action_type:
            logger.info(f"Fuzzy match: {best_action_type.value} (pattern: {best_match}, score: {best_score:.2f})")

            parameters = self._extract_parameters(message, best_action_type)
            confidence = self._calculate_confidence(message, best_action_type, parameters)

            # Penalizar confiança pelo fuzzy matching
            confidence = min(confidence * (0.9 + best_score * 0.1), 1.0)

            return ActionRequest(
                action_type=best_action_type,
                category=self._get_category(best_action_type),
                parameters=parameters,
                detected_from_message=message,
                confidence=confidence,
                user_id=user_id,
                session_id=session_id,
            )

        return None

    def _extract_keywords_from_pattern(self, pattern: str) -> list[str]:
        """
        Extrai palavras-chave de um pattern regex.

        Args:
            pattern: Pattern regex

        Returns:
            Lista de keywords principais
        """
        # Remove regex syntax e extrai palavras
        cleaned = re.sub(r"[?+*\[\](){}|\\]", " ", pattern)
        cleaned = re.sub(r"\s+", " ", cleaned)

        words = [w for w in cleaned.split() if len(w) > 3]
        return words[:3]  # Top 3 keywords

    def _detect_with_llm(self, message: str, user_id: str, session_id: str) -> ActionRequest | None:
        """
        Fallback: usa LLM para detectar intenção.

        Args:
            message: Mensagem do usuário
            user_id: ID do usuário
            session_id: ID da sessão

        Returns:
            ActionRequest ou None
        """
        if not self.llm_provider:
            return None

        try:
            # Criar prompt para LLM
            action_types_list = "\n".join([f"- {at.value}: {self._get_action_description(at)}" for at in ActionType])

            prompt = f"""Analise a mensagem do usuário e identifique se há uma intenção de ação.

Mensagem: "{message}"

Ações disponíveis:
{action_types_list}

Responda APENAS com o código da ação (ex: create_scale) ou "none" se não identificar ação clara.
Se identificar, também extraia parâmetros relevantes em formato JSON.

Formato:
action: <codigo_acao>
confidence: <0.0-1.0>
parameters: {{"param": "value"}}
"""

            # Chamar LLM
            response = self.llm_provider.generate(prompt, max_tokens=200)

            # Parse resposta
            action_match = re.search(r"action:\s*(\w+)", response)
            confidence_match = re.search(r"confidence:\s*([\d.]+)", response)
            params_match = re.search(r"parameters:\s*(\{[^}]+\})", response)

            if action_match and action_match.group(1) != "none":
                action_code = action_match.group(1)

                # Encontrar ActionType correspondente
                action_type = None
                for at in ActionType:
                    if at.value == action_code:
                        action_type = at
                        break

                if action_type:
                    confidence = float(confidence_match.group(1)) if confidence_match else 0.7
                    parameters = {}

                    if params_match:
                        import contextlib
                        import json

                        with contextlib.suppress(json.JSONDecodeError):
                            parameters = json.loads(params_match.group(1))

                    logger.info(f"LLM detectou ação: {action_type.value} (confidence: {confidence:.2f})")

                    return ActionRequest(
                        action_type=action_type,
                        category=self._get_category(action_type),
                        parameters=parameters,
                        detected_from_message=message,
                        confidence=confidence,
                        user_id=user_id,
                        session_id=session_id,
                    )

        except Exception as e:
            logger.error(f"Erro no fallback LLM: {e}", exc_info=True)

        return None

    def _get_action_description(self, action_type: ActionType) -> str:
        """Retorna descrição de uma ação para o LLM."""
        descriptions = {
            ActionType.CREATE_SCALE: "Criar nova escala de trabalho",
            ActionType.APPROVE_SCALE: "Aprovar escala pendente",
            ActionType.ALLOCATE_EMPLOYEE: "Alocar funcionário em posto",
            ActionType.GENERATE_REPORT: "Gerar relatório",
            # Adicionar mais conforme necessário
        }
        return descriptions.get(action_type, action_type.value.replace("_", " "))

    def _extract_parameters(self, message: str, action_type: ActionType) -> dict[str, Any]:
        """
        Extração de parâmetros com melhorias de NLP.

        Extends parent method com:
        - Melhor detecção de nomes
        - Suporte a datas relativas
        - Detecção de ranges
        """
        # Começar com extração padrão
        params = super()._extract_parameters(message, action_type)

        # Adicionar extrações avançadas
        message_lower = message.lower()

        # Datas relativas
        if "hoje" in message_lower:
            from datetime import datetime

            params["date"] = datetime.now().strftime("%Y-%m-%d")
        elif "amanhã" in message_lower or "amanha" in message_lower:
            from datetime import datetime, timedelta

            params["date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "próximo mês" in message_lower or "proximo mes" in message_lower:
            from datetime import datetime

            now = datetime.now()
            next_month = now.month % 12 + 1
            next_year = now.year + (1 if next_month == 1 else 0)
            params["month"] = next_month
            params["year"] = next_year

        # Detectar ranges de tempo
        range_match = re.search(r"(\d{1,2})[:\-]00\s*(?:às?|ate|a)\s*(\d{1,2})[:\-]00", message_lower)
        if range_match:
            params["start_hour"] = int(range_match.group(1))
            params["end_hour"] = int(range_match.group(2))

        # Detectar prioridade
        if any(word in message_lower for word in ["urgente", "urgência", "prioridade alta"]):
            params["priority"] = "high"
        elif any(word in message_lower for word in ["normal", "média prioridade"]):
            params["priority"] = "medium"
        elif any(word in message_lower for word in ["baixa", "pode esperar"]):
            params["priority"] = "low"

        # Detectar confirmação/negação
        if any(word in message_lower for word in ["sim", "confirma", "ok", "pode"]):
            params["confirmed"] = True
        elif any(word in message_lower for word in ["não", "nao", "cancela", "negativo"]):
            params["confirmed"] = False

        return params

    def get_suggestions(self, partial_message: str, limit: int = 5) -> list[str]:
        """
        Retorna sugestões de ações baseado em mensagem parcial.

        Útil para autocomplete em UI.

        Args:
            partial_message: Mensagem parcial do usuário
            limit: Máximo de sugestões

        Returns:
            Lista de sugestões de ações
        """
        suggestions = []
        partial_lower = partial_message.lower()

        for action_type, patterns in self._expanded_patterns.items():
            for pattern in patterns:
                keywords = self._extract_keywords_from_pattern(pattern)

                for keyword in keywords:
                    if keyword.startswith(partial_lower) or partial_lower in keyword:
                        desc = self._get_action_description(action_type)
                        if desc not in suggestions:
                            suggestions.append(desc)

                        if len(suggestions) >= limit:
                            return suggestions

        return suggestions
