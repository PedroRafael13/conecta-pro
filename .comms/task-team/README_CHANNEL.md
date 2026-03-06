# Task Team Channel - Operacao Obrigatoria

Plano-mestre de referencia:
- /opt/conecta-pro/audit/CLAUDE_TASK_TEAM_OPUS46_MASTER_PLAN_20260212-153807.md

## Regras obrigatorias
1. Todo agente e tarefa deve usar `claude-opus-4.6`.
2. Toda atividade deve registrar evento em `.comms/task-team/events.ndjson`.
3. Toda entrega precisa de aprovacao no arquivo `.comms/task-team/approvals.ndjson`.
4. Qualquer acao fora do plano deve ser registrada com `on_plan=false` e justificativa.

## Campos obrigatorios de evento
- ts (ISO-8601)
- agent
- model
- phase (0..8)
- task_id
- action
- status (started|progress|blocked|done)
- on_plan (true|false)
- evidence (lista de caminhos/comandos)
- notes
