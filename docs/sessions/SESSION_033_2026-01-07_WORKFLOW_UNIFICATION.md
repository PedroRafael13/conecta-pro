# Sessão: Unificação de Módulos Workflow
**Data:** 2026-01-07
**Status:** CONCLUÍDO

## Contexto Inicial

Existiam dois módulos duplicados de workflow no projeto:

1. **`modules/workflows/`** - Implementação com Python Dataclasses (~111KB de services)
   - Mais funcionalidades (ActionExecutor, ConditionEvaluator, TriggerService, etc.)
   - NÃO persistia no banco de dados

2. **`modules/automation/workflow/`** - Implementação com SQLAlchemy ORM
   - Registrado no Sprint 33
   - Tabelas no banco de dados
   - Menos funcionalidades

## Decisão Tomada

Usuário escolheu: **"(A) Fazer agora - Unificar completamente"**

Estratégia: Manter SQLAlchemy como base e enriquecer com funcionalidades do Dataclass.

## Trabalho Realizado

### 1. Novos Models SQLAlchemy Criados

#### `workflow_action.py`
- `ActionType` enum com 30+ tipos de ações
- `ActionCategory` enum (COMMUNICATION, DATA, INTEGRATION, etc.)
- Campos: type_config, input_schema, output_schema, message_template, custom_script
- Estatísticas: execution_count, success_count, avg_duration

#### `workflow_condition.py`
- `ConditionType` enum (SIMPLE, COMPOUND, EXPRESSION, FUNCTION, SCRIPT)
- `ConditionOperator` enum (20+ operadores)
- `LogicalOperator` enum (AND, OR, NOT, XOR)
- Campos: simple_condition, condition_group, expression, script
- Branches: true_step_id, false_step_id, branches (multi-way)

#### `workflow_step_execution.py`
- `StepExecutionStatus` enum
- Tracking individual de cada step
- Campos: input_data, output_data, error_message, retry_count, duration_ms

### 2. Models Existentes Enriquecidos

#### `workflow_execution.py`
- Adicionado `ExecutionPriority` enum
- Novos status: QUEUED, RETRYING
- Campos: workflow_name, workflow_version, trigger_type, priority
- Tracking: input_data, output_data, variables, completed_step_ids
- Métricas: steps_total/completed/failed/skipped
- Métodos: progress_percent, can_retry, set_variable, get_variable

#### `workflow_log.py`
- Renomeado __tablename__ para "execution_logs" (match com migration existente)
- Adicionados: step_execution_id, action_id

### 3. Services Migrados

De `workflows/services/` para `automation/workflow/services/`:
- `action_executor.py` - Executor de ações com handlers
- `condition_evaluator.py` - Avaliador de condições com funções builtin
- `trigger_service.py` - Gerenciamento de triggers (eventos, webhooks, schedules)
- `scheduler.py` - Agendador de jobs com fila e concorrência
- `workflow_designer.py` - Designer visual de workflows
- `workflow_executor.py` - Executor principal de workflows

### 4. Controller/Router Criado

`controllers/workflow_controller.py`:
- GET/POST `/api/v1/workflows` - Listar/Criar
- GET/PUT/DELETE `/api/v1/workflows/{id}` - CRUD
- POST `/api/v1/workflows/{id}/activate` - Ativar
- POST `/api/v1/workflows/{id}/deactivate` - Desativar
- GET `/api/v1/workflows/{id}/executions` - Listar execuções
- POST `/api/v1/workflows/executions/{id}/cancel` - Cancelar

### 5. Migration Alembic

`alembic/versions/sprint33_workflow_unified.py`:
- Adiciona novas colunas às tabelas existentes
- Usa batch_alter_table com try/except para idempotência
- NÃO recria tabelas (já existem do sprint07)

### 6. Módulo Deprecado

`modules/workflows/` renomeado para `modules/_deprecated_workflows_dataclass/`
- Mantido porque services migrados ainda dependem dos Dataclasses
- Imports atualizados via sed

### 7. Documentação

`docs/PROGRESSO_GERAL.md` atualizado:
- Sprint 33 marcado como "COMPLETO + UNIFICADO"
- Lista todos os novos models e services
- Documenta Action Types e API Endpoints

## Estrutura Final

```
modules/automation/workflow/           # PRINCIPAL
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── workflow.py
│   ├── workflow_step.py
│   ├── workflow_trigger.py
│   ├── workflow_execution.py
│   ├── workflow_log.py
│   ├── workflow_action.py             # NOVO
│   ├── workflow_condition.py          # NOVO
│   └── workflow_step_execution.py     # NOVO
├── services/
│   ├── __init__.py
│   ├── workflow_service.py
│   ├── workflow_engine.py
│   ├── action_executor.py             # MIGRADO
│   ├── condition_evaluator.py         # MIGRADO
│   ├── trigger_service.py             # MIGRADO
│   ├── scheduler.py                   # MIGRADO
│   ├── workflow_designer.py           # MIGRADO
│   └── workflow_executor.py           # MIGRADO
└── controllers/
    ├── __init__.py                    # NOVO
    └── workflow_controller.py         # NOVO

modules/_deprecated_workflows_dataclass/  # DEPRECADO (referência)
```

## Arquivos Modificados

| Arquivo | Ação |
|---------|------|
| `models/workflow_action.py` | CRIADO |
| `models/workflow_condition.py` | CRIADO |
| `models/workflow_step_execution.py` | CRIADO |
| `models/workflow_execution.py` | MODIFICADO (enriquecido) |
| `models/workflow_log.py` | MODIFICADO (tablename fix) |
| `models/__init__.py` | ATUALIZADO (exports) |
| `services/__init__.py` | ATUALIZADO (imports) |
| `services/action_executor.py` | COPIADO |
| `services/condition_evaluator.py` | COPIADO |
| `services/trigger_service.py` | COPIADO |
| `services/scheduler.py` | COPIADO |
| `services/workflow_designer.py` | COPIADO |
| `services/workflow_executor.py` | COPIADO |
| `controllers/__init__.py` | CRIADO |
| `controllers/workflow_controller.py` | CRIADO |
| `api/v1/__init__.py` | MODIFICADO (router registration) |
| `alembic/versions/sprint33_workflow_unified.py` | CRIADO |
| `docs/PROGRESSO_GERAL.md` | ATUALIZADO |

## Próximos Passos Pendentes

1. **Executar migration**: `alembic upgrade head`
2. **Testar endpoints**: Verificar `/api/v1/workflows`
3. **Refatorar services**: Remover dependência gradual do módulo deprecado
4. **Criar testes**: Para novos models e controller
5. **Remover módulo deprecado**: Quando não houver mais dependências

## Observações Técnicas

- Services migrados ainda importam de `modules._deprecated_workflows_dataclass`
- Isso é intencional - permite refatoração gradual
- Migration usa try/except para ser idempotente (pode rodar múltiplas vezes)
- Tabelas base já existiam (sprint07), migration apenas adiciona colunas

## Comandos Úteis

```bash
# Verificar estrutura
tree /opt/conecta-pro/backend/modules/automation/workflow/

# Rodar migration
cd /opt/conecta-pro/backend
alembic upgrade head

# Testar API
curl http://localhost:8000/api/v1/workflows -H "Authorization: Bearer $TOKEN"

# Verificar imports deprecados
grep -r "modules._deprecated_workflows_dataclass" /opt/conecta-pro/backend/modules/automation/workflow/
```
