# PLANO DE TRABALHO CONSOLIDADO
## Auditorias Kimi K2.5 + Claude Opus 4.6 - Conecta PRO v2.0

**Data:** 06/02/2026
**Notas:** Kimi 70.60/100 | Claude 72.15/100
**Status:** ADEQUADO/REGULAR (B)
**Objetivo:** Alcançar 85/100 (BOM) em 30 dias

---

## 🎯 CONSOLIDAÇÃO DOS ACHADOS

### Prioridade CRÍTICA (Segurança & Estabilidade)

| # | Problema | Kimi | Claude | Impacto |
|---|----------|------|--------|---------|
| 1 | **Secrets em .env** (JWT_SECRET_KEY, OPENAI_API_KEY) | ❌ Não detectou | 🔴 Encontrou | CRÍTICO |
| 2 | **python-jose vulnerável** (2021) | ❌ Não detectou | 🔴 Encontrou | CRÍTICO |
| 3 | **337 bare `except:`** | 🔴 337 | 🔴 Encontrados | CRÍTICO |
| 4 | **1263 testes backend falhando** | ✅ Corrigidos | 🔴 1263 falhas | CRÍTICO |
| 5 | **localhost em CORS produção** | ✅ Correto | 🔴 Encontrou | ALTO |
| 6 | **Rate limiting incompleto** | ❌ 0/10 | 🟡 8/10 (parcial) | ALTO |

### Prioridade ALTA (Qualidade & Manutenibilidade)

| # | Problema | Kimi | Claude | Impacto |
|---|----------|------|--------|---------|
| 7 | **308 violações Ruff** | ⚠️ Estimativa | 🔴 308 específicas | ALTO |
| 8 | **27 imports circulares** | ❌ Não detectou | 🔴 Encontrados | ALTO |
| 9 | **16 hooks duplicados** | ❌ Não detectou | 🔴 Encontrados | ALTO |
| 10 | **261 usos de `:any`** | ❌ Não detectou | 🔴 261 específicos | ALTO |
| 11 | **N+1 queries** | 🔴 106 | 🟡 ~40% sem otimização | ALTO |
| 12 | **JSONB overuse** | 🟡 3 colunas | 🔴 23 colunas | ALTO |

---

## 📋 PLANO DE TRABALHO - 30 DIAS

### FASE 1: CRÍTICO (Dias 1-7)
**Objetivo: Segurança e estabilidade básica**

#### Dia 1-2: Segurança Imediata
```bash
# RESPONSÁVEL: DevSecOps
# TEMPO: 16 horas
```

| Tarefa | Descrição | Comando/Script | Critério de Sucesso |
|--------|-----------|----------------|---------------------|
| 1.1 | Rotacionar secrets | `openssl rand -base64 32` | Novos secrets em arquivo separado |
| 1.2 | Mover secrets do .env | Criar `.env.secrets` (gitignored) | `.env` sem secrets hardcoded |
| 1.3 | Migrar python-jose | `pip install PyJWT` + refactor | Tests passando com PyJWT |
| 1.4 | Remover localhost CORS | Editar `main.py` | Apenas domínios prod em CORS |

**Validação:**
```bash
gitleaks detect --no-git -v /opt/conecta-pro/  # 0 secrets
grep -c "python-jose" requirements.txt  # 0
```

#### Dia 3-4: Correção de Testes
```bash
# RESPONSÁVEL: QA + Backend
# TEMPO: 16 horas
```

| Tarefa | Descrição | Critério de Sucesso |
|--------|-----------|---------------------|
| 2.1 | Instalar pytest-cov | `pip install pytest-cov` | Cobertura mensurável |
| 2.2 | Corrigir imports quebrados | Resolver 21 arquivos com import errors | `pytest --collect-only` passa |
| 2.3 | Corrigir 1263 testes falhando | Batch fix por categoria | >90% testes passando |
| 2.4 | Configurar CI testes | GitHub Actions | Block PR se tests < 90% |

**Métrica:**
- Antes: 1263 falhando, 459 errors
- Depois: < 100 falhando, 0 errors

#### Dia 5-7: Tratamento de Exceções
```bash
# RESPONSÁVEL: Backend
# TEMPO: 24 horas
```

| Tarefa | Descrição | Script | Critério |
|--------|-----------|--------|----------|
| 3.1 | Listar bare excepts | `grep -rn "except:" --include="*.py"` | Lista de 337 ocorrências |
| 3.2 | Corrigir batch 1 | `sed -i 's/except:/except Exception:/g'` | 100 arquivos corrigidos |
| 3.3 | Corrigir batch 2 | Refatorar manualmente | 100 arquivos corrigidos |
| 3.4 | Corrigir batch 3 | Refatorar manualmente | 137 restantes |
| 3.5 | Validar | `grep -c "except:"` | Apenas `except Exception:` |

---

### FASE 2: ALTA (Dias 8-18)
**Objetivo: Qualidade de código e performance**

#### Dia 8-11: Backend Code Quality
```bash
# RESPONSÁVEL: Backend + Tech Lead
# TEMPO: 32 horas
```

| # | Tarefa | Ferramenta | Critério |
|---|--------|------------|----------|
| 4.1 | Configurar Ruff | `pip install ruff` + `pyproject.toml` | ruff check passando |
| 4.2 | Auto-fix violações | `ruff check --fix .` | < 50 violações restantes |
| 4.3 | Resolver imports circulares | Lazy imports + TYPE_CHECKING | 0 imports circulares |
| 4.4 | Refatorar funções complexas | Extrair 18 funções CC>10 | CC máximo < 10 |
| 4.5 | Adicionar type hints | `mypy --strict` | 60% type coverage |

**Script de automação:**
```python
#!/usr/bin/env python3
# fix_imports.py - Resolver imports circulares

import re
import sys

for filepath in sys.argv[1:]:
    with open(filepath, 'r') as f:
        content = f.read()

    # Adicionar TYPE_CHECKING
    if 'from typing import' not in content:
        content = content.replace(
            'from typing import',
            'from typing import TYPE_CHECKING\nfrom typing import'
        )

    # Mover imports para TYPE_CHECKING block
    content = re.sub(
        r'^(from \.models import|from \.schemas import)',
        r'if TYPE_CHECKING:\n    \1',
        content,
        flags=re.MULTILINE
    )

    with open(filepath, 'w') as f:
        f.write(content)
```

#### Dia 12-14: Frontend Code Quality
```bash
# RESPONSÁVEL: Frontend
# TEMPO: 24 horas
```

| # | Tarefa | Descrição | Critério |
|---|--------|-----------|----------|
| 5.1 | Consolidar hooks duplicados | Merge 16 hooks duplicados | 0 duplicados |
| 5.2 | Eliminar `:any` críticos | Refatorar 261 usos | < 50 usos de `:any` |
| 5.3 | Corrigir 18 erros TS | `tsc --noEmit` | 0 erros em produção |
| 5.4 | Configurar strict mode | `tsconfig.json` | strict: true |

#### Dia 15-18: Database Optimization
```bash
# RESPONSÁVEL: DBA + Backend
# TEMPO: 32 horas
```

| # | Tarefa | SQL/Script | Critério |
|--------|-----------|------------|----------|
| 6.1 | Analisar queries N+1 | `grep -r "for.*in.*\.all()"` | < 20 patterns restantes |
| 6.2 | Adicionar selectinload | Refatorar queries | 80% queries otimizadas |
| 6.3 | Criar índices compostos | `CREATE INDEX` | índices em (condominio_id, status) |
| 6.4 | Normalizar JSONB | Migrar 23 colunas JSONB | < 10 colunas JSONB |
| 6.5 | Configurar pool health | `pool_pre_ping=True` | Sem conexões stale |

**Migration exemplo:**
```sql
-- migrations/20260206_add_composite_indexes.sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_condominio_status
ON condominios (condominio_id, status);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_faturas_vencimento
ON faturas (condominio_id, vencimento, status);
```

---

### FASE 3: MÉDIA (Dias 19-25)
**Objetivo: LGPD, documentação e refinamentos**

#### Dia 19-21: LGPD Compliance
```bash
# RESPONSÁVEL: Backend + Legal
# TEMPO: 24 horas
```

| # | Tarefa | Endpoint | Critério |
|---|--------|----------|----------|
| 7.1 | Criar endpoint delete/me | `DELETE /api/v1/me` | Usuário pode se excluir |
| 7.2 | Criar endpoint anonymize | `POST /api/v1/me/anonymize` | Dados anonimizados |
| 7.3 | Criar endpoint data/export | `GET /api/v1/me/data` | Exportação JSON/CSV |
| 7.4 | Criar endpoint consent | `POST /api/v1/me/consent` | Gestão de consentimentos |
| 7.5 | Audit log LGPD | Middleware | Log de todas as operações |

#### Dia 22-25: Testes e Cobertura
```bash
# RESPONSÁVEL: QA
# TEMPO: 32 horas
```

| # | Tarefa | Ferramenta | Meta |
|---|--------|------------|------|
| 8.1 | Backend coverage | `pytest-cov` | > 70% cobertura |
| 8.2 | Frontend coverage | `jest --coverage` | > 50% cobertura |
| 8.3 | E2E tests novos | Playwright | +20 specs |
| 8.4 | Testes de contrato | `schemathesis` | Validar OpenAPI |

---

### FASE 4: BAIXA (Dias 26-30)
**Objetivo: Refinamentos e otimizações**

#### Dia 26-28: Performance
```bash
# RESPONSÁVEL: Performance Engineer
# TEMPO: 24 horas
```

| # | Tarefa | Descrição | Meta |
|---|--------|-----------|------|
| 9.1 | Lazy loading 100% | `dynamic()` em todas páginas | 100% lazy loaded |
| 9.2 | Bundle optimization | `next-bundle-analyzer` | First Load < 500KB |
| 9.3 | Redis cache 100% | `@cache` em endpoints | 100% read endpoints |
| 9.4 | Compressão | `gzip` + `brotli` | -30% transfer |

#### Dia 29-30: Documentação e Handoff
```bash
# RESPONSÁVEL: Tech Lead
# TEMPO: 16 horas
```

| # | Tarefa | Entregável |
|---|--------|------------|
| 10.1 | README atualizado | `/docs/DEPLOY.md` |
| 10.2 | Runbooks | `/docs/RUNBOOKS.md` |
| 10.3 | ADRs | `/docs/architecture/` |
| 10.4 | Treinamento equipe | Sessão 2h |

---

## 📊 CRONOGRAMA VISUAL

```
SEMANA 1 (Dias 1-7): CRÍTICO
[████] Dia 1-2: Secrets + python-jose
[████] Dia 3-4: Testes corrigidos
[████] Dia 5-7: Bare excepts

SEMANA 2 (Dias 8-14): ALTA
[████] Dia 8-11: Ruff + imports + type hints
[████] Dia 12-14: Frontend hooks + any

SEMANA 3 (Dias 15-21): ALTA/MÉDIA
[████] Dia 15-18: Database N+1 + índices
[████] Dia 19-21: LGPD endpoints

SEMANA 4 (Dias 22-30): MÉDIA/BAIXA
[████] Dia 22-25: Cobertura testes
[████] Dia 26-28: Performance
[████] Dia 29-30: Documentação
```

---

## 🎯 MÉTRICAS DE SUCESSO (30 dias)

### Segurança
- [ ] gitleaks: 0 secrets expostos
- [ ] python-jose: 0 ocorrências
- [ ] bare except: 0 ocorrências
- [ ] CORS: apenas domínios prod

### Qualidade
- [ ] Ruff: 0 violações
- [ ] Imports circulares: 0
- [ ] Hooks duplicados: 0
- [ ] Uso de `:any`: < 50

### Testes
- [ ] Backend: > 90% passando
- [ ] Cobertura backend: > 70%
- [ ] Cobertura frontend: > 50%
- [ ] E2E: > 150 specs

### Performance
- [ ] N+1 queries: < 20
- [ ] Índices: +20 compostos
- [ ] Lazy loading: 100%
- [ ] First Load JS: < 500KB

---

## 👥 EQUIPE RECOMENDADA

| Função | Qtd | Responsabilidade |
|--------|-----|------------------|
| Tech Lead | 1 | Coordenação, code review |
| Backend Senior | 2 | Testes, Ruff, imports |
| Frontend Senior | 1 | Hooks, TypeScript |
| DBA/DevOps | 1 | Database, migrations |
| QA Engineer | 1 | Testes, cobertura |
| DevSecOps | 1 | Segurança, secrets |

**Total:** 7 pessoas × 30 dias = 210 pessoa-dias

---

## 💰 ESTIMATIVA DE CUSTO

| Recurso | Custo/Dia | Total |
|---------|-----------|-------|
| Equipe técnica (7 pessoas) | R$ 800 | R$ 168.000 |
| Infraestrutura (testes) | - | R$ 5.000 |
| Ferramentas (Snyk, etc) | - | R$ 3.000 |
| **TOTAL** | | **R$ 176.000** |

---

## ⚠️ RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Testes quebrarem produção | Média | Alto | Blue-green deploy |
| Refactor causar regressão | Alta | Médio | Feature flags |
| DBA indisponível | Baixa | Alto | Documentação queries |
| Scope creep | Alta | Médio | Sprints fixos |

---

## ✅ CHECKLIST FINAL (Dia 30)

```bash
# Script de validação final
#!/bin/bash
echo "=== VALIDAÇÃO FINAL ==="

echo "1. Segurança:"
gitleaks detect --no-git -v . | grep -c "Secret" || echo "✅ 0 secrets"
grep -c "except:" backend/app/ || echo "✅ 0 bare excepts"

echo "2. Qualidade:"
ruff check . | grep -c "error" || echo "✅ 0 violações"
grep -r "import.*from.*models" --include="*.py" backend/ | grep -v "TYPE_CHECKING" | wc -l

echo "3. Testes:"
cd backend && pytest --tb=no -q | tail -1
cd frontend && npm test -- --run 2>&1 | grep "passed"

echo "4. Performance:"
curl -s http://localhost:8000/health | jq '.status'
```

---

**Documento consolidado:** Kimi K2.5 + Claude Opus 4.6
**Versão:** 1.0
**Próxima revisão:** 06/03/2026
