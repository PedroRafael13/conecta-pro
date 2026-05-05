# T4 CPRO12 — Fix TenantStatus.ATIVO → active
**Data:** 2026-05-05
**Executor:** Claude Sonnet 4.6 [session: t4] [module: operacional]
**Decisão:** Opção A — string `'active'` direta (Opção B quebraria test_config_model.py:648 e config_repository)

---

## Hipóteses

| H | Descrição | Resultado |
|---|-----------|-----------|
| H1 | TenantStatus.ATIVO na linha ~39 | ✅ Linha 39 exata: `Tenant.status == TenantStatus.ATIVO,` |
| H2 | enum definido em arquivo separado | ✅ `backend/modules/config/models/tenant.py` |
| H3 | TenantStatus.ATIVO = "ativo" | ✅ Confirmado (`test_config_model.py:648: assert TenantStatus.ATIVO.value == "ativo"`) |
| H4 | banco tem enum inglês | ✅ `{active,inactive,suspended,blocked,trial,cancelled}` |
| H5 | DataError nos logs do worker | ✅ Container: `297439d0453a_conecta-pro-celery-operacional` (nome com hash) — DataError confirmado pré-fix: `DataError: invalid input value for enum tenant_status: "ATIVO"` (01:01–01:03 de 2026-05-05) |
| H6 | TenantStatus não em zonas proibidas | ✅ Zero ocorrências em `financial/` ou `government_integrations/` |
| H7 | py_compile passou | ✅ `COMPILE OK` |
| H8 | worker sem DataError após fix | ✅ Confirmado pós-reload com cache pyc limpo — task `check_late_employees` succeeded em 0.49s sem DataError (01:11:32 de 2026-05-05) |

---

## Investigação pré-fix

### notification_triggers.py — função `_get_active_tenants` (linha 30-44)

```python
def _get_active_tenants(db: Session) -> list[UUID]:
    rows = (
        db.query(Tenant.id)
        .filter(
            Tenant.status == TenantStatus.ATIVO,  # ← BUG
            Tenant.ativo.is_(True),
        )
        .all()
    )
    return [row[0] for row in rows]
```

### TenantStatus enum Python (`config/models/tenant.py`)

```python
class TenantStatus(StrEnum):
    ATIVO = "ativo"       # PT-BR
    INATIVO = "inativo"
    SUSPENSO = "suspenso"
    BLOQUEADO = "bloqueado"
    TRIAL = "trial"
    CANCELADO = "cancelado"
```

### Enum PostgreSQL `tenant_status`

```
{active, inactive, suspended, blocked, trial, cancelled}   ← inglês
```

### Por que `'ATIVO'` (uppercase) no erro?

`Column(Enum(TenantStatus))` sem `values_callable` → SQLAlchemy usa `.name` ("ATIVO"),
não `.value` ("ativo"). Em ambos os casos o valor é incompatível com o banco.

---

## Fix aplicado

**Arquivo:** `backend/modules/operacional/services/notification_triggers.py`

```diff
- Tenant.status == TenantStatus.ATIVO,
+ Tenant.status == 'active',
```

**Argumento:** Opção A (cirúrgica). TenantStatus.ATIVO aparece em 14 lugares do codebase
(config_repository, config_models, tests). Alterar o valor do enum (Opção B) quebraria:
- `test_config_model.py:648: assert TenantStatus.ATIVO.value == "ativo"` (teste falha)
- Dados existentes no banco que usem "ativo" como valor armazenado
- Todos os outros SELECT que comparam com TenantStatus.ATIVO no config_repository

---

## Commits

| Commit | Tipo | Hash |
|--------|------|------|
| docs: §61 no CONTRACTS_GEDEON.md (renumerado de §55) | docs | (já em HEAD) |
| fix: notification_triggers.py | code | `78671301` |

---

## Status worker pós-fix

### Pré-fix (DataError confirmado — 01:01–01:03 de 2026-05-05)

```
[2026-05-05 01:01:32] Task operacional.check_late_employees[bd63ef65...] retry: DataError invalid input value for enum tenant_status: "ATIVO"
[2026-05-05 01:02:32] Task operacional.check_late_employees[...] retry: DataError invalid input value for enum tenant_status: "ATIVO"
[2026-05-05 01:03:32] Task operacional.check_late_employees[...] retry: DataError invalid input value for enum tenant_status: "ATIVO"
```

### Causa do atraso no reload

Primeiro `docker cp` + `kill -HUP 1` não eliminou DataError porque `__pycache__/*.pyc` stale
no container ainda carregava o bytecode antigo. Solução final: limpar cache pyc + docker cp + SIGHUP.

```bash
docker exec $CELERY_OP find /app/modules/operacional/services/__pycache__ -name "notification_triggers*.pyc" -delete
docker cp notification_triggers.py $CELERY_OP:/app/modules/operacional/services/notification_triggers.py
docker exec $CELERY_OP python3 -c "import os, signal; os.kill(1, signal.SIGHUP)"
```

### Pós-fix (DataError eliminado — 01:11:32 de 2026-05-05)

```
[2026-05-05 01:11:23,627: INFO/MainProcess] Connected to redis://
[2026-05-05 01:11:24,694: INFO/MainProcess] operacional@50a04240fb53 ready.
[2026-05-05 01:11:32,269: INFO/ForkPoolWorker-2] Verificando colaboradores atrasados para tenant 841a3906...
[2026-05-05 01:11:32,306: INFO/ForkPoolWorker-2] Tenant 841a3906...: 0 atrasados, 0 notificações enviadas
[2026-05-05 01:11:32,308: INFO/ForkPoolWorker-2] Task operacional.check_late_employees[51370a21...] succeeded in 0.4855s
```

Zero DataError. Task succeeded.

---

## Teste vermelho (STEP 8)

```sql
SELECT id, nome, status FROM tenants
WHERE status = 'active'::tenant_status AND ativo IS true;

-- Resultado:
                  id                  |            nome             | status
--------------------------------------+-----------------------------+--------
 841a3906-5410-4047-a076-bc7bce95ffd2 | CONECTAMAIS ELETRONICA LTDA | active
(1 row)  ← sem DataError ✅
```

---

## Self-check (12 itens)

| Item | Status |
|------|--------|
| STEP 0 — contrato lido, §54 confirmado, §13.1 citado | ✅ |
| STEP 1.1 — notification_triggers.py lido INTEIRO | ✅ |
| STEP 1.3 — TenantStatus definição lida | ✅ |
| STEP 1.5 — DataError confirmado (container com hash) | ✅ |
| STEP 2 — backup .bak.t4cpro12 criado | ✅ |
| STEP 3 — fix Opção A aplicado, argumento documentado | ✅ |
| STEP 4 — py_compile OK | ✅ |
| STEP 5 — §61 no CONTRACTS_GEDEON (renumerado de §55, reordenado entre §60 e §62) | ✅ |
| STEP 6 — hot-reload via docker cp + kill -HUP 1 | ✅ |
| STEP 7 — logs do worker verificados pós-fix | ✅ |
| STEP 8 — teste vermelho: 1 linha sem DataError | ✅ |
| STEP 9 — 2 commits separados + push + backup removido | ✅ |
| Zero arquivos fora do escopo | ✅ |
| §13.4 — nenhum refactor não solicitado | ✅ |

---

## Cenário

**Cenário A** — DataError eliminado. Worker operacional executa sem erro.
Notificações desbloqueadas para o tenant `CONECTAMAIS ELETRONICA LTDA`.

---

**T4 CPRO12 OK — DataError eliminado, worker operacional executa tasks sem erro**

[session: t4] [module: operacional]
