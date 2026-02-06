"""
domains/procurement/entities/procurement.py - PROCUREMENT ENTITY
================================================================
Enterprise procurement entity with rich domain logic
"""

from typing import Dict, List, Optional, Any, Literal, NewType
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

from .enums import (
    ProcurementStatus,
    ProcurementType,
    ProcurementUrgency,
    SupplierRisk,
    PaymentTerms,
    ContractType,
    BiddingModality
)
from ..value_objects.money import Money

# Strong typing for domain identifiers
ProcurementId = NewType('ProcurementId', UUID)
SupplierId = NewType('SupplierId', UUID)
BudgetId = NewType('BudgetId', UUID)


class BudgetAllocation(BaseModel):
    """Alocacao orcamentaria - Value Object."""

    model_config = ConfigDict(frozen=True)

    budget_id: UUID
    account_code: str = Field(..., pattern=r"^\d{1,4}\.\d{1,2}\.\d{1,2}\.\d{1,3}$")
    allocated_amount: Money
    available_amount: Money
    fiscal_year: int = Field(..., ge=2020, le=2035)
    cost_center: str = Field(..., min_length=3, max_length=20)

    @model_validator(mode='after')
    def validate_amounts(self) -> 'BudgetAllocation':
        """Valida que disponivel nao excede alocado."""
        if self.available_amount > self.allocated_amount:
            raise ValueError("Valor disponivel nao pode exceder valor alocado")
        return self


class ContractTerms(BaseModel):
    """Termos contratuais - Value Object."""

    model_config = ConfigDict(frozen=True)

    payment_terms: PaymentTerms
    payment_description: str = Field(..., min_length=10, max_length=500)
    delivery_deadline_days: int = Field(..., gt=0, le=730)
    warranty_months: int = Field(default=0, ge=0, le=120)
    penalty_rate_percent: Decimal = Field(
        default=Decimal("0.5"),
        ge=Decimal("0"),
        le=Decimal("5")
    )
    contract_type: ContractType
    acceptance_criteria: str = Field(..., min_length=20, max_length=2000)
    sla_requirements: Dict[str, str] = Field(default_factory=dict)
    quality_standards: List[str] = Field(default_factory=list)


class SupplierQualification(BaseModel):
    """Qualificacao do fornecedor - Value Object."""

    model_config = ConfigDict(frozen=True)

    supplier_id: UUID
    supplier_name: str
    technical_score: int = Field(..., ge=0, le=100)
    commercial_score: int = Field(..., ge=0, le=100)
    compliance_score: int = Field(..., ge=0, le=100)
    financial_score: int = Field(..., ge=0, le=100)
    risk_rating: SupplierRisk
    certifications: List[str] = Field(default_factory=list)
    evaluation_date: date
    evaluation_notes: Optional[str] = None

    @property
    def overall_score(self) -> float:
        """Score geral ponderado do fornecedor."""
        weights = {
            'technical': 0.35,
            'commercial': 0.25,
            'compliance': 0.25,
            'financial': 0.15
        }
        return (
            self.technical_score * weights['technical'] +
            self.commercial_score * weights['commercial'] +
            self.compliance_score * weights['compliance'] +
            self.financial_score * weights['financial']
        )

    @property
    def is_qualified(self) -> bool:
        """Verifica se fornecedor esta qualificado."""
        min_scores = {
            'technical': 60,
            'commercial': 50,
            'compliance': 70,
            'overall': 65
        }
        return (
            self.technical_score >= min_scores['technical'] and
            self.commercial_score >= min_scores['commercial'] and
            self.compliance_score >= min_scores['compliance'] and
            self.overall_score >= min_scores['overall'] and
            self.risk_rating in [SupplierRisk.LOW, SupplierRisk.MEDIUM]
        )


class AuditEntry(BaseModel):
    """Entrada de auditoria."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str
    user_id: str
    details: Dict[str, Any] = Field(default_factory=dict)
    workflow_stage: int
    status: str


class ProcurementEntity(BaseModel):
    """
    Entidade principal de contratacao.

    Implementa regras de negocio e logica de dominio para
    processos de aquisicao enterprise.
    """

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True
    )

    # Identity
    procurement_id: UUID = Field(default_factory=uuid4)
    procurement_number: str = Field(..., pattern=r"^PROC-\d{4}-\d{6}$")

    # Basic Information
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=5000)
    procurement_type: ProcurementType
    urgency: ProcurementUrgency
    bidding_modality: Optional[BiddingModality] = None

    # Workflow
    status: ProcurementStatus = Field(default=ProcurementStatus.PLANNING)
    workflow_stage: int = Field(default=1, ge=1, le=12)

    # Financial
    budget_allocation: BudgetAllocation
    estimated_value: Money
    approved_value: Optional[Money] = None

    # Contract
    contract_terms: ContractTerms
    selected_supplier_id: Optional[UUID] = None
    supplier_qualifications: List[SupplierQualification] = Field(default_factory=list)

    # Timeline
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    planned_start_date: date
    planned_end_date: date
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None

    # Compliance
    legal_framework: str = Field(..., min_length=5, max_length=100)
    justification: Optional[str] = Field(None, max_length=2000)
    approval_chain: List[Dict[str, Any]] = Field(default_factory=list)

    # Audit
    audit_trail: List[AuditEntry] = Field(default_factory=list)
    created_by: str
    updated_by: Optional[str] = None

    # Metadata
    tags: List[str] = Field(default_factory=list)
    attachments: List[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_procurement(self) -> 'ProcurementEntity':
        """Valida regras de negocio da contratacao."""
        # Valida datas
        if self.planned_end_date <= self.planned_start_date:
            raise ValueError("Data final deve ser posterior a data inicial")

        # Valida prazo vs urgencia
        duration_days = (self.planned_end_date - self.planned_start_date).days
        max_days = self.urgency.max_duration_days()

        if duration_days > max_days:
            raise ValueError(
                f"Contratacao {self.urgency.value} deve ser concluida em ate {max_days} dias"
            )

        # Valida valor vs urgencia (contratacoes urgentes tem limite)
        if self.urgency in [ProcurementUrgency.EMERGENCY, ProcurementUrgency.CRITICAL]:
            max_value = Money(Decimal("1000000"))
            if self.estimated_value > max_value:
                raise ValueError(
                    f"Contratacoes {self.urgency.value} nao podem exceder {max_value}"
                )

        # Valida justificativa para urgencias
        if self.urgency.requires_justification() and not self.justification:
            raise ValueError(
                f"Contratacao {self.urgency.value} requer justificativa"
            )

        return self

    # ==========================================================================
    # Business Methods
    # ==========================================================================

    def advance_workflow(self, user_id: str, notes: Optional[str] = None) -> bool:
        """Avanca para proxima etapa do workflow."""
        if not self.status.can_advance():
            return False

        current_stage = self.workflow_stage
        next_status_map = {
            1: ProcurementStatus.BUDGET_APPROVAL,
            2: ProcurementStatus.BIDDING_PROCESS,
            3: ProcurementStatus.SUPPLIER_SELECTION,
            4: ProcurementStatus.CONTRACT_NEGOTIATION,
            5: ProcurementStatus.CONTRACT_SIGNED,
            6: ProcurementStatus.DELIVERY_PHASE,
            7: ProcurementStatus.QUALITY_CONTROL,
            8: ProcurementStatus.DELIVERED,
            9: ProcurementStatus.INVOICED,
            10: ProcurementStatus.PAID,
            11: ProcurementStatus.COMPLETED
        }

        if current_stage < 11:
            self.workflow_stage += 1
            self.status = next_status_map.get(self.workflow_stage, self.status)
            self.updated_at = datetime.utcnow()
            self.updated_by = user_id

            self._add_audit_entry(
                action="workflow_advance",
                user_id=user_id,
                details={
                    "from_stage": current_stage,
                    "to_stage": self.workflow_stage,
                    "notes": notes
                }
            )
            return True

        return False

    def approve_budget(
        self,
        approved_value: Money,
        approver_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """Aprova orcamento da contratacao."""
        # Verifica tolerancia de 10%
        max_variance = self.estimated_value * Decimal("1.1")
        if approved_value > max_variance:
            raise ValueError("Valor aprovado excede 10% do valor estimado")

        # Verifica saldo disponivel
        if approved_value > self.budget_allocation.available_amount:
            raise ValueError("Valor aprovado excede saldo orcamentario disponivel")

        self.approved_value = approved_value
        self.updated_at = datetime.utcnow()
        self.updated_by = approver_id

        self._add_audit_entry(
            action="budget_approval",
            user_id=approver_id,
            details={
                "estimated_value": str(self.estimated_value),
                "approved_value": str(approved_value),
                "variance_percent": float(
                    (approved_value.amount / self.estimated_value.amount - 1) * 100
                ),
                "notes": notes
            }
        )

        return True

    def select_supplier(
        self,
        supplier_id: UUID,
        user_id: str,
        justification: str
    ) -> bool:
        """Seleciona fornecedor para a contratacao."""
        # Busca qualificacao do fornecedor
        supplier_qual = next(
            (sq for sq in self.supplier_qualifications
             if sq.supplier_id == supplier_id),
            None
        )

        if not supplier_qual:
            raise ValueError("Fornecedor nao encontrado nas qualificacoes")

        if not supplier_qual.is_qualified:
            raise ValueError("Fornecedor nao atende aos criterios de qualificacao")

        # Verifica valor vs risco
        max_value = supplier_qual.risk_rating.max_contract_value()
        if self.estimated_value.amount > max_value:
            raise ValueError(
                f"Valor da contratacao excede limite para risco {supplier_qual.risk_rating}"
            )

        self.selected_supplier_id = supplier_id
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

        self._add_audit_entry(
            action="supplier_selection",
            user_id=user_id,
            details={
                "supplier_id": str(supplier_id),
                "supplier_name": supplier_qual.supplier_name,
                "overall_score": supplier_qual.overall_score,
                "risk_rating": supplier_qual.risk_rating,
                "justification": justification
            }
        )

        return True

    def add_supplier_qualification(
        self,
        qualification: SupplierQualification,
        user_id: str
    ) -> None:
        """Adiciona qualificacao de fornecedor."""
        # Remove qualificacao anterior do mesmo fornecedor
        self.supplier_qualifications = [
            sq for sq in self.supplier_qualifications
            if sq.supplier_id != qualification.supplier_id
        ]

        self.supplier_qualifications.append(qualification)
        self.updated_at = datetime.utcnow()

        self._add_audit_entry(
            action="supplier_qualification_added",
            user_id=user_id,
            details={
                "supplier_id": str(qualification.supplier_id),
                "supplier_name": qualification.supplier_name,
                "overall_score": qualification.overall_score,
                "is_qualified": qualification.is_qualified
            }
        )

    def cancel(self, user_id: str, reason: str) -> bool:
        """Cancela a contratacao."""
        if self.status in ProcurementStatus.terminal_statuses():
            raise ValueError("Contratacao ja esta em status terminal")

        previous_status = self.status
        self.status = ProcurementStatus.CANCELLED
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

        self._add_audit_entry(
            action="cancelled",
            user_id=user_id,
            details={
                "previous_status": previous_status,
                "reason": reason
            }
        )

        return True

    def suspend(self, user_id: str, reason: str) -> bool:
        """Suspende a contratacao."""
        if self.status in ProcurementStatus.terminal_statuses():
            raise ValueError("Contratacao ja esta em status terminal")

        previous_status = self.status
        self.status = ProcurementStatus.SUSPENDED
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

        self._add_audit_entry(
            action="suspended",
            user_id=user_id,
            details={
                "previous_status": previous_status,
                "reason": reason
            }
        )

        return True

    def calculate_risk(self) -> Literal["low", "medium", "high", "critical"]:
        """Calcula risco geral da contratacao."""
        risk_score = 0

        # Risco por urgencia
        urgency_risk = {
            ProcurementUrgency.ROUTINE: 0,
            ProcurementUrgency.URGENT: 20,
            ProcurementUrgency.EMERGENCY: 35,
            ProcurementUrgency.CRITICAL: 50
        }
        risk_score += urgency_risk.get(self.urgency, 0)

        # Risco por valor
        value = self.estimated_value.amount
        if value > Decimal("10000000"):
            risk_score += 30
        elif value > Decimal("1000000"):
            risk_score += 20
        elif value > Decimal("100000"):
            risk_score += 10

        # Risco por prazo
        duration = (self.planned_end_date - self.planned_start_date).days
        if duration < 30:
            risk_score += 25
        elif duration < 60:
            risk_score += 15
        elif duration < 90:
            risk_score += 5

        # Risco por fornecedor selecionado
        if self.selected_supplier_id:
            supplier_qual = next(
                (sq for sq in self.supplier_qualifications
                 if sq.supplier_id == self.selected_supplier_id),
                None
            )
            if supplier_qual:
                supplier_risk = {
                    SupplierRisk.LOW: 0,
                    SupplierRisk.MEDIUM: 10,
                    SupplierRisk.HIGH: 25,
                    SupplierRisk.CRITICAL: 40
                }
                risk_score += supplier_risk.get(supplier_qual.risk_rating, 20)

        # Classificacao final
        if risk_score >= 80:
            return "critical"
        elif risk_score >= 60:
            return "high"
        elif risk_score >= 30:
            return "medium"
        return "low"

    def get_progress_percentage(self) -> int:
        """Retorna percentual de progresso."""
        return int((self.workflow_stage / 12) * 100)

    def _add_audit_entry(
        self,
        action: str,
        user_id: str,
        details: Dict[str, Any]
    ) -> None:
        """Adiciona entrada no audit trail."""
        entry = AuditEntry(
            action=action,
            user_id=user_id,
            details=details,
            workflow_stage=self.workflow_stage,
            status=self.status.value if isinstance(self.status, ProcurementStatus) else self.status
        )
        self.audit_trail.append(entry)

    @staticmethod
    def generate_procurement_number(year: int, sequence: int) -> str:
        """Gera numero da contratacao."""
        return f"PROC-{year}-{sequence:06d}"
