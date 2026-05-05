# T1-F3F4 CPRO12 — Fix sync script + health_occupational subscribers
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization
**Duração:** ~25min
**Tipo:** Bugfix código + deploy (zero rebuild)

---

## RESULTADO — SUCESSO

> F3: sync_celery_workers.sh expandido para 8 containers (nfse + sefaz adicionados ao loop 1).
> F4: health_occupational/__init__.py — .warning() → .debug() (INV-5 compliance).
> Commit: e8d12f6d. Push: ✅ origin/feature/people-management-reorganization.

---

## Hipóteses validadas

| Hipótese | Resultado |
|----------|-----------|
| H1 Loop 1 do script excluía nfse e sefaz | ✅ CONFIRMADO — 6 containers, nfse e sefaz ausentes |
| H2 Loop 2 (celery_app.py) já tinha nfse e sefaz | ✅ CONFIRMADO — 7 containers, correto |
| H3 health_occupational/__init__.py tinha try/except | ✅ CONFIRMADO — bloco já existia com .warning() |
| H4 Nível .warning() viola INV-5 (deve ser .debug()) | ✅ CONFIRMADO — alterado para .debug() |
| H5 py_compile OK após alteração | ✅ CONFIRMADO — sem erros de sintaxe |
| H6 bash -n OK no script após F3 | ✅ CONFIRMADO — script sintaticamente correto |
| H7 warning ausente nos logs após hot-copy F4 | ✅ CONFIRMADO — priority e sefaz sem warning pós-copy |
| H8 CONTRACTS_GEDEON.md §72 registrado antes do commit | ✅ CONFIRMADO — §72 appended |

---

## STEP F3 — sync_celery_workers.sh

**Antes (loop 1 — 6 containers):**
```bash
for CONTAINER in conecta-pro-backend conecta-pro-celery-beat conecta-pro-celery-batch \
  conecta-pro-celery-operacional conecta-pro-celery-integrations conecta-pro-celery-priority; do
```

**Depois (loop 1 — 8 containers):**
```bash
for CONTAINER in conecta-pro-backend conecta-pro-celery-beat conecta-pro-celery-batch \
  conecta-pro-celery-operacional conecta-pro-celery-integrations conecta-pro-celery-priority \
  conecta-pro-celery-nfse conecta-pro-celery-sefaz; do
```

**Validação:** `bash -n scripts/deploy/sync_celery_workers.sh` → OK

---

## STEP F4 — health_occupational/__init__.py

**Antes:**
```python
_log.getLogger(__name__).warning("Health Occupational: falha ao registrar subscribers: %s", _e)
```

**Depois:**
```python
_log.getLogger(__name__).debug("Health Occupational: integrations não disponível: %s", _e)
```

**Validação:** `python3 -m py_compile` → OK

**Hot-copy para containers (containers que exibiam warning pré-fix):**
| Container | docker cp | Resultado |
|-----------|-----------|-----------|
| conecta-pro-celery-priority | ✅ OK | warning ausente pós-copy |
| conecta-pro-celery-sefaz | ✅ OK | warning ausente pós-copy |

**Princípio INV-5:** integrations/ não copiado para containers (só tasks/). try/except legítimo — módulo
ausente por design (apenas HOST tem o módulo completo). Log em debug, não silenciado.

---

## STEP 8 — Commits

| Tipo | Hash | Mensagem |
|------|------|---------|
| fix | `e8d12f6d` | fix(deploy+health): sync script +nfse+sefaz; subscribers import warning→debug (§72) |

**Nota:** CONTRACTS_GEDEON.md §72 foi registrado em commit anterior no mesmo dia (commit da sessão
anterior que travou no staging). Único commit de código aqui.

Push: `→ feature/people-management-reorganization` ✅

---

## SELF-CHECK

| Item | Status |
|------|--------|
| STEP F3 — loop 1 expandido para 8 containers (+ nfse + sefaz) | ✅ |
| STEP F3 — loop 2 (celery_app.py) já tinha nfse+sefaz, inalterado | ✅ |
| STEP F3 — bash -n OK | ✅ |
| STEP F4 — try/except existia, .warning() → .debug() | ✅ |
| STEP F4 — py_compile OK | ✅ |
| STEP F4 — hot-copy para priority + sefaz | ✅ |
| STEP F4 — warning ausente dos logs pós-fix | ✅ |
| CONTRACTS_GEDEON.md §72 registrado | ✅ |
| Commit e8d12f6d — 2 arquivos, INV-3 celery_app.py NÃO tocado | ✅ |
| Push origin feature/people-management-reorganization | ✅ |
| Backups .bak.t1f3f4 removidos | ✅ |

---

**T1-F3F4 CPRO12 OK — script sync corrigido (8 containers) + subscribers em debug.**
