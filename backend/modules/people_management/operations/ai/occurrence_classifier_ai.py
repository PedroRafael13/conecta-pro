"""
Occurrence Classifier AI — Classificacao automatica de ocorrencias operacionais.

Classifica ocorrencias em categorias e severidades com base na descricao
textual e evidencias fornecidas.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Categorias de ocorrencia
CATEGORIES: list[str] = [
    "disciplinar",
    "operacional",
    "seguranca_trabalho",
    "conduta",
    "assiduidade",
]

# Severidades
SEVERITIES: list[str] = [
    "leve",
    "moderada",
    "grave",
    "gravissima",
]

# Palavras-chave por categoria (PT-BR)
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "disciplinar": [
        "insubordinacao",
        "desobediencia",
        "indisciplina",
        "desrespeito",
        "recusa",
        "ordem",
        "advertencia",
        "suspensao",
        "justa causa",
        "abandono",
        "regulamento",
        "norma interna",
    ],
    "operacional": [
        "escala",
        "turno",
        "posto",
        "ronda",
        "equipamento",
        "uniforme",
        "radio",
        "viatura",
        "camera",
        "alarme",
        "sensor",
        "portaria",
        "chave",
        "controle acesso",
        "patrimonio",
        "material",
        "procedimento",
        "protocolo",
        "relatorio",
    ],
    "seguranca_trabalho": [
        "acidente",
        "incidente",
        "lesao",
        "ferimento",
        "queda",
        "epi",
        "epc",
        "cipa",
        "nr",
        "insalubridade",
        "periculosidade",
        "risco",
        "saude",
        "emergencia",
        "primeiros socorros",
        "cat",
        "afastamento medico",
    ],
    "conduta": [
        "assedio",
        "discriminacao",
        "agressao",
        "ameaca",
        "furto",
        "roubo",
        "embriaguez",
        "alcool",
        "droga",
        "entorpecente",
        "conduta inadequada",
        "comportamento",
        "moral",
        "etica",
        "sexual",
        "violencia",
    ],
    "assiduidade": [
        "falta",
        "atraso",
        "ausencia",
        "nao compareceu",
        "atestado",
        "absenteismo",
        "pontualidade",
        "frequencia",
        "justificativa",
        "dispensa",
        "liberacao antecipada",
        "saida antecipada",
    ],
}

# Indicadores de severidade
SEVERITY_INDICATORS: dict[str, list[str]] = {
    "gravissima": [
        "justa causa",
        "demissao",
        "crime",
        "policia",
        "delegacia",
        "agressao fisica",
        "furto",
        "roubo",
        "arma",
        "morte",
        "assedio sexual",
        "droga",
        "entorpecente",
    ],
    "grave": [
        "suspensao",
        "reincidencia",
        "recorrente",
        "segunda vez",
        "acidente grave",
        "lesao",
        "ameaca",
        "embriaguez",
        "abandono posto",
        "dano patrimonial",
    ],
    "moderada": [
        "advertencia escrita",
        "ocorrencia formal",
        "desrespeito",
        "atraso reiterado",
        "desobediencia",
        "descuido",
        "negligencia",
        "falta injustificada",
    ],
    "leve": [
        "orientacao",
        "verbal",
        "primeira vez",
        "leve",
        "atraso",
        "esquecimento",
        "descuido menor",
    ],
}

# Acoes sugeridas por severidade
SUGGESTED_ACTIONS: dict[str, list[str]] = {
    "leve": [
        "Orientacao verbal pelo supervisor imediato",
        "Registro na ficha do colaborador",
    ],
    "moderada": [
        "Advertencia escrita formal",
        "Treinamento de reciclagem",
        "Acompanhamento pelo RH por 30 dias",
    ],
    "grave": [
        "Suspensao de 1 a 5 dias",
        "Sindicancia interna",
        "Comunicacao ao cliente",
        "Remanejamento de posto",
    ],
    "gravissima": [
        "Analise juridica para possivel justa causa",
        "Afastamento imediato do posto",
        "Registro de boletim de ocorrencia (se aplicavel)",
        "Comunicacao formal ao cliente",
        "Abertura de processo administrativo",
    ],
}


class OccurrenceClassifierAI:
    """Classificador automatico de ocorrencias operacionais.

    Utiliza analise de palavras-chave e heuristicas para classificar
    ocorrencias em categorias e severidades, sugerindo acoes apropriadas.

    A confianca (confidence) e calculada com base na quantidade e
    qualidade dos indicadores encontrados no texto.
    """

    def __init__(self) -> None:
        """Inicializa o classificador com dicionarios de referencia."""
        self.category_keywords = CATEGORY_KEYWORDS.copy()
        self.severity_indicators = SEVERITY_INDICATORS.copy()
        self.suggested_actions = SUGGESTED_ACTIONS.copy()

    async def classify_occurrence(
        self,
        description: str,
        evidence: list[str] | None = None,
    ) -> dict[str, Any]:
        """Classifica uma ocorrencia com base na descricao e evidencias.

        Analisa o texto fornecido para determinar categoria, severidade,
        acao sugerida e nivel de confianca da classificacao.

        Args:
            description: Descricao textual da ocorrencia.
            evidence: Lista opcional de URLs ou descricoes de evidencias
                      (fotos, videos, documentos).

        Returns:
            Dict contendo:
                - category: Uma das categorias definidas.
                - severity: Nivel de severidade (leve a gravissima).
                - suggested_action: Lista de acoes recomendadas.
                - confidence: Float 0.0-1.0 indicando confianca.
                - details: Dict com informacoes adicionais da analise.
        """
        if not description or not description.strip():
            return {
                "category": "operacional",
                "severity": "leve",
                "suggested_action": ["Verificar detalhes da ocorrencia"],
                "confidence": 0.0,
                "details": {"error": "Descricao vazia ou invalida"},
            }

        text = description.lower().strip()
        evidence_text = " ".join(evidence).lower() if evidence else ""
        combined_text = f"{text} {evidence_text}"

        # Classificar categoria
        category, cat_confidence = self._classify_category(combined_text)

        # Classificar severidade
        severity, sev_confidence = self._classify_severity(combined_text)

        # Ajustar severidade com base em evidencias
        if evidence and len(evidence) >= 3:
            # Muitas evidencias sugerem ocorrencia mais grave
            severity_idx = SEVERITIES.index(severity)
            if severity_idx < len(SEVERITIES) - 1:
                severity = SEVERITIES[min(severity_idx + 1, len(SEVERITIES) - 1)]

        # Calcular confianca geral
        confidence = cat_confidence * 0.6 + sev_confidence * 0.4

        # Acoes sugeridas
        actions = self.suggested_actions.get(severity, [])

        # Detalhes da analise
        details: dict[str, Any] = {
            "category_confidence": round(cat_confidence, 3),
            "severity_confidence": round(sev_confidence, 3),
            "keywords_found": self._find_matching_keywords(combined_text, category),
            "evidence_count": len(evidence) if evidence else 0,
            "text_length": len(description),
        }

        return {
            "category": category,
            "severity": severity,
            "suggested_action": actions,
            "confidence": round(confidence, 3),
            "details": details,
        }

    def _classify_category(self, text: str) -> tuple[str, float]:
        """Determina a categoria da ocorrencia por keyword matching.

        Args:
            text: Texto normalizado para analise.

        Returns:
            Tupla (categoria, confianca).
        """
        scores: dict[str, int] = {}

        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
                    # Bonus para match exato de palavras compostas
                    if " " in keyword:
                        score += 1
            scores[category] = score

        if not any(scores.values()):
            return "operacional", 0.2

        best_category = max(scores, key=scores.get)  # type: ignore[arg-type]
        best_score = scores[best_category]
        total_keywords = len(self.category_keywords[best_category])

        confidence = min(best_score / max(total_keywords * 0.3, 1), 1.0)

        return best_category, confidence

    def _classify_severity(self, text: str) -> tuple[str, float]:
        """Determina a severidade da ocorrencia por keyword matching.

        Verifica de gravissima para leve, retornando a maior severidade
        encontrada.

        Args:
            text: Texto normalizado para analise.

        Returns:
            Tupla (severidade, confianca).
        """
        for severity in reversed(SEVERITIES):
            indicators = self.severity_indicators.get(severity, [])
            matches = sum(1 for ind in indicators if ind in text)

            if matches > 0:
                confidence = min(matches / max(len(indicators) * 0.2, 1), 1.0)
                return severity, confidence

        return "leve", 0.3

    def _find_matching_keywords(
        self,
        text: str,
        category: str,
    ) -> list[str]:
        """Retorna as palavras-chave encontradas no texto para a categoria.

        Args:
            text: Texto normalizado.
            category: Categoria classificada.

        Returns:
            Lista de keywords que deram match.
        """
        keywords = self.category_keywords.get(category, [])
        return [kw for kw in keywords if kw in text]
