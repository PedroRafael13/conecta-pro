# SPRINT 14: PROPOSTAS PREMIUM (CPQ)
## ERP CONECTA MAIS - FASE 2

**Duracao:** 2 semanas
**Modulo:** CRM
**Prioridade:** MAXIMA
**Dependencia:** CRM Fase 1 concluido

---

## OBJETIVO

Implementar sistema CPQ (Configure, Price, Quote) completo:
- Criacao de propostas profissionais
- Motor de precificacao com CCT
- Calculo automatico de impostos
- Workflow de aprovacao
- Geracao de PDF
- Assinatura digital

---

## ARQUIVOS A CRIAR

### 1. Models

```
modules/crm/models/proposal.py
modules/crm/models/proposal_item.py
modules/crm/models/proposal_approval.py
modules/crm/models/proposal_template.py
modules/crm/models/proposal_history.py
```

### 2. Schemas

```
modules/crm/schemas/proposal.py
```

### 3. Repository

```
modules/crm/repositories/proposal_repository.py
```

### 4. Services

```
modules/crm/services/proposal_service.py
modules/crm/services/pricing_engine.py
modules/crm/services/pdf_generator.py
```

### 5. Controller

```
modules/crm/controllers/proposal_controller.py
```

### 6. Testes

```
tests/test_proposal_model.py
tests/test_pricing_engine.py
tests/test_proposal_api.py
```

---

## DIA 1-2: MODELS

### Tarefa 1.1: Proposal Model

```python
# modules/crm/models/proposal.py
"""Model de Proposta Comercial."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum as SQLEnum,
    ForeignKey, Integer, Numeric, String, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class ProposalStatus(str, Enum):
    """Status da proposta."""
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class Proposal(Base):
    """
    Proposta comercial.

    Representa uma proposta de venda com itens,
    precificacao e workflow de aprovacao.
    """

    __tablename__ = "proposals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identificacao
    number = Column(String(20), unique=True, nullable=False, index=True)
    version = Column(Integer, default=1)

    # Relacionamentos principais
    opportunity_id = Column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id"),
        nullable=False
    )
    client_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id"),
        nullable=False
    )
    salesperson_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    # Status
    status = Column(
        SQLEnum(ProposalStatus),
        default=ProposalStatus.DRAFT,
        nullable=False
    )

    # Valores (SEMPRE Decimal)
    subtotal = Column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))
    discount_percent = Column(Numeric(5, 2), default=Decimal("0.00"))
    discount_value = Column(Numeric(15, 2), default=Decimal("0.00"))
    tax_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    total = Column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))

    # CCT
    cct_value = Column(Numeric(15, 2), default=Decimal("0.00"))
    cct_percent = Column(Numeric(5, 2), default=Decimal("0.00"))

    # Margem
    margin_percent = Column(Numeric(5, 2), default=Decimal("0.00"))
    margin_value = Column(Numeric(15, 2), default=Decimal("0.00"))

    # Datas
    valid_until = Column(Date, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)

    # Conteudo
    introduction = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Template
    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("proposal_templates.id"),
        nullable=True
    )

    # Assinatura
    signature_url = Column(String(500), nullable=True)
    signed_at = Column(DateTime, nullable=True)
    signed_by = Column(String(200), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    items = relationship(
        "ProposalItem",
        back_populates="proposal",
        cascade="all, delete-orphan"
    )
    approvals = relationship(
        "ProposalApproval",
        back_populates="proposal",
        cascade="all, delete-orphan"
    )
    history = relationship(
        "ProposalHistory",
        back_populates="proposal",
        cascade="all, delete-orphan"
    )
    opportunity = relationship("Opportunity", back_populates="proposals")
    client = relationship("Company")
    salesperson = relationship("User", foreign_keys=[salesperson_id])

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<Proposal(id={self.id}, number='{self.number}', status={self.status})>"

    def is_editable(self) -> bool:
        """Verifica se proposta pode ser editada."""
        return self.status in (ProposalStatus.DRAFT, ProposalStatus.PENDING_APPROVAL)

    def calculate_totals(self) -> None:
        """Recalcula totais baseado nos itens."""
        if not self.items:
            self.subtotal = Decimal("0.00")
            self.total = Decimal("0.00")
            return

        self.subtotal = sum(item.total for item in self.items)
        self.discount_value = self.subtotal * (self.discount_percent / 100)
        self.total = self.subtotal - self.discount_value + self.tax_amount
```

### Tarefa 1.2: ProposalItem Model

```python
# modules/crm/models/proposal_item.py
"""Model de Item de Proposta."""

from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class ProposalItem(Base):
    """
    Item de uma proposta.

    Representa um produto ou servico incluido
    na proposta comercial.
    """

    __tablename__ = "proposal_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    proposal_id = Column(
        UUID(as_uuid=True),
        ForeignKey("proposals.id"),
        nullable=False
    )

    # Referencia ao produto/servico
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=True)

    # Descricao
    description = Column(String(500), nullable=False)
    details = Column(Text, nullable=True)

    # Quantidades
    quantity = Column(Integer, default=1, nullable=False)
    unit = Column(String(20), default="un")

    # Valores (SEMPRE Decimal)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=Decimal("0.00"))
    total = Column(Numeric(15, 2), nullable=False)

    # CCT do item
    cct_value = Column(Numeric(15, 2), default=Decimal("0.00"))
    headcount = Column(Integer, default=0)

    # Impostos
    tax_rate = Column(Numeric(5, 2), default=Decimal("0.00"))
    tax_amount = Column(Numeric(15, 2), default=Decimal("0.00"))

    # Ordem
    sort_order = Column(Integer, default=0)

    # Relationship
    proposal = relationship("Proposal", back_populates="items")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<ProposalItem(id={self.id}, description='{self.description[:30]}...')>"

    def calculate_total(self) -> None:
        """Calcula total do item."""
        base = self.unit_price * self.quantity
        discount = base * (self.discount_percent / 100)
        self.total = base - discount + self.tax_amount
```

---

## DIA 3-4: PRICING ENGINE

### Tarefa 3.1: Motor de Precificacao

```python
# modules/crm/services/pricing_engine.py
"""Motor de Precificacao para Propostas."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from core.logging import logger


@dataclass
class PricingInput:
    """Dados de entrada para precificacao."""

    base_salary: Decimal
    headcount: int
    contract_months: int
    service_type: str
    client_state: str
    margin_target: Decimal
    benefits_value: Decimal = Decimal("0.00")
    equipment_value: Decimal = Decimal("0.00")


@dataclass
class PricingResult:
    """Resultado do calculo de preco."""

    base_cost: Decimal
    cct_value: Decimal
    cct_percent: Decimal
    labor_cost: Decimal
    benefits_cost: Decimal
    equipment_cost: Decimal
    total_cost: Decimal
    tax_amount: Decimal
    tax_breakdown: dict[str, Decimal]
    margin_value: Decimal
    margin_percent: Decimal
    unit_price: Decimal
    total_monthly: Decimal
    total_contract: Decimal


class PricingEngine:
    """
    Motor de precificacao com calculo de CCT.

    Calcula custos trabalhistas, impostos e margem
    para formacao de preco de venda.
    """

    # Encargos trabalhistas (CCT)
    CCT_COMPONENTS = {
        "inss_empresa": Decimal("0.20"),
        "fgts": Decimal("0.08"),
        "sat_rat": Decimal("0.03"),
        "terceiros": Decimal("0.058"),
        "ferias": Decimal("0.1111"),
        "ferias_terco": Decimal("0.0370"),
        "decimo_terceiro": Decimal("0.0833"),
        "aviso_previo": Decimal("0.0417"),
        "multa_fgts": Decimal("0.04"),
        "provisao_rescisao": Decimal("0.05"),
    }

    # Impostos por tipo de servico
    TAX_RATES = {
        "default": {
            "iss": Decimal("0.05"),
            "pis": Decimal("0.0065"),
            "cofins": Decimal("0.03"),
            "irpj": Decimal("0.048"),
            "csll": Decimal("0.0288"),
        },
        "vigilancia": {
            "iss": Decimal("0.05"),
            "pis": Decimal("0.0065"),
            "cofins": Decimal("0.03"),
            "irpj": Decimal("0.048"),
            "csll": Decimal("0.0288"),
        },
        "limpeza": {
            "iss": Decimal("0.02"),
            "pis": Decimal("0.0065"),
            "cofins": Decimal("0.03"),
            "irpj": Decimal("0.048"),
            "csll": Decimal("0.0288"),
        },
    }

    def calculate(self, pricing_input: PricingInput) -> PricingResult:
        """
        Calcula preco completo com todos os componentes.

        Args:
            pricing_input: Dados de entrada

        Returns:
            PricingResult com todos os valores calculados

        Raises:
            ValueError: Se dados de entrada invalidos
        """
        self._validate_input(pricing_input)

        # 1. Custo base de salarios
        base_cost = (
            pricing_input.base_salary *
            pricing_input.headcount *
            pricing_input.contract_months
        )

        # 2. Calcular CCT
        cct_percent = self._calculate_cct_percent()
        cct_value = base_cost * cct_percent

        # 3. Custo de mao de obra
        labor_cost = base_cost + cct_value

        # 4. Custos adicionais
        benefits_cost = (
            pricing_input.benefits_value *
            pricing_input.headcount *
            pricing_input.contract_months
        )
        equipment_cost = pricing_input.equipment_value

        # 5. Custo total
        total_cost = labor_cost + benefits_cost + equipment_cost

        # 6. Margem
        margin_value = total_cost * (pricing_input.margin_target / 100)

        # 7. Preco antes de impostos
        price_before_tax = total_cost + margin_value

        # 8. Calcular impostos "por dentro"
        taxes = self._get_tax_rates(pricing_input.service_type)
        total_tax_rate = sum(taxes.values())

        # Preco final = preco_antes / (1 - taxa)
        total_contract = price_before_tax / (1 - total_tax_rate)
        tax_amount = total_contract - price_before_tax

        # 9. Breakdown de impostos
        tax_breakdown = {
            name: self._round(total_contract * rate)
            for name, rate in taxes.items()
        }

        # 10. Valores mensais e unitarios
        total_monthly = total_contract / pricing_input.contract_months
        unit_price = total_monthly / pricing_input.headcount

        # 11. Margem efetiva
        effective_margin = (
            (total_contract - total_cost - tax_amount) /
            total_contract * 100
        )

        logger.info(
            "Precificacao calculada",
            extra={
                "headcount": pricing_input.headcount,
                "months": pricing_input.contract_months,
                "total": str(total_contract),
                "margin": str(effective_margin),
            }
        )

        return PricingResult(
            base_cost=self._round(base_cost),
            cct_value=self._round(cct_value),
            cct_percent=self._round(cct_percent * 100),
            labor_cost=self._round(labor_cost),
            benefits_cost=self._round(benefits_cost),
            equipment_cost=self._round(equipment_cost),
            total_cost=self._round(total_cost),
            tax_amount=self._round(tax_amount),
            tax_breakdown=tax_breakdown,
            margin_value=self._round(margin_value),
            margin_percent=self._round(effective_margin),
            unit_price=self._round(unit_price),
            total_monthly=self._round(total_monthly),
            total_contract=self._round(total_contract),
        )

    def _validate_input(self, data: PricingInput) -> None:
        """Valida dados de entrada."""
        if data.base_salary <= 0:
            raise ValueError("Salario base deve ser positivo")
        if data.headcount <= 0:
            raise ValueError("Headcount deve ser positivo")
        if data.contract_months <= 0:
            raise ValueError("Meses de contrato deve ser positivo")
        if data.margin_target < 0:
            raise ValueError("Margem nao pode ser negativa")

    def _calculate_cct_percent(self) -> Decimal:
        """Calcula percentual total de CCT."""
        return sum(self.CCT_COMPONENTS.values())

    def _get_tax_rates(self, service_type: str) -> dict[str, Decimal]:
        """Retorna taxas de impostos do servico."""
        return self.TAX_RATES.get(service_type, self.TAX_RATES["default"])

    def _round(self, value: Decimal) -> Decimal:
        """Arredonda para 2 casas decimais."""
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# Instancia global
pricing_engine = PricingEngine()
```

---

## DIA 5-6: SCHEMAS E REPOSITORY

### Tarefa 5.1: Schemas

```python
# modules/crm/schemas/proposal.py
"""Schemas Pydantic para Propostas."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ProposalItemBase(BaseModel):
    """Schema base de item."""

    description: str = Field(..., min_length=1, max_length=500)
    details: Optional[str] = Field(None, max_length=2000)
    quantity: int = Field(1, ge=1)
    unit: str = Field("un", max_length=20)
    unit_price: Decimal = Field(..., ge=0)
    discount_percent: Decimal = Field(Decimal("0"), ge=0, le=100)
    headcount: int = Field(0, ge=0)

    @field_validator("unit_price", "discount_percent", mode="before")
    @classmethod
    def convert_to_decimal(cls, value: any) -> Decimal:
        """Converte para Decimal."""
        if isinstance(value, float):
            value = Decimal(str(value))
        if isinstance(value, str):
            value = Decimal(value)
        return value


class ProposalItemCreate(ProposalItemBase):
    """Schema para criar item."""

    product_id: Optional[UUID] = None
    service_id: Optional[UUID] = None


class ProposalItemResponse(ProposalItemBase):
    """Schema de resposta do item."""

    id: UUID
    proposal_id: UUID
    total: Decimal
    cct_value: Decimal
    tax_amount: Decimal

    model_config = {"from_attributes": True}


class ProposalBase(BaseModel):
    """Schema base de proposta."""

    opportunity_id: UUID
    client_id: UUID
    valid_until: date
    introduction: Optional[str] = Field(None, max_length=5000)
    terms: Optional[str] = Field(None, max_length=10000)
    notes: Optional[str] = Field(None, max_length=2000)
    discount_percent: Decimal = Field(Decimal("0"), ge=0, le=100)


class ProposalCreate(ProposalBase):
    """Schema para criar proposta."""

    items: list[ProposalItemCreate] = Field(default_factory=list)
    template_id: Optional[UUID] = None


class ProposalUpdate(BaseModel):
    """Schema para atualizar proposta."""

    valid_until: Optional[date] = None
    introduction: Optional[str] = None
    terms: Optional[str] = None
    notes: Optional[str] = None
    discount_percent: Optional[Decimal] = None


class ProposalResponse(ProposalBase):
    """Schema de resposta da proposta."""

    id: UUID
    number: str
    version: int
    status: str
    subtotal: Decimal
    discount_value: Decimal
    tax_amount: Decimal
    total: Decimal
    cct_value: Decimal
    cct_percent: Decimal
    margin_percent: Decimal
    margin_value: Decimal
    salesperson_id: UUID
    sent_at: Optional[datetime]
    accepted_at: Optional[datetime]
    signature_url: Optional[str]
    signed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    items: list[ProposalItemResponse] = []

    model_config = {"from_attributes": True}


class ProposalList(BaseModel):
    """Schema para listagem."""

    items: list[ProposalResponse]
    total: int
    page: int
    page_size: int
    pages: int


class PricingRequest(BaseModel):
    """Schema para calcular preco."""

    base_salary: Decimal = Field(..., gt=0)
    headcount: int = Field(..., gt=0)
    contract_months: int = Field(..., gt=0)
    service_type: str = Field("default")
    client_state: str = Field("SP", max_length=2)
    margin_target: Decimal = Field(Decimal("15"), ge=0)
    benefits_value: Decimal = Field(Decimal("0"), ge=0)
    equipment_value: Decimal = Field(Decimal("0"), ge=0)


class PricingResponse(BaseModel):
    """Schema de resposta do pricing."""

    base_cost: Decimal
    cct_value: Decimal
    cct_percent: Decimal
    labor_cost: Decimal
    benefits_cost: Decimal
    equipment_cost: Decimal
    total_cost: Decimal
    tax_amount: Decimal
    tax_breakdown: dict[str, Decimal]
    margin_value: Decimal
    margin_percent: Decimal
    unit_price: Decimal
    total_monthly: Decimal
    total_contract: Decimal
```

---

## DIA 7-8: CONTROLLER E TESTES

### Tarefa 7.1: Controller

```python
# modules/crm/controllers/proposal_controller.py
"""Controller de Propostas."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from core.logging import logger
from modules.crm.models.proposal import ProposalStatus
from modules.crm.repositories.proposal_repository import ProposalRepository
from modules.crm.schemas.proposal import (
    PricingRequest,
    PricingResponse,
    ProposalCreate,
    ProposalList,
    ProposalResponse,
    ProposalUpdate,
)
from modules.crm.services.pricing_engine import PricingEngine, PricingInput
from modules.crm.services.proposal_service import ProposalService

router = APIRouter(prefix="/proposals", tags=["Propostas"])


@router.get("/", response_model=ProposalList)
async def listar_propostas(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    client_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> ProposalList:
    """
    Lista propostas com filtros e paginacao.

    Args:
        page: Numero da pagina
        page_size: Itens por pagina
        status: Filtro por status
        client_id: Filtro por cliente
        db: Sessao do banco
        current_user: Usuario autenticado

    Returns:
        Lista paginada de propostas
    """
    repo = ProposalRepository(db)
    skip = (page - 1) * page_size

    items, total = repo.get_all(
        skip=skip,
        limit=page_size,
        status=status,
        client_id=client_id
    )

    return ProposalList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def obter_proposta(
    proposal_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> ProposalResponse:
    """
    Obtem proposta por ID.

    Args:
        proposal_id: UUID da proposta
        db: Sessao do banco
        current_user: Usuario autenticado

    Returns:
        Proposta encontrada

    Raises:
        HTTPException: 404 se nao encontrada
    """
    repo = ProposalRepository(db)
    proposal = repo.get_by_id(proposal_id)

    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposta nao encontrada"
        )

    return proposal


@router.post(
    "/",
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED
)
async def criar_proposta(
    data: ProposalCreate,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),
) -> ProposalResponse:
    """
    Cria nova proposta.

    Args:
        data: Dados da proposta
        db: Sessao do banco
        current_user: Usuario autenticado

    Returns:
        Proposta criada
    """
    service = ProposalService(db)
    proposal = service.create_proposal(data, current_user.id)

    logger.info(
        "Proposta criada",
        extra={
            "proposal_id": str(proposal.id),
            "number": proposal.number,
            "user_id": str(current_user.id)
        }
    )

    return proposal


@router.post("/calculate-price", response_model=PricingResponse)
async def calcular_preco(
    data: PricingRequest,
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> PricingResponse:
    """
    Calcula preco com CCT e impostos.

    Args:
        data: Dados para calculo
        current_user: Usuario autenticado

    Returns:
        Resultado do calculo
    """
    engine = PricingEngine()

    pricing_input = PricingInput(
        base_salary=data.base_salary,
        headcount=data.headcount,
        contract_months=data.contract_months,
        service_type=data.service_type,
        client_state=data.client_state,
        margin_target=data.margin_target,
        benefits_value=data.benefits_value,
        equipment_value=data.equipment_value
    )

    result = engine.calculate(pricing_input)

    return PricingResponse(
        base_cost=result.base_cost,
        cct_value=result.cct_value,
        cct_percent=result.cct_percent,
        labor_cost=result.labor_cost,
        benefits_cost=result.benefits_cost,
        equipment_cost=result.equipment_cost,
        total_cost=result.total_cost,
        tax_amount=result.tax_amount,
        tax_breakdown=result.tax_breakdown,
        margin_value=result.margin_value,
        margin_percent=result.margin_percent,
        unit_price=result.unit_price,
        total_monthly=result.total_monthly,
        total_contract=result.total_contract
    )


@router.post("/{proposal_id}/submit")
async def submeter_aprovacao(
    proposal_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),
) -> dict:
    """Submete proposta para aprovacao."""
    service = ProposalService(db)
    service.submit_for_approval(proposal_id, current_user.id)
    return {"message": "Proposta submetida para aprovacao"}


@router.post("/{proposal_id}/approve")
async def aprovar_proposta(
    proposal_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),
) -> dict:
    """Aprova proposta."""
    service = ProposalService(db)
    service.approve(proposal_id, current_user.id)
    return {"message": "Proposta aprovada"}


@router.post("/{proposal_id}/reject")
async def rejeitar_proposta(
    proposal_id: UUID,
    reason: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),
) -> dict:
    """Rejeita proposta."""
    service = ProposalService(db)
    service.reject(proposal_id, current_user.id, reason)
    return {"message": "Proposta rejeitada"}


@router.get("/{proposal_id}/pdf")
async def gerar_pdf(
    proposal_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> dict:
    """Gera PDF da proposta."""
    service = ProposalService(db)
    pdf_url = service.generate_pdf(proposal_id)
    return {"pdf_url": pdf_url}
```

---

## DIA 9-10: TESTES E AUDITORIA

### Tarefa 9.1: Testes do Pricing Engine

```python
# tests/test_pricing_engine.py
"""Testes do Motor de Precificacao."""

from decimal import Decimal

import pytest

from modules.crm.services.pricing_engine import PricingEngine, PricingInput


class TestPricingEngine:
    """Testes do PricingEngine."""

    @pytest.fixture
    def engine(self) -> PricingEngine:
        """Fixture do engine."""
        return PricingEngine()

    @pytest.fixture
    def basic_input(self) -> PricingInput:
        """Input basico para testes."""
        return PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=12,
            service_type="vigilancia",
            client_state="SP",
            margin_target=Decimal("15.00")
        )

    def test_calculate_basic(
        self,
        engine: PricingEngine,
        basic_input: PricingInput
    ) -> None:
        """Testa calculo basico."""
        result = engine.calculate(basic_input)

        assert result.base_cost > 0
        assert result.cct_value > 0
        assert result.total_contract > result.total_cost

    def test_cct_percent_range(self, engine: PricingEngine) -> None:
        """Testa que CCT esta na faixa esperada."""
        cct = engine._calculate_cct_percent()  # pylint: disable=protected-access

        # CCT deve estar entre 70% e 100%
        assert cct >= Decimal("0.70")
        assert cct <= Decimal("1.00")

    def test_margin_applied(
        self,
        engine: PricingEngine,
        basic_input: PricingInput
    ) -> None:
        """Testa que margem e aplicada."""
        result = engine.calculate(basic_input)

        # Margem efetiva deve ser proxima da solicitada
        assert result.margin_percent >= Decimal("10")
        assert result.margin_percent <= Decimal("20")

    def test_decimal_precision(
        self,
        engine: PricingEngine,
        basic_input: PricingInput
    ) -> None:
        """Testa precisao Decimal."""
        result = engine.calculate(basic_input)

        # Todos os valores devem ter 2 casas decimais
        assert str(result.total_contract).count(".") <= 1
        if "." in str(result.total_contract):
            decimals = str(result.total_contract).split(".")[1]
            assert len(decimals) <= 2

    def test_invalid_salary_raises(self, engine: PricingEngine) -> None:
        """Testa erro com salario invalido."""
        invalid_input = PricingInput(
            base_salary=Decimal("-100"),
            headcount=10,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("15")
        )

        with pytest.raises(ValueError, match="Salario base"):
            engine.calculate(invalid_input)

    def test_invalid_headcount_raises(self, engine: PricingEngine) -> None:
        """Testa erro com headcount invalido."""
        invalid_input = PricingInput(
            base_salary=Decimal("2000"),
            headcount=0,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("15")
        )

        with pytest.raises(ValueError, match="Headcount"):
            engine.calculate(invalid_input)

    def test_tax_breakdown_matches_total(
        self,
        engine: PricingEngine,
        basic_input: PricingInput
    ) -> None:
        """Testa que breakdown de impostos bate com total."""
        result = engine.calculate(basic_input)

        breakdown_sum = sum(result.tax_breakdown.values())
        diff = abs(breakdown_sum - result.tax_amount)

        # Diferenca deve ser < R$ 0.10 (erro de arredondamento)
        assert diff < Decimal("0.10")

    def test_different_service_types(self, engine: PricingEngine) -> None:
        """Testa diferentes tipos de servico."""
        base = PricingInput(
            base_salary=Decimal("2000"),
            headcount=10,
            contract_months=12,
            service_type="vigilancia",
            client_state="SP",
            margin_target=Decimal("15")
        )

        result_vig = engine.calculate(base)

        base.service_type = "limpeza"
        result_limp = engine.calculate(base)

        # Limpeza tem ISS menor, deve ter preco final menor
        assert result_limp.total_contract < result_vig.total_contract
```

---

## CHECKLIST FINAL SPRINT 14

- [ ] Model Proposal criado e testado
- [ ] Model ProposalItem criado e testado
- [ ] Model ProposalApproval criado e testado
- [ ] PricingEngine implementado
- [ ] Calculos CCT validados
- [ ] Schemas Pydantic completos
- [ ] Repository com CRUD
- [ ] Controller com todos endpoints
- [ ] Testes unitarios >= 85% cobertura
- [ ] Testes de API funcionando
- [ ] Pylint 100/100 em todos arquivos
- [ ] Mypy sem errors
- [ ] Black formatado
- [ ] Isort ordenado
- [ ] Migracao Alembic criada
- [ ] Documentacao atualizada

---

## APOS CONCLUSAO

```bash
# Executar auditoria final
cd /opt/erp-conecta-mais/backend
source venv/bin/activate

pylint --rcfile=.pylintrc modules/crm/ --score=y
pytest tests/test_proposal*.py tests/test_pricing*.py -v --cov=modules/crm

# Commit
git add .
git commit -m "feat: implementa sistema CPQ de propostas (Sprint 14)

- Adiciona models Proposal, ProposalItem, ProposalApproval
- Implementa PricingEngine com calculo de CCT
- Adiciona endpoints CRUD para propostas
- Implementa workflow de aprovacao
- Cobertura de testes: 87%
- Pylint: 100/100"
```

---

*Sprint 14 - Propostas Premium - ERP Conecta Mais Fase 2*
