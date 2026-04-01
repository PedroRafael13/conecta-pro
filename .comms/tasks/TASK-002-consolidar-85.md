# TASK-002: Consolidar 85% — Opção B

> Prioridade: ALTA
> Atribuído a: Kimi K2.5
> Criado por: Claude Opus 4.6 — 2026-02-09
> Auditor: Claude (monitorando em tempo real)
> Status: COMPLETE_COMMITED

## Objetivo

Consolidar o score 85/100 com qualidade real. NÃO forçar 100%.

## Fase 1: Limpar 15 itens de código morto

### Encontrar os itens
```bash
cd /opt/conecta-pro/backend
# Variáveis não usadas
ruff check . --select F841 --output-format text 2>/dev/null | head -30
# Imports não usados
ruff check . --select F401 --output-format text 2>/dev/null | head -30
# Nomes indefinidos
ruff check . --select F821 --output-format text 2>/dev/null | head -30
```

### Regras
1. **NÃO deletar arquivo inteiro** — só a variável/import morto
2. **Verificar ANTES de remover** que não é usado em outro lugar: `grep -rn "nome_var" /opt/conecta-pro/backend/`
3. **Testar DEPOIS de cada mudança**: `docker exec conecta-pro-backend python -c "import <modulo>"` para garantir que não quebrou
4. **Copiar para container** após editar: `docker cp <arquivo> conecta-pro-backend:<path> && docker exec -u root conecta-pro-backend chmod 644 <path>`

## Fase 2: Documentar módulos API-only

Os 15 módulos backend SEM frontend são API-only por design. Criar um arquivo simples:

```bash
# Criar /opt/conecta-pro/docs/MODULES_API_ONLY.md
```

Conteúdo: lista dos 15 módulos, breve descrição, e justificativa de por que não têm frontend (ex: "ai — consumido via API por outros módulos", "monitoring — acesso via Grafana/Prometheus").

### Módulos API-only (sem frontend)
- ai, audit, clients, core, document_kits, fase5, ged, hr, integrations, mobile, monitoring, notifications, retention, search, services

## Fase 3: Verificação Final

1. Rodar TODOS os testes: `docker exec conecta-pro-backend python -m pytest /app/tests/ -v --no-cov --tb=short`
2. Confirmar 0 failures
3. Rodar linting: `cd /opt/conecta-pro/backend && ruff check . --output-format text 2>/dev/null | wc -l`
4. Reportar resultado via `.comms/messages/kimi-out.jsonl`

## Entregáveis

1. 15 itens de código morto → 0
2. MODULES_API_ONLY.md criado
3. 0 failures nos testes
4. Linting reduzido (comparar antes/depois)
5. Mensagem com relatório final

## O QUE NÃO FAZER

- NÃO criar frontends para os 15 módulos
- NÃO criar testes novos (já temos 44/44 PASS)
- NÃO refatorar código que funciona
- NÃO editar conftest.py nem notification models (Claude já corrigiu)
- NÃO chamar configure_mappers() em nada
- NÃO importar `from main import app` no topo de arquivos
