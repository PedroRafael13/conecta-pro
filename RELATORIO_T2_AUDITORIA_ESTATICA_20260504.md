# RELATÓRIO T2 — AUDITORIA ESTÁTICA
**Data:** 2026-05-04
**Sessão:** tmux-t2 | **Módulo:** auditoria (read-only)
**Branch:** feature/people-management-reorganization
**Início:** 01:45:17 | **Fim:** ~02:10

---

## MAPA: páginas em /modulos/

Total: **230 page.tsx** sob `frontend/src/app/modulos/`

Módulos presentes:
- agendador, analytics, area-cliente, assistente, automacoes, bi/dashboard
- campo (checkin, comunicados, monitoramento)
- configuracoes (sistema, feature-flags, integracoes, templates-notificacao, tenants)
- crm (clientes, comissoes, contatos, contratos, leads, oportunidades, precificacao, propostas)
- documentos (arquivos, kits, pastas)
- dp (admissao, aviso-previo, beneficios, contratos, documentos, esocial, ferias, folha, funcionarios, licencas, ponto, reembolsos, rescisao)
- empresas (dashboard, demonstrativos, liminares, migrador, obrigacoes, rentabilidade)
- equipamentos (comodatos, manutencoes, patrimonio)
- financeiro (agentes, banking, boletos, clientes, cobrancas, compras, conciliacao, contabilidade, contas-pagar, contas-receber, contratos, custeio, custos, dashboard, estoque, faturamento, fiscal, fluxo-caixa, fornecedores, inter, inter/pagamentos, nfse-entrada, orcamentos, precificacao, relatorios)
- fiscal (certidoes × 10 tipos, dctfweb, esocial, nfse, nfse-multi, reinf, sped)
- gestao-pessoas (ged × 13, ponto × 7, rh × 7, saude-ocupacional × 8, sst × 5)
- integracoes (api-keys, conectores, logs, solides, sync, webhooks)
- licitacoes (certidoes, contratos, disputas, documentos, editais, ia, oportunidades, propostas, resultados)
- marketing (brand-voice, campanhas, funil, lead-magnet)
- operacional (agentes, ai-command-center, alocacoes, banco-horas, campo, cobertura, colaboradores, comunicados, diaristas × 3, disciplinar, escalas × 4, ferias, kpi, mapa, medidas-administrativas, notificacoes, ocorrencias, postos, reembolsos, relatorios, rondas, substituicoes, turnos)
- portal (assinatura, beneficios, cct, contracheque, dados-pessoais, documentos, escalas, ferias, notificacoes, perfil, ponto, treinamentos)
- recrutamento (candidatos, candidaturas, entrevistas, vagas)
- reembolso (aprovacoes), relatorios (central, comercial, dashboards, financeiro, operacional)
- rh (avaliacoes, candidatos, carreira, certificados, clima, cursos, dashboard, entrevistas, ia, onboarding, treinamentos, turnover)
- saude-ocupacional (afastamentos, ajuda-medicamento, alertas, cat, epi, estabilidade, exames, riscos)
- seguranca (auditoria, consentimento, criptografia, esquecimento, mascaramento, pia-dpia)
- servicos (agendamentos, contratos, ordens), suprimentos

---

## ENDPOINTS BACKEND

Total: **3.492 rotas registradas**

Módulos carregados no startup:
- Auth, Users, Comercial (CRM + Clients + Bidding + Services)
- Operações (Operacional + Campo)
- Técnico (Equipment + Document Kits + Documents/OCR)
- GED (Certidões, Pessoas, Auto-Assemble)
- Financeiro (18 routers + Financial Overview + Dashboard + Cashflow/Forecast + BI + Custeio ABC + Precificação + Cobrança PIX + Conciliação Inter + MCP Financial)
- Fiscal/Contábil (Empresas + Fiscal + Government + Certidões + NF-e + NFS-e + Dashboard Fiscal)
- Inteligência (Analytics + Reports + Monitoring)
- Inter (D6 + D7 + Banking Payments)
- Gestão (Config + Audit + Notifications + Mobile + Workflows + Integrations + WhatsApp)
- People Management (DP + RH + Operations + Portal + GED)
- Client Portal, CCT 2026, GEDEON (3 routers), GDrive, Webhooks Inter, Jurídico Skills

**⚠️ OpenClaw:** `No module named 'modules.ai.openclaw'` — módulo ausente (não crítico)

---

## HEALTH BACKEND

```json
{"status":"healthy","app":"Conecta PRO","version":"2.0.0","environment":"production"}
```

---

## CONTADORES DE TABELAS PRINCIPAIS

| Tabela | Count | Status |
|--------|-------|--------|
| users | 55 | ✅ |
| employees | 58 | ✅ |
| clients | 11 | ✅ |
| contracts | 10 | ✅ |
| condominios | 11 | ✅ |
| posts (postos) | 10 | ✅ |
| shifts | 180 | ✅ |
| hr_payslips | 51 | ✅ |
| inter_transactions | 536 | ✅ |
| **inter_cobrancas** | **0** | ⚠️ suspeito |
| **inter_payments** | **0** | ⚠️ suspeito |
| leads | 11 | ✅ |
| employee_alocacoes | 47 | ✅ |
| onvio_documents | 534 | ✅ (subiu de 436) |

**⚠️ inter_cobrancas=0 e inter_payments=0** — inter_transactions tem 536 registros mas os módulos de cobrança/pagamento estão vazios. Provável: tudo passa direto por inter_transactions sem popular as tabelas derivadas.

---

## SMOKE TESTS ENDPOINTS GET (URLs do prompt)

| Status | Endpoint | Diagnóstico |
|--------|----------|-------------|
| 200 ✅ | /api/v1/clients?limit=1 | OK |
| 200 ✅ | /api/v1/crm/leads?limit=1 | OK |
| 200 ✅ | /api/v1/ged/certidoes | OK |
| 200 ✅ | /api/v1/financeiro/inter/saldo | OK |
| 200 ✅ | /api/v1/financeiro/inter/extrato/resumo?dias=30 | OK |
| 200 ✅ | /api/v1/financeiro/inter/cobrancas?limit=1 | OK |
| 200 ✅ | /api/v1/financeiro/inter/pix/recebidos?limit=1 | OK |
| 404 | /api/v1/people-management/employees?limit=1 | URL errada → real: `/api/v1/operacional/employees/` |
| 404 | /api/v1/contracts?limit=1 | URL errada → real: `/api/v1/crm/contracts` |
| 404 | /api/v1/operacional/postos?limit=1 | URL errada → real: não mapeada diretamente |
| 404 | /api/v1/operacional/escalas?limit=1 | URL errada → real: `/api/v1/people-management/operations/escalas/scales/` |
| 404 | /api/v1/operacional/shifts?limit=1 | URL errada → real: `/api/v1/operacional/shifts/` (com /) |
| 404 | /api/v1/payroll/payslips?limit=1 | URL errada → real: `/api/v1/people-management/hr/...` |
| 404 | /api/v1/financeiro/contas-pagar?limit=1 | Prefixo errado → real: `/api/v1/financial/payables` |
| 404 | /api/v1/financeiro/contas-receber?limit=1 | Prefixo errado → real: `/api/v1/financial/receivables` |
| 404 | /api/v1/financeiro/fluxo-caixa | Prefixo errado → real: `/api/v1/financial/cashflow/summary` |
| 404 | /api/v1/crm/precificacao?limit=1 | Módulo diferente → real: `/api/v1/financial/precificacao/simulador` |
| 404 | /api/v1/dashboard/stats | Não existe → real: `/api/v1/financial/dashboard` |

**Padrão sistêmico:** frontend usa `/financeiro/` mas backend registra `/financial/`. São 10 de 18 endpoints com URL incorreta no prompt — os endpoints EXISTEM, as URLs do prompt estão erradas.

---

## ENDPOINTS QUE RETORNAM 5xx OU 4xx INESPERADOS — BODY CAPTURADO

Todos os 404s retornam `{"detail":"Not Found"}` — sem stack trace, sem 5xx.
**Zero erros 5xx** em todos os 18 endpoints testados.

URLs reais confirmadas como 200:
```
GET /api/v1/operacional/employees/              → 200
GET /api/v1/crm/contracts                       → 200
GET /api/v1/people-management/operations/escalas/scales/ → 200
GET /api/v1/operacional/shifts/                 → 200
GET /api/v1/financial/precificacao/simulador    → 200
GET /api/v1/financial/payables                  → 200
GET /api/v1/financial/receivables               → 200
GET /api/v1/financial/cashflow/summary          → 200
GET /api/v1/financial/dashboard                 → 200
GET /api/v1/analytics/executive/dashboard       → 200
GET /api/v1/gedeon/kits/lote?mes_ref=04.2026   → 200
```

---

## SERVIÇOS DOCKER

| Container | Status | Porta |
|-----------|--------|-------|
| conecta-pro-backend | Up ~1h (healthy) | 8080 |
| conecta-pro-frontend | Up 13min (healthy) | 3001→3000 |
| conecta-pro-celery-beat | **health: starting** (16s) | — |
| conecta-pro-celery-batch | **health: starting** (18s) | — |
| conecta-pro-celery-integrations | Up 2 weeks (healthy) | — |
| conecta-pro-celery-priority | Up 2 weeks (healthy) | — |
| conecta-pro-celery-sefaz | Up 2 weeks (healthy) | — |
| conecta-pro-celery-nfse | Up 2 weeks (healthy) | — |
| conecta-pro-celery-operacional | Up 2 weeks (healthy) | — |
| conecta-pro-postgres | Up 2 weeks (healthy) | 5432 |
| conecta-pro-redis | Up 2 weeks (healthy) | 6379 |
| erp-prometheus, loki, alertmanager, node-exporter, redis-exporter, postgres-exporter | Up 2 weeks | — |

**⚠️ celery-beat e celery-batch:** `health: starting` — reiniciaram pouco antes da captura. Monitorar se voltam a healthy.

---

## LOGS RECENTES BACKEND (erros)

**Zero erros/exceptions** nos últimos 100 logs do container.

Apenas warning conhecido:
```
SOPHIA v2.0: Anthropic indisponível (Error code: 404 — model: claude-3-haiku-20240307)
usando dense fallback
```
**🔴 SOPHIA usa modelo obsoleto:** `claude-3-haiku-20240307` foi deprecated. Está em fallback silencioso — funcional mas sem IA real.

---

## CRON STATUS (rotinas D5+D6 mensal)

`crontab` não existe no container backend. Rotinas agendadas via **Celery Beat** (`celery_app.py`):

| Task | Schedule | Fila |
|------|----------|------|
| gedeon-kronos-diario | 06:00 diário | gov.batch |
| gedeon-themis-assinaturas | a cada 4h | gov.batch |
| gedeon-fiscal-verificar-certidoes | 07:00 diário | gov.batch |
| check-endpoints-5min | 5 min | gov.batch |
| check-certificates-6h | 6h | gov.batch |
| reprocess-failures-15min | 15 min | gov.batch |
| daily-report | 24h | gov.batch |
| fiscal-nfse-entrada-diario | 06:30 diário | gov.nfse |
| fiscal-nfe-entrada-2h | a cada 2h | gov.sefaz.nfe |
| solides-incremental-sync-all | 15 min | integrations |
| solides-health-check-all | 5 min | integrations |
| solides-process-webhooks | 30s | webhooks |
| solides-retry-failed-webhooks | 1h | integrations |
| solides-cleanup-sync-logs | 24h (manter 30d) | maintenance |
| solides-cleanup-webhook-logs | 24h (manter 7d) | maintenance |
| operacional-check-late-employees | 5 min | operacional |
| operacional-check-pending-approvals | 1h | operacional |
| operacional-expire-time-bank-daily | 24h (00:30) | operacional |
| operacional-shift-reminders-30min | 30 min | operacional |
| operacional-daily-coverage-report | 24h | operacional |
| bidding-sync-pncp-2h | 2h | gov.batch |
| bidding-check-certidoes-6h | 6h | gov.batch |
| bidding-sync-precos-daily | 24h | gov.batch |
| sst-check-expired-leaves-daily | 24h | operacional |
| sst-check-inss-pending-daily | 24h | operacional |

`scheduler_tasks` DB: 0 linhas (tabela não utilizada — Celery Beat é a fonte das rotinas).

---

## ARQUIVOS GRANDES SUSPEITOS EM /opt

| Path | Tamanho |
|------|---------|
| /opt/conecta-pro/frontend | 1.7G |
| /opt/conecta-pro/backend | 1.5G |
| /opt/conecta-pro/reports | 274M |
| /opt/conecta-pro/logs | 45M |
| /opt/conecta-pro/agents | 45M |
| /opt/conecta-pro/backups | 26M |
| /opt/conecta-pro/uploads | 16M |
| /opt/conecta-pro/docs | 16M |

**⚠️ reports: 274M** — crescimento esperado mas monitorar. Backend 1.5G inclui venv (~600MB), normal.

---

## ÚLTIMOS 10 COMMITS

```
f7df8b84 fix(inter-d7): auditoria regressão — TS2769 atob split undefined + relatório completo
56034cb0 docs: relatório regressão D7 UI [session: tmux-t1] [module: inter-d7]
88f85178 fix(inter-d7): regressão UI — ReferenceError fetchAudit temporal dead zone
7639bde5 fix(inter-d7): auditoria round 2 — loading/error audit + build ID + relatório
6ccdb1a2 fix(inter-d7): auditoria prompt — 5 itens faltantes corrigidos
e6e7af21 docs: relatório fix desvios D7 pagamentos Inter [session: tmux-t1] [module: inter-d7]
7f34afaa fix(inter-d7): header saldo+limite + tab audit log global Jordan (§52)
42b8ced1 fix(dashboard): agregação Cert A1 + auditoria 100% completa (§51.3 A2)
40e821cc docs(dashboard): auditoria 100% — §7 + docker cp static executado
4aee35ce docs(dashboard): relatório fix divergência dashboard vs /certidoes (§51)
```

---

## RESUMO EXECUTIVO — ACHADOS PRINCIPAIS

### 🔴 Crítico
1. **SOPHIA modelo obsoleto** — `claude-3-haiku-20240307` deprecated (HTTP 404 Anthropic). Funcionando em fallback sem IA.

### ⚠️ Atenção
2. **10/18 URLs do smoke test erradas** — padrão `/financeiro/` vs `/financial/` e paths deslocalizados. Backend OK, frontend pode ter hooks apontando para URLs erradas.
3. **inter_cobrancas=0, inter_payments=0** com inter_transactions=536 — tabelas de cobrança/pagamento não populadas.
4. **celery-beat e celery-batch** reiniciaram pouco antes da captura (health: starting).

### ✅ OK
5. Zero erros 5xx em todos os endpoints testados
6. Backend logs limpos
7. 3.492 rotas carregadas sem falha (exceto openclaw)
8. Todos os serviços principais healthy
9. Dados crescendo normalmente (onvio_documents: 436→534)
