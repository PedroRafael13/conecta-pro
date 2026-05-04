# T1 GEDEON-MAP — Mapeamento Estado Real
**Data:** 2026-05-04
**Duração:** 02:18 → 02:29 (~11min)
**Branch:** feature/people-management-reorganization
**Tipo:** Read-only, zero alteração — inventário puro

---

## 1. CONTRACTS_GEDEON.md

| Item | Valor |
|------|-------|
| Tamanho | 183 KB |
| Total de seções `##§` | **39** |
| Última seção pura GEDEON | §48 (D5.5.2 logging) |
| Últimas seções (§49–§54) | D6/D7 Inter — banking, fora do escopo GEDEON |
| Versão declarada | v1.54 (§54 = último commit 2026-05-04) |

**Últimas 10 seções:**
§45 D5.3.1 | §46 D5.4 CertidoesUpdater | §47 D5.5 UI Card | §48 D5.5.2 Logging |
§49 D6 Inter | §50 D7 Pagamentos | §51 Fix Dashboard | §52 Fix Desvios D7 | §53 Fix Auth | §54 Fix Saldo

---

## 2. Pasta agents/

| Item | Valor |
|------|-------|
| Total de arquivos | **505** |
| Subpastas | `core/`, `modules/`, `cto/`, `knowledge/`, `nivel3/` |

**Conteúdo real — sistema de monitoramento CTO, NÃO GEDEON puro:**
- `agents/core/` — BaseAgent, BaseOrchestrator, AuditOrchestrator, AutoRemediator, CodeFixer
- `agents/modules/` — 13 orquestradores de monitoramento (`orch_dp.py`, `orch_ged.py`, etc.)
- `agents/cto/` — brain, predicação, escalonamento, monitor_bot, tickets, pos_mortem
- `orchestrator_unificado.py` — roda via cron a cada 5/30/360min via Telegram

**Nota:** Os "80+ agentes" documentados no CLAUDE.md são do sistema de monitoramento. GEDEON tem sub-agentes próprios em `backend/modules/gedeon/agents/`.

---

## 3. Rotinas/scripts

| Item | Status |
|------|--------|
| `rotinas/scripts/onvio-auth-refresh.sh` | ✅ existe |
| `rotinas/scripts/onvio-sync-mensal.sh` | ✅ existe |
| Total de scripts em `rotinas/scripts/` | **2** (prompt previa 5) |

**Scripts no crontab relacionados ao GEDEON:**
```
0 2 1 * *  /opt/conecta-pro/scripts/gerar_kits_mensais.sh      # 1º do mês
30 7 * * 1-5  /opt/conecta-pro/scripts/briefing_jordan.sh       # seg-sex 07:30
*/30 * * * *  orchestrator_unificado.py completo                # a cada 30min
*/5  * * * *  orchestrator_unificado.py rapido                  # a cada 5min
0 */6 * * *   orchestrator_unificado.py heartbeat               # a cada 6h
```

⚠️ `onvio-auth-refresh.sh` e `onvio-sync-mensal.sh` **NÃO estão no crontab** — rodam apenas manualmente.

---

## 4. Endpoints GEDEON registrados (backend)

> **Nota:** OpenAPI desabilitado em produção (`openapi_url=None`). Mapeado via source code.

### gedeon_controller (prefixo: `/gedeon`)
| Método | Path |
|--------|------|
| GET | `/context/{cliente_id}/{competencia}` |
| GET | `/context/{cliente_id}/{competencia}/tipo2` |
| GET | `/dashboard` |
| GET | `/alertas/vencimentos` |
| GET | `/conformidade/{cliente_id}/{competencia}` |
| POST | `/hermes/classificar` |
| GET | `/kits/status` |
| GET | `/kits/config` |
| GET | `/atlas/insights` |
| GET | `/atlas/historico/{cliente_id}/{competencia}` |
| GET | `/atlas/anomalia/{cliente_id}` |
| GET | `/sophia/status` |
| GET | `/sophia/buscar` |
| POST | `/sophia/perguntar` |
| POST | `/sophia/reindexar` |
| GET | `/sophia/alertas` |
| GET | `/sophia/impacto-folha` |
| POST | `/sophia/indexar` |

### kit_controller (prefixo: `/gedeon/kits`)
2 endpoints (GET)

### onvio_controller (prefixo: `/onvio`)
| Método | Path |
|--------|------|
| GET | `/status` |
| POST | `/sync` |
| GET | `/documentos` |
| GET | `/historico` |
| GET | `/stats` |
| POST | `/reclassificar` |
| POST | `/extrair-valores` |
| GET | `/guias/fgts` |
| GET | `/guias/inss` |
| GET | `/valores-fiscais-resumo` |

### gdrive_controller (prefixo: `/gdrive`)
12 endpoints: status, autorizar, kits, ingestão, montar-e-enviar, enviar-email, montar, link, portal/{client_id}/kits, oauth/callback, desconectar, autorizar

### GED base (prefixo: `/ged`)
14 sub-routers: Pastas, Documentos, Versões, Compartilhamentos, Tags, Assinaturas, Estatísticas, Config & Reports, Integração, Certidões, Auto-Assemble, Kit PDFs, Kit Real, Coleta Automática

---

## 5. Celery Beat — Tasks GEDEON (de 38 tasks totais)

| Task | Schedule | Fila |
|------|----------|------|
| `gedeon.daily_all` | 07:00 diário | gov.batch |
| `gedeon.kronos.verificacao_diaria` | 06:00 diário | gov.batch |
| `gedeon.fiscal.verificar_certidoes` | 07:00 diário | gov.batch |
| `gedeon.cashflow_predictor` | 07:15 diário | gov.batch |
| `gedeon.collection_negotiator` | 09:00 diário | gov.batch |
| `gedeon.risk_monitor` | a cada 5min | — |
| `ged.buscar_certidoes_portais` | 06:30 diário | ged |
| `ged.sync_cnds` | a cada 24h | operacional |
| `ged.auto_collect_documents` | 1º mês 02:00 | operacional |
| `bidding.verificar_certidoes_vencimento` | a cada 6h | gov.batch |
| `fiscal.certidoes.sync_diario` | 06:30 diário | ged |
| `fiscal-nfe-entrada-2h` | a cada 2h | gov.sefaz.nfe |

⚠️ `celery-batch` e `celery-beat` reiniciaram durante o mapeamento (backend restart). Logs sem entradas GEDEON no período.

---

## 6. Módulo backend GEDEON

| Item | Valor |
|------|-------|
| Total .py | **40 arquivos** |
| Subpastas | agents, context, controllers, gedeon/, models, onvio/, schemas, services, subscribers, tasks |

**Sub-agentes:**
- `argos.py` — vigilância documental
- `atlas.py` — análise e insights
- `hermes.py` — classificação de documentos
- `kronos.py` — verificação cronológica/certidões
- `sophia.py` — busca semântica + IA
- `themis.py` — conformidade legal

**Onvio (subpasta `onvio/`):** onvio_client, onvio_parser, onvio_sync_service, pdf_extractors (DCTFWEB, FGTS, INSS), enrichment_service

**Serviços:** kit_builder_service, onvio_doc_scope_classifier

---

## 7. Tabelas DB — Estado Real

| Tabela | Linhas | Status |
|--------|--------|--------|
| `onvio_documents` | **534** | 534 categorizados, 436 com doc_scope, 121 com detalhes_json |
| `gedeon_document_index` | **617** | 617 com embedding + modulo |
| `ged_kit_documents` | **1.237** | 18 kits distintos |
| `kit_template_presenca` | **320** | |
| `kit_documental_templates` | **32** | |
| `gedeon_kit_config` | **13** | |
| `onvio_sync_log` | **85** | ⚠️ últimos 5: todos `status=error` |
| `ged_coleta_logs` | **59** | última: cnds_only success 2026-05-03 |
| `ged_document_kits` | **18** | |
| `ged_certidoes` | **8** | 6 com alerta_ativo=true |
| `ged_clients` | **11** | 10 condomínios + Conecta Mais |
| `gedeon_client_patterns` | **6** | |
| `gedeon_kit_history` | **11** | |
| `gedeon_learning_events` | **0** | sem eventos |
| `gdrive_config` | **1** | 1 conta conectada |
| `gdrive_kits` | **0** | sem uploads |

**onvio_documents por doc_scope:**
| scope | qtd |
|-------|-----|
| condominio | 236 |
| empresa_matriz | 107 |
| NULL (sem scope) | 98 |
| funcionario | 93 |

**ged_clients (11):**
10 condomínios (Michelangelo, Flores da Cidade, Mirante das Flores, Gelain, Prime Arena, Green Hills, Parise Village, Villa dos Pássaros, Villa dei Fiori, Laranjeiras Village) + Conecta Mais Segurança e Tecnologia

---

## 8. Telegram Bot

| Item | Status |
|------|--------|
| `TELEGRAM_BOT_TOKEN` | ✅ em `/opt/conecta-pro/.env` (REDACTED) |
| `TELEGRAM_CHAT_ID` | ✅ em `/opt/conecta-pro/.env` (REDACTED) |
| `MONITOR_BOT_TOKEN` | Exposto no crontab (bot diferente — CTO monitor) |
| Tabelas notificação | 14 tabelas (notification_logs, notification_queue, etc.) |
| notification_logs | **0 linhas** — não usada |

---

## 9. Frontend — Páginas GED

**13 páginas** em `/modulos/gestao-pessoas/ged/`:

| Rota | Arquivo |
|------|---------|
| `/ged` | page.tsx (dashboard GED) |
| `/ged/clientes` | Gestão de clientes |
| `/ged/kits` | Lista de kits |
| `/ged/kits/[id]` | Detalhe do kit |
| `/ged/documentos` | Documentos |
| `/ged/certidoes` | Certidões (semáforo D5.5) |
| `/ged/onvio-sync` | Sync Onvio |
| `/ged/upload` | Upload de documentos |
| `/ged/envios` | Histórico de envios |
| `/ged/relatorios` | Relatórios |
| `/ged/configuracoes` | Configurações |
| `/ged/assinaturas` | Assinaturas digitais |
| `/ged/whatsapp` | Notificações WhatsApp |

Nenhuma página `/modulos/gedeon` dedicada — GEDEON opera como backend invisível exposto via `/gedeon/*` endpoints.

---

## 10. Logs Celery GEDEON

Containers `celery-batch` e `celery-beat` reiniciaram durante mapeamento. **Zero logs GEDEON encontrados** no período recente. Containers `celery-priority`, `celery-sefaz`, `celery-nfse`, `celery-operacional`, `celery-integrations` estão há 2 semanas rodando sem restart.

---

## 11. Tabelas de Execução (Scheduler)

| Tabela | Linhas |
|--------|--------|
| `scheduler_executions` | **0** |
| `execution_logs` | **0** |
| `scheduler_tasks` | — |
| `ai_workflow_executions` | — |

As tabelas do scheduler interno existem mas estão vazias — tasks GEDEON rodam via Celery Beat (não pelo scheduler interno).

---

## 12. ged_certidoes_update_logs (D5.5.2)

**Tabela `ged_certidoes_update_logs` não existe no banco.** A tabela equivalente real é `ged_coleta_logs`.

**10 últimas execuções (ged_coleta_logs):**

| run_type | status | certidoes_atualizadas | alertas_disparados | run_at |
|----------|--------|----------------------|--------------------|----|
| cnds_only | success | 6 | 5 | 2026-05-03 23:56 |
| manual | success | 6 | 5 | 2026-04-30 14:47 |
| manual | success | 6 | 5 | 2026-04-30 14:47 |
| manual | success | 6 | 5 | 2026-04-30 14:45 |
| cnds_only | success | 6 | 5 | 2026-04-30 14:44 |
| manual | error | 0 | 0 | 2026-04-30 03:14 |
| manual | success | 0 | 0 | 2026-04-30 03:14 |
| manual | success | 0 | 0 | 2026-04-30 03:14 |
| manual | success | 0 | 0 | 2026-04-30 03:14 |
| manual | error | 0 | 0 | 2026-04-28 19:20 |

---

## SINAIS DE ATENÇÃO

| # | Sinal | Impacto |
|---|-------|---------|
| 🔴 | Alvará de Funcionamento vencido desde **2026-02-28** | Legal — risco operacional |
| 🟡 | `onvio_sync_log` — todos `status=error` desde 2026-04-30 | Onvio sync via API não funciona |
| 🟡 | `onvio-auth-refresh.sh` existe mas **não está no crontab** | Sessão Onvio pode expirar |
| 🟡 | 98 docs em `onvio_documents` sem `doc_scope` (NULL) | Parser não classificou 18% |
| 🟡 | `gedeon_learning_events` = 0 linhas | GEDEON não registrou aprendizados |
| 🟢 | `ged_coleta_logs` última execução: success 2026-05-03 | CNDs atualizando normalmente |
| 🟢 | 617 documentos indexados com embedding | Sophia funcional |
| 🟢 | 12 tasks Celery Beat GEDEON agendadas | Schedule configurado |

---

## RESUMO EXECUTIVO

**O que existe e funciona:**
- Backend GEDEON: 40 arquivos .py, 6 sub-agentes, 18+ endpoints ativos
- DB: 534 docs Onvio, 617 indexados com embedding, 18 kits, 11 clientes
- Frontend: 13 páginas GED, todas roteadas em `/modulos/gestao-pessoas/ged/`
- Certidões: atualizando (última run: 2026-05-03, 6 certidões, 5 alertas)
- Celery Beat: 12 tasks agendadas

**O que está parado/com problema:**
- Onvio sync via API: todos os 5 últimos logs `error` (desde 2026-04-30)
- Onvio auth refresh: script existe, não agendado no crontab
- 98 documentos Onvio sem classificação de scope
- Alvará de Funcionamento vencido (fevereiro/2026)
