# OpenClaw - Integracao como Skill do Bartolo
# Conecta PRO - Prompt Completo de Implementacao
# Versao: 1.0 | Data: 01/02/2026

---

## 1. VISAO GERAL

O OpenClaw sera integrado ao Bartolo como uma **skill nativa**, permitindo que
o usuario interaja via chat natural ou comandos `/openclaw` para executar checks
de qualidade, visualizar relatorios, disparar deploys e monitorar o sistema.

### Fluxo de Interacao

```
[Usuario no Chat do Bartolo]
  │
  ├─ "/openclaw status"           → Skill direta (sem LLM)
  ├─ "/openclaw testes"           → Executa pytest via runner.py
  ├─ "/openclaw report"           → Mostra ultimo relatorio
  │
  ├─ "como esta a qualidade?"     → Intent detection → OpenClaw agent
  ├─ "roda os testes"             → Action detection → Preview → Confirma → Executa
  ├─ "qual a cobertura?"          → Data query → latest.json → Resposta natural
  │
  └─ [Pagina /modulos/openclaw]   → Dashboard visual com historico + botoes
```

---

## 2. ACESSO E PERMISSOES

### Usuario Autorizado (Fase 1)
- **Nome:** Jordan
- **Email:** jjesus@conectamais.pro
- **Nivel:** admin (controle total)
- **Permissao necessaria:** `openclaw:execute`, `openclaw:view`, `openclaw:deploy`

### Modelo de Permissoes

```python
# Novas permissoes no sistema RBAC
OPENCLAW_PERMISSIONS = {
    "openclaw:view":      "Visualizar relatorios e status do OpenClaw",
    "openclaw:execute":   "Executar checks (testes, lint, security, health)",
    "openclaw:deploy":    "Disparar deploy via OpenClaw",
    "openclaw:configure": "Alterar configuracoes do OpenClaw",
    "openclaw:daemon":    "Controlar modo daemon (start/stop)",
}

# Mapeamento de roles
ROLE_PERMISSIONS = {
    "admin":           ["openclaw:view", "openclaw:execute", "openclaw:deploy", "openclaw:configure", "openclaw:daemon"],
    "gerente":         ["openclaw:view", "openclaw:execute"],
    "supervisor":      ["openclaw:view"],
    "operador":        [],
}
```

---

## 3. SKILL: /openclaw

### Arquivo: `backend/modules/ai/bartolo/skills/openclaw_skill.py`

### Comandos Disponiveis

| Comando | Descricao | Permissao | Exemplo |
|---------|-----------|-----------|---------|
| `/openclaw status` | Status geral (ultimo ciclo) | view | "/openclaw status" |
| `/openclaw report` | Ultimo relatorio detalhado | view | "/openclaw report" |
| `/openclaw historico` | Ultimos N ciclos | view | "/openclaw historico 10" |
| `/openclaw testes` | Executar pytest backend | execute | "/openclaw testes" |
| `/openclaw testes-front` | Executar vitest frontend | execute | "/openclaw testes-front" |
| `/openclaw lint` | Executar ruff + eslint | execute | "/openclaw lint" |
| `/openclaw security` | Executar bandit scan | execute | "/openclaw security" |
| `/openclaw coverage` | Verificar cobertura | execute | "/openclaw coverage" |
| `/openclaw health` | Health check servicos | execute | "/openclaw health" |
| `/openclaw ciclo` | Ciclo completo (todos checks) | execute | "/openclaw ciclo" |
| `/openclaw deploy` | Disparar deploy producao | deploy | "/openclaw deploy" |
| `/openclaw config` | Ver/alterar configuracao | configure | "/openclaw config" |
| `/openclaw daemon` | Status/start/stop daemon | daemon | "/openclaw daemon start" |
| `/openclaw ajuda` | Lista de comandos | view | "/openclaw ajuda" |

---

## 4. ACTION TYPES

### Novos tipos de acao no sistema Bartolo

```python
class ActionType(str, Enum):
    # ... acoes existentes ...

    # OpenClaw - Quality
    OPENCLAW_RUN_TESTS = "openclaw_run_tests"
    OPENCLAW_RUN_LINT = "openclaw_run_lint"
    OPENCLAW_RUN_SECURITY = "openclaw_run_security"
    OPENCLAW_RUN_COVERAGE = "openclaw_run_coverage"
    OPENCLAW_RUN_HEALTH = "openclaw_run_health"
    OPENCLAW_RUN_FULL_CYCLE = "openclaw_run_full_cycle"

    # OpenClaw - Deploy
    OPENCLAW_DEPLOY_STAGING = "openclaw_deploy_staging"
    OPENCLAW_DEPLOY_PRODUCTION = "openclaw_deploy_production"

    # OpenClaw - Daemon
    OPENCLAW_DAEMON_START = "openclaw_daemon_start"
    OPENCLAW_DAEMON_STOP = "openclaw_daemon_stop"
```

---

## 5. PADROES DE DETECCAO (Regex)

### Para o Action Detector reconhecer linguagem natural

```python
OPENCLAW_PATTERNS = {
    ActionType.OPENCLAW_RUN_TESTS: [
        r"(?:roda|execut|faz)(?:r|ar?)?\s+(?:os?\s+)?test(?:e|es)",
        r"test(?:ar?|es?)\s+(?:o\s+)?(?:backend|sistema|codigo)",
        r"(?:como|qual)\s+(?:esta|e|sao)\s+(?:os?\s+)?test(?:e|es)",
    ],
    ActionType.OPENCLAW_RUN_LINT: [
        r"(?:roda|execut|faz)(?:r|ar?)?\s+(?:o\s+)?lint",
        r"verific(?:ar?|a)\s+(?:a\s+)?(?:formatacao|qualidade)\s+(?:do\s+)?codigo",
        r"(?:tem|ha)\s+(?:erros?\s+)?(?:de\s+)?lint",
    ],
    ActionType.OPENCLAW_RUN_SECURITY: [
        r"(?:scan|verific|analisa)(?:r|ar?)?\s+(?:a\s+)?seguranc(?:a|ça)",
        r"(?:roda|execut)(?:r|ar?)?\s+(?:o\s+)?(?:bandit|security)",
        r"(?:tem|ha)\s+vulnerabilidade",
    ],
    ActionType.OPENCLAW_RUN_COVERAGE: [
        r"(?:qual|como)\s+(?:esta|e)\s+(?:a\s+)?cobertura",
        r"verific(?:ar?|a)\s+(?:a\s+)?cobertura",
        r"coverage\s+(?:do\s+)?(?:backend|codigo)",
    ],
    ActionType.OPENCLAW_RUN_HEALTH: [
        r"(?:como|qual)\s+(?:esta|e|sao)\s+(?:os?\s+)?servic(?:o|os)",
        r"health\s*check",
        r"(?:esta|tudo)\s+(?:tudo\s+)?(?:ok|bem|funcionando|rodando)",
        r"status\s+(?:dos?\s+)?(?:servicos|containers|docker|sistema)",
    ],
    ActionType.OPENCLAW_RUN_FULL_CYCLE: [
        r"(?:roda|execut|faz)(?:r|ar?)?\s+(?:um\s+)?ciclo\s+(?:completo|completo|inteiro|full)",
        r"(?:roda|execut|faz)(?:r|ar?)?\s+(?:o\s+)?openclaw",
        r"(?:verific|analisa|checa)(?:r|ar?)?\s+tudo",
        r"qualidade\s+(?:geral|completa|do\s+sistema)",
    ],
    ActionType.OPENCLAW_DEPLOY_PRODUCTION: [
        r"(?:faz|execut|dispar)(?:r|er|ar?)?\s+(?:o\s+)?deploy",
        r"deploy(?:ar?)?\s+(?:para?\s+)?(?:prod|producao|production)",
        r"(?:atualiz|public)(?:ar?|a)\s+(?:o\s+)?(?:sistema|producao)",
    ],
}
```

---

## 6. INTEGRACAO COM SYSTEM PROMPT

### Adicionar ao system_prompt.py do Bartolo

```
SKILLS DE QUALIDADE E DEVOPS (OpenClaw):
- `/openclaw status` - Ver status geral do sistema (testes, lint, security, health)
- `/openclaw testes` - Rodar testes automatizados (pytest + vitest)
- `/openclaw lint` - Verificar qualidade do codigo (ruff + eslint)
- `/openclaw security` - Scan de seguranca (bandit)
- `/openclaw coverage` - Verificar cobertura de testes (meta: 60%)
- `/openclaw health` - Health check de todos os servicos
- `/openclaw ciclo` - Ciclo completo de qualidade
- `/openclaw report` - Ver ultimo relatorio
- `/openclaw deploy` - Deploy para producao (requer confirmacao)

O OpenClaw e o agente de qualidade autonomo do Conecta PRO.
Ele monitora continuamente: testes, lint, seguranca, cobertura,
saude dos servicos, espaco em disco e containers Docker.

Quando o usuario perguntar sobre qualidade, testes, bugs, deploy,
status do sistema ou cobertura, use os dados do OpenClaw para responder.

Relatorios ficam em: /opt/conecta-pro/reports/openclaw/latest.json
```

---

## 7. DATA CONNECTOR - Queries OpenClaw

### Novas queries no data_connector.py

```python
class QueryType(str, Enum):
    # ... queries existentes ...

    # OpenClaw
    OPENCLAW_STATUS = "openclaw_status"
    OPENCLAW_REPORT = "openclaw_report"
    OPENCLAW_HISTORY = "openclaw_history"
    OPENCLAW_TRENDS = "openclaw_trends"

# Deteccao de queries OpenClaw
OPENCLAW_QUERY_PATTERNS = {
    QueryType.OPENCLAW_STATUS: [
        r"(?:status|estado|situacao)\s+(?:do\s+)?(?:openclaw|qualidade|sistema)",
        r"como\s+(?:esta|anda)\s+(?:o\s+)?(?:sistema|qualidade|openclaw)",
    ],
    QueryType.OPENCLAW_REPORT: [
        r"(?:ultimo|mais\s+recente)\s+relatorio\s+(?:do\s+)?openclaw",
        r"relatorio\s+(?:de\s+)?qualidade",
    ],
    QueryType.OPENCLAW_HISTORY: [
        r"historico\s+(?:do\s+)?openclaw",
        r"(?:ultimos|recentes)\s+(?:\d+\s+)?ciclos",
    ],
}

# Execucao: le /opt/conecta-pro/reports/openclaw/latest.json
async def execute_openclaw_query(self, query_type):
    import json
    from pathlib import Path

    reports_dir = Path("/opt/conecta-pro/reports/openclaw")
    latest = reports_dir / "latest.json"

    if query_type == QueryType.OPENCLAW_STATUS:
        data = json.loads(latest.read_text())
        status = data["overall_status"].upper()
        counts = data["summary"]["status_counts"]
        duration = data["duration_seconds"]

        return f"""Status OpenClaw: {status}
Ultimo ciclo: {data['cycle_id']}
Duracao: {duration:.1f}s
Resultados: {counts['pass']} pass | {counts['fail']} fail | {counts['warn']} warn | {counts['skip']} skip | {counts['error']} error"""

    elif query_type == QueryType.OPENCLAW_HISTORY:
        reports = sorted(reports_dir.glob("cycle_*.json"), reverse=True)[:10]
        lines = ["Ultimos ciclos OpenClaw:", ""]
        for r in reports:
            data = json.loads(r.read_text())
            lines.append(f"  {data['cycle_id']} - {data['overall_status'].upper()} ({data['duration_seconds']:.1f}s)")
        return "\n".join(lines)
```

---

## 8. BACKEND API - Endpoint de Execucao

### Novo endpoint no bartolo_controller ou controller dedicado

```
POST /api/v1/openclaw/run
Body: { "check": "tests|lint|security|coverage|health|full" }
Response: { "cycle_id": "...", "status": "...", "checks": [...], "summary": {...} }

GET /api/v1/openclaw/report
Response: { ... latest.json content ... }

GET /api/v1/openclaw/history?limit=10
Response: { "reports": [...] }

GET /api/v1/openclaw/status
Response: { "daemon_running": bool, "last_cycle": {...}, "next_cycle_at": "..." }
```

### Execucao real via subprocess

```python
import subprocess, json
from pathlib import Path

RUNNER_PATH = "/opt/conecta-pro/scripts/openclaw/runner.py"

async def run_openclaw_check(check_group: str) -> dict:
    """Executa check do OpenClaw e retorna resultado."""
    cmd = ["python3", RUNNER_PATH]
    if check_group != "full":
        cmd.extend(["--only", check_group])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,
        cwd="/opt/conecta-pro"
    )

    # Le o relatorio gerado
    latest = Path("/opt/conecta-pro/reports/openclaw/latest.json")
    if latest.exists():
        return json.loads(latest.read_text())

    return {"error": result.stderr, "returncode": result.returncode}
```

---

## 9. FRONTEND - Pagina /modulos/openclaw

### Componentes da pagina

```
/modulos/openclaw/page.tsx
├── Header: "OpenClaw - Agente de Qualidade"
├── StatusCard: Status geral (PASS/FAIL/WARN) com cor
├── QuickActions: Botoes para cada check
│   ├── [Testes] [Lint] [Security] [Coverage] [Health] [Ciclo Completo]
│   └── Cada botao chama POST /api/v1/openclaw/run
├── LastReport: Tabela com checks do ultimo ciclo
│   ├── Nome | Status | Duracao | Mensagem
│   └── Colorido por status (verde/vermelho/amarelo)
├── TrendChart: Grafico de tendencia (Recharts)
│   └── Ultimos 30 ciclos: pass/fail/warn ao longo do tempo
├── HistoryTable: Tabela paginada de ciclos anteriores
│   └── Ciclo | Data | Status | Duracao | Acoes
└── BartoloChat: Widget do Bartolo integrado (module="openclaw")
    └── Pre-configurado com contexto do OpenClaw
```

---

## 10. SEGURANCA

### Controles implementados

1. **Autenticacao:** JWT existente do Conecta PRO (nao precisa MFA separado)
2. **Autorizacao:** Permissoes RBAC `openclaw:*` verificadas em cada endpoint
3. **Audit Trail:** Todas as execucoes registradas no audit log existente
4. **Rate Limiting:** Max 10 execucoes/hora por usuario (evitar abuso)
5. **Timeout:** 5 minutos max por execucao de ciclo
6. **Sandboxing:** OpenClaw so le/executa dentro de /opt/conecta-pro
7. **Deploy:** Requer confirmacao dupla (preview → confirmar) via Bartolo actions

### Log de atividades

```python
# Toda execucao do OpenClaw via Bartolo e registrada
await audit_log.record(
    action="openclaw_execute",
    user_id=current_user.id,
    resource="openclaw",
    details={
        "check_group": check_group,
        "cycle_id": cycle_id,
        "result_status": result["overall_status"],
        "triggered_by": "bartolo_skill",  # ou "api", "dashboard", "daemon"
    }
)
```

---

## 11. NOTIFICACOES E FEEDBACK

### Tempo real (durante execucao)

- Enquanto o check roda, o Bartolo mostra "Executando testes..." com spinner
- Ao concluir, mostra resultado formatado com cores

### Pos-execucao

- Se `fail` ou `error`: notifica via Discord/Slack (notify.sh)
- Relatorio salvo automaticamente em reports/openclaw/
- Historico acessivel via `/openclaw historico` ou dashboard

### Alertas automaticos (modo daemon)

- Daemon roda a cada 1h (configuravel)
- Se status muda de PASS para FAIL: notificacao imediata
- Se disco < 5GB: alerta critico
- Se container unhealthy: alerta

---

## 12. METAS E EVOLUCAO

### Fase 1 (Atual) - Skill + Dashboard
- [x] runner.py funcional com 10 checks
- [ ] Skill /openclaw no Bartolo (12 comandos)
- [ ] Action types + detection patterns
- [ ] Endpoint API /api/v1/openclaw/*
- [ ] Pagina frontend /modulos/openclaw
- [ ] Data connector queries (status, report, history)
- [ ] System prompt atualizado

### Fase 2 - Inteligencia
- [ ] Bartolo analisa relatorio e sugere acoes ("cobertura caiu, quer que eu identifique os modulos?")
- [ ] Comparacao entre ciclos ("piorou em testes desde ontem")
- [ ] Previsao de problemas baseado em tendencia
- [ ] Auto-fix para lint issues (ruff --fix automatico)

### Fase 3 - Automacao Total
- [ ] OpenClaw roda pre-commit validations antes de cada deploy
- [ ] Gate de qualidade: deploy bloqueado se coverage < 60%
- [ ] Rollback automatico se health check falha pos-deploy
- [ ] Integracao com GitHub Actions (trigger via API)
