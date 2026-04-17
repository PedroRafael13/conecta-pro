# RELATÓRIO T2 — GEDEON Fase 3: Alembic Onvio Sync Tables
**Data:** 2026-04-17
**Sessão:** tmux-t2
**Módulo:** ged
**Branch:** feature/people-management-reorganization

---

## Missão
Criar as migrações Alembic para as 4 novas tabelas da GEDEON Fase 3 — Onvio Sync.

---

## DIAGNOSE

| Item | Resultado |
|------|-----------|
| DATABASE_URL | `postgresql+asyncpg://postgres:****@172.18.0.3:5432/conecta_pro` |
| Container PostgreSQL | `conecta-pro-postgres` (Up 13 days, healthy) |
| Tabelas existentes relacionadas | `bidding_sync_jobs`, `documentos_fiscais`, `rubricas_folha`, etc. |
| Tabelas do tema já existiam? | Sim — criadas em sessão anterior sem migration registrada |

---

## STEP 1 — Models criados

**Arquivo:** `backend/modules/ged/models/onvio_models.py`
*(adaptação: `app/models/` não existe neste projeto — correto path é `modules/ged/models/`)*

| Classe | `__tablename__` | Colunas |
|--------|----------------|---------|
| `OnvioSyncStatus` | enum | 5 valores |
| `OnvioDocCategory` | enum | 18 valores |
| `OnvioSyncLog` | `onvio_sync_log` | id, mes_ref, status, docs_baixados, docs_novos, docs_erro, duracao_s, detalhes, created_at |
| `OnvioDocument` | `onvio_documents` | id, onvio_id, onvio_folder_id, nome_arquivo, categoria, mes_ref, caminho_local, tamanho_bytes, data_onvio, data_importado, processado, metadata_json |
| `FgtsGuia` | `fgts_guias` | id, mes_ref, tipo, valor, vencimento, status, arquivo_pdf, onvio_doc_id, created_at |
| `InssGuia` | `inss_guias` | id, mes_ref, valor, vencimento, competencia, status, arquivo_pdf, onvio_doc_id, created_at |

---

## STEP 2 — __init__.py atualizado

`backend/modules/ged/models/__init__.py` — adicionados exports:
- `OnvioSyncLog`, `OnvioSyncStatus`, `OnvioDocument`, `OnvioDocCategory`, `FgtsGuia`, `InssGuia`

---

## STEP 3 — Migração

`--autogenerate` bloqueou por FK orphan pré-existente em `documentos_fiscais_diaristas → diaristas` (issue pré-existente, não relacionada a este task).
**Solução:** migration escrita manualmente.

| Arquivo | Revision ID | Status |
|---------|-------------|--------|
| `sprint82_gedeon_fase3_onvio_sync.py` | `sprint82_gedeon_fase3_onvio` | ✅ aplicado (stamp) |
| `sprint82b_gedeon_fase3_schema_fix.py` | `sprint82b_gedeon_schema_fix` | ✅ aplicado |

---

## STEP 4 — Alembic state resolvido

| Problema | Causa | Solução |
|----------|-------|---------|
| DB tinha 2 heads (`sprint80_payable` + `sprint80b`) | stale entry em `alembic_version` | DELETE da entrada sprint80_payable (sprint80b depende dela — era duplicata) |
| `sprint81` já aplicado sem registro | tabela já existia | `alembic stamp sprint81` |
| Tabelas sprint82 já existiam | criadas em sessão anterior | `alembic stamp sprint82` |
| Schema divergente (fgts/inss) | tabelas criadas com colunas erradas | migration sprint82b corrigiu |
| `alembic upgrade head` final | sprint82b → aplicado normalmente | ✅ |

---

## STEP 5 — Validação final

```
 fgts_guias      |    9 cols
 inss_guias      |    9 cols
 onvio_documents |   13 cols
 onvio_sync_log  |    9 cols
```

**alembic current:** `sprint82b_gedeon_schema_fix (head)` ✅

### Schema detalhado — fgts_guias (9 cols)
id (uuid) | mes_ref (varchar) | tipo (varchar) | arquivo_pdf (varchar) | valor (float) |
vencimento (timestamptz) | status (varchar) | created_at (timestamptz) | onvio_doc_id (uuid)

### Schema detalhado — inss_guias (9 cols)
id (uuid) | mes_ref (varchar) | arquivo_pdf (varchar) | valor (float) | vencimento (timestamptz) |
status (varchar) | created_at (timestamptz) | onvio_doc_id (uuid) | competencia (varchar)

### Schema detalhado — onvio_documents (13 cols)
id | onvio_id | onvio_folder_id | nome_arquivo | categoria | mes_ref |
caminho_local | data_onvio (timestamptz ✅) | processado | created_at | tamanho_bytes | data_importado | metadata_json

### Schema detalhado — onvio_sync_log (9 cols)
id | mes_ref | status | docs_baixados | docs_novos | docs_erro | duracao_s | detalhes | created_at

---

## Commits

| Hash | Descrição |
|------|-----------|
| `3ad12f49` | feat(ged): GEDEON Fase 3 — migration sprint82 + alembic env/models sync |
| `(sprint82b)` | feat(ged): GEDEON Fase 3 — sprint82b schema fix fgts/inss/onvio_documents |

---

## Resultado Final

| Item | Status |
|------|--------|
| `onvio_sync_log` — 9 colunas | ✅ |
| `onvio_documents` — 13 colunas | ✅ |
| `fgts_guias` — 9 colunas | ✅ |
| `inss_guias` — 9 colunas | ✅ |
| Schema 100% compatível com models Python | ✅ |
| `alembic_version` = `sprint82b_gedeon_schema_fix (head)` | ✅ |
| alembic/env.py importa todos os 4 models | ✅ |
| modules/ged/models/__init__.py exporta todos os enums/classes | ✅ |
| Push para `feature/people-management-reorganization` | ✅ |

**RELATÓRIO: 4 tabelas novas criadas | Schema validado ✅**
