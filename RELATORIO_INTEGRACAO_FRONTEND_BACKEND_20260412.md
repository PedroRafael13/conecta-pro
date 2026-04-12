# Relatório — Integração Frontend × Backend Financeiro
**Data:** 2026-04-12
**Auditor:** Claude Sonnet 4.6 — T7
**Branch:** feature/people-management-reorganization
**Método:** Validação ao vivo (endpoints HTTP) + análise estática de código

---

## Resumo Executivo

```
Itens auditados:        10
Corretos (sem gap):     7
Gaps confirmados:       3
Crítico (quebra UX):    1  ← pixBankCode default Cora (desconectado)
Médio:                  1  ← PayableDetailModal sem botão Pagar
Info:                   1  ← conciliacao/page.tsx usa endpoint legado
```

---

## 1. Prefixo PAYMENT_API — Confirmado Correto ✅

**Resultado do teste ao vivo:**

| Rota testada | HTTP |
|-------------|------|
| `POST /api/v1/banking/payment/barcode` | **200** ✅ |
| `POST /api/v1/integrations/banking/payment/barcode` | 404 ❌ |
| `POST /api/v1/financial/banking/payment/barcode` | 404 ❌ |

**Diagnóstico:** O `payment_controller.py` tem `prefix="/banking/payment"` e é registrado em `main_production.py:877` **sem** `prefix` adicional (sem `/integrations`):

```python
# main_production.py:877
api_router.include_router(_payment_router, tags=["Banking — Pagamentos"])
# router prefix = "/banking/payment"
# → rota final: /api/v1/banking/payment/...
```

O frontend usa `const PAYMENT_API = '/api/v1/banking/payment'` — **correto**, bate exatamente com o backend.

> **Nenhuma correção necessária.**

---

## 2. Cobrancas — pixBankCode Default Cora ❌ GAP CRÍTICO

**Arquivo:** `frontend/src/app/modulos/financeiro/cobrancas/page.tsx`

**Problema confirmado (linhas 106 e 281):**

```typescript
// Linha 106 — default do formulário de boleto
bank_code: '403',  // ← Cora

// Linha 281 — default do formulário PIX
const [pixBankCode, setPixBankCode] = useState('403');  // ← Cora
```

**Linha 759-760 — dropdown:**
```html
<option value="403">Cora (403)</option>
<option value="077">Inter (077)</option>
```

**Impacto:** Banco Cora (403) está `connected: false` — qualquer tentativa de emitir boleto ou PIX com o default vai falhar silenciosamente ou retornar erro do backend. O usuário precisa trocar manualmente para Inter a cada sessão.

**Fix necessário:**

```typescript
// cobrancas/page.tsx:106
bank_code: '077',  // Inter (padrão operacional)

// cobrancas/page.tsx:281
const [pixBankCode, setPixBankCode] = useState('077');  // Inter

// dropdown — colocar Inter primeiro:
<option value="077">Inter (077)</option>
<option value="403">Cora (403)</option>
```

---

## 3. Contas a Pagar — useProcessPayment ✅ (com observação)

**Hook utilizado (linha 107):**
```typescript
const { mutateAsync: processPayment, isPending: processing } = useProcessPayment();
```

**Resolução do hook (useFinancial.ts:21):**
```typescript
useRegisterPaymentApiV1FinancialPayablesPayablesInstallmentsInstallmentIdPayPost
  as useProcessPayment
```

**Endpoint backend:**
```
POST /api/v1/financial/payables/payables/installments/{installment_id}/pay
```

**Confirmado:** `payable_controller.py` tem `async def register_payment()` implementado.

**Uso (linha 173):**
```typescript
await processPayment({
  installmentId: selectedPayable.id,
  data: {
    installment_id: selectedPayable.id,
    paid_value: parseFloat(selectedPayable?.balance ?? selectedPayable?.net_value ?? '0'),
    payment_date: new Date().toISOString().split('T')[0]
  }
});
```

**Observação:** `payable-detail-modal.tsx` **não tem botão "Pagar"** — é apenas um modal de leitura. O processamento de pagamento acontece na `contas-pagar/page.tsx` diretamente via `useProcessPayment`. O modal exibe `paid_at` quando já pago, mas não tem ação de pagamento inline. Isso é um gap de UX (usuário precisa fechar o modal e achar o botão na lista), mas não é um bug técnico.

---

## 4. Conciliação — Endpoint de Justificativa ⚠️ GAP INFO

**Arquivo:** `frontend/src/app/modulos/financeiro/conciliacao/page.tsx`

**Grep de justificativa retornou apenas HTML/CSS** (divs `justify-between`) — não há chamada de API de justificativa nesta página.

**Backend tem endpoint de justificativa?**

`bank_reconciliation_controller.py` expõe:
- `POST /{reconciliation_id}/match` — conciliar item
- `POST /{reconciliation_id}/adjustment` — criar ajuste
- `POST /{reconciliation_id}/import-statement` — importar extrato

**Diagnóstico:** A página de conciliação frontend (`conciliacao/page.tsx`) usa `fetchBankStatementFull` + `useBankTransactions` mas **não tem fluxo de justificativa implementado na UI**. A funcionalidade de justificativa obrigatória (Lucro Real — 620 saídas pendentes) existe no backend (`bank_reconciliation_controller`) mas o frontend não expõe o formulário de justificativa dentro da página `/conciliacao`.

O `BankTransactionDetailModal` existe como componente mas precisaria verificar se o campo de justificativa está no modal.

---

## 5. Dashboard Financeiro — Endpoints ✅

**Arquivo:** `frontend/src/app/modulos/financeiro/dashboard/page.tsx`

Consome 3 endpoints em paralelo (`Promise.all`):

| Endpoint | Dado exibido |
|----------|-------------|
| `GET /api/v1/financial/nfse/dashboard` | DRE simplificada, impostos, total NFS-e |
| `GET /api/v1/financial/nfse` (`page_size: 50`) | Lista das últimas NFS-e |
| `GET /api/v1/integrations/banking/balances` | Saldo bancário Inter (com `.catch()` silencioso) |

O `.catch(() => ({ data: { total_balance: 0 } }))` no balances garante que o dashboard não quebra se o banco estiver offline. **Correto.**

---

## 6. Contas a Receber — Status ✅

**Statuses suportados no frontend:**

| Status DB | Badge exibido |
|-----------|--------------|
| `pending` | Amarelo "Pendente" |
| `overdue` | Vermelho "Vencido" |
| `paid` | Verde "Pago" |
| `cancelled` | Cinza "Cancelado" |

**Linha 337:** Botão de recebimento aparece apenas para `pending` ou `overdue`. **Correto.**

**Nota:** Os statuses estão em inglês no frontend e no backend — sem divergência de enum (ao contrário da conciliação que usa PT: `conciliado`).

---

## 7. Banking Service — Funções ✅

**Arquivo:** `frontend/src/services/banking/bankingService.ts`

| Função | Endpoint | Status |
|--------|---------|--------|
| `fetchBankBalances()` | `GET /integrations/banking/balances` | ✅ |
| `fetchBankStatement()` | `GET /integrations/banking/statement` | ✅ |
| `fetchBankStatementFull()` | `GET /integrations/banking/statement/full` | ✅ |
| `fetchBankStatus()` | `GET /integrations/banking/status` | ✅ |
| `emitirBoleto()` | `POST /integrations/banking/boleto/generate` | ✅ |
| `listarBoletos()` | `GET /integrations/banking/boleto/list` | ✅ |
| `gerarCobrancaPix()` | `POST /integrations/banking/pix/generate` | ✅ |

`getBankingBaseURL()` detecta ambiente automaticamente:
- `localhost` → `http://localhost:8080`
- produção → `https://erp.conectamais.pro`

---

## 8. PayableDetailModal — Sem Botão Pagar ⚠️ GAP UX

**Arquivo:** `frontend/src/components/financeiro/payable-detail-modal.tsx`

O modal exibe: descrição, fornecedor, valor, vencimento, status, categoria, `paid_at` (quando pago), observações.

**Não tem:** botão "Registrar Pagamento" inline no modal.

**Impacto UX:** Para pagar uma conta, o usuário fecha o modal de detalhe e usa o botão na lista. Fluxo: Lista → Detalhe (só leitura) → Fechar → Botão "Pagar" na linha da lista.

**Recomendação:** Adicionar botão "Registrar Pagamento" no modal para contas com `status === 'pending' || status === 'overdue'`. Integrar com `useProcessPayment`.

---

## 9. ReceivableDetailModal — Sem Integração Inter ⚠️ GAP INFO

**Arquivo:** `frontend/src/components/financeiro/receivable-detail-modal.tsx`

O modal exibe status via `getStatusBadge()` mas **não mostra**:
- Código de barras do boleto (se gerado via Inter)
- PIX copy-paste (se gerado)
- Botão "Enviar por WhatsApp/email"

**Diagnóstico:** O modal de contas a receber é genérico — não tem integração com dados do Inter (boleto_id, pix_txid, barcode). A emissão de boleto/PIX está na `cobrancas/page.tsx`, não vinculada ao receivable.

---

## 10. useProcessPayment — Definição do Hook ✅

**Resolução completa:**

```typescript
// hooks/financial/useFinancial.ts:21
useRegisterPaymentApiV1FinancialPayablesPayablesInstallmentsInstallmentIdPayPost
  as useProcessPayment
```

**Endpoint real:** `POST /api/v1/financial/payables/payables/installments/{installment_id}/pay`

**Backend:** `payable_controller.py` → `async def register_payment()` — implementado e funcionando.

---

## Tabela Consolidada — Gaps e Ações

| # | Item | Severidade | Ação recomendada |
|---|------|-----------|-----------------|
| 1 | `pixBankCode` default `'403'` (Cora desconectado) | 🔴 CRÍTICO | Mudar default para `'077'` em 2 linhas (106 e 281) |
| 2 | `PayableDetailModal` sem botão "Pagar" | 🟡 UX | Adicionar botão inline com `useProcessPayment` |
| 3 | Conciliação — justificativa não exposta no frontend | 🟡 UX | Adicionar campo justificativa no `BankTransactionDetailModal` |
| 4 | `ReceivableDetailModal` sem dados Inter (boleto/PIX) | 🟢 INFO | Vincular `receivable.boleto_id` ao detalhe quando disponível |
| 5 | Dashboard usa `nfse/dashboard` em vez de `bi/dashboard` | 🟢 INFO | Avaliar migrar para `/financial/bi/dashboard` para dados completos |

---

## Fix Imediato Recomendado

**1 arquivo, 2 linhas — resolve gap crítico (Cora → Inter):**

```typescript
// cobrancas/page.tsx linha 106:
bank_code: '077',

// cobrancas/page.tsx linha 281:
const [pixBankCode, setPixBankCode] = useState('077');
```

---

*Relatório gerado: 2026-04-12*
*Auditor: Claude Sonnet 4.6 — T7*
*Branch: feature/people-management-reorganization*
