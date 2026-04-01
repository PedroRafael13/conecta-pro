# FASE 0 — BASELINE E CONGELAMENTO CONTROLADO
**Data:** 2026-02-12T16:00Z (v4: 2026-02-12T17:44Z)
**Executor:** Claude Opus 4.6 (Program-Manager)
**Branch:** audit/20260211-234159
**Revisão:** v4 — corrigida após reprovação CHIEF-012 (evidência bruta obrigatória)

---

## SNAPSHOT DO ESTADO ATUAL

### Testes
| Suite | Resultado | Nota |
|-------|----------|------|
| Backend pytest | 6232 passed, 43 skipped, 12 xfailed, 3404 warnings | OK (warnings são utcnow deprecated) |
| Frontend vitest | 2468 passed (125 files) | OK (era 2362, +106 dos agentes) |
| Frontend E2E | 2985 listados, 0 executados | NÃO VERIFICADO |

### Qualidade de Código
| Check | Comando | Resultado | Status |
|-------|---------|----------|--------|
| ruff (backend) | `cd /opt/conecta-pro/backend && ./venv/bin/ruff check modules core api` | All checks passed | ✅ VERDE |
| mypy (backend) | `cd /opt/conecta-pro/backend && ./venv/bin/mypy modules` | Found 14746 errors in 916 files (checked 1728 source files) | ❌ VERMELHO |
| ESLint (frontend) | `cd /opt/conecta-pro/frontend && npx eslint .` | 30 errors, 6 warnings | ❌ VERMELHO |
| TypeScript (frontend) | `cd /opt/conecta-pro/frontend && npx tsc --noEmit` | 83 erros em 9 arquivos | ❌ VERMELHO |
| Next.js build | `cd /opt/conecta-pro/frontend && npx next build` | COMPILOU OK | ✅ VERDE |

### Saída bruta — ruff (2026-02-12T17:43:48+00:00)
```
$ cd /opt/conecta-pro/backend && ./venv/bin/ruff check modules core api
warning: The following rules have been removed and ignoring them has no effect:
    - UP038

All checks passed!
```
**Config ativa** (`pyproject.toml` [tool.ruff].select): E, F, I, N, W, UP, B, C4, SIM, A
**Versão:** ruff 0.14.14
**Nota A003:** `report_section.py:203` usa `remote_side=[id]` (padrão SQLAlchemy). O `# noqa: A003` na linha 205 suprime a violação. Com regra A ativa na config, ruff passa.

### Saída bruta — mypy (2026-02-12T17:44:00+00:00)
```
$ cd /opt/conecta-pro/backend && ./venv/bin/mypy modules
Found 14746 errors in 916 files (checked 1728 source files)
```
**Config ativa** (`pyproject.toml` [tool.mypy]): explicit_package_bases=true, ignore_missing_imports=true, check_untyped_defs=false
**Nota:** Os 14.746 erros são dívida técnica pré-existente. mypy nunca foi enforçado neste projeto. O erro original de "duplicate module services" foi resolvido por `explicit_package_bases = true`.

### Alterações feitas ao pyproject.toml nesta sessão
1. Adicionado `"A"` (flake8-builtins) ao `[tool.ruff].select`
2. Adicionado seção `[tool.mypy]` completa (não existia antes)

**NOTA DE DIVERGÊNCIA:** Se o chefe executar e obtiver resultado diferente, verificar:
- Se `pyproject.toml` está atualizado (mudanças desta sessão não commitadas)
- CWD deve ser `/opt/conecta-pro/backend`
- ruff e mypy devem ser chamados via `./venv/bin/`

### Segurança — Dependências
| Scanner | Resultado | Status |
|---------|----------|--------|
| safety (Python) | 2 vulns reportadas (sentry-sdk, h11) + 20 ignoradas | ❌ |
| npm audit (Node) | 2 high (xlsx — sem fix disponível) | ❌ |

### Segurança — Segredos no Repo (P0)
- `.env` com JWT_SECRET_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY
- `docker-compose.prod.yml` com JWT_SECRET_KEY hardcoded
- `credentials/certificates/*.pem/*.key` com chaves privadas
- `scripts/deploy.sh` e `deploy/update-dns.sh` com API_TOKEN

### Mudanças Pendentes (não commitadas)
- 37 arquivos modificados
- 8 arquivos novos (untracked)
- Inclui fixes críticos: hasPermission null check, cache headers, sw.js, global-error.tsx

### Infraestrutura
- 20 containers rodando (verified via HANDOFF)
- SSL válido até 2026-04-16
- Backup diário 3AM UTC

---

## MAPA DE AGENTES E FRENTES

### Frente A: Segurança + Qualidade (Fases 1-4)
| Agente | Task ID | Fase | Escopo |
|--------|---------|------|--------|
| Security-Lead | SEC-001 | 1-2 | Segredos P0, OAuth, deps vulneráveis |
| Backend-Lead | BACK-001 | 3 | ruff, mypy, deps pinning, warnings |
| Frontend-Lead | FRONT-001 | 4 | ESLint (30 erros), TSC (83 erros), next.config |

### Frente B: Dados + SRE + Observabilidade (Fases 5-7)
| Agente | Task ID | Fase | Escopo |
|--------|---------|------|--------|
| Data-Lead | DATA-001 | 5 | Schema, migrações, DR test |
| SRE-Lead | SRE-001 | 7 | Docker, healthchecks, alertas, runbooks |
| QA-Lead | QA-001 | 6 | E2E critical paths, smoke suite, flakiness |

### Frente C: Release Readiness (Fase 8)
| Agente | Task ID | Fase | Escopo |
|--------|---------|------|--------|
| Release-Lead | REL-001 | 8 | Go/no-go, checklist, rollback |
| Audit-Lead | AUD-001 | cross | Evidências, rastreabilidade, conformidade |

### Orquestração
| Agente | Task ID | Fase | Escopo |
|--------|---------|------|--------|
| Program-Manager | BOOTSTRAP-001 | 0 | Baseline, coordenação, dependências |

---

## SLO/SLI ALVO PARA GO-LIVE

| Métrica | SLI | SLO |
|---------|-----|-----|
| Disponibilidade | Uptime do /health | ≥99.5% |
| Latência | P95 response time | ≤200ms |
| Erros | 5xx rate | ≤0.1% |
| Segurança | Segredos no repo | 0 |
| Segurança | CVE high/critical | 0 bloqueadores |
| Qualidade | TSC errors | 0 |
| Qualidade | ESLint errors | 0 |
| Testes | Backend pytest pass rate | 100% |
| Testes | Frontend vitest pass rate | 100% |
| Testes | E2E smoke critical | 100% verde |

---

## GATES DE APROVAÇÃO (STATUS INICIAL)

| Gate | Descrição | Status |
|------|-----------|--------|
| A | Sem segredos no repo | ❌ FAIL |
| B | Deps sem high/critical bloqueador | ❌ FAIL |
| C | OAuth/WS sem token em URL | ❌ FAIL |
| D | Lint + typecheck 100% verde | ❌ FAIL |
| E | Build backend/frontend verde | ⚠️ PARTIAL |
| F | Unit + integration + E2E crítico verde | ⚠️ PARTIAL |
| G | Observabilidade e alertas validados | ⚠️ PARTIAL |
| H | Plano de rollback e DR testado | ⚠️ PARTIAL |
