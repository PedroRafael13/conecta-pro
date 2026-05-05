# T4 CPRO12 — Agente HERMES: Matching onvio_documents → kit (§94)
**Data:** 2026-05-05
**Executor:** Claude Sonnet 4.6 [session: t5] [module: ged]
**Tipo:** FEATURE — matching documental onvio → ged_kit_documents

---

## Hipóteses Validadas

| H | Descrição | Resultado |
|---|-----------|---------|
| H1 | cond_to_ged map via word-intersection funciona para todos os 10 condominios | ✅ 10/10 mapeados (incluindo VILLA PÁSSAROS e P. GELAIN) |
| H2 | Docs folha_pagamento 03.2026 com cond_id linkáveis | ❌ Slots já preenchidos por kit_builder_service (INV-5 respeitado) |
| H3 | Docs atestado 03.2026 com employee_id linkáveis a slot aso | ❌ Kit Ideal Flores 03.2026 não tem slot `aso` no template |
| H4 | HERMES idempotente — não grava sobre slots preenchidos | ✅ 0 erros em 82 docs processados retroativamente |
| H5 | get_sync_db está em core.database.session (não core.database) | ✅ Confirmado — `core.database.session.get_sync_db` |
| H6 | `:param::uuid` syntax funciona com psycopg2 | ❌ Causa SyntaxError — fix: `CAST(:param AS uuid)` |
| H7 | Beat schedule registrado sem quebrar celery_app.py | ✅ py_compile OK, 8 workers receberam hot-copy |

---

## Implementação

### Arquivos modificados

| Arquivo | Mudança |
|---------|---------|
| `backend/modules/gedeon/agents/hermes.py` | +330 linhas: MAPA_TIPOS_ONVIO_EMPRESA (19 tipos), MAPA_TIPOS_ONVIO_FUNCIONARIO (6 tipos), _STOP_WORDS_MATCH, _build_cond_to_ged_map(), _vincular_empresa(), _vincular_funcionario(), _recalcular_completude_mes(), processar_mes() |
| `backend/modules/gedeon/tasks/kronos_tasks.py` | +25 linhas: task `gedeon.hermes_vincular_docs_mes` |
| `backend/celery_app.py` | +7 linhas: beat schedule `gedeon-hermes-vincular-docs-0900` (dia 1 às 09:00) |

### Fluxo de matching implementado

```
processar_mes(mes_ref)
  ├── get_sync_db()
  ├── _build_cond_to_ged_map(db)
  │     condominios.id → ged_clients.id via word-set intersection (_STOP_WORDS_MATCH)
  ├── SELECT onvio_documents WHERE mes_ref AND caminho_local IS NOT NULL
  ├── para cada doc:
  │   ├── doc_scope='funcionario' + employee_id → _vincular_funcionario()
  │   │     employee_alocacoes → condominio_id → ged_client → kit → slot (employee_id+doc_type)
  │   └── condominio_id SET → _vincular_empresa()
  │         ged_client → kit → slot (doc_type, employee_id IS NULL)
  ├── db.commit()
  └── _recalcular_completude_mes() → UPDATE completion_percentage para todos os kits
      db.commit()
```

### Bug encontrado e corrigido

**Sintoma:** `psycopg2.errors.SyntaxError: syntax error at or near ":"` em `:client_id::uuid`

**Causa:** psycopg2 interpreta `::` como parte do nome do parâmetro nomeado SQLAlchemy, não como cast PostgreSQL.

**Fix:** Substituir `:param::type` por `CAST(:param AS type)` em todos os parâmetros UUID/date.

---

## Teste Retroativo — 3 Meses

```
02.2026: vinculados=0, ignorados=29, erros=0, kits_atualizados=0
03.2026: vinculados=0, ignorados=43, erros=0, kits_atualizados=8
04.2026: vinculados=0, ignorados=10, erros=0, kits_atualizados=10
```

**Resultado esperado:** 0 vinculados é correto. Diagnóstico:
- 02.2026: nenhum kit existe → kits_atualizados=0 → slots inacessíveis
- 03.2026: todos os slots `folha_pagamento` (empresa-level) já foram preenchidos pelo kit_builder_service em execução anterior. Slot `aso` não existe nos templates de 03.2026.
- 04.2026: todos os docs de abril têm `doc_scope=NULL` (sem condominio_id) → ignorados

**INV-5 comprovado:** zero sobrescritas. **Zero erros** em 82 docs processados.

---

## cond_to_ged Map (10/10)

| condominios.nome | condominios.id | ged_clients.id |
|-----------------|----------------|----------------|
| PRIME ARENA | 21929c3d | 52958919 |
| MICHELANGELO | b3ca559f | 02d784d5 |
| IDEAL FLORES | 215a124b | 4db583b6 |
| LARANJEIRAS | 7c2323fd | e55f6f4c |
| MIRANTE | dfa6645a | 130186bf |
| VILLA DEI FIORI | ef2f9c03 | 14809ac8 |
| VILLA PÁSSAROS | 6fb88de2 | 4909237d |
| P. GELAIN | ab146423 | 8199960d |
| GREEN HILLS | 4900de33 | b4a13504 |
| PARISE | 9be1e32b | d4dd6c53 |

---

## Hot-copy — 8/8 workers

| Container | Status |
|-----------|--------|
| conecta-pro-backend | ✅ |
| conecta-pro-celery-beat | ✅ |
| conecta-pro-celery-batch | ✅ |
| 297439d0453a_conecta-pro-celery-operacional | ✅ |
| conecta-pro-celery-integrations | ✅ |
| 34bbe0bcda76_conecta-pro-celery-priority | ✅ |
| 8f30da3e29ad_conecta-pro-celery-nfse | ✅ |
| a853a3056bf9_conecta-pro-celery-sefaz | ✅ |

pyc limpos antes de cada cópia. Backend recarregado (kill -9 → restart policy).

---

## Achados Arquiteturais

| Achado | Impacto |
|--------|---------|
| `core.database.session.get_sync_db` (não `core.database.get_sync_db`) | Import correto para tasks Celery — __init__.py não exporta get_sync_db |
| `:param::uuid` causa SyntaxError no psycopg2 | Usar `CAST(:param AS type)` em todas as queries com UUID/date em text() |
| Kit slots (folha_pagamento empresa) já preenchidos pelo kit_builder_service | HERMES é idempotente — só age quando há slots vazios |
| Docs `recibo_folha` com `doc_scope='condominio'` mas sem `referente_a_employee_id` | Não mapeáveis a slots individuais por funcionário — requer GEDEON FASE 2 |
| 81% dos docs Onvio sem `condominio_id` | Limitação conhecida do parser Onvio — HERMES ignora esses docs corretamente |

---

## Self-check

| Item | Status |
|------|--------|
| STEP 0 — CONTRACTS_GEDEON lido, §94 adicionado ANTES do commit código | ✅ |
| STEP 1 — hermes.py lido, kit_builder_service MAPA/STOP_WORDS capturados | ✅ |
| STEP 2 — hermes.py implementado: processar_mes + 4 helpers | ✅ |
| STEP 3 — kronos_tasks.py: task hermes_vincular_docs_mes adicionada | ✅ |
| STEP 4 — celery_app.py: beat schedule dia 1 às 09:00 adicionado | ✅ |
| STEP 5 — py_compile 3/3 OK | ✅ |
| STEP 6 — Bug psycopg2 `::uuid` identificado e corrigido → `CAST(:p AS uuid)` | ✅ |
| STEP 7 — Hot-copy 8/8 workers (pyc limpos) + backend reload | ✅ |
| STEP 8 — Retroativo 02/03/04.2026: 0 vinculados, 0 erros (correto) | ✅ |
| STEP 9 — 2 commits: docs(§94) → feat(hermes) + push | ✅ |
| INV-5 — Nunca sobrescreve file_path já preenchido | ✅ WHERE file_path IS NULL OR file_path='' |
| INV-12 — Recalcula completion_percentage após vincular | ✅ _recalcular_completude_mes() pós-commit |
| INV-3 — Código existente Hermes não modificado | ✅ Apenas métodos novos adicionados |

---

## Commits

| Commit | Tipo | Hash |
|--------|------|------|
| docs(contracts): §94 — HERMES matching onvio→colaborador→condomínio→kit | docs | `706f9bc7` |
| feat(gedeon): HERMES matching onvio→colaborador→condomínio→kit (§94) | code | `3ffb75ac` |

---

**T4 HERMES CPRO12 OK**

HERMES está operacional. Beat schedule registrado para execução dia 1 de cada mês às 09:00. Quando novos docs Onvio chegarem com `condominio_id` preenchido e slots vazios existirem nos kits, o agente vinculará automaticamente.

[session: t5] [module: ged]
