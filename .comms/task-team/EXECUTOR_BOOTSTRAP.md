# Bootstrap do Executor (terminal do Claude Opus)

Execute nesta ordem:

1. Confirmar leitura do canal:
- `cat /opt/conecta-pro/.comms/task-team/README_CHANNEL.md`
- `cat /opt/conecta-pro/.comms/task-team/to_executor.md`

2. Publicar evento inicial:
- `python3 /opt/conecta-pro/scripts/task_team/post_event.py --agent Program-Manager --model claude-opus-4.6 --phase 0 --task-id BOOTSTRAP-001 --action "iniciar task team" --status started --on-plan true --evidence "/opt/conecta-pro/audit/CLAUDE_TASK_TEAM_OPUS46_MASTER_PLAN_20260212-153807.md" --notes "bootstrap do time iniciado"`

3. Confirmar no canal ao chefe:
- adicionar em `/opt/conecta-pro/.comms/task-team/to_chief.md` um bloco `UPDATE` com resumo da inicializacao.

4. Para cada tarefa subsequente:
- registrar `started` ao iniciar
- registrar `progress` em marcos
- registrar `done` ao finalizar
- registrar `blocked` com impedimentos
- se sair do plano, usar `--on-plan false` e explicar no campo `--notes`
