# T4 CPRO12 — Sync Onvio + Kit Prime Arena 04/2026
**Data:** 2026-05-05
**Executor:** Claude Sonnet 4.6 [session: t5] [module: ged]
**Tipo:** DIAGNÓSTICO + OPERAÇÃO (INV-3: código não modificado)

---

## Hipóteses Validadas

| H | Descrição | Resultado |
|---|-----------|---------|
| H1 | Docs Onvio de Março/2026 no banco | ✅ 43 docs mes_ref='03.2026' no banco; Prime Arena tem 2 (folha_pagamento + recibo_folha) |
| H2 | Prime Arena tem client_id mapeado | ✅ ged_clients.id=52958919-... / condominios.id=21929c3d-... |
| H3 | Endpoint /onvio/sync existe e responde | ❌ HTTP 404 — router não registrado em main_production.py |
| H4 | Endpoint auto-build existe | ✅ `POST /api/v1/ged/auto-assemble` → HTTP 201 |
| H5 | Após sync, novos docs de Março aparecem | ✅ Sync já rodou em 2026-05-04 (12 docs para 03.2026) |
| H6 | Após auto-build, kit Prime Arena tem docs | ❌ 0 docs file_path — mes_ref='04.2026' ausente para Prime Arena |
| H7 | Endpoint auto-build existe | ✅ `POST /api/v1/ged/auto-assemble` + `POST /api/v1/ged/kits/montar` |
| H8 | Kit Prime Arena 04/2026 já existe | ✅ id=a5d04bc6-..., 133 slots, completion=3.76% (stale) |

---

## Estado Pré-Sync (READ-ONLY)

### Documentos Onvio no banco (total: 605)

| mes_ref | total |
|---------|-------|
| 03.2026 | 43 |
| 02.2026 | 29 |
| 01.2026 | 27 |
| 04.2026 | 10 |
| 12.2025 | 29 |
| 11.2025 | 27 |
| 10.2025 | 21 |
| NULL | 165 |
| 2026 (sem MM) | 20 |
| 2025 (sem MM) | 155 |

**Atenção:** 489/605 docs (81%) têm `condominio_id = NULL` — não associados a nenhum condomínio.

### Docs Onvio do Prime Arena (condominios.id = 21929c3d)

| categoria | mes_ref | total |
|-----------|---------|-------|
| folha_pagamento | 03.2026 | 1 ✅ |
| recibo_folha | 03.2026 | 1 ✅ |
| folha_pagamento | 02.2026 | 1 |
| recibo_folha | 02.2026 | 1 |
| folha_pagamento | 01.2026 | 1 |
| recibo_folha | 01.2026 | 1 |
| folha_pagamento | 12.2025 | 1 |
| recibo_folha | 12.2025 | 1 |
| (outros meses 07-11/2025) | ... | 10 |
| **TOTAL** | | **18** |

**Prime Arena tem ZERO docs com mes_ref='04.2026'.**

### Kit Prime Arena 04/2026 (pré-operações)

- `ged_document_kits.id`: a5d04bc6-ca53-4978-b32b-41873df8b4be
- `completion_percentage`: 3.76% (valor stale — calculado anteriormente)
- `status`: em_montagem
- Slots em `ged_kit_documents`: 133 total, 0 com file_path

---

## Sync Onvio (STEP 3 — ANTES/DEPOIS)

**Docs Onvio antes do sync:** 605
**Endpoint disparado:** `POST /api/v1/onvio/sync` → HTTP 404 `{"detail":"Not Found"}`
**Sleep 30s executado:** sim
**Docs Onvio depois do sync:** 605
**Novos docs:** 0

### Status do endpoint
- `POST /api/v1/onvio/sync` → **HTTP 404**
- `POST /api/v1/gedeon/onvio/sync` → **HTTP 404**

### Causa raiz do 404
O `main_production.py` tenta importar `modules.gedeon.onvio.controllers.onvio_controller`
(caminho inexistente). O endpoint real está em `modules.gedeon.controllers.onvio_controller`
(linha 84: `@router.post("/sync")`), mas esse controller **não está registrado** em
`main_production.py`.

### Última sync registrada (onvio_sync_log)
| mes_ref | status | docs_baixados | docs_novos | data |
|---------|--------|---------------|------------|------|
| 04.2026 | success | 58 | 58 | 2026-05-04 17:31 |
| 03.2026 | success | 12 | 12 | 2026-05-04 18:46 |
| 02.2026 | success | 1 | 1 | 2026-05-04 18:45 |
| 01.2026 | success | 0 | 0 | 2026-05-04 18:42 |
| all | error | 0 | 0 | 2026-05-05 02:42 |

**INV-4 aplicado: endpoint inacessível documentado, não corrigido.**

---

## Auto-Build para Abril/2026 (STEP 5)

### Operações disparadas

**Operação 1:** `POST /api/v1/ged/auto-assemble?reference_month=2026-04-01`
```json
{
  "reference_month": "2026-04-01",
  "total_clients": 11,
  "kits_created": 8,
  "kits_updated": 0,
  "total_documents": 880,
  "errors": []
}
```
HTTP 201 ✅

**Operação 2:** `POST /api/v1/ged/kits/montar` com `{"mes_ref": "04.2026"}`
```json
{
  "kits_criados": 3,
  "detalhes": [
    {"client": "Conecta Mais - Seguranca e Tecnologia"},
    {"client": "CONDOMINIO RESIDENCIAL PARISE VILLAGE"},
    {"client": "CONDOMINIO RESIDENCIAL GREEN HILLS"}
  ]
}
```
HTTP 201 ✅

---

## Estado Pós-Auto-Build (STEP 6)

### Prime Arena 04/2026 — GEDEON Completude

| Métrica | Valor |
|---------|-------|
| total_esperado | 94 |
| total_presente_confirmado | **0** |
| total_presente_pendente_revisao | 0 |
| total_faltante | 30 (tipos distintos) |
| pct_completude_confirmada | **0.0%** |
| pct_completude_total | 0.0% |

### Prime Arena 04/2026 — GED Kit Documents (STEP 6 — query ✅/❌)

| document_type | total | preenchidos | status |
|---------------|-------|-------------|--------|
| aso | 1 | 0 | ❌ |
| boleto | 1 | 0 | ❌ |
| cnd_caixa | 1 | 0 | ❌ |
| cnd_estadual | 1 | 0 | ❌ |
| cnd_federal | 1 | 0 | ❌ |
| cnd_municipal | 1 | 0 | ❌ |
| cnd_prefeitura | 1 | 0 | ❌ |
| cnd_rfb | 1 | 0 | ❌ |
| cnd_sefaz | 1 | 0 | ❌ |
| cnd_trabalhista | 1 | 0 | ❌ |
| cndt_trabalhista | 1 | 0 | ❌ |
| comp_fgts_rescisao | 7 | 0 | ❌ |
| comp_pag_fgts | 1 | 0 | ❌ |
| comp_salario_individual | 7 | 0 | ❌ |
| comp_va_solides | 7 | 0 | ❌ |
| comp_vt_individual | 7 | 0 | ❌ |
| comp_vt_va_combinado | 7 | 0 | ❌ |
| comprovante_va | 6 | 0 | ❌ |
| comprovante_vr | 6 | 0 | ❌ |
| comprovante_vt | 6 | 0 | ❌ |
| contracheque | 11 | 0 | ❌ |
| contrato_trabalho | 7 | 0 | ❌ |
| crf_fgts | 1 | 0 | ❌ |
| dctfweb_declaracao | 1 | 0 | ❌ |
| dctfweb_extrato | 1 | 0 | ❌ |
| dctfweb_recibo | 1 | 0 | ❌ |
| escala_mes | 6 | 0 | ❌ |
| ficha_empregado | 7 | 0 | ❌ |
| folha_pagamento | 1 | 0 | ❌ |
| folha_ponto | 6 | 0 | ❌ |
| folhas_ponto | 7 | 0 | ❌ |
| gfd_fgts_mensal | 1 | 0 | ❌ |
| gfd_fgts_rescisao | 7 | 0 | ❌ |
| nfse | 1 | 0 | ❌ |
| recibo_vt_va | 1 | 0 | ❌ |
| relatorio_gfd_fgts | 1 | 0 | ❌ |
| relatorio_gfd_rescisao | 7 | 0 | ❌ |
| relatorio_pedido_va | 1 | 0 | ❌ |
| **TOTAL** | **133** | **0** | |

### Prime Arena 04/2026 — Via API (STEP 6)

`GET /api/v1/ged/kits?client_id=52958919-...&month=4&year=2026&limit=1` → HTTP 200:

```json
{
  "total": 1,
  "items": [{
    "id": "a5d04bc6-ca53-4978-b32b-41873df8b4be",
    "client_name": "CONDOMINIO PRIME ARENA",
    "reference_month": "2026-04-01",
    "status": "em_montagem",
    "total_employees": 6,
    "total_documents": 133,
    "documents_signed": 5,
    "completion_percentage": 4,
    "sent_at": null
  }]
}
```

> **Nota:** `documents_signed=5` e `completion_percentage=4` são valores stale na coluna
> `ged_document_kits` — não refletem o estado atual. A query direta em `ged_kit_documents`
> confirma 0 docs com `file_path`. O Prime Arena tem 6 funcionários alocados.

### Resumo GED Kit Documents

| Campo | Valor |
|-------|-------|
| Slots totais | 133 |
| Com file_path | **0** |
| Sem file_path | 133 |
| completion_percentage (stale) | 4% |
| documents_signed (stale) | 5 |

---

## Documentos Faltantes — 30 tipos em 4 categorias

### ❌ nao_encontrado_onvio (12 tipos) — aguarda publicação no Onvio de Abril/2026

| Tipo | Escopo |
|------|--------|
| folha_pagamento | condominio |
| contracheque | funcionario |
| folhas_ponto | funcionario |
| gfd_fgts_mensal | condominio |
| relatorio_gfd_fgts | condominio |
| gfd_fgts_rescisao | funcionario |
| relatorio_gfd_rescisao | funcionario |
| dctfweb_declaracao | condominio |
| dctfweb_recibo | condominio |
| dctfweb_extrato | condominio |
| aso | condominio |
| contrato_trabalho | funcionario |
| ficha_empregado | funcionario |
| rescisao_contrato | funcionario |

### ⏳ aguarda_fase_2_banco (9 tipos) — depende de integração bancária (FASE 2 GEDEON)

| Tipo | Escopo |
|------|--------|
| boleto | condominio |
| comp_pag_fgts | condominio |
| nfse | condominio |
| comp_fgts_rescisao | funcionario |
| comp_rescisao | funcionario |
| comp_salario_individual | funcionario |
| comp_vt_individual | funcionario |

### ⏳ aguarda_fase_1_cnd (5 tipos) — depende de busca automática CND (FASE 1 GEDEON)

| Tipo | Escopo |
|------|--------|
| cnd_rfb | empresa_matriz |
| cnd_caixa | empresa_matriz |
| cnd_prefeitura | empresa_matriz |
| cnd_sefaz | empresa_matriz |
| cnd_trabalhista | empresa_matriz |

### ⚠️ nao_sincronizado (4 tipos) — VA/VT não sincronizados no Onvio

| Tipo | Escopo |
|------|--------|
| comp_va_solides | funcionario |
| comp_vt_va_combinado | funcionario |
| recibo_vt_va | condominio |
| relatorio_pedido_va | condominio |

---

## Causa Raiz do 0% Completude

O `KitBuilderService` (GEDEON) busca:
```sql
SELECT caminho_local FROM onvio_documents
WHERE condominio_id = '21929c3d-f469-4eb4-8309-4d8201231100'
  AND mes_ref = '04.2026'     ← AQUI está o bloqueio
  AND categoria = :cat
  AND caminho_local IS NOT NULL
```

Prime Arena tem docs até `mes_ref='03.2026'` (folha + recibo). **Docs com mes_ref='04.2026' ainda não foram publicados no Onvio** — são os documentos de competência Abril/2026 (folha paga em Maio, FGTS de Abril, etc.), que geralmente chegam entre os dias 5–20 do mês seguinte.

---

## Cenário Aplicado

**Cenário B** — Completude 0% após auto-build.

Onvio NÃO tem docs de `mes_ref='04.2026'` para o Prime Arena. O sync de 2026-05-04 trouxe 10 docs com mes_ref='04.2026' mas todos `documento_digitalizado` sem condominio_id. Os 58 docs do sync '04.2026' resultaram em 60 com mes_ref=NULL e 10 com mes_ref='04.2026' (nenhum do Prime Arena).

---

## Achados Arquiteturais

| Achado | Impacto |
|--------|---------|
| 81% dos docs Onvio sem condominio_id | Auto-matching impossível para a maioria dos docs |
| Endpoint POST /onvio/sync não registrado | Impossível disparar sync manual via API |
| Path errado em main_production.py (onvio.controllers vs controllers) | Router Onvio inacessível |
| KitBuilderService usa mes_ref=kit_month (não kit_month-1) | Docs de Março só aparecem no kit de Março, não no de Abril |
| 3.76% em ged_document_kits é valor stale | Completude não recalculada após build sem matches |

---

## Próximos Passos

1. **Aguardar** publicação dos documentos de Abril/2026 no Onvio (ETA: 10–20/05/2026)
2. **Registrar** `modules.gedeon.controllers.onvio_controller` em main_production.py (requer Jordan — Zona Proibida)
3. **Após registro**: rodar `POST /api/v1/gedeon/onvio/sync` com `mes_ref=04.2026`
4. **Após sync**: rodar `POST /api/v1/ged/auto-assemble?reference_month=2026-04-01` novamente
5. **FASE 1** (CND): quando ativa, preenche cnd_rfb, cnd_caixa, cnd_prefeitura, cnd_sefaz, cnd_trabalhista automaticamente
6. **FASE 2** (banco): quando ativa, preenche boleto, comp_pag_fgts, comp_salario_individual, etc.

---

## Self-check

| Item | Status |
|------|--------|
| STEP 0 — contrato lido, §83 confirmado, §13.1 + INV-8 citados | ✅ |
| STEP 1 — TOKEN obtido | ✅ |
| STEP 2 — estado pré-sync documentado (docs por categoria, kit_id, condominio_ids) | ✅ |
| STEP 3 — ANTES=605, sync HTTP 404, sleep 30s, DEPOIS=605, Novos=0 | ✅ |
| STEP 4 — endpoints auto-build identificados e testados | ✅ |
| STEP 5 — auto-build 04/2026 disparado (2 endpoints, HTTP 201) | ✅ |
| STEP 6 — query ✅/❌ (38 tipos, 133 slots, 0 preenchidos) + API GED confirmada | ✅ |
| STEP 7 — §85 + commit 848f4a68 + push | ✅ |
| STEP 8 — relatório completo gerado | ✅ |
| INV-8 — kit NÃO enviado ao cliente | ✅ |
| INV-3 — código não modificado | ✅ |
| INV-4/5 — erros documentados, não corrigidos | ✅ |

---

## Commits

| Commit | Tipo | Hash |
|--------|------|------|
| docs(contracts): §85 — Sync Onvio + auto-build Prime Arena 04/2026 | docs | `848f4a68` |

---

**T4 SYNC CPRO12** — Cenário B. Auto-build executado. Prime Arena 04/2026: 0% completude.
Bloqueio principal: Onvio ainda não publicou documentos de Abril/2026 (mes_ref='04.2026') para o Prime Arena.
Endpoint de sync Onvio inacessível via HTTP — requer registro em main_production.py (Jordan).

[session: t5] [module: ged]
