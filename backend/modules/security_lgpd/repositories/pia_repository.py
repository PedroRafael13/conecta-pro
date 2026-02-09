"""
Repository de Avaliacao de Impacto de Privacidade (PIA) LGPD.
"""

import builtins
import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from modules.security_lgpd.models.pia_assessment import (
    AssessmentStatus,
    PIAAssessment,
    RiskLevel,
)

logger = logging.getLogger(__name__)


class PIARepository:
    """Repository para operacoes de persistencia de avaliacoes PIA.

    Encapsula o acesso ao banco de dados para a entidade PIAAssessment.
    """

    def __init__(self, db: Session):
        """Inicializa o repository.

        Args:
            db: Sessao do banco de dados.
        """
        self.db = db

    def create(self, assessment: PIAAssessment) -> PIAAssessment:
        """Cria uma nova avaliacao PIA.

        Args:
            assessment: Instancia da avaliacao.

        Returns:
            Avaliacao criada.
        """
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        logger.info("Avaliacao PIA criada: %s", assessment.id)
        return assessment

    def get_by_id(self, assessment_id: UUID) -> PIAAssessment | None:
        """Busca avaliacao por ID.

        Args:
            assessment_id: UUID da avaliacao.

        Returns:
            Avaliacao ou None.
        """
        return self.db.query(PIAAssessment).filter(PIAAssessment.id == assessment_id).first()

    def get_by_project_name(self, project_name: str) -> PIAAssessment | None:
        """Busca avaliacao por nome do projeto.

        Args:
            project_name: Nome do projeto.

        Returns:
            Avaliacao ou None.
        """
        return self.db.query(PIAAssessment).filter(PIAAssessment.project_name == project_name).first()

    def update(self, assessment: PIAAssessment) -> PIAAssessment:
        """Atualiza uma avaliacao.

        Args:
            assessment: Instancia da avaliacao.

        Returns:
            Avaliacao atualizada.
        """
        assessment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def list(
        self,
        status: AssessmentStatus | None = None,
        risk_level: RiskLevel | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PIAAssessment]:
        """Lista avaliacoes com filtros.

        Args:
            status: Filtro por status.
            risk_level: Filtro por nivel de risco.
            limit: Limite de resultados.
            offset: Offset para paginacao.

        Returns:
            Lista de avaliacoes.
        """
        query = self.db.query(PIAAssessment)

        if status:
            query = query.filter(PIAAssessment.status == status)
        if risk_level:
            query = query.filter(PIAAssessment.risk_level == risk_level)

        return query.order_by(PIAAssessment.created_at.desc()).offset(offset).limit(limit).all()

    def list_requiring_dpia(self) -> builtins.list[PIAAssessment]:
        """Lista avaliacoes que requerem DPIA completo.

        Returns:
            Lista de avaliacoes.
        """
        return (
            self.db.query(PIAAssessment)
            .filter(PIAAssessment.requires_dpia)
            .filter(PIAAssessment.status != AssessmentStatus.ARCHIVED)
            .order_by(PIAAssessment.created_at.desc())
            .all()
        )

    def list_high_risk(self) -> builtins.list[PIAAssessment]:
        """Lista avaliacoes de alto risco.

        Returns:
            Lista de avaliacoes.
        """
        return (
            self.db.query(PIAAssessment)
            .filter(PIAAssessment.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]))
            .filter(PIAAssessment.status != AssessmentStatus.ARCHIVED)
            .order_by(PIAAssessment.created_at.desc())
            .all()
        )

    def approve(
        self,
        assessment_id: UUID,
        approved_by: str,
    ) -> PIAAssessment | None:
        """Aprova uma avaliacao.

        Args:
            assessment_id: UUID da avaliacao.
            approved_by: ID do aprovador.

        Returns:
            Avaliacao aprovada ou None.
        """
        assessment = self.get_by_id(assessment_id)
        if assessment:
            assessment.status = AssessmentStatus.APPROVED
            assessment.approved_by = approved_by
            assessment.approved_at = datetime.utcnow()
            return self.update(assessment)
        return None

    def count_by_status(self) -> dict:
        """Conta avaliacoes por status.

        Returns:
            Dict com contagens por status.
        """
        from sqlalchemy import func

        result = self.db.query(PIAAssessment.status, func.count(PIAAssessment.id)).group_by(PIAAssessment.status).all()
        return {status.value: count for status, count in result}

    def count_by_risk_level(self) -> dict:
        """Conta avaliacoes por nivel de risco.

        Returns:
            Dict com contagens por nivel de risco.
        """
        from sqlalchemy import func

        result = (
            self.db.query(PIAAssessment.risk_level, func.count(PIAAssessment.id))
            .filter(PIAAssessment.risk_level.isnot(None))
            .group_by(PIAAssessment.risk_level)
            .all()
        )
        return {level.value: count for level, count in result}
