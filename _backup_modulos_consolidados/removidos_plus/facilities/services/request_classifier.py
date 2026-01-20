"""
RequestClassifierService - Classificação inteligente de solicitações.

Este serviço implementa algoritmos de IA para:
- Classificar automaticamente solicitações de serviço
- Sugerir prioridade baseada no conteúdo
- Identificar solicitações similares
- Estimar tempo de resolução
- Sugerir responsável ideal
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from core.logging import logger
from modules.facilities.models.service_request import (
    ServiceRequestCategory,
    ServiceRequestPriority,
)


class RequestClassifierService:
    """
    Serviço inteligente de classificação de solicitações.

    Implementa algoritmos de IA para classificar e priorizar
    solicitações de serviço automaticamente.
    """

    # Keywords por categoria
    CATEGORY_KEYWORDS = {
        ServiceRequestCategory.ELETRICA: [
            "luz", "lampada", "lâmpada", "energia", "eletric", "tomada",
            "disjuntor", "fio", "interruptor", "apagou", "queimou",
            "curto", "circuito", "voltagem", "choque", "led", "luminaria",
        ],
        ServiceRequestCategory.HIDRAULICA: [
            "agua", "água", "vazamento", "vaza", "torneira", "pia",
            "descarga", "entupido", "entupiu", "cano", "esgoto",
            "goteira", "gotejando", "umidade", "infiltracao", "infiltração",
            "caixa dagua", "cisterna", "bomba", "registro", "ralo",
        ],
        ServiceRequestCategory.LIMPEZA: [
            "limpeza", "limpar", "sujo", "sujeira", "lixo", "detrito",
            "higienização", "faxina", "varrer", "mofo", "bolor",
        ],
        ServiceRequestCategory.SEGURANCA: [
            "camera", "câmera", "segurança", "portao", "portão", "tranca",
            "fechadura", "alarme", "interfone", "citofone", "cerca",
            "sensor", "arrombamento", "invasao", "invasão",
        ],
        ServiceRequestCategory.JARDINAGEM: [
            "jardim", "grama", "planta", "arvore", "árvore", "poda",
            "mato", "adubo", "irrigação", "irrigacao", "folha",
            "paisagismo", "canteiro", "cerca viva",
        ],
        ServiceRequestCategory.PINTURA: [
            "pintura", "pintar", "parede", "tinta", "descascando",
            "desbotado", "mancha", "rachadura", "trinca",
        ],
        ServiceRequestCategory.CIVIL: [
            "obra", "construção", "construcao", "reforma", "piso",
            "azulejo", "rejunte", "cimento", "concreto", "estrutura",
            "fissura", "demolição", "demolir",
        ],
        ServiceRequestCategory.CLIMATIZACAO: [
            "ar condicionado", "ar-condicionado", "climatizacao", "climatização",
            "ventilador", "exaustor", "quente", "frio", "temperatura",
            "split", "janeleiro",
        ],
        ServiceRequestCategory.ELEVADORES: [
            "elevador", "elevadores", "cabine", "subir", "descer",
            "parado", "travado", "porta elevador", "andar",
        ],
    }

    # Keywords de urgência
    URGENCY_KEYWORDS = {
        "critical": [
            "urgente", "emergencia", "emergência", "perigo", "risco",
            "imediato", "grave", "critico", "crítico", "fogo", "incendio",
            "incêndio", "inundacao", "inundação", "desabamento", "choque",
            "sem agua", "sem água", "sem luz", "vazamento grande",
        ],
        "high": [
            "urgência", "importante", "prioritario", "prioritário", "rapido",
            "rápido", "logo", "hoje", "agora", "muito", "grande",
            "varios", "vários", "quebrado", "não funciona", "parou",
        ],
        "medium": [
            "problema", "precisa", "necessario", "necessário", "arrumar",
            "consertar", "verificar", "checar", "olhar",
        ],
        "low": [
            "quando puder", "sem pressa", "oportunidade", "eventual",
            "melhoria", "sugestao", "sugestão", "poderia",
        ],
    }

    # Tempo médio de resolução por categoria (em horas)
    AVG_RESOLUTION_TIME = {
        ServiceRequestCategory.ELETRICA: 4,
        ServiceRequestCategory.HIDRAULICA: 6,
        ServiceRequestCategory.LIMPEZA: 2,
        ServiceRequestCategory.SEGURANCA: 8,
        ServiceRequestCategory.JARDINAGEM: 4,
        ServiceRequestCategory.PINTURA: 8,
        ServiceRequestCategory.CIVIL: 24,
        ServiceRequestCategory.CLIMATIZACAO: 8,
        ServiceRequestCategory.ELEVADORES: 12,
        ServiceRequestCategory.MANUTENCAO: 6,
        ServiceRequestCategory.OUTROS: 8,
    }

    def __init__(self) -> None:
        """Inicializa o serviço."""
        self._initialized = True

    def classify(
        self,
        title: str,
        description: str,
        location: Optional[str] = None,
        historical_requests: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Classifica uma solicitação de serviço.

        Args:
            title: Título da solicitação
            description: Descrição detalhada
            location: Localização (opcional)
            historical_requests: Histórico de solicitações similares

        Returns:
            Classificação com categoria, prioridade e análise
        """
        logger.info(f"Classificando solicitação: {title[:50]}...")

        # Combinar texto para análise
        full_text = f"{title} {description} {location or ''}".lower()

        # Classificar categoria
        category, category_confidence = self._classify_category(full_text)

        # Determinar prioridade
        priority, priority_reasons = self._determine_priority(full_text, category)

        # Encontrar similares
        similar = []
        if historical_requests:
            similar = self._find_similar_requests(
                title,
                description,
                historical_requests,
            )

        # Estimar tempo de resolução
        estimated_time = self._estimate_resolution_time(category, priority)

        # Extrair entidades
        entities = self._extract_entities(full_text)

        # Gerar análise
        analysis = self._generate_analysis(
            category,
            priority,
            entities,
            similar,
        )

        return {
            "suggested_category": category.value,
            "category_confidence": category_confidence,
            "suggested_priority": priority.value,
            "priority_reasons": priority_reasons,
            "estimated_resolution_hours": estimated_time,
            "similar_requests": similar[:3],
            "entities": entities,
            "analysis": analysis,
            "keywords_found": self._get_matched_keywords(full_text, category),
        }

    def suggest_assignee(
        self,
        category: ServiceRequestCategory,
        priority: ServiceRequestPriority,
        available_technicians: List[Dict[str, Any]],
        location: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Sugere responsáveis para a solicitação.

        Args:
            category: Categoria da solicitação
            priority: Prioridade
            available_technicians: Técnicos disponíveis
            location: Localização

        Returns:
            Lista de sugestões ordenadas por adequação
        """
        logger.info(f"Sugerindo responsável para categoria {category.value}")

        if not available_technicians:
            return []

        suggestions = []

        for tech in available_technicians:
            score = self._calculate_technician_score(
                tech,
                category,
                priority,
                location,
            )
            suggestions.append(
                {
                    "technician_id": tech.get("id"),
                    "name": tech.get("name"),
                    "score": score,
                    "specialties": tech.get("specialties", []),
                    "current_workload": tech.get("current_requests", 0),
                    "avg_resolution_time": tech.get("avg_resolution_time"),
                }
            )

        # Ordenar por score
        suggestions.sort(key=lambda x: x["score"], reverse=True)

        return suggestions[:5]

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analisa sentimento do texto.

        Args:
            text: Texto para análise

        Returns:
            Análise de sentimento
        """
        text_lower = text.lower()

        # Palavras negativas
        negative_words = [
            "problema", "não funciona", "quebrado", "horrível", "péssimo",
            "absurdo", "inaceitável", "inaceitavel", "ridiculo", "ridículo",
            "vergonha", "demora", "nunca", "sempre", "reclamação", "reclamacao",
        ]

        # Palavras urgentes/preocupadas
        urgent_words = [
            "urgente", "perigo", "risco", "socorro", "ajuda", "por favor",
            "preciso", "necessito", "imediato",
        ]

        negative_count = sum(1 for word in negative_words if word in text_lower)
        urgent_count = sum(1 for word in urgent_words if word in text_lower)

        if negative_count >= 3 or urgent_count >= 2:
            sentiment = "very_negative"
            urgency = "high"
        elif negative_count >= 1 or urgent_count >= 1:
            sentiment = "negative"
            urgency = "medium"
        else:
            sentiment = "neutral"
            urgency = "low"

        return {
            "sentiment": sentiment,
            "perceived_urgency": urgency,
            "negative_indicators": negative_count,
            "urgent_indicators": urgent_count,
            "requires_follow_up": sentiment == "very_negative",
        }

    def _classify_category(
        self,
        text: str,
    ) -> Tuple[ServiceRequestCategory, float]:
        """Classifica categoria baseado em keywords."""
        scores = {}

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[category] = score

        if not scores:
            return ServiceRequestCategory.MANUTENCAO, 0.5

        best_category = max(scores.items(), key=lambda x: x[1])
        total_matches = sum(scores.values())
        confidence = min(0.95, best_category[1] / max(total_matches, 1) * 0.8 + 0.2)

        return best_category[0], round(confidence, 2)

    def _determine_priority(
        self,
        text: str,
        category: ServiceRequestCategory,
    ) -> Tuple[ServiceRequestPriority, List[str]]:
        """Determina prioridade baseado em análise."""
        reasons = []

        # Verificar keywords de urgência
        for priority_level, keywords in self.URGENCY_KEYWORDS.items():
            matches = [kw for kw in keywords if kw in text]
            if matches:
                reasons.append(f"Palavras-chave detectadas: {', '.join(matches[:3])}")

                if priority_level == "critical":
                    return ServiceRequestPriority.CRITICAL, reasons
                if priority_level == "high":
                    return ServiceRequestPriority.HIGH, reasons
                if priority_level == "low":
                    return ServiceRequestPriority.LOW, reasons

        # Categorias que são naturalmente mais urgentes
        high_priority_categories = [
            ServiceRequestCategory.SEGURANCA,
            ServiceRequestCategory.ELEVADORES,
        ]

        if category in high_priority_categories:
            reasons.append(f"Categoria {category.value} requer atenção prioritária")
            return ServiceRequestPriority.HIGH, reasons

        # Padrão
        reasons.append("Prioridade padrão baseada no conteúdo")
        return ServiceRequestPriority.MEDIUM, reasons

    def _find_similar_requests(
        self,
        title: str,
        description: str,
        historical: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Encontra solicitações similares no histórico."""
        if not historical:
            return []

        current_words = set(
            re.findall(r"\w+", f"{title} {description}".lower())
        )

        similarities = []

        for req in historical:
            req_words = set(
                re.findall(
                    r"\w+",
                    f"{req.get('title', '')} {req.get('description', '')}".lower(),
                )
            )

            if not req_words:
                continue

            # Calcular similaridade (Jaccard)
            intersection = len(current_words & req_words)
            union = len(current_words | req_words)
            similarity = intersection / union if union > 0 else 0

            if similarity > 0.3:  # Threshold
                similarities.append(
                    {
                        "id": req.get("id"),
                        "title": req.get("title"),
                        "similarity": round(similarity, 2),
                        "resolution": req.get("resolution"),
                        "resolution_time_hours": req.get("resolution_time_hours"),
                    }
                )

        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities

    def _estimate_resolution_time(
        self,
        category: ServiceRequestCategory,
        priority: ServiceRequestPriority,
    ) -> int:
        """Estima tempo de resolução em horas."""
        base_time = self.AVG_RESOLUTION_TIME.get(category, 8)

        # Ajustar por prioridade
        priority_factors = {
            ServiceRequestPriority.CRITICAL: 0.5,  # Mais rápido
            ServiceRequestPriority.HIGH: 0.75,
            ServiceRequestPriority.MEDIUM: 1.0,
            ServiceRequestPriority.LOW: 1.5,
            ServiceRequestPriority.URGENT: 0.25,
        }

        factor = priority_factors.get(priority, 1.0)
        return max(1, int(base_time * factor))

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extrai entidades do texto."""
        entities = {
            "locations": [],
            "equipment": [],
            "quantities": [],
        }

        # Extrair localizações
        location_patterns = [
            r"bloco\s*[a-zA-Z0-9]+",
            r"apartamento\s*\d+",
            r"apt\.?\s*\d+",
            r"andar\s*\d+",
            r"térreo",
            r"cobertura",
            r"garagem",
            r"subsolo",
            r"hall",
            r"portaria",
            r"piscina",
            r"academia",
            r"salão",
            r"churrasqueira",
        ]

        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["locations"].extend(matches)

        # Extrair equipamentos
        equipment_patterns = [
            r"elevador\s*\d*",
            r"ar[\s-]condicionado",
            r"bomba\s*\d*",
            r"gerador",
            r"portão\s*(social|garagem)?",
            r"interfone",
            r"câmera\s*\d*",
        ]

        for pattern in equipment_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["equipment"].extend(matches)

        # Extrair quantidades
        quantity_patterns = [
            r"\d+\s*(unidades?|peças?|itens?|pontos?)",
            r"(uma?|duas?|três|tres|quatro|cinco)\s+\w+",
        ]

        for pattern in quantity_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities["quantities"].extend(
                    [m if isinstance(m, str) else m[0] for m in matches]
                )

        return entities

    def _generate_analysis(
        self,
        category: ServiceRequestCategory,
        priority: ServiceRequestPriority,
        entities: Dict[str, List[str]],
        similar: List[Dict[str, Any]],
    ) -> str:
        """Gera análise textual."""
        parts = []

        parts.append(
            f"Solicitação classificada como {category.value} "
            f"com prioridade {priority.value}."
        )

        if entities["locations"]:
            parts.append(f"Localização identificada: {', '.join(entities['locations'][:3])}")

        if entities["equipment"]:
            parts.append(f"Equipamento mencionado: {', '.join(entities['equipment'][:3])}")

        if similar:
            avg_time = sum(s.get("resolution_time_hours", 0) for s in similar) / len(similar)
            parts.append(
                f"Baseado em {len(similar)} solicitações similares, "
                f"tempo médio de resolução: {int(avg_time)} horas."
            )

        return " ".join(parts)

    def _get_matched_keywords(
        self,
        text: str,
        category: ServiceRequestCategory,
    ) -> List[str]:
        """Retorna keywords que foram encontradas."""
        keywords = self.CATEGORY_KEYWORDS.get(category, [])
        return [kw for kw in keywords if kw in text][:5]

    def _calculate_technician_score(
        self,
        technician: Dict[str, Any],
        category: ServiceRequestCategory,
        _priority: ServiceRequestPriority,
        _location: Optional[str],
    ) -> float:
        """Calcula score de adequação do técnico."""
        score = 50.0  # Base

        # Especialidade
        specialties = technician.get("specialties", [])
        if category.value in specialties:
            score += 30

        # Carga de trabalho atual
        workload = technician.get("current_requests", 0)
        if workload == 0:
            score += 15
        elif workload < 3:
            score += 10
        elif workload > 5:
            score -= 20

        # Tempo médio de resolução
        avg_time = technician.get("avg_resolution_time")
        if avg_time and avg_time < self.AVG_RESOLUTION_TIME.get(category, 8):
            score += 10

        # Avaliação
        rating = technician.get("rating", 0)
        score += rating * 2

        # Disponibilidade
        if technician.get("available", True):
            score += 5
        else:
            score -= 30

        return min(100, max(0, score))


# Singleton
request_classifier = RequestClassifierService()
