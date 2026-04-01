# Skill: /verify — Verificação Completa do Projeto

## Descrição
Executa verificação completa de todas as métricas do projeto e compara com o baseline.
**OBRIGATÓRIO** rodar antes e depois de qualquer tarefa.

## Quando Usar
- ANTES de começar qualquer tarefa (capturar estado "antes")
- DEPOIS de concluir qualquer tarefa (capturar estado "depois")
- ANTES de reportar conclusão ao Claude
- Quando Claude solicitar verificação

## Execução

### Verificação rápida (sem test run):
```bash
/opt/conecta-pro/scripts/verify-all.sh
```

### Verificação completa (com test run ~15min):
```bash
FULL_TEST=true /opt/conecta-pro/scripts/verify-all.sh
```

## Output
- Terminal: relatório legível com cores e status
- Arquivo: `/opt/conecta-pro/.comms/verification-report.json` (machine-readable)
- Comparação automática com `/opt/conecta-pro/.comms/BASELINE.json`

## Interpretação

### Exit code
- `0` = todas as verificações passaram, sem regressões
- `1` = alguma verificação falhou ou regressão detectada

### Regressões
Se o script detectar que QUALQUER métrica piorou comparado ao baseline:
1. **PARE** o trabalho atual
2. **REVERTA** as mudanças: `git stash`
3. **INVESTIGUE** a causa da regressão
4. **REPORTE** ao Claude via `.comms/messages/kimi-out.jsonl`

## Métricas Verificadas
1. Ambiente (venv, deps)
2. Git status
3. Ruff (Python linting)
4. Pytest collection
5. Pytest run
6. Alembic heads
7. Bandit (security)
8. TypeScript
9. ESLint

## Regra de Ouro
**NUNCA diga "tarefa concluída" se `verify-all.sh` retorna exit code 1.**
