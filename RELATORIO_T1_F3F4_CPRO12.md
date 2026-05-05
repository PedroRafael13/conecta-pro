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

## Hipóteses validadas (H1-H8 conforme prompt)

| Hipótese | Resultado |
|----------|-----------|
| H1: script lista 6 containers, exclui nfse/sefaz | ✅ CONFIRMADO — grep retornou nfse/sefaz ausentes no loop 1 |
| H2: __init__.py importa integrations sem try/except | ⚠️ CENÁRIO C — try/except JÁ EXISTIA, mas com .warning() violando INV-5. Fix: .warning()→.debug() |
| H3: diretório integrations/ não existe no módulo | ❌ NÃO CONFIRMADO — integrations/ EXISTE no HOST. Ausente nos containers (apenas tasks/ copiado em T2-C). try/except é correto |
| H4: containers priority e sefaz mostram o warning nos logs | ✅ CONFIRMADO — warning visível antes do hot-copy F4 |
| H5: após fix, py_compile passa sem erro | ✅ CONFIRMADO — python3 -m py_compile: OK |
| H6: após hot-copy, warning some dos logs | ✅ CONFIRMADO — priority e sefaz: sem output grep pós-copy |
| H7: bash -n OK no script após adição nfse/sefaz | ✅ CONFIRMADO — bash -n: SCRIPT SYNTAX OK |
| H8: containers nfse e sefaz têm health_occupational/ presente | ✅ CONFIRMADO — ls /app/modules/: health_occupational em ambos |

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
| docs | `dce85399` | docs(relatorio): T1-F3F4 CPRO12 — sync script +nfse+sefaz + health_occupational warning→debug |

**INV-8 status:** O prompt exige 2 commits (docs §72 + code). O commit code foi feito (`e8d12f6d`).
O commit docs standalone para CONTRACTS_GEDEON.md §72 NÃO foi feito separadamente — §72 entrou
via commit `a52b84c4` (§74, sessão tmux-t2 paralela). Conteúdo correto e commitado; estrutura de 2
commits não respeitada. GAP documentado (não corrigível sem git reset — proibido).

Push: `→ feature/people-management-reorganization` ✅

---

## SELF-CHECK (14 itens conforme prompt)

| Item | Status |
|------|--------|
| STEP 0 — contrato lido, §N confirmado, §13.1 citado | ✅ |
| STEP 1.1 — sync_celery_workers.sh lido inteiro (Chesterton) | ✅ |
| STEP 1.2 — health_occupational/__init__.py lido inteiro (Chesterton) | ✅ |
| STEP 2 — backups criados (bak.t1f3f4) | ✅ |
| STEP 3 — nfse + sefaz adicionados ao loop 1; bash -n OK | ✅ |
| STEP 4 — try/except preservado; .warning() → .debug() (INV-4/INV-5) | ✅ |
| STEP 5 — py_compile OK | ✅ |
| STEP 6 — §72 em CONTRACTS_GEDEON.md antes do commit de código | ✅ (via cat >>) |
| STEP 7 — hot-copy __init__.py → priority + sefaz com pyc limpos; SIGHUP enviado | ✅ |
| STEP 7 — warning ausente nos logs de priority e sefaz pós-fix | ✅ |
| STEP 8 — 2 commits separados (docs + code) | ⚠️ GAP: docs §72 não commitado standalone (ver STEP 8 acima) |
| STEP 8 — push + backups removidos | ✅ |
| INV-3 — apenas 2 containers adicionados ao script | ✅ |
| INV-4 — try/except mantido, bloco NÃO removido | ✅ |
| INV-5 — log em .debug(), não silenciado | ✅ |

---

**T1-F3F4 CPRO12OK — script sync cobre 8 containers; warning subscribers eliminado.**
**GAP INV-8:** commit docs §72 não foi standalone (entrou via §74 de sessão paralela). Conteúdo correto.
