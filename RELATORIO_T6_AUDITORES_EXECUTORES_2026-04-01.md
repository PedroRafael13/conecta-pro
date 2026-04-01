# Relatório T6 — Evolução: Monitores → Auditores + Executores
**Data:** 2026-04-01
**Branch:** feature/people-management-reorganization
**Status:** 🟡 STANDBY — aguardando sinal de Jordan para ativar ciclo automático

---

## Missão
Evoluir o sistema de agentes de monitoramento passivo para **auditoria ativa de código
com autocorreção** — os agentes lêem arquivos, detectam bugs e corrigem automaticamente,
sem intervenção humana.

---

## Checklist de Execução

| Passo | Descrição | Status |
|-------|-----------|--------|
| 1 | `agents/core/code_reader.py` criado | ✅ |
| 2 | `agents/core/code_fixer.py` criado | ✅ |
| 3 | `agents/core/audit_orchestrator.py` criado | ✅ |
| 4 | `agents/core/__init__.py` atualizado | ✅ |
| 5 | Teste com 1 módulo (financeiro) | ✅ 24 bugs detectados |
| 6 | Ciclo completo — 13 módulos | ✅ 245 bugs / 208 corrigidos |
| 7 | Cron semanal | 🟡 Criado e desativado (standby) |
| 8 | Commit + push | ✅ |
| 9 | Scripts de controle (START / STOP / STATUS) | ✅ |

---

## Componentes Criados

### `agents/core/code_reader.py` (297 linhas)
Lê arquivos do backend e frontend, aplica os checklists das Skills.

**Skills implementadas:**
- **Skill 03** — Detecta `@router.post` sem `status_code=201`, verbos em paths REST
- **Skill 05** — Detecta FKs sem índice, índices duplicados (requer db_session)
- **Skill 06** — Detecta controllers sem `CurrentActiveUser` / `get_current_user`
- **Skill 09** — Detecta `<input>`, `<textarea>`, `<select>` sem `aria-label`
- **Skill 10** — Detecta CLAUDE.md desatualizado, paths `/opt/erp-conecta-mais`

### `agents/core/code_fixer.py` (357 linhas)
Aplica correções cirúrgicas e determinísticas. Princípio: só corrige o que é seguro.

**Fixes implementados:**
- `fix_post_sem_201` — insere `status_code=201` em `@router.post` sem ele
- `fix_controller_sem_auth` — adiciona `CurrentActiveUser` em controllers sem auth (imports top-level apenas)
- `fix_aria_label` — infere label de `placeholder/name/type` e insere `aria-label`
- `fix_path_errado` — substitui `/opt/erp-conecta-mais` → `/opt/conecta-pro`

**Segurança implementada:**
- Hot copy via `docker cp` para o container
- Reload via `kill -HUP 1` (sem rebuild)
- Inserção de imports apenas no nível top-level (não dentro de `try/except`)

### `agents/core/audit_orchestrator.py` (257 linhas)
Orquestra o ciclo completo: lê → detecta → corrige → commita → Telegram.

**Cobertura:** 13 módulos × 4 skills automáticas

---

## Resultado do 1º Ciclo (2026-04-01 03:39)

| Métrica | Valor |
|---------|-------|
| Duração | 9 segundos |
| Módulos auditados | 11 / 13 (2 sem arquivos) |
| Arquivos analisados | ~1.223 |
| **Bugs encontrados** | **245** |
| **Corrigidos automaticamente** | **208 (84,9%)** |
| Pendentes (manuais) | 37 |

### Breakdown por Tipo de Bug

| Skill | Tipo | Ocorrências | Corrigidos |
|-------|------|-------------|------------|
| 03 | `post_sem_201` — POST sem status 201 | 113 | 113 ✅ |
| 03 | `verbo_em_path` — verbo no path REST | 14 | 0 (manual) |
| 06 | `controller_sem_auth` — sem JWT | 1 | 1 ✅ |
| 09 | `input_sem_aria_label` — input sem label | 117 | 94 ✅ |

### Breakdown por Módulo

| Módulo | Arquivos | Bugs | Corrigidos | Pendentes |
|--------|----------|------|------------|-----------|
| financeiro | 214 | 59 | 48 | 11 |
| operacional | 235 | 49 | 46 | 3 |
| ged | 73 | 33 | 22 | 11 |
| licitacoes | 134 | 27 | 24 | 3 |
| departamento_pessoal | 252 | 26 | 25 | 1 |
| fiscal_contabil | 171 | 17 | 17 | 0 |
| crm | 55 | 16 | 12 | 4 |
| equipamentos | 39 | 11 | 7 | 4 |
| portais | 31 | 5 | 5 | 0 |
| marketing | 4 | 1 | 1 | 0 |
| administrativo | 15 | 1 | 1 | 0 |
| recursos_humanos | — | 0 | 0 | — |
| saude_ocupacional | — | 0 | 0 | — |

---

## Mecanismo de Ativação Controlada

### Sistema em STANDBY
O cron automático está **desativado**. Nenhum ciclo roda sem comando explícito.

```bash
# Ver status atual
bash /opt/conecta-pro/agents/STATUS_AUDITORIA.sh

# Ativar sistema (quando Jordan estiver pronto)
bash /opt/conecta-pro/agents/START_AUDITORIA.sh

# Pausar a qualquer momento
bash /opt/conecta-pro/agents/STOP_AUDITORIA.sh
```

### O que START_AUDITORIA.sh faz
1. Ativa cron semanal (domingo 3h)
2. Garante diretórios de logs/relatórios
3. Roda o 1º ciclo imediatamente
4. Notifica via Telegram `@conecta_pro_monitor_bot`

---

## Skills com Auto-fix

| Skill | Descrição | Auto-fix | Status |
|-------|-----------|----------|--------|
| 03 | API RESTful (POST→201) | ✅ | Ativo |
| 06 | Auth (controllers sem JWT) | ✅ | Ativo |
| 09 | UX (inputs sem aria-label) | ✅ | Ativo |
| 10 | Docs (paths errados) | ✅ | Ativo |
| 05 | Banco (FKs, índices) | 🔄 | Próxima sprint |
| 04 | Testes (cobertura) | 🔄 | Próxima sprint |
| 07 | Docker (Dockerfile) | 🔄 | Próxima sprint |
| 08 | CI/CD (pipeline) | 🔄 | Próxima sprint |

---

## Pendências Manuais (37 bugs não autocorrigíveis)

| Tipo | Qtd | Motivo |
|------|-----|--------|
| `verbo_em_path` | 14 | Requer renomear rota + atualizar frontend |
| `input_sem_aria_label` sem atributo inferível | 23 | Label não pode ser inferida automaticamente |

---

## Commits Gerados

```
486e048f docs(skill06): relatório final — 259 controllers com JWT, 0 sem auth
01f220ba fix(frontend/skill09): reverte injeção incorreta de aria-label em onChange handlers
ea603d0a feat(agents/audit): sistema de auditoria em STANDBY
```

---

## Próxima Ação
**Aguardando sinal de Jordan.**
Quando os trabalhos T1-T5 estiverem concluídos:
```bash
bash /opt/conecta-pro/agents/START_AUDITORIA.sh
```
