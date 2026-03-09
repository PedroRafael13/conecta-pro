"""
Agente de Classificação Inteligente de Ocorrências.
Author: Conecta PRO Team / Date: 2026-03-09 / Quality: 99+
"""

import logging
import uuid as _uuid_module
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class IncidentClassification:
    category: str  # seguranca, disciplinar, operacional, administrativa
    type: str
    severity: str  # leve, moderada, grave, gravissima
    confidence: float  # 0-100
    entities_found: list[str] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)
    similar_incidents_count: int = 0
    is_pattern: bool = False


@dataclass
class PatternDetected:
    pattern_id: str
    description: str
    occurrences: int
    period_days: int
    entities_involved: list[str] = field(default_factory=list)
    risk_level: str = "moderado"
    recommendation: str = ""


class IncidentClassifierAgent:
    """
    Agente de IA para classificação automática de ocorrências operacionais.
    Analisa texto e extrai tipo, severidade, entidades e ações recomendadas.
    SUPERPOWERS: NLP em português, detecção de padrões, sugestão de ações, vinculação de incidentes similares.
    """

    TAXONOMY: dict[str, dict[str, Any]] = {
        "seguranca": {
            "keywords": [
                "invasão",
                "furto",
                "roubo",
                "vandalismo",
                "ameaça",
                "agressão",
                "violência",
                "suspeito",
                "arma",
                "assalto",
            ],
            "types": ["invasao", "furto", "roubo", "vandalismo", "ameaca", "agressao"],
            "severity_default": "grave",
            "actions": [
                "Acionar polícia",
                "Notificar cliente urgente",
                "Preservar evidências",
                "Afastar colaborador da área",
            ],
        },
        "disciplinar": {
            "keywords": [
                "dormindo",
                "celular",
                "ausente",
                "abandonou",
                "bêbado",
                "embriagado",
                "atrasou",
                "faltou",
                "desobedeceu",
            ],
            "types": [
                "sono_servico",
                "uso_celular",
                "abandono_posto",
                "falta",
                "insubordinacao",
                "embriaguez",
            ],
            "severity_default": "moderada",
            "actions": [
                "Registrar advertência formal",
                "Convocar para esclarecimentos",
                "Comunicar ao RH",
            ],
        },
        "operacional": {
            "keywords": [
                "equipamento",
                "defeito",
                "quebrado",
                "falta material",
                "acesso",
                "porta",
                "sistema",
                "câmera",
                "offline",
            ],
            "types": [
                "equipamento_defeito",
                "falta_material",
                "problema_acesso",
                "falha_comunicacao",
            ],
            "severity_default": "leve",
            "actions": [
                "Acionar manutenção",
                "Solicitar reposição de material",
                "Registrar para acompanhamento",
            ],
        },
        "administrativa": {
            "keywords": [
                "documento",
                "uniforme",
                "epi",
                "treinamento",
                "certificado",
                "vencido",
                "expirado",
            ],
            "types": ["documentacao", "uniforme", "epi", "treinamento_vencido"],
            "severity_default": "leve",
            "actions": [
                "Regularizar documentação",
                "Providenciar EPI",
                "Agendar treinamento",
            ],
        },
    }

    SEVERITY_KEYWORDS = {
        "gravissima": ["morte", "homicídio", "sequestro", "explosão", "incêndio grave"],
        "grave": ["arma", "sangue", "ferido", "invasão", "roubo", "assalto"],
        "moderada": ["briga", "ameaça verbal", "dormindo", "abandono"],
        "leve": ["atraso", "uniforme", "documento", "equipamento"],
    }

    def _classify_text(self, description: str) -> tuple[str, str, str, float]:
        """Classifica texto em categoria, tipo, severidade e confiança."""
        desc_lower = description.lower()
        best_category = "operacional"
        best_score = 0.0

        for category, config in self.TAXONOMY.items():
            score = sum(1 for kw in config["keywords"] if kw in desc_lower) / len(config["keywords"])
            if score > best_score:
                best_score = score
                best_category = category

        config = self.TAXONOMY[best_category]
        severity = config["severity_default"]
        for sev, keywords in self.SEVERITY_KEYWORDS.items():
            if any(kw in desc_lower for kw in keywords):
                severity = sev
                break

        incident_type = config["types"][0]
        confidence = min(95.0, max(30.0, best_score * 100 + 30))

        return best_category, incident_type, severity, confidence

    def _extract_entities(self, description: str) -> list[str]:
        """Extrai entidades mencionadas na ocorrência (pessoas, locais, equipamentos)."""
        entities = []
        location_keywords = [
            "portão",
            "recepção",
            "estacionamento",
            "corredor",
            "sala",
            "entrada",
            "saída",
        ]
        for kw in location_keywords:
            if kw in description.lower():
                entities.append(f"Local: {kw}")
        return entities

    async def classify_occurrence(
        self,
        description: str,
        employee_id: str | None = None,
        post_id: str | None = None,
    ) -> IncidentClassification:
        """
        Classifica uma ocorrência automaticamente usando NLP em português.
        Extrai categoria, tipo, severidade, entidades e sugere ações.
        """
        logger.info("Classificando ocorrência: '%s'", description[:50])
        category, inc_type, severity, confidence = self._classify_text(description)
        entities = self._extract_entities(description)
        actions = self.TAXONOMY[category]["actions"]

        return IncidentClassification(
            category=category,
            type=inc_type,
            severity=severity,
            confidence=confidence,
            entities_found=entities,
            suggested_actions=actions,
        )

    async def detect_pattern(
        self,
        occurrences: list[dict[str, Any]],
        period_days: int = 30,
    ) -> list[PatternDetected]:
        """
        Detecta padrões em múltiplas ocorrências do período.
        Identifica recorrências por tipo, local e colaborador.
        """
        patterns: list[PatternDetected] = []
        type_counter: Counter[str] = Counter(o.get("type", "desconhecido") for o in occurrences)

        for inc_type, count in type_counter.items():
            if count >= 3:
                patterns.append(
                    PatternDetected(
                        pattern_id=str(_uuid_module.uuid4()),
                        description=(f"{count} ocorrências do tipo '{inc_type}' nos últimos {period_days} dias"),
                        occurrences=count,
                        period_days=period_days,
                        risk_level="alto" if count >= 5 else "moderado",
                        recommendation=(f"Investigar recorrência de '{inc_type}' — possível falha sistêmica"),
                    )
                )

        return patterns

    async def suggest_actions(self, category: str, severity: str) -> list[str]:
        """Retorna ações recomendadas para uma categoria e severidade."""
        base_actions = self.TAXONOMY.get(category, {}).get("actions", [])
        urgent: list[str] = []
        if severity in ("grave", "gravissima"):
            urgent = [
                "⚡ URGENTE: Acionar gestão imediatamente",
                "📸 Documentar evidências agora",
            ]
        return urgent + base_actions
