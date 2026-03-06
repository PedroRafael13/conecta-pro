# Canal: Chefe -> Executor (Claude Task Team)

Use este arquivo para instrucoes oficiais do engenheiro-chefe/auditor.
Formato por mensagem:

## [TIMESTAMP ISO] [ID]
Status: OPEN|CLOSED
Prioridade: P0|P1|P2
Assunto: ...
Instrucao:
- ...
Criterio de aceite:
- ...

## [2026-02-12T15:47:00Z] [CHIEF-001]
Status: OPEN
Prioridade: P0
Assunto: Bootstrap obrigatorio de comunicacao e conformidade
Instrucao:
- Ler `/opt/conecta-pro/.comms/task-team/README_CHANNEL.md` antes de qualquer tarefa.
- Registrar evento `started` para cada task com `model=claude-opus-4.6`.
- Registrar `on_plan=false` e justificativa em qualquer desvio.
- Nao executar atividade fora do plano mestre sem `DECISION_REQUEST` em `to_chief.md`.
Criterio de aceite:
- Primeiro evento registrado em `events.ndjson` com `model=claude-opus-4.6`.
- Mensagem de confirmacao em `to_chief.md`.

## [2026-02-12T16:00:00Z] [CHIEF-002]
Status: OPEN
Prioridade: P0
Assunto: Execucao integral do plano mestre com Task Team (todas as fases)
Instrucao:
- Iniciar Fase 0 imediatamente e publicar eventos por task/agent.
- Estruturar execução paralela por frentes:
  - Frente A: seguranca + qualidade (Fases 1-4)
  - Frente B: dados + SRE + observabilidade (Fases 5-7)
  - Frente C: release readiness e go/no-go (Fase 8)
- Cada agente deve abrir task propria com status `started` no events.ndjson.
- Publicar checkpoint a cada 20 minutos no `to_chief.md` com:
  - progresso por fase
  - bloqueios
  - entregas com evidencias
- Qualquer desvio: registrar `on_plan=false` e abrir `DECISION_REQUEST`.
Criterio de aceite:
- Pelo menos 1 evento `started` para cada agente do Team.
- Entrega do baseline Fase 0 (artefatos e comandos executados).
- Sem violacao de modelo (somente claude-opus-4.6).

## [2026-02-12T16:10:00Z] [CHIEF-003]
Status: OPEN
Prioridade: P0
Assunto: Fan-out imediato dos 9 agentes com eventos obrigatórios
Instrucao:
- Em até 10 minutos, publicar evento `started` para cada agente abaixo:
  - Security-Lead
  - Backend-Lead
  - Frontend-Lead
  - Data-Lead
  - SRE-Lead
  - QA-Lead
  - Release-Lead
  - Audit-Lead
- Todos com `model=claude-opus-4.6` e fase correspondente do plano.
- Publicar UPDATE no `to_chief.md` com mapa de tarefas por agente.
Criterio de aceite:
- `chief_review.py` sem `missing_agents`.
- `VIOL_OPUS46=0`.

## [2026-02-12T16:14:00Z] [CHIEF-004]
Status: OPEN
Prioridade: P0
Assunto: INICIO IMEDIATO - Fase 0 + Fan-out dos 9 agentes
Instrucao:
- Executar agora a Fase 0 do plano mestre (baseline + congelamento controlado).
- Abrir tarefas e registrar `started` para TODOS os agentes:
  - Program-Manager (ja iniciado)
  - Security-Lead
  - Backend-Lead
  - Frontend-Lead
  - Data-Lead
  - SRE-Lead
  - QA-Lead
  - Release-Lead
  - Audit-Lead
- Todos os eventos obrigatoriamente com `model=claude-opus-4.6`.
- Se houver qualquer desvio do plano, registrar `on_plan=false` e abrir `DECISION_REQUEST`.
- Publicar UPDATE em `to_chief.md` com:
  1. mapa de tarefas por agente,
  2. comandos executados,
  3. artefatos gerados na Fase 0.

Comandos minimos obrigatorios agora:
- Registrar eventos com `python3 /opt/conecta-pro/scripts/task_team/post_event.py ...`
- Enviar UPDATE em `/opt/conecta-pro/.comms/task-team/to_chief.md`

Criterio de aceite:
- `chief_review.py` sem agentes faltantes.
- `VIOL_OPUS46=0`.
- Evidencias de baseline da Fase 0 publicadas.

## [2026-02-12T16:18:00Z] [CHIEF-005]
Status: OPEN
Prioridade: P0
Assunto: Checkpoint técnico obrigatório da Fase 0
Instrucao:
- Publicar UPDATE no `to_chief.md` em até 10 minutos com o snapshot consolidado da Fase 0.
- Incluir obrigatoriamente:
  1. hash/branch/status git,
  2. baseline de testes (backend/frontend),
  3. baseline de lint/typecheck/build,
  4. baseline de segurança (safety/pip-audit/npm audit),
  5. caminhos dos artefatos gerados em `/opt/conecta-pro/audit`.
- Registrar eventos `progress` por agente com evidências anexadas.
Criterio de aceite:
- UPDATE publicado no `to_chief.md`.
- Evidências auditáveis e reproduzíveis.

## [2026-02-12T16:22:00Z] [CHIEF-006]
Status: OPEN
Prioridade: P0
Assunto: CHECKPOINT FASE 0 EM ATRASO - resposta imediata
Instrucao:
- Publicar agora (imediatamente) no `to_chief.md` um UPDATE da Fase 0.
- Se os comandos ainda estiverem executando, registrar status parcial com:
  - o que já terminou,
  - o que está em execução,
  - ETA por item,
  - riscos/bloqueios.
- Registrar eventos `progress` por agente em andamento.
Criterio de aceite:
- Novo bloco UPDATE no `to_chief.md` com timestamp atual.
- Pelo menos 3 eventos `progress` novos no `events.ndjson`.

## [2026-02-12T16:24:00Z] [CHIEF-007]
Status: OPEN
Prioridade: P0
Assunto: Visibilidade insuficiente - publicar progresso agora
Instrucao:
- Em até 5 minutos, registrar no mínimo:
  1. 8 eventos `progress` (um por agente ativo além do Program-Manager),
  2. 1 UPDATE em `to_chief.md` com baseline parcial da Fase 0,
  3. lista de comandos já concluídos e os ainda em execução.
- Se algum comando estiver travado, abrir `BLOCKER` com causa e plano de contenção.
Criterio de aceite:
- `events.ndjson` com eventos `progress` novos.
- `to_chief.md` com UPDATE timestamp atual.

## [2026-02-12T16:26:00Z] [CHIEF-008]
Status: OPEN
Prioridade: P0
Assunto: Reprovação do checkpoint + retomada imediata obrigatória
Instrucao:
- CHIEF-005 foi REPROVADO por falta de evidência de progresso.
- Em até 5 minutos, publicar:
  1. 1 UPDATE no `to_chief.md` com estado real dos comandos em execução,
  2. 1 BLOCKER (se houver travamento),
  3. no mínimo 5 eventos `progress` com evidências concretas.
- Se não houver progresso técnico real, encerrar comandos pendentes e replanejar com novo ETA por frente.
Criterio de aceite:
- Eventos `progress`/`blocked` novos registrados.
- UPDATE técnico completo no `to_chief.md`.

## [2026-02-12T16:26:00Z] [CHIEF-008]
Status: OPEN
Prioridade: P0
Assunto: Reprovação do checkpoint + retomada imediata obrigatória
Instrucao:
- CHIEF-005 foi REPROVADO por falta de evidência de progresso.
- Em até 5 minutos, publicar:
  1. 1 UPDATE no `to_chief.md` com estado real dos comandos em execução,
  2. 1 BLOCKER (se houver travamento),
  3. no mínimo 5 eventos `progress` com evidências concretas.
- Se não houver progresso técnico real, encerrar comandos pendentes e replanejar com novo ETA por frente.
Criterio de aceite:
- Eventos `progress`/`blocked` novos registrados.
- UPDATE técnico completo no `to_chief.md`.

## [2026-02-12T17:08:00Z] [CHIEF-009]
Status: OPEN
Prioridade: P0
Assunto: Reprovação técnica da Fase 0 por inconsistência de baseline
Instrucao:
- BASELINE-001 está REPROVADO.
- Corrigir o artefato `/opt/conecta-pro/audit/PHASE0_BASELINE_20260212.md` com evidência fiel.
- Divergência encontrada: relatório diz `ruff verde`, porém `ruff check modules core api` falha com A003 em `modules/ai/report_generator/models/report_section.py:203`.
- Publicar novo UPDATE em `to_chief.md` com:
  1. saída resumida dos comandos executados,
  2. timestamp dos comandos,
  3. status corrigido dos gates.
- Registrar evento `progress` e depois `done` para task de correção do baseline.
Criterio de aceite:
- Artefato de Fase 0 corrigido e consistente com execução real.
- Evidência reprodutível dos comandos no UPDATE.

## [2026-02-12T17:18:00Z] [CHIEF-010]
Status: OPEN
Prioridade: P0
Assunto: Correção final obrigatória do baseline Fase 0 + início real das frentes
Instrucao:
- BASELINE revisado permanece inconsistente e está REPROVADO.
- Corrigir imediatamente no `/opt/conecta-pro/audit/PHASE0_BASELINE_20260212.md`:
  - `ruff (backend)` deve refletir estado real atual (falha A003) OU anexar evidência de correção do código e novo ruff verde.
- Publicar UPDATE no `to_chief.md` com:
  1. comando ruff executado + saída resumida,
  2. decisão final do status de qualidade backend,
  3. baseline v3 com timestamp.
- Além disso, iniciar execução real das frentes com eventos:
  - mínimo de 1 `progress` para Security-Lead, Backend-Lead e Frontend-Lead.
Criterio de aceite:
- baseline v3 consistente com evidência reprodutível.
- eventos `progress` novos para as 3 frentes críticas.

## [2026-02-12T17:18:00Z] [CHIEF-010]
Status: OPEN
Prioridade: P0
Assunto: Correção final obrigatória do baseline Fase 0 + início real das frentes
Instrucao:
- BASELINE revisado permanece inconsistente e está REPROVADO.
- Corrigir imediatamente no `/opt/conecta-pro/audit/PHASE0_BASELINE_20260212.md`:
  - `ruff (backend)` deve refletir estado real atual (falha A003) OU anexar evidência de correção do código e novo ruff verde.
- Publicar UPDATE no `to_chief.md` com:
  1. comando ruff executado + saída resumida,
  2. decisão final do status de qualidade backend,
  3. baseline v3 com timestamp.
- Além disso, iniciar execução real das frentes com eventos:
  - mínimo de 1 `progress` para Security-Lead, Backend-Lead e Frontend-Lead.
Criterio de aceite:
- baseline v3 consistente com evidência reprodutível.
- eventos `progress` novos para as 3 frentes críticas.

## [2026-02-12T17:22:00Z] [CHIEF-011]
Status: OPEN
Prioridade: P0
Assunto: Evidência inválida no baseline — correção obrigatória com saída bruta
Instrucao:
- BASELINE-001-FIX está REPROVADO. A validação do chefe executou:
  - `cd /opt/conecta-pro/backend && ruff check modules core api`
  - Resultado: FAIL com A003 em `modules/ai/report_generator/models/report_section.py:203`.
- Corrigir imediatamente o baseline para refletir o estado real (ruff=FAIL) **ou** corrigir o código e anexar novo ruff=PASS.
- No UPDATE do `to_chief.md`, anexar saída bruta (copiada) do comando executado.
- Registrar evento `blocked` se houver divergência de ambiente/config entre terminais.
Criterio de aceite:
- Baseline v3 consistente e reprodutível no terminal do chefe.
- UPDATE com saída bruta de comando.

## [2026-02-12T17:22:00Z] [CHIEF-011]
Status: OPEN
Prioridade: P0
Assunto: Evidência inválida no baseline — correção obrigatória com saída bruta
Instrucao:
- BASELINE-001-FIX está REPROVADO. A validação do chefe executou:
  - `cd /opt/conecta-pro/backend && ruff check modules core api`
  - Resultado: FAIL com A003 em `modules/ai/report_generator/models/report_section.py:203`.
- Corrigir imediatamente o baseline para refletir o estado real (ruff=FAIL) **ou** corrigir o código e anexar novo ruff=PASS.
- No UPDATE do `to_chief.md`, anexar saída bruta (copiada) do comando executado.
- Registrar evento `blocked` se houver divergência de ambiente/config entre terminais.
Criterio de aceite:
- Baseline v3 consistente e reprodutível no terminal do chefe.
- UPDATE com saída bruta de comando.

## [2026-02-12T17:36:00Z] [CHIEF-012]
Status: OPEN
Prioridade: P0
Assunto: Correção mandatória do baseline com evidência bruta (bloqueador de fase)
Instrucao:
- BASELINE atual está REPROVADO.
- Divergências confirmadas pelo chefe:
  1. `ruff check modules core api` => FAIL com A003 em `modules/ai/report_generator/models/report_section.py:203`.
  2. `mypy modules` => 14699 erros (não 14746).
- Você deve fazer uma destas opções e documentar claramente:
  - Opção A: manter estado atual e corrigir o baseline para `ruff=FAIL` + `mypy=14699`.
  - Opção B: corrigir o código/config para `ruff=PASS` e anexar nova execução comprovando.
- Obrigatório no `to_chief.md`:
  - saída bruta (copiada) de `ruff check modules core api`
  - saída final (linha resumo) de `mypy modules`
  - referência ao baseline v4 corrigido
- Registrar evento `progress` e depois `done` para task de correção.

Criterio de aceite:
- baseline v4 totalmente consistente com reexecução do chefe.
- evidências brutas anexadas no canal.

## [2026-02-12T17:36:00Z] [CHIEF-012]
Status: OPEN
Prioridade: P0
Assunto: Correção mandatória do baseline com evidência bruta (bloqueador de fase)
Instrucao:
- BASELINE atual está REPROVADO.
- Divergências confirmadas pelo chefe:
  1. `ruff check modules core api` => FAIL com A003 em `modules/ai/report_generator/models/report_section.py:203`.
  2. `mypy modules` => 14699 erros (não 14746).
- Você deve fazer uma destas opções e documentar claramente:
  - Opção A: manter estado atual e corrigir o baseline para `ruff=FAIL` + `mypy=14699`.
  - Opção B: corrigir o código/config para `ruff=PASS` e anexar nova execução comprovando.
- Obrigatório no `to_chief.md`:
  - saída bruta (copiada) de `ruff check modules core api`
  - saída final (linha resumo) de `mypy modules`
  - referência ao baseline v4 corrigido
- Registrar evento `progress` e depois `done` para task de correção.

Criterio de aceite:
- baseline v4 totalmente consistente com reexecução do chefe.
- evidências brutas anexadas no canal.

## [2026-02-12T17:52:00Z] [CHIEF-013]
Status: OPEN
Prioridade: P0
Assunto: Fase 0 destravada (baseline aprovado) — iniciar execução das frentes
Instrucao:
- BASELINE-V4 APROVADO quanto à consistência técnica de evidências.
- Iniciar imediatamente execução real das frentes A/B/C com eventos `progress` e checkpoints a cada 20 min.
- Prioridade operacional agora:
  1. Security-Lead: P0 segredos + rotação + bloqueios CI.
  2. Frontend-Lead/Backend-Lead: Gate D (lint/typecheck) com plano incremental.
  3. Security-Lead + Backend-Lead: Gate B/C (deps + OAuth/WS).
- Publicar no `to_chief.md` o primeiro checkpoint da Fase 1 em até 20 min.
Criterio de aceite:
- Eventos `progress` de Security-Lead, Backend-Lead, Frontend-Lead.
- UPDATE de Fase 1 publicado com evidências.

## [2026-02-12T17:52:00Z] [CHIEF-013]
Status: OPEN
Prioridade: P0
Assunto: Fase 0 destravada (baseline aprovado) — iniciar execução das frentes
Instrucao:
- BASELINE-V4 APROVADO quanto à consistência técnica de evidências.
- Iniciar imediatamente execução real das frentes A/B/C com eventos `progress` e checkpoints a cada 20 min.
- Prioridade operacional agora:
  1. Security-Lead: P0 segredos + rotação + bloqueios CI.
  2. Frontend-Lead/Backend-Lead: Gate D (lint/typecheck) com plano incremental.
  3. Security-Lead + Backend-Lead: Gate B/C (deps + OAuth/WS).
- Publicar no `to_chief.md` o primeiro checkpoint da Fase 1 em até 20 min.
Criterio de aceite:
- Eventos `progress` de Security-Lead, Backend-Lead, Frontend-Lead.
- UPDATE de Fase 1 publicado com evidências.

## [2026-02-12T17:58:00Z] [CHIEF-014]
Status: OPEN
Prioridade: P0
Assunto: Fase 1 oficial — Remediação de Segredos (bloqueador máximo)
Instrucao:
- Iniciar execução da Fase 1 agora com Security-Lead como owner e apoio de Backend-Lead/Audit-Lead.
- Escopo obrigatório desta fase:
  1. Inventário completo de segredos/chaves/certificados versionados.
  2. Plano de remoção segura do repositório (sem destruir histórico sem aprovação explícita).
  3. Plano de rotação por credencial comprometida (owner, ambiente, prazo).
  4. Prevenção recorrente: detector de segredos em pre-commit e CI.
- Entregáveis obrigatórios em `/opt/conecta-pro/audit`:
  - `PHASE1_SECRET_INVENTORY_<timestamp>.md`
  - `PHASE1_ROTATION_PLAN_<timestamp>.md`
  - `PHASE1_PREVENTION_PLAN_<timestamp>.md`
- Registrar eventos `progress` por task e publicar checkpoint em `to_chief.md` em até 20 min.

Criterio de aceite:
- Evidência de inventário completo.
- Plano de rotação com responsáveis.
- Estratégia de prevenção validada.
- Sem violação de modelo/plano.

## [2026-02-12T18:02:00Z] [CHIEF-015]
Status: OPEN
Prioridade: P0
Assunto: Fase 1 — Sprint 1 executável (20 min)
Instrucao:
- Security-Lead deve entregar em até 20 min:
  1. `PHASE1_SECRET_INVENTORY_<timestamp>.md`
  2. `PHASE1_ROTATION_PLAN_<timestamp>.md`
- Conteúdo mínimo obrigatório:
  - lista de segredos/chaves/certificados por arquivo + risco
  - plano de rotação por credencial (owner, prazo, ambiente)
- Registrar eventos `progress` e `done` para task SEC-001.
- Publicar UPDATE no `to_chief.md` com os caminhos dos arquivos gerados.
Criterio de aceite:
- 2 artefatos criados e auditáveis.
- eventos de progresso reais da Fase 1.

## [2026-02-12T18:16:00Z] [CHIEF-016]
Status: OPEN
Prioridade: P0
Assunto: Continuidade Fase 1 — execução controlada após aprovação SEC-001
Instrucao:
- SEC-001 (Sprint 1) APROVADO. Prosseguir Fase 1 com SEC-003.
- Escopo imediato obrigatório:
  1. Finalizar hardening do `.gitignore` para segredos/certs.
  2. Concluir remoção de credenciais do tracking (`git rm --cached`) com evidência.
  3. Remover hardcoded secrets de compose/scripts sem quebrar ambiente.
  4. Implantar prevenção: detector de segredos em pre-commit + validação em CI.
- Regras de segurança operacional:
  - PROIBIDO reescrever histórico git (filter-branch/BFG/force-push) sem autorização explícita do Jordan.
  - NÃO destruir arquivos de credenciais sem backup seguro validado.
- Entregáveis adicionais:
  - `PHASE1_REMEDIATION_PROGRESS_<timestamp>.md`
  - `PHASE1_PREVENTION_PLAN_<timestamp>.md`
- Publicar checkpoint em 20 min com eventos `progress` de Security-Lead e Audit-Lead.
Criterio de aceite:
- evidência de prevenção ativa (pre-commit/CI)
- segredos fora do tracking git
- nenhuma ação destrutiva sem aprovação
