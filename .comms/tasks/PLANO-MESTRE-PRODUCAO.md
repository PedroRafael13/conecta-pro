# PLANO MESTRE — Conecta PRO 100% Produção

> **Autor:** Claude Opus 4.6 (Auditor)
> **Executor:** Kimi K2.5 (100 sub-agentes)
> **Data:** 2026-02-09
> **Objetivo:** Resolver TODOS os bloqueadores para produção
> **Qualidade mínima:** 99.5% — qualquer coisa inferior será REJEITADA

---

## REGRAS ABSOLUTAS (NÃO NEGOCIÁVEIS)

1. **NUNCA declare sucesso sem verificar com comandos reais**
2. **NUNCA invente correções — leia o código ANTES de modificar**
3. **SEMPRE rode o comando de verificação APÓS cada correção**
4. **SEMPRE teste DUAS vezes antes de dar por entregue**
5. **NÃO modifique arquivos em `src/types/generated/`** (são auto-gerados pelo Orval)
6. **NÃO delete código que não entende — pergunte primeiro**
7. **NÃO faça commits parciais — só commite quando a fase INTEIRA passar**
8. **SEMPRE atualize MEMORY.md com lições aprendidas**
9. **USE seus 100 sub-agentes para paralelizar trabalho independente**
10. **Claude Opus está auditando TUDO em tempo real**

---

## BASELINE ATUAL (antes de começar)

| Métrica | Valor |
|---------|-------|
| Pytest collection errors | **159** |
| Pytest tests collected | 1.531 |
| Pytest tests passing | 44/44 (apenas 3 test files executam) |
| Ruff errors | 0 |
| Bandit High | 4 |
| Alembic heads | 12 (não mergeados) |
| ESLint errors (frontend) | 1.170 |
| ESLint warnings (frontend) | 473 |
| TypeScript errors | 0 |
| Frontend tests | 1985/1985 PASS |
| console.log no frontend | 38 |
| EmailTemplate duplicados | 4 locais |

---

## FASE 1 — PYTEST COLLECTION ERRORS (CRÍTICO)
**Prioridade:** MÁXIMA
**Sub-agentes sugeridos:** 10-15 paralelos
**Tempo estimado:** 1-2 horas

### Diagnóstico
Os 159 erros se dividem assim:

| Erro | Quantidade | Causa |
|------|-----------|-------|
| `ModuleNotFoundError: No module named 'core.auth'` | 86 | Import absoluto errado |
| `ModuleNotFoundError: No module named 'core.models'` | 33 | Import absoluto errado |
| `ModuleNotFoundError: No module named 'core.database'` | 16 | Import absoluto errado |
| `ModuleNotFoundError: No module named 'core.logging'` | 6 | Import absoluto errado |
| `ModuleNotFoundError: No module named 'core.security'` | 4 | Import absoluto errado |
| `ModuleNotFoundError: No module named 'core.config'` | 3 | Import absoluto errado |
| `ModuleNotFoundError: No module named 'modules.workflows'` | 2 | Módulo inexistente |
| `ModuleNotFoundError: No module named 'modules.remote_gatehouse'` | 2 | Módulo inexistente |
| `KeyError: 'modules.financial'` | 2 | SQLAlchemy registry |
| Outros | ~5 | Variados |

### Estratégia

**93% dos erros (148/159)** são `ModuleNotFoundError: No module named 'core.*'`. O problema é que os testes fazem imports como:
```python
from core.auth import get_current_user  # FALHA
```
Quando deveriam estar mockando ou o PYTHONPATH não está configurado.

### Instruções Passo a Passo

#### 1.1 — Verificar conftest.py e pytest.ini
```bash
cd /opt/conecta-pro/backend
cat pytest.ini
cat conftest.py | head -40
```
Verificar se `pythonpath = .` está no pytest.ini. Se não estiver, adicionar:
```ini
[pytest]
pythonpath = .
```

#### 1.2 — Verificar se os módulos core existem
```bash
ls -la /opt/conecta-pro/backend/core/
ls -la /opt/conecta-pro/backend/core/auth/
ls -la /opt/conecta-pro/backend/core/models/
ls -la /opt/conecta-pro/backend/core/database/
```

#### 1.3 — Se `pythonpath = .` já existe mas não funciona
O problema pode ser que os testes estão em `tests/` e importam `core.*` que existe em `backend/core/`. Verificar a estrutura:
```bash
# O pytest roda de qual diretório?
cat pytest.ini | grep testpaths
# A estrutura é backend/core/ ou core/?
find /opt/conecta-pro/backend -name "__init__.py" -path "*/core/*" -maxdepth 3
```

#### 1.4 — Corrigir imports nos testes (PARALELIZAR)
Se o PYTHONPATH resolve, pular. Senão, para cada grupo de erro:

**Grupo A (86 arquivos — `core.auth`):**
```bash
# Listar todos os arquivos afetados
cd /opt/conecta-pro/backend && python -m pytest --collect-only -q 2>&1 | grep "core.auth" | grep -oP "tests/\S+\.py" | sort -u
```
Em cada arquivo, verificar o import e corrigir se necessário. O padrão correto é:
```python
from unittest.mock import MagicMock, patch
# Mock ao invés de import direto:
with patch('core.auth.get_current_user') as mock_auth:
    mock_auth.return_value = {"id": "test-user-id", "role": "admin"}
```

**Grupo B (33 arquivos — `core.models`):** Mesmo padrão.
**Grupo C (16 arquivos — `core.database`):** Mesmo padrão.
**Grupo D (6+4+3 = 13 arquivos — `core.logging/security/config`):** Mesmo padrão.

#### 1.5 — Módulos inexistentes (4 arquivos)
Para `modules.workflows` e `modules.remote_gatehouse`:
```bash
find /opt/conecta-pro/backend/modules -type d -name "workflows"
find /opt/conecta-pro/backend/modules -type d -name "remote_gatehouse"
```
Se não existem, os testes devem ser movidos para `tests/_orphaned/` ou deletados.

#### 1.6 — KeyError 'modules.financial' (2 arquivos)
Provavelmente `test_bi_dashboard_api.py` e `test_bi_dashboard_models.py` fazem import que carrega o registry do SQLAlchemy. Aplicar o mesmo padrão lazy-load do conftest ou mover para `_orphaned/`.

### Verificação (OBRIGATÓRIA — rodar DUAS vezes)
```bash
cd /opt/conecta-pro/backend && source venv/bin/activate
python -m pytest --collect-only -q 2>&1 | tail -5
# ESPERADO: "X tests collected" e 0 errors
# Se errors > 0, NÃO passe para Fase 2
```

### Critério de Aceite
- **0 collection errors**
- **Todos os 1531+ testes coletados**
- **Rodar `pytest -x -q` e verificar quantos passam**

---

## FASE 2 — ALEMBIC MIGRATIONS MERGE (CRÍTICO)
**Prioridade:** ALTA
**Sub-agentes:** 1 (sequencial, não paralelizável)
**Tempo estimado:** 30-60 min

### Diagnóstico
12 heads independentes. 3 delas partem de `<base>` (sem parent).

### Instruções

#### 2.1 — Mapear a árvore de dependências
```bash
cd /opt/conecta-pro/backend && source venv/bin/activate
alembic heads -v 2>&1
alembic branches -v 2>&1
```

#### 2.2 — Merge sequencial
Merges devem ser feitos 2 a 2, do mais antigo para o mais recente:
```bash
# Exemplo (ajustar IDs reais):
alembic merge heads -m "merge: consolidate all migration heads" --rev-id merge_all_heads
```

**CUIDADO:** Se as migrations têm conflitos de schema (mesma tabela alterada em branches diferentes), o merge automático pode falhar. Nesse caso:
1. Verificar quais tabelas cada migration altera
2. Resolver conflitos manualmente
3. Testar com `alembic upgrade head` em DB de teste

#### 2.3 — Testar upgrade
```bash
# Verificar que há apenas 1 head
alembic heads 2>&1
# ESPERADO: apenas 1 linha

# Testar upgrade (DRY RUN se possível)
alembic upgrade head --sql 2>&1 | tail -20
```

### Critério de Aceite
- **1 única head** no alembic
- **`alembic upgrade head --sql`** gera SQL válido sem erros

---

## FASE 3 — ESLINT FRONTEND (ALTO)
**Prioridade:** ALTA
**Sub-agentes:** 5-10 paralelos
**Tempo estimado:** 1-2 horas

### Diagnóstico
- 1.115/1.643 erros estão em `src/types/generated/` (67.9%)
- Regra dominante: `react-hooks/immutability` (1.107 erros, 94.6%)
- 428 warnings são auto-fixáveis
- 385 erros em código manual

### Instruções

#### 3.1 — Ignorar `src/types/generated/` no ESLint
Esses arquivos são gerados pelo Orval e NÃO devem ser editados manualmente.

Verificar qual config existe:
```bash
ls /opt/conecta-pro/frontend/eslint.config.* /opt/conecta-pro/frontend/.eslintrc* 2>/dev/null
```

Adicionar ignore pattern para `src/types/generated/**` na config ESLint.

Se for `eslint.config.mjs` (flat config):
```javascript
{
  ignores: ["src/types/generated/**"]
}
```

Se for `.eslintrc.json`:
```json
{
  "ignorePatterns": ["src/types/generated/**"]
}
```

**Isso elimina 1.115 problemas de uma vez.**

#### 3.2 — Auto-fix warnings
```bash
cd /opt/conecta-pro/frontend && npx eslint src/ --fix --ignore-pattern "src/types/generated/**"
```
Isso corrige ~428 warnings automaticamente.

#### 3.3 — Corrigir erros manuais (385 restantes)
Dividir por regra e paralelizar sub-agentes:

| Regra | Erros | Ação |
|-------|-------|------|
| `react-hooks/immutability` | ~60 | Usar spread operator em vez de mutação direta |
| `react-hooks/set-state-in-effect` | 46 | Mover setState para callbacks |
| `react-hooks/exhaustive-deps` | 30 | Adicionar deps faltantes ou `// eslint-disable-next-line` com justificativa |
| `import/no-anonymous-default-export` | 15 | Nomear exports anônimos |
| `react/no-unescaped-entities` | 10 | Usar `&apos;` etc. |
| Outros | ~4 | Case by case |

**Para cada arquivo:**
1. Ler o arquivo
2. Entender o contexto
3. Corrigir o erro seguindo o padrão React/Next.js
4. Verificar que não quebrou nada

#### 3.4 — Verificação
```bash
cd /opt/conecta-pro/frontend
npx eslint src/ --ignore-pattern "src/types/generated/**" 2>&1 | tail -5
# ESPERADO: 0 errors, 0 warnings (ou mínimo residual justificado)

# Verificar que testes ainda passam
npx vitest run 2>&1 | tail -5
# ESPERADO: 1985/1985 PASS

# Verificar build
npx next build 2>&1 | tail -5
# ESPERADO: build sem erros

# TypeScript
npx tsc --noEmit 2>&1 | tail -5
# ESPERADO: 0 errors
```

### Critério de Aceite
- **0 ESLint errors** (excluindo `types/generated/`)
- **0 ESLint warnings** (excluindo `types/generated/`)
- **1985/1985 testes passando**
- **Build OK**
- **TypeScript 0 errors**

---

## FASE 4 — SEGURANÇA (ALTO)
**Prioridade:** ALTA
**Sub-agentes:** 4 paralelos (1 por issue)
**Tempo estimado:** 30 min

### 4.1 — SHA1 em NFe/NFCe (B324)
**Arquivos:**
- `modules/government_integrations/core/nfce_manager.py:162`
- `modules/government_integrations/core/xml_signer.py:262`

**Ação:** Adicionar `usedforsecurity=False` ao hashlib.sha1():
```python
# ANTES:
hashlib.sha1(data)
# DEPOIS:
hashlib.sha1(data, usedforsecurity=False)  # SEFAZ exige SHA1 para assinatura XML NFe
```

### 4.2 — SSL verify=False (B501)
**Arquivos:**
- `modules/government_integrations/core/sefaz_am.py:216`
- `scripts/test_gov_connections.py:389`

**Ação para sefaz_am.py:** Usar certificado SSL adequado:
```python
# ANTES:
response = httpx.post(url, verify=False, ...)
# DEPOIS:
response = httpx.post(url, verify="/path/to/sefaz-ca-bundle.pem", ...)
# OU se impossível (SEFAZ com cert self-signed):
response = httpx.post(url, verify=False, ...)  # noqa: S501 - SEFAZ AM usa cert self-signed
```

**Ação para test_gov_connections.py:** Adicionar `# noqa: S501` com justificativa (é script de teste).

### 4.3 — Permissão backend/.env
```bash
chmod 600 /opt/conecta-pro/backend/.env
```

### Verificação
```bash
cd /opt/conecta-pro/backend && source venv/bin/activate
bandit -r . -q --severity-level high 2>&1 | tail -5
# ESPERADO: 0 high severity issues (ou apenas noqa justificados)
```

### Critério de Aceite
- **0 Bandit High** (ou todos com `# noqa` justificado)
- **backend/.env com permissão 600**

---

## FASE 5 — EMAILTEMPLATE DUPLICADO (ALTO)
**Prioridade:** ALTA
**Sub-agentes:** 2-3
**Tempo estimado:** 1 hora

### Diagnóstico
`class EmailTemplate` existe em 4 locais:
1. `modules/integrations/email/models/email_template.py` (PRINCIPAL)
2. `modules/ai/email_assistant/models/email.py`
3. `modules/ai/email_assistant/schemas/email_schemas.py` (schema, não model)
4. `modules/fase5/email_intelligence/models.py`

### Instruções

#### 5.1 — Identificar qual é o model canônico
```bash
# Ver qual mapeia para tabela real
grep -n "__tablename__\|class EmailTemplate" /opt/conecta-pro/backend/modules/integrations/email/models/email_template.py
grep -n "__tablename__\|class EmailTemplate" /opt/conecta-pro/backend/modules/ai/email_assistant/models/email.py
grep -n "__tablename__\|class EmailTemplate" /opt/conecta-pro/backend/modules/fase5/email_intelligence/models.py
```

#### 5.2 — Consolidar
- Manter o model em `modules/integrations/email/models/email_template.py` (mais completo)
- Nos outros módulos, importar dele:
```python
from modules.integrations.email.models.email_template import EmailTemplate
```
- Se `fase5/` e `ai/email_assistant/` têm campos diferentes, criar schemas separados (não models SQLAlchemy duplicados)

#### 5.3 — O arquivo `email.py` no `ai/email_assistant/models/`
O nome `email.py` causa **A005** (shadows stdlib `email`). Renomear para `email_model.py` ou `assistant_email.py`.

### Verificação
```bash
# Verificar que só existe 1 class EmailTemplate mapeando tabela
grep -rn "class EmailTemplate.*Base" /opt/conecta-pro/backend/modules --include="*.py"
# ESPERADO: apenas 1 resultado

# Verificar que testes ainda passam
cd /opt/conecta-pro/backend && source venv/bin/activate
python -m pytest tests/test_operacional_models.py tests/test_core_services.py tests/test_security_headers_middleware.py -q
# ESPERADO: 44/44 PASS
```

### Critério de Aceite
- **1 único model EmailTemplate** mapeando tabela
- **0 imports circulares**
- **44/44 testes passando**

---

## FASE 6 — PADRONIZAR JWT (MÉDIO)
**Prioridade:** MÉDIA
**Sub-agentes:** 1
**Tempo estimado:** 30 min

### Diagnóstico
- Produção (`core/auth/jwt.py`): usa `import jwt` (PyJWT)
- Testes: usam `from jose import jwt` (python-jose)
- Ambos instalados: PyJWT 2.11.0 + python-jose 3.5.0

### Instruções

#### 6.1 — Padronizar em python-jose (recomendado — já é usado nos testes)
**OU** padronizar em PyJWT (já é usado em produção).

**Decisão:** Manter **PyJWT** (é o de produção). Corrigir os testes para usar PyJWT.

```bash
grep -rn "from jose" /opt/conecta-pro/backend --include="*.py" | grep -v __pycache__ | grep -v venv
```

Em cada arquivo de teste que usa `from jose import jwt`, trocar para:
```python
import jwt  # PyJWT (mesmo que produção)
```

**ATENÇÃO:** As APIs são diferentes:
- python-jose: `jwt.decode(token, key, algorithms=["HS256"])`
- PyJWT: `jwt.decode(token, key, algorithms=["HS256"])` (similar mas exceptions diferentes)

Verificar que os testes usam os patterns corretos do PyJWT.

### Verificação
```bash
grep -rn "from jose" /opt/conecta-pro/backend --include="*.py" | grep -v __pycache__ | grep -v venv
# ESPERADO: 0 resultados

cd /opt/conecta-pro/backend && source venv/bin/activate
python -m pytest tests/test_core_services.py -q
# ESPERADO: 11/11 PASS
```

### Critério de Aceite
- **0 imports de `jose`** no código
- **Testes JWT passando**

---

## FASE 7 — LIMPEZA FRONTEND (BAIXO)
**Prioridade:** BAIXA
**Sub-agentes:** 3-5 paralelos
**Tempo estimado:** 30 min

### 7.1 — Remover console.log (38 ocorrências)
```bash
grep -rn "console.log" /opt/conecta-pro/frontend/src --include="*.ts" --include="*.tsx" | grep -v node_modules | grep -v ".test."
```

Para cada ocorrência:
- Se é debug/dev: **REMOVER**
- Se é error handling: trocar para `console.error` ou logger
- Se é importante para produção: manter com justificativa

### 7.2 — Verificação
```bash
cd /opt/conecta-pro/frontend
grep -rn "console.log" src/ --include="*.ts" --include="*.tsx" | grep -v ".test." | wc -l
# ESPERADO: 0 (ou mínimo justificado)

npx vitest run 2>&1 | tail -5
# ESPERADO: 1985/1985 PASS
```

---

## FASE 8 — VALIDAÇÃO FINAL (OBRIGATÓRIA)
**Prioridade:** MÁXIMA
**Sub-agentes:** Todos disponíveis para rodar em paralelo
**Tempo estimado:** 30 min

### Rodar TODOS os checks em paralelo:

```bash
# 1. Backend lint
cd /opt/conecta-pro/backend && source venv/bin/activate && ruff check . 2>&1 | tail -5

# 2. Backend tests collection
cd /opt/conecta-pro/backend && source venv/bin/activate && python -m pytest --collect-only -q 2>&1 | tail -5

# 3. Backend tests execution
cd /opt/conecta-pro/backend && source venv/bin/activate && python -m pytest -q 2>&1 | tail -10

# 4. Backend security
cd /opt/conecta-pro/backend && source venv/bin/activate && bandit -r . -q --severity-level high 2>&1 | tail -5

# 5. Alembic heads
cd /opt/conecta-pro/backend && source venv/bin/activate && alembic heads 2>&1

# 6. Frontend TypeScript
cd /opt/conecta-pro/frontend && npx tsc --noEmit 2>&1 | tail -5

# 7. Frontend ESLint
cd /opt/conecta-pro/frontend && npx eslint src/ --ignore-pattern "src/types/generated/**" 2>&1 | tail -5

# 8. Frontend tests
cd /opt/conecta-pro/frontend && npx vitest run 2>&1 | tail -5

# 9. Frontend build
cd /opt/conecta-pro/frontend && npx next build 2>&1 | tail -5

# 10. Git status
cd /opt/conecta-pro && git status --short | wc -l
```

### Tabela de Resultados (preencher)

| # | Check | Resultado | Status |
|---|-------|-----------|--------|
| 1 | Ruff errors | ___ | __ |
| 2 | Pytest collection errors | ___ | __ |
| 3 | Pytest tests pass/fail | ___/___ | __ |
| 4 | Bandit High | ___ | __ |
| 5 | Alembic heads | ___ | __ |
| 6 | TypeScript errors | ___ | __ |
| 7 | ESLint errors | ___ | __ |
| 8 | Frontend tests | ___/___ | __ |
| 9 | Frontend build | ___ | __ |
| 10 | Uncommitted files | ___ | __ |

### Critérios de Aceite FINAIS

| Métrica | Mínimo Aceitável |
|---------|-----------------|
| Ruff errors | 0 |
| Pytest collection errors | 0 |
| Pytest tests passing | ≥95% |
| Bandit High | 0 (ou com noqa justificado) |
| Alembic heads | 1 |
| TypeScript errors | 0 |
| ESLint errors (sem generated) | 0 |
| Frontend tests | 1985/1985 |
| Frontend build | OK |
| Uncommitted files | 0 |

---

## ORDEM DE EXECUÇÃO

```
FASE 1 (collection errors) ──────────────────────┐
FASE 3 (ESLint frontend) ───────────────────────┐ │
FASE 4 (segurança) ────────────────────────────┐ │ │
FASE 7 (console.log) ────────────────────────┐ │ │ │
                                              │ │ │ │
                                              ▼ ▼ ▼ ▼
                              PARALELO (sub-agentes)
                                              │
                                              ▼
                                    FASE 2 (alembic) ← sequencial
                                              │
                                              ▼
                              FASE 5 (EmailTemplate) ← depende de F1
                                              │
                                              ▼
                                    FASE 6 (JWT) ← depende de F1
                                              │
                                              ▼
                                FASE 8 (validação final)
                                              │
                                              ▼
                                           COMMIT
```

**Fases 1, 3, 4, 7:** PARALELAS (independentes entre si)
**Fases 2, 5, 6:** SEQUENCIAIS (dependem das anteriores)
**Fase 8:** ÚLTIMA (validação de tudo)

---

## COMMIT FINAL

Após Fase 8 passar com 100%:

```bash
cd /opt/conecta-pro
git add -A
git commit -m "feat: resolve todos os bloqueadores para produção

- Fix 159 pytest collection errors (imports core.*)
- Merge 12 alembic heads em 1
- Fix 1170 ESLint errors (ignore generated + manual fixes)
- Fix 4 Bandit High (SHA1 usedforsecurity, SSL verify)
- Consolidar EmailTemplate (4 → 1 model)
- Padronizar JWT (python-jose → PyJWT)
- Remover 38 console.log
- Permissão backend/.env 600

Co-Authored-By: Kimi K2.5 <noreply@kimi.ai>"
```

---

## COMUNICAÇÃO

Após cada fase:
1. Enviar mensagem via `.comms/messages/kimi-out.jsonl` com resultado
2. Se qualquer verificação falhar, PARAR e reportar ao Claude
3. Se não sabe como resolver algo, PERGUNTAR antes de inventar
4. Nunca declarar "100%" sem ter rodado os 10 checks da Fase 8
