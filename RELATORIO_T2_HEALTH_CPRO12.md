# T2 CPRO12 — Fix health_occupational ModuleNotFoundError
**Data:** 2026-05-05
**Sessão:** tmux-t2 | **Módulo:** health_occupational (deploy sync)
**Branch:** feature/people-management-reorganization

---

## Decisão: Opção A variante — sync deployment (não stub)

O módulo `health_occupational/tasks/` já existia no HOST com 3 tasks reais.
O container `conecta-pro-celery-batch` não tinha recebido o sync deste diretório.
Fix = `docker cp tasks/ → container` (não criação de stub).

**Argumento:** `git log` mostrou 10 commits no módulo desde fevereiro/2026 — módulo ativo e implementado. INV-5 (stub) não se aplica pois implementação real existe e é correta a nível de módulo.

---

## Hipóteses Validadas

| Hipótese | Resultado |
|----------|-----------|
| H1: celery_app referencia `health_occupational.tasks` | ✅ SIM — linha 28 do include |
| H2: diretório não existe no container | ✅ SIM — existia no HOST, ausente no container |
| H3: nunca existiu no git | ❌ NÃO — 10 commits desde fev/2026 |
| H4: batch em loop antes do fix | ✅ SIM — `health: starting` em loop |
| H5: outras referências no projeto | ✅ `main_production.py:658` + `tests/test_health_status.py` |
| H6: import OK após fix (host) | ✅ `OK celery_app carregou` |
| H7: batch subiu após fix | ⚠️ CENÁRIO B — novo erro (ver abaixo) |
| H8: outros workers OK | ✅ integrations, priority, sefaz, nfse, operacional — todos healthy |

---

## STEP 1 — Investigação

### 1.1 celery_app.py (§13.1 Chesterton — lido inteiro)
Linha 28 do `include`:
```python
"modules.health_occupational.tasks",
```
Confirmado que o módulo é importado pelo Celery ao iniciar o worker.

### 1.2 Filesystem HOST
`backend/modules/health_occupational/tasks/` existe com:
- `__init__.py` (importa 3 tasks de `sst_alerts_tasks.py`)
- `sst_alerts_tasks.py` (3 tasks reais: ASO, EPI, exames periódicos)

### 1.3 Histórico git
```
a983d63b feat: hookar controllers Saúde, DP e Operacional no ConectaEventBus
3190d7c2 feat(gedeon): GEDEON Core implementado
cb2d18a3 fix(orm): remover 4 modelos SQLAlchemy duplicados em health_occupational/core/
4b0faee5 fix(api/skill03): POST → 201 + aliases REST sem verbos nos paths
... 6 commits anteriores
```
Módulo tem histórico rico — nunca foi abandonado. → **Opção A variante** (não B).

### 1.4 Outras referências
- `main_production.py:658` — router importado
- `tests/test_health_status.py` — testes existem
- `celery_app.py:28` — include list

### 1.5 Status antes do fix
```
conecta-pro-celery-batch   Up 5 seconds (health: starting)  ← loop de crash
```

---

## STEP 2 — Backup
```
backend/celery_app.py.bak.t2cpro12  ← criado
```

---

## STEP 3 — Fix Aplicado

Nenhuma alteração de código necessária. O `tasks/__init__.py` já estava correto:
```python
from .sst_alerts_tasks import (
    verificar_asos_vencendo,
    verificar_epis_vencendo,
    verificar_exames_pendentes,
)
```

`from core.database import get_sync_session` é **lazy** (dentro das funções), não afeta o import do módulo.

Fix real = deployment sync:
```bash
docker exec -u root conecta-pro-celery-batch rm -rf /app/modules/health_occupational/health_occupational
docker cp backend/modules/health_occupational/tasks conecta-pro-celery-batch:/app/modules/health_occupational/tasks
```

---

## STEP 4 — Validação Host
```
cd backend && python3 -c "import sys; sys.path.insert(0, '.'); import celery_app; print('OK')"
→ OK celery_app carregou
```

---

## STEP 7 — Teste Vermelho (container)
```
docker exec conecta-pro-celery-batch python3 -c "
  from modules.health_occupational import tasks
  print('Import health_occupational.tasks OK')
"
→ Import health_occupational.tasks OK  ✅
```

---

## CENÁRIO B — Novo erro após fix

Após resolver `health_occupational.tasks`, o batch revelou o próximo erro na cadeia:

```
ModuleNotFoundError: No module named 'modules.gedeon'
```

**Causa:** `celery_app.py` inclui `modules.gedeon.tasks.kronos_tasks` mas o container não tem o módulo `gedeon/` (mesma situação: container com imagem antiga, módulo adicionado após build).

**Ação:** NÃO corrigido — escopo §13.4 restrito a `health_occupational`. Jordan decide se autoriza sync de `gedeon/` para o container.

---

## Bugs Residuais Identificados

| Bug | Arquivo | Problema | Impacto |
|-----|---------|----------|---------|
| C4b | `celery_app.py include` | `modules.gedeon` ausente no container | batch ainda em loop |
| C4c | `sst_alerts_tasks.py:34,164,246` | `from core.database import get_sync_session` — função não existe (use `get_sync_db`) | tasks SST falham em runtime |

---

## Commits

| Tipo | Hash | Mensagem |
|------|------|----------|
| docs | `cc871a5b` | `docs(contracts): §59 — Fix Bug C4 health_occupational ModuleNotFoundError (CPRO12 T2)` |
| code | `1759cbaa` | `fix(celery): resolve ModuleNotFoundError health_occupational — destravar batch (§59)` |

---

## Status Final

```
conecta-pro-celery-integrations    Up 2 weeks  (healthy)   ✅
conecta-pro-celery-priority        Up 2 weeks  (healthy)   ✅
conecta-pro-celery-sefaz           Up 2 weeks  (healthy)   ✅
conecta-pro-celery-nfse            Up 2 weeks  (healthy)   ✅
conecta-pro-celery-operacional     Up 2 weeks  (healthy)   ✅
conecta-pro-celery-beat            Up 15s      (starting)  ⚠️ BUG-2 punch_controller (T1)
conecta-pro-celery-batch           Up 17s      (starting)  ⚠️ CENÁRIO B: modules.gedeon
```

**T2 CPRO12 — health_occupational RESOLVIDO. celery-batch ainda em loop por novo erro: `modules.gedeon` ausente no container. Aguarda autorização Jordan para sync gedeon.**
