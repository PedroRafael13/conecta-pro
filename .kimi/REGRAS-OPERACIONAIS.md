# Regras Operacionais — Kimi K2.5 no Conecta PRO

**Versão:** 1.0.0 — 2026-02-09
**Autor:** Claude Opus 4.6 (auditor e arquiteto)
**Status:** VIGENTE — cumprir 100%

---

## REGRA 1: NUNCA MENTIR SOBRE NÚMEROS

- **PROIBIDO** dizer "0 erros" sem ter rodado o comando e verificado o output
- **PROIBIDO** dizer "todos os testes passam" baseado em amostra parcial
- **OBRIGATÓRIO** qualificar scope: "0 erros NO MÓDULO X" ou "376 testes passam DOS 6468 COLETADOS"
- **OBRIGATÓRIO** incluir o comando exato que rodou e a última linha do output

**Exemplo ERRADO:**
> "Ruff 0 erros. ESLint 0 erros. Testes estáveis."

**Exemplo CORRETO:**
> "Ruff: `ruff check .` → 'All checks passed!' (0 erros)
> ESLint: `npx eslint . --no-error-on-unmatched-pattern` → '539 problems (29 errors, 510 warnings)'
> Pytest: `python -m pytest --tb=no -q` → '4689 passed, 1307 failed, 457 errors' (72.5% pass rate)"

---

## REGRA 2: SEMPRE ATIVAR VENV

Antes de QUALQUER comando Python:
```bash
cd /opt/conecta-pro/backend && source venv/bin/activate
```

Sem venv, faltam dependências (defusedxml, faker, etc.) e os resultados são INCORRETOS.

---

## REGRA 3: NUNCA MOVER TESTES PARA _ORPHANED

- **PROIBIDO** mover testes que falham para `_orphaned/` como "solução"
- Se um teste falha, as opções são:
  1. **CORRIGIR** o teste (preferível)
  2. **Marcar** com `@pytest.mark.xfail(reason="motivo específico")`
  3. **Marcar** com `@pytest.mark.skip(reason="motivo específico")`
  4. **Reportar** ao Claude que não conseguiu resolver e pedir orientação
- `_orphaned/` só pode receber arquivos com APROVAÇÃO EXPLÍCITA do Claude

---

## REGRA 4: NUNCA DELETAR ARQUIVOS DE CONFIGURAÇÃO

Estes arquivos são INTOCÁVEIS sem aprovação:
- `pytest.ini`
- `conftest.py` (qualquer um)
- `pyproject.toml`
- `ruff.toml`
- `eslint.config.mjs`
- `tsconfig.json`
- `next.config.ts`
- `orval.config.ts`
- `.env*`
- `docker-compose*.yml`
- `alembic.ini`
- `alembic/env.py`

Se precisar modificar → PERGUNTE ao Claude ANTES.

---

## REGRA 5: VERIFICAR ANTES E DEPOIS

### Antes de começar qualquer tarefa:
```bash
/opt/conecta-pro/scripts/verify-all.sh 2>&1 | tee /tmp/verify-ANTES.txt
```

### Depois de concluir qualquer tarefa:
```bash
/opt/conecta-pro/scripts/verify-all.sh 2>&1 | tee /tmp/verify-DEPOIS.txt
```

### Comparar:
```bash
diff /tmp/verify-ANTES.txt /tmp/verify-DEPOIS.txt
```

Se QUALQUER métrica piorou → REVERTER mudanças e investigar.

---

## REGRA 6: ESLINT = `npx eslint .`, NUNCA `next lint`

- `next lint` só checa `src/` e ignora `docs/`, `e2e/`, etc.
- `npx eslint . --no-error-on-unmatched-pattern` checa TUDO
- Sempre usar o segundo. O primeiro dá falsos "0 erros".

---

## REGRA 7: REPORTAR PROGRESSO HONESTAMENTE

Formato obrigatório para reports ao Claude:

```
TASK: [nome da tarefa]
STATUS: [em andamento | concluído | bloqueado]

MÉTRICAS ANTES:
  Ruff: X erros (comando: ...)
  Pytest: X passed, Y failed (comando: ...)
  ESLint: X errors (comando: ...)

MÉTRICAS DEPOIS:
  Ruff: X erros (comando: ...)
  Pytest: X passed, Y failed (comando: ...)
  ESLint: X errors (comando: ...)

DELTA:
  Ruff: -5 erros (melhorou)
  Pytest: +20 passed (melhorou)
  ESLint: +2 errors (PIOROU - investigar)

ARQUIVOS MODIFICADOS:
  [listar todos]

ARQUIVOS DELETADOS/MOVIDOS:
  [listar todos — se nenhum, dizer "nenhum"]

PROBLEMAS ENCONTRADOS:
  [descrever honestamente]

PRÓXIMOS PASSOS:
  [o que falta fazer]
```

---

## REGRA 8: NUNCA EDITAR ARQUIVOS GERADOS

Estes diretórios são GERADOS AUTOMATICAMENTE:
- `frontend/src/api/generated/`
- `frontend/src/types/generated/`
- `frontend/.next/`
- `frontend/node_modules/`
- `backend/venv/`
- `backend/alembic/versions/` (exceto merge migrations aprovadas)

Se precisar mudar algo gerado → regenerar com o comando correto, não editar manualmente.

---

## REGRA 9: COMMITS EM PORTUGUÊS COM ESCOPO

Formato:
```
tipo(escopo): descrição concisa

Corpo detalhado se necessário.
Incluir números REAIS de métricas.
```

Tipos: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

**Exemplo BOM:**
```
fix(tests): corrige 15 testes de government_integrations

- Ajusta imports para usar venv paths
- Corrige enum português (aberta vs active)
- Pytest: 4689→4704 passed (+15)
```

**Exemplo RUIM:**
```
fix: corrige testes
```

---

## REGRA 10: SE PIOROU, REVERTE

Se `verify-all.sh` mostra regressão:

1. `git stash` ou `git checkout -- .` para reverter
2. Reportar ao Claude: "Tentei X, causou regressão Y, reverti"
3. Pedir orientação antes de tentar novamente

**NUNCA** continuar trabalhando em cima de uma regressão.

---

## REGRA 11: SCOPE LIMITADO

Cada tarefa tem um escopo definido. NÃO fazer:
- Refatorações "de bônus" não solicitadas
- Renames "para ficar mais bonito"
- Reorganizações de diretórios sem aprovação
- "Melhorias" em código que não faz parte da tarefa

Se encontrar algo que precisa ser melhorado fora do escopo → anotar no report, NÃO corrigir.

---

## REGRA 12: COMUNICAÇÃO INTER-IA

### Para perguntas ao Claude:
```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","from":"kimi","to":"claude","type":"question","id":"kimi-'$(date +%s)'","reply_to":null,"priority":"high","subject":"ASSUNTO","content":"PERGUNTA DETALHADA"}' >> /opt/conecta-pro/.comms/messages/kimi-out.jsonl
```

### Para reports de progresso:
```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","from":"kimi","to":"claude","type":"status","id":"kimi-'$(date +%s)'","reply_to":null,"priority":"normal","subject":"Progress TASK-X","content":"MÉTRICAS ANTES/DEPOIS"}' >> /opt/conecta-pro/.comms/messages/kimi-out.jsonl
```

### Reportar A CADA commit, não só no final.

---

## REGRA 13: IMPACTO CRUZADO

Se você modificou um **model** SQLAlchemy:
```bash
grep -r "NomeDoModel" /opt/conecta-pro/backend/ --include="*.py" -l
```
Verificar TODOS os arquivos que usam esse model.

Se você renomeou algo:
```bash
grep -r "nome_antigo" /opt/conecta-pro/ --include="*.py" --include="*.ts" --include="*.tsx" -l
```
Verificar TODOS os arquivos que referenciam o nome antigo.

Se você modificou um import:
```bash
cd /opt/conecta-pro/backend && source venv/bin/activate && python -m pytest --collect-only -q 2>&1 | grep ERROR
```
Verificar que NENHUM teste quebrou por import.

---

## RESUMO: CHECKLIST PRÉ-REPORT

Antes de dizer "tarefa concluída":

- [ ] Rodei `verify-all.sh` ANTES e DEPOIS?
- [ ] Comparei métricas — nenhuma piorou?
- [ ] Ativei venv antes de rodar pytest/ruff?
- [ ] Usei `npx eslint .` e NÃO `next lint`?
- [ ] Reportei números DO PROJETO INTEIRO, não só do que toquei?
- [ ] NÃO movi nada para `_orphaned/`?
- [ ] NÃO deletei nenhum conftest.py ou config?
- [ ] NÃO editei arquivos em `generated/`?
- [ ] Commit com tipo(escopo) e métricas reais?
- [ ] Reportei ao Claude via `.comms/messages/kimi-out.jsonl`?

**Se qualquer item é NÃO → NÃO reporte conclusão.**
