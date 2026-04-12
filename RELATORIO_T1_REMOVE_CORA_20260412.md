# T1 — Remover Cora + Fix pixBankCode
**Data:** 2026-04-12
**Engenheiro:** Claude Sonnet 4.6
**Branch:** feature/people-management-reorganization

---

## RESUMO EXECUTIVO

Banco Cora (403) removido completamente do sistema.
Banco Inter (077) é o único banco integrado.
pixBankCode default corrigido para '077' em todos os formulários.

---

## PASSO 1 — Mapeamento

| Arquivo | Referências Cora encontradas |
|---------|------------------------------|
| `cobrancas/page.tsx` | BANK_COLORS, BANK_NAMES, bank_code default, BankSelector, pixBankCode, dropdown option |
| `boletos/page.tsx` | BANK_COLORS, BANK_NAMES, bank_code default, texto header, array bancos, dropdown option |
| `financeiro/page.tsx` | description card, comment, isCora logic, bankBalances fallback, text |
| `conciliacao/page.tsx` | getBankBadge(), dropdown option, texto instrução |
| `bankingService.ts` | docstring, fallback balances, fallback status, interface comment, bank_name mapping |
| `banking_controller.py` | docstring, Cora registration, banks list, bank_names dict, boleto/PIX logic, list_boletos |
| `adapters/__init__.py` | import CoraAdapter, __all__ |
| `adapters/base.py` | `CORA = "403"` em BankCode |
| `services/banking_service.py` | import CoraAdapter, ADAPTER_MAP |
| `adapters/cora.py` | **ARQUIVO DELETADO** |

---

## PASSO 2 — Frontend: Alterações

### `cobrancas/page.tsx`
- `BANK_COLORS`: removida entrada `'403': '#e85d26'`
- `BANK_NAMES`: removida entrada `'403': 'Banco Cora'`
- `INITIAL_BOLETO_FORM.bank_code`: `'403'` → `'077'`
- `BankSelector`: lista reduzida para apenas `[{ code: '077', name: 'Inter' }]`
- `pixBankCode`: `useState('403')` → `useState('077')`
- Dropdown: removida `<option value="403">Cora (403)</option>`

### `boletos/page.tsx`
- `BANK_COLORS`, `BANK_NAMES`: removidas entradas Cora
- `INITIAL_FORM.bank_code`: `'403'` → `'077'`
- Texto header: "Emissão via Cora e Inter" → "Emissão via Banco Inter"
- Array bancos: removido `{ code: '403', name: 'Cora', sub: '403' }`
- Dropdown: removida `<option value="403">Cora (403)</option>`

### `financeiro/page.tsx`
- Card description: "via Cora e Inter" → "via Banco Inter"
- Comment: "Cora + Inter" → "Banco Inter"
- `isCora` logic removida — cor fixa `#00a859` (Inter)
- Texto "não conectadas": removida referência à Cora
- Fallback `bankBalances`: removida entrada Cora

### `conciliacao/page.tsx`
- `getBankBadge()`: removido `if (bankCode === '403') return { label: 'Cora', ... }`
- Dropdown: removida `<option value="403">Cora</option>`
- Texto instrução: "Cora, Inter ou outro" → "Banco Inter"

### `bankingService.ts`
- Docstring: removida referência Cora
- Fallback `fetchBankBalances`: apenas entrada Inter
- Fallback `fetchBankStatus`: apenas entrada Inter
- Interface comment: `"403" = Cora` removido
- `bank_name` mapping: removida ternária Cora/Inter → fixo "Banco Inter"

---

## PASSO 3 — Backend: Alterações

### `adapters/cora.py`
- **ARQUIVO DELETADO** ✅

### `adapters/__init__.py`
- Removido: `from .cora import CoraAdapter`
- Removido: `"CoraAdapter"` de `__all__`

### `adapters/base.py`
- Removido: `CORA = "403"  # Cora SCD` da enum `BankCode`

### `services/banking_service.py`
- Removido: import `CoraAdapter`
- Removido: `BankCode.CORA: CoraAdapter` de `ADAPTER_MAP`

### `controllers/banking_controller.py`
- Docstring: atualizada para "Banco Inter"
- `BoletoGenerateRequest.bank_code` comment: removido Cora
- `PixChargeRequest.bank_code` default: `"403"` → `"077"`
- `_get_banking_service()`: removido bloco de registro Cora (15 linhas)
- `get_bank_balances()`: removida entrada `("403", "Banco Cora", ...)`
- `get_bank_statement()`: `["403", "077"]` → `["077"]`
- `get_bank_status()`: removida entrada `("403", "Banco Cora")`
- `_BANK_NAMES`: removida entrada `"403": "Banco Cora"`
- `generate_boleto()`: removido bloco `if req.bank_code == "403": # Cora: generate_invoice`
- `generate_pix_charge()`: removido bloco `if req.bank_code == "403":` + erro Cora PIX
- `list_boletos()`: removido bloco Cora (`list_invoices`), `banks_to_query = ["077"]`
- `get_bank_statement_full()`: `["403", "077"]` → `["077"]`
- Variáveis não usadas removidas (`start_date`, `bank_name` em `list_boletos`)

---

## PASSO 4 — Verificação

```
FRONTEND — Cora restante: ✅ Nenhuma referência banking Cora
BACKEND — Cora restante: ✅ Nenhuma referência Cora (banking)
Inter default confirmado:
  cobrancas/page.tsx: bank_code: '077', pixBankCode = '077'
  boletos/page.tsx:   bank_code: '077'
```

Único "403" restante no backend: `elif "403" in error_msg:` — verifica HTTP 403 Forbidden, não banco Cora. ✅ Correto manter.

---

## PASSO 5 — Deploy

| Etapa | Status |
|-------|--------|
| Hot copy backend `modules/` | ✅ |
| `docker restart conecta-pro-backend` | ✅ healthy |
| `next build` | ✅ (fix TS: `paymentForm.data_pagamento ?? ''`) |
| `docker cp .next/standalone/` frontend | ✅ |
| `docker cp .next/static/` frontend | ✅ |
| `docker restart conecta-pro-frontend` | ✅ healthy |

---

## PASSO 6 — Commits

```
3ab7a765  feat(banking): remove Banco Cora — apenas Banco Inter (077)
          5 files: adapters/__init__.py, base.py, cora.py (deleted), controller, service

69abbf15  feat(banking): remove Cora UI — Inter como banco padrão (077)
          6 files: boletos, cobrancas, conciliacao, financeiro/page, payable-detail-modal, bankingService

push: ✅ origin/feature/people-management-reorganization
```

---

*Relatório gerado em 2026-04-12 por Claude Sonnet 4.6*
