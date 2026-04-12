# RELATÓRIO — T5 Frontend: receivable_id no body boleto/PIX
**Data:** 2026-04-12
**Commit:** `a6a71787`

---

## SUMÁRIO

| Item | Status |
|------|--------|
| `receivable_id: receivable.id` no body do boleto | ✅ linha 96 |
| `receivable_id: receivable.id` no body do PIX | ✅ linha 142 |
| Build Next.js | ✅ |
| Deploy container `conecta-pro-frontend` | ✅ healthy |
| Commit mensagem exata do prompt | ✅ `a6a71787` |
| Push `feature/people-management-reorganization` | ✅ |

---

## CICLO END-TO-END FECHADO

```
Modal → POST /boleto/generate { receivable_id: receivable.id, ... }
      → Backend salva boleto_id/barcode/digitable_line no receivable_account
Modal → POST /pix/generate { receivable_id: receivable.id, ... }
      → Backend salva pix_txid/pix_copy_paste no receivable_account
Próxima abertura do modal → exibe cobrança existente ✅
```

---

**Relatório gerado:** 2026-04-12
