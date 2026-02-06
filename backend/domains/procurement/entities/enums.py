"""
domains/procurement/entities/enums.py - PROCUREMENT ENUMS
==========================================================
Enterprise procurement status and type enumerations
"""

from enum import Enum
from typing import List


class ProcurementStatus(str, Enum):
    """Status da contratacao com fluxo empresarial completo."""

    PLANNING = "planning"
    BUDGET_APPROVAL = "budget_approval"
    BIDDING_PROCESS = "bidding_process"
    SUPPLIER_SELECTION = "supplier_selection"
    CONTRACT_NEGOTIATION = "contract_negotiation"
    CONTRACT_SIGNED = "contract_signed"
    DELIVERY_PHASE = "delivery_phase"
    QUALITY_CONTROL = "quality_control"
    DELIVERED = "delivered"
    INVOICED = "invoiced"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"

    @classmethod
    def active_statuses(cls) -> List["ProcurementStatus"]:
        """Retorna status ativos."""
        return [
            cls.PLANNING, cls.BUDGET_APPROVAL, cls.BIDDING_PROCESS,
            cls.SUPPLIER_SELECTION, cls.CONTRACT_NEGOTIATION,
            cls.CONTRACT_SIGNED, cls.DELIVERY_PHASE, cls.QUALITY_CONTROL
        ]

    @classmethod
    def terminal_statuses(cls) -> List["ProcurementStatus"]:
        """Retorna status terminais."""
        return [cls.COMPLETED, cls.CANCELLED, cls.SUSPENDED]

    def can_advance(self) -> bool:
        """Verifica se pode avancar para proximo status."""
        return self not in self.terminal_statuses()

    def workflow_order(self) -> int:
        """Retorna ordem no workflow."""
        order_map = {
            self.PLANNING: 1,
            self.BUDGET_APPROVAL: 2,
            self.BIDDING_PROCESS: 3,
            self.SUPPLIER_SELECTION: 4,
            self.CONTRACT_NEGOTIATION: 5,
            self.CONTRACT_SIGNED: 6,
            self.DELIVERY_PHASE: 7,
            self.QUALITY_CONTROL: 8,
            self.DELIVERED: 9,
            self.INVOICED: 10,
            self.PAID: 11,
            self.COMPLETED: 12,
            self.CANCELLED: 99,
            self.SUSPENDED: 98
        }
        return order_map.get(self, 0)


class ProcurementType(str, Enum):
    """Tipo de contratacao."""

    GOODS = "goods"
    SERVICES = "services"
    CONSTRUCTION = "construction"
    CONSULTING = "consulting"
    MAINTENANCE = "maintenance"
    OUTSOURCING = "outsourcing"
    IT_SERVICES = "it_services"
    LOGISTICS = "logistics"

    def requires_technical_evaluation(self) -> bool:
        """Verifica se requer avaliacao tecnica."""
        return self in [
            self.CONSTRUCTION,
            self.CONSULTING,
            self.IT_SERVICES
        ]

    def default_warranty_months(self) -> int:
        """Garantia padrao em meses por tipo."""
        warranty_map = {
            self.GOODS: 12,
            self.SERVICES: 6,
            self.CONSTRUCTION: 60,
            self.CONSULTING: 3,
            self.MAINTENANCE: 3,
            self.OUTSOURCING: 0,
            self.IT_SERVICES: 12,
            self.LOGISTICS: 0
        }
        return warranty_map.get(self, 6)


class ProcurementUrgency(str, Enum):
    """Urgencia da contratacao."""

    ROUTINE = "routine"
    URGENT = "urgent"
    EMERGENCY = "emergency"
    CRITICAL = "critical"

    def max_duration_days(self) -> int:
        """Duracao maxima em dias por urgencia."""
        duration_map = {
            self.ROUTINE: 180,
            self.URGENT: 60,
            self.EMERGENCY: 30,
            self.CRITICAL: 15
        }
        return duration_map.get(self, 180)

    def requires_justification(self) -> bool:
        """Verifica se requer justificativa especial."""
        return self in [self.EMERGENCY, self.CRITICAL]


class SupplierRisk(str, Enum):
    """Nivel de risco do fornecedor."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def max_contract_value(self) -> int:
        """Valor maximo de contrato por risco (em reais)."""
        value_map = {
            self.LOW: 10_000_000,
            self.MEDIUM: 1_000_000,
            self.HIGH: 100_000,
            self.CRITICAL: 0
        }
        return value_map.get(self, 0)


class PaymentTerms(str, Enum):
    """Condicoes de pagamento."""

    ADVANCE = "advance"
    UPON_DELIVERY = "upon_delivery"
    NET_15 = "net_15"
    NET_30 = "net_30"
    NET_60 = "net_60"
    NET_90 = "net_90"
    MILESTONE = "milestone"
    INSTALLMENTS = "installments"


class ContractType(str, Enum):
    """Tipo de contrato."""

    FIXED_PRICE = "fixed_price"
    COST_PLUS = "cost_plus"
    TIME_AND_MATERIALS = "time_and_materials"
    FRAMEWORK_AGREEMENT = "framework_agreement"
    SERVICE_LEVEL_AGREEMENT = "sla"
    MAINTENANCE_CONTRACT = "maintenance"


class BiddingModality(str, Enum):
    """Modalidade de licitacao (Lei 8.666/93 e Lei 14.133/21)."""

    CONCORRENCIA = "concorrencia"
    TOMADA_PRECOS = "tomada_precos"
    CONVITE = "convite"
    CONCURSO = "concurso"
    LEILAO = "leilao"
    PREGAO_ELETRONICO = "pregao_eletronico"
    PREGAO_PRESENCIAL = "pregao_presencial"
    DISPENSA = "dispensa"
    INEXIGIBILIDADE = "inexigibilidade"
    DIALOGO_COMPETITIVO = "dialogo_competitivo"

    def is_competitive(self) -> bool:
        """Verifica se e modalidade competitiva."""
        return self not in [self.DISPENSA, self.INEXIGIBILIDADE]
