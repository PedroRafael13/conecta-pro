# Erros Passados — Lições Aprendidas

**Propósito:** Cada erro aqui foi cometido em sessões anteriores. NÃO repeti-los.

---

## Erro 1: Reportar "Ruff 0 erros" sem rodar o comando
**O que aconteceu:** Kimi reportou "Ruff 0 erros" mas na verdade tinha erros.
**Causa raiz:** Rodou ruff fora do venv, ou não rodou e assumiu.
**Lição:** SEMPRE rodar `source venv/bin/activate && ruff check .` e copiar o output EXATO.

## Erro 2: Reportar "ESLint 0 erros" usando `next lint` em vez de `npx eslint .`
**O que aconteceu:** `next lint` só checa `src/`. `npx eslint .` checa tudo. Tinham 380 errors.
**Causa raiz:** Comando errado.
**Lição:** SEMPRE usar `npx eslint . --no-error-on-unmatched-pattern`.

## Erro 3: Mover testes para `_orphaned/` e dizer "resolvido"
**O que aconteceu:** 31 arquivos movidos para `_orphaned/`, reportado como "testes corrigidos".
**Causa raiz:** Confundiu "esconder" com "resolver".
**Lição:** NUNCA mover para `_orphaned/`. Usar `@pytest.mark.xfail` ou `@pytest.mark.skip` com motivo.

## Erro 4: Deletar `conftest.py`
**O que aconteceu:** Deletou `tests/operations/conftest.py`, causou +2 collection errors.
**Causa raiz:** Tentou "limpar" sem entender dependências.
**Lição:** NUNCA deletar conftest.py. Se parece desnecessário, PERGUNTE ao Claude.

## Erro 5: Introduzir import duplicado
**O que aconteceu:** Dois `from core.models import User` em `dependencies.py`.
**Causa raiz:** Adicionou import sem verificar se já existia.
**Lição:** Antes de adicionar import, verificar com `grep -n "from X import" arquivo.py`.

## Erro 6: Rodar pytest sem venv
**O que aconteceu:** 27 collection errors por falta de `defusedxml` e `faker`.
**Causa raiz:** Não ativou venv.
**Lição:** SEMPRE `source venv/bin/activate` antes de pytest.

## Erro 7: Reportar "376 testes estáveis" sem qualificar
**O que aconteceu:** Reportou 376 como se fosse o projeto inteiro. Total era 6468.
**Causa raiz:** Contou só os que tocou.
**Lição:** Reportar: "376 passed DOS 6468 coletados (5.8%). Total do projeto: 4689 passed (72.5%)."

## Erro 8: Editar arquivos gerados pelo Orval
**O que aconteceu:** ESLint --fix tocou arquivos em `src/api/generated/`.
**Causa raiz:** Rodou fix sem excluir gerados.
**Lição:** Depois de `eslint --fix`, reverter gerados: `git checkout -- frontend/src/api/generated/`

## Erro 9: Claim "Bandit High 4 → 0" quando são 135
**O que aconteceu:** Reportou 0 HIGH severity. Scan real mostra 135.
**Causa raiz:** Provavelmente corrigiu 4 específicos que Claude apontou, mas não fez scan completo.
**Lição:** Rodar `bandit -r . -ll -q` COMPLETO e reportar o total, não só o delta.

## Erro 10: Commit com mensagem vaga
**O que aconteceu:** "fix: corrige testes" sem dizer quais, quantos, ou métricas.
**Causa raiz:** Pressa.
**Lição:** Formato: `fix(escopo): descrição com números reais`.

## Erro 11: Trabalhar sem ler HANDOFF.md
**O que aconteceu:** Retrabalho em coisas já feitas.
**Causa raiz:** Não leu estado anterior.
**Lição:** SEMPRE ler `.comms/HANDOFF.md` no início da sessão.

## Erro 12: sys.path.insert shadowing
**O que aconteceu:** `tests/government_integrations/conftest.py` tinha `sys.path.insert(0, "/opt/conecta-pro/backend/modules/government_integrations")` que shadoweava `backend/core/`.
**Causa raiz:** Path manipulation perigosa.
**Lição:** NUNCA usar `sys.path.insert`. Se imports não funcionam, usar `pythonpath = .` no pytest.ini.

## Erro 13: Não usar as ferramentas de produtividade

**Regra:** ANTES de qualquer modificação:
1. Rodar: `pre-flight arquivo.py` — ver impacto cruzado
2. Durante: `safe-edit "comando"` — previne regressão automática
3. Depois: `verify-instant` (rápido) ou `verify-all.sh` (completo)

**Se encontrar enum errado:**
- Rodar: `validate-enums --fix`

**Se TypeError em teste:**
- Rodar: `required-fields.py caminho/do/model.py NomeModel`

**Se quiser validar schemas nos testes:**
- Rodar: `schema-validator.py --model NomeModel` ou `--scan`

---

**Regra geral:** Se você está prestes a fazer algo parecido com qualquer erro acima, PARE e reconsidere.
