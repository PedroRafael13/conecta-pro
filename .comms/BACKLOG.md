# BACKLOG — Tarefas (v6 — DEPLOY PRODUÇÃO)

**Atualizado:** 2026-02-10 por Claude Opus 4.6

---

## Estado Atual: PLANO MESTRE CONCLUÍDO, DEPLOY PENDENTE

### Baseline de código (NÃO regredir):
- **Pytest:** 6287 passed, 0 failed
- **ESLint:** 0 errors, 0 warnings
- **TypeScript:** 0 errors
- **Vitest:** 1985/1985 passed
- **Bandit:** 0 High
- **Alembic:** 1 head
- **Next.js build:** OK

---

## ATIVAS — Plano de Deploy para Produção

| # | Fase | Assignee | Prioridade | Status |
|---|------|----------|------------|--------|
| D1 | Scripts deploy/rollback/health | Opus | CRÍTICA | PENDENTE |
| D2 | Segurança & secrets audit | Opus | CRÍTICA | PENDENTE |
| D3 | AlertManager & notificações | Kimi | ALTA | PENDENTE |
| D4 | Logrotate & Loki retention | Kimi | ALTA | PENDENTE |
| D5 | Backup & DR test | Opus | ALTA | PENDENTE |
| D6 | Load testing (k6) | Kimi | ALTA | PENDENTE |
| D7 | DNS & SSL activation | Jordan | CRÍTICA | CONCLUÍDA (live em erp.conectamais.pro) |
| D8 | Deploy staging (todos os serviços) | Todos | CRÍTICA | PENDENTE |
| D9 | Validação final (15 checks × 3 terminais) | Todos | CRÍTICA | PENDENTE |

**Plano detalhado:** `/opt/conecta-pro/.comms/tasks/PLANO-DEPLOY-PRODUCAO.md`
**Instruções Kimi:** `/opt/conecta-pro/.comms/INSTRUCOES-KIMI-DEPLOY.md`
**Instruções Opus:** `/opt/conecta-pro/.comms/INSTRUCOES-OPUS-DEPLOY.md`
**Instruções Claude:** `/opt/conecta-pro/.comms/INSTRUCOES-CLAUDE-DEPLOY.md`

---

## CONCLUÍDAS (histório)

- ~~Tarefas 1-10: Fixes de testes e código~~
- ~~Plano Mestre Fases 1-8: Qualidade 100%~~

---

## PRIORIDADE — Cobertura Frontend

| # | Tarefa | Assignee | Prioridade | Status |
|---|--------|----------|------------|--------|
| C1 | Vitest coverage report (medir atual) | Kimi | ALTA | PENDENTE |
| C2 | Identificar áreas sem cobertura | Kimi | ALTA | PENDENTE |
| C3 | Escrever testes para hooks críticos | Kimi | ALTA | PENDENTE |
| C4 | Escrever testes para componentes core | Kimi/Opus | MÉDIA | PENDENTE |
| C5 | Meta: cobertura ≥80% | Todos | ALTA | PENDENTE |

## FUTURAS (pós-deploy)

| # | Tarefa | Prioridade | Descrição |
|---|--------|------------|-----------|
| F1 | React 19 immutability | Média | 322 warnings (dívida técnica planejada) |
| F2 | Teste flaky | Baixa | `test_report_calculate_next_execution_daily` |
| F3 | Backend coverage | Média | pytest-cov |
| F4 | NotificationChannel mapper | Baixa | Bug pré-existente |
| F5 | Database HA (primary-replica) | Média | Alta disponibilidade |
| F6 | CDN (S3 + CloudFront) | Baixa | Assets estáticos |

---

## REGRAS

- NÃO tocar no código da aplicação durante deploy
- NÃO subir containers antes de TODOS os scripts prontos
- NÃO rodar load test sem containers UP
- Cada fase: implementar → testar → commitar → próxima
- Comunicação via `.comms/messages/` (JSONL)
