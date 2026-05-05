# T4 CPRO12 — Sync Onvio + Kit Prime Arena 04/2026
**Data:** 2026-05-05
**Executor:** Claude Sonnet 4.6 [session: t5] [module: ged]
**Tipo:** DIAGNÓSTICO + OPERAÇÃO (INV-3: código não modificado)

---

## Hipóteses Validadas

| H | Descrição | Resultado |
|---|-----------|---------|
| H1 | Docs Onvio de Março/2026 no banco | ✅ 43 docs mes_ref='03.2026'; Prime Arena: 2 (folha_pagamento + recibo_folha) |
| H2 | Prime Arena tem client_id mapeado | ✅ ged_clients.id=52958919 / condominios.id=21929c3d |
| H3 | Endpoint /onvio/sync existe e responde | ❌ HTTP 404 — router não registrado em main_production.py |
| H4 | Endpoint auto-build existe | ✅ POST /api/v1/ged/auto-assemble → HTTP 201 |
| H5 | Após sync, novos docs de Março aparecem | N/A — sync retornou 404; last sync foi 2026-05-04 (12 docs 03.2026) |
| H6 | Após auto-build, kit Prime Arena tem docs | ❌ 0 file_paths — mes_ref='04.2026' ausente para Prime Arena no Onvio |
| H7 | Endpoint /ged/kits/auto-build existe | ❌ HTTP 405 — URL casa com /kits/{kit_id} sem handler POST |
| H8 | Kit Prime Arena 04/2026 já existe | ✅ id=a5d04bc6, 133 slots GED / 94 esperados GEDEON |

---

## Estado pré-sync

Docs Onvio no banco: 605

Categorias presentes:

| categoria | total | min_mes | max_mes |
|-----------|-------|---------|---------|
| outros | 160 | 02.2026 | 2025 |
| folha_pagamento | 69 | 01.2026 | 12.2025 |
| recibo_folha | 68 | 01.2026 | 12.2025 |
| documento_digitalizado | 26 | 02.2026 | 04.2026 |
| das_simples_nacional | 21 | 11.2025 | 2026 |
| guia_issqn | 20 | 2025 | 2026 |
| parcelamento_simples | 20 | 2025 | 2026 |
| contrato_trabalho | 16 | — | — |
| ficha_registro | 13 | — | — |
| fgts_relatorio | 12 | 01.2026 | 12.2025 |
| dctfweb_declaracao | 12 | 01.2026 | 2025 |
| (+ 14 outras categorias) | 118 | | |

Prime Arena 04/2026 slots: 94 (GEDEON esperado) / 133 (ged_kit_documents real)

Docs preenchidos antes: 0

Completude antes: 0.0% (GEDEON) / 3.76% estale (ged_document_kits)

---

## Sync Onvio

HTTP status: 404 `{"detail":"Not Found"}`

Docs novos adicionados: 0

Resposta: endpoint `POST /api/v1/onvio/sync` não está registrado em main_production.py. O controller `modules.gedeon.controllers.onvio_controller` tem o endpoint na linha 84 mas não é importado no app. A última sync real foi em 2026-05-04 via cron interno (03.2026: 12 docs, 04.2026: 58 docs). Contagem ANTES=605, sleep 30s, DEPOIS=605.

**INV-4 aplicado:** erro documentado, não corrigido.

---

## Auto-build 04/2026

Endpoint usado: `POST /api/v1/ged/auto-assemble?reference_month=2026-04-01`

HTTP status: 201

Resposta:
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

Sleep 20s executado após o build. Operação 2 complementar: `POST /api/v1/ged/kits/montar` com `{"mes_ref":"04.2026"}` → HTTP 201, 3 kits novos (Conecta Matriz, Parise Village, Green Hills).

---

## Estado pós-build

Docs preenchidos depois: 0/94

Completude depois: 0.0%

Docs por tipo:

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

Confirmação via API `GET /api/v1/ged/kits?client_id=52958919&month=4&year=2026`:
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

---

## Docs faltantes (categorias sem arquivo)

Classificação por causa raiz:

**nao_encontrado_onvio (14 tipos)** — Onvio não tem mes_ref='04.2026' para Prime Arena:
folha_pagamento, contracheque, folhas_ponto, folha_ponto, escala_mes, gfd_fgts_mensal,
relatorio_gfd_fgts, gfd_fgts_rescisao, relatorio_gfd_rescisao, dctfweb_declaracao,
dctfweb_recibo, dctfweb_extrato, aso, contrato_trabalho, ficha_empregado, rescisao_contrato

**aguarda_fase_2_banco (9 tipos)** — integração bancária (FASE 2 GEDEON não implementada):
boleto, nfse, comp_pag_fgts, crf_fgts, comp_fgts_rescisao, comp_rescisao,
comp_salario_individual, comp_vt_individual, comprovante_va, comprovante_vr, comprovante_vt

**aguarda_fase_1_cnd (5 tipos)** — busca automática CND (FASE 1 GEDEON):
cnd_rfb, cnd_caixa, cnd_prefeitura, cnd_sefaz, cnd_trabalhista

**nao_sincronizado (4 tipos)** — VA/VT Sólides não configurados:
comp_va_solides, comp_vt_va_combinado, recibo_vt_va, relatorio_pedido_va

**Causa raiz principal:** KitBuilderService busca `onvio_documents WHERE mes_ref='04.2026'`
para Prime Arena. Docs de Abril/2026 ainda não publicados no Onvio (chegam entre 5–20/05/2026).
Adicional: endpoint `POST /onvio/sync` não registrado → impossível disparar sync manual via API.

---

## Próximos passos

Completude atual: 0% → Kit NÃO pronto para envio.

O que falta vincular:
1. **Aguardar** publicação de docs Abril/2026 no Onvio (folha, FGTS, DCTF-Web) — ETA 10–20/05/2026
2. **Registrar** `modules.gedeon.controllers.onvio_controller` em main_production.py (requer Jordan — Zona Proibida)
3. Após registro: rodar `POST /api/v1/gedeon/onvio/sync?mes_ref=04.2026` → depois `POST /api/v1/ged/auto-assemble?reference_month=2026-04-01`
4. **FASE 1** (CND): ativa automaticamente cnd_rfb, cnd_caixa, cnd_prefeitura, cnd_sefaz, cnd_trabalhista
5. **FASE 2** (banco): ativa automaticamente boleto, comp_pag_fgts, comp_salario_individual, etc.
6. **VA/VT Sólides**: configurar sync manual para comp_va_solides, recibo_vt_va, relatorio_pedido_va

---

## Achados Arquiteturais

| Achado | Impacto |
|--------|---------|
| 81% dos docs Onvio sem condominio_id | Auto-matching impossível para maioria dos docs |
| POST /onvio/sync HTTP 404 (não registrado) | Sync manual via API impossível |
| Path errado: gedeon.onvio.controllers vs gedeon.controllers | Router Onvio inacessível |
| KitBuilderService usa mes_ref=kit_month (não kit_month-1) | Docs Março só no kit de Março, não no de Abril |
| POST /ged/kits/auto-build → HTTP 405 | URL casa com /kits/{kit_id}; endpoint real é /ged/auto-assemble |
| documents_signed=5 em ged_document_kits | Valor stale; query direta confirma 0 file_paths |

---

## Self-check

| Item | Status |
|------|--------|
| STEP 0 — contrato lido, §83 confirmado, §13.1 + INV-8 citados | ✅ |
| STEP 1 — TOKEN obtido | ✅ |
| STEP 2 — estado pré-sync documentado (605 docs, categorias, kit_id, condominio_ids) | ✅ |
| STEP 3 — ANTES=605, sync HTTP 404, sleep 30s, DEPOIS=605, Novos=0 | ✅ |
| STEP 4 — /ged/auto-assemble (201) + /ged/kits/montar (201) + /ged/kits/auto-build (405) | ✅ |
| STEP 5 — auto-build 04/2026 disparado + sleep 20s | ✅ |
| STEP 6 — query ✅/❌ (38 tipos, 133 slots, 0 preenchidos) + API GED confirmada | ✅ |
| STEP 7 — §85 com campos template + commit 848f4a68 + push | ✅ |
| STEP 8 — relatório com estrutura exata do template + todos campos preenchidos | ✅ |
| INV-8 — kit NÃO enviado ao cliente | ✅ |
| INV-3 — código não modificado | ✅ |
| INV-4/5 — erros documentados, não corrigidos | ✅ |

---

## Commits

| Commit | Tipo | Hash |
|--------|------|------|
| docs(contracts): §85 Sync Onvio + auto-build Prime Arena 04/2026 | docs | `848f4a68` |
| docs(relatorio): T4-SYNC auditoria 100% — ANTES/DEPOIS + query ✅/❌ + API GED | docs | `f406f903` |
| docs: T4-SYNC auditoria 100% final — STEP4 /auto-build 405 + STEP5 sleep20 + §85 template | docs | `0dffd9f9` |
| docs: T4-SYNC relatório reescrito com estrutura exata do template STEP 8 | docs | (este commit) |

---

Commit: 848f4a68 (docs §85), f406f903 (audit pass 1), 0dffd9f9 (audit pass 2), (este — audit final)

T4 SYNC CPRO12 OK

[session: t5] [module: ged]
