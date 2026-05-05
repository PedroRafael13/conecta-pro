# T4-C CPRO12 — CLAUDE.md atualizado: regra hot-copy
**Data:** 2026-05-05
**Executor:** Claude Sonnet 4.6 [session: t4] [module: operacional]
**Tipo:** DOCS — zero alteração de código ou containers

---

## Investigação pré-edição

**Seção encontrada sobre deploy:** SIM — `## Comandos Essenciais` (linha 74)
- Linha 86-88: `docker cp` + `kill -HUP 1` (apenas container backend)
- Linha 113: "Backend changes: hot copy via docker cp, nunca rebuild completo"

**Seção sobre pyc existia:** NÃO — zero referências a `pyc`, `__pycache__` ou cache

**Script sync_celery_workers.sh:** CONFIRMADO em `scripts/deploy/sync_celery_workers.sh`
- Cobre 6 containers (faltam nfse e sefaz — nota para Jordan)
- Já inclui limpeza de pyc antes do cp
- Já inclui `kill -HUP 1` ao final

**Referências a celery-beat/celery-batch antes da edição:** ZERO

---

## Hipóteses

| H | Validada? | Detalhe |
|---|-----------|---------|
| H1 — CLAUDE.md tem seção deploy/hot-copy | ✅ SIM | Linha 86-88 em "Comandos Essenciais" — mas cobria apenas backend |
| H2 — Sem regra sobre containers Celery | ✅ CONFIRMADO | Zero ocorrências de celery-beat/celery-batch no arquivo original |
| H3 — Script sync_celery_workers.sh existe | ✅ CONFIRMADO | scripts/deploy/sync_celery_workers.sh, 603 bytes, executável |
| H4 — Sem regra pyc antes | ✅ CONFIRMADO | Zero ocorrências de pyc/__pycache__/cache no arquivo original |
| H5 — CLAUDE.md válido após edição | ✅ | 240 → 325 linhas; head/tail intactos; estrutura preservada |

---

## Regra adicionada

**Posição:** entre `## Comandos Essenciais` (linha 99) e `## Zonas Proibidas` (linha 185)
**Título:** `## REGRA CRÍTICA — HOT-COPY PARA TODOS OS CONTAINERS CELERY`
**Linhas adicionadas:** 85 (CLAUDE.md: 240 → 325 linhas)

### Conteúdo da regra:

1. **Por que existe** — celery-beat ficou 46 dias em loop (2026-03-20 a 2026-05-04) porque punch_controller.py foi corrigido no disco mas nunca copiado para os workers

2. **Lista dos 8 containers** com indicação de quando incluir cada um

3. **Aviso de hash no nome** — alguns containers têm prefixo hash; como resolver com docker ps

4. **Fluxo obrigatório** — Opção 1 (script padrão) e Opção 2 (manual com pyc limpeza)

5. **Regra pyc stale** — documentada com sintoma e causa (descoberto T4 CPRO12)

6. **Regra SIGHUP** — documentado como usar kill -HUP 1 e o fallback python para workers sem binary kill

7. **Regra celery_app.py** — sync obrigatório quando include[] muda, com comando para todos os workers

---

## Nota sobre o script (não corrigida — zero código)

`sync_celery_workers.sh` lista 6 containers mas o inventário (§66) identificou **8 containers Celery**
(faltam `celery-nfse` e `celery-sefaz`). O script não foi modificado (INV-4 — zero código).
Jordan decide se atualiza o script para incluir os 2 containers faltantes.

---

## CLAUDE.md antes vs depois

| Métrica | Antes | Depois |
|---------|-------|--------|
| Linhas | 240 | 325 |
| Referências a celery workers | 0 | 12+ |
| Referências a pyc/cache | 0 | 4 |
| Regra sobre hot-copy completo | NÃO | SIM |
| Lista de containers | NÃO | SIM (8 containers) |

---

## Commits

| Commit | Tipo | Hash |
|--------|------|------|
| docs: CLAUDE.md + §70 CONTRACTS_GEDEON | docs | `7adee072` |

---

## Self-check (8 itens)

| Item | Status |
|------|--------|
| STEP 0 — contrato lido, §66 confirmado, §13.1 citado | ✅ |
| STEP 1 — CLAUDE.md lido inteiro antes de editar (240 linhas) | ✅ |
| STEP 2 — backup criado (CLAUDE.md.bak.t4cpro12c) | ✅ |
| STEP 3 — regra adicionada (não substituída, não removida) | ✅ |
| STEP 4 — CLAUDE.md válido após edição (325 linhas, estrutura intacta) | ✅ |
| STEP 5 — §70 adicionado ao CONTRACTS_GEDEON.md | ✅ |
| STEP 6 — commit único (docs) + push + backup removido | ✅ |
| INV-2 — nenhuma seção existente removida | ✅ |

---

**Cenário A** — Regra adicionada, commit OK.

**T4-C CPRO12 OK — CLAUDE.md tem regra permanente de hot-copy para todos os 8 containers Celery.
A lição dos 46 dias de celery-beat parado e do pyc stale agora está documentada como invariante.**

[session: t4] [module: operacional]
