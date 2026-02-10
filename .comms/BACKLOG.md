# BACKLOG — Tarefas Pendentes (v3)

**Atualizado:** 2026-02-10 02:20 UTC por Claude Opus 4.6

---

## Estado Atual: ~84.7% (5315 passed, 718 failed, 218 errors)

## META: 100% pass rate (0 failures, 0 errors)

## REVERTIDOS: commits 394e051d e 7aab7abb (causaram regressão de -365 testes)

---

## ⚠️ REGRA ABSOLUTA: NUNCA usar --fix em scripts de automação sem testar ANTES

O commit 394e051d usou `validate-enums.py --fix` cegamente em 104 arquivos (4235 mudanças).
Resultado: **regressão de 84.7% → 78.8%** porque enums com mesmo nome existem em módulos diferentes.

**PROIBIDO:**
- `validate-enums.py --fix` (troca enums corretos por errados)
- `auto-fix-fields.py --fix` em massa (sem verificar cada mudança)
- Qualquer script que modifique mais de 5 arquivos sem verificação intermediária

**OBRIGATÓRIO:**
- Corrigir 1 arquivo de teste por vez
- Rodar pytest nesse arquivo após correção
- Só ir para o próximo arquivo se o anterior passou

---

## ✅ CONCLUÍDAS

### ~~Tarefa 1: PushNotification Mapper Collision~~ ✅
### ~~Tarefa 2: Table push_notifications Metadata Duplicate~~ ✅
### ~~Tarefa 3: Enums EN vs PT (parcial)~~ ✅
### ~~Tarefa 6: ESLint 29 Errors~~ ✅
### ~~Tarefa 4: Fixture async_client~~ ✅ (Claude corrigiu com lazy-load)

---

## PENDENTES — ARQUIVO POR ARQUIVO

### Tarefa 7: Corrigir Top 15 Arquivos de Teste [MANUAL — OBRIGATÓRIO]

**Impacto:** ~560 failures (~78% do total)

**Método OBRIGATÓRIO para CADA arquivo:**

```bash
cd /opt/conecta-pro/backend && source venv/bin/activate

# PASSO 1: Rodar o teste e ver EXATAMENTE quais erros tem
python -m pytest tests/test_client_model.py --tb=short -q 2>&1 | head -60

# PASSO 2: Para cada erro de enum — verificar valor REAL no módulo:
grep -r "class AccountType" modules/ --include="*.py" -A 15

# PASSO 3: Para cada erro de campo — ver campos reais:
python /opt/conecta-pro/scripts/required-fields.py modules/clients/models/client.py Client

# PASSO 4: Corrigir no teste (NÃO no código de produção)

# PASSO 5: Rodar o teste novamente para confirmar
python -m pytest tests/test_client_model.py --tb=short -q

# PASSO 6: Se passou, commitar e ir para o próximo
# PASSO 7: Se falhou, investigar mais antes de seguir
```

**Ordem dos arquivos (por impacto):**

| # | Arquivo | Failures | Tipo Principal |
|---|---|---:|---|
| 1 | test_client_model.py | 55 | Campos inválidos (name→legal_name) |
| 2 | test_accounting_model.py | 45 | Enums (AccountType.CHECKING) |
| 3 | test_reports_model.py | 45 | Enums (ReportType, KPICategory) |
| 4 | test_client_service.py | 41 | Campos + mocks |
| 5 | test_config_model.py | 39 | Enums + campos |
| 6 | test_bi_dashboard_models.py | 34 | Campos inválidos |
| 7 | test_inventory_model.py | 34 | Enums (ProductType) |
| 8 | test_config_service.py | 31 | ERRORs (import/mock) |
| 9 | test_config_api.py | 29 | Fixture + campos |
| 10 | test_sync_system.py | 28 | Enums (SyncStatus) |
| 11 | test_diarist_api.py | 27 | ERRORs |
| 12 | test_purchase_models.py | 26 | Enums + campos |
| 13 | test_time_tracking_model.py | 26 | Enums (ShiftType) |
| 14 | test_recruitment_models.py | 25 | Enums + campos |
| 15 | test_cashflow_api.py | 24 | ERRORs |

---

### Tarefa 8: Collection Errors [218 errors]

**Depois de corrigir a Tarefa 7**, investigar os 218 errors:
```bash
python -m pytest --collect-only -q 2>&1 | grep "ERROR"
```

---

### Tarefa 5: Pydantic ValidationError [~40 failures]

Usar `schema-validator.py --scan` para identificar.

---

## Ferramentas Disponíveis em /opt/conecta-pro/scripts/

| Script | Uso | MODO |
|---|---|---|
| `verify-instant.sh` | Ruff + collection + alembic | RODAR |
| `required-fields.py <arquivo> <Model>` | Ver campos corretos | CONSULTA |
| `validate-enums.py` | Ver enums errados (SEM --fix) | CONSULTA |
| `pre-flight.sh <arquivo>` | Impacto antes de editar | CONSULTA |
| `schema-validator.py --model X` | Validar schemas | CONSULTA |
| `diagnose-failures.py` | Categorizar failures | CONSULTA |
| ~~validate-enums.py --fix~~ | **PROIBIDO** | NUNCA |
| ~~auto-fix-fields.py --fix~~ | **PROIBIDO em massa** | NUNCA |

**REGRA: Scripts de --fix são PROIBIDOS. Usar apenas como CONSULTA.**
