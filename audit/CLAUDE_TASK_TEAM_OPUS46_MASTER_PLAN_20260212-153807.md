# PLANO MESTRE - CLAUDE CODE TASK TEAM (OPUS 4.6 OBRIGATORIO)

- Data: $(date -Iseconds)
- Escopo: Conecta PRO completo (seguranca, backend, frontend, dados, infra, observabilidade, release)
- Objetivo: levar o sistema a prontidao real de producao com evidencias auditaveis

## 1) Contrato obrigatorio do Team

**Regra imutavel:** todo agente, subagente e tarefa deve usar **Claude Opus 4.6**.

### Politica de execucao (copiar no bootstrap do Team)
1. Model lock: `claude-opus-4.6` em 100% das tasks.
2. Se qualquer task iniciar em outro modelo: abortar automaticamente e reexecutar.
3. Nao aprovar PR sem evidencias de modelo e logs de execucao.
4. Toda saida deve incluir: `agent`, `model`, `task_id`, `commit_sha`, `evidence_links`.

### Gate de conformidade de modelo
- Gate M0 (bloqueador): validar arquivo de configuracao do Team e logs antes de iniciar trabalho tecnico.
- Critico: se 1 task rodar fora de Opus 4.6, sprint invalida.

## 2) Estrutura de agentes (Task Team)

1. `Program-Manager` (orquestracao, dependencias, risco, cronograma)
2. `Security-Lead` (segredos, OAuth, websocket auth, hardening)
3. `Backend-Lead` (Python/FastAPI, dependencias, lint/test)
4. `Frontend-Lead` (Next.js/TS, lint/typecheck/build/test)
5. `Data-Lead` (Postgres/Redis, migracoes, integridade)
6. `SRE-Lead` (docker, healthchecks, runtime readiness)
7. `QA-Lead` (unit/integration/e2e/performance)
8. `Release-Lead` (go/no-go, checklist, rollback)
9. `Audit-Lead` (evidencias, rastreabilidade, conformidade)

Todos com `model = claude-opus-4.6`.

## 3) Fases completas (0 a 8)

## Fase 0 - Baseline e congelamento controlado
- Criar branch de programa (`stabilization/production-readiness-<date>`).
- Snapshot de estado atual (testes, CVEs, lint/typecheck, build).
- Definir SLO/SLI alvo para go-live.

Aceite:
- Baseline versionado com hashes e timestamps.

## Fase 1 - P0 Seguranca (bloqueador maximo)
- Remover segredos/chaves/certificados do repo e historico.
- Rotacionar TODAS as credenciais expostas.
- Implantar secret scanning no pre-commit + CI.
- Implementar politica de arquivos proibidos (denylist).

Aceite:
- 0 segredos detectados.
- Evidencia de rotacao validada por Security-Lead.

## Fase 2 - P1 Seguranca de aplicacao
- Eliminar token em query string no OAuth callback.
- Mover autenticacao websocket para mecanismo seguro (header/cookie/token efemero).
- Revisar links de reset/assinatura para evitar vazamento de token.
- Atualizar dependencias vulneraveis Python/Node prioritarias.

Aceite:
- `pip-audit` sem vulnerabilidade critica/high bloqueadora.
- `npm audit --omit=dev` sem high/critical bloqueadora.
- Testes de auth e sessao atualizados e verdes.

## Fase 3 - Qualidade backend
- Corrigir falhas de lint backend.
- Reduzir warnings deprecados criticos (utcnow, pydantic v2, etc).
- Garantir compatibilidade com stack alvo.

Aceite:
- `ruff check` verde.
- `pytest` verde sem regressao de cobertura.

## Fase 4 - Qualidade frontend
- Corrigir lint frontend (incluindo docs/e2e/tests com escopo definido).
- Corrigir typecheck TS integral.
- Ajustar `next.config.ts` (migracao de `serverComponentsExternalPackages`).

Aceite:
- `npm run lint` verde.
- `npm run type-check` verde.
- `npm run build` verde sem warnings bloqueadores.

## Fase 5 - Dados e integridade operacional
- Auditoria de schema/migracoes.
- Verificacao de consistencia transacional de fluxos criticos.
- Politicas de backup/restore testadas.

Aceite:
- Plano de DR testado com restore bem-sucedido.
- Check de integridade aprovado pelo Data-Lead.

## Fase 6 - E2E e qualidade de release
- Executar matriz E2E por dominio critico.
- Rodar smoke suite obrigatoria em cada PR.
- Controlar flakiness e estabilizar testes intermitentes.

Aceite:
- Smoke E2E: 100% verde.
- E2E critico (auth/financeiro/operacional/LGPD): verde com evidencias.

## Fase 7 - Observabilidade e operacao
- Integrar monitoramento (Sentry + Prometheus/Grafana + logs centralizados).
- Definir alertas de erro/latencia/disponibilidade.
- Criar runbooks de incidente e rollback.

Aceite:
- Alertas testados em ambiente de staging.
- Runbooks aprovados por SRE-Lead.

## Fase 8 - Go/No-Go e liberacao
- War room de release com checklist final.
- Go-live progressivo (canary/blue-green, se disponivel).
- Janela de observacao e handoff operacional.

Aceite:
- Todos os gates A..H aprovados (abaixo).

## 4) Gates obrigatorios de aprovacao

- Gate A: Sem segredos no repo/historico ativo.
- Gate B: Seguranca de dependencia sem bloqueador high/critical.
- Gate C: OAuth/WebSocket sem token em URL.
- Gate D: Lint + typecheck 100% verde.
- Gate E: Build backend/frontend verde.
- Gate F: Unit + integration + E2E critico verde.
- Gate G: Observabilidade e alertas validados.
- Gate H: Plano de rollback e DR testado.

**Regra:** release proibida se qualquer gate falhar.

## 5) Definicao de pronto para producao (DoD)

1. Todos os gates A..H aprovados.
2. Sem P0/P1 aberto em seguranca.
3. 0 regressao funcional nos fluxos criticos.
4. Evidencias completas publicadas em `/opt/conecta-pro/audit`.
5. Assinatura final: Security + QA + SRE + Release + Auditoria.

## 6) Backlog executivo em ondas

- Onda 1: Segredos + rotacao + bloqueios CI.
- Onda 2: OAuth/websocket + CVEs runtime.
- Onda 3: lint/typecheck/build stabilization.
- Onda 4: E2E critico + observabilidade + go-live.

## 7) Artefatos obrigatorios por onda

1. `WAVE_N_REPORT.md`
2. `WAVE_N_RISK_REGISTER.md`
3. `WAVE_N_TEST_EVIDENCE.md`
4. `WAVE_N_RELEASE_DECISION.md`

## 8) Supervisao (Codex)

- Revisao tecnica diaria de diffs e evidencias.
- Auditoria de conformidade de modelo (Opus 4.6).
- Reprovacao automatica de pacote incompleto.
- Consolidacao de status executivo para decisao de continuidade.
