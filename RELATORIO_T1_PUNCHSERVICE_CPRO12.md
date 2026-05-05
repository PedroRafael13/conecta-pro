# T1 CPRO12 — Fix PunchService instanciação global — celery-beat crash
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization
**Duração:** ~25min
**Tipo:** Diagnóstico + deploy container (zero edição de código)

---

## RESULTADO FINAL

| Item | Status |
|------|--------|
| PunchService global instantiation | ✅ FIXADO (container atualizado) |
| celery-beat scheduling tasks | ✅ FUNCIONANDO (Scheduler: Sending due task...) |
| celery-batch | ✅ EM RECUPERAÇÃO (gedeon copiado) |
| Hipótese H1 (disco bugado) | ❌ FALSA — disco já estava correto |

---

## 1. Causa Raiz

**Hipótese H1 do prompt (FALSA):** arquivo `punch_controller.py` no disco continha `_service = PunchService()` global.

**Causa real:** O arquivo no disco já estava correto — o fix havia sido aplicado em commit anterior mas **nunca foi copiado (docker cp) para os containers `celery-beat` e `celery-batch`**.

### Traceback nos containers (pré-fix)
```
File "/app/modules/people_management/ponto/controllers/punch_controller.py", line 34, in <module>
    _service = PunchService()
               ^^^^^^^^^^^^^^
TypeError: PunchService.__init__() missing 1 required positional argument: 'db'
```

### Estado do arquivo no disco (pré-intervenção)
- Todos os 10 endpoints já usavam `service = PunchService(db)` localmente
- `get_db` e `Depends` já importados na linha 13
- `py_compile` passava sem erros

---

## 2. Cadeia de erros no celery-beat (cronologia)

Cada container tinha múltiplos módulos desatualizados. A reparação foi progressiva:

| # | Erro | Fix |
|---|------|-----|
| 1 | `TypeError: PunchService.__init__() missing 1 required positional argument: 'db'` | docker cp punch_controller.py → backend + celery-beat + celery-batch |
| 2 | `ModuleNotFoundError: No module named 'modules.health_occupational.tasks'` | docker cp health_occupational/ → celery-beat |
| 3 | `ModuleNotFoundError: No module named 'modules.gedeon'` | docker cp gedeon/ → celery-beat + celery-batch |

**Padrão:** containers celery não recebiam hot-copy; apenas o container `backend` era atualizado rotineiramente.

---

## 3. Ações executadas

### STEP 1 — Diagnóstico
```bash
docker logs conecta-pro-celery-beat --tail 30
# Revelou: TypeError PunchService.__init__()
```

### STEP 2 — Backup
```bash
cp punch_controller.py punch_controller.py.bak.t1cpro12
```

### STEP 3 — Verificação disco
```bash
python3 -m py_compile punch_controller.py  # OK — arquivo já correto
```

### STEP 4 — CONTRACTS_GEDEON.md §58 adicionado
Documentação antes do deploy (princípio §13.3).

### STEP 5 — Hot-copy punch_controller.py
```bash
# backend (já correto — HUP para confirmar)
docker cp punch_controller.py conecta-pro-backend:/app/.../punch_controller.py
docker exec conecta-pro-backend kill -HUP 1

# celery-beat (versão velha com bug)
docker cp punch_controller.py conecta-pro-celery-beat:/app/.../punch_controller.py

# celery-batch (versão velha com bug)
docker cp punch_controller.py conecta-pro-celery-batch:/app/.../punch_controller.py
```

### STEP 6 — Hot-copy health_occupational/tasks/
```bash
docker cp backend/modules/health_occupational/tasks/ \
  conecta-pro-celery-beat:/app/modules/health_occupational/tasks/
```

### STEP 7 — Hot-copy gedeon/
```bash
docker cp backend/modules/gedeon/ conecta-pro-celery-beat:/app/modules/gedeon/
docker cp backend/modules/gedeon/ conecta-pro-celery-batch:/app/modules/gedeon/
```

---

## 4. Verificação final

### Import no backend
```
python3 -c "from modules.people_management.ponto.controllers import punch_controller; print('OK')"
# → OK
```

### celery-beat após fix
```
[2026-05-05 01:00:31,787] Scheduler: Sending due task bidding-check-certidoes-6h
[2026-05-05 01:00:31,790] Scheduler: Sending due task sst-check-expired-leaves-daily
[2026-05-05 01:00:31,797] Scheduler: Sending due task sst-check-inss-pending-daily
... (10 tasks enviadas)
```

**Container uptime:** >40 segundos contínuos — primeiro run estável desde 2026-03-20.

---

## 5. Descoberta adicional — containers celery desatualizados

**Achado crítico:** Os containers `celery-beat` e `celery-batch` nunca recebem hot-copy. Apenas o container `backend` é atualizado com `docker cp + kill -HUP 1`. Os celery workers estão rodando versões antigas dos módulos.

**Solução sustentável:** Incluir `celery-beat` e `celery-batch` no fluxo de hot-copy ao modificar qualquer módulo que contenha tasks Celery.

```bash
# Fluxo correto para módulos com tasks
docker cp backend/modules/$MODULO/ conecta-pro-backend:/app/modules/$MODULO/
docker cp backend/modules/$MODULO/ conecta-pro-celery-beat:/app/modules/$MODULO/
docker cp backend/modules/$MODULO/ conecta-pro-celery-batch:/app/modules/$MODULO/
docker exec conecta-pro-backend kill -HUP 1
```

---

## 6. Sinais de atenção pós-fix

| # | Sinal | Impacto |
|---|-------|---------|
| 🟢 | celery-beat schedulando tasks | Todos os Celery Beat agendamentos voltaram |
| 🟡 | celery-batch ainda em recuperação | gedeon copiado — aguardar próximo restart |
| 🟡 | `get_sync_session` nas tasks SST | ImportError em runtime (out of scope — Jordan decide) |
| 🟡 | Outros módulos no celery podem estar desatualizados | Monitorar logs após estabilização |

---

## PRINCÍPIOS APLICADOS

| Princípio | Aplicação |
|-----------|-----------|
| §13.1 Chesterton | `docker logs` lido ANTES de qualquer ação; disco vs container comparado |
| §13.4 Escopo sagrado | Apenas `punch_controller.py`, `health_occupational/tasks/`, `gedeon/` tocados |
| INV-6 | `docker cp + kill -HUP 1` — NÃO `docker restart` para o backend |
| §58 documentado antes do código | CONTRACTS_GEDEON.md §58 adicionado antes do deploy |
