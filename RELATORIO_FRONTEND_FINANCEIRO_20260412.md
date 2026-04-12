# Relatório — Frontend Financeiro: Mapeamento Completo
**Data:** 2026-04-12
**Auditor:** Claude Sonnet 4.6 — T7
**Branch:** feature/people-management-reorganization
**Método:** Análise estática de código — sem execução

---

## Resumo Executivo

```
Páginas financeiro:         23 pages.tsx mapeadas
Subpáginas:                 22 subpáginas em /financeiro/
Hooks:                      483 endpoints cobertos via useFinancial.ts
Submódulos de tipos:        17 tipos gerados (financial-*)
Serviço banking:            8 funções — Inter API
Maior página:               cobrancas/page.tsx (1.519 linhas)
```

---

## 1. Estrutura de Páginas — Módulo Financeiro

| Página | Linhas | Responsabilidade |
|--------|--------|-----------------|
| `cobrancas/page.tsx` | **1.519** | Emissão boleto + cobrança PIX Inter |
| `conciliacao/page.tsx` | **1.206** | Conciliação bancária + extrato + OFX |
| `relatorios/page.tsx` | **1.188** | DRE, cashflow, projeção, AI advisor |
| `page.tsx` (raiz) | **1.066** | Landing do módulo financeiro |
| `custeio/page.tsx` | **961** | Custeio ABC |
| `faturamento/page.tsx` | **907** | Regras de faturamento + billing rules |
| `orcamentos/page.tsx` | **875** | Orçamentos |
| `boletos/page.tsx` | **672** | Lista de boletos emitidos |
| `fluxo-caixa/page.tsx` | **666** | Cashflow + projeções |
| `banking/page.tsx` | **653** | Saldo Inter, extrato, boleto, PIX, DARF |
| `custos/page.tsx` | **635** | Gestão de custos |
| `dashboard/page.tsx` | **615** | Dashboard NFS-e + saldo bancário |
| `contratos/page.tsx` | **551** | Contratos financeiros |
| `fornecedores/page.tsx` | **518** | Fornecedores + qualificação |
| `contabilidade/page.tsx` | **508** | Lançamentos contábeis |
| `compras/page.tsx` | **502** | Requisições + ordens de compra |
| `estoque/page.tsx` | **465** | Itens + armazéns + saldo estoque |
| `precificacao/page.tsx` | **449** | Precificação de serviços |
| `contas-pagar/page.tsx` | **445** | Contas a pagar + dashboard AP |
| `clientes/page.tsx` | **434** | Clientes financeiros |
| `contas-receber/page.tsx` | **419** | Contas a receber + recebimento |
| `fiscal/page.tsx` | **380** | Painel fiscal integrado |
| `nfse-entrada/page.tsx` | **165** | NFS-e de entrada |

**Total estimado:** ~16.000 linhas de frontend financeiro

---

## 2. Arquitetura de Dados — Hooks e Serviços

### Camada de hooks (`/hooks/financial/useFinancial.ts`)

Arquivo central que consolida **483 endpoints** em 17 submódulos gerados automaticamente:

| Submódulo | Hook(s) principal(is) |
|-----------|----------------------|
| `financial-payables` | `usePayables`, `usePayableDashboard`, `useCreatePayable`, `useUpdatePayable`, `useProcessPayment` |
| `financial-receivables` | `useReceivables`, `useReceivableDashboard`, `useCreateReceivable` |
| `financial-bank-accounts` | `useBankAccounts`, `useCreateBankAccount` |
| `financial-bank-transactions` | `useBankTransactions`, `useImportOFX` |
| `financial-cashflow` | `useCashflow` |
| `financial-purchase` | `usePurchaseRequisitions`, `usePurchaseOrders` |
| `financial-inventory` | `useInventoryItems`, `useWarehouses`, `useStockBalance` |
| `financial-accounting` | hooks de lançamentos contábeis |
| `financial-fiscal` | hooks fiscais integrados |
| `financial-bi-dashboard` | hooks BI financeiro |
| `financial-billing-rules` | `useBillingRules`, `useCreateBillingRule`, `useActivateBillingRule` |
| `financial-abc-costing` | hooks custeio ABC |
| `financial-customers` | hooks clientes financeiros |
| `financial-suppliers` | hooks fornecedores |
| `financial-receivable-categories` | hooks categorias |
| `financial-bank-reconciliation` | hooks conciliação |

### Serviço banking (`/services/banking/bankingService.ts`)

| Função | Endpoint Backend | Usado em |
|--------|-----------------|----------|
| `fetchBankBalances()` | `GET /api/v1/integrations/banking/balances` | `dashboard/`, `conciliacao/` |
| `fetchBankStatement()` | `GET /api/v1/integrations/banking/statement` | `conciliacao/` |
| `fetchBankStatementFull()` | `GET /api/v1/integrations/banking/statement/full` | `conciliacao/` |
| `fetchBankStatus()` | `GET /api/v1/integrations/banking/status` | `conciliacao/` |
| `emitirBoleto()` | `POST /api/v1/integrations/banking/boleto/generate` | `cobrancas/` |
| `listarBoletos()` | `GET /api/v1/integrations/banking/boleto/list` | `cobrancas/`, `boletos/` |
| `gerarCobrancaPix()` | `POST /api/v1/integrations/banking/pix/generate` | `cobrancas/` |
| *(implícito)* | `GET /api/v1/integrations/banking/balances` | `dashboard/` |

---

## 3. Endpoints API Consumidos (mapeados)

### Financeiro core (via hooks gerados)
```
/api/v1/financial/payable/...          → contas-pagar/
/api/v1/financial/receivable/...       → contas-receber/
/api/v1/financial/bank-account/...     → conciliacao/
/api/v1/financial/bank-transaction/... → conciliacao/
/api/v1/financial/cashflow/...         → fluxo-caixa/
/api/v1/financial/purchase/...         → compras/
/api/v1/financial/inventory/...        → estoque/
/api/v1/financial/accounting/...       → contabilidade/
/api/v1/financial/billing-rule/...     → faturamento/
/api/v1/financial/customer/...         → clientes/
/api/v1/financial/supplier/...         → fornecedores/
```

### Financeiro direto (fetch explícito)
```
/api/v1/financial/nfse/dashboard       → dashboard/page.tsx:143
/api/v1/financial/nfse                 → dashboard/page.tsx:144
/api/v1/financial/bi/dashboard         → BI dashboard hook
/api/v1/financial/headcount            → hook headcount
/api/v1/financial/ai/advisor/relatorio → relatorios/page.tsx:303
```

### Banking Inter (bankingService.ts)
```
GET  /api/v1/integrations/banking/balances        → dashboard + conciliacao
GET  /api/v1/integrations/banking/statement       → conciliacao
GET  /api/v1/integrations/banking/statement/full  → conciliacao
GET  /api/v1/integrations/banking/status          → conciliacao
POST /api/v1/integrations/banking/boleto/generate → cobrancas
GET  /api/v1/integrations/banking/boleto/list     → cobrancas + boletos
POST /api/v1/integrations/banking/pix/generate    → cobrancas
```

### Banking payment controller (page.tsx banking)
```
POST /api/v1/banking/payment/barcode  → banking/page.tsx aba "pagar"
POST /api/v1/banking/payment/darf     → banking/page.tsx aba "darf"
GET  /api/v1/banking/payment/list     → banking/page.tsx
```

---

## 4. Páginas-chave — Análise por Funcionalidade

### `cobrancas/page.tsx` (1.519 linhas) — Principal
- Modo `boleto` → `emitirBoleto()` → `POST /boleto/generate`
- Modo `pix` → `gerarCobrancaPix()` → `POST /pix/generate`
- Lista boletos via `listarBoletos()` → `GET /boleto/list`
- Dashboard contas a receber via `useReceivableDashboard`
- Exibe `pix_copy_paste`, QR code, código de barras

### `conciliacao/page.tsx` (1.206 linhas)
- Tabs: `statement` (extrato Inter), `transactions` (banco de dados local), `accounts` (contas bancárias)
- Usa `fetchBankStatementFull()` (extrato ao vivo) + `useBankTransactions()` (DB local)
- `useImportOFX()` — importação de extrato OFX
- `BankTransactionDetailModal` — detalhe de transação com justificativa
- `fetchBankBalances()` — saldo Inter ao vivo

### `dashboard/page.tsx` (615 linhas)
- Consome `api.get('/api/v1/financial/nfse/dashboard')` — total NFS-e, impostos
- Consome `api.get('/api/v1/integrations/banking/balances')` — saldo Inter
- Exibe DRE simplificada, saldo bancário, últimas NFS-e

### `contas-pagar/page.tsx` (445 linhas)
- Hooks: `usePayables`, `usePayableDashboard`, `useCreatePayable`, `useUpdatePayable`, `useProcessPayment`
- Filtros: search, status, fornecedor, paginação
- Modais: `PayableFormModal`, `PayableDetailModal`

### `contas-receber/page.tsx` (419 linhas)
- Hooks: `useReceivables`, `useReceivableDashboard`, `useCreateReceivable`
- Filtros: search, status, cliente, paginação
- Modais: `ReceivableFormModal`, `ReceivableDetailModal`
- Modal adicional: `receiveModalOpen` (baixa de recebimento)

### `faturamento/page.tsx` (907 linhas)
- Hooks: `useBillingRules`, `useCreateBillingRule`, `useActivateBillingRule`, `usePauseBillingRule`
- Gerencia regras de cobrança recorrente + MRR

---

## 5. Componentes Financeiros (`/components/financeiro/`)

| Componente | Responsabilidade |
|------------|-----------------|
| `payable-form-modal.tsx` | Criar/editar conta a pagar |
| `payable-detail-modal.tsx` | Detalhe + baixa de pagamento |
| `receivable-form-modal.tsx` | Criar/editar conta a receber |
| `receivable-detail-modal.tsx` | Detalhe + baixa de recebimento |
| `bank-account-form-modal.tsx` | Cadastrar conta bancária |
| `bank-transaction-detail-modal.tsx` | Detalhe transação + justificativa (Lucro Real) |
| `billing-rule-form-modal.tsx` | Regra de faturamento |
| `cashflow-form-modal.tsx` | Lançamento cashflow |
| `customer-form-modal.tsx` | Cliente financeiro |
| `supplier-form-modal.tsx` | Fornecedor + qualificação |
| `supplier-detail-modal.tsx` | Detalhe do fornecedor |
| `purchase-form-modal.tsx` | Ordem/requisição de compra |
| `purchase-detail-modal.tsx` | Detalhe da compra |
| `inventory-form-modal.tsx` | Item de estoque |
| `journal-entry-form-modal.tsx` | Lançamento contábil |
| `nfe-form-modal.tsx` | NF-e entrada |
| `nfe-detail-modal.tsx` | Detalhe NF-e |

---

## 6. Gaps Identificados

| # | Gap | Página afetada | Impacto |
|---|-----|---------------|---------|
| 1 | `banking/page.tsx` usa `PAYMENT_API = '/api/v1/banking/payment'` — prefixo diverge do backend (`/api/v1/integrations/banking/payment` ou `/api/v1/financial/billing`) | `banking/page.tsx` | 🟡 Verificar se endpoints DARF/barcode estão acessíveis |
| 2 | `cobrancas/page.tsx` usa `pixBankCode: '403'` (Cora) como default — Cora está desconectado | `cobrancas/page.tsx` | 🟡 Trocar default para `'077'` (Inter) |
| 3 | `dashboard/page.tsx` não consome `/api/v1/financial/bi/dashboard` — consome NFS-e dashboard separado | `dashboard/page.tsx` | 🟢 Dashboard BI existe mas não é o padrão |
| 4 | Hooks gerados cobrem 483 endpoints mas não há mapeamento direto para folha PIX | `dp/folha/` | 🟢 Folha PIX é via DP, não financeiro |

---

## 7. Conclusão

O módulo financeiro frontend está **maduro e bem estruturado**:

- **22 subpáginas** cobrindo todo o ciclo financeiro (AP/AR, banking, conciliação, DRE, NFS-e)
- **Arquitetura limpa**: hooks gerados (`useFinancial.ts`) + serviço dedicado banking (`bankingService.ts`)
- **Banking Inter totalmente integrado**: balances, statement, boleto, PIX via `bankingService.ts`
- **483 endpoints** mapeados nos tipos gerados — cobertura de API completa
- **Ponto de atenção**: prefixo `PAYMENT_API` no `banking/page.tsx` deve ser validado contra o controller backend

---

*Relatório gerado: 2026-04-12*
*Auditor: Claude Sonnet 4.6 — T7*
*Branch: feature/people-management-reorganization*
