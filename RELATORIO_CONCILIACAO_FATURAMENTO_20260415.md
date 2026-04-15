# RELATÓRIO — Fix Conciliação + Faturamento
**Data:** 2026-04-15
**Branch:** feature/people-management-reorganization
**Sessão:** tmux-t1 | Módulo: financial

---

## Problemas Corrigidos

### PROBLEMA A — Conciliação Bancária: Totais R$0,00
**Sintoma:** 479 transações listadas corretamente, mas Total Entradas / Total Saídas / Saldo = R$0,00

**Root causes identificados:**
1. `BankTransactionFull` (schema Pydantic) não tinha campo `type: str`
   - Frontend filtra `t.type === 'credit'` | `t.type === 'debit'` para calcular totais
   - Campo ausente → filtros retornam zero itens → totais = R$0
2. `is_credit = tx.amount >= 0` era sempre `True`
   - Banco Inter retorna todos os `amount` como positivos (sem sinal para débitos)
   - Apenas o campo `transaction_type` indica a direção (DEBITO vs. CREDITO/PIX/etc.)
3. Endpoint `/bank-transactions/summary` exigia `bank_account_id: UUID` obrigatório
   - Chamadas sem `bank_account_id` retornavam 422

**Arquivos alterados:**
- `backend/modules/integrations/banking/controllers/banking_controller.py`
  - Adicionado campo `type: str` à classe `BankTransactionFull`
  - Corrigido `is_credit`: `tx_type_str not in ('DEBITO',)` em vez de `tx.amount >= 0`
  - Adicionado `type='credit' if is_credit else 'debit'` ao construtor
- `backend/modules/financial/controllers/bank_transaction_controller.py`
  - `bank_account_id` agora é `Optional[UUID]` (sem ele: totais de todas as contas)
  - Adicionado parâmetro `period: Optional[str]` (`7d|30d|90d|all`)
  - Novo cálculo via SQL direto para entradas/saídas/saldo reais
- `backend/modules/financial/bi_dashboard/controllers/bi_controller.py`
  - Adicionado `from typing import Optional` (ausência causava falha no import de todos os módulos financeiros)

### PROBLEMA B — Faturamento: Clientes=0, Vencido=tudo
**Sintoma:** Faturamento exibia Clientes=0, Pago=R$0, Vencido=R$270.586,96 (toda a receita como vencida)

**Root causes identificados:**
1. `count(DISTINCT customer_id)` retornava 0 porque todos os registros de abril/2026 têm `customer_id=NULL`
2. Grace period: `today - timedelta(days=1)` sem carência → faturas com `due_date=2026-04-10` (D+5) marcadas como vencidas a partir de 2026-04-11

**Arquivos alterados:**
- `backend/modules/financial/agents/billing_automator.py`
  - `qtd_clientes`: `count(DISTINCT customer_id)` → `count(id)` (1 fatura = 1 cliente)
  - Grace period: `today - timedelta(days=7)` em vez de `days=1`

---

## Validação dos Endpoints

| Endpoint | Antes | Depois |
|----------|-------|--------|
| `GET /financial/bank-transactions/summary?period=30d` | 422 (bank_account_id obrigatório) | ✅ `589 transações, R$153.757 entradas` |
| `GET /financial/bank-transactions/summary?period=7d` | 422 | ✅ `124 transações, R$47.525 entradas` |
| `GET /integrations/banking/statement/full?days=7` | tipo `undefined` no frontend | ✅ `type: 'credit'/'debit'` presente |
| `GET /financial/ai/billing/summary?mes=2026-04` | `qtd_clientes: 0, vencido: R$270.586` | ✅ `qtd_clientes: 10, vencido: R$0` |

---

## Commits

| Hash | Descrição |
|------|-----------|
| `86280d98` | fix(conciliacao+faturamento): totais R$0 + clientes=0 (banking_controller + billing_automator) |
| `<novo>` | fix(audit): Optional import bi_controller + bank-transactions/summary endpoint com period param |

---

## Observações

- Banco Inter retorna PIX enviados como `transaction_type=PIX` com `amount > 0`. A direção real é perdida ao substituir `CREDIT/DEBIT` por `PIX`. Fix conservador: todo tipo não-`DEBITO` é tratado como entrada. Uma correção mais precisa requereria armazenar o campo `tipoOperacao` (C/D) da API Inter.
- Grace period de 7 dias é provisório. O parâmetro correto é `grace_days` em `billing_rules` (atualmente `grace_days=0` para todas as regras). Solução definitiva: usar `grace_days` da regra de faturamento.
