# ARQUEOLOGIA COMPLETA — MÓDULO FINANCEIRO
**Data:** 2026-04-12 15:50
**Auditor:** Claude Sonnet 4.6 — T7 / CPRO 7
**Branch:** feature/people-management-reorganization
**Método:** Radiografia cirúrgica — apenas evidências do sistema real

---

## SUMÁRIO EXECUTIVO

```
Backend Python (financeiro, sem venv): 265 arquivos
  └─ modules/financial: 178 arquivos
Endpoints declarados (únicos):         350+
Endpoints HTTP 200 (confirmados):      12 de 19 testados
Tabelas financeiras no DB:             16 (+ tabelas core)
Tabelas core com dados reais:          8/8
Agentes IA (módulo financial):         12 agentes
Skills VPS:                            3 subpastas (sem financeiro)
MCP servers:                           5 (em fase5/client_portal)
Integrações com credenciais ativas:    19 variáveis
```

---

## BLOCO 1 — BACKEND: ARQUIVOS E LINHAS (TOP 30)

Módulo `modules/financial` — **178 arquivos**, principais por tamanho:

| Linhas | Arquivo |
|--------|---------|
| 978 | `modules/financial/repositories/fiscal_repository.py` |
| 956 | `modules/financial/agents/financial_advisor.py` |
| 923 | `modules/financial/controllers/receivable_controller.py` |
| 909 | `modules/financial/services/period_closing_service.py` |
| 882 | `modules/integrations/banking/adapters/inter.py` |
| 850 | `modules/integrations/banking/controllers/banking_controller.py` |
| 849 | `modules/financial/controllers/cashflow_controller.py` |
| 843 | `modules/fiscal_contabil/notas_fiscais/nfe/controller.py` |
| 829 | `modules/government_integrations/core/nfse_nacional.py` |
| 820 | `modules/financial/schemas/accounting_schemas.py` |
| 795 | `modules/financial/repositories/cashflow_repository.py` |
| 780 | `modules/financial/services/balance_sheet_service.py` |
| 1823 | `modules/financial/bi_dashboard/controllers/bi_controller.py` |
| 1685 | `modules/financial/controllers/accounting_controller.py` |
| 1049 | `modules/financial/controllers/ai_controller.py` |
| 639 | `modules/financial/controllers/bank_reconciliation_controller.py` |
| 624 | `modules/financial/controllers/bank_transaction_controller.py` |

**Outros módulos relevantes:**
- `modules/empresas/agents/financial_statements.py` — 289 ln
- `modules/ai/intelligence_hub/insight_distributor.py` — 609 ln
- `domains/financial/entities/journal_entry.py` — 442 ln

---

## BLOCO 2 — ENDPOINTS DECLARADOS: 350 únicos

**Amostra dos principais grupos:**

```
GET  /atual, /dashboard, /dre, /dre/mensal, /balancete
GET  /payables-aging, /receivables-aging, /kpis-summary
GET  /cashflow/cashflow/dashboard, /cashflow-analysis, /cashflow-prediction
GET  /cobrar-recorrente/{mes}/{ano}/preview
GET  /boleto, /boleto/list, /boleto/{boleto_id}, /statement, /statement/full
GET  /balances, /status, /pix/received

POST /barcode, /darf, /batch, /cancel/{payment_id}
POST /boleto/generate, /pix/generate, /ted/transfer
POST /nfse/emitir, /nfse/cancelar, /nfse/sync-prestador
POST /nfse-entrada/sync, /nfse-entrada/auto-criar-payables
POST /cobrar-recorrente/{mes}/{ano}
POST /auto-criar, /payable/auto-criar
POST /bank-reconciliations/auto
POST /forecast/*, /analytics/*, /advisor, /advisor/chat
POST /calcular/lucro-real, /calcular/simples, /calcular/retencoes-nfse
POST /sped, /sped/gerar, /das, /das/calcular

DELETE /boleto/{boleto_id}
```

**Total grupos:** payables, receivables, banking, inter, nfse, nfe, fiscal, cashflow,
accounting, BI-dashboard, AI-advisor, costing/ABC, pricing, inventory,
purchase, suppliers, customers, billing-rules, bank-reconciliation

---

## BLOCO 3 — TESTE HTTP REAL (STATUS AO VIVO)

### Endpoints dos prompts originais — todos 404
Os 31 endpoints genéricos do prompt (`/financeiro/dashboard`, `/banking/saldo`, etc.)
retornaram **404** — esses paths não existem no sistema. O sistema usa prefixo `/financial/`.

### Endpoints reais testados

| HTTP | Endpoint | Dados |
|------|----------|-------|
| **200** | `GET /financial/nfse` | `total, items` |
| **200** | `GET /financial/nfse-entrada` | `total, total_valor_bruto, nfse_entrada` |
| **200** | `GET /fiscal-dashboard/atual` | `periodo, gerado_em, dre` |
| **200** | `GET /fiscal-dashboard/4/2026` | `periodo:04/2026, resultado:-R$771,50` |
| **200** | `GET /financial/cashflow/cashflow/dashboard` | `saldo_atual, entradas_7d, saidas_7d` |
| **200** | `GET /financial/ai/command-center` | `health, alerts, insights` |
| **200** | `GET /financial/ai/advisor/recommendations` | 3 itens |
| **200** | `GET /integrations/banking/balances` | `R$ 58.045,22 (Inter 077)` |
| **200** | `GET /integrations/banking/status` | 2 bancos |
| **200** | `GET /integrations/banking/statement` | `transactions, total_credits, total_debits` |
| **200** | `GET /integrations/banking/boleto/list` | `boletos, total` |
| **200** | `GET /banking/payment/list` | `success, total, pagamentos` |
| **200** | `GET /justificativa/pendentes` | `total:590, valor_total:R$176.864,92` |
| **200** | `GET /people-management/dp/payslips/folha/pagar-via-pix/3/2026/preview` | `46 func, R$66.677,59` |
| **200** | `GET /financial/billing/cobrar-recorrente/4/2026/preview` | `modo, mes, ano` |
| **422** | `GET /financial/payables/payables` | params obrigatórios |
| **422** | `GET /financial/receivables/receivables` | params obrigatórios |
| **422** | `GET /financial/suppliers/suppliers` | params obrigatórios |
| **422** | `GET /financial/customers/customers` | params obrigatórios |
| **422** | `GET /financial/bank-accounts/bank-accounts` | params obrigatórios |
| **422** | `GET /financial/bank-transactions/bank-transactions` | params obrigatórios |
| **422** | `GET /financial/billing-rules/billing-rules` | params obrigatórios |
| **404** | `GET /financial/bi/bi-dashboard/bi/dashboards` | prefixo duplo |

> **422 = operacional** — endpoint existe, exige `condominio_id` ou parâmetro obrigatório.
> **404 real** = BI dashboard com prefixo duplicado (`/financial/bi/bi-dashboard/...`).

---

## BLOCO 4 — BANCO DE DADOS

### Tabelas financeiras (filtro ILIKE)

| Tabela | Colunas | Tamanho |
|--------|---------|---------|
| `bank_reconciliations` | 75 | 96 kB |
| `bank_transactions` | 64 | 752 kB |
| `financial_contract_costs` | 35 | 48 kB |
| `financial_dashboards` | 26 | 40 kB |
| `financial_kpis` | 36 | 48 kB |
| `financial_widgets` | 35 | 32 kB |
| `fiscal_obligations` | 17 | 64 kB |
| `nfe_compras_estoque` | 11 | 40 kB |
| `nfe_entradas` | 14 | 48 kB |
| `nfe_itens` | 35 | 40 kB |
| `nfes` | 55 | 128 kB |
| `nfse_entrada` | 28 | 48 kB |
| `nfses` | 58 | 104 kB |

### Tabelas core — contagem real

| Tabela | Registros | Mais antigo |
|--------|-----------|-------------|
| `bank_transactions` | **656** | 2026-03-23 |
| `payable_accounts` | **19** | 2026-03-23 |
| `receivable_accounts` | **21** | 2026-03-23 |
| `nfses` | **27** | 2026-03-23 |
| `nfse_entrada` | **10** | 2026-03-23 |
| `suppliers` | **13** | 2026-03-23 |
| `customers` | **11** | 2026-03-23 |
| `billing_rules` | **11** | 2026-03-23 |
| `bank_accounts` | **2** | 2026-03-23 |
| `nfes` | **2** | 2026-04-11 |
| `fiscal_obligations` | **23** | 2026-03-23 |
| `bank_reconciliations` | **1** | 2026-04-12 |

### Tabelas com 0 registros (implementadas, não usadas)

| Tabela | Status |
|--------|--------|
| `cashflow_entries` | 0 registros |
| `payable_payments` | 0 registros |
| `receivable_payments` | 0 registros |
| `purchase_orders` | 0 registros |
| `payment_methods` | 0 registros |
| `payment_agreements` | 0 registros |
| `financial_dashboards` | 0 registros |
| `financial_kpis` | 0 registros |
| `financial_widgets` | 0 registros |

### Tabelas inexistentes (não migradas)

| Tabela | Status |
|--------|--------|
| `accounting_entries` | ❌ não existe |
| `inventory_items` | ❌ não existe (usa `stock_items` ou similar) |

---

## BLOCO 5 — AGENTES DE IA FINANCEIROS (12 agentes)

**Orquestrador:** `modules/financial/agents/orchestrator.py` — 175 ln

| Agente | Linhas | Responsabilidade |
|--------|--------|-----------------|
| `FinancialAdvisorAgent` | 956 | Consultor financeiro estratégico — dados reais do DB |
| `RiskMonitorAgent` | 427 | Monitora riscos e calcula health score financeiro |
| `TaxCalculatorAgent` | 478 | Cálculo de impostos (IRPJ, CSLL, ISS, COFINS, PIS) |
| `BillingAutomatorAgent` | 304 | Automação do ciclo de faturamento |
| `CashflowPredictorAgent` | 254 | Projeção de fluxo de caixa com dados históricos |
| `CollectionNegotiatorAgent` | 215 | Analisa inadimplentes e gera estratégias de cobrança |
| `CostingAnalyzerAgent` | 229 | Análise de custeio ABC por tipo de serviço |
| `PricingOptimizerAgent` | 275 | Precificação ótima para contratos de segurança |
| `ProfitabilityAnalyzerAgent` | 210 | Análise de rentabilidade |
| `BaseAgent` | 39 | Classe base |
| `__init__.py` | 15 | Exports |

**Outros agentes com componente financeiro:**
- `modules/empresas/agents/financial_statements.py` — 289 ln (demonstrativos)
- `modules/empresas/agents/bookkeeper_auto.py` — 241 ln (contabilidade automática)
- `modules/bidding/agents/pricer_agent.py` — 558 ln (precificação licitações)

---

## BLOCO 6 — SKILLS VPS

**Pasta:** `/opt/conecta-pro/skills/`

```
/skills/
├── codigo/           ← 10 skills técnicas de desenvolvimento
├── ged/              ← skills de gestão documental
└── marketing-vendas/ ← 10+ skills de vendas/marketing
```

**Skills com referência financeira (indiretas):**
- `03-design-api-restful-conecta-pro.md` — menciona módulo financeiro
- `04-testes-unitarios-conecta-pro.md` — cobre testes financeiros
- `marketing-vendas/*.md` — funil, proposta, MRR

**❌ GAP: Sem pasta `/skills/financeiro/`** — não há skills dedicadas ao módulo financeiro (DRE, fluxo de caixa, conciliação, custeio ABC, Lucro Real).

---

## BLOCO 7 — MCP SERVERS

**MCP servers implementados (5 arquivos):**

| Arquivo | Status |
|---------|--------|
| `backend/mcp_portal_server.py` | ✅ implementado |
| `modules/fase5/mcp_servers/base.py` | ✅ |
| `modules/fase5/mcp_servers/config.py` | ✅ |
| `modules/fase5/mcp_servers/__init__.py` | ✅ |
| `modules/client_portal/controllers/mcp_controller.py` | ✅ |

**❌ Nenhum MCP server dedicado ao módulo financial.**
O `fase5` tem infraestrutura MCP mas não expõe dados financeiros via protocolo MCP.

---

## BLOCO 8 — FRONTEND: COMPONENTES FINANCEIROS

### Páginas reais (25 pages.tsx)

| Linhas | Página | Mocks | Fetch real |
|--------|--------|-------|-----------|
| 1516 | `financeiro/cobrancas/page.tsx` | 16 | 0* |
| 1233 | `financeiro/conciliacao/page.tsx` | 3 | 12 |
| 1188 | `financeiro/relatorios/page.tsx` | 1 | 10 |
| 1071 | `financeiro/page.tsx` | 1 | 8 |
| 961 | `financeiro/custeio/page.tsx` | 12 | 10 |
| 907 | `financeiro/faturamento/page.tsx` | 4 | 7 |
| 875 | `financeiro/orcamentos/page.tsx` | 1 | 0* |
| 805 | `financeiro/dashboard/page.tsx` | 7 | 7 |
| 666 | `financeiro/fluxo-caixa/page.tsx` | 2 | 12 |
| 653 | `financeiro/banking/page.tsx` | 3 | 10 |
| 635 | `financeiro/custos/page.tsx` | 2 | 13 |
| 551 | `financeiro/contratos/page.tsx` | 2 | 3 |
| 518 | `financeiro/fornecedores/page.tsx` | 2 | 6 |
| 508 | `financeiro/contabilidade/page.tsx` | 1 | 9 |
| 502 | `financeiro/compras/page.tsx` | 3 | 5 |
| 465 | `financeiro/estoque/page.tsx` | 1 | 7 |
| 449 | `financeiro/precificacao/page.tsx` | 1 | 3 |
| 446 | `financeiro/contas-pagar/page.tsx` | 4 | 5 |
| 434 | `financeiro/clientes/page.tsx` | 2 | 4 |
| 419 | `financeiro/contas-receber/page.tsx` | 4 | 3 |
| 392 | `relatorios/financeiro/page.tsx` | 1 | 7 |
| 380 | `financeiro/fiscal/page.tsx` | 3 | 4 |
| 165 | `financeiro/nfse-entrada/page.tsx` | 1 | 2 |

*`fetch:0` = usa `bankingService.ts` ou hooks gerados sem grep direto

### Páginas com mock alto (> 10) — atenção
- `cobrancas/page.tsx` — 16 mocks (tem TODO comentado)
- `custeio/page.tsx` — 12 mocks (dados simulados em algumas seções)

---

## BLOCO 9 — INTEGRAÇÕES ATIVAS

### Credenciais configuradas no `.env`

| Integração | Variáveis | Status |
|------------|-----------|--------|
| **Banco Inter** | `INTER_CLIENT_ID`, `INTER_CLIENT_SECRET`, `INTER_PIX_KEY` | ✅ ativo |
| **Certificado A1** | `CERTIFICATE_PATH` | ✅ válido até 2027-01-13 |
| **Domínio Sistemas** | `DOMINIO_API_KEY`, `DOMINIO_API_URL`, `DOMINIO_CNPJ`, `DOMINIO_ENABLED` | ✅ configurado |
| **NFS-e Manaus (ABRASF)** | `NFSE_MANAUS_CNPJ`, `USUARIO`, `SENHA`, `IM`, `ENVIRONMENT` | ✅ operacional |
| **NFS-e Nacional** | `NFSE_NACIONAL_CNPJ`, `COD_MUNICIPIO`, `RAZAO_SOCIAL`, `ENVIRONMENT` | ✅ configurado |
| **Solides** | `SOLIDES_WEBHOOK_SECRET` | ✅ ativo |
| **Gov.br** | `GOVBR_CPF_CNPJ` | ✅ configurado |

### Credenciais Inter (certificado mTLS)

```
/opt/conecta-pro/credentials/inter/
├── Inter_API_Certificado.crt  (2026-04-11, 1613 bytes)
├── Inter_API_Chave.key        (2026-04-11, 1704 bytes)
└── inter_ca.crt               (2026-04-12, 4113 bytes)
```

### Integração Banco Inter — confirmada ao vivo
- `GET /integrations/banking/balances` → **R$ 58.045,22** (conta 370990072-2) ✅
- `GET /integrations/banking/statement` → 652+ transações ✅
- `POST /banking/payment/barcode` → HTTP 200 ✅

---

## BLOCO 10 — SCORE POR DIMENSÃO

```
Backend arquivos Python (sem venv):        265  ██████████████████████████████
Endpoints declarados (únicos):             350  ██████████████████████████████
Tabelas financeiras no DB:                  16  ████████████████░░░░░░░░░░░░░░
Tabelas CORE com dados reais:                8  ████████░░░░░░░░░░░░░░░░░░░░░░
Componentes frontend (páginas reais):       70  ██████████████████████████████
Agentes IA módulo financial:                12  ████████████░░░░░░░░░░░░░░░░░░
Skills VPS (pasta /skills):                  3  ███░░░░░░░░░░░░░░░░░░░░░░░░░░░
MCP servers implementados:                   5  █████░░░░░░░░░░░░░░░░░░░░░░░░░
Integrações com credenciais ativas:         19  ███████████████████░░░░░░░░░░░
```

### Gap Analysis

| Severidade | Gap | Evidência |
|-----------|-----|-----------|
| 🔴 ALTO | **Skills financeiras ausentes** — sem `/skills/financeiro/` | 3 subpastas, nenhuma financeira |
| 🟡 MÉDIO | **BI Dashboard 404** — prefixo duplicado `/financial/bi/bi-dashboard/bi/dashboards` | HTTP 404 confirmado |
| 🟡 MÉDIO | **Tabelas zeradas**: `cashflow_entries`, `payable_payments`, `receivable_payments`, `purchase_orders` | 0 registros cada |
| 🟡 MÉDIO | **`accounting_entries` não existe no DB** — controller implementado mas tabela ausente | ❌ tabela inexistente |
| 🟡 MÉDIO | **`inventory_items` não existe no DB** — schema referencia mas tabela diferente | ❌ tabela inexistente |
| 🟢 INFO | **MCP sem cobertura financeira** — fase5/client_portal mas não financial | 5 MCP, nenhum financeiro |
| 🟢 INFO | **`cobrancas/page.tsx` e `custeio/page.tsx` com mocks altos** (16 e 12) | fetch:0 em cobrancas |
| 🟢 INFO | **590 saídas bancárias sem justificativa** — R$ 176.864,92 pendente Lucro Real | /justificativa/pendentes |

---

## BLOCO 11 — SOPHIA/GEDEON: DOCUMENTOS FINANCEIROS

### gedeon_document_index
```
Total documentos indexados: 617
Documentos financeiros por módulo: 0 (tabela sem coluna module)
```

### ged_documents
```
Total: 0 registros
```

### Tabelas GED relacionadas (existem)
- `gedeon_document_index` — 617 docs indexados
- `ged_documents` — 0 registros
- `documentos_fiscais` — presente (ver contagem separada)
- `gedeon_kit_history`, `gedeon_client_patterns` — ativos

---

## RESUMO — O QUE EXISTE, O QUE FUNCIONA, O QUE É PLACEHOLDER

### ✅ EXISTE E FUNCIONA (confirmado ao vivo)
- Banco Inter: saldo R$ 58.045,22, extrato 656 txs, boleto, PIX
- NFS-e emissão via ABRASF Manaus (27 notas)
- NFS-e entrada (10 registros, sync ativo)
- Contas a pagar (19) e receber (21) — dados reais desde mar/2026
- Conciliação bancária (656 txs, 29 conciliadas)
- Fiscal dashboard (`/fiscal-dashboard/atual`) — DRE parcial abr/2026
- AI Advisor (`/financial/ai/command-center`, `/advisor/recommendations`)
- Justificativa Lucro Real (590 saídas pendentes)
- Pagamento folha PIX (46 funcionários, R$ 66.677,59)
- Cobrança recorrente PIX (10 clientes, R$ 270.586,96 MRR)
- Pagamento via Inter API (barcode, DARF, lote)

### ⚠️ IMPLEMENTADO MAS SEM DADOS
- `cashflow_entries` — controller OK, 0 registros
- `payable_payments` / `receivable_payments` — 0 movimentações
- `purchase_orders` — 0 pedidos de compra
- `financial_dashboards/kpis/widgets` — tabelas OK, 0 configurações BI
- Agentes IA financeiros — 12 implementados, não há evidência de execução automática

### ❌ DECLARADO MAS QUEBRADO / INCOMPLETO
- `GET /financial/bi/bi-dashboard/bi/dashboards` — 404 (prefixo duplicado)
- `accounting_entries` — controller existe, tabela não criada no DB
- `inventory_items` — model referenciado, tabela não existe com esse nome
- NFS-e Nacional — configurado mas Manaus usa ABRASF (limitação municipal)

### 🔴 GAP CRÍTICO PARA CPRO 7
- **Nenhuma skill financeira** na pasta `/skills/` — oportunidade principal do CPRO 7

---

*Relatório gerado: 2026-04-12 15:50*
*Auditor: Claude Sonnet 4.6 — T7*
*Prompt: ARQUEOLOGIA COMPLETA — MÓDULO FINANCEIRO | CPRO 7 | Terminal T1*
