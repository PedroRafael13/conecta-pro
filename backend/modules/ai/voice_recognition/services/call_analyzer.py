"""
Call Analyzer Service - Sprint 52.

Service for analyzing phone calls and voice interactions.
"""

import re
import time
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID


class CallAnalyzer:
    """Service for analyzing phone calls."""

    # Sentiment keywords (Portuguese)
    POSITIVE_KEYWORDS = {
        "obrigado", "obrigada", "agradeço", "excelente", "ótimo", "perfeito",
        "bom", "boa", "satisfeito", "satisfeita", "resolvido", "ajudou",
        "maravilhoso", "fantástico", "parabéns", "adorei", "gostei",
    }

    NEGATIVE_KEYWORDS = {
        "problema", "reclamação", "insatisfeito", "insatisfeita", "péssimo",
        "horrível", "terrível", "demora", "atraso", "não funciona", "quebrado",
        "irritado", "irritada", "raiva", "absurdo", "vergonha", "inaceitável",
        "cancelar", "desistir", "nunca mais", "pior",
    }

    # Call type patterns
    CALL_TYPE_PATTERNS = {
        "support": ["problema", "não funciona", "erro", "ajuda", "suporte"],
        "complaint": ["reclamação", "insatisfeito", "péssimo", "absurdo"],
        "inquiry": ["gostaria de saber", "informação", "dúvida", "pergunta"],
        "scheduling": ["agendar", "marcar", "visita", "horário", "data"],
        "emergency": ["urgente", "emergência", "imediato", "grave"],
        "sales": ["contratar", "preço", "valor", "plano", "proposta"],
    }

    # Emotion patterns
    EMOTION_PATTERNS = {
        "anger": ["raiva", "irritado", "absurdo", "inaceitável", "vergonha"],
        "frustration": ["cansado", "demora", "novamente", "de novo", "sempre"],
        "satisfaction": ["satisfeito", "ótimo", "perfeito", "obrigado"],
        "anxiety": ["preocupado", "urgente", "preciso", "logo"],
        "confusion": ["não entendi", "confuso", "como assim", "não sei"],
    }

    # Quality metrics weights
    QUALITY_WEIGHTS = {
        "greeting": 0.10,
        "professionalism": 0.20,
        "knowledge": 0.20,
        "empathy": 0.15,
        "resolution": 0.25,
        "closing": 0.10,
    }

    def __init__(self):
        """Initialize call analyzer."""
        self.min_quality_score = 70

    def analyze_call(
        self,
        transcription_text: str,
        segments: Optional[List[Dict]] = None,
        duration_seconds: Optional[float] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a phone call transcription.

        Args:
            transcription_text: Full transcription text
            segments: Transcription segments with speaker labels
            duration_seconds: Call duration
            metadata: Additional call metadata

        Returns:
            Complete call analysis
        """
        start_time = time.time()
        metadata = metadata or {}
        segments = segments or []

        # Classify call type
        call_type, type_confidence = self._classify_call_type(transcription_text)

        # Analyze sentiment
        sentiment_result = self._analyze_sentiment(transcription_text, segments)

        # Detect emotions
        emotions = self._detect_emotions(transcription_text)

        # Extract topics and keywords
        topics = self._extract_topics(transcription_text)
        keywords = self._extract_keywords(transcription_text)

        # Identify issues
        issues = self._identify_issues(transcription_text)

        # Calculate quality metrics
        quality_result = self._calculate_quality(transcription_text, segments)

        # Generate summary
        summary = self._generate_summary(transcription_text, call_type, sentiment_result)

        # Extract action items
        action_items = self._extract_action_items(transcription_text)

        # Predict satisfaction
        csat, nps = self._predict_satisfaction(sentiment_result, quality_result, issues)

        # Check compliance
        compliance_result = self._check_compliance(transcription_text)

        # Generate alerts
        alerts = self._generate_alerts(
            sentiment_result, quality_result, issues, compliance_result
        )

        processing_time_ms = int((time.time() - start_time) * 1000)

        return {
            "status": "completed",
            "call_type": call_type,
            "call_type_confidence": type_confidence,
            "call_categories": self._get_categories(transcription_text),
            "duration_seconds": duration_seconds,
            "overall_sentiment": sentiment_result["overall"],
            "sentiment_score": sentiment_result["score"],
            "agent_sentiment": sentiment_result.get("agent"),
            "customer_sentiment": sentiment_result.get("customer"),
            "sentiment_timeline": sentiment_result.get("timeline", []),
            "emotions_detected": emotions["emotions"],
            "dominant_emotion": emotions["dominant"],
            "emotion_timeline": emotions.get("timeline", []),
            "topics": topics,
            "primary_topic": topics[0] if topics else None,
            "keywords": keywords,
            "issues_identified": issues,
            "complaint_detected": any(i["severity"] == "high" for i in issues),
            "escalation_needed": self._needs_escalation(sentiment_result, issues),
            "escalation_reason": self._get_escalation_reason(sentiment_result, issues),
            "resolution_status": self._determine_resolution(transcription_text),
            "resolution_summary": self._get_resolution_summary(transcription_text),
            "action_items": action_items,
            "follow_up_required": len(action_items) > 0,
            "quality_score": quality_result["overall"],
            "quality_breakdown": quality_result["breakdown"],
            "agent_score": quality_result.get("agent_score"),
            "agent_metrics": quality_result.get("agent_metrics", {}),
            "csat_predicted": csat,
            "nps_predicted": nps,
            "effort_score": self._calculate_effort_score(transcription_text, duration_seconds),
            "compliance_score": compliance_result["score"],
            "compliance_issues": compliance_result["issues"],
            "summary": summary,
            "key_points": self._extract_key_points(transcription_text),
            "recommendations": self._generate_recommendations(quality_result, issues),
            "alerts": alerts,
            "processing_time_ms": processing_time_ms,
        }

    def _classify_call_type(self, text: str) -> Tuple[str, float]:
        """Classify the type of call."""
        text_lower = text.lower()
        scores = {}

        for call_type, patterns in self.CALL_TYPE_PATTERNS.items():
            score = sum(1 for p in patterns if p in text_lower)
            if score > 0:
                scores[call_type] = score

        if not scores:
            return "other", 0.5

        best_type = max(scores, key=scores.get)
        confidence = min(scores[best_type] / 3, 1.0)

        return best_type, round(confidence, 2)

    def _analyze_sentiment(
        self,
        text: str,
        segments: List[Dict],
    ) -> Dict[str, Any]:
        """Analyze sentiment of the call."""
        text_lower = text.lower()

        # Count positive and negative keywords
        positive_count = sum(1 for w in self.POSITIVE_KEYWORDS if w in text_lower)
        negative_count = sum(1 for w in self.NEGATIVE_KEYWORDS if w in text_lower)

        total = positive_count + negative_count
        if total == 0:
            score = 0.0
            overall = "neutral"
        else:
            score = (positive_count - negative_count) / total
            if score > 0.3:
                overall = "positive" if score < 0.7 else "very_positive"
            elif score < -0.3:
                overall = "negative" if score > -0.7 else "very_negative"
            else:
                overall = "neutral"

        return {
            "overall": overall,
            "score": round(score, 2),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "timeline": [],  # Would be populated with segment-level analysis
        }

    def _detect_emotions(self, text: str) -> Dict[str, Any]:
        """Detect emotions in the call."""
        text_lower = text.lower()
        emotions = {}

        for emotion, patterns in self.EMOTION_PATTERNS.items():
            count = sum(1 for p in patterns if p in text_lower)
            if count > 0:
                emotions[emotion] = count

        dominant = max(emotions, key=emotions.get) if emotions else "neutral"

        return {
            "emotions": emotions,
            "dominant": dominant,
            "timeline": [],
        }

    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from the call."""
        text_lower = text.lower()
        topics = []

        topic_keywords = {
            "acesso": ["acesso", "portão", "entrada", "senha"],
            "manutenção": ["manutenção", "conserto", "reparo", "quebrado"],
            "financeiro": ["boleto", "pagamento", "taxa", "cobrança"],
            "segurança": ["câmera", "alarme", "vigilância", "roubo"],
            "reserva": ["reserva", "salão", "churrasqueira", "área comum"],
            "reclamação": ["reclamação", "barulho", "vizinho", "problema"],
        }

        for topic, keywords in topic_keywords.items():
            if any(k in text_lower for k in keywords):
                topics.append(topic)

        return topics[:5]

    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text."""
        words = re.findall(r'\b\w{4,}\b', text.lower())
        stopwords = {"para", "como", "quando", "onde", "porque", "isso", "esse", "esta"}
        word_freq = {}

        for word in words:
            if word not in stopwords:
                word_freq[word] = word_freq.get(word, 0) + 1

        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [w[0] for w in sorted_words[:max_keywords]]

    def _identify_issues(self, text: str) -> List[Dict]:
        """Identify issues mentioned in the call."""
        issues = []
        text_lower = text.lower()

        issue_patterns = {
            "high": [
                ("não funciona", "Equipamento não funcionando"),
                ("não consigo acessar", "Problema de acesso"),
                ("emergência", "Situação de emergência"),
            ],
            "medium": [
                ("demora", "Atraso no atendimento"),
                ("erro", "Erro no sistema"),
                ("problema", "Problema reportado"),
            ],
            "low": [
                ("dúvida", "Dúvida do cliente"),
                ("informação", "Solicitação de informação"),
            ],
        }

        for severity, patterns in issue_patterns.items():
            for pattern, description in patterns:
                if pattern in text_lower:
                    issues.append({
                        "issue": description,
                        "severity": severity,
                        "resolved": "resolvido" in text_lower or "solucionado" in text_lower,
                    })

        return issues

    def _calculate_quality(
        self,
        text: str,
        segments: List[Dict],
    ) -> Dict[str, Any]:
        """Calculate call quality metrics."""
        text_lower = text.lower()

        # Simulate quality scoring
        breakdown = {}

        # Greeting check
        greeting_patterns = ["bom dia", "boa tarde", "boa noite", "olá", "alô"]
        breakdown["greeting"] = 80 if any(p in text_lower for p in greeting_patterns) else 40

        # Professionalism
        breakdown["professionalism"] = 75  # Default score

        # Knowledge (check if answers were provided)
        knowledge_indicators = ["a resposta é", "você pode", "isso acontece porque"]
        breakdown["knowledge"] = 80 if any(p in text_lower for p in knowledge_indicators) else 60

        # Empathy
        empathy_patterns = ["entendo", "compreendo", "lamento", "desculpe"]
        breakdown["empathy"] = 85 if any(p in text_lower for p in empathy_patterns) else 50

        # Resolution
        resolution_patterns = ["resolvido", "solucionado", "pronto", "concluído"]
        breakdown["resolution"] = 90 if any(p in text_lower for p in resolution_patterns) else 50

        # Closing
        closing_patterns = ["mais alguma coisa", "posso ajudar", "obrigado pela ligação"]
        breakdown["closing"] = 80 if any(p in text_lower for p in closing_patterns) else 40

        # Calculate weighted overall score
        overall = sum(
            breakdown[metric] * weight
            for metric, weight in self.QUALITY_WEIGHTS.items()
        )

        return {
            "overall": round(overall, 1),
            "breakdown": breakdown,
            "agent_score": overall,
            "agent_metrics": breakdown,
        }

    def _predict_satisfaction(
        self,
        sentiment: Dict,
        quality: Dict,
        issues: List[Dict],
    ) -> Tuple[float, float]:
        """Predict CSAT and NPS scores."""
        base_score = 3.0  # Neutral CSAT

        # Adjust based on sentiment
        sentiment_score = sentiment.get("score", 0)
        base_score += sentiment_score * 1.5

        # Adjust based on quality
        quality_score = quality.get("overall", 70)
        base_score += (quality_score - 70) / 50

        # Adjust based on issues
        unresolved = sum(1 for i in issues if not i.get("resolved", False))
        base_score -= unresolved * 0.3

        # Clamp CSAT to 1-5
        csat = max(1, min(5, base_score))

        # Convert to NPS (-100 to 100)
        nps = (csat - 3) * 50

        return round(csat, 1), round(nps, 0)

    def _check_compliance(self, text: str) -> Dict[str, Any]:
        """Check call compliance."""
        text_lower = text.lower()
        issues = []
        score = 100

        # Check required disclosures
        required_phrases = {
            "identificação": ["meu nome é", "aqui é", "sou o", "sou a"],
            "empresa": ["conecta", "empresa", "atendimento"],
        }

        for disclosure, phrases in required_phrases.items():
            if not any(p in text_lower for p in phrases):
                issues.append({
                    "type": "missing_disclosure",
                    "disclosure": disclosure,
                    "severity": "medium",
                })
                score -= 10

        return {
            "score": max(0, score),
            "issues": issues,
        }

    def _generate_alerts(
        self,
        sentiment: Dict,
        quality: Dict,
        issues: List[Dict],
        compliance: Dict,
    ) -> List[Dict]:
        """Generate alerts based on analysis."""
        alerts = []

        # Sentiment alerts
        if sentiment.get("score", 0) < -0.5:
            alerts.append({
                "type": "negative_sentiment",
                "severity": "high",
                "message": "Cliente muito insatisfeito detectado",
            })

        # Quality alerts
        if quality.get("overall", 0) < 60:
            alerts.append({
                "type": "low_quality",
                "severity": "medium",
                "message": "Pontuação de qualidade abaixo do esperado",
            })

        # Issue alerts
        high_severity = [i for i in issues if i.get("severity") == "high"]
        if high_severity:
            alerts.append({
                "type": "critical_issue",
                "severity": "high",
                "message": f"{len(high_severity)} problema(s) crítico(s) identificado(s)",
            })

        # Compliance alerts
        if compliance.get("score", 100) < 80:
            alerts.append({
                "type": "compliance_issue",
                "severity": "medium",
                "message": "Problemas de conformidade detectados",
            })

        return alerts

    def _needs_escalation(self, sentiment: Dict, issues: List[Dict]) -> bool:
        """Check if call needs escalation."""
        if sentiment.get("score", 0) < -0.6:
            return True
        if any(i.get("severity") == "high" and not i.get("resolved") for i in issues):
            return True
        return False

    def _get_escalation_reason(self, sentiment: Dict, issues: List[Dict]) -> Optional[str]:
        """Get reason for escalation."""
        reasons = []
        if sentiment.get("score", 0) < -0.6:
            reasons.append("Cliente muito insatisfeito")
        for issue in issues:
            if issue.get("severity") == "high" and not issue.get("resolved"):
                reasons.append(f"Problema crítico: {issue.get('issue')}")
        return "; ".join(reasons) if reasons else None

    def _determine_resolution(self, text: str) -> str:
        """Determine resolution status."""
        text_lower = text.lower()
        if any(p in text_lower for p in ["resolvido", "solucionado", "pronto"]):
            return "resolved"
        if any(p in text_lower for p in ["vou verificar", "retorno", "entraremos em contato"]):
            return "pending"
        return "unresolved"

    def _get_resolution_summary(self, text: str) -> Optional[str]:
        """Get resolution summary."""
        status = self._determine_resolution(text)
        summaries = {
            "resolved": "Problema resolvido durante a ligação",
            "pending": "Aguardando retorno/verificação",
            "unresolved": "Problema não resolvido",
        }
        return summaries.get(status)

    def _extract_action_items(self, text: str) -> List[Dict]:
        """Extract action items from call."""
        action_items = []
        text_lower = text.lower()

        patterns = [
            (r"vou (?:verificar|checar|analisar)", "Verificar situação"),
            (r"(?:ligar|retornar|entrar em contato)", "Retornar para cliente"),
            (r"(?:enviar|mandar) (?:técnico|equipe)", "Enviar técnico"),
            (r"(?:abrir|criar) (?:chamado|ocorrência)", "Abrir chamado"),
        ]

        for pattern, action in patterns:
            if re.search(pattern, text_lower):
                action_items.append({
                    "action": action,
                    "status": "pending",
                })

        return action_items

    def _generate_summary(self, text: str, call_type: str, sentiment: Dict) -> str:
        """Generate call summary."""
        sentiment_text = {
            "very_positive": "muito satisfeito",
            "positive": "satisfeito",
            "neutral": "neutro",
            "negative": "insatisfeito",
            "very_negative": "muito insatisfeito",
        }.get(sentiment.get("overall", "neutral"), "neutro")

        return f"Ligação de {call_type}. Cliente {sentiment_text}."

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from call."""
        # Simplified extraction
        sentences = text.split(".")
        return [s.strip() for s in sentences[:3] if s.strip()]

    def _generate_recommendations(
        self,
        quality: Dict,
        issues: List[Dict],
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        breakdown = quality.get("breakdown", {})

        if breakdown.get("greeting", 100) < 60:
            recommendations.append("Melhorar saudação inicial")
        if breakdown.get("empathy", 100) < 60:
            recommendations.append("Demonstrar mais empatia com o cliente")
        if breakdown.get("resolution", 100) < 60:
            recommendations.append("Focar na resolução efetiva do problema")

        unresolved = sum(1 for i in issues if not i.get("resolved", False))
        if unresolved > 0:
            recommendations.append(f"Resolver {unresolved} problema(s) pendente(s)")

        return recommendations

    def _calculate_effort_score(
        self,
        text: str,
        duration: Optional[float],
    ) -> float:
        """Calculate customer effort score."""
        base_score = 3.0  # Neutral

        # Long calls indicate more effort
        if duration and duration > 600:  # > 10 min
            base_score += 1.0
        elif duration and duration > 300:  # > 5 min
            base_score += 0.5

        # Multiple mentions of problem indicate effort
        text_lower = text.lower()
        problem_count = text_lower.count("problema") + text_lower.count("não funciona")
        base_score += problem_count * 0.2

        return min(5.0, round(base_score, 1))

    def _get_categories(self, text: str) -> List[str]:
        """Get call categories."""
        categories = []
        text_lower = text.lower()

        category_keywords = {
            "técnico": ["técnico", "manutenção", "reparo"],
            "financeiro": ["pagamento", "boleto", "taxa"],
            "atendimento": ["informação", "dúvida", "ajuda"],
            "reclamação": ["reclamação", "insatisfeito"],
        }

        for category, keywords in category_keywords.items():
            if any(k in text_lower for k in keywords):
                categories.append(category)

        return categories
