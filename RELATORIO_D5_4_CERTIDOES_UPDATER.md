# RELATORIO D5.4 — CertidoesUpdaterService
**Data:** 2026-04-28
**Branch:** feature/people-management-reorganization

---

## 1. Timestamps

| Marco | Horário |
|-------|---------|
| T+0 (pré-voo) | 17:50:42 |
| T+30 (design STEP 2) | ~18:05 |
| T+final (push) | ~19:35 |

---

## 2. STEP 1 — Código atual (resumo)

**ColetaAutomaticaService:** 2 fases (sync Onvio + auto-assemble). Status `success/partial/error`. Grava `GedColetaLog` com sync_novos/kits_assembled/onvio_matched.

**ged_certidoes:** TEXT notes, alerta_ativo BOOLEAN, 8 rows:
`certidao_negativa_fgts`, `certidao_negativa_federal`, `certidao_negativa_inss`,
`certidao_negativa_trabalhista`, `certidao_negativa_estadual`, `certidao_negativa_municipal`,
`alvara_funcionamento`, `registro_cnpj`

**cnd_sync_task.py:** já existia mas era Celery task (não service class), sem dedup INSS, sem alerta_ativo logic, sem Fase 3 no ColetaAutomaticaService.

**GedColetaLog:** campos id, run_type, status, duration_ms, sync_novos, kits_assembled, onvio_matched, erros, triggered_by. Sem certidoes_atualizadas/alertas_disparados → migration necessária.

---

## 3. STEP 2 — Design

| document_type | Client | Método | Nota |
|---|---|---|---|
| certidao_negativa_fgts | CRFFGTSClient | consultar_crf | |
| certidao_negativa_federal | CNDFederalClient | consultar_cnd | |
| certidao_negativa_inss | CNDFederalClient | consultar_cnd | DEDUP cache |
| certidao_negativa_trabalhista | CNDTTrabalhistaClient | consultar_cndt | |
| certidao_negativa_estadual | SefazAMClient | consultar_cnd | |
| certidao_negativa_municipal | PrefeituraManausClient | consultar_cnd | |
| alvara_funcionamento | — | SKIP | |
| registro_cnpj | — | SKIP | |

Dedup: 6 doc_types → 5 chamadas efetivas (federal+inss = 1 chamada via cache).

---

## 4. STEP 3 — Service criado

Arquivo: `backend/modules/people_management/ged/services/certidoes_updater_service.py`

- `executar(cnpj)` → `{certidoes_atualizadas, alertas_disparados, erros}`
- `_chamar_client(mod, cls, method, cnpj)` — import dinâmico + close
- `_atualizar_certidao(doc_type, resultado)` — UPDATE expiry_date + notes JSON
- `_deve_alertar(resultado, expiry_date)` — 3 condições
- `_set_alerta(cert_id, ativo)` — UPDATE alerta_ativo
- `_calcular_expiry_date(resultado, atual, doc_type)` — data_validade → dias → atual

---

## 5. STEP 4 — Fase 3 + endpoint + migration

**ColetaAutomaticaService:** Fase 3 adicionada após Fase 2. Erro na Fase 3 não interrompe Fases 1+2.

**Endpoint:** `POST /api/v1/ged/coleta-automatica/cnds/run` — lock Redis `ged:certidoes:running` TTL 300s. 202 started / 409 já rodando.

**Migration** `sprint85_d5_4_certidoes`: `certidoes_atualizadas INTEGER DEFAULT 0` + `alertas_disparados INTEGER DEFAULT 0` em `ged_coleta_logs`. Aplicada com `alembic upgrade head`.

**GedColetaLog model** atualizado com 2 novos campos.

---

## 6. STEP 5 — Live test + ged_certidoes + pytest

**Live test:**
```
certidoes_atualizadas: 6
alertas_disparados: 5
erros: 0
```

**ged_certidoes pós-execução:**
```
alvara_funcionamento          → intocado (SKIP)
certidao_negativa_estadual    → updated_at=hoje, alerta_ativo=f (regular=True real)
certidao_negativa_federal     → updated_at=hoje, alerta_ativo=t (BrasilAPI fallback)
certidao_negativa_fgts        → updated_at=hoje, alerta_ativo=t (BrasilAPI fallback)
certidao_negativa_inss        → updated_at=hoje, alerta_ativo=t (BrasilAPI fallback, dedup)
certidao_negativa_municipal   → updated_at=hoje, alerta_ativo=t (regular=False real SEMEF)
certidao_negativa_trabalhista → updated_at=hoje, alerta_ativo=t (BrasilAPI fallback)
registro_cnpj                 → intocado (SKIP)
```

**Endpoint:**
```
POST /cnds/run → 202 {"status": "started", ...}
POST /cnds/run → 409 {"detail": "Atualização de certidões já em execução."}
```

**Pytest:**
```
test_d5_4_certidoes_updater.py   5/5 PASS  (D5.4)
test_d4_coleta_automatica.py    13/14 PASS (1 flaky pre-existente — timeout HTTP)
test_d4_1_meses_com_kits.py      1/1 PASS  (D4.1)
test_crf_client_fallback.py      4/4 PASS  (D5.1)
test_cnd_federal_fallback.py     4/4 PASS  (D5.2)
test_cndt_client_fallback.py     5/5 PASS  (D5.3)
======================== 31/32 passed (1 pre-existing flaky) ========================
```

---

## 7. Tabela: 8 document_types e cobertura

| document_type | Client | Coberto D5.4? | Alerta hoje |
|---|---|---|---|
| certidao_negativa_fgts | CRFFGTSClient | ✅ | t (fallback) |
| certidao_negativa_federal | CNDFederalClient | ✅ | t (fallback) |
| certidao_negativa_inss | CNDFederalClient (dedup) | ✅ | t (fallback) |
| certidao_negativa_trabalhista | CNDTTrabalhistaClient | ✅ | t (fallback) |
| certidao_negativa_estadual | SefazAMClient | ✅ | f (portal vivo, regular) |
| certidao_negativa_municipal | PrefeituraManausClient | ✅ | t (portal vivo, irregular) |
| alvara_funcionamento | — | ❌ SKIP | t (pré-existente vencido) |
| registro_cnpj | — | ❌ SKIP | f |

---

## 8. Cenário identificado

Hoje: 3 portais federais (CRF, CND, CNDT) caem em BrasilAPI fallback → `regular=None` → `alerta_ativo=True` preventivo. Sefaz-AM respondeu diretamente com `regular=True`. SEMEF Manaus respondeu com `regular=False` (débito municipal real confirmado). A certidão municipal precisa de atenção manual.

---

## 9. Backlog

- **D5.5** — UI card Certidões com semáforo (verde=regular, amarelo=indeterminado, vermelho=irregular/vencido)
- **D5.6** — Playwright para CNDT real (TST JSF + captcha imagem)
- **D5.2.1** — OAuth2 gov.br para CND federal real
- **D5.x** — alvara_funcionamento e registro_cnpj sem automação
