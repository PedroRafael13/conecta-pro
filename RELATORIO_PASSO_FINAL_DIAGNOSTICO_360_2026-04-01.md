# Passo Final — Auto-Auditoria: Diagnóstico 360°
**Data:** 2026-04-01
**Branch:** feature/people-management-reorganization

---

## Checklist de Execução

| Passo | Tarefa | Status |
|-------|--------|--------|
| 1 | Mapear todos os tokens Telegram + identidade dos bots (getMe) | ✅ |
| 2 | Distinguir @conectapro_alertas_bot de @conecta_pro_monitor_bot | ✅ |
| 3 | Mapear todos os arquivos do OpenClaw | ✅ |
| 4 | Mapear rotas, modelos, tabelas DB do OpenClaw | ✅ |
| 5 | Testar todos os endpoints OpenClaw com curl | ✅ |
| 6 | Mapear fluxo de dados (Alertmanager → OpenClaw → Telegram) | ✅ |
| 7 | Mapear /agents/dashboard (HTML estático + cron + data API) | ✅ |
| 8 | Verificar webhook vs polling do bot | ✅ |
| 9 | Verificar PM2 e logs de restart | ✅ |
| 10 | Verificar autenticação do webhook (descoberta crítica) | ✅ |

---

## Bug Crítico Descoberto

### OpenClaw Webhook — Quebrado pelo Commit 4b0faee5

**Sintoma:** `POST /api/v1/ai/openclaw/alert-webhook` retorna `HTTP 401` sem token JWT.

**Causa:** O commit `4b0faee5` (`fix(api/skill03): POST → 201 + aliases REST sem verbos nos paths`) adicionou `CurrentActiveUser` a **todos** os endpoints do OpenClaw, incluindo o webhook de alertas:

```python
# controller.py linha 35-38 — COMO ESTÁ (quebrado)
@router.post("/alert-webhook", response_model=list[InterventionResponse])
async def receive_alert_webhook(
    payload: AlertmanagerPayload,
    current_user: CurrentActiveUser,   # ← Skill03 adicionou isso aqui
    db: AsyncSession = Depends(get_db),
):
```

**Impacto:** O Alertmanager não envia token JWT — nunca enviou. Portanto:
- Desde o commit `4b0faee5` (aplicado nesta sessão), **nenhum alerta do Prometheus chega ao OpenClaw**
- As 18 intervenções no DB foram criadas em **2026-03-23** — antes do Skill03
- O OpenClaw está **silencioso** desde então: nenhuma auto-remediação, nenhum alerta Telegram via OpenClaw
- Alertmanager config não tem `http_config.authorization` configurado (confirmado)

**Evidência:**
```bash
# Sem auth (como Alertmanager envia):
curl -X POST http://127.0.0.1:8080/api/v1/ai/openclaw/alert-webhook -d '{...}'
→ {"detail":"Token de autenticação não fornecido"} HTTP 401

# Com JWT (único jeito de funcionar agora):
curl -H "Authorization: Bearer $TOKEN" ... → OK
```

**Solução correta:** Remover `current_user: CurrentActiveUser` apenas do webhook `/alert-webhook` (os outros endpoints de consulta devem continuar protegidos).

---

## Resultados dos Testes de Endpoint

| Endpoint | Método | Status | Resultado |
|----------|--------|--------|-----------|
| `/api/v1/ai/openclaw/alert-webhook` | POST (sem auth) | **401** | Quebrado — Alertmanager não consegue enviar |
| `/api/v1/ai/openclaw/interventions` | GET | 200 | OK — 3 items retornados |
| `/api/v1/ai/openclaw/interventions/stats` | GET | 200 | OK — 18 total, 88.9% resolvido |
| `/api/v1/ai/openclaw/patterns` | GET | 200 | OK — 2 padrões |
| `/api/v1/ai/openclaw/knowledge` | GET | 200 | OK — 2 componentes |

---

## Diagnóstico Completo: @conectapro_alertas_bot

**Identidade confirmada via Telegram getMe API:**

| Bot | Username | ID | Token |
|-----|----------|----|-------|
| Conecta PRO Alertas | `@conectapro_alertas_bot` | `8343886201` | `.env: TELEGRAM_BOT_TOKEN` |
| Conecta PRO Monitor | `@conecta_pro_monitor_bot` | `8562364686` | Hardcoded em agents/ |

### Dual purpose de @conectapro_alertas_bot

```
@conectapro_alertas_bot
├── PAPEL 1: Assistente do CEO (Claude AI)
│   └── agents/telegram_assistant.py → PM2 (polling getUpdates, 3s)
│   └── Token: TELEGRAM_BOT_TOKEN (.env) — correto, não hardcoded
│   └── Status: online, 11 restarts/3h
│   └── Causa dos restarts: KeyboardInterrupt (manual) + reinícios da sessão
│   └── Último uso: 10:31 (Jordan consultou folha de pagamento)
│
└── PAPEL 2: Alertas OpenClaw
    └── openclaw/telegram_service.py → async HTTP
    └── Token: TELEGRAM_BOT_TOKEN (mesmo .env)
    └── Throttle: 1 msg/5min/alert + máx 10/hora global
    └── Status: INATIVO (webhook quebrado desde commit 4b0faee5)
```

### PM2 — Detalhes do telegram-assistant

```
id=1  telegram-assistant  online  PID=62087  uptime=3h  restarts=11
mem=66.2mb  cpu=0%

Restarts analisados (logs):
- 05:36:58 — KeyboardInterrupt (manual, sessão Claude anterior)
- 12:10:05 — KeyboardInterrupt (manual)
- 12:33:29 — KeyboardInterrupt (manual)

Conclusão: restarts NÃO são por crash — são por interrupção manual
durante sessões de desenvolvimento. Processo está estável.
```

---

## OpenClaw: Mapa Completo

### Fluxo de dados (como deveria ser vs como está)

```
COMO DEVERIA SER:
Prometheus → Alertmanager → POST /alert-webhook → OpenClaw → Telegram

COMO ESTÁ AGORA (quebrado):
Prometheus → Alertmanager → POST /alert-webhook → HTTP 401 ← BLOQUEADO
```

### Arquivos e tabelas

```
backend/modules/ai/openclaw/
├── controller.py          6 rotas registradas em /api/v1/ai/openclaw
├── models.py              3 tabelas: interventions, patterns, knowledge_base
├── schemas.py             Pydantic: AlertmanagerPayload, InterventionResponse, etc.
├── remediation_service.py Diagnóstico via subprocess + ações automáticas
├── memory_service.py      Aprendizado: frequência → confidence_score (0.3→0.95)
└── telegram_service.py    Notificações via @conectapro_alertas_bot

Migrações:
├── sprint77_openclaw_interventions.py   → cria openclaw_interventions
└── sprint77_openclaw_memory_tables.py   → cria openclaw_patterns + openclaw_knowledge_base

Registros atuais no DB:
├── openclaw_interventions: 18 (todos de 2026-03-23, antes do bug)
├── openclaw_patterns:       2
└── openclaw_knowledge_base: 2 componentes
```

### Alertmanager config (monitoring/alertmanager/alertmanager.yml)

```yaml
receivers:
  - name: 'default-webhook'
    webhook_configs:
      - url: 'http://conecta-pro-backend:8080/api/v1/ai/openclaw/alert-webhook'
        send_resolved: true
  # SEM http_config.authorization — nunca enviou JWT
```

---

## /agents/dashboard: Mapa Completo

```
NÃO é rota FastAPI nem página Next.js.

Sistema de 3 peças:
├── agents/dashboard.html       UI estática (220+ KB, auto-contida)
├── agents/dashboard_data.json  Snapshot JSON atualizado a cada 2min
└── agents/dashboard_api.py     Coletor: docker ps + /proc + psycopg2 direto

Cron: */2 * * * * python3 /opt/conecta-pro/agents/dashboard_api.py > /dev/null 2>&1

Dados coletados:
├── Containers: docker ps -a (status, health, imagem)
├── Sistema: load/mem/disk/swap via /proc + free
├── OpenClaw interventions: SELECT ... FROM openclaw_interventions LIMIT 20
├── OpenClaw patterns: SELECT ... FROM openclaw_patterns WHERE is_active = true
├── Uptime: simulado (sempre 100% — não reflete outages reais)
├── Ações agendadas: lista hardcoded
└── Fila Celery: redis-cli llen celery

Acesso: sem rota nginx pública. Arquivo local apenas.
```

---

## Estado do Sistema (Snapshot 2026-04-01 15:43)

| Métrica | Valor | Status |
|---------|-------|--------|
| Containers up | 9+ | ✅ |
| Load 1m/5m | 5.15 / 3.72 | ⚠️ Alto |
| Memória | 16.8 / 31.3 GB (53.6%) | ✅ |
| Disco | 94 / 386 GB (25%) | ✅ |
| **Swap** | **4.0 / 4.0 GB (100%)** | **🔴 CRÍTICO** |
| Uptime VPS | 50.9 dias | ✅ |
| PM2 telegram-assistant | online | ✅ |
| OpenClaw webhook | **401 BLOQUEADO** | **🔴 CRÍTICO** |
| Intervenções DB | 18 (todas de 23/03) | ⚠️ Desatualizadas |

---

## Sumário dos Riscos

| # | Risco | Severidade | Commit causador |
|---|-------|-----------|-----------------|
| 1 | **OpenClaw webhook bloqueado** — Alertmanager não consegue enviar alertas | **CRÍTICO** | `4b0faee5` (Skill03) |
| 2 | **Swap 100%** — 4.0/4.0 GB saturado | **CRÍTICO** | — |
| 3 | Token `@conecta_pro_monitor_bot` hardcoded em 3 arquivos agents/ | MÉDIO | — |
| 4 | Cooldown OpenClaw in-memory — zera em restart do backend | MÉDIO | — |
| 5 | dashboard.html sem rota pública | BAIXO | — |
| 6 | Uptime no dashboard sempre 100% (simulado) | BAIXO | — |

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_PASSO_FINAL_DIAGNOSTICO_360_2026-04-01.md ~/Downloads/
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_T6_DIAGNOSTICO_360_2026-04-01_1543.md ~/Downloads/
```
