# T2 — Botão Pagar no PayableDetailModal
**Data:** 2026-04-12
**Commit modal:** `69abbf15`
**Branch:** feature/people-management-reorganization

---

## Missão

Adicionar botão "Registrar Pagamento" no modal de detalhes de contas a pagar (`payable-detail-modal.tsx`) com suporte a:
- Pagamento via Banco Inter (API — código de barras)
- Pagamento manual (registro direto no banco)

---

## PASSO 1 — Diagnóstico do PayableDetailModal

**Arquivo:** `frontend/src/components/financeiro/payable-detail-modal.tsx`

Estado anterior:
- Apenas exibia detalhes da conta (descrição, fornecedor, valor, vencimento, status, categoria)
- Sem qualquer funcionalidade de pagamento
- Props: `isOpen`, `onClose`, `payable`

---

## PASSO 2 — Reescrita do Modal com Botão Pagar

**Arquivo:** `frontend/src/components/financeiro/payable-detail-modal.tsx`
**Commit:** `69abbf15`

### Adições

| Item | Detalhe |
|------|---------|
| Import `useState` | Gerenciamento de estado local do formulário de pagamento |
| Import `useProcessPayment` | Hook Orval para pagamento manual via `@/hooks/financial/useFinancial` |
| Prop `onSuccess?: () => void` | Callback executado após pagamento bem-sucedido |
| Estado `showPayment` | Controla visibilidade do formulário de pagamento |
| Estado `paymentForm` | `{ codigo_barras, via_inter, data_pagamento }` |
| Estado `paymentLoading` | Spinner durante processamento |
| Estado `paymentMsg` | Mensagem de sucesso/erro inline |

### Função `handlePagar`

```typescript
const handlePagar = async () => {
  if (paymentForm.via_inter && paymentForm.codigo_barras) {
    // POST /api/v1/banking/payment/barcode
    // → Inter API paga o boleto
    // → atualiza payable_accounts no banco
  } else {
    // processPayment.mutateAsync(...)
    // → pagamento manual registrado
  }
};
```

### UI do Botão de Pagamento

- Visível apenas para `status === 'pending' | 'pendente' | 'overdue'`
- Toggle "🏦 Via Inter" / "📝 Manual"
- Campo de código de barras (apenas Via Inter)
- Seletor de data de pagamento
- Botão "✅ Confirmar" com estado de loading
- Mensagem inline de resultado (verde = sucesso, vermelho = erro)
- `setTimeout(2000)` → fecha modal e dispara `onSuccess()` após sucesso

---

## PASSO 3 — Build e Deploy

**Build ID:** `conecta-pro-1776004216509`

```bash
NODE_OPTIONS=--max-old-space-size=4096 npm run build
# Build concluído com sucesso

docker cp .next/standalone/. conecta-pro-frontend:/app/
docker cp .next/static/. conecta-pro-frontend:/app/.next/static/
docker restart conecta-pro-frontend

docker ps --filter name=conecta-pro-frontend --format "{{.Names}} {{.Status}}"
# → conecta-pro-frontend Up 12 seconds (healthy) ✅

docker exec conecta-pro-frontend cat /app/.next/BUILD_ID
# → conecta-pro-1776004216509 ✅
```

---

## PASSO 4 — Commit e Push

| Hash | Descrição |
|------|-----------|
| `69abbf15` | feat(banking): remove Cora UI — Inter como banco padrão (077) [inclui rewrite do payable-detail-modal] |

```
git push origin feature/people-management-reorganization ✅
```

---

## Validação Final

```
✅ PASSO 1 — Modal diagnosticado (sem botão pagar)
✅ PASSO 2 — Modal reescrito com botão pagar (Via Inter + Manual)
✅ PASSO 3 — Build OK (conecta-pro-1776004216509) + container (healthy)
✅ PASSO 4 — Commit 69abbf15 + push OK
```

---

## Endpoint Backend Usado

```
POST /api/v1/banking/payment/barcode
Authorization: Bearer <token>
{
  "codigo_barras": "...",
  "data_pagamento": "YYYY-MM-DD",
  "descricao": "...",
  "payable_id": "uuid"
}
```

O endpoint (`payment_controller.py`) paga via Banco Inter API e atualiza `payable_accounts`:
```sql
UPDATE payable_accounts SET
    status = 'pago',
    paid_at = NOW(),
    paid_value = :valor,
    transacao_bancaria_id = :transacao_id,
    updated_at = NOW()
WHERE id = :payable_id
```

---

## Download
```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_T2_PAYABLE_BTN_20260412.md ~/Downloads/RELATORIO_T2_PAYABLE_BTN_20260412.md
```
