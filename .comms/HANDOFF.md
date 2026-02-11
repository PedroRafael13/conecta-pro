# HANDOFF — Estado Atual do Projeto

**Última atualização:** 2026-02-10 por Claude Opus 4.6 (Auditor)
**Branch:** feature/openclaw-v2
**Último commit:** 899c5ed6

---

## PLANO MESTRE DE PRODUÇÃO — 100% CONCLUÍDO (2026-02-10)

Triple-verified por Claude, Kimi e Opus. Ver detalhes em:
`/opt/conecta-pro/.comms/tasks/PLANO-MESTRE-PRODUCAO.md`

### Métricas finais:
- Pytest: 6287 passed, 0 failed | ESLint: 0 warnings | TypeScript: 0 errors
- Vitest: 1985/1985 | Bandit: 0 High | Alembic: 1 head | Build: OK

---

## PRÓXIMO: PLANO DE DEPLOY PARA PRODUÇÃO

**Plano completo:** `/opt/conecta-pro/.comms/tasks/PLANO-DEPLOY-PRODUCAO.md`
**Status:** PLANEJADO — aguardando execução na próxima sessão

### Distribuição de trabalho:

| Fase | Descrição | Assignee | Deps | Status |
|------|-----------|----------|------|--------|
| 1 | Scripts deploy/rollback/health | Opus | — | PENDENTE |
| 2 | Segurança & secrets | Opus | F1 | PENDENTE |
| 3 | AlertManager & notificações | Kimi | — | PENDENTE |
| 4 | Logrotate & manutenção | Kimi | — | PENDENTE |
| 5 | Backup & DR test | Opus | F2 | PENDENTE |
| 6 | Load testing (k6) | Kimi | — | PENDENTE |
| 7 | DNS & SSL | Jordan | — | CONCLUÍDA (já live em erp.conectamais.pro) |
| 8 | Deploy staging | Todos | F1-7 | PENDENTE |
| 9 | Validação final (15 checks × 3) | Todos | F8 | PENDENTE |

### Info Produção:
- **URL:** https://erp.conectamais.pro (LIVE)
- **DNS:** Configurado
- **Google Accounts:** Configurado

### Prioridade extra: Cobertura Frontend
- Vitest coverage report
- Identificar áreas sem cobertura
- Aumentar cobertura para ≥80%

### Paralelismo:
- **Rodada 1:** Opus(F1) + Kimi(F3) — simultâneo
- **Rodada 2:** Opus(F2) + Kimi(F4+coverage frontend) — simultâneo
- **Rodada 3:** Opus(F5) + Kimi(F6) — simultâneo
- **Rodada 4:** Todos(F8) → Todos(F9)

---

## Instruções por Agente

- **Kimi:** Leia `/opt/conecta-pro/.comms/INSTRUCOES-KIMI-DEPLOY.md`
- **Opus:** Leia `/opt/conecta-pro/.comms/INSTRUCOES-OPUS-DEPLOY.md`
- **Claude:** Leia `/opt/conecta-pro/.comms/INSTRUCOES-CLAUDE-DEPLOY.md`

---

## O Que NÃO Fazer

- NÃO toque no código da aplicação (backend/frontend) — só infraestrutura
- NÃO edite `src/types/generated/` ou `src/api/**/generated/`
- NÃO suba containers antes da Fase 8
- NÃO rode load test antes dos containers estarem UP
- NÃO quebre os testes (verificar com verify-all.sh se tocar em algo)
