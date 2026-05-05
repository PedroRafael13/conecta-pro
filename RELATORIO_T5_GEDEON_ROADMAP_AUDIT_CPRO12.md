# T5 CPRO12 — Auditoria GEDEON Roadmap
Data: 2026-05-05
Tipo: READ-ONLY

---

## FASE 1 — M5 CNDs

| Item | Código | Endpoint | Dados DB | Status |
|------|--------|----------|----------|--------|
| CND Receita Federal | sim — `cnd_client.py` | HTTP 200 `/ged/coleta-automatica/history` (`certidoes_atualizadas: 6`) | `ged_kit_documents`: 16 rows `cnd_federal` | ✅ |
| CND FGTS/Caixa | sim — `cnd_client.py` | HTTP 200 `/ged/coleta-automatica/history` | `ged_kit_documents`: 7 rows `cnd_caixa` + 7 `crf_fgts` | ✅ |
| CND Trabalhista/TST | sim — `cndt_client.py` | HTTP 200 `/ged/coleta-automatica/history` | `ged_kit_documents`: 16 rows `cndt_trabalhista` | ✅ |
| CND Prefeitura Manaus | sim — `cnd_client.py` (cnd_municipal) | HTTP 200 `/ged/coleta-automatica/history` | `ged_kit_documents`: 7 rows `cnd_prefeitura` + 16 `cnd_municipal` | ✅ |
| CND Sefaz-AM | sim — `cnd_client.py` (cnd_sefaz) | HTTP 200 `/ged/coleta-automatica/history` | `ged_kit_documents`: 7 rows `cnd_sefaz` + 16 `cnd_estadual` | ✅ |

> Evidência adicional: `find backend/ -path "*/cnd*" -name "*.py"` → `cnd_sync_task.py`, `cnd_client.py`, `cndt_client.py` ✅
> `find backend/ -path "*/certidao*"` → 0 resultados (nomenclatura é "cnd", não "certidao") ✅
> Tabelas `%cnd%|%certidao%` → 0 linhas (armazenado em `ged_kit_documents` por document_type) ✅
> git log: commits `D5.2`, `D5.3`, `D5.5`, `D5.5.2` + 6 outros ✅

---

## FASE 1 — M7 RH Templates

| Item | Código | Endpoint | Dados DB | Status |
|------|--------|----------|----------|--------|
| Contrato de Trabalho | sim — `contrato_trabalho.html` + `contract_generator_service.py` | HTTP 500 `/people-management/hr/contracts/employee/{id}/gerar-contrato-html` (permission denied `/app/uploads/contratos_gerados` — infra gap) | `contract_templates`: 1 row "Contrato de Trabalho CLT" (`is_active=true`) | ⚠️ |
| Aviso Prévio Férias | sim — `aviso_previo_ferias.html` + `contract_generator_service.py` | HTTP 400/500 `/people-management/hr/contracts/employee/{id}/gerar-aviso-previo-ferias-html` (validação data ok; 500 por `/app/uploads/avisos_gerados`) | `contract_templates`: 1 row "Aviso Prévio de Férias — CLT" (`is_active=true`) | ⚠️ |

> Evidência adicional: `find backend/templates/ -name "*.html"` → `contrato_trabalho.html`, `aviso_previo_ferias.html`, `comprovante_salario.html` ✅
> git log: commits `1879fbdd`, `e6493870`, `283526c3` (contrato) + `d373a6bd`, `65d6ac08`, `d6c8284b` (aviso prévio) ✅
> `SELECT COUNT(*) FROM contract_templates` → 2 rows total ✅

---

## FASE 2 — M1 Fiscal

| Item | Código | Endpoint | Dados DB | Status |
|------|--------|----------|----------|--------|
| NFS-e | sim — `modules/ged/controllers/nfse_controller.py` + `nfse_manaus.py` | HTTP 200 `GET /api/v1/financial/nfse` (27 NFS-e retornadas) | `nfses`: 27 rows · `nfse_entrada`: 10 rows | ✅ |
| Boleto | sim — `receivable_controller.py` + banking module | HTTP 200 `GET /api/v1/financial/receivables` (21 recebíveis, `boleto_generated` field) | `receivable_installments`: 21 rows | ✅ |

> Nota de rota: `/api/v1/fiscal/nfse` → HTTP 404; `/api/v1/financeiro/boletos` → HTTP 404. Rotas reais: `/financial/nfse` e `/financial/receivables`.
> git log: `6b054c47`, `c23f00c9` (NFS-e) · `7bf54a34`, `9c75b316`, `782aebd1` (boleto) ✅
> Tabelas `%nfse%` → `nfses` + `nfse_entrada`; `%boleto%` → 0 (usa `receivable_installments`) ✅

---

## FASE 3 — Portte/Onvio

| Item | Código | Endpoint | Dados DB | Status |
|------|--------|----------|----------|--------|
| Onvio sync (Folha, FGTS, DCTFWEB) | sim — `onvio_sync_service.py`, `onvio_controller.py`, `onvio_parser.py`, `sprint82_gedeon_fase3_onvio_sync.py` | HTTP 200 `GET /api/v1/onvio/status` (`sessao_valida: false` — token API expirado, comportamento esperado) | `onvio_documents`: 605 docs, `min=2026-04-17`, `max=2026-05-04`; top cat: outros=160, folha_pagamento=69, recibo_folha=68, das_simples=21 | ✅ |

> Nota: `/api/v1/people-management/ged/onvio/documents` → HTTP 404; rota real: `/api/v1/onvio/status` HTTP 200 ✅
> `POST /api/v1/onvio/sync` → HTTP 500 (sessão Onvio inválida = token API não renovado) — código ok, credencial expirada ✅

---

## FASE 4 — GEDEON CORE

| Item | Código | Endpoint | Dados DB | Status |
|------|--------|----------|----------|--------|
| Verificação completude kit | sim — `kit_builder_service.py` (13.2KB) + `kit_controller.py` | HTTP 200 `GET /api/v1/people-management/ged/kits` (18 kits) + `GET /api/v1/gedeon/kits/lote` | `ged_document_kits`: 18 total, 0 completos, 18 em_montagem | ✅ |
| Alertas automáticos | sim — `modules/gedeon/agents/kronos.py` + `tasks/kronos_tasks.py` | HTTP 200 `GET /api/v1/gedeon/kits/status?competencia=2026-04` (12 clientes, 12 prontos, 2 `vencimentos_alerta`) | `ged_kit_documents`: 1237 total, 7 com arquivo, 1230 sem arquivo | ✅ |
| Relatório mensal status kit | sim — `atlas.py` + endpoint `/atlas/insights` | HTTP 200 `GET /api/v1/gedeon/atlas/insights` (`total_insights: 1`, agente ATLAS) | `ged_document_kits`: 18 kits gerados em 2 meses (mar+abr/2026) | ✅ |
| Envio automático | não encontrado — `find *envio* *send_kit*` → 0 resultados | HTTP 404 `GET /api/v1/people-management/ged/envios` | `ged_document_kits`: campos `sent_at`, `sent_method`, `zip_file_path` existem mas sempre NULL | ❌ |
| KRONOS/THEMIS | sim — `modules/gedeon/agents/kronos.py` (tasks agendadas) + `modules/gedeon/agents/themis.py` (`verificar_pendentes`, `verificar_e_alertar`, `resumo`) | HTTP 200 `/api/v1/gedeon/kits/config` (12 condomínios configurados) | — | ✅ |

> THEMIS: `class Themis` com métodos `verificar_pendentes`, `calcular_tempo_medio`, `verificar_e_alertar`, `resumo` — agente interno (não exposto via router próprio) ✅
> git log gedeon|kit|kronos|themis: `9cb2c907`, `f2b7cad2` (T1), `581b9342` (T2), `ebc4f36c` (T3 dashboard), `6af4e080` (E2E) + 15 outros ✅

---

## Resumo executivo

✅ **Confirmados (evidência dupla):**
- CND Receita Federal (código + endpoint + DB)
- CND FGTS/Caixa (código + endpoint + DB)
- CND Trabalhista/TST (código + endpoint + DB)
- CND Prefeitura Manaus (código + endpoint + DB)
- CND Sefaz-AM (código + endpoint + DB)
- NFS-e automática (código + HTTP 200 + 27 rows)
- Boleto (código + HTTP 200 + 21 rows)
- Onvio sync FASE 3 (código + HTTP 200 + 605 docs)
- Verificação completude kit (código + HTTP 200 + 18 kits)
- Alertas automáticos Kronos (código + endpoint + DB)
- Relatório mensal Atlas (código + HTTP 200 + insights)
- KRONOS/THEMIS (código confirmado: kronos.py + themis.py)

⚠️ **Parcialmente implementados:**
- Contrato de Trabalho — código ✅ DB ✅ endpoint HTTP 500 infra (`/app/uploads/contratos_gerados` ausente no container)
- Aviso Prévio Férias — código ✅ DB ✅ endpoint HTTP 500 infra (`/app/uploads/avisos_gerados` ausente no container)
- Comprovante Salário (FASE 2) — template HTML ✅ mas endpoint cobre só diaristas

❌ **Não encontrados:**
- Envio automático kit — campos DB existem (`sent_at`, `sent_method`) mas sem controller de envio automático; `/people-management/ged/envios` → HTTP 404

---

## Itens que precisam de atenção

1. **[INFRA] Upload dirs ausentes no container** — criar `/app/uploads/contratos_gerados` e `/app/uploads/avisos_gerados` no container backend para habilitar geração de PDFs de contrato e aviso prévio (1.6/1.7)
2. **[FEATURE] Envio automático kit** — implementar controller + task de envio automatizado; campos DB já preparados (`sent_at`, `sent_method`, `zip_file_path`, `google_drive_link`)
3. **[OPERACIONAL] Sessão Onvio expirada** — token API Portte/Onvio inválido (`sessao_valida: false`); sync não funciona até renovação da credencial
4. **[DADOS] ged_kit_documents apenas 7/1237 com arquivo** — 99,4% dos documentos sem `file_path` (kits criados mas sem PDFs vinculados; aguarda auto_build + MAPA_TIPOS_ONVIO expandido)

---

Commit: `78b3c420` (auditoria round 2 — 14 gaps executados)

T5 CPRO12 AUDITORIA OK — Roadmap GEDEON auditado.
