"""Classificador de intencoes para IA conversacional."""

import re
from dataclasses import dataclass
from typing import Optional

from modules.ai.conversation.models.chat_message import IntentCategory


@dataclass
class IntentResult:
    """Resultado da classificacao de intencao."""

    intent: IntentCategory
    confidence: float
    keywords_matched: list[str]
    entities: dict[str, str]


class IntentClassifier:
    """
    Classificador de intencoes do usuario.

    Usa uma combinacao de:
    - Palavras-chave
    - Padroes regex
    - Contexto da conversa
    """

    # Mapeamento de intencoes com palavras-chave e pesos
    INTENT_PATTERNS: dict[IntentCategory, dict] = {
        IntentCategory.GREETING: {
            "keywords": [
                "oi",
                "ola",
                "hey",
                "bom dia",
                "boa tarde",
                "boa noite",
                "e ai",
                "salve",
                "fala",
            ],
            "weight": 1.0,
            "requires_start": True,
        },
        IntentCategory.FAREWELL: {
            "keywords": [
                "tchau",
                "adeus",
                "ate mais",
                "ate logo",
                "flw",
                "falou",
                "valeu",
                "obrigado por tudo",
            ],
            "weight": 1.0,
            "requires_start": False,
        },
        IntentCategory.HELP_NAVIGATION: {
            "keywords": [
                "como",
                "onde",
                "encontrar",
                "localizar",
                "achar",
                "navegar",
                "ir para",
                "acessar",
                "abrir",
                "menu",
                "tela",
                "pagina",
            ],
            "weight": 0.9,
            "requires_start": False,
        },
        IntentCategory.DATA_QUERY: {
            "keywords": [
                "mostrar",
                "listar",
                "quantos",
                "dados",
                "ver",
                "exibir",
                "consultar",
                "buscar",
                "pesquisar",
                "total",
                "quantidade",
                "estatistica",
            ],
            "weight": 0.9,
            "requires_start": False,
        },
        IntentCategory.ACTION_REQUEST: {
            "keywords": [
                "criar",
                "adicionar",
                "deletar",
                "excluir",
                "alterar",
                "editar",
                "atualizar",
                "modificar",
                "remover",
                "cadastrar",
                "registrar",
                "salvar",
            ],
            "weight": 0.95,
            "requires_start": False,
        },
        IntentCategory.ANALYSIS_REQUEST: {
            "keywords": [
                "analisar",
                "relatorio",
                "comparar",
                "grafico",
                "dashboard",
                "tendencia",
                "evolucao",
                "desempenho",
                "performance",
                "resumo",
                "insight",
            ],
            "weight": 0.9,
            "requires_start": False,
        },
        IntentCategory.SYSTEM_INFO: {
            "keywords": [
                "status",
                "versao",
                "configuracao",
                "sistema",
                "sobre",
                "informacao",
                "config",
                "setup",
                "ambiente",
            ],
            "weight": 0.85,
            "requires_start": False,
        },
        IntentCategory.TROUBLESHOOTING: {
            "keywords": [
                "erro",
                "problema",
                "nao funciona",
                "bug",
                "falha",
                "travou",
                "lento",
                "nao consigo",
                "ajuda",
                "socorro",
                "deu ruim",
            ],
            "weight": 0.95,
            "requires_start": False,
        },
        IntentCategory.FEEDBACK: {
            "keywords": [
                "sugestao",
                "feedback",
                "melhorar",
                "reclamacao",
                "elogio",
                "opiniao",
                "avaliar",
                "nota",
            ],
            "weight": 0.85,
            "requires_start": False,
        },
    }

    # Padroes regex para extracao de entidades
    ENTITY_PATTERNS = {
        "email": r"[\w\.-]+@[\w\.-]+\.\w+",
        "phone": r"(\d{2}[\s-]?)?\d{4,5}[\s-]?\d{4}",
        "cpf": r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}",
        "cnpj": r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}",
        "date": r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
        "money": r"R?\$?\s*\d+(?:[.,]\d{2,3})*(?:[.,]\d{2})?",
        "number": r"\b\d+\b",
        "module": r"\b(crm|financeiro|rh|estoque|vendas|clientes|leads|contratos)\b",
    }

    def __init__(self) -> None:
        """Inicializa o classificador."""
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compila os padroes regex."""
        self._entity_regex = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.ENTITY_PATTERNS.items()
        }

    def _normalize_text(self, text: str) -> str:
        """Normaliza o texto para classificacao."""
        # Converte para minusculas
        text = text.lower()

        # Remove acentos comuns (simplificado)
        replacements = {
            "á": "a",
            "à": "a",
            "ã": "a",
            "â": "a",
            "é": "e",
            "ê": "e",
            "í": "i",
            "ó": "o",
            "ô": "o",
            "õ": "o",
            "ú": "u",
            "ç": "c",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)

        # Remove pontuacao extra
        text = re.sub(r"[^\w\s]", " ", text)

        # Remove espacos extras
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def _extract_entities(self, text: str) -> dict[str, str]:
        """Extrai entidades do texto."""
        entities = {}

        for entity_name, pattern in self._entity_regex.items():
            matches = pattern.findall(text)
            if matches:
                # Pega a primeira ocorrencia
                entities[entity_name] = matches[0] if isinstance(matches[0], str) else matches[0][0]

        return entities

    def _calculate_intent_score(
        self, normalized_text: str, intent: IntentCategory
    ) -> tuple[float, list[str]]:
        """Calcula score para uma intencao."""
        config = self.INTENT_PATTERNS.get(intent)
        if not config:
            return 0.0, []

        keywords = config["keywords"]
        weight = config["weight"]
        requires_start = config.get("requires_start", False)

        matched_keywords = []
        words = normalized_text.split()

        for keyword in keywords:
            keyword_normalized = self._normalize_text(keyword)

            # Verifica se requer estar no inicio
            if requires_start:
                if normalized_text.startswith(keyword_normalized):
                    matched_keywords.append(keyword)
            else:
                # Verifica se a palavra-chave esta presente
                if keyword_normalized in normalized_text:
                    matched_keywords.append(keyword)
                # Verifica palavras individuais
                elif any(keyword_normalized in word for word in words):
                    matched_keywords.append(keyword)

        if not matched_keywords:
            return 0.0, []

        # Calcula score baseado na quantidade de matches
        base_score = len(matched_keywords) / len(keywords)
        final_score = min(base_score * weight * 1.5, 1.0)

        return final_score, matched_keywords

    def classify(
        self, message: str, context: Optional[dict] = None
    ) -> IntentResult:
        """
        Classifica a intencao da mensagem.

        Args:
            message: Mensagem do usuario
            context: Contexto adicional da conversa

        Returns:
            IntentResult com intencao, confianca e entidades
        """
        normalized = self._normalize_text(message)

        # Extrai entidades
        entities = self._extract_entities(message)

        # Calcula scores para cada intencao
        scores: list[tuple[IntentCategory, float, list[str]]] = []

        for intent in IntentCategory:
            score, keywords = self._calculate_intent_score(normalized, intent)
            if score > 0:
                scores.append((intent, score, keywords))

        # Ordena por score
        scores.sort(key=lambda x: x[1], reverse=True)

        # Se nenhuma intencao foi identificada, retorna general_conversation
        if not scores:
            return IntentResult(
                intent=IntentCategory.GENERAL_CONVERSATION,
                confidence=0.5,
                keywords_matched=[],
                entities=entities,
            )

        # Retorna a intencao com maior score
        best_intent, confidence, keywords = scores[0]

        # Ajusta confianca baseado no contexto
        if context:
            # Se o contexto indica um modulo especifico, aumenta confianca
            if context.get("module") and entities.get("module"):
                confidence = min(confidence * 1.1, 1.0)

        return IntentResult(
            intent=best_intent,
            confidence=round(confidence, 3),
            keywords_matched=keywords,
            entities=entities,
        )

    async def classify_async(
        self, message: str, context: Optional[dict] = None
    ) -> IntentResult:
        """Versao assincrona do classify."""
        return self.classify(message, context)

    def get_intent_description(self, intent: IntentCategory) -> str:
        """Retorna descricao da intencao."""
        descriptions = {
            IntentCategory.HELP_NAVIGATION: "Ajuda com navegacao no sistema",
            IntentCategory.DATA_QUERY: "Consulta de dados e informacoes",
            IntentCategory.ACTION_REQUEST: "Solicitacao de acao no sistema",
            IntentCategory.ANALYSIS_REQUEST: "Solicitacao de analise ou relatorio",
            IntentCategory.SYSTEM_INFO: "Informacoes sobre o sistema",
            IntentCategory.TROUBLESHOOTING: "Resolucao de problemas",
            IntentCategory.FEEDBACK: "Feedback ou sugestao",
            IntentCategory.GREETING: "Saudacao",
            IntentCategory.FAREWELL: "Despedida",
            IntentCategory.GENERAL_CONVERSATION: "Conversa geral",
        }
        return descriptions.get(intent, "Intencao nao identificada")
