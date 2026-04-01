# Instruções para Opus (Executor) — Lote B + Lote C

Leia `/opt/conecta-pro/.comms/HANDOFF.md` para contexto completo do projeto.

## Sua Tarefa: Corrigir 32 falhas em 12 arquivos (E2E + isolados)

Estes são mais complexos que model tests — exigem investigação.

---

### Lote B: E2E/Integration Tests (24 falhas)

| # | Arquivo | Falhas | Padrão provável |
|---|---------|--------|-----------------|
| 1 | tests/_integration/e2e/test_operations_flow.py | 8 | Routes não registradas no app de teste |
| 2 | tests/_integration/e2e/test_crm_flow.py | 7 | Routes não registradas no app de teste |
| 3 | tests/_integration/test_health_detailed.py | 4 | Mock de health check incorreto |
| 4 | tests/_integration/e2e/test_financial_flow.py | 2 | Routes não registradas |
| 5 | tests/_integration/e2e/test_auth_flow.py | 2 | Token validation mock |
| 6 | tests/_integration/e2e/test_health.py | 1 | Route de operations não registrada |

**Padrão comum nos E2E:** Muitos testam se endpoints existem (`test_XXX_endpoint_exists`), mas o `TestClient` não inclui todos os routers. Pode ser necessário:
- Verificar como o `app` é montado em `main.py` ou `app.py`
- Verificar quais routers estão registrados
- Ajustar o teste para usar o app correto ou registrar os routers faltantes na fixture

### Lote C: Falhas Isoladas (8 falhas)

| # | Arquivo | Falhas | Notas |
|---|---------|--------|-------|
| 7 | tests/test_config_service.py | 3 | Bug no serviço: `create_notification_template` passa `channel=` mas model espera `channel_id=`. Pode corrigir o serviço (1 linha) |
| 8 | tests/test_accounting_api.py | 1 | `test_create_chart` — 1 falha isolada |
| 9 | tests/monitoring/test_early_warning.py | 1 | `test_should_alert_in_cooldown` |
| 10 | tests/modules/notifications/anti_procrastination/test_checklist.py | 1 | `test_generate_daily_checklist` |
| 11 | tests/modules/lgpd/test_delete_me.py | 1 | `test_anonymize_email_format` |
| 12 | tests/_integration/e2e/test_ai_modules.py | 1 | `test_chatbot_endpoint_exists` |

---

## Método para E2E tests:

```bash
cd /opt/conecta-pro/backend && source venv/bin/activate

# 1. Ver o erro exato
python3 -m pytest tests/_integration/e2e/test_XXX.py -v --tb=long 2>&1 | tail -60

# 2. Investigar como o app é montado
python3 -c "
import sys; sys.path.insert(0, '.')
from main import app  # ou de onde o app é criado
for route in app.routes:
    if hasattr(route, 'path'):
        print(f'{route.methods} {route.path}')
" 2>&1 | head -50

# 3. Ver o que o teste espera vs o que existe
# 4. Corrigir o teste (ou em casos justificados, o código)
# 5. Rodar e confirmar 0 failures
# 6. Commitar
```

## Método para falhas isoladas:

```bash
# 1. Ver o erro exato
python3 -m pytest tests/test_XXX.py::TestClass::test_method -v --tb=long

# 2. Investigar a causa raiz
# 3. Corrigir
# 4. Confirmar
# 5. Commitar
```

---

## Regras:
- NÃO inventar enums/campos — SEMPRE verificar nos models reais
- NÃO usar scripts `--fix` em massa
- Pode corrigir código de produção APENAS para bugs óbvios de 1 linha (como o channel→channel_id)
- 1 arquivo por vez → testar → commitar → próximo
- Pre-commit hooks ativos: ruff, ruff-format, bandit, detect-secrets
- Se commit falhar por ruff-format: `git add -u && git commit -m "mesma msg"`

## Comunicação:
Após cada arquivo, reportar status em `/opt/conecta-pro/.comms/messages/opus-exec-out.jsonl`:
```json
{"ts":"2026-02-10T...","from":"opus-exec","type":"status","file":"test_XXX.py","before":N,"after":0,"result":"PASSED"}
```
