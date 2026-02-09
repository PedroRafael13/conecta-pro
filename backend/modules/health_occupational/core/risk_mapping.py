"""
Module: RiskMapping
Description: Sistema de mapeamento de riscos ocupacionais (PPRA/PGR)
             conforme NR-9 - Programa de Prevencao de Riscos Ambientais.
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: NR-9 (Portaria MTb 3.214/78) - PPRA/PGR
"""

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()


class RiskCategory(StrEnum):
    """Categorias de riscos ocupacionais conforme NR-9."""

    FISICO = "fisico"  # Ruido, vibracoes, temperaturas, etc
    QUIMICO = "quimico"  # Poeiras, fumos, gases, vapores
    BIOLOGICO = "biologico"  # Virus, bacterias, fungos
    ERGONOMICO = "ergonomico"  # Posturas, movimentos repetitivos
    ACIDENTE = "acidente"  # Mecanicos, eletricos, quedas


class RiskLevel(StrEnum):
    """Niveis de risco."""

    TRIVIAL = "trivial"  # Nao requer acao
    TOLERAVEL = "toleravel"  # Monitorar
    MODERADO = "moderado"  # Controlar
    SUBSTANCIAL = "substancial"  # Acao urgente
    INTOLERAVEL = "intoleravel"  # Parar atividade


class ExposureFrequency(StrEnum):
    """Frequencia de exposicao ao risco."""

    RARA = "rara"  # Menos de 1x/mes
    OCASIONAL = "ocasional"  # 1-4x/mes
    FREQUENTE = "frequente"  # 1-4x/semana
    CONTINUA = "continua"  # Diaria


class ControlType(StrEnum):
    """Tipos de medidas de controle (hierarquia)."""

    ELIMINACAO = "eliminacao"  # Eliminar o risco
    SUBSTITUICAO = "substituicao"  # Substituir por menos perigoso
    CONTROLE_ENGENHARIA = "engenharia"  # Controles de engenharia
    CONTROLE_ADMINISTRATIVO = "administrativo"  # Procedimentos, sinalizacao
    EPI = "epi"  # Equipamento de protecao individual


class RiskMappingError(Exception):
    """Erro em operacao de mapeamento de riscos."""

    pass


@dataclass
class RiskAgent:
    """Agente de risco identificado."""

    id: UUID
    name: str
    category: RiskCategory
    description: str
    tolerance_limit: str | None = None  # Limite de tolerancia (NR-15)
    measurement_unit: str | None = None  # Unidade de medida
    health_effects: list[str] = field(default_factory=list)
    legal_reference: str | None = None  # Referencia legal (NR)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "tolerance_limit": self.tolerance_limit,
            "measurement_unit": self.measurement_unit,
            "health_effects": self.health_effects,
            "legal_reference": self.legal_reference,
        }


@dataclass
class RiskMeasurement:
    """Medicao quantitativa de risco."""

    id: UUID
    risk_id: UUID
    measured_value: float
    unit: str
    measurement_date: date
    measurement_method: str
    equipment_used: str | None = None
    location: str | None = None
    conditions: str | None = None
    measured_by: str | None = None
    above_limit: bool = False
    observations: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "risk_id": str(self.risk_id),
            "measured_value": self.measured_value,
            "unit": self.unit,
            "measurement_date": self.measurement_date.isoformat(),
            "measurement_method": self.measurement_method,
            "equipment_used": self.equipment_used,
            "above_limit": self.above_limit,
        }


@dataclass
class ControlMeasure:
    """Medida de controle de risco."""

    id: UUID
    risk_id: UUID
    control_type: ControlType
    description: str
    status: str  # planned, in_progress, implemented
    effectiveness: str | None = None  # alta, media, baixa
    responsible: str | None = None
    deadline: date | None = None
    implemented_at: date | None = None
    cost_estimate: float | None = None
    observations: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "risk_id": str(self.risk_id),
            "control_type": self.control_type.value,
            "description": self.description,
            "status": self.status,
            "effectiveness": self.effectiveness,
            "responsible": self.responsible,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "implemented_at": self.implemented_at.isoformat() if self.implemented_at else None,
        }


@dataclass
class OccupationalRisk:
    """Risco ocupacional identificado e avaliado."""

    id: UUID
    agent: RiskAgent
    location_id: str
    location_name: str
    department: str
    activity: str
    exposure_frequency: ExposureFrequency
    exposed_workers: int
    probability: int  # 1-5
    severity: int  # 1-5
    risk_level: RiskLevel
    measurements: list[RiskMeasurement] = field(default_factory=list)
    control_measures: list[ControlMeasure] = field(default_factory=list)
    requires_epi: bool = False
    required_epi: list[str] = field(default_factory=list)
    requires_training: bool = False
    identified_at: datetime = field(default_factory=datetime.utcnow)
    identified_by: str | None = None
    last_review: datetime | None = None
    next_review: date | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def risk_score(self) -> int:
        """Calcula score de risco (P x S)."""
        return self.probability * self.severity

    @classmethod
    def calculate_risk_level(cls, probability: int, severity: int) -> RiskLevel:
        """Calcula nivel de risco baseado na matriz P x S."""
        score = probability * severity
        if score <= 2:
            return RiskLevel.TRIVIAL
        elif score <= 4:
            return RiskLevel.TOLERAVEL
        elif score <= 9:
            return RiskLevel.MODERADO
        elif score <= 16:
            return RiskLevel.SUBSTANCIAL
        else:
            return RiskLevel.INTOLERAVEL

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "agent": self.agent.to_dict(),
            "location_id": self.location_id,
            "location_name": self.location_name,
            "department": self.department,
            "activity": self.activity,
            "exposure_frequency": self.exposure_frequency.value,
            "exposed_workers": self.exposed_workers,
            "probability": self.probability,
            "severity": self.severity,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level.value,
            "measurements": [m.to_dict() for m in self.measurements],
            "control_measures": [c.to_dict() for c in self.control_measures],
            "requires_epi": self.requires_epi,
            "required_epi": self.required_epi,
            "requires_training": self.requires_training,
            "identified_at": self.identified_at.isoformat(),
            "next_review": self.next_review.isoformat() if self.next_review else None,
        }


@dataclass
class WorkLocation:
    """Local de trabalho para mapeamento de riscos."""

    id: UUID
    name: str
    department: str
    description: str | None = None
    area_m2: float | None = None
    workers_count: int = 0
    activities: list[str] = field(default_factory=list)
    parent_id: UUID | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "department": self.department,
            "description": self.description,
            "area_m2": self.area_m2,
            "workers_count": self.workers_count,
            "activities": self.activities,
        }


# SQLAlchemy Models
class OccupationalRiskModel(Base):
    """Modelo de banco para riscos ocupacionais."""

    __tablename__ = "health_occupational_risks"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    agent_id = Column(PGUUID(as_uuid=True), nullable=False)
    agent_name = Column(String(255), nullable=False)
    category = Column(String(30), nullable=False, index=True)
    location_id = Column(String(100), nullable=False, index=True)
    location_name = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False, index=True)
    activity = Column(Text, nullable=False)
    exposure_frequency = Column(String(20), nullable=False)
    exposed_workers = Column(Integer, default=0)
    probability = Column(Integer, nullable=False)
    severity = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False, index=True)
    measurements = Column(JSONB, default=[])
    control_measures = Column(JSONB, default=[])
    requires_epi = Column(Boolean, default=False)
    required_epi = Column(JSONB, default=[])
    requires_training = Column(Boolean, default=False)
    identified_at = Column(DateTime, default=datetime.utcnow)
    identified_by = Column(String(100), nullable=True)
    last_review = Column(DateTime, nullable=True)
    next_review = Column(Date, nullable=True, index=True)
    extra_metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RiskAgentModel(Base):
    """Modelo de banco para agentes de risco."""

    __tablename__ = "health_risk_agents"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, unique=True)
    category = Column(String(30), nullable=False, index=True)
    description = Column(Text, nullable=True)
    tolerance_limit = Column(String(100), nullable=True)
    measurement_unit = Column(String(50), nullable=True)
    health_effects = Column(JSONB, default=[])
    legal_reference = Column(String(100), nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PPRAConfig(BaseModel):
    """Configuracao do sistema PPRA/PGR."""

    default_review_months: int = Field(default=12, ge=6)
    auto_schedule_reviews: bool = True
    require_quantitative_measurement: bool = False
    probability_scale: int = Field(default=5, ge=3, le=10)
    severity_scale: int = Field(default=5, ge=3, le=10)


class RiskMappingManager:
    """
    Gerenciador de mapeamento de riscos ocupacionais (PPRA/PGR).

    Coordena identificacao, avaliacao e controle de riscos
    ambientais conforme NR-9.

    Example:
        >>> manager = RiskMappingManager()
        >>> risk = await manager.identify_risk(
        ...     agent=noise_agent,
        ...     location_id="loc1",
        ...     probability=3,
        ...     severity=4
        ... )
    """

    def __init__(self, config: PPRAConfig | None = None):
        """
        Inicializa o gerenciador PPRA/PGR.

        Args:
            config: Configuracao do sistema.
        """
        self.config = config or PPRAConfig()
        self._risks: dict[UUID, OccupationalRisk] = {}
        self._agents: dict[UUID, RiskAgent] = {}
        self._locations: dict[UUID, WorkLocation] = {}
        self._init_default_agents()
        logger.info("RiskMappingManager inicializado")

    def _init_default_agents(self) -> None:
        """Inicializa agentes de risco padrao."""
        default_agents = [
            RiskAgent(
                id=uuid4(),
                name="Ruido",
                category=RiskCategory.FISICO,
                description="Exposicao a niveis de pressao sonora elevados",
                tolerance_limit="85 dB(A) para 8h",
                measurement_unit="dB(A)",
                health_effects=["PAIR", "Estresse", "Fadiga"],
                legal_reference="NR-15 Anexo 1",
            ),
            RiskAgent(
                id=uuid4(),
                name="Calor",
                category=RiskCategory.FISICO,
                description="Exposicao a temperaturas elevadas",
                tolerance_limit="IBUTG conforme NR-15",
                measurement_unit="IBUTG",
                health_effects=["Desidratacao", "Exaustao termica"],
                legal_reference="NR-15 Anexo 3",
            ),
            RiskAgent(
                id=uuid4(),
                name="Vibracoes",
                category=RiskCategory.FISICO,
                description="Exposicao a vibracoes corpo inteiro ou maos-bracos",
                measurement_unit="m/s2",
                health_effects=["Lesoes vasculares", "Dores articulares"],
                legal_reference="NR-15 Anexo 8",
            ),
            RiskAgent(
                id=uuid4(),
                name="Poeira mineral",
                category=RiskCategory.QUIMICO,
                description="Exposicao a poeiras inorganicas",
                tolerance_limit="Conforme NR-15 Anexo 12",
                health_effects=["Pneumoconiose", "Silicose"],
                legal_reference="NR-15 Anexo 12",
            ),
            RiskAgent(
                id=uuid4(),
                name="Agentes biologicos",
                category=RiskCategory.BIOLOGICO,
                description="Exposicao a microorganismos patogenicos",
                health_effects=["Infeccoes", "Doencas infecciosas"],
                legal_reference="NR-32",
            ),
            RiskAgent(
                id=uuid4(),
                name="Postura inadequada",
                category=RiskCategory.ERGONOMICO,
                description="Manutencao de posturas inadequadas",
                health_effects=["LER/DORT", "Lombalgia"],
                legal_reference="NR-17",
            ),
            RiskAgent(
                id=uuid4(),
                name="Queda de altura",
                category=RiskCategory.ACIDENTE,
                description="Risco de queda de nivel diferente",
                health_effects=["Fraturas", "Traumatismos"],
                legal_reference="NR-35",
            ),
        ]

        for agent in default_agents:
            self._agents[agent.id] = agent

    async def identify_risk(
        self,
        agent: RiskAgent,
        location_id: str,
        location_name: str,
        department: str,
        activity: str,
        probability: int,
        severity: int,
        exposure_frequency: ExposureFrequency,
        exposed_workers: int,
        identified_by: str | None = None,
        required_epi: list[str] | None = None,
    ) -> OccupationalRisk:
        """
        Identifica e registra um risco ocupacional.

        Args:
            agent: Agente de risco.
            location_id: ID do local.
            location_name: Nome do local.
            department: Departamento.
            activity: Atividade de exposicao.
            probability: Probabilidade (1-5).
            severity: Severidade (1-5).
            exposure_frequency: Frequencia de exposicao.
            exposed_workers: Numero de trabalhadores expostos.
            identified_by: ID de quem identificou.
            required_epi: EPIs necessarios.

        Returns:
            OccupationalRisk: Risco identificado.
        """
        risk_level = OccupationalRisk.calculate_risk_level(probability, severity)
        requires_epi = risk_level in [RiskLevel.MODERADO, RiskLevel.SUBSTANCIAL, RiskLevel.INTOLERAVEL]

        risk = OccupationalRisk(
            id=uuid4(),
            agent=agent,
            location_id=location_id,
            location_name=location_name,
            department=department,
            activity=activity,
            exposure_frequency=exposure_frequency,
            exposed_workers=exposed_workers,
            probability=probability,
            severity=severity,
            risk_level=risk_level,
            requires_epi=requires_epi,
            required_epi=required_epi or [],
            requires_training=risk_level != RiskLevel.TRIVIAL,
            identified_by=identified_by,
            next_review=date.today() + timedelta(days=self.config.default_review_months * 30),
        )

        self._risks[risk.id] = risk

        logger.info(
            "Risco identificado: id=%s, agent=%s, location=%s, level=%s",
            risk.id,
            agent.name,
            location_name,
            risk_level.value,
        )

        return risk

    async def add_measurement(
        self,
        risk_id: UUID,
        measured_value: float,
        unit: str,
        measurement_date: date,
        measurement_method: str,
        equipment_used: str | None = None,
        measured_by: str | None = None,
        tolerance_limit: float | None = None,
    ) -> RiskMeasurement:
        """
        Adiciona medicao quantitativa a um risco.

        Args:
            risk_id: ID do risco.
            measured_value: Valor medido.
            unit: Unidade de medida.
            measurement_date: Data da medicao.
            measurement_method: Metodo de medicao.
            equipment_used: Equipamento utilizado.
            measured_by: ID de quem mediu.
            tolerance_limit: Limite de tolerancia para comparacao.

        Returns:
            RiskMeasurement: Medicao registrada.
        """
        risk = self._risks.get(risk_id)
        if not risk:
            raise RiskMappingError(f"Risco nao encontrado: {risk_id}")

        above_limit = False
        if tolerance_limit is not None:
            above_limit = measured_value > tolerance_limit

        measurement = RiskMeasurement(
            id=uuid4(),
            risk_id=risk_id,
            measured_value=measured_value,
            unit=unit,
            measurement_date=measurement_date,
            measurement_method=measurement_method,
            equipment_used=equipment_used,
            measured_by=measured_by,
            above_limit=above_limit,
        )

        risk.measurements.append(measurement)

        logger.info(
            "Medicao adicionada: risk=%s, value=%s %s, above_limit=%s", risk_id, measured_value, unit, above_limit
        )

        return measurement

    async def add_control_measure(
        self,
        risk_id: UUID,
        control_type: ControlType,
        description: str,
        responsible: str | None = None,
        deadline: date | None = None,
        cost_estimate: float | None = None,
    ) -> ControlMeasure:
        """
        Adiciona medida de controle a um risco.

        Args:
            risk_id: ID do risco.
            control_type: Tipo de controle.
            description: Descricao da medida.
            responsible: Responsavel pela implementacao.
            deadline: Prazo para implementacao.
            cost_estimate: Estimativa de custo.

        Returns:
            ControlMeasure: Medida de controle registrada.
        """
        risk = self._risks.get(risk_id)
        if not risk:
            raise RiskMappingError(f"Risco nao encontrado: {risk_id}")

        measure = ControlMeasure(
            id=uuid4(),
            risk_id=risk_id,
            control_type=control_type,
            description=description,
            status="planned",
            responsible=responsible,
            deadline=deadline,
            cost_estimate=cost_estimate,
        )

        risk.control_measures.append(measure)

        logger.info("Medida de controle adicionada: risk=%s, type=%s", risk_id, control_type.value)

        return measure

    async def update_control_status(
        self, risk_id: UUID, control_id: UUID, status: str, effectiveness: str | None = None
    ) -> ControlMeasure:
        """
        Atualiza status de medida de controle.

        Args:
            risk_id: ID do risco.
            control_id: ID da medida.
            status: Novo status.
            effectiveness: Efetividade (se implementada).

        Returns:
            ControlMeasure: Medida atualizada.
        """
        risk = self._risks.get(risk_id)
        if not risk:
            raise RiskMappingError(f"Risco nao encontrado: {risk_id}")

        for measure in risk.control_measures:
            if measure.id == control_id:
                measure.status = status
                if status == "implemented":
                    measure.implemented_at = date.today()
                if effectiveness:
                    measure.effectiveness = effectiveness
                return measure

        raise RiskMappingError(f"Medida de controle nao encontrada: {control_id}")

    async def reassess_risk(
        self, risk_id: UUID, new_probability: int, new_severity: int, assessed_by: str | None = None
    ) -> OccupationalRisk:
        """
        Reavalia um risco apos implementacao de controles.

        Args:
            risk_id: ID do risco.
            new_probability: Nova probabilidade.
            new_severity: Nova severidade.
            assessed_by: ID de quem reavaliou.

        Returns:
            OccupationalRisk: Risco reavaliado.
        """
        risk = self._risks.get(risk_id)
        if not risk:
            raise RiskMappingError(f"Risco nao encontrado: {risk_id}")

        old_level = risk.risk_level

        risk.probability = new_probability
        risk.severity = new_severity
        risk.risk_level = OccupationalRisk.calculate_risk_level(new_probability, new_severity)
        risk.last_review = datetime.utcnow()
        risk.next_review = date.today() + timedelta(days=self.config.default_review_months * 30)

        # Registra historico
        risk.metadata["assessment_history"] = risk.metadata.get("assessment_history", [])
        risk.metadata["assessment_history"].append(
            {
                "date": datetime.utcnow().isoformat(),
                "old_level": old_level.value,
                "new_level": risk.risk_level.value,
                "assessed_by": assessed_by,
            }
        )

        logger.info("Risco reavaliado: id=%s, %s -> %s", risk_id, old_level.value, risk.risk_level.value)

        return risk

    async def get_risk(self, risk_id: UUID) -> OccupationalRisk | None:
        """Recupera risco por ID."""
        return self._risks.get(risk_id)

    async def list_risks(
        self,
        location_id: str | None = None,
        department: str | None = None,
        category: RiskCategory | None = None,
        risk_level: RiskLevel | None = None,
    ) -> list[OccupationalRisk]:
        """
        Lista riscos com filtros.

        Args:
            location_id: Filtrar por local.
            department: Filtrar por departamento.
            category: Filtrar por categoria.
            risk_level: Filtrar por nivel.

        Returns:
            List[OccupationalRisk]: Riscos encontrados.
        """
        risks = list(self._risks.values())

        if location_id:
            risks = [r for r in risks if r.location_id == location_id]
        if department:
            risks = [r for r in risks if r.department == department]
        if category:
            risks = [r for r in risks if r.agent.category == category]
        if risk_level:
            risks = [r for r in risks if r.risk_level == risk_level]

        return risks

    async def get_high_risks(self) -> list[OccupationalRisk]:
        """Lista riscos substanciais ou intoleraveis."""
        return [r for r in self._risks.values() if r.risk_level in [RiskLevel.SUBSTANCIAL, RiskLevel.INTOLERAVEL]]

    async def get_pending_reviews(self) -> list[OccupationalRisk]:
        """Lista riscos com revisao pendente."""
        today = date.today()
        return [r for r in self._risks.values() if r.next_review and r.next_review <= today]

    async def generate_risk_matrix(self) -> dict[str, Any]:
        """
        Gera matriz de riscos.

        Returns:
            Dict: Matriz de riscos com contagens.
        """
        matrix = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_risks": len(self._risks),
            "by_level": {},
            "by_category": {},
            "by_department": {},
            "matrix": [[0 for _ in range(5)] for _ in range(5)],  # 5x5
        }

        for risk in self._risks.values():
            # Por nivel
            level = risk.risk_level.value
            matrix["by_level"][level] = matrix["by_level"].get(level, 0) + 1

            # Por categoria
            cat = risk.agent.category.value
            matrix["by_category"][cat] = matrix["by_category"].get(cat, 0) + 1

            # Por departamento
            dept = risk.department
            matrix["by_department"][dept] = matrix["by_department"].get(dept, 0) + 1

            # Matriz P x S
            p = min(risk.probability - 1, 4)
            s = min(risk.severity - 1, 4)
            matrix["matrix"][p][s] += 1

        return matrix

    async def generate_ppra_report(
        self, location_id: str | None = None, department: str | None = None
    ) -> dict[str, Any]:
        """
        Gera relatorio PPRA/PGR.

        Args:
            location_id: Filtrar por local.
            department: Filtrar por departamento.

        Returns:
            Dict: Relatorio PPRA formatado.
        """
        risks = await self.list_risks(location_id=location_id, department=department)

        report = {
            "report_type": "PPRA/PGR",
            "generated_at": datetime.utcnow().isoformat(),
            "validity_period": f"{date.today().isoformat()} a {(date.today() + timedelta(days=365)).isoformat()}",
            "summary": {
                "total_risks": len(risks),
                "high_risks": len([r for r in risks if r.risk_level in [RiskLevel.SUBSTANCIAL, RiskLevel.INTOLERAVEL]]),
                "total_exposed_workers": sum(r.exposed_workers for r in risks),
                "pending_controls": 0,
            },
            "by_category": {},
            "risks": [],
            "action_plan": [],
        }

        # Agrupa por categoria
        for risk in risks:
            cat = risk.agent.category.value
            if cat not in report["by_category"]:
                report["by_category"][cat] = []
            report["by_category"][cat].append(risk.to_dict())

            # Adiciona risco detalhado
            report["risks"].append(risk.to_dict())

            # Plano de acao para controles pendentes
            for control in risk.control_measures:
                if control.status != "implemented":
                    report["pending_controls"] = report["summary"]["pending_controls"] + 1
                    report["action_plan"].append(
                        {
                            "risk": risk.agent.name,
                            "location": risk.location_name,
                            "control": control.description,
                            "type": control.control_type.value,
                            "responsible": control.responsible,
                            "deadline": control.deadline.isoformat() if control.deadline else None,
                        }
                    )

        report["summary"]["pending_controls"] = len(report["action_plan"])

        return report

    async def get_agent(self, agent_id: UUID) -> RiskAgent | None:
        """Recupera agente de risco por ID."""
        return self._agents.get(agent_id)

    async def list_agents(self, category: RiskCategory | None = None) -> list[RiskAgent]:
        """Lista agentes de risco."""
        agents = list(self._agents.values())
        if category:
            agents = [a for a in agents if a.category == category]
        return agents

    async def register_agent(self, agent: RiskAgent) -> RiskAgent:
        """Registra novo agente de risco."""
        self._agents[agent.id] = agent
        logger.info("Agente registrado: %s (%s)", agent.name, agent.category.value)
        return agent


# Singleton
_risk_manager: RiskMappingManager | None = None


def get_risk_manager() -> RiskMappingManager:
    """Retorna instancia singleton do RiskMappingManager."""
    global _risk_manager
    if _risk_manager is None:
        _risk_manager = RiskMappingManager()
    return _risk_manager


def init_risk_manager(config: PPRAConfig | None = None) -> RiskMappingManager:
    """Inicializa o RiskMappingManager singleton."""
    global _risk_manager
    _risk_manager = RiskMappingManager(config)
    return _risk_manager
