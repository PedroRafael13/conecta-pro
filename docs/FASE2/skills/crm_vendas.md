# SKILL: CRM E VENDAS
## ERP CONECTA MAIS - FASE 2

**Modulo:** CRM & Vendas
**Sprints:** 14 (Propostas Premium)
**Prioridade:** MAXIMA

---

## CONTEXTO DO MODULO

O modulo CRM ja existe na Fase 1 com:
- Leads (model, scoring, nurturing basico)
- Oportunidades
- Contatos
- Empresas

A Fase 2 expande com:
- Sistema CPQ completo (Configure, Price, Quote)
- Pricing Engine com calculo de CCT
- Propostas com templates profissionais
- Assinatura digital
- Pipeline avancado

---

## ENTIDADES A IMPLEMENTAR

### 1. Proposal (Proposta)

```python
# Campos obrigatorios
class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(UUID, primary_key=True, default=uuid4)

    # Identificacao
    number = Column(String(20), unique=True, nullable=False)  # PRO-2026-0001
    version = Column(Integer, default=1)

    # Relacionamentos
    opportunity_id = Column(UUID, ForeignKey("opportunities.id"), nullable=False)
    client_id = Column(UUID, ForeignKey("companies.id"), nullable=False)
    salesperson_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    # Status
    status = Column(Enum(ProposalStatus), default=ProposalStatus.DRAFT)
    # DRAFT, PENDING_APPROVAL, APPROVED, SENT, ACCEPTED, REJECTED, EXPIRED

    # Valores (SEMPRE Decimal)
    subtotal = Column(Numeric(15, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=Decimal("0.00"))
    discount_value = Column(Numeric(15, 2), default=Decimal("0.00"))
    tax_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    total = Column(Numeric(15, 2), nullable=False)

    # CCT (Custo de Contratacao Trabalhista)
    cct_value = Column(Numeric(15, 2), default=Decimal("0.00"))
    cct_percent = Column(Numeric(5, 2), default=Decimal("0.00"))

    # Margem
    margin_percent = Column(Numeric(5, 2), nullable=False)
    margin_value = Column(Numeric(15, 2), nullable=False)

    # Datas
    valid_until = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)

    # Conteudo
    introduction = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Template
    template_id = Column(UUID, ForeignKey("proposal_templates.id"), nullable=True)

    # Assinatura
    signature_url = Column(String(500), nullable=True)
    signed_at = Column(DateTime, nullable=True)
    signed_by = Column(String(200), nullable=True)

    # Relacionamentos
    items = relationship("ProposalItem", back_populates="proposal")
    approvals = relationship("ProposalApproval", back_populates="proposal")
    history = relationship("ProposalHistory", back_populates="proposal")
```

### 2. ProposalItem (Item da Proposta)

```python
class ProposalItem(Base):
    __tablename__ = "proposal_items"

    id = Column(UUID, primary_key=True, default=uuid4)
    proposal_id = Column(UUID, ForeignKey("proposals.id"), nullable=False)

    # Produto/Servico
    product_id = Column(UUID, ForeignKey("products.id"), nullable=True)
    service_id = Column(UUID, ForeignKey("services.id"), nullable=True)

    # Descricao
    description = Column(String(500), nullable=False)
    details = Column(Text, nullable=True)

    # Quantidades
    quantity = Column(Integer, default=1)
    unit = Column(String(20), default="un")  # un, hora, mes, m2

    # Valores
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=Decimal("0.00"))
    total = Column(Numeric(15, 2), nullable=False)

    # CCT do item
    cct_value = Column(Numeric(15, 2), default=Decimal("0.00"))
    headcount = Column(Integer, default=0)  # Numero de funcionarios

    # Impostos
    tax_rate = Column(Numeric(5, 2), default=Decimal("0.00"))
    tax_amount = Column(Numeric(15, 2), default=Decimal("0.00"))

    # Ordem
    sort_order = Column(Integer, default=0)
```

### 3. ProposalApproval (Aprovacao)

```python
class ProposalApproval(Base):
    __tablename__ = "proposal_approvals"

    id = Column(UUID, primary_key=True, default=uuid4)
    proposal_id = Column(UUID, ForeignKey("proposals.id"), nullable=False)

    # Aprovador
    approver_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    level = Column(Integer, nullable=False)  # 1, 2, 3...

    # Status
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    # PENDING, APPROVED, REJECTED

    # Datas
    requested_at = Column(DateTime, default=datetime.utcnow)
    decided_at = Column(DateTime, nullable=True)

    # Comentarios
    comments = Column(Text, nullable=True)
```

---

## PRICING ENGINE

### Estrutura do Motor de Precificacao

```python
# modules/crm/services/pricing_engine.py
"""
Motor de Precificacao para Propostas.

Calcula CCT, impostos, margens e preco final.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from dataclasses import dataclass

from core.logging import logger


@dataclass
class PricingInput:
    """Dados de entrada para precificacao."""
    base_salary: Decimal  # Salario base do funcionario
    headcount: int  # Numero de funcionarios
    contract_months: int  # Duracao do contrato
    service_type: str  # Tipo de servico
    client_state: str  # UF do cliente (para impostos)
    margin_target: Decimal  # Margem desejada (%)


@dataclass
class PricingResult:
    """Resultado do calculo de preco."""
    base_cost: Decimal
    cct_value: Decimal
    cct_percent: Decimal
    labor_cost: Decimal
    tax_amount: Decimal
    tax_breakdown: dict
    margin_value: Decimal
    margin_percent: Decimal
    unit_price: Decimal
    total_monthly: Decimal
    total_contract: Decimal


class PricingEngine:
    """Motor de precificacao com calculo de CCT."""

    # Encargos trabalhistas (CCT)
    CCT_COMPONENTS = {
        "inss_empresa": Decimal("0.20"),      # 20%
        "fgts": Decimal("0.08"),               # 8%
        "sat_rat": Decimal("0.03"),            # 1-3% (media 3%)
        "terceiros": Decimal("0.058"),         # 5.8% (Sistema S)
        "ferias": Decimal("0.1111"),           # 1/9
        "ferias_terco": Decimal("0.0370"),     # 1/3 das ferias
        "decimo_terceiro": Decimal("0.0833"),  # 1/12
        "aviso_previo": Decimal("0.0417"),     # 1/24
        "multa_fgts": Decimal("0.04"),         # 40% sobre 8%
        "provisao_rescisao": Decimal("0.05"),  # 5%
    }

    # Impostos por servico
    TAXES = {
        "iss": Decimal("0.05"),      # 2-5% (media 5%)
        "pis": Decimal("0.0065"),    # 0.65%
        "cofins": Decimal("0.03"),   # 3%
        "irpj": Decimal("0.0480"),   # 4.8% (lucro presumido)
        "csll": Decimal("0.0288"),   # 2.88% (lucro presumido)
    }

    def calculate(self, pricing_input: PricingInput) -> PricingResult:
        """
        Calcula preco completo com todos os componentes.

        Args:
            pricing_input: Dados de entrada

        Returns:
            PricingResult com todos os valores calculados
        """
        # 1. Custo base (salario * headcount * meses)
        base_cost = (
            pricing_input.base_salary *
            pricing_input.headcount *
            pricing_input.contract_months
        )

        # 2. Calcular CCT
        cct_percent = self._calculate_cct_percent()
        cct_value = base_cost * cct_percent

        # 3. Custo total de mao de obra
        labor_cost = base_cost + cct_value

        # 4. Calcular margem sobre custo
        margin_value = labor_cost * (pricing_input.margin_target / 100)

        # 5. Preco antes de impostos
        price_before_tax = labor_cost + margin_value

        # 6. Calcular impostos (sobre o preco de venda)
        # Impostos sao calculados "por dentro"
        tax_rate = self._get_total_tax_rate(pricing_input.service_type)
        # Preco final = preco_antes / (1 - taxa_imposto)
        total_contract = price_before_tax / (1 - tax_rate)
        tax_amount = total_contract - price_before_tax

        # 7. Calcular valores mensais e unitarios
        total_monthly = total_contract / pricing_input.contract_months
        unit_price = total_monthly / pricing_input.headcount

        # 8. Recalcular margem efetiva
        effective_margin = (
            (total_contract - labor_cost - tax_amount) / total_contract * 100
        )

        # 9. Breakdown de impostos
        tax_breakdown = self._calculate_tax_breakdown(total_contract)

        logger.info(
            "Precificacao calculada",
            extra={
                "base_cost": str(base_cost),
                "cct_percent": str(cct_percent),
                "total": str(total_contract)
            }
        )

        return PricingResult(
            base_cost=self._round(base_cost),
            cct_value=self._round(cct_value),
            cct_percent=self._round(cct_percent * 100),
            labor_cost=self._round(labor_cost),
            tax_amount=self._round(tax_amount),
            tax_breakdown=tax_breakdown,
            margin_value=self._round(margin_value),
            margin_percent=self._round(effective_margin),
            unit_price=self._round(unit_price),
            total_monthly=self._round(total_monthly),
            total_contract=self._round(total_contract)
        )

    def _calculate_cct_percent(self) -> Decimal:
        """Calcula percentual total de CCT."""
        return sum(self.CCT_COMPONENTS.values())

    def _get_total_tax_rate(self, service_type: str) -> Decimal:
        """Retorna taxa total de impostos."""
        # Pode variar por tipo de servico
        return sum(self.TAXES.values())

    def _calculate_tax_breakdown(self, total: Decimal) -> dict:
        """Calcula cada imposto individualmente."""
        return {
            name: self._round(total * rate)
            for name, rate in self.TAXES.items()
        }

    def _round(self, value: Decimal) -> Decimal:
        """Arredonda para 2 casas decimais."""
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

---

## WORKFLOW DE PROPOSTA

### Estados e Transicoes

```
DRAFT -> PENDING_APPROVAL (submeter para aprovacao)
PENDING_APPROVAL -> APPROVED (todos niveis aprovaram)
PENDING_APPROVAL -> DRAFT (rejeitado, volta para edicao)
APPROVED -> SENT (enviada ao cliente)
SENT -> ACCEPTED (cliente aceitou)
SENT -> REJECTED (cliente rejeitou)
SENT -> EXPIRED (prazo expirou)
```

### Niveis de Aprovacao

```python
# Baseado no valor da proposta
APPROVAL_LEVELS = {
    Decimal("10000"): 1,    # Ate R$ 10k: 1 nivel (gerente)
    Decimal("50000"): 2,    # Ate R$ 50k: 2 niveis (gerente + diretor)
    Decimal("100000"): 3,   # Ate R$ 100k: 3 niveis (+ CEO)
    Decimal("999999999"): 3 # Acima: sempre 3 niveis
}
```

---

## ENDPOINTS A IMPLEMENTAR

### CRUD Basico

```
POST   /api/v1/proposals/           - Criar proposta
GET    /api/v1/proposals/           - Listar propostas
GET    /api/v1/proposals/{id}       - Obter proposta
PATCH  /api/v1/proposals/{id}       - Atualizar proposta
DELETE /api/v1/proposals/{id}       - Remover proposta
```

### Itens

```
POST   /api/v1/proposals/{id}/items      - Adicionar item
GET    /api/v1/proposals/{id}/items      - Listar itens
PATCH  /api/v1/proposals/{id}/items/{item_id}  - Atualizar item
DELETE /api/v1/proposals/{id}/items/{item_id}  - Remover item
```

### Workflow

```
POST   /api/v1/proposals/{id}/submit     - Submeter para aprovacao
POST   /api/v1/proposals/{id}/approve    - Aprovar
POST   /api/v1/proposals/{id}/reject     - Rejeitar
POST   /api/v1/proposals/{id}/send       - Enviar ao cliente
POST   /api/v1/proposals/{id}/clone      - Clonar proposta
```

### Pricing

```
POST   /api/v1/proposals/calculate-price - Calcular preco
GET    /api/v1/proposals/{id}/pricing    - Ver detalhes de preco
```

### PDF

```
GET    /api/v1/proposals/{id}/pdf        - Gerar PDF
GET    /api/v1/proposals/{id}/preview    - Preview HTML
```

---

## TESTES OBRIGATORIOS

### Testes de Pricing

```python
def test_cct_calculation():
    """Testa calculo de CCT."""
    engine = PricingEngine()
    result = engine.calculate(PricingInput(
        base_salary=Decimal("2000.00"),
        headcount=10,
        contract_months=12,
        service_type="vigilancia",
        client_state="SP",
        margin_target=Decimal("15.00")
    ))

    # CCT deve ser aproximadamente 70-80% do salario
    assert result.cct_percent >= Decimal("70")
    assert result.cct_percent <= Decimal("90")


def test_margin_calculation():
    """Testa calculo de margem."""
    # Margem solicitada de 15% deve resultar em margem similar
    assert result.margin_percent >= Decimal("14")
    assert result.margin_percent <= Decimal("16")


def test_decimal_precision():
    """Testa precisao de Decimal."""
    # Nunca pode haver erro de arredondamento
    total_items = sum(item.total for item in proposal.items)
    assert total_items == proposal.subtotal
```

---

## VALIDACOES DE NEGOCIO

1. Proposta deve ter pelo menos 1 item
2. Valor total deve ser > 0
3. Margem minima de 10%
4. Validade minima de 7 dias
5. Aprovador nao pode ser o criador
6. Proposta expirada nao pode ser enviada
7. Proposta aceita nao pode ser alterada

---

## INTEGRACAO COM DOCUSIGN

```python
# Para assinatura digital
class DocuSignService:
    """Integracao com DocuSign para assinatura."""

    def send_for_signature(
        self,
        proposal: Proposal,
        signers: list[dict]
    ) -> str:
        """
        Envia proposta para assinatura.

        Args:
            proposal: Proposta a assinar
            signers: Lista de assinantes

        Returns:
            URL para assinatura
        """
        # Gerar PDF
        pdf_content = self._generate_pdf(proposal)

        # Criar envelope no DocuSign
        envelope = self._create_envelope(pdf_content, signers)

        # Retornar URL
        return envelope.signing_url
```

---

## CHECKLIST DO SPRINT 14

- [ ] Model Proposal criado
- [ ] Model ProposalItem criado
- [ ] Model ProposalApproval criado
- [ ] PricingEngine implementado
- [ ] Calculos CCT validados com contador
- [ ] Endpoints CRUD funcionando
- [ ] Workflow de aprovacao testado
- [ ] Geracao de PDF implementada
- [ ] Testes com cobertura >= 85%
- [ ] Pylint 100/100
- [ ] Documentacao atualizada

---

*Skill CRM e Vendas - ERP Conecta Mais Fase 2*
