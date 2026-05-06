# T1 — §122 SolidesBenefitService — Sync VT/VA → kit GED
**Data:** 2026-05-06
**Branch:** feature/people-management-reorganization
**Tipo:** FEAT — sincronização pedidos benefícios Sólides + vinculação GED
**Commits:** `c833a2a3` (feat §122)

---

## RESULTADO

| Métrica | Valor |
|---------|-------|
| API Sólides benefit-orders | ❌ Não exposto (6 endpoints → 404) |
| Pedidos sincronizados (fallback Inter) | **30** |
| Itens vinculados ao kit (por CPF) | **0** |
| Completude GED | **27.0% → 27.0%** (sem alteração) |

---

## STEP 1 — DIAGNÓSTICO

### API Sólides (Tangerino)
URL base: `https://employer.tangerino.com.br`

6 endpoints tentados, todos retornam 404:
- `/benefit-orders`
- `/v1/benefit-orders`
- `/benefits/orders`
- `/api/v1/benefit-orders`
- `/benefit/find-all`
- `/order/find-all`

**Conclusão:** API Sólides (Tangerino) expõe apenas endpoints HR/DP (employees, absences, occurrences). Benefit-orders não está disponível — documentado em §122.

### Inter Transactions SOLIDES
Filtro aplicado:
- `tipo_operacao = 'D'` (débito)
- `counterpart_name ILIKE '%solides%'` OR `ILIKE '%swap%'` OR `counterpart_document ILIKE '%10461302%'`
- CNPJ identificado: 10.461.302/0001-10 (SWAP IP S.A. — processador Sólides)

**30 transações PIX lump-sum encontradas.**

Problema estrutural: pagamentos chegam como lump-sum (valor total VT+VA de todos os funcionários em um único PIX). Sem breakdown por CPF/funcionário no payload Inter.

---

## STEP 2 — IMPLEMENTAÇÃO

### Arquivos criados/modificados

**`backend/modules/integrations/connectors/solides/benefit_service.py`** (novo)
- `_tentar_api_benefit_orders(mes_ref)` — tenta 6 endpoints, retorna [] se 404
- `SolidesBenefitService.sync_benefit_orders(mes_ref)` — API + fallback Inter
- `SolidesBenefitService._sync_from_inter_transactions(mes_ref)` — cria orders a partir das inter_transactions SOLIDES
- `SolidesBenefitService.match_inter_transactions()` — vincula orders a inter_transactions por valor±0.01 e data±1dia
- `SolidesBenefitService.vincular_kits(mes_ref)` — preenche slots kit por CPF (requer items)

**`backend/modules/integrations/controllers/solides_controller.py`** (modificado)
- `POST /beneficios/sync` — sync + match automático
- `POST /beneficios/vincular-kits` — vincula slots kit

### Tabelas criadas (via psql direto — INV-6)
```sql
CREATE TABLE solides_benefit_orders (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    order_number TEXT UNIQUE NOT NULL,
    data_pedido DATE,
    data_pagamento DATE,
    valor_total NUMERIC(12,2),
    status TEXT NOT NULL DEFAULT 'PENDENTE',
    inter_transaction_id UUID REFERENCES inter_transactions(id),
    raw_payload JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE solides_benefit_order_items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES solides_benefit_orders(id) ON DELETE CASCADE,
    employee_id UUID REFERENCES employees(id),
    kit_document_id UUID REFERENCES ged_kit_documents(id),
    valor_mobilidade NUMERIC(12,2) DEFAULT 0,
    valor_refeicao NUMERIC(12,2) DEFAULT 0,
    valor_total NUMERIC(12,2) GENERATED ALWAYS AS (valor_mobilidade + valor_refeicao) STORED,
    raw_payload JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## STEP 3 — EXECUÇÃO

### POST /api/v1/integrations/solides/beneficios/sync
```json
{
    "synced_total": 30,
    "from_api": 0,
    "from_inter_fallback": 30,
    "api_available": false,
    "mes_ref": "todos",
    "nota": "API Sólides não expõe benefit-orders. Orders criadas a partir das inter_transactions SOLIDES (lump-sum). Items por funcionário requerem upload de relatório Sólides (PDF/CSV).",
    "match_inter": {
        "matched_now": 0,
        "total_orders": 30,
        "com_inter_tx": 30,
        "sem_inter_tx": 0
    }
}
```

*30/30 orders já têm `inter_transaction_id` (preenchido diretamente pelo fallback).*

### POST /api/v1/integrations/solides/beneficios/vincular-kits
```json
{
    "vinculados": 0,
    "sem_slot": 0,
    "total_items": 0,
    "mes_ref": "todos",
    "nota": "solides_benefit_order_items vazio — API Sólides não expõe breakdown por funcionário. Vincular kits requer upload de relatório Sólides (PDF/CSV) e processamento manual dos items."
}
```

### Completude GED
```
447/1656 = 27.0%  (sem alteração — vinculação por CPF requer items)
```

---

## SELF-CHECK

| Item | Status |
|------|--------|
| INV-1 — benefit_service.py lido antes de modificar | ✅ (arquivo novo) |
| INV-2 — solides_controller.py lido completo antes de modificar | ✅ |
| INV-3 — tabelas criadas via DDL real (não Alembic — INV-6 pendente) | ✅ |
| INV-4 — zero dados simulados, apenas inter_transactions reais | ✅ |
| INV-4 — py_compile OK | ✅ |
| INV-4 — hot-copy + docker restart | ✅ |
| STEP 1 — API Sólides testada (6 endpoints → 404) | ✅ |
| STEP 1 — Inter transactions SOLIDES identificadas | ✅ 30 PIX lump-sum |
| STEP 2 — `_tentar_api_benefit_orders` com 6 endpoints | ✅ |
| STEP 2 — `sync_benefit_orders` API + fallback | ✅ |
| STEP 2 — `_sync_from_inter_transactions` (CAST JSONB, ON CONFLICT) | ✅ |
| STEP 2 — `match_inter_transactions` (valor±0.01, data±1dia) | ✅ |
| STEP 2 — `vincular_kits` (slot por employee_id + doc_type) | ✅ |
| STEP 2 — endpoints POST /beneficios/sync + /vincular-kits | ✅ |
| STEP 3 — POST sync executado → 30 orders | ✅ |
| STEP 3 — POST vincular-kits executado → 0 itens (esperado) | ✅ |
| STEP 3 — FK verification query | ✅ 30/30 com inter_tx |
| STEP 3 — Completude GED | ✅ 27.0% (sem alteração) |
| STEP 6 — git commit feat `c833a2a3` + push | ✅ |
| STEP 6 — CONTRACTS_GEDEON §122 | ✅ |
| STEP 6 — RELATORIO criado | ✅ |
| INV-6 — Alembic migration | ⚠️ Tabelas criadas via DDL direto; migration pendente |
| Rota implementada | ⚠️ `/integrations/solides/...` (main_production.py zona proibida — não foi possível criar `/dp/solides/...`) |

---

## LIMITAÇÕES E PRÓXIMOS PASSOS

| Item | Detalhe |
|------|---------|
| API benefit-orders | Sólides (Tangerino) não expõe endpoint — status documentado |
| Breakdown por CPF | Requer upload de relatório Sólides (PDF/CSV) + parser |
| `solides_benefit_order_items` | Vazio — será populado via relatório ou enriquecimento futuro |
| Alembic migration | Tabelas criadas via DDL direto em produção; migration deve ser criada para consistência |
| Rota `/dp/solides/...` | Não implementada — `main_production.py` é zona proibida; rota `/integrations/solides/...` funcional |

---

**§122 concluído. 30 pedidos VT/VA sincronizados via fallback Inter. 0 itens vinculados ao kit (limite da API Sólides sem breakdown por CPF). Completude GED 27.0% estável.**
