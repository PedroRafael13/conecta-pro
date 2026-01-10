"""
Module: PrivacyImpact
Description: Sistema de Avaliacao de Impacto a Protecao de Dados (DPIA/RIPD)
             conforme LGPD Art. 38 e GDPR Art. 35.
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: LGPD Art. 38 - Relatorio de Impacto a Protecao de Dados
"""

from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime, date
from uuid import UUID, uuid4
import json
import logging

from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Float
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()


class RiskLevel(str, Enum):
    """Niveis de risco para avaliacao de impacto."""
    NEGLIGIBLE = "negligible"    # Insignificante
    LOW = "low"                  # Baixo
    MEDIUM = "medium"            # Medio
    HIGH = "high"                # Alto
    CRITICAL = "critical"        # Critico


class RiskCategory(str, Enum):
    """Categorias de risco avaliadas."""
    DATA_BREACH = "data_breach"              # Vazamento de dados
    UNAUTHORIZED_ACCESS = "unauthorized_access"  # Acesso nao autorizado
    DATA_LOSS = "data_loss"                  # Perda de dados
    CONSENT_VIOLATION = "consent_violation"  # Violacao de consentimento
    RIGHTS_VIOLATION = "rights_violation"    # Violacao de direitos do titular
    CROSS_BORDER = "cross_border"            # Transferencia internacional
    PROFILING = "profiling"                  # Decisoes automatizadas/profiling
    SENSITIVE_DATA = "sensitive_data"        # Dados sensiveis
    LARGE_SCALE = "large_scale"              # Processamento em larga escala
    VULNERABLE_SUBJECTS = "vulnerable_subjects"  # Titulares vulneraveis


class ProcessingType(str, Enum):
    """Tipos de tratamento de dados."""
    COLLECTION = "collection"
    STORAGE = "storage"
    USE = "use"
    SHARING = "sharing"
    TRANSFER = "transfer"
    DELETION = "deletion"
    AUTOMATED_DECISION = "automated_decision"
    PROFILING = "profiling"


class AssessmentStatus(str, Enum):
    """Status de uma avaliacao de impacto."""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CONSULTATION = "requires_consultation"
    ARCHIVED = "archived"


class PIAError(Exception):
    """Erro em operacao de avaliacao de impacto."""

    def __init__(self, message: str, assessment_id: Optional[str] = None):
        self.message = message
        self.assessment_id = assessment_id
        super().__init__(self.message)


@dataclass
class DataProcessingActivity:
    """Atividade de tratamento de dados avaliada."""
    id: UUID
    name: str
    description: str
    processing_types: List[ProcessingType]
    data_categories: List[str]          # Categorias de dados tratados
    data_subjects: List[str]            # Categorias de titulares
    purposes: List[str]                 # Finalidades do tratamento
    legal_basis: str                    # Base legal
    retention_period: Optional[str] = None
    recipients: List[str] = field(default_factory=list)
    international_transfers: bool = False
    automated_decisions: bool = False
    third_party_processors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "processing_types": [p.value for p in self.processing_types],
            "data_categories": self.data_categories,
            "data_subjects": self.data_subjects,
            "purposes": self.purposes,
            "legal_basis": self.legal_basis,
            "retention_period": self.retention_period,
            "recipients": self.recipients,
            "international_transfers": self.international_transfers,
            "automated_decisions": self.automated_decisions,
            "third_party_processors": self.third_party_processors,
        }


@dataclass
class RiskAssessment:
    """Avaliacao de um risco especifico."""
    category: RiskCategory
    inherent_likelihood: int        # 1-5: probabilidade sem controles
    inherent_impact: int            # 1-5: impacto sem controles
    controls: List[str]             # Controles mitigadores
    residual_likelihood: int        # 1-5: probabilidade com controles
    residual_impact: int            # 1-5: impacto com controles
    notes: Optional[str] = None

    @property
    def inherent_risk_score(self) -> float:
        """Calcula score de risco inerente (0-25)."""
        return self.inherent_likelihood * self.inherent_impact

    @property
    def residual_risk_score(self) -> float:
        """Calcula score de risco residual (0-25)."""
        return self.residual_likelihood * self.residual_impact

    @property
    def inherent_risk_level(self) -> RiskLevel:
        """Determina nivel de risco inerente."""
        return self._score_to_level(self.inherent_risk_score)

    @property
    def residual_risk_level(self) -> RiskLevel:
        """Determina nivel de risco residual."""
        return self._score_to_level(self.residual_risk_score)

    @staticmethod
    def _score_to_level(score: float) -> RiskLevel:
        """Converte score para nivel de risco."""
        if score <= 2:
            return RiskLevel.NEGLIGIBLE
        elif score <= 6:
            return RiskLevel.LOW
        elif score <= 12:
            return RiskLevel.MEDIUM
        elif score <= 20:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "inherent_likelihood": self.inherent_likelihood,
            "inherent_impact": self.inherent_impact,
            "inherent_risk_score": self.inherent_risk_score,
            "inherent_risk_level": self.inherent_risk_level.value,
            "controls": self.controls,
            "residual_likelihood": self.residual_likelihood,
            "residual_impact": self.residual_impact,
            "residual_risk_score": self.residual_risk_score,
            "residual_risk_level": self.residual_risk_level.value,
            "notes": self.notes,
        }


@dataclass
class MitigationMeasure:
    """Medida de mitigacao de risco."""
    id: UUID
    description: str
    risk_categories: List[RiskCategory]
    priority: int                       # 1-5
    status: str                         # planned, in_progress, implemented
    responsible: Optional[str] = None
    deadline: Optional[date] = None
    implementation_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "description": self.description,
            "risk_categories": [r.value for r in self.risk_categories],
            "priority": self.priority,
            "status": self.status,
            "responsible": self.responsible,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "implementation_notes": self.implementation_notes,
        }


@dataclass
class PrivacyImpactAssessment:
    """Avaliacao de Impacto a Protecao de Dados (DPIA/RIPD)."""
    id: UUID
    title: str
    description: str
    status: AssessmentStatus
    created_at: datetime
    created_by: str
    processing_activities: List[DataProcessingActivity] = field(default_factory=list)
    risk_assessments: List[RiskAssessment] = field(default_factory=list)
    mitigation_measures: List[MitigationMeasure] = field(default_factory=list)
    dpo_opinion: Optional[str] = None
    dpo_approved: Optional[bool] = None
    dpo_approved_at: Optional[datetime] = None
    requires_authority_consultation: bool = False
    authority_consultation_notes: Optional[str] = None
    last_reviewed: Optional[datetime] = None
    next_review_date: Optional[date] = None
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def overall_risk_level(self) -> RiskLevel:
        """Determina nivel de risco geral da avaliacao."""
        if not self.risk_assessments:
            return RiskLevel.NEGLIGIBLE

        max_residual = max(r.residual_risk_score for r in self.risk_assessments)
        return RiskAssessment._score_to_level(max_residual)

    @property
    def high_risk_count(self) -> int:
        """Conta riscos altos ou criticos."""
        return sum(
            1 for r in self.risk_assessments
            if r.residual_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "processing_activities": [a.to_dict() for a in self.processing_activities],
            "risk_assessments": [r.to_dict() for r in self.risk_assessments],
            "mitigation_measures": [m.to_dict() for m in self.mitigation_measures],
            "overall_risk_level": self.overall_risk_level.value,
            "high_risk_count": self.high_risk_count,
            "dpo_opinion": self.dpo_opinion,
            "dpo_approved": self.dpo_approved,
            "dpo_approved_at": self.dpo_approved_at.isoformat() if self.dpo_approved_at else None,
            "requires_authority_consultation": self.requires_authority_consultation,
            "authority_consultation_notes": self.authority_consultation_notes,
            "last_reviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "next_review_date": self.next_review_date.isoformat() if self.next_review_date else None,
            "version": self.version,
            "metadata": self.metadata,
        }


# SQLAlchemy Model
class PIAModel(Base):
    """Modelo de banco para avaliacoes de impacto."""
    __tablename__ = "lgpd_privacy_impact_assessments"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="draft")
    created_by = Column(String(100), nullable=False)
    processing_activities = Column(JSONB, default=[])
    risk_assessments = Column(JSONB, default=[])
    mitigation_measures = Column(JSONB, default=[])
    overall_risk_level = Column(String(20), nullable=True)
    dpo_opinion = Column(Text, nullable=True)
    dpo_approved = Column(Boolean, nullable=True)
    dpo_approved_at = Column(DateTime, nullable=True)
    requires_authority_consultation = Column(Boolean, default=False)
    authority_consultation_notes = Column(Text, nullable=True)
    last_reviewed = Column(DateTime, nullable=True)
    next_review_date = Column(DateTime, nullable=True)
    version = Column(Integer, default=1)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PIATemplate:
    """Template para criacao de avaliacoes de impacto."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.required_risk_categories: List[RiskCategory] = []
        self.default_controls: Dict[RiskCategory, List[str]] = {}
        self.questions: List[Dict[str, Any]] = []

    def add_risk_category(
        self,
        category: RiskCategory,
        default_controls: Optional[List[str]] = None
    ) -> None:
        """Adiciona categoria de risco ao template."""
        self.required_risk_categories.append(category)
        if default_controls:
            self.default_controls[category] = default_controls

    def add_question(
        self,
        question: str,
        category: str,
        help_text: Optional[str] = None
    ) -> None:
        """Adiciona pergunta ao questionario."""
        self.questions.append({
            "question": question,
            "category": category,
            "help_text": help_text,
        })


class PIAManager:
    """
    Gerenciador de Avaliacoes de Impacto a Protecao de Dados.

    Coordena criacao, avaliacao e aprovacao de DPIAs/RIPDs
    conforme LGPD e GDPR.

    Example:
        >>> manager = PIAManager()
        >>> assessment = await manager.create_assessment(
        ...     title="Sistema de RH",
        ...     description="Avaliacao do processamento de dados de funcionarios",
        ...     created_by="dpo@company.com"
        ... )
    """

    def __init__(self):
        self._assessments: Dict[UUID, PrivacyImpactAssessment] = {}
        self._templates: Dict[str, PIATemplate] = {}
        self._init_default_templates()
        logger.info("PIAManager inicializado")

    def _init_default_templates(self) -> None:
        """Inicializa templates padrao."""
        # Template para processamento de dados de funcionarios
        hr_template = PIATemplate(
            name="hr_processing",
            description="Template para processamento de dados de funcionarios"
        )
        hr_template.add_risk_category(
            RiskCategory.SENSITIVE_DATA,
            ["Criptografia de dados sensiveis", "Controle de acesso baseado em funcao"]
        )
        hr_template.add_risk_category(
            RiskCategory.UNAUTHORIZED_ACCESS,
            ["Autenticacao multifator", "Logs de acesso", "Revisao periodica de permissoes"]
        )
        hr_template.add_risk_category(
            RiskCategory.DATA_BREACH,
            ["Criptografia em repouso", "Backup seguro", "Plano de resposta a incidentes"]
        )
        self._templates["hr_processing"] = hr_template

        # Template para marketing
        marketing_template = PIATemplate(
            name="marketing_processing",
            description="Template para processamento de dados para marketing"
        )
        marketing_template.add_risk_category(
            RiskCategory.CONSENT_VIOLATION,
            ["Gestao de consentimentos", "Opt-out facil", "Registro de preferencias"]
        )
        marketing_template.add_risk_category(
            RiskCategory.PROFILING,
            ["Transparencia no profiling", "Direito de objecao", "Revisao humana"]
        )
        self._templates["marketing_processing"] = marketing_template

        # Template para integracao com terceiros
        integration_template = PIATemplate(
            name="third_party_integration",
            description="Template para compartilhamento de dados com terceiros"
        )
        integration_template.add_risk_category(
            RiskCategory.CROSS_BORDER,
            ["Clausulas contratuais padrao", "Avaliacao de adequacao do pais"]
        )
        integration_template.add_risk_category(
            RiskCategory.DATA_LOSS,
            ["SLA com terceiros", "Auditoria de processadores"]
        )
        self._templates["third_party_integration"] = integration_template

    async def create_assessment(
        self,
        title: str,
        description: str,
        created_by: str,
        template_name: Optional[str] = None
    ) -> PrivacyImpactAssessment:
        """
        Cria nova avaliacao de impacto.

        Args:
            title: Titulo da avaliacao.
            description: Descricao do processamento.
            created_by: ID do criador.
            template_name: Nome do template a usar.

        Returns:
            PrivacyImpactAssessment: Avaliacao criada.
        """
        assessment = PrivacyImpactAssessment(
            id=uuid4(),
            title=title,
            description=description,
            status=AssessmentStatus.DRAFT,
            created_at=datetime.utcnow(),
            created_by=created_by,
        )

        # Aplica template se especificado
        if template_name and template_name in self._templates:
            template = self._templates[template_name]
            for category in template.required_risk_categories:
                assessment.risk_assessments.append(
                    RiskAssessment(
                        category=category,
                        inherent_likelihood=3,
                        inherent_impact=3,
                        controls=template.default_controls.get(category, []),
                        residual_likelihood=2,
                        residual_impact=2,
                    )
                )

        self._assessments[assessment.id] = assessment

        logger.info(
            "Avaliacao criada: id=%s, title=%s, by=%s",
            assessment.id, title, created_by
        )

        return assessment

    async def add_processing_activity(
        self,
        assessment_id: UUID,
        activity: DataProcessingActivity
    ) -> PrivacyImpactAssessment:
        """
        Adiciona atividade de processamento a avaliacao.

        Args:
            assessment_id: ID da avaliacao.
            activity: Atividade de processamento.

        Returns:
            PrivacyImpactAssessment: Avaliacao atualizada.
        """
        assessment = self._assessments.get(assessment_id)
        if not assessment:
            raise PIAError("Avaliacao nao encontrada", str(assessment_id))

        assessment.processing_activities.append(activity)

        # Auto-detecta riscos baseado na atividade
        await self._auto_detect_risks(assessment, activity)

        logger.info(
            "Atividade adicionada: assessment=%s, activity=%s",
            assessment_id, activity.name
        )

        return assessment

    async def _auto_detect_risks(
        self,
        assessment: PrivacyImpactAssessment,
        activity: DataProcessingActivity
    ) -> None:
        """Detecta riscos automaticamente baseado na atividade."""
        existing_categories = {r.category for r in assessment.risk_assessments}

        # Verifica transferencia internacional
        if activity.international_transfers and RiskCategory.CROSS_BORDER not in existing_categories:
            assessment.risk_assessments.append(
                RiskAssessment(
                    category=RiskCategory.CROSS_BORDER,
                    inherent_likelihood=4,
                    inherent_impact=4,
                    controls=["Clausulas contratuais padrao"],
                    residual_likelihood=2,
                    residual_impact=3,
                )
            )

        # Verifica decisoes automatizadas
        if activity.automated_decisions and RiskCategory.PROFILING not in existing_categories:
            assessment.risk_assessments.append(
                RiskAssessment(
                    category=RiskCategory.PROFILING,
                    inherent_likelihood=4,
                    inherent_impact=4,
                    controls=["Revisao humana", "Transparencia algoritmica"],
                    residual_likelihood=2,
                    residual_impact=2,
                )
            )

        # Verifica dados sensiveis
        sensitive_categories = {"health", "biometric", "genetic", "political", "religious"}
        if any(cat in activity.data_categories for cat in sensitive_categories):
            if RiskCategory.SENSITIVE_DATA not in existing_categories:
                assessment.risk_assessments.append(
                    RiskAssessment(
                        category=RiskCategory.SENSITIVE_DATA,
                        inherent_likelihood=4,
                        inherent_impact=5,
                        controls=["Criptografia forte", "Controle de acesso restrito"],
                        residual_likelihood=2,
                        residual_impact=3,
                    )
                )

    async def add_risk_assessment(
        self,
        assessment_id: UUID,
        risk: RiskAssessment
    ) -> PrivacyImpactAssessment:
        """
        Adiciona avaliacao de risco.

        Args:
            assessment_id: ID da avaliacao.
            risk: Avaliacao de risco.

        Returns:
            PrivacyImpactAssessment: Avaliacao atualizada.
        """
        assessment = self._assessments.get(assessment_id)
        if not assessment:
            raise PIAError("Avaliacao nao encontrada", str(assessment_id))

        assessment.risk_assessments.append(risk)
        return assessment

    async def add_mitigation_measure(
        self,
        assessment_id: UUID,
        measure: MitigationMeasure
    ) -> PrivacyImpactAssessment:
        """
        Adiciona medida de mitigacao.

        Args:
            assessment_id: ID da avaliacao.
            measure: Medida de mitigacao.

        Returns:
            PrivacyImpactAssessment: Avaliacao atualizada.
        """
        assessment = self._assessments.get(assessment_id)
        if not assessment:
            raise PIAError("Avaliacao nao encontrada", str(assessment_id))

        assessment.mitigation_measures.append(measure)
        return assessment

    async def submit_for_review(self, assessment_id: UUID) -> PrivacyImpactAssessment:
        """
        Submete avaliacao para revisao do DPO.

        Args:
            assessment_id: ID da avaliacao.

        Returns:
            PrivacyImpactAssessment: Avaliacao atualizada.
        """
        assessment = self._assessments.get(assessment_id)
        if not assessment:
            raise PIAError("Avaliacao nao encontrada", str(assessment_id))

        if assessment.status != AssessmentStatus.DRAFT:
            raise PIAError("Avaliacao nao esta em rascunho", str(assessment_id))

        # Verifica completude
        if not assessment.processing_activities:
            raise PIAError("Avaliacao deve ter ao menos uma atividade de processamento", str(assessment_id))

        if not assessment.risk_assessments:
            raise PIAError("Avaliacao deve ter ao menos uma avaliacao de risco", str(assessment_id))

        assessment.status = AssessmentStatus.IN_REVIEW

        # Verifica se requer consulta a autoridade
        if assessment.high_risk_count > 0 or assessment.overall_risk_level == RiskLevel.CRITICAL:
            assessment.requires_authority_consultation = True

        logger.info(
            "Avaliacao submetida para revisao: id=%s, risk_level=%s",
            assessment_id, assessment.overall_risk_level.value
        )

        return assessment

    async def dpo_review(
        self,
        assessment_id: UUID,
        approved: bool,
        opinion: str,
        reviewer_id: str
    ) -> PrivacyImpactAssessment:
        """
        Registra revisao do DPO.

        Args:
            assessment_id: ID da avaliacao.
            approved: Se aprovado.
            opinion: Parecer do DPO.
            reviewer_id: ID do revisor.

        Returns:
            PrivacyImpactAssessment: Avaliacao atualizada.
        """
        assessment = self._assessments.get(assessment_id)
        if not assessment:
            raise PIAError("Avaliacao nao encontrada", str(assessment_id))

        if assessment.status != AssessmentStatus.IN_REVIEW:
            raise PIAError("Avaliacao nao esta em revisao", str(assessment_id))

        assessment.dpo_opinion = opinion
        assessment.dpo_approved = approved
        assessment.dpo_approved_at = datetime.utcnow()

        if approved:
            if assessment.requires_authority_consultation:
                assessment.status = AssessmentStatus.REQUIRES_CONSULTATION
            else:
                assessment.status = AssessmentStatus.APPROVED
        else:
            assessment.status = AssessmentStatus.REJECTED

        logger.info(
            "Revisao DPO: assessment=%s, approved=%s, by=%s",
            assessment_id, approved, reviewer_id
        )

        return assessment

    async def get_assessment(self, assessment_id: UUID) -> Optional[PrivacyImpactAssessment]:
        """Recupera avaliacao por ID."""
        return self._assessments.get(assessment_id)

    async def list_assessments(
        self,
        status: Optional[AssessmentStatus] = None,
        risk_level: Optional[RiskLevel] = None
    ) -> List[PrivacyImpactAssessment]:
        """
        Lista avaliacoes com filtros.

        Args:
            status: Filtrar por status.
            risk_level: Filtrar por nivel de risco.

        Returns:
            List: Avaliacoes encontradas.
        """
        results = list(self._assessments.values())

        if status:
            results = [a for a in results if a.status == status]

        if risk_level:
            results = [a for a in results if a.overall_risk_level == risk_level]

        return results

    async def generate_report(
        self,
        assessment_id: UUID,
        format_type: str = "full"
    ) -> Dict[str, Any]:
        """
        Gera relatorio da avaliacao.

        Args:
            assessment_id: ID da avaliacao.
            format_type: Tipo de relatorio (full, summary, authority).

        Returns:
            Dict: Relatorio formatado.
        """
        assessment = self._assessments.get(assessment_id)
        if not assessment:
            raise PIAError("Avaliacao nao encontrada", str(assessment_id))

        report = {
            "report_type": "privacy_impact_assessment",
            "format": format_type,
            "generated_at": datetime.utcnow().isoformat(),
            "assessment": assessment.to_dict(),
        }

        if format_type == "summary":
            report["summary"] = {
                "title": assessment.title,
                "status": assessment.status.value,
                "overall_risk": assessment.overall_risk_level.value,
                "high_risks": assessment.high_risk_count,
                "activities_count": len(assessment.processing_activities),
                "mitigations_count": len(assessment.mitigation_measures),
                "dpo_approved": assessment.dpo_approved,
            }

        elif format_type == "authority":
            # Relatorio para autoridade de protecao de dados
            report["authority_report"] = {
                "organization": "Conecta PRO",
                "dpo_contact": "dpo@conectapro.com.br",
                "assessment_summary": assessment.description,
                "high_risk_processing": [
                    r.to_dict() for r in assessment.risk_assessments
                    if r.residual_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
                ],
                "consultation_reason": assessment.authority_consultation_notes,
                "mitigation_plan": [m.to_dict() for m in assessment.mitigation_measures],
            }

        return report

    async def schedule_review(
        self,
        assessment_id: UUID,
        review_date: date
    ) -> PrivacyImpactAssessment:
        """
        Agenda proxima revisao da avaliacao.

        Args:
            assessment_id: ID da avaliacao.
            review_date: Data da proxima revisao.

        Returns:
            PrivacyImpactAssessment: Avaliacao atualizada.
        """
        assessment = self._assessments.get(assessment_id)
        if not assessment:
            raise PIAError("Avaliacao nao encontrada", str(assessment_id))

        assessment.next_review_date = review_date
        logger.info(
            "Revisao agendada: assessment=%s, date=%s",
            assessment_id, review_date
        )

        return assessment


# Singleton
_pia_manager: Optional[PIAManager] = None


def get_pia_manager() -> PIAManager:
    """Retorna instancia singleton do PIAManager."""
    global _pia_manager
    if _pia_manager is None:
        _pia_manager = PIAManager()
    return _pia_manager


def init_pia_manager() -> PIAManager:
    """Inicializa o PIAManager singleton."""
    global _pia_manager
    _pia_manager = PIAManager()
    return _pia_manager


# Funcao utilitaria para verificar necessidade de DPIA
def requires_dpia(
    large_scale: bool = False,
    sensitive_data: bool = False,
    automated_decisions: bool = False,
    systematic_monitoring: bool = False,
    vulnerable_subjects: bool = False,
    innovative_technology: bool = False,
    cross_border_transfer: bool = False
) -> Tuple[bool, List[str]]:
    """
    Verifica se processamento requer DPIA conforme LGPD/GDPR.

    Args:
        large_scale: Processamento em larga escala.
        sensitive_data: Dados sensiveis (Art. 11 LGPD).
        automated_decisions: Decisoes automatizadas com efeitos significativos.
        systematic_monitoring: Monitoramento sistematico de areas publicas.
        vulnerable_subjects: Tratamento de dados de vulneraveis (criancas, etc).
        innovative_technology: Uso de nova tecnologia.
        cross_border_transfer: Transferencia internacional.

    Returns:
        Tuple[bool, List[str]]: (requer_dpia, lista_de_motivos)
    """
    reasons = []

    if large_scale:
        reasons.append("Processamento em larga escala de dados pessoais")

    if sensitive_data:
        reasons.append("Tratamento de dados sensiveis (LGPD Art. 11)")

    if automated_decisions:
        reasons.append("Decisoes automatizadas com efeitos legais ou significativos")

    if systematic_monitoring:
        reasons.append("Monitoramento sistematico em larga escala")

    if vulnerable_subjects:
        reasons.append("Tratamento de dados de titulares vulneraveis")

    if innovative_technology:
        reasons.append("Uso de nova tecnologia ou inovacao")

    if cross_border_transfer:
        reasons.append("Transferencia internacional de dados")

    # DPIA obrigatoria se 2+ criterios ou dados sensiveis
    requires = len(reasons) >= 2 or sensitive_data or automated_decisions

    return requires, reasons


# Import necessario para tipagem
from typing import Tuple
