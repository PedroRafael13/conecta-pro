# SKILL: FINANCEIRO
## ERP CONECTA MAIS - FASE 2

**Modulo:** Financeiro
**Sprints:** 22-29
**Prioridade:** ALTA

---

## CONTEXTO DO MODULO

Modulo financeiro completo:
- Contas a Pagar (A/P)
- Contas a Receber (A/R)
- Fluxo de Caixa
- DRE e Balanco
- Conciliacao Bancaria
- Open Banking

---

## REGRA DE OURO FINANCEIRO

```
TODOS os valores monetarios DEVEM usar Decimal
NUNCA usar float para dinheiro
SEMPRE arredondar com ROUND_HALF_UP
SEMPRE 2 casas decimais
```

---

## ESTRUTURA DO MODULO

```
modules/financial/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── supplier.py           # Fornecedores
│   ├── payable.py            # Contas a pagar
│   ├── payment.py            # Pagamentos
│   ├── receivable.py         # Contas a receber
│   ├── invoice.py            # Faturas
│   ├── bank_account.py       # Contas bancarias
│   ├── bank_transaction.py   # Transacoes
│   ├── cost_center.py        # Centros de custo
│   ├── chart_account.py      # Plano de contas
│   └── journal_entry.py      # Lancamentos
├── schemas/
│   ├── __init__.py
│   ├── payable.py
│   ├── receivable.py
│   ├── banking.py
│   └── reports.py
├── repositories/
│   ├── __init__.py
│   ├── payable_repository.py
│   ├── receivable_repository.py
│   └── banking_repository.py
├── services/
│   ├── __init__.py
│   ├── payable_service.py
│   ├── receivable_service.py
│   ├── cnab_processor.py     # CNAB 240/400
│   ├── banking_service.py    # Open Banking
│   ├── reconciliation.py     # Conciliacao
│   ├── cashflow_service.py   # Fluxo de caixa
│   ├── dre_service.py        # DRE
│   └── collection_service.py # Cobranca
└── controllers/
    ├── __init__.py
    ├── payable_controller.py
    ├── receivable_controller.py
    ├── banking_controller.py
    └── reports_controller.py
```

---

## SPRINT 22-23: CONTAS A PAGAR

### Payable (Conta a Pagar)

```python
class Payable(Base):
    """Conta a pagar."""
    __tablename__ = "payables"

    id = Column(UUID, primary_key=True, default=uuid4)

    # Identificacao
    document_number = Column(String(50), nullable=False)
    document_type = Column(Enum(DocumentType))
    # INVOICE, BILL, CONTRACT, OTHER

    # Fornecedor
    supplier_id = Column(UUID, ForeignKey("suppliers.id"), nullable=False)
    supplier = relationship("Supplier", back_populates="payables")

    # Categoria
    category_id = Column(UUID, ForeignKey("payment_categories.id"))
    cost_center_id = Column(UUID, ForeignKey("cost_centers.id"))

    # Valores (SEMPRE Decimal)
    original_value = Column(Numeric(15, 2), nullable=False)
    discount = Column(Numeric(15, 2), default=Decimal("0.00"))
    interest = Column(Numeric(15, 2), default=Decimal("0.00"))
    fine = Column(Numeric(15, 2), default=Decimal("0.00"))
    final_value = Column(Numeric(15, 2), nullable=False)
    paid_value = Column(Numeric(15, 2), default=Decimal("0.00"))

    # Datas
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    payment_date = Column(Date, nullable=True)

    # Status
    status = Column(Enum(PayableStatus), default=PayableStatus.PENDING)
    # PENDING, APPROVED, PAID, CANCELLED, OVERDUE

    # Pagamento
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    # PIX, TED, BOLETO, CHEQUE, CASH
    bank_account_id = Column(UUID, ForeignKey("bank_accounts.id"), nullable=True)

    # Aprovacao
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(UUID, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)

    # Recorrencia
    is_recurring = Column(Boolean, default=False)
    recurrence_id = Column(UUID, nullable=True)

    # Anexos
    attachments = Column(JSONB, default=[])

    # Observacoes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID, ForeignKey("users.id"))
```

### CNABProcessor

```python
# modules/financial/services/cnab_processor.py
"""Processador de arquivos CNAB 240 e 400."""

from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from dataclasses import dataclass

from core.logging import logger


@dataclass
class CNABLine:
    """Linha do arquivo CNAB."""
    line_number: int
    content: str
    record_type: str


@dataclass
class PaymentInstruction:
    """Instrucao de pagamento."""
    supplier_name: str
    document: str
    value: Decimal
    due_date: date
    barcode: Optional[str]
    pix_key: Optional[str]
    bank_data: Optional[dict]


class CNABProcessor:
    """Processador CNAB 240."""

    BANK_CODES = {
        "001": "Banco do Brasil",
        "033": "Santander",
        "104": "Caixa",
        "237": "Bradesco",
        "341": "Itau",
        "756": "Sicoob",
    }

    def generate_remessa(
        self,
        payments: list[PaymentInstruction],
        bank_code: str,
        company_data: dict
    ) -> str:
        """
        Gera arquivo de remessa CNAB 240.

        Args:
            payments: Lista de pagamentos
            bank_code: Codigo do banco
            company_data: Dados da empresa

        Returns:
            Conteudo do arquivo CNAB
        """
        lines = []

        # Header do arquivo
        lines.append(self._generate_file_header(bank_code, company_data))

        # Header do lote
        lines.append(self._generate_batch_header(bank_code, company_data))

        # Registros de pagamento
        for i, payment in enumerate(payments, start=1):
            lines.extend(self._generate_payment_records(payment, i))

        # Trailer do lote
        lines.append(self._generate_batch_trailer(len(payments)))

        # Trailer do arquivo
        lines.append(self._generate_file_trailer(len(lines)))

        content = "\r\n".join(lines)

        logger.info(
            "Remessa CNAB gerada",
            extra={
                "bank": bank_code,
                "payments": len(payments),
                "size": len(content)
            }
        )

        return content

    def process_retorno(self, content: str) -> list[dict]:
        """
        Processa arquivo de retorno.

        Args:
            content: Conteudo do arquivo

        Returns:
            Lista de pagamentos processados
        """
        results = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if len(line) < 240:
                continue

            record_type = line[7:8]

            if record_type == "3":  # Detalhe
                segment = line[13:14]
                if segment == "T":  # Segmento T
                    result = self._parse_segment_t(line)
                    results.append(result)

        logger.info(
            "Retorno CNAB processado",
            extra={"records": len(results)}
        )

        return results

    def _generate_file_header(self, bank: str, company: dict) -> str:
        """Gera header do arquivo (registro 0)."""
        line = ""
        line += bank.zfill(3)                    # 1-3: Banco
        line += "0000"                           # 4-7: Lote
        line += "0"                              # 8: Tipo registro
        line += " " * 9                          # 9-17: Uso FEBRABAN
        line += "2"                              # 18: Tipo inscricao (CNPJ)
        line += company["cnpj"].zfill(14)        # 19-32: CNPJ
        line += " " * 20                         # 33-52: Convenio
        line += company["agency"].zfill(5)       # 53-57: Agencia
        line += " "                              # 58: Digito
        line += company["account"].zfill(12)    # 59-70: Conta
        line += " "                              # 71: Digito
        line += " "                              # 72: Digito ag/conta
        line += company["name"][:30].ljust(30)  # 73-102: Nome empresa
        line += self.BANK_CODES[bank][:30].ljust(30)  # 103-132: Nome banco
        line += " " * 10                         # 133-142: Uso FEBRABAN
        line += "1"                              # 143: Codigo remessa
        line += datetime.now().strftime("%d%m%Y")  # 144-151: Data
        line += datetime.now().strftime("%H%M%S")  # 152-157: Hora
        line += "000001"                         # 158-163: NSA
        line += "089"                            # 164-166: Versao layout
        line += "00000"                          # 167-171: Densidade
        line += " " * 69                         # 172-240: Reservado

        return line[:240]

    def _generate_batch_header(self, bank: str, company: dict) -> str:
        """Gera header do lote (registro 1)."""
        # Implementar conforme especificacao do banco
        pass

    def _generate_payment_records(
        self,
        payment: PaymentInstruction,
        seq: int
    ) -> list[str]:
        """Gera registros de detalhe (3)."""
        records = []

        # Segmento A (dados do favorecido)
        records.append(self._generate_segment_a(payment, seq))

        # Segmento B (dados complementares) - opcional
        if payment.pix_key:
            records.append(self._generate_segment_b(payment, seq))

        return records

    def _generate_segment_a(self, payment: PaymentInstruction, seq: int) -> str:
        """Gera segmento A."""
        # Implementar conforme especificacao
        pass

    def _generate_segment_b(self, payment: PaymentInstruction, seq: int) -> str:
        """Gera segmento B."""
        # Implementar conforme especificacao
        pass

    def _generate_batch_trailer(self, count: int) -> str:
        """Gera trailer do lote (registro 5)."""
        pass

    def _generate_file_trailer(self, total_lines: int) -> str:
        """Gera trailer do arquivo (registro 9)."""
        pass

    def _parse_segment_t(self, line: str) -> dict:
        """Parse do segmento T (retorno)."""
        return {
            "document": line[58:73].strip(),
            "value": Decimal(line[119:134]) / 100,
            "status_code": line[15:17],
            "status": self._get_status_description(line[15:17])
        }

    def _get_status_description(self, code: str) -> str:
        """Retorna descricao do status."""
        statuses = {
            "00": "Pagamento efetuado",
            "01": "Insuficiencia de fundos",
            "02": "Conta encerrada",
            "03": "Agencia/conta invalida",
        }
        return statuses.get(code, "Status desconhecido")
```

---

## SPRINT 24-25: CONTAS A RECEBER

### Receivable (Conta a Receber)

```python
class Receivable(Base):
    """Conta a receber."""
    __tablename__ = "receivables"

    id = Column(UUID, primary_key=True, default=uuid4)

    # Identificacao
    document_number = Column(String(50), nullable=False)
    our_number = Column(String(20), unique=True)  # Nosso numero

    # Cliente
    client_id = Column(UUID, ForeignKey("companies.id"), nullable=False)

    # Contrato (opcional)
    contract_id = Column(UUID, ForeignKey("contracts.id"), nullable=True)

    # Valores
    original_value = Column(Numeric(15, 2), nullable=False)
    discount = Column(Numeric(15, 2), default=Decimal("0.00"))
    interest = Column(Numeric(15, 2), default=Decimal("0.00"))
    fine = Column(Numeric(15, 2), default=Decimal("0.00"))
    final_value = Column(Numeric(15, 2), nullable=False)
    received_value = Column(Numeric(15, 2), default=Decimal("0.00"))

    # Datas
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    received_date = Column(Date, nullable=True)

    # Status
    status = Column(Enum(ReceivableStatus), default=ReceivableStatus.PENDING)
    # PENDING, RECEIVED, PARTIAL, OVERDUE, CANCELLED, NEGOTIATED

    # Boleto
    boleto_url = Column(String(500), nullable=True)
    boleto_barcode = Column(String(50), nullable=True)
    boleto_line = Column(String(50), nullable=True)

    # NFSe
    nfse_number = Column(String(20), nullable=True)
    nfse_url = Column(String(500), nullable=True)

    # Cobranca
    collection_attempts = Column(Integer, default=0)
    last_collection_at = Column(DateTime, nullable=True)
    collection_status = Column(Enum(CollectionStatus), nullable=True)
    # NOT_STARTED, IN_PROGRESS, NEGOTIATING, SUCCESS, FAILED

    # Negativacao
    is_negativated = Column(Boolean, default=False)
    negativated_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
```

### CollectionService

```python
# modules/financial/services/collection_service.py
"""Servico de cobranca automatizada."""

from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal

from core.logging import logger
from modules.financial.models.receivable import Receivable


class CollectionService:
    """Servico de cobranca automatizada."""

    # Regua de cobranca (dias antes/depois do vencimento)
    COLLECTION_RULES = [
        {"days": -5, "channel": "email", "template": "reminder_5d"},
        {"days": -3, "channel": "whatsapp", "template": "reminder_3d"},
        {"days": -1, "channel": "whatsapp", "template": "reminder_1d"},
        {"days": 0, "channel": "whatsapp", "template": "due_today"},
        {"days": 1, "channel": "whatsapp", "template": "overdue_1d"},
        {"days": 3, "channel": "email", "template": "overdue_3d"},
        {"days": 7, "channel": "whatsapp", "template": "overdue_7d"},
        {"days": 15, "channel": "phone", "template": "overdue_15d"},
        {"days": 30, "channel": "phone", "template": "overdue_30d"},
        {"days": 45, "channel": "legal", "template": "legal_notice"},
    ]

    async def process_collection(self, receivable: Receivable) -> dict:
        """
        Processa cobranca de um titulo.

        Args:
            receivable: Titulo a cobrar

        Returns:
            Resultado da acao
        """
        today = datetime.now().date()
        days_diff = (today - receivable.due_date).days

        # Encontrar regra aplicavel
        rule = self._find_applicable_rule(days_diff)

        if not rule:
            return {"action": "none", "reason": "No rule applies"}

        # Executar acao
        result = await self._execute_action(receivable, rule)

        # Atualizar receivable
        receivable.collection_attempts += 1
        receivable.last_collection_at = datetime.now()

        logger.info(
            "Cobranca processada",
            extra={
                "receivable_id": str(receivable.id),
                "days_overdue": days_diff,
                "channel": rule["channel"],
                "result": result
            }
        )

        return result

    def _find_applicable_rule(self, days: int) -> Optional[dict]:
        """Encontra regra aplicavel."""
        for rule in self.COLLECTION_RULES:
            if rule["days"] == days:
                return rule
        return None

    async def _execute_action(self, receivable: Receivable, rule: dict) -> dict:
        """Executa acao de cobranca."""
        channel = rule["channel"]

        if channel == "email":
            return await self._send_email(receivable, rule["template"])
        elif channel == "whatsapp":
            return await self._send_whatsapp(receivable, rule["template"])
        elif channel == "phone":
            return await self._schedule_call(receivable)
        elif channel == "legal":
            return await self._initiate_legal(receivable)

        return {"action": channel, "status": "executed"}

    async def _send_email(self, receivable: Receivable, template: str) -> dict:
        """Envia email de cobranca."""
        # Implementar envio de email
        return {"channel": "email", "status": "sent"}

    async def _send_whatsapp(self, receivable: Receivable, template: str) -> dict:
        """Envia WhatsApp de cobranca."""
        # Implementar envio via WhatsApp Business API
        return {"channel": "whatsapp", "status": "sent"}

    async def _schedule_call(self, receivable: Receivable) -> dict:
        """Agenda ligacao de cobranca."""
        # Criar tarefa para telefonema
        return {"channel": "phone", "status": "scheduled"}

    async def _initiate_legal(self, receivable: Receivable) -> dict:
        """Inicia processo de negativacao."""
        # Iniciar negativacao SPC/Serasa
        return {"channel": "legal", "status": "initiated"}

    def calculate_fine_interest(
        self,
        original_value: Decimal,
        due_date: datetime,
        fine_rate: Decimal = Decimal("2.00"),
        daily_interest: Decimal = Decimal("0.033")
    ) -> tuple[Decimal, Decimal, Decimal]:
        """
        Calcula multa e juros.

        Args:
            original_value: Valor original
            due_date: Data de vencimento
            fine_rate: Percentual de multa
            daily_interest: Juros ao dia

        Returns:
            Tupla (multa, juros, total)
        """
        today = datetime.now().date()
        days_overdue = (today - due_date.date()).days

        if days_overdue <= 0:
            return Decimal("0"), Decimal("0"), original_value

        # Multa (fixa)
        fine = original_value * (fine_rate / 100)

        # Juros (proporcional aos dias)
        interest = original_value * (daily_interest / 100) * days_overdue

        total = original_value + fine + interest

        return (
            fine.quantize(Decimal("0.01")),
            interest.quantize(Decimal("0.01")),
            total.quantize(Decimal("0.01"))
        )
```

---

## SPRINT 26: OPEN BANKING

### BankingService

```python
# modules/financial/services/banking_service.py
"""Servico de integracao Open Banking."""

from abc import ABC, abstractmethod
from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from dataclasses import dataclass

from core.logging import logger


@dataclass
class BankBalance:
    """Saldo bancario."""
    available: Decimal
    blocked: Decimal
    total: Decimal
    date: datetime


@dataclass
class BankTransaction:
    """Transacao bancaria."""
    id: str
    date: datetime
    description: str
    value: Decimal
    type: str  # CREDIT, DEBIT
    balance: Decimal


class BankAdapter(ABC):
    """Interface para adapters de banco."""

    @abstractmethod
    async def get_balance(self, account_id: str) -> BankBalance:
        """Obtem saldo da conta."""
        pass

    @abstractmethod
    async def get_transactions(
        self,
        account_id: str,
        start_date: date,
        end_date: date
    ) -> list[BankTransaction]:
        """Obtem extrato."""
        pass

    @abstractmethod
    async def initiate_payment(
        self,
        from_account: str,
        to_data: dict,
        value: Decimal
    ) -> dict:
        """Inicia pagamento."""
        pass


class BancoBrasilAdapter(BankAdapter):
    """Adapter para Banco do Brasil."""

    def __init__(self, client_id: str, client_secret: str) -> None:
        """Inicializa adapter."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.bb.com.br"
        self.token: Optional[str] = None

    async def authenticate(self) -> str:
        """Autentica na API."""
        # Implementar OAuth2
        pass

    async def get_balance(self, account_id: str) -> BankBalance:
        """Obtem saldo."""
        # GET /contas/{id}/saldo
        response = await self._request("GET", f"/contas/{account_id}/saldo")

        return BankBalance(
            available=Decimal(str(response["saldoDisponivel"])),
            blocked=Decimal(str(response["saldoBloqueado"])),
            total=Decimal(str(response["saldoTotal"])),
            date=datetime.now()
        )

    async def get_transactions(
        self,
        account_id: str,
        start_date: date,
        end_date: date
    ) -> list[BankTransaction]:
        """Obtem extrato."""
        response = await self._request(
            "GET",
            f"/contas/{account_id}/extrato",
            params={
                "dataInicio": start_date.isoformat(),
                "dataFim": end_date.isoformat()
            }
        )

        return [
            BankTransaction(
                id=t["id"],
                date=datetime.fromisoformat(t["data"]),
                description=t["descricao"],
                value=Decimal(str(t["valor"])),
                type=t["tipo"],
                balance=Decimal(str(t["saldo"]))
            )
            for t in response["lancamentos"]
        ]

    async def initiate_payment(
        self,
        from_account: str,
        to_data: dict,
        value: Decimal
    ) -> dict:
        """Inicia pagamento."""
        # POST /pagamentos
        pass

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Faz request para API."""
        # Implementar request HTTP
        pass


class BankingService:
    """Servico unificado de banking."""

    def __init__(self) -> None:
        """Inicializa servico."""
        self.adapters: dict[str, BankAdapter] = {}

    def register_adapter(self, bank_code: str, adapter: BankAdapter) -> None:
        """Registra adapter de banco."""
        self.adapters[bank_code] = adapter

    async def get_balance(self, bank_code: str, account_id: str) -> BankBalance:
        """Obtem saldo de qualquer banco."""
        adapter = self._get_adapter(bank_code)
        return await adapter.get_balance(account_id)

    async def get_all_balances(
        self,
        accounts: list[dict]
    ) -> dict[str, BankBalance]:
        """Obtem saldo de todas as contas."""
        balances = {}

        for account in accounts:
            try:
                balance = await self.get_balance(
                    account["bank_code"],
                    account["account_id"]
                )
                balances[account["id"]] = balance
            except Exception as e:
                logger.error(
                    "Erro ao obter saldo",
                    extra={"account": account["id"], "error": str(e)}
                )

        return balances

    def _get_adapter(self, bank_code: str) -> BankAdapter:
        """Obtem adapter do banco."""
        if bank_code not in self.adapters:
            raise ValueError(f"Banco {bank_code} nao configurado")
        return self.adapters[bank_code]
```

---

## SPRINT 27-29: FLUXO E DRE

### CashFlowService

```python
# modules/financial/services/cashflow_service.py
"""Servico de fluxo de caixa."""

from decimal import Decimal
from datetime import date, timedelta
from typing import Optional
from dataclasses import dataclass

from core.logging import logger


@dataclass
class CashFlowPeriod:
    """Periodo do fluxo de caixa."""
    date: date
    opening_balance: Decimal
    total_inflows: Decimal
    total_outflows: Decimal
    net_flow: Decimal
    closing_balance: Decimal
    inflows_detail: list[dict]
    outflows_detail: list[dict]


class CashFlowService:
    """Servico de fluxo de caixa."""

    async def get_cashflow(
        self,
        start_date: date,
        end_date: date,
        include_forecast: bool = True
    ) -> list[CashFlowPeriod]:
        """
        Gera fluxo de caixa.

        Args:
            start_date: Data inicial
            end_date: Data final
            include_forecast: Incluir previsoes

        Returns:
            Lista de periodos
        """
        periods = []
        current_date = start_date
        current_balance = await self._get_opening_balance(start_date)

        while current_date <= end_date:
            # Obter movimentacoes do dia
            inflows = await self._get_inflows(current_date, include_forecast)
            outflows = await self._get_outflows(current_date, include_forecast)

            total_in = sum(i["value"] for i in inflows)
            total_out = sum(o["value"] for o in outflows)
            net = total_in - total_out
            closing = current_balance + net

            periods.append(CashFlowPeriod(
                date=current_date,
                opening_balance=current_balance,
                total_inflows=total_in,
                total_outflows=total_out,
                net_flow=net,
                closing_balance=closing,
                inflows_detail=inflows,
                outflows_detail=outflows
            ))

            current_balance = closing
            current_date += timedelta(days=1)

        return periods

    async def forecast(
        self,
        days: int = 30
    ) -> dict[str, any]:
        """
        Previsao de fluxo com IA.

        Args:
            days: Dias para prever

        Returns:
            Previsao com cenarios
        """
        today = date.today()
        end_date = today + timedelta(days=days)

        # Cenario realista
        realistic = await self.get_cashflow(today, end_date, include_forecast=True)

        # Cenario otimista (+20% receitas, -10% despesas)
        optimistic = self._apply_scenario(realistic, Decimal("1.2"), Decimal("0.9"))

        # Cenario pessimista (-20% receitas, +10% despesas)
        pessimistic = self._apply_scenario(realistic, Decimal("0.8"), Decimal("1.1"))

        return {
            "realistic": realistic,
            "optimistic": optimistic,
            "pessimistic": pessimistic,
            "min_balance": min(p.closing_balance for p in pessimistic),
            "alert": any(p.closing_balance < 0 for p in realistic)
        }

    def _apply_scenario(
        self,
        periods: list[CashFlowPeriod],
        inflow_factor: Decimal,
        outflow_factor: Decimal
    ) -> list[CashFlowPeriod]:
        """Aplica cenario aos periodos."""
        result = []
        balance = periods[0].opening_balance

        for p in periods:
            inflows = p.total_inflows * inflow_factor
            outflows = p.total_outflows * outflow_factor
            net = inflows - outflows
            closing = balance + net

            result.append(CashFlowPeriod(
                date=p.date,
                opening_balance=balance,
                total_inflows=inflows,
                total_outflows=outflows,
                net_flow=net,
                closing_balance=closing,
                inflows_detail=[],
                outflows_detail=[]
            ))

            balance = closing

        return result

    async def _get_opening_balance(self, ref_date: date) -> Decimal:
        """Obtem saldo de abertura."""
        # Somar saldos das contas bancarias
        pass

    async def _get_inflows(
        self,
        ref_date: date,
        include_forecast: bool
    ) -> list[dict]:
        """Obtem entradas do dia."""
        # Buscar recebiveis com vencimento no dia
        pass

    async def _get_outflows(
        self,
        ref_date: date,
        include_forecast: bool
    ) -> list[dict]:
        """Obtem saidas do dia."""
        # Buscar pagaveis com vencimento no dia
        pass
```

### DREService

```python
# modules/financial/services/dre_service.py
"""Servico de DRE (Demonstracao de Resultado)."""

from decimal import Decimal
from datetime import date
from dataclasses import dataclass


@dataclass
class DRELine:
    """Linha da DRE."""
    code: str
    description: str
    value: Decimal
    percent: Decimal
    level: int


class DREService:
    """Servico de DRE."""

    async def generate_dre(
        self,
        start_date: date,
        end_date: date
    ) -> list[DRELine]:
        """
        Gera DRE do periodo.

        Args:
            start_date: Inicio
            end_date: Fim

        Returns:
            Lista de linhas da DRE
        """
        lines = []

        # 1. RECEITA OPERACIONAL BRUTA
        revenue = await self._get_revenue(start_date, end_date)
        lines.append(DRELine(
            code="1",
            description="RECEITA OPERACIONAL BRUTA",
            value=revenue,
            percent=Decimal("100"),
            level=0
        ))

        # 2. (-) DEDUCOES DA RECEITA
        deductions = await self._get_deductions(start_date, end_date)
        lines.append(DRELine(
            code="2",
            description="(-) Deducoes da Receita",
            value=-deductions,
            percent=self._percent(deductions, revenue),
            level=1
        ))

        # 3. (=) RECEITA OPERACIONAL LIQUIDA
        net_revenue = revenue - deductions
        lines.append(DRELine(
            code="3",
            description="(=) RECEITA OPERACIONAL LIQUIDA",
            value=net_revenue,
            percent=self._percent(net_revenue, revenue),
            level=0
        ))

        # 4. (-) CUSTOS DOS SERVICOS
        costs = await self._get_costs(start_date, end_date)
        lines.append(DRELine(
            code="4",
            description="(-) Custos dos Servicos",
            value=-costs,
            percent=self._percent(costs, revenue),
            level=1
        ))

        # 5. (=) LUCRO BRUTO
        gross_profit = net_revenue - costs
        lines.append(DRELine(
            code="5",
            description="(=) LUCRO BRUTO",
            value=gross_profit,
            percent=self._percent(gross_profit, revenue),
            level=0
        ))

        # 6. (-) DESPESAS OPERACIONAIS
        expenses = await self._get_expenses(start_date, end_date)
        lines.append(DRELine(
            code="6",
            description="(-) Despesas Operacionais",
            value=-expenses,
            percent=self._percent(expenses, revenue),
            level=1
        ))

        # 7. (=) RESULTADO OPERACIONAL
        operating_result = gross_profit - expenses
        lines.append(DRELine(
            code="7",
            description="(=) RESULTADO OPERACIONAL",
            value=operating_result,
            percent=self._percent(operating_result, revenue),
            level=0
        ))

        # 8. (+/-) RESULTADO FINANCEIRO
        financial = await self._get_financial_result(start_date, end_date)
        lines.append(DRELine(
            code="8",
            description="(+/-) Resultado Financeiro",
            value=financial,
            percent=self._percent(abs(financial), revenue),
            level=1
        ))

        # 9. (=) RESULTADO ANTES DO IR/CS
        ebt = operating_result + financial
        lines.append(DRELine(
            code="9",
            description="(=) RESULTADO ANTES IR/CS",
            value=ebt,
            percent=self._percent(ebt, revenue),
            level=0
        ))

        # 10. (-) IR/CSLL
        taxes = await self._calculate_taxes(ebt)
        lines.append(DRELine(
            code="10",
            description="(-) IR/CSLL",
            value=-taxes,
            percent=self._percent(taxes, revenue),
            level=1
        ))

        # 11. (=) LUCRO/PREJUIZO LIQUIDO
        net_profit = ebt - taxes
        lines.append(DRELine(
            code="11",
            description="(=) LUCRO/PREJUIZO LIQUIDO",
            value=net_profit,
            percent=self._percent(net_profit, revenue),
            level=0
        ))

        return lines

    def _percent(self, value: Decimal, base: Decimal) -> Decimal:
        """Calcula percentual."""
        if base == 0:
            return Decimal("0")
        return (value / base * 100).quantize(Decimal("0.01"))

    async def _get_revenue(self, start: date, end: date) -> Decimal:
        """Obtem receita bruta."""
        pass

    async def _get_deductions(self, start: date, end: date) -> Decimal:
        """Obtem deducoes (impostos sobre venda)."""
        pass

    async def _get_costs(self, start: date, end: date) -> Decimal:
        """Obtem custos dos servicos."""
        pass

    async def _get_expenses(self, start: date, end: date) -> Decimal:
        """Obtem despesas operacionais."""
        pass

    async def _get_financial_result(self, start: date, end: date) -> Decimal:
        """Obtem resultado financeiro."""
        pass

    async def _calculate_taxes(self, ebt: Decimal) -> Decimal:
        """Calcula IR e CSLL."""
        if ebt <= 0:
            return Decimal("0")

        # IR 15% + adicional 10% sobre excedente
        ir = ebt * Decimal("0.15")
        if ebt > Decimal("20000"):
            ir += (ebt - Decimal("20000")) * Decimal("0.10")

        # CSLL 9%
        csll = ebt * Decimal("0.09")

        return ir + csll
```

---

## CHECKLIST MODULO FINANCEIRO

- [ ] Sprint 22-23: Contas a Pagar
  - [ ] CRUD completo
  - [ ] Aprovacao em niveis
  - [ ] CNAB 240 (remessa)
  - [ ] CNAB retorno
  - [ ] Conciliacao

- [ ] Sprint 24-25: Contas a Receber
  - [ ] CRUD completo
  - [ ] Geracao de boletos
  - [ ] NFSe
  - [ ] Regua de cobranca
  - [ ] WhatsApp cobranca

- [ ] Sprint 26: Open Banking
  - [ ] Adapter BB
  - [ ] Adapter Itau
  - [ ] Saldo tempo real
  - [ ] Extrato

- [ ] Sprint 27-29: Fluxo/DRE
  - [ ] Fluxo de caixa
  - [ ] Previsao IA
  - [ ] DRE automatico
  - [ ] Balancete

---

*Skill Financeiro - ERP Conecta Mais Fase 2*
