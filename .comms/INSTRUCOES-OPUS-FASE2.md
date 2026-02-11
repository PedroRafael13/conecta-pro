# Instruções para Opus (Executor) — Fase 2 do Plano Mestre

Leia `/opt/conecta-pro/.comms/tasks/PLANO-MESTRE-PRODUCAO.md` para contexto completo.

## Estado Atual
- Pytest: 6232 passed, 0 failed (100%)
- Alembic: 1 head (OK)
- ESLint: 0 errors, 510 warnings
- Bandit High: 1
- Ruff: 0 errors
- python-jose: 0 imports (OK)
- console.log: 6 restantes
- EmailTemplate: 1 ORM model (OK, fase5 usa Pydantic BaseModel)

## Sua Tarefa: Backend finishing + ESLint complexo

### Tarefa 1: Fix Bandit High (1 min)

Arquivo: `/opt/conecta-pro/backend/scripts/test_gov_connections.py:389`
O `verify=False` já tem `# noqa: S501` mas falta `# nosec B501` para Bandit.

```python
# ANTES:
async with httpx.AsyncClient(timeout=15.0, verify=False) as client:  # noqa: S501
# DEPOIS:
async with httpx.AsyncClient(timeout=15.0, verify=False) as client:  # noqa: S501  # nosec B501
```

Verificar:
```bash
cd /opt/conecta-pro/backend && source venv/bin/activate
bandit -r . -q --severity-level high -x ./venv,./tests,./.venv 2>&1 | grep "High"
# ESPERADO: High: 0
```

### Tarefa 2: Fix 2 bugs de produção (5 min cada)

**Bug A:** `modules/ai/unified_dashboard/services/unified_dashboard.py`
Método `_task_to_data()` passa `metadata=` mas `PendingTaskData` espera `task_metadata=`.
Fix: trocar `metadata=` por `task_metadata=` (1 linha).

**Bug B:** `modules/government_integrations/fiscal/services/efd_reinf_service.py`
`valor_base_retencao=None` causa `Decimal(str(None))` → ConversionSyntax.
Fix: adicionar guard `Decimal(str(valor_base_retencao or 0))` (1 linha).

Verificar após cada fix:
```bash
cd /opt/conecta-pro/backend && source venv/bin/activate
python3 -m pytest --tb=no -q 2>&1 | tail -3
# ESPERADO: 6232 passed, 0 failed
```

### Tarefa 3: ESLint warnings complexos (~86 warnings)

Após backend, focar nos warnings mais complexos do frontend:

```bash
cd /opt/conecta-pro/frontend
```

**Regra `react-hooks/set-state-in-effect` (41 warnings):**
- Problema: setState chamado dentro de useEffect sem deps corretas
- Fix: mover setState para callback ou adicionar deps

**Regra `react-hooks/exhaustive-deps` (30 warnings):**
- Fix: adicionar deps faltantes no array, ou extrair funções com useCallback

**Regra `import/no-anonymous-default-export` (15 warnings):**
- Fix: nomear o export antes de exportar

### Método
1. Corrigir 1 arquivo por vez
2. Verificar que não quebra nada:
```bash
cd /opt/conecta-pro/frontend && npx tsc --noEmit 2>&1 | tail -3
```
3. Commitar após cada grupo de fixes

### Status
Após cada tarefa, escreva em `/opt/conecta-pro/.comms/messages/opus-exec-out.jsonl`:
```json
{"ts":"2026-02-10T...","from":"opus-exec","type":"status","task":"tarefa_N","result":"descrição"}
```
