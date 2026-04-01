# SESSÃO NOTURNA — Kimi K2.5 Autônomo

> **Criado por:** Claude Opus 4.6 (Auditor)
> **Data:** 2026-02-10 02:30 UTC
> **Executor:** Kimi K2.5
> **Duração:** A noite toda — Jordan vai conferir de manhã
> **Regra:** Claude auditará de manhã. TUDO será verificado.

---

## ⚠️ REGRAS DA SESSÃO NOTURNA (LER ANTES DE TUDO)

1. **1 ARQUIVO POR VEZ** — Corrigir, testar, commitar. Só depois ir pro próximo.
2. **NUNCA usar --fix em scripts de automação** (validate-enums.py, auto-fix-fields.py)
3. **SEMPRE rodar pytest no arquivo após corrigir:**
   ```bash
   python -m pytest tests/ARQUIVO.py --tb=short -q
   ```
4. **COMMITAR a cada arquivo que passar** (formato: `fix(tests): corrige test_X — N tests passando`)
5. **Se não souber corrigir um teste: `@pytest.mark.xfail(reason="motivo")`**
6. **NUNCA editar código de produção (modules/) — só testes (tests/)**
7. **NUNCA deletar testes — corrigir ou xfail**
8. **Reportar progresso a cada 5 arquivos** via kimi-out.jsonl

---

## BASELINE ATUAL (2026-02-10 02:30 UTC)

```
Pytest: 5315 passed, 718 failed, 218 errors (84.7%)
Collection: 6288 tests, 0 errors
Ruff F401/F841: 0 errors
ESLint: 0 errors, 510 warnings
TypeScript: 0 errors
Alembic: 1 head
```

---

## PLANO DE TRABALHO — ORDEM EXATA

### BLOCO 1: Corrigir Top 15 Arquivos de Teste (PRIORIDADE MÁXIMA)

Este é o trabalho principal. 718 failed + 218 errors concentrados em ~50 arquivos.

**Para CADA arquivo, seguir este workflow EXATO:**

```bash
cd /opt/conecta-pro/backend && source venv/bin/activate

# 1. Rodar o teste e ver os erros
python -m pytest tests/ARQUIVO.py --tb=short -q 2>&1

# 2. Para cada erro de enum (AttributeError: 'EnumName' has no attribute 'VALUE'):
#    Consultar o enum real:
grep -r "class NomeDoEnum" modules/ --include="*.py" -A 20

# 3. Para cada erro de campo (TypeError: 'X' is an invalid keyword argument):
#    Ver os campos corretos:
python /opt/conecta-pro/scripts/required-fields.py modules/CAMINHO/models/ARQUIVO.py NomeModel

# 4. Para cada AssertionError:
#    Ler o teste, entender o que testa, corrigir a assertion

# 5. Para cada ValidationError:
#    Ver campos obrigatórios e adicionar os que faltam

# 6. Rodar o teste novamente
python -m pytest tests/ARQUIVO.py --tb=short -q

# 7. Se passou: commitar
# 8. Se falhou: continuar corrigindo ou xfail os irrecuperáveis
```

**ORDEM DOS ARQUIVOS (por impacto):**

```
1.  tests/test_client_model.py          — 55 failures (Client usa legal_name, não name)
2.  tests/test_accounting_model.py      — 45 failures (AccountType.CHECKING não existe)
3.  tests/test_reports_model.py         — 45 failures (ReportType, KPICategory errados)
4.  tests/test_client_service.py        — 41 failures
5.  tests/test_config_model.py          — 39 failures
6.  tests/test_bi_dashboard_models.py   — 34 failures
7.  tests/test_inventory_model.py       — 34 failures
8.  tests/test_config_service.py        — 31 errors
9.  tests/test_config_api.py            — 29 failures
10. tests/test_sync_system.py           — 28 failures
11. tests/test_diarist_api.py           — 27 errors
12. tests/test_purchase_models.py       — 26 failures
13. tests/test_time_tracking_model.py   — 26 failures
14. tests/test_recruitment_models.py    — 25 failures
15. tests/test_cashflow_api.py          — 24 failures
```

**Dicas por arquivo:**

- **test_client_model.py**: Client tem campos: `code`, `legal_name`, `document_number` (NÃO `name`, `razao_social`). Use `required-fields.py modules/clients/models/client.py Client`
- **test_accounting_model.py**: Verificar `grep -r "class AccountType" modules/ --include="*.py" -A 20`
- **test_reports_model.py**: Verificar `grep -r "class ReportType" modules/ --include="*.py" -A 20` e `grep -r "class KPICategory" modules/ --include="*.py" -A 20`
- **test_config_model.py**: Verificar TenantSettings, FeatureFlag com required-fields.py
- **test_config_service.py**: Provavelmente erros de mock (import direto em vez de mock). Verificar se faz `from main import app` em vez de usar lazy-load.

**COMMIT a cada arquivo corrigido:**
```bash
git add tests/ARQUIVO.py
git commit -m "fix(tests): corrige test_client_model — X/Y passando"
```

---

### BLOCO 2: Investigar Collection Errors (218 errors)

Após o Bloco 1, os 218 errors podem ter diminuído. Verificar:

```bash
python -m pytest --tb=no -q 2>&1 | tail -5
```

Se ainda houver errors, investigar:
```bash
python -m pytest --tb=line -q 2>&1 | grep "^ERROR" | head -30
```

Para cada group de errors:
- Se é fixture missing → já tem async_client no conftest.py, verificar se faltam outras
- Se é import error → verificar se o módulo existe
- Se é TypeError na collection → provavelmente conftest.py problem

---

### BLOCO 3: Segurança — Plano Mestre Fase 4

```bash
cd /opt/conecta-pro/backend && source venv/bin/activate

# 3.1 — SHA1 usedforsecurity
# Arquivos: modules/government_integrations/core/nfce_manager.py e xml_signer.py
# Trocar: hashlib.sha1(data) → hashlib.sha1(data, usedforsecurity=False)

# 3.2 — SSL verify=False
# Arquivo: modules/government_integrations/core/sefaz_am.py
# Adicionar comentário: # noqa: S501 - SEFAZ AM usa cert self-signed

# 3.3 — Permissão .env
chmod 600 /opt/conecta-pro/backend/.env

# Verificar:
bandit -r modules/ -q --severity-level high 2>&1 | tail -10
```

---

### BLOCO 4: EmailTemplate Duplicado — Plano Mestre Fase 5

```bash
# Encontrar todas as definições
grep -rn "class EmailTemplate" modules/ --include="*.py"

# Ver qual tem __tablename__
grep -B2 -A10 "class EmailTemplate" modules/integrations/email/models/email_template.py
grep -B2 -A10 "class EmailTemplate" modules/ai/email_assistant/models/email.py
grep -B2 -A10 "class EmailTemplate" modules/fase5/email_intelligence/models.py

# Renomear os duplicados (NÃO o principal):
# ai/email_assistant → AIEmailTemplate
# fase5 → Fase5EmailTemplate
# OU importar do principal
```

---

### BLOCO 5: Padronizar JWT — Plano Mestre Fase 6

```bash
# Encontrar uso de python-jose
grep -rn "from jose" /opt/conecta-pro/backend --include="*.py" | grep -v __pycache__ | grep -v venv

# Para cada arquivo: trocar de jose para PyJWT
# from jose import jwt → import jwt
# Atenção: exceptions são diferentes
```

---

### BLOCO 6: Limpeza Frontend — Plano Mestre Fase 7

```bash
cd /opt/conecta-pro/frontend

# Encontrar console.log
grep -rn "console.log" src/ --include="*.ts" --include="*.tsx" | grep -v ".test." | grep -v node_modules

# Remover ou trocar para console.error/logger
# NÃO remover console.error ou console.warn
```

---

### BLOCO 7: Validação Parcial (após cada bloco)

```bash
cd /opt/conecta-pro/backend && source venv/bin/activate
python -m pytest --tb=no -q 2>&1 | tail -5
```

Reportar resultado via kimi-out.jsonl:
```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","from":"kimi","to":"claude","type":"progress","id":"kimi-'$(date +%s)'","priority":"high","subject":"Progresso noturno","content":"Bloco X concluído. Passed: XXXX, Failed: XXX, Errors: XXX. Arquivos corrigidos: X. Commits: X."}' >> /opt/conecta-pro/.comms/messages/kimi-out.jsonl
```

---

## PRIORIDADES (se o tempo for curto)

1. **BLOCO 1 é OBRIGATÓRIO** — Fix dos 15 arquivos (maior impacto no pass rate)
2. BLOCO 2 — Investigation dos errors
3. BLOCO 3 — Security (rápido, 15 min)
4. BLOCO 5 — JWT (rápido, 15 min)
5. BLOCO 4 — EmailTemplate (30 min)
6. BLOCO 6 — console.log (15 min)

**Se só der tempo para 1 bloco: fazer o BLOCO 1 inteiro.**

---

## FERRAMENTAS DISPONÍVEIS (APENAS CONSULTA)

```bash
# Ver campos de um model
python /opt/conecta-pro/scripts/required-fields.py modules/PATH/models/FILE.py ModelName

# Ver enum correto
grep -r "class EnumName" modules/ --include="*.py" -A 20

# Impacto antes de editar
/opt/conecta-pro/scripts/pre-flight.sh arquivo.py

# Verificação rápida
/opt/conecta-pro/scripts/verify-instant.sh
```

**PROIBIDO: qualquer script com --fix**

---

## META DA MANHÃ

Jordan e Claude vão conferir de manhã. O ideal seria:

| Métrica | Atual | Meta manhã |
|---|---|---|
| Passed | 5315 | 5800+ |
| Failed | 718 | <200 |
| Errors | 218 | <50 |
| Pass rate | 84.7% | 95%+ |
| Bandit High | 135 | <10 |
| ESLint errors | 0 | 0 |

**Cada arquivo corrigido = progresso real. Trabalhe a noite toda.**
