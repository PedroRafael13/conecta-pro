"""
Service de Avaliacao de Impacto de Privacidade (PIA/DPIA) LGPD.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PIAService:
    """Service para gerenciamento de avaliacoes de impacto.

    Encapsula a logica de avaliacao de impacto de privacidade
    conforme Art. 38 da LGPD (RIPD).
    """

    # Armazenamento em memoria (em producao, usar banco de dados)
    _assessments: Dict[str, Dict[str, Any]] = {}

    # Categorias de dados sensiveis (Art. 5, II LGPD)
    SENSITIVE_CATEGORIES = [
        "racial_ethnic",
        "political_opinion",
        "religious_belief",
        "health_data",
        "sexual_data",
        "genetic_data",
        "biometric_data",
    ]

    def __init__(self):
        """Inicializa o service."""
        pass

    def _calculate_risk_level(
        self,
        data_categories: List[str],
        processing_purposes: List[str],
        data_subjects: List[str],
        risk_factors: List[str],
    ) -> str:
        """Calcula nivel de risco baseado nos fatores.

        Returns:
            Nivel de risco: low, medium, high, critical
        """
        score = 0

        # Dados sensiveis aumentam risco
        for cat in data_categories:
            if cat in self.SENSITIVE_CATEGORIES:
                score += 3

        # Grande volume de titulares
        if "mass" in data_subjects or "public" in data_subjects:
            score += 2

        # Fatores de risco identificados
        score += len(risk_factors)

        # Finalidades de alto risco
        high_risk_purposes = ["profiling", "automated_decision", "surveillance"]
        for purpose in processing_purposes:
            if purpose in high_risk_purposes:
                score += 3

        if score >= 10:
            return "critical"
        elif score >= 6:
            return "high"
        elif score >= 3:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(
        self,
        risk_level: str,
        data_categories: List[str],
    ) -> List[str]:
        """Gera recomendacoes baseadas na avaliacao."""
        recommendations = []

        if risk_level in ("high", "critical"):
            recommendations.append("Realizar DPIA completo conforme Art. 38 LGPD")
            recommendations.append("Consultar Encarregado de Dados (DPO)")
            recommendations.append("Considerar consulta previa a ANPD")

        if any(cat in self.SENSITIVE_CATEGORIES for cat in data_categories):
            recommendations.append("Implementar medidas de seguranca reforçadas para dados sensiveis")
            recommendations.append("Obter consentimento especifico conforme Art. 11 LGPD")

        if risk_level in ("medium", "high", "critical"):
            recommendations.append("Documentar medidas de mitigacao implementadas")
            recommendations.append("Realizar revisao periodica da avaliacao")

        if not recommendations:
            recommendations.append("Manter documentacao do tratamento de dados")

        return recommendations

    def create_assessment(
        self,
        project_name: str,
        description: str,
        data_categories: List[str],
        processing_purposes: List[str],
        data_subjects: Optional[List[str]] = None,
        risk_factors: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Cria avaliacao de impacto de privacidade.

        Args:
            project_name: Nome do projeto.
            description: Descricao do tratamento.
            data_categories: Categorias de dados tratados.
            processing_purposes: Finalidades do tratamento.
            data_subjects: Titulares afetados.
            risk_factors: Fatores de risco identificados.

        Returns:
            Dict com resultado da avaliacao.
        """
        data_subjects = data_subjects or ["funcionarios"]
        risk_factors = risk_factors or []

        assessment_id = str(uuid.uuid4())
        now = datetime.utcnow()

        risk_level = self._calculate_risk_level(
            data_categories,
            processing_purposes,
            data_subjects,
            risk_factors,
        )

        recommendations = self._generate_recommendations(risk_level, data_categories)

        assessment_data = {
            "assessment_id": assessment_id,
            "project_name": project_name,
            "description": description,
            "data_categories": data_categories,
            "processing_purposes": processing_purposes,
            "data_subjects": data_subjects,
            "risk_factors": risk_factors,
            "risk_level": risk_level,
            "requires_dpia": risk_level in ("high", "critical"),
            "recommendations": recommendations,
            "status": "completed",
            "created_at": now.isoformat(),
            "created_by": None,
        }

        self._assessments[assessment_id] = assessment_data

        logger.info(
            "PIA criado: projeto=%s, nivel de risco=%s",
            project_name,
            risk_level,
        )

        return {
            "assessment_id": assessment_id,
            "project_name": project_name,
            "risk_level": risk_level,
            "requires_dpia": risk_level in ("high", "critical"),
            "recommendations": recommendations,
        }

    def get_assessment(self, assessment_id: str) -> Dict[str, Any]:
        """Consulta avaliacao de impacto.

        Args:
            assessment_id: ID da avaliacao.

        Returns:
            Dict com detalhes da avaliacao.

        Raises:
            ValueError: Se avaliacao nao encontrada.
        """
        if assessment_id not in self._assessments:
            raise ValueError(f"Avaliacao nao encontrada: {assessment_id}")

        return self._assessments[assessment_id]

    def list_assessments(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Lista avaliacoes de impacto.

        Args:
            status: Filtro por status.
            limit: Limite de resultados.
            offset: Offset para paginacao.

        Returns:
            Dict com lista de avaliacoes.
        """
        assessments = list(self._assessments.values())

        if status:
            assessments = [a for a in assessments if a["status"] == status]

        total = len(assessments)
        paginated = assessments[offset:offset + limit]

        return {
            "assessments": paginated,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def get_risk_categories(self) -> List[Dict[str, str]]:
        """Lista categorias de risco disponiveis.

        Returns:
            Lista de categorias de risco.
        """
        return [
            {"id": "low", "description": "Baixo risco", "color": "green"},
            {"id": "medium", "description": "Risco medio", "color": "yellow"},
            {"id": "high", "description": "Alto risco", "color": "orange"},
            {"id": "critical", "description": "Risco critico", "color": "red"},
        ]

    def get_data_categories(self) -> List[Dict[str, str]]:
        """Lista categorias de dados LGPD.

        Returns:
            Lista de categorias de dados.
        """
        return [
            {"id": "personal", "description": "Dados pessoais", "sensitive": False},
            {"id": "financial", "description": "Dados financeiros", "sensitive": False},
            {"id": "health_data", "description": "Dados de saude", "sensitive": True},
            {"id": "biometric_data", "description": "Dados biometricos", "sensitive": True},
            {"id": "genetic_data", "description": "Dados geneticos", "sensitive": True},
            {"id": "racial_ethnic", "description": "Origem racial/etnica", "sensitive": True},
            {"id": "political_opinion", "description": "Opiniao politica", "sensitive": True},
            {"id": "religious_belief", "description": "Crenca religiosa", "sensitive": True},
            {"id": "sexual_data", "description": "Vida sexual", "sensitive": True},
        ]
