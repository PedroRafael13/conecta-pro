# RELATÓRIO — GEDEON BLOCO C: EXTENSÃO 9 CONDOMÍNIOS 04/2026
**Data:** 2026-04-22
**Branch:** feature/people-management-reorganization
**Sessão:** tmux-t1 [module: ged]

---

## 1. STEP 0 — Pré-voo (BLOCO B confirmado)

```
grep "Versão:" CONTRACTS_GEDEON.md | head -1
→ Versão: v1.35

SELECT templates, presencas, kits, docs:
→ 32 | 320 | 1 | 83
```

| Check | Resultado |
|-------|-----------|
| Contrato v1.35? | ✅ sim |
| Estado BLOCO B (32/320/1/83)? | ✅ exato |
| Objetivo BLOCO C | Criar 9 kits em 04/2026 para os condomínios restantes (LARANJEIRAS já feito). ESCRITÓRIO SKIP por 0 templates. Total esperado: 552 docs todos placeholders. |

---

## 2. STEP 1 — 5 Investigações

### 1.1 — Mapear ged_clients dos 10 condomínios

> ⚠️ Schema discovery: `ged_clients.condominio_id` NÃO EXISTE (sem FK para condominios).
> A query do prompt (`LEFT JOIN ged_clients gc ON gc.condominio_id = c.id`) falha com
> `ERROR: column gc.condominio_id does not exist`. Mapeamento feito via SELECT direto
> em ged_clients + matching por nome (bug com ILIKE duplicatas → corrigido para UUID hardcoded).

Mapeamento final confirmado (via SELECT id, name FROM ged_clients ORDER BY name):

| nome_normalizado | condominio_id | ged_client_id |
|-----------------|---------------|---------------|
| prime_arena | `21929c3d-f469-4eb4-8309-4d8201231100` | `52958919-0a15-4e4f-806d-be3c75e5951b` |
| ideal_flores | `215a124b-2dd7-4125-ab3f-6efa3aa67c99` | `4db583b6-815a-494f-a1e3-0c62fa81eca9` |
| mirante | `dfa6645a-5061-4b4d-b64a-aada36f2b732` | `130186bf-9e37-4fba-bf19-817292df4ace` |
| villa_dei_fiori | `ef2f9c03-e2d7-4a10-8458-e26c9a696f69` | `14809ac8-f5e1-4dac-848c-4f5e0c347ecc` |
| villa_passaros | `6fb88de2-4093-451f-b188-e60c318c0b2a` | `4909237d-1003-41cd-a404-bcbe08f9c2cf` |
| michelangelo | `b3ca559f-2728-4238-916e-5e303d70b4e6` | `02d784d5-c150-479b-94fa-7f3615072e79` |
| green_hills | `4900de33-c778-4792-818d-e0901b559aed` | `b4a13504-cffc-4505-8e91-e1bebed493ed` |
| p_gelain | `ab146423-859e-4e6e-aeaf-041987a18f25` | `8199960d-42be-43ba-b0cb-ccf342bfb601` |
| parise | `9be1e32b-0ff1-4668-9094-74f720c9a487` | `d4dd6c53-222f-4c6d-a864-6d0856cd53d5` |
| laranjeiras | `7c2323fd-e226-4121-806d-d9b2598feeed` | `e55f6f4c-a641-4b08-9584-eef61dcb5575` |
| escritorio | — | — (sem ged_client para kit — SKIP) |

**Decisão:** todos os 9 têm ged_client_id. Prosseguir. ✅

### 1.2 — Contagem de templates aplicáveis por condomínio

```sql
SELECT c.nome_normalizado,
       COUNT(*) FILTER (WHERE p.presenca='obrigatorio') AS obrig,
       COUNT(*) FILTER (WHERE p.presenca='eventual') AS eventual,
       COUNT(*) FILTER (WHERE p.presenca='na') AS na
FROM condominios c
LEFT JOIN kit_template_presenca p ON p.condominio_id=c.id
GROUP BY c.nome_normalizado ORDER BY c.nome_normalizado;
```

Output (extrato relevante):
```
 escritorio      |  0 |  0 | 32
 green_hills     |  2 |  0 | 30
 ideal_flores    | 30 |  2 |  0
 laranjeiras     | 28 |  2 |  2
 michelangelo    | 21 |  2 |  9
 mirante         | 28 |  2 |  2
 p_gelain        |  2 |  0 | 30
 parise          |  2 |  0 | 30
 prime_arena     | 28 |  2 |  2
 villa_dei_fiori | 24 |  2 |  6
 villa_passaros  | 20 |  2 | 10
```

**ESCRITÓRIO: obrig=0 → SKIP confirmado** ✅

### 1.3 — N funcionários ativos em 04/2026 por condomínio

```sql
SELECT c.nome_normalizado, COUNT(DISTINCT ea.employee_id) AS n_func
FROM condominios c
LEFT JOIN employee_alocacoes ea ON ea.condominio_id=c.id
  AND (ea.data_fim IS NULL OR ea.data_fim >= '2026-04-01')
  AND ea.data_inicio <= '2026-04-30'
GROUP BY c.nome_normalizado ORDER BY n_func DESC;
```

Output:
```
 ideal_flores    | 11
 mirante         | 10
 prime_arena     |  7
 laranjeiras     |  6
 villa_dei_fiori |  6
 villa_passaros  |  6
 michelangelo    |  1
 escritorio      |  0
 green_hills     |  0
 p_gelain        |  0
 parise          |  0
```

**Valores batem com BLOCO A (7,11,10,6,6,1)** ✅

> Nota: VILLA PÁSSAROS aparece com 6 (não 6 como em BLOCO A §37.1 col "N func=6" ✅).

### 1.4 — Script BLOCO B reutilizável em loop

Leitura de `backend/scripts/seed_bloco_b_laranjeiras_042026.py` confirmou:
- Lógica de idempotência via SELECT antes de INSERT ✅
- Guard `if eh_eventual and fp is None: continue` ✅
- Estrutura refatorável: extrair `processar_condominio(db, nome)` ✅

### 1.5 — PDFs 04/2026 no servidor

```bash
find /opt/conecta-pro/uploads -type f -iname "*04.2026*" 2>/dev/null | wc -l
→ 0

find /opt/conecta-pro/uploads -type f \
  \( -iname "*2026-04*" -o -iname "*abril*" -o -iname "*abr.2026*" \) 2>/dev/null | wc -l
→ 0
```

**0 PDFs de 04/2026 no servidor** — Cenário C (todos placeholders) ✅

### Decisão STEP 1

| Check | Status |
|-------|--------|
| 10 condomínios têm ged_client_id? | ✅ sim (9 com kit + escritório sem) |
| ESCRITÓRIO tem obrig=0 templates? | ✅ confirma SKIP |
| N funcionários bate com BLOCO A (7,11,10,6,6,1)? | ✅ exato |
| Script BLOCO B é parametrizável em loop? | ✅ sim |
| PDFs 04/2026 no servidor? | 0 (esperado) |

---

## 3. STEP 2 — §37 no Contrato

- CONTRACTS_GEDEON.md v1.35 → v1.36
- §37.1 a §37.5 adicionados: escopo, totais, script loop, resultado, próximos passos, fora de escopo
- **Commit 1:** `ba4f8da4` — `docs(gedeon): CONTRATO v1.36 — §37 BLOCO C extensão 9 condomínios`

---

## 4. STEP 3 — Seed executado

### 4.1 — Backup SQL
```
/tmp/backup_before_bloco_c_20260422_160950.sql
-rw-r--r-- 1 root root 26788 Apr 22 16:09 /tmp/backup_before_bloco_c_20260422_160950.sql
```

### 4.2 — Script criado
`backend/scripts/seed_bloco_c_extensao_042026.py`

### 4.3 — Output do seed (9 condomínios processados)

```
======================================================================
GEDEON BLOCO C — Extensão 9 condomínios 04.2026
======================================================================

▶ Processando: prime_arena
  ✅ kit_id=a5d04bc6-ca53-4978-b32b-41873df8b4be
     docs inseridos: 94

▶ Processando: ideal_flores
  ✅ kit_id=55a1e366-9a6d-4e8d-acb2-c7afb2fa24b1
     docs inseridos: 127

▶ Processando: mirante
  ✅ kit_id=c33e5408-82eb-4fe9-9d18-4cd97c51d2e2
     docs inseridos: 116

▶ Processando: villa_dei_fiori
  ✅ kit_id=c4053743-1abf-4f08-a760-2a334488985d
     docs inseridos: 64

▶ Processando: villa_passaros
  ✅ kit_id=32cd60d2-4650-40bc-ad89-2c8d9cc35863
     docs inseridos: 45

▶ Processando: michelangelo
  ✅ kit_id=24d76d61-ed97-4864-80d5-29dde37a150e
     docs inseridos: 17

▶ Processando: green_hills
  ✅ kit_id=a5fa41d8-cf96-4688-9c6a-a3f6fb56432a
     docs inseridos: 2

▶ Processando: p_gelain
  ✅ kit_id=dfcfb2af-d2cf-4626-9148-af55b0f172eb
     docs inseridos: 2

▶ Processando: parise
  ✅ kit_id=af4f1cdf-5260-410a-bb5f-7dfaa99316e5
     docs inseridos: 2

======================================================================
BLOCO C — RESUMO
======================================================================
  Kits criados:    9
  Docs inseridos:  469
  Skipped:         0
  Total kits 04/2026 (incluindo LARANJEIRAS): 10
  Total docs  04/2026 (incluindo LARANJEIRAS): 552
```

### 4.4 — Confirmação no DB (STEP 3.4)

> ⚠️ A query exata do prompt usa `JOIN condominios c ON c.id=gc.condominio_id` — esta coluna
> não existe em `ged_clients` (schema discovery BLOCO B). Query equivalente executada:

```sql
SELECT gc.name, dk.id AS kit_id, dk.reference_month,
       COUNT(gkd.id) AS docs_total,
       COUNT(gkd.id) FILTER (WHERE gkd.file_path IS NOT NULL) AS com_pdf,
       COUNT(gkd.id) FILTER (WHERE gkd.file_path IS NULL) AS faltantes
FROM ged_document_kits dk
JOIN ged_clients gc ON gc.id = dk.client_id
LEFT JOIN ged_kit_documents gkd ON gkd.kit_id = dk.id
WHERE dk.reference_month = '2026-04-01'
GROUP BY gc.name, dk.id, dk.reference_month ORDER BY gc.name;
```

Output (10 rows, ESCRITÓRIO NÃO aparece ✅):
```
 CONDOMINIO DO EDIFICIO MICHELANGELO       | 24d76d61-... | 2026-04-01 | 17  | 0 | 17
 CONDOMINIO IDEAL FLORES DA CIDADE         | 55a1e366-... | 2026-04-01 | 127 | 0 | 127
 CONDOMINIO MIRANTE DAS FLORES             | c33e5408-... | 2026-04-01 | 116 | 0 | 116
 CONDOMINIO PARQUE RESIDENCIAL GELAIN      | dfcfb2af-... | 2026-04-01 | 2   | 0 | 2
 CONDOMINIO PRIME ARENA                    | a5d04bc6-... | 2026-04-01 | 94  | 0 | 94
 CONDOMINIO RESIDENCIAL GREEN HILLS        | a5fa41d8-... | 2026-04-01 | 2   | 0 | 2
 CONDOMINIO RESIDENCIAL PARISE VILLAGE     | af4f1cdf-... | 2026-04-01 | 2   | 0 | 2
 CONDOMINIO RESIDENCIAL VILLA DOS PASSAROS | 32cd60d2-... | 2026-04-01 | 45  | 0 | 45
 CONDOMINIO VILLA DEI FIORI                | c4053743-... | 2026-04-01 | 64  | 0 | 64
 RESIDENCIAL LARANJEIRAS VILLAGE           | 0107be85-... | 2026-04-01 | 83  | 0 | 83
```

Totais agregados: `kits_04=10, docs_04=552` ✅

### 4.5 — Idempotência testada (STEP 3.5)

2ª execução: todos os 9 → SKIP (kit já existe). `COUNT(*) = 10` (não duplicou). ✅

### 4.6 — Testes pytest criados (STEP 3.6)

`backend/tests/modules/gedeon/test_seed_bloco_c.py` — 13 testes em 4 classes:
- `TestBlocoC` (5): kits=10, docs=552, todos placeholder, totais×condomínio, ESCRITÓRIO sem kit
- `TestBlocoCIdempotencia` (2): 10 kits exatos, 552 docs exatos após rerun
- `TestBlocoCLaranjeirasPreservado` (2): UUID preservado, 83 docs intactos
- `TestBlocoCZonasProibidas` (4): templates=32, presencas=320, onvio≥436, 03/2026 preservado

Resultado: **13/13 PASS** ✅

### 4.7 — Smoke endpoint (STEP 3.7)

```
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8080/api/v1/gedeon/kits/lote?mes_ref=04.2026"

Condomínios: 11
  ESCRITÓRIO                          esperado=   0 presente=  0 pct=0.0%
  GREEN HILLS                         esperado=   2 presente=  0 pct=0.0%
  IDEAL FLORES                        esperado= 127 presente=  0 pct=0.0%
  LARANJEIRAS                         esperado=  83 presente=  0 pct=0.0%
  MICHELANGELO                        esperado=  17 presente=  0 pct=0.0%
  MIRANTE                             esperado= 116 presente=  0 pct=0.0%
  P. GELAIN                           esperado=   2 presente=  0 pct=0.0%
  PARISE                              esperado=   2 presente=  0 pct=0.0%
  PRIME ARENA                         esperado=  94 presente=  0 pct=0.0%
  VILLA DEI FIORI                     esperado=  64 presente=  0 pct=0.0%
  VILLA PÁSSAROS                      esperado=  45 presente=  0 pct=0.0%
```

11 condomínios. ESCRITÓRIO esperado=0. Todos 0.0%. Valores canônicos corretos. ✅

---

## 5. STEP 4 — Validações 🔴

| ID | Check | Resultado |
|----|-------|-----------|
| 🔴A | pytest gedeon 85/85 (55 BLOCO A + 17 BLOCO B + 13 BLOCO C) | ✅ PASS |
| 🔴B | GET /gedeon/kits/lote sem auth → 401 | ✅ 401 |
| 🔴C | DB: cond=11, aloc=47+, tpl=32, presenca=320, onvio=436, cert=7+, kits=10, docs=552 | ✅ EXACT |
| 🔴D | Endpoint retorna 11 condomínios com valores canônicos esperados | ✅ |
| 🔴E | LARANJEIRAS UUID `0107be85-0109-464e-a80b-3665c666dd01` preservado | ✅ |
| 🔴F | Zero diff em zonas proibidas (kit_builder_service, kit_controller, alembic, scripts BLOCO A/B, frontend) | ✅ 0 bytes |

**Detalhe 🔴C (psql — 8 contagens exatas do prompt):**
```
 cond | aloc | tpl | presenca | onvio | cert | kits | docs
------+------+-----+----------+-------+------+------+------
   11 |   47 |  32 |      320 |   436 |    8 |   10 |  552
```
Esperado: `11, 47+, 32, 320, 436, 7+, 10, 552` → **Obtido: 11, 47, 32, 320, 436, 8, 10, 552 ✅**

**Detalhe 🔴E (psql — query exata do prompt):**
```sql
SELECT id, reference_month FROM ged_document_kits
WHERE id='0107be85-0109-464e-a80b-3665c666dd01';
→ 0107be85-0109-464e-a80b-3665c666dd01 | 2026-04-01   (1 row) ✅
```

---

## 6. STEP 5 — Commits

| # | Commit | Hash | Mensagem |
|---|--------|------|---------|
| 1 (docs) | `ba4f8da4` | docs(gedeon): CONTRATO v1.36 — §37 BLOCO C extensão 9 condomínios |
| 2 (code) | `017d9c94` | feat(gedeon): BLOCO C — extensão 9 condomínios 04/2026 (§37) |

Arquivos no commit 2:
- `backend/scripts/seed_bloco_c_extensao_042026.py` (novo)
- `backend/tests/modules/gedeon/test_seed_bloco_c.py` (novo)
- `backend/tests/modules/gedeon/test_seed_bloco_b.py` (fix: total_kits 1→10, necessário pois BLOCO B test quebrava com 10 kits)

**Push:** `feature/people-management-reorganization` → origin ✅

---

## 7. Self-check 12/12

| # | Item do prompt | Status |
|---|----------------|--------|
| 1 | STEP 0 — BLOCO B confirmado (32/320/1/83) | ✅ |
| 2 | STEP 1 — ged_clients dos 10 mapeados | ✅ (9 com kit + escritório sem) |
| 3 | STEP 1 — ESCRITÓRIO confirmado com 0 templates (SKIP) | ✅ obrig=0 |
| 4 | STEP 1 — N funcionários bate com BLOCO A (7,11,10,6,6,1) | ✅ |
| 5 | STEP 2 — §37 em v1.36 + commit 1 `ba4f8da4` | ✅ |
| 6 | STEP 3 — Backup SQL criado antes de INSERT | ✅ |
| 7 | STEP 3 — Script executado: 10 kits, 552 docs | ✅ |
| 8 | STEP 3 — Idempotência validada (rodar 2x não duplica) | ✅ |
| 9 | STEP 3 — Testes pytest novos criados e PASS | ✅ 13/13 |
| 10 | STEP 4 — 6 validações 🔴 PASS (F=zero diff) | ✅ |
| 11 | STEP 4 — LARANJEIRAS UUID `0107be85-...` preservado | ✅ |
| 12 | STEP 5 — Commit 2 `017d9c94` + push + hash anotado | ✅ |

---

## 8. Cenário identificado

**CENÁRIO C** (parcial) em todos os 9 condomínios: 0% PDFs localizados.
04/2026 ainda não sincronizado via Onvio (competência aberta em 22/04).
Todos os 469 docs novos = placeholders (file_path=NULL).
Eventuais (rescisao_contrato + comp_rescisao): NÃO inseridos.

---

## 9. Tabela 10 kits × total_esperado × N_funcionarios × kit_id

| Condomínio | Esperado | N_func | Com PDF | Placeholder | kit_id |
|-----------|---------|--------|---------|-------------|--------|
| RESIDENCIAL LARANJEIRAS VILLAGE | 83 | 6 | 0 | 83 | `0107be85-0109-464e-a80b-3665c666dd01` |
| CONDOMINIO PRIME ARENA | 94 | 7 | 0 | 94 | `a5d04bc6-ca53-4978-b32b-41873df8b4be` |
| CONDOMINIO IDEAL FLORES DA CIDADE | 127 | 11 | 0 | 127 | `55a1e366-9a6d-4e8d-acb2-c7afb2fa24b1` |
| CONDOMINIO MIRANTE DAS FLORES | 116 | 10 | 0 | 116 | `c33e5408-82eb-4fe9-9d18-4cd97c51d2e2` |
| CONDOMINIO VILLA DEI FIORI | 64 | 6 | 0 | 64 | `c4053743-1abf-4f08-a760-2a334488985d` |
| CONDOMINIO RESIDENCIAL VILLA DOS PASSAROS | 45 | 6 | 0 | 45 | `32cd60d2-4650-40bc-ad89-2c8d9cc35863` |
| CONDOMINIO DO EDIFICIO MICHELANGELO | 17 | 1 | 0 | 17 | `24d76d61-ed97-4864-80d5-29dde37a150e` |
| CONDOMINIO RESIDENCIAL GREEN HILLS | 2 | 0 | 0 | 2 | `a5fa41d8-cf96-4688-9c6a-a3f6fb56432a` |
| CONDOMINIO PARQUE RESIDENCIAL GELAIN | 2 | 0 | 0 | 2 | `dfcfb2af-d2cf-4626-9148-af55b0f172eb` |
| CONDOMINIO RESIDENCIAL PARISE VILLAGE | 2 | 0 | 0 | 2 | `af4f1cdf-5260-410a-bb5f-7dfaa99316e5` |
| **TOTAL** | **552** | — | **0** | **552** | — |

---

## 10. Status Final

**TRILOGIA GEDEON A/B/C FECHADA — aguardando E2E CIC Jordan validar dashboard completo + próximos passos do roadmap.**

10 kits placeholders em 04/2026 aguardando PDFs.

- 10 kits criados em 04/2026 ✅
- 552 placeholders prontos ✅
- LARANJEIRAS UUID preservado: `0107be85-0109-464e-a80b-3665c666dd01` ✅
- Regressão BLOCO A: 55/55 PASS ✅
- Testes BLOCO B: 17/17 PASS ✅
- Testes BLOCO C: 13/13 PASS ✅
- Total: **85/85 PASS** ✅
- Commits: `ba4f8da4` (docs §37) + `017d9c94` (código) + `802b381e` (auditoria) ✅

---

## Artefatos Produzidos

```
backend/scripts/seed_bloco_c_extensao_042026.py   (novo — commit 017d9c94)
backend/tests/modules/gedeon/test_seed_bloco_c.py (novo — commit 017d9c94)
backend/tests/modules/gedeon/test_seed_bloco_b.py (fix total_kits 1→10 — commit 017d9c94)
CONTRACTS_GEDEON.md  (v1.35 → v1.36, §37 adicionado — commit ba4f8da4)
RELATORIO_BLOCO_C_EXTENSAO.md (este arquivo)
```

## Zonas NÃO Tocadas (§13.4 Chesterton Preservado)

- `backend/modules/gedeon/services/kit_builder_service.py` — intocado ✅
- `backend/modules/gedeon/controllers/kit_controller.py` — intocado ✅
- `backend/modules/gedeon/schemas/` — intocado ✅
- `backend/alembic/versions/` — intocado ✅
- `backend/modules/financial/` — intocado ✅
- `backend/modules/government_integrations/` — intocado ✅
- `main_production.py` — intocado ✅
- `docker-compose*.yml` — intocado ✅
- `.env*` — intocado ✅
- `frontend/` — intocado ✅
- `kit_documental_templates` (32 rows) — intacto ✅
- `kit_template_presenca` (320 rows) — intacto ✅
- `onvio_documents` (436 rows) — intacto ✅
- `ged_certidoes` (8 rows) — intacto ✅
- LARANJEIRAS kit (83 docs, UUID `0107be85-...`) — intacto ✅
- `backend/scripts/seed_bloco_a_*.py` — intocado ✅
- `backend/scripts/seed_bloco_b_*.py` — intocado ✅
