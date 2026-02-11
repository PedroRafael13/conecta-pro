# BACKLOG — Tarefas (v7 — PÓS-DEPLOY)

**Atualizado:** 2026-02-11 por Claude Opus 4.6 (Auditor)

---

## Estado Atual: DEPLOY PRODUÇÃO 100% CONCLUÍDO

### Validação final (F9):
- **Triple-verified:** 3 terminais × 15 checks = 45/45 PASS
- **URL:** https://erp.conectamais.pro (LIVE)
- **20 containers** rodando, SSL ativo, backup automático

### Baseline de código (NÃO regredir):
- **Pytest:** 6287 passed, 0 failed
- **ESLint:** 0 errors, 0 warnings
- **TypeScript:** 0 errors
- **Vitest:** 1985/1985 passed
- **Bandit:** 0 High
- **Alembic:** 1 head
- **Next.js build:** OK

---

## CONCLUÍDAS — Deploy Produção (2026-02-11)

| # | Fase | Assignee | Status |
|---|------|----------|--------|
| ~~D1~~ | ~~Scripts deploy/rollback/health~~ | Opus | ✅ |
| ~~D2~~ | ~~Segurança & secrets~~ | Opus | ✅ |
| ~~D3~~ | ~~AlertManager & notificações~~ | Kimi | ✅ |
| ~~D4~~ | ~~Logrotate & Loki retention~~ | Kimi | ✅ |
| ~~D5~~ | ~~Backup & DR test~~ | Opus | ✅ |
| ~~D6~~ | ~~Load testing (k6)~~ | Kimi | ✅ |
| ~~D7~~ | ~~DNS & SSL~~ | Jordan | ✅ |
| ~~D8~~ | ~~Deploy staging~~ | Todos | ✅ |
| ~~D9~~ | ~~Validação final (15×3)~~ | Todos | ✅ 45/45 |

## CONCLUÍDAS — Cobertura Frontend

| # | Tarefa | Assignee | Status |
|---|--------|----------|--------|
| ~~C1~~ | ~~Vitest coverage report~~ | Kimi | ✅ 84.46% stmts |
| ~~C2~~ | ~~Identificar áreas sem cobertura~~ | Kimi | ✅ Relatório criado |
| ~~C3~~ | ~~Testes para hooks críticos~~ | Kimi | ✅ +17 testes |
| ~~C4~~ | ~~Testes para componentes core~~ | Kimi | ✅ dropdown-menu |
| C5 | Meta: cobertura branches ≥80% | — | ⚠️ 69.33% (stmts 84.46%) |

---

## PENDÊNCIAS PÓS-DEPLOY (não bloqueantes)

| # | Tarefa | Prioridade | Descrição |
|---|--------|------------|-----------|
| P1 | Discord webhook | ALTA | Configurar `DISCORD_WEBHOOK=<url>` no `.env` para alertas reais |
| P2 | Certbot dry-run | MÉDIA | Matar processo travado (`kill 62575`) e retestar `certbot renew --dry-run` |
| P3 | Healthcheck celery-beat | BAIXA | Ajustar grep pattern no docker-compose.celery.yml |
| P4 | Cobertura branches 80% | MÉDIA | Frontend branches 69.33%, meta 80%. Requer ~4-6h de testes |

---

## FUTURAS (roadmap)

| # | Tarefa | Prioridade | Descrição |
|---|--------|------------|-----------|
| F1 | React 19 immutability | Média | 322 warnings (dívida técnica planejada) |
| F2 | Teste flaky | Baixa | `test_report_calculate_next_execution_daily` |
| F3 | Backend coverage | Média | pytest-cov |
| F4 | NotificationChannel mapper | Baixa | Bug pré-existente |
| F5 | Database HA (primary-replica) | Média | Alta disponibilidade |
| F6 | CDN (S3 + CloudFront) | Baixa | Assets estáticos |
| F7 | Load test completo | Média | Rodar cenários login + api_reads + mixed (não só smoke) |
| F8 | Flower inspect fix | Baixa | Flower não consegue inspecionar todos os workers |
| F9 | Backup offsite S3 | Média | Configurar `S3_BACKUP_BUCKET` no `.env` |

---

## REGRAS

- Baseline é sagrado — NÃO regredir métricas
- Verificar com `verify-all.sh` antes e depois de mudanças
- Comunicação via `.comms/messages/` (JSONL)
- Deploy via `scripts/deploy.sh`, rollback via `scripts/rollback.sh`
