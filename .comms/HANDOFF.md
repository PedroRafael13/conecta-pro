# HANDOFF — Estado Atual do Projeto

**Última atualização:** 2026-02-09 21:30 UTC por Claude Opus 4.6
**Branch:** feature/openclaw-v2
**Último commit:** 1cacb1e5

---

## IMPORTANTE: NOVO FRAMEWORK OPERACIONAL

O Claude criou um framework operacional completo para você. **LEIA ANTES DE FAZER QUALQUER COISA:**

1. `/opt/conecta-pro/.kimi/SESSION-START.md` — checklist de início (6 passos)
2. `/opt/conecta-pro/.kimi/ENVIRONMENT.md` — ambiente, paths, comandos exatos
3. `/opt/conecta-pro/.kimi/REGRAS-OPERACIONAIS.md` — 13 regras obrigatórias
4. `/opt/conecta-pro/.kimi/ERROS-PASSADOS.md` — 12 erros que você cometeu antes
5. `/opt/conecta-pro/.kimi/commands-reference.json` — comandos verificados
6. `/opt/conecta-pro/.comms/BASELINE.json` — números reais do projeto

**Skill nova:** `/verify` → roda `/opt/conecta-pro/scripts/verify-all.sh`

---

## Métricas Reais do Projeto (verificadas por Claude)

| Métrica | Valor | Status |
|---------|-------|--------|
| Ruff | 0 erros | OK |
| Pytest collection | 6468 coletados, 0 erros | OK |
| Pytest run | 4689 passed, 1307 failed, 457 errors | 72.5% pass |
| Alembic | 1 head | OK |
| Bandit HIGH | 135 | PRECISA ATENÇÃO |
| TypeScript | 0 erros | OK |
| ESLint | 29 errors, 510 warnings | PRECISA FIX |
| Orphaned | 31 arquivos em _orphaned/ | NÃO MOVER MAIS |

---

## Causa-Raiz dos 1307 Failures (análise Claude)

| Prioridade | Problema | Impacto | Fix |
|------------|----------|---------|-----|
| **P0** | PushCampaign/PushNotification mapper collision | 1068 failures (82%) | Resolver conflito de modelo/tabela |
| **P1** | Table `push_notifications` metadata duplicate | 94 failures | `extend_existing=True` ou deduplicar |
| **P2** | Enums EN vs PT (ACTIVE→ATIVO, etc.) | 77+ failures | Corrigir nos testes |
| **P3** | Fixture `async_client` não encontrada | 27 failures | Adicionar ao conftest |
| **P4** | Pydantic schemas desatualizados | 46+ failures | Atualizar fields nos testes |

**Resolver só P0 leva de 72.5% → ~89% pass rate.**

---

## O Que NÃO Fazer

- NÃO mover testes para `_orphaned/`
- NÃO deletar conftest.py ou configs
- NÃO usar `next lint` (usar `npx eslint .`)
- NÃO rodar pytest sem ativar venv
- NÃO reportar números sem rodar `verify-all.sh`

---

## Sessão Anterior (resumo)

- Fases 1,2,4,6,7 do plano mestre: COMPLETAS
- Collection errors: 159 → 0
- Alembic: 12 → 1 head
- Console.log: 38 → 0
- ESLint: Claude corrigiu 383→0 (depois Kimi adicionou 29 em docs/e2e)
- 12 commits no branch
