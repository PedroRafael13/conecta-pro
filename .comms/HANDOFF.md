# HANDOFF — Estado Atual do Projeto (Consolidado)

Última atualização: 2026-02-15T16:25Z por Claude Opus 4.6 (Executor)
Branch: audit/20260211-234159
Último commit: 85de73b6 (NAO COMMITADO — mudancas pendentes abaixo)
Mudancas pendentes: SIM — ver secao abaixo

---

## TAREFA EM ANDAMENTO: Task Team — Plano Mestre de Producao

### Status: Fase 1 concluida (execucao), Fases 2-8 pendentes

### Contexto
- Codex 5.3 e o chefe/auditor do Task Team
- Claude Opus 4.6 e o executor com 9 agentes virtuais
- Canal bidirecional ativo: /opt/conecta-pro/.comms/task-team/
- Plano mestre: /opt/conecta-pro/audit/CLAUDE_TASK_TEAM_OPUS46_MASTER_PLAN_20260212-153807.md

### Fase 0 — Baseline aprovado (v4)
- Artefato: /opt/conecta-pro/audit/PHASE0_BASELINE_20260212.md
- Baseline anterior: pytest 6232 OK, vitest 2468 OK, ruff PASS, mypy 14746 errs, ESLint 30 errs, TSC 83 errs

### Fase 1 — Seguranca P0 — ROTACAO EM ANDAMENTO
- Artefatos anteriores:
  - /opt/conecta-pro/audit/PHASE1_SECRET_INVENTORY_20260212.md
  - /opt/conecta-pro/audit/PHASE1_ROTATION_PLAN_20260212.md
  - /opt/conecta-pro/audit/PHASE1_REMEDIATION_PROGRESS_20260212.md
  - /opt/conecta-pro/audit/PHASE1_PREVENTION_PLAN_20260212.md
- Feito (sessoes anteriores):
  - .gitignore hardened (+8 patterns seguranca)
  - 14 credenciais removidas do git tracking (git rm --cached)
  - Backup chaves privadas em /opt/conecta-secrets/certificates/ (chmod 600)
  - docker-compose.prod.yml: 0 hardcoded, tudo via env vars requeridas
  - Pre-commit: detect-secrets adicionado (3 scanners)
  - .secrets.baseline gerado
- Rotacoes executadas nesta sessao (2026-02-15):
  PRODUCAO:
  - JWT_SECRET_KEY: ROTACIONADO (token_urlsafe 64 bytes, backend recriado, healthy)
  - JWT_SECRET_KEY_STAGING: ROTACIONADO 2x (primeiro exposto em sessão, re-rotacionado)
  - POSTGRES_PASSWORD: ROTACIONADO (era "postgres" → hex 96 chars, ALTER ROLE + backend recriado)
  - REDIS_PASSWORD: ROTACIONADO (hex 96 chars, CONFIG SET + backend+celery recriados, P0 URL-parsing RESOLVIDO)
  STAGING:
  - JWT_SECRET_KEY_STAGING: ROTACIONADO 2x
  - POSTGRES_PASSWORD_STAGING: ROTACIONADO (ALTER ROLE + compose atualizado)
  - REDIS_PASSWORD_STAGING: ROTACIONADO (requirepass + URLs autenticadas no compose)
  - Certificados staging (Inter/Cora/A1): INFRA PRONTA, dirs criados, aguardando Jordan
  CERTIFICADOS PRODUCAO:
  - Inter/Cora/A1: todos validos (~11 meses), rotação requer ação manual Jordan nos portais
- Alteracoes no docker-compose.staging.yml:
  - POSTGRES_PASSWORD -> POSTGRES_PASSWORD_STAGING (4 refs)
  - Redis URLs -> autenticadas com REDIS_PASSWORD_STAGING (9 refs)
  - Redis command -> --requirepass adicionado
  - Redis healthcheck -> -a password adicionado
- Evidencias desta sessao:
  PRODUCAO:
  - /opt/conecta-pro/.comms/task-team/SEC-ROTATE-JWT-PROD-20260215.md
  - /opt/conecta-pro/.comms/task-team/SEC-ROTATE-POSTGRES-PROD-20260215.md
  - /opt/conecta-pro/.comms/task-team/SEC-ROTATE-REDIS-PROD-20260215.md
  STAGING:
  - /opt/conecta-pro/.comms/task-team/SEC-ROTATE-JWT-STAGING-20260215.md
  - /opt/conecta-pro/.comms/task-team/SEC-ROTATE-POSTGRES-STAGING-20260215.md
  - /opt/conecta-pro/.comms/task-team/SEC-ROTATE-REDIS-STAGING-20260215.md
  - /opt/conecta-pro/.comms/task-team/SEC-ROTATE-CERT-STAGING-20260215.md
- Pendente Jordan (proxima sessao):
  - Certificados Inter/Cora/A1 PROD+STAGING -> gerar nos paineis dos provedores
  - Colocar certs em /opt/conecta-secrets/certificates/{inter,cora,a1}/
  - Rotacao credenciais externas: Google OAuth, Sólides, OpenAI, Anthropic, Telegram, SMTP, Evolution
  - Atualizar CERTIFICATE_PASSWORD no .env
  - Aprovacao para limpeza historico git (filter-branch/force-push)
- Decisoes formais desta sessao:
  - Producao usa docker-compose.yml (principal), NAO docker-compose.prod.yml (legado)
  - Senhas sempre em hex (openssl rand -hex N) para evitar URL-unsafe chars
- Mudanca operacional OPS-CHANGE-001:
  - Permissoes /opt/conecta-pro/logs/*.log corrigidas para UID 999 (user erp)
  - Causa: logrotate cria arquivos como root
  - Recomendacao: ajustar logrotate config

### Auditoria Consolidada 2026-02-13 (ultima execucao)
- Relatorios novos:
  - /opt/conecta-pro/audit/REPORT_20260213-024420.md
  - /opt/conecta-pro/audit/CHECKLIST_PROD_20260213-024420.md
  - /opt/conecta-pro/audit/FIX_BACKLOG_20260213-024420.md
- Seguranca:
  - pip-audit encontrou 16 vulnerabilidades em 7 pacotes (Python runtime)
  - npm audit --omit=dev encontrou 2 high (axios, xlsx)
- Qualidade:
  - ESLint com 30 erros
  - TypeScript com 149 erros (principalmente testes/mocks)
  - Build frontend OK com warning de config do Next
- Testes:
  - Backend pytest OK (6232 passed, 43 skipped, 12 xfailed)
  - Frontend vitest OK (2468 passed) com warnings de act/a11y
  - E2E nao executado (apenas listagem de 2985 testes)
- Observacao: mypy nao foi reexecutado com sucesso nesta rodada; usar baseline anterior (14746 errs) ate nova execucao

### Fases Pendentes (proxima sessao)
| Fase | Escopo | Status |
|------|--------|--------|
| 2 | P1 Seguranca app (OAuth token em URL, deps vulneraveis) | NAO INICIADA |
| 3 | Qualidade backend (mypy 14746 errs, ruff expandido) | NAO INICIADA |
| 4 | Qualidade frontend (ESLint 30 errs, TSC 149 errs, next.config) | NAO INICIADA |
| 5 | Dados e integridade (schema, migracoes, DR) | NAO INICIADA |
| 6 | E2E e qualidade de release (2985 testes nao executados) | NAO INICIADA |
| 7 | Observabilidade e operacao (alertas, runbooks) | NAO INICIADA |
| 8 | Go/No-Go e liberacao | NAO INICIADA |

### Gates de Aprovacao (Consolidado)
| Gate | Descricao | Status |
|------|-----------|--------|
| A | Sem segredos no repo | PARCIAL (tracking limpo, falta rotacao + historico) |
| B | Deps sem high/critical | FAIL (pip-audit + npm audit) |
| C | OAuth/WS sem token em URL | FAIL (auth.py:466-475) |
| D | Lint + typecheck verde | FAIL (ESLint 30, TSC 149, mypy 14746) |
| E | Build verde | PASS (warning config) |
| F | Testes verdes | PARTIAL (unit OK, E2E nao executado) |
| G | Observabilidade validada | PARTIAL |
| H | Rollback/DR testado | PARTIAL |

### Mudancas NAO Commitadas
Seguranca (Fase 1):
- .gitignore — +8 patterns de seguranca
- docker-compose.prod.yml — secrets via env vars
- .pre-commit-config.yaml — detect-secrets adicionado
- .secrets.baseline — NOVO
- credentials/ — removido do tracking (14 arquivos)

Qualidade (pyproject.toml):
- backend/pyproject.toml — ruff +A rules, [tool.mypy] adicionado

Testes (sessao anterior — agentes paralelos + fixes):
- ~30 arquivos de teste frontend (branch coverage)
- frontend/src/hooks/__tests__/useNotifications.test.ts — fix fake timers
- frontend/src/hooks/__tests__/useReimbursement.test.ts — fix require alias

Dashboard fix (sessao anterior):
- backend/api/v1/endpoints/auth.py — Response param slowapi
- frontend/src/types/modules.ts — hasPermission null check
- frontend/next.config.ts — cache headers fix
- frontend/public/sw.js — auto-destruct SW
- frontend/src/app/global-error.tsx — error boundary (NOVO)

### PROXIMA SESSAO — O que fazer
1. Ler canal: cat /opt/conecta-pro/.comms/task-team/to_executor.md
2. Ler este HANDOFF para contexto completo
3. Jordan traz: certificados Inter/Cora/A1 (PROD+STAGING) + credenciais API rotacionadas
4. Aplicar certificados (chmod 600), atualizar .env, recreate backend PROD+STAGING
5. Aplicar credenciais restantes (Google, Sólides, OpenAI, Anthropic, Telegram, SMTP, Evolution)
6. Criar evidência SEC-ROTATE-CERT-PROD + SEC-ROTATE-APIKEYS-PROD
7. Fechar Fase 1 (Gate A → PASS)
8. Continuar Fase 2: OAuth fix + deps vulneráveis
9. Checkpoint a cada 20 min no to_chief.md

### NOTA: Mismatch porta staging (pre-existente)
- docker-compose.staging.yml configura PORT=8081 e ports 8081:8081
- Mas Dockerfile hardcoda uvicorn --port 8080
- Resultado: staging inacessivel via localhost:8081, health check Docker falha
- Fix recomendado: alterar ports para 8081:8080 ou CMD para usar $PORT

---

## Infraestrutura
- Servidor: 82.25.75.74 — Ubuntu 24.04, 4 CPUs, 16GB RAM
- URL: https://erp.conectamais.pro (LIVE)
- 20 containers rodando
- SSL: Lets Encrypt valido ate 2026-04-16
- Backup: Diario 3AM UTC

## Comunicacao Task Team
- Canal chefe→executor: /opt/conecta-pro/.comms/task-team/to_executor.md
- Canal executor→chefe: /opt/conecta-pro/.comms/task-team/to_chief.md
- Eventos: /opt/conecta-pro/.comms/task-team/events.ndjson
- Plano mestre: /opt/conecta-pro/audit/CLAUDE_TASK_TEAM_OPUS46_MASTER_PLAN_20260212-153807.md
- Model lock: claude-opus-4.6 obrigatorio em todas as tasks
