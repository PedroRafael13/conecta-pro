# Relatório T5 — Skill 08: CI/CD Fix
**Data:** 2026-04-01 | **Commit:** `0f934958`

---

## Resultado

| Métrica | Antes | Depois |
|---------|-------|--------|
| Score Skill 08 | 7.1/10 | **9.5/10** |
| DEPLOY_PATH correto | ❌ | ✅ |
| Branch feature/* coberta | ❌ | ✅ |
| Quality gates bloqueantes | 0/7 | **5/7** |
| Gates opcionais explícitos | 0 | 2 |
| YAML válido | ✅ | ✅ |

---

## Problema 1 — DEPLOY_PATH errado (`deploy.yml`)

| | Valor |
|-|-------|
| **Antes** | `DEPLOY_PATH: /opt/erp-conecta-mais` |
| **Depois** | `DEPLOY_PATH: /opt/conecta-pro` |

O path antigo (`/opt/erp-conecta-mais`) não existe no servidor. Todos os 3 jobs de deploy
(`validate`, `deploy-staging`, `deploy-production`) usavam `cd ${{ env.DEPLOY_PATH }}`,
o que causaria falha imediata em qualquer deploy real.

---

## Problema 2 — Branch `feature/*` não coberta (`ci.yml`)

| Trigger | Antes | Depois |
|---------|-------|--------|
| `push.branches` | `[main, master, develop]` | `[main, master, develop, feature/*]` |
| `pull_request.branches` | `[main, master]` | `[main, master, feature/*]` |

O projeto está ativamente no branch `feature/people-management-reorganization`.
Sem essa cobertura, nenhum push ou PR de feature acionava o CI.

---

## Problema 3 — 7 quality gates com `|| true` (`ci.yml`)

| # | Step | Job | Ação | Justificativa |
|---|------|-----|------|---------------|
| 1 | MyPy (type checking) | lint | `|| true` → **removido** | Type safety deve bloquear o build |
| 2 | ESLint | frontend-lint | `|| true` → **removido** | Linting deve bloquear o build |
| 3 | TypeScript check (`tsc --noEmit`) | frontend-lint | `|| true` → **removido** | Type safety deve bloquear o build |
| 4 | Bandit (security scan) | security | `|| true` → **`continue-on-error: true`** | Alta taxa de falsos positivos em scans estáticos; resultado reportado mas não bloqueia |
| 5 | Safety (vulnerabilidades) | security | `|| true` → **removido** | Dependências vulneráveis conhecidas devem bloquear |
| 6 | Vitest (testes) | frontend-test | `|| true` → **removido** | Testes com falha devem bloquear o build |
| 7 | Vitest (coverage) | frontend-test | `|| true` → **`continue-on-error: true`** | Relatório de cobertura é informacional; já capturado pelo step de testes acima |

**Nota:** Os `|| true` em `security-schedule.yml` foram mantidos — esse workflow é agendado
e coleta relatórios de segurança, não é um quality gate de CI.

---

## Arquivos Alterados

| Arquivo | Alteração |
|---------|-----------|
| `.github/workflows/deploy.yml` | DEPLOY_PATH corrigido |
| `.github/workflows/ci.yml` | branches + 7 quality gates |
| `.secrets.baseline` | atualizado automaticamente pelo hook |

---

## Verificações Realizadas

```
✅ .github/workflows/deploy.yml: YAML válido
✅ .github/workflows/ci.yml: YAML válido
✅ .github/workflows/security-schedule.yml: YAML válido
✅ .github/workflows/openclaw.yml: YAML válido
✅ DEPLOY_PATH: /opt/conecta-pro
✅ feature/* em push e pull_request triggers
✅ 0 || true críticos restantes em ci.yml
✅ Commit 0f934958 | Push OK
```

---

## Download

```bash
scp root@srv1134814.hstgr.cloud:/opt/conecta-pro/RELATORIO_T5_SKILL08_CICD_2026-04-01.md ~/Downloads/
```
