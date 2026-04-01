# Passo Final — Auto-Auditoria: Monitor Unificado
**Data:** 2026-04-01
**Commits:** 9fcee18a + b318d236
**Branch:** feature/people-management-reorganization

---

## Checklist de Execução

| Passo | Tarefa | Status |
|-------|--------|--------|
| 1 | Mapear funcionalidades únicas do skills_agent | ✅ |
| 2 | Criar `orchestrator_unificado.py` | ✅ |
| 3 | Testar 3 modos (rapido / completo / heartbeat) | ✅ |
| 4 | Substituir crons antigos | ✅ |
| 5 | Desativar skills_agent.py | ✅ |
| 6 | Validar no Telegram | ✅ |
| 7 | Commit + push | ✅ |
| Fix | Cron rapido com caminho absoluto (sem cd) | ✅ |

---

## Diagnóstico: O Que Havia de Errado

### 4 sistemas rodando em paralelo (contradições garantidas):

| Sistema | Cron | Problema |
|---------|------|---------|
| `skills_agent.py` | fora do cron | Usava `egonzaga@conectamais.pro` — usuário DIFERENTE, score distinto |
| `orchestrator_geral.py` | `*/30` | Score correto mas sem containers/DB |
| `monitor_heartbeat.sh` | `0 */6` | Bash frágil, lia state file de outro sistema |
| `health_check.sh` | `*/5` | **Script não existia** — cron falhava silenciosamente há semanas |

---

## O Que Foi Criado

### `agents/orchestrator_unificado.py` (3 modos)

**Modo `rapido` — cron `*/5`:**
- Verifica 4 containers críticos + 6 módulos de endpoints
- Silencioso se score OK (sem spam)
- Alerta Telegram só em regressão (Δ ≥ 2.0) ou bug persistente (3+ ciclos)
- Integrado com `regression_detector.py`

**Modo `completo` — cron `*/30`:**
- Ciclo rápido primeiro
- 13 orquestradores dinâmicos com renovação automática de token
- `check_database()` — query direta ao PostgreSQL
- `check_recent_errors()` — contagem rápida de erros 500
- Score combinado: containers (peso×2) + endpoints + orquestradores
- Relatório JSON em `reports/modules/ciclo_geral_*.json`

**Modo `heartbeat` — cron `0 */6`:**
- Ciclo rápido primeiro
- CPU / RAM / Disco / Uptime
- PM2 status, Redis ping, Backend HTTP
- Estatísticas do `monitor_state.json` (ciclos/correções/regressões)
- Indicadores coloridos 🟢🟡🔴

### O que foi absorvido de cada sistema anterior

| Origem | Funcionalidade absorvida |
|--------|--------------------------|
| `skills_agent.py` | `check_containers()`, `check_endpoints()`, `check_database()`, `monitor_state` + `regression_detector` |
| `orchestrator_geral.py` | `_load_pyc`, `_injetar_token`, `_obter_token_com_retry`, 13 ORCHESTRATORS, `carregar_orquestrador()` |
| `monitor_heartbeat.sh` | PM2 status, Redis ping, infra metrics, leitura de `monitor_state.json` |
| `health_check.sh` | Substituído pelo modo `rapido` |

---

## Crons Finais

```cron
# */5  — containers + endpoints, silencioso se OK
*/5  * * * * MONITOR_BOT_TOKEN=... MONITOR_CHAT_ID=...
             python3 /opt/conecta-pro/agents/orchestrator_unificado.py rapido
             >> /opt/conecta-pro/logs/monitor_rapido.log 2>&1

# */30 — ciclo completo (13 módulos + banco)
*/30 * * * * cd /opt/conecta-pro && MONITOR_BOT_TOKEN=... MONITOR_CHAT_ID=...
             python3 agents/orchestrator_unificado.py completo
             >> logs/monitor_completo.log 2>&1

# 0/6  — heartbeat (infra + estatísticas)
0 */6 * * * cd /opt/conecta-pro && MONITOR_BOT_TOKEN=... MONITOR_CHAT_ID=...
             python3 agents/orchestrator_unificado.py heartbeat
             >> logs/monitor_heartbeat.log 2>&1
```

---

## Verificação Ao Vivo (15:11)

```
rapido    (cd /tmp): Score 10.0/10 | Containers 4/4 | Erros 0 | 0.4s  ✅
heartbeat:           Enviado ao Telegram ✅
completo:            Score 9.8/10 | 13 módulos | 52s → Telegram ✅
```

---

## skills_agent.py

**Status: DESATIVADO**
- Renomeado: `agents/skills_agent.py` → `agents/skills_agent.py.DESATIVADO`
- Não está no cron
- `orchestrator_geral.py` mantido como arquivo legado (não está no cron)
- `monitor_heartbeat.sh` mantido como arquivo legado (não está no cron)

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_PASSO_FINAL_MONITOR_UNIFICADO_2026-04-01.md ~/Downloads/
```
