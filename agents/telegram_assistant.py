#!/usr/bin/env python3
"""
Assistente Conecta PRO via Telegram + Claude API.

Polling do Telegram → Contexto do sistema → Claude Sonnet → Resposta.
Executa ações quando Claude identifica necessidade (tool use).
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

import anthropic
import httpx

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-20250514"
POLL_INTERVAL = 3  # segundos

# Ler do .env se não estiver no ambiente
ENV_FILE = "/opt/conecta-pro/.env"
if os.path.exists(ENV_FILE):
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            if key == "TELEGRAM_BOT_TOKEN" and not TELEGRAM_TOKEN:
                TELEGRAM_TOKEN = val
            elif key == "TELEGRAM_CHAT_ID" and not CHAT_ID:
                CHAT_ID = val
            elif key == "ANTHROPIC_API_KEY" and not ANTHROPIC_KEY:
                ANTHROPIC_KEY = val

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

PG_PASS = ""
if os.path.exists(ENV_FILE):
    with open(ENV_FILE) as f:
        for line in f:
            if line.startswith("POSTGRES_PASSWORD=") and "STAGING" not in line:
                PG_PASS = line.strip().split("=", 1)[1]
                break

# Memória de conversa (últimas 10 trocas)
conversation_history: list[dict] = []
MAX_HISTORY = 10

SYSTEM_PROMPT = """Voce e o Cerebro Executivo da Conecta Mais — o assistente pessoal de Jordan Jesus, CEO.

EMPRESA: Conecta Mais Seguranca e Tecnologia | Manaus-AM
CNPJ: 35.710.481/0001-03 | Lucro Real desde 01/2026
MRR: R$ 272.086,96 | 42 funcionarios ativos | 11 condominios

CLIENTES ATIVOS (mao de obra — recebem kit mensal):
- Ideal Flores: R$ 65.842/mes | retem ISS+INSS+CSLL
- Laranjeiras Village: R$ 42.544/mes | retem ISS+INSS+CSLL
- Mirante das Flores: R$ 42.255/mes | sem retencao
- Prime Arena: R$ 40.466/mes | retem INSS 11%
- Villa dos Passaros: R$ 37.338/mes | sem retencao
- Villa Dei Fiori: R$ 25.592/mes | sem retencao
- Michelangelo: R$ 8.346/mes | sem retencao
- Gelain: R$ 6.000/mes | portaria remota
SEM KIT: Parise Village, Green Hills (CFTV), Life Centro (ex)

BANCO: Inter (principal, PIX) | Cora (secundario)
Laranjeiras e Gelain pagam via BOLETO (nao PIX)

SEU PAPEL: Voce e um COO de IA. Fala direto, sem rodeios.
Tom executivo mas humano. Usa dados reais SEMPRE.
NUNCA inventa numeros. Se nao souber, diz claramente.

CAPACIDADES (use as tools):
- get_saldo_bancario: saldo atual das contas
- get_inadimplentes: clientes em atraso
- get_recebimentos: entradas da semana/mes
- get_folha_pagamento: custo com pessoal
- get_equipe: funcionarios ativos por cargo
- get_status_kits: kits mensais dos condominios
- get_nfse_status: notas fiscais do mes
- get_analise_cliente: dados de 1 cliente especifico
- gerar_kit_cliente: gera kit mensal automaticamente
- get_briefing: resumo executivo completo
- get_system_status: estado dos containers/infra

REGRAS:
- Maximo 15 linhas por resposta. Telegram = conciso.
- Use emojis com moderacao (1-2 por resposta).
- Sempre termine com dado acionavel ou pergunta.
- Valores: sempre R$ formatado com virgula.
- Nao invente dados — use APENAS o que as tools retornam.
- Para acoes destrutivas (restart, delete), confirme antes.
"""

# =============================================================================
# TOOLS — Ações que Claude pode executar
# =============================================================================

TOOLS = [
    # ── BUSINESS TOOLS (Cerebro Executivo) ──────────────────────────────────
    {
        "name": "get_saldo_bancario",
        "description": "Retorna saldo atual das contas bancarias (Inter + Cora). Use quando Jordan perguntar sobre saldo, dinheiro no banco, quanto tem na conta.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_inadimplentes",
        "description": "Lista clientes em atraso ou com vencimento proximo. Use quando perguntar: quem nao pagou, inadimplentes, vencidos, atrasados, pagou?",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_recebimentos",
        "description": "Mostra recebimentos (creditos) recentes no banco. Use quando perguntar: quanto recebi, entradas, recebimentos da semana.",
        "input_schema": {
            "type": "object",
            "properties": {"dias": {"type": "integer", "description": "Periodo em dias (padrao: 7)"}},
            "required": [],
        },
    },
    {
        "name": "get_folha_pagamento",
        "description": "Retorna custo da folha de pagamento do mes. Use quando perguntar: folha, salarios, custo pessoal, quanto pago.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_equipe",
        "description": "Retorna total de funcionarios ativos e distribuicao por cargo. Use quando perguntar: quantos funcionarios, minha equipe, headcount.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_status_kits",
        "description": "Retorna status dos kits documentais mensais de todos os condominios. Use quando perguntar: kits, documentos, kit mensal, enviou kit.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_nfse_status",
        "description": "Retorna status das NFS-e emitidas no mes. Use quando perguntar: notas fiscais, nfse, emiti nota.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_analise_cliente",
        "description": "Analise detalhada de um cliente especifico: contrato, pagamentos, status. Use quando mencionar nome de condominio (Ideal Flores, Mirante, Laranjeiras, etc).",
        "input_schema": {
            "type": "object",
            "properties": {"cliente": {"type": "string", "description": "Nome ou parte do nome do cliente"}},
            "required": ["cliente"],
        },
    },
    {
        "name": "gerar_kit_cliente",
        "description": "Gera automaticamente o kit mensal de um condominio com todos os PDFs. Use quando Jordan pedir: gera o kit, manda o kit, prepara documentos do X.",
        "input_schema": {
            "type": "object",
            "properties": {"cliente": {"type": "string", "description": "Nome do condominio"}},
            "required": ["cliente"],
        },
    },
    {
        "name": "get_briefing",
        "description": "Gera resumo executivo completo: saldo, inadimplencia, kits, equipe, nfse. Use quando pedir: resumo, como esta a empresa, briefing, overview.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    # ── DEVOPS TOOLS ────────────────────────────────────────────────────────
    {
        "name": "get_system_status",
        "description": "Retorna estado completo do sistema: containers Docker, CPU, RAM, disco, uptime.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "run_tests",
        "description": "Executa testes pytest em um módulo específico do backend. Módulos: operacional, financial, crm, hr, ged, clients, bidding, ai, government_integrations, notifications, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "module": {
                    "type": "string",
                    "description": "Nome do módulo para testar. Ex: 'financial', 'operacional', 'crm'",
                }
            },
            "required": ["module"],
        },
    },
    {
        "name": "get_logs",
        "description": "Retorna logs recentes de um container Docker.",
        "input_schema": {
            "type": "object",
            "properties": {
                "container": {
                    "type": "string",
                    "description": "Nome do container. Ex: 'conecta-pro-backend', 'conecta-pro-postgres'",
                },
                "lines": {"type": "integer", "description": "Número de linhas (padrão: 20)"},
            },
            "required": ["container"],
        },
    },
    {
        "name": "restart_container",
        "description": "Reinicia um container Docker. Use apenas quando Jordan confirmar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "container": {
                    "type": "string",
                    "description": "Nome do container para reiniciar.",
                }
            },
            "required": ["container"],
        },
    },
    {
        "name": "get_interventions",
        "description": "Lista intervenções recentes do OpenClaw (sistema de auto-remediação).",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Número de intervenções (padrão: 5)"},
            },
            "required": [],
        },
    },
    {
        "name": "force_backup",
        "description": "Executa backup do PostgreSQL imediatamente.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_coverage",
        "description": "Retorna relatório resumido de cobertura de testes do backend.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_alerts",
        "description": "Consulta alertas ativos no Prometheus/Alertmanager.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "run_command",
        "description": "Executa um comando shell arbitrário no servidor. Usar com cuidado.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Comando shell para executar."},
            },
            "required": ["command"],
        },
    },
]


# =============================================================================
# IMPLEMENTAÇÃO DAS TOOLS
# =============================================================================


def _run(cmd: str, timeout: int = 30) -> str:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip()[:3000]
    except subprocess.TimeoutExpired:
        return f"Timeout após {timeout}s"
    except Exception as e:
        return f"Erro: {e}"


def get_system_status() -> str:
    parts = []

    # Containers
    out = _run("docker ps --format '{{.Names}}\t{{.Status}}' | sort")
    parts.append(f"CONTAINERS:\n{out}")

    # Recursos
    disk = _run("df -h / | tail -1 | awk '{print $3\"/\"$2\" (\"$5\" usado)\"}'")
    mem = _run("free -h | awk '/^Mem:/ {print $3\"/\"$2\" (\"int($3/$2*100)\"%%)\"}'")
    load = _run("cat /proc/loadavg | awk '{print $1, $2, $3}'")
    uptime = _run("uptime -p")
    parts.append(f"DISCO: {disk}")
    parts.append(f"RAM: {mem}")
    parts.append(f"LOAD: {load}")
    parts.append(f"UPTIME: {uptime}")

    # Health
    health = _run("curl -sf http://localhost:8080/health 2>/dev/null")
    parts.append(f"API HEALTH: {health}")

    return "\n".join(parts)


def run_tests(module: str) -> str:
    # Mapear nomes comuns para paths
    module_paths = {
        "financial": "tests/test_financial*.py",
        "financeiro": "tests/test_financial*.py",
        "operacional": "tests/test_operacional*.py",
        "crm": "tests/test_crm*.py",
        "ged": "tests/test_ged*.py",
        "hr": "tests/test_hr*.py",
        "rh": "tests/test_hr*.py",
        "all": "tests/",
        "todos": "tests/",
    }
    path = module_paths.get(module.lower(), f"tests/test_{module}*.py")

    out = _run(
        f"docker exec conecta-pro-backend python3 -m pytest {path} -v --timeout=60 -q 2>&1 | tail -20",
        timeout=120,
    )
    return f"Testes '{module}':\n{out}"


def get_logs(container: str, lines: int = 20) -> str:
    # Sanitizar nome do container
    safe_name = "".join(c for c in container if c.isalnum() or c in "-_")
    out = _run(f"docker logs --tail {lines} {safe_name} 2>&1")
    return f"Logs {safe_name} (últimas {lines} linhas):\n{out}"


def restart_container(container: str) -> str:
    safe_name = "".join(c for c in container if c.isalnum() or c in "-_")
    out = _run(f"docker restart {safe_name} 2>&1", timeout=60)
    time.sleep(5)
    status = _run(f"docker inspect --format='{{{{.State.Status}}}}' {safe_name} 2>/dev/null")
    return f"Restart {safe_name}: {out}\nStatus após restart: {status}"


def get_interventions(limit: int = 5) -> str:
    out = _run(
        f"docker exec conecta-pro-postgres psql -U postgres -d conecta_pro -t -c "
        f"\"SELECT alert_name, status, severity, "
        f"to_char(created_at, 'DD/MM HH24:MI'), "
        f"left(diagnosis, 100) "
        f"FROM openclaw_interventions ORDER BY created_at DESC LIMIT {limit}\" 2>/dev/null"
    )
    return f"Últimas {limit} intervenções OpenClaw:\n{out}" if out.strip() else "Nenhuma intervenção registrada."


def force_backup() -> str:
    out = _run("/opt/conecta-pro/scripts/backup_database.sh 2>&1", timeout=120)
    return f"Backup executado:\n{out}"


def get_coverage() -> str:
    out = _run(
        "docker exec conecta-pro-backend python3 -m pytest tests/ --timeout=60 -q --co 2>&1 | tail -3",
        timeout=60,
    )
    total_tests = _run(
        "docker exec conecta-pro-backend python3 -m pytest tests/ --timeout=60 -q 2>&1 | tail -5",
        timeout=180,
    )
    return f"Cobertura:\n{out}\nResultado:\n{total_tests}"


def get_alerts() -> str:
    out = _run("curl -sf http://localhost:9093/api/v2/alerts 2>/dev/null")
    if not out or out == "[]":
        return "Nenhum alerta ativo no Alertmanager."
    try:
        alerts = json.loads(out)
        lines = []
        for a in alerts[:10]:
            name = a.get("labels", {}).get("alertname", "?")
            severity = a.get("labels", {}).get("severity", "?")
            status = a.get("status", {}).get("state", "?")
            lines.append(f"  {severity}: {name} ({status})")
        return "Alertas ativos:\n" + "\n".join(lines)
    except json.JSONDecodeError:
        return f"Alertas (raw):\n{out[:1000]}"


def run_command(command: str) -> str:
    # Bloquear comandos perigosos
    dangerous = ["rm -rf /", "mkfs", "dd if=", ":(){ :|:&", "shutdown", "reboot", "halt"]
    for d in dangerous:
        if d in command:
            return f"BLOQUEADO: comando perigoso detectado ({d})"
    return _run(command, timeout=30)


# =============================================================================
# BUSINESS TOOLS — Cerebro Executivo
# =============================================================================

DB_CMD = f'docker exec conecta-pro-postgres psql -U postgres -d conecta_pro -t -c'


def get_saldo_bancario() -> str:
    out = _run(f"""{DB_CMD} "SELECT bank_name, account_type, current_balance FROM bank_accounts WHERE status IN ('ativa','ativo') ORDER BY current_balance DESC;" """)
    total = _run(f"""{DB_CMD} "SELECT COALESCE(SUM(current_balance), 0) FROM bank_accounts WHERE status IN ('ativa','ativo');" """)
    return f"SALDO BANCARIO:\n{out}\nTOTAL: R$ {total.strip()}"


def get_inadimplentes() -> str:
    vencidos = _run(f"""{DB_CMD} "SELECT c.name, ra.gross_value, ra.due_date, ra.status FROM receivable_accounts ra LEFT JOIN clients c ON ra.customer_id = c.id WHERE ra.status IN ('pendente','overdue','vencido') AND ra.due_date < CURRENT_DATE ORDER BY ra.due_date LIMIT 10;" """)
    vencendo = _run(f"""{DB_CMD} "SELECT c.name, ra.gross_value, ra.due_date FROM receivable_accounts ra LEFT JOIN clients c ON ra.customer_id = c.id WHERE ra.status = 'pendente' AND ra.due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 7 ORDER BY ra.due_date LIMIT 10;" """)
    total = _run(f"""{DB_CMD} "SELECT COALESCE(SUM(ra.gross_value), 0) FROM receivable_accounts ra WHERE ra.status IN ('pendente','overdue','vencido') AND ra.due_date < CURRENT_DATE;" """)
    result = f"VENCIDOS:\n{vencidos if vencidos.strip() else '  Nenhum!'}\n\nVENCENDO EM 7 DIAS:\n{vencendo if vencendo.strip() else '  Nenhum!'}\n\nTOTAL EM RISCO: R$ {total.strip()}"
    return result


def get_recebimentos(dias: int = 7) -> str:
    out = _run(f"""{DB_CMD} "SELECT description, amount, transaction_date FROM bank_transactions WHERE transaction_type IN ('credito','credit','entrada') AND transaction_date >= CURRENT_DATE - {dias} ORDER BY transaction_date DESC LIMIT 15;" """)
    total = _run(f"""{DB_CMD} "SELECT COALESCE(SUM(amount), 0) FROM bank_transactions WHERE transaction_type IN ('credito','credit','entrada') AND transaction_date >= CURRENT_DATE - {dias};" """)
    return f"RECEBIMENTOS ULTIMOS {dias} DIAS:\n{out if out.strip() else '  Nenhum recebimento.'}\n\nTOTAL: R$ {total.strip()}"


def get_folha_pagamento() -> str:
    out = _run(f"""{DB_CMD} "SELECT COUNT(*) as func, COALESCE(SUM(salario_base), 0) as bruta FROM employees WHERE is_active = true;" """)
    encargos = _run(f"""{DB_CMD} "SELECT ROUND(SUM(salario_base) * 0.08, 2) as fgts, ROUND(SUM(salario_base) * 0.20, 2) as inss_patr FROM employees WHERE is_active = true;" """)
    return f"FOLHA DE PAGAMENTO:\nFuncionarios + Salario Bruto: {out}\nEncargos (FGTS 8% + INSS 20%): {encargos}"


def get_equipe() -> str:
    total = _run(f"""{DB_CMD} "SELECT COUNT(*) FROM employees WHERE is_active = true;" """)
    por_cargo = _run(f"""{DB_CMD} "SELECT cargo, COUNT(*) FROM employees WHERE is_active = true GROUP BY cargo ORDER BY COUNT(*) DESC LIMIT 10;" """)
    return f"EQUIPE: {total.strip()} funcionarios ativos\n\nPOR CARGO:\n{por_cargo}"


def get_status_kits() -> str:
    out = _run(f"""{DB_CMD} "SELECT g.name, k.status, k.total_documents, k.completion_percentage FROM ged_document_kits k JOIN ged_clients g ON g.id::text = k.client_id::text WHERE k.reference_month >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') ORDER BY k.reference_month DESC, g.name LIMIT 15;" """)
    total = _run(f"""{DB_CMD} "SELECT COUNT(*) FROM ged_document_kits WHERE reference_month >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month');" """)
    return f"KITS MENSAIS ({total.strip()} total):\n{out}"


def get_nfse_status() -> str:
    out = _run(f"""{DB_CMD} "SELECT tomador_razao_social, numero_nfse, valor_servicos, status FROM nfses WHERE data_competencia >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') AND active = true ORDER BY data_competencia DESC, valor_servicos DESC LIMIT 15;" """)
    totais = _run(f"""{DB_CMD} "SELECT COUNT(*), COALESCE(SUM(valor_servicos), 0) FROM nfses WHERE data_competencia >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') AND active = true;" """)
    return f"NFS-e RECENTES:\n{out}\n\nTOTAIS (qtd | valor): {totais}"


def get_analise_cliente(cliente: str) -> str:
    palavra = cliente.upper().split()[0] if cliente else "IDEAL"
    contrato = _run(f"""{DB_CMD} "SELECT c.name, c.document_number, ct.monthly_value, ct.status FROM contracts ct JOIN clients c ON ct.client_id = c.id WHERE UPPER(c.name) LIKE '%{palavra}%' AND ct.is_active = true LIMIT 3;" """)
    recebimentos = _run(f"""{DB_CMD} "SELECT bt.description, bt.amount, bt.transaction_date FROM bank_transactions bt WHERE UPPER(bt.description) LIKE '%{palavra}%' AND bt.transaction_type IN ('credito','credit','entrada') ORDER BY bt.transaction_date DESC LIMIT 5;" """)
    nfse = _run(f"""{DB_CMD} "SELECT numero_nfse, valor_servicos, data_competencia, status FROM nfses WHERE UPPER(tomador_razao_social) LIKE '%{palavra}%' AND active = true ORDER BY data_competencia DESC LIMIT 5;" """)
    return f"ANALISE CLIENTE '{cliente}':\n\nCONTRATO:\n{contrato}\n\nRECEBIMENTOS:\n{recebimentos if recebimentos.strip() else '  Nenhum encontrado.'}\n\nNFS-e:\n{nfse if nfse.strip() else '  Nenhuma.'}"


def gerar_kit_cliente(cliente: str) -> str:
    palavra = cliente.upper().split()[0] if cliente else ""
    if not palavra:
        return "Qual condominio? Tenho: Ideal Flores, Laranjeiras, Mirante, Prime Arena, Villa Passaros, Villa Dei Fiori, Michelangelo, Gelain"
    kit_id = _run(f"""{DB_CMD} "SELECT k.id FROM ged_document_kits k JOIN ged_clients g ON g.id::text = k.client_id::text WHERE UPPER(g.name) LIKE '%{palavra}%' ORDER BY k.reference_month DESC LIMIT 1;" """).strip()
    if not kit_id:
        return f"Kit nao encontrado para '{cliente}'. Verifique o nome do condominio."
    token = _run("""curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d "username=jjesus@conectamais.pro&password=Jordan0612" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])" """)
    result = _run(f"""curl -sf -X POST "http://127.0.0.1:8080/api/v1/ged/kit-real/{kit_id}/gerar" -H "Authorization: Bearer {token}" """, timeout=60)
    return f"KIT GERADO para '{cliente}':\nkit_id: {kit_id}\n{result[:500]}"


def get_briefing() -> str:
    token = _run("""curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d "username=jjesus@conectamais.pro&password=Jordan0612" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])" """)
    result = _run(f"""curl -sf "http://127.0.0.1:8080/api/v1/ai/briefing/diario" -H "Authorization: Bearer {token}" """, timeout=30)
    return f"BRIEFING EXECUTIVO:\n{result[:3000]}"


TOOL_FUNCTIONS = {
    # Business
    "get_saldo_bancario": lambda **_: get_saldo_bancario(),
    "get_inadimplentes": lambda **_: get_inadimplentes(),
    "get_recebimentos": lambda dias=7, **_: get_recebimentos(int(dias)),
    "get_folha_pagamento": lambda **_: get_folha_pagamento(),
    "get_equipe": lambda **_: get_equipe(),
    "get_status_kits": lambda **_: get_status_kits(),
    "get_nfse_status": lambda **_: get_nfse_status(),
    "get_analise_cliente": lambda cliente="", **_: get_analise_cliente(cliente),
    "gerar_kit_cliente": lambda cliente="", **_: gerar_kit_cliente(cliente),
    "get_briefing": lambda **_: get_briefing(),
    # DevOps
    "get_system_status": lambda **_: get_system_status(),
    "run_tests": lambda module="all", **_: run_tests(module),
    "get_logs": lambda container="conecta-pro-backend", lines=20, **_: get_logs(container, int(lines)),
    "restart_container": lambda container="", **_: restart_container(container),
    "get_interventions": lambda limit=5, **_: get_interventions(int(limit)),
    "force_backup": lambda **_: force_backup(),
    "get_coverage": lambda **_: get_coverage(),
    "get_alerts": lambda **_: get_alerts(),
    "run_command": lambda command="", **_: run_command(command),
}


# =============================================================================
# TELEGRAM API
# =============================================================================


def telegram_get_updates(offset: int = 0) -> list[dict]:
    try:
        r = httpx.get(
            f"{TELEGRAM_API}/getUpdates",
            params={"offset": offset, "timeout": 3, "allowed_updates": json.dumps(["message"])},
            timeout=10,
        )
        data = r.json()
        if data.get("ok"):
            return data.get("result", [])
    except Exception as e:
        log(f"Erro ao buscar updates: {e}")
    return []


def telegram_send(chat_id: str, text: str) -> bool:
    # Telegram limita a 4096 chars
    if len(text) > 4000:
        text = text[:3997] + "..."
    try:
        r = httpx.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=10,
        )
        if not r.json().get("ok"):
            # Retry sem Markdown se falhou (chars especiais)
            httpx.post(
                f"{TELEGRAM_API}/sendMessage",
                json={"chat_id": chat_id, "text": text},
                timeout=10,
            )
        return True
    except Exception as e:
        log(f"Erro ao enviar mensagem: {e}")
        return False


def telegram_send_typing(chat_id: str):
    try:
        httpx.post(
            f"{TELEGRAM_API}/sendChatAction",
            json={"chat_id": chat_id, "action": "typing"},
            timeout=5,
        )
    except Exception:
        pass


# =============================================================================
# CLAUDE API
# =============================================================================

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)


def ask_claude(user_message: str) -> str:
    """Envia mensagem para Claude com tools e contexto de conversa."""
    global conversation_history

    # Adicionar mensagem do usuário ao histórico
    conversation_history.append({"role": "user", "content": user_message})

    # Manter apenas últimas MAX_HISTORY mensagens
    if len(conversation_history) > MAX_HISTORY * 2:
        conversation_history = conversation_history[-(MAX_HISTORY * 2) :]

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=conversation_history,
        )
    except Exception as e:
        error_msg = f"Erro na Claude API: {e}"
        log(error_msg)
        return error_msg

    # Processar resposta — pode ter tool_use
    return _process_response(response)


def _process_response(response) -> str:
    """Processa resposta do Claude, executando tools se necessário."""
    global conversation_history

    final_text = []
    tool_results = []

    for block in response.content:
        if block.type == "text":
            final_text.append(block.text)
        elif block.type == "tool_use":
            tool_name = block.name
            tool_input = block.input
            tool_id = block.id

            log(f"Executando tool: {tool_name}({json.dumps(tool_input, ensure_ascii=False)[:100]})")

            # Executar a tool
            func = TOOL_FUNCTIONS.get(tool_name)
            if func:
                try:
                    result = func(**tool_input)
                except Exception as e:
                    result = f"Erro ao executar {tool_name}: {e}"
            else:
                result = f"Tool '{tool_name}' não encontrada."

            tool_results.append({"type": "tool_result", "tool_use_id": tool_id, "content": result})

    # Se houve tool_use, enviar resultados de volta ao Claude
    if tool_results:
        # Adicionar assistant message com tool_use ao histórico
        conversation_history.append({"role": "assistant", "content": response.content})
        conversation_history.append({"role": "user", "content": tool_results})

        try:
            follow_up = client.messages.create(
                model=MODEL,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=conversation_history,
            )
            # Processar recursivamente (Claude pode chamar mais tools)
            return _process_response(follow_up)
        except Exception as e:
            log(f"Erro no follow-up: {e}")
            return "\n".join(final_text) + f"\n\n(Erro no follow-up: {e})"

    # Resposta final sem tool_use
    assistant_text = "\n".join(final_text)
    conversation_history.append({"role": "assistant", "content": assistant_text})
    return assistant_text


# =============================================================================
# MAIN LOOP
# =============================================================================


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def main():
    log("Assistente Conecta PRO iniciando...")
    log(f"Telegram Bot: ...{TELEGRAM_TOKEN[-8:]}")
    log(f"Chat ID autorizado: {CHAT_ID}")
    log(f"Claude model: {MODEL}")

    if not TELEGRAM_TOKEN or not CHAT_ID or not ANTHROPIC_KEY:
        log("ERRO: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID e ANTHROPIC_API_KEY são obrigatórios")
        sys.exit(1)

    offset = 0

    # Notificar que está online
    telegram_send(CHAT_ID, "🟢 Assistente Conecta PRO online. Como posso ajudar?")
    log("Online. Aguardando mensagens...")

    while True:
        try:
            updates = telegram_get_updates(offset)

            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = str(message.get("chat", {}).get("id", ""))
                text = message.get("text", "")
                sender = message.get("from", {}).get("first_name", "?")

                if not text:
                    continue

                # Verificar autorização
                if chat_id != CHAT_ID:
                    log(f"Mensagem ignorada de chat_id={chat_id} ({sender})")
                    telegram_send(chat_id, "⛔ Acesso não autorizado.")
                    continue

                log(f"Jordan: {text[:100]}")

                # Indicador de digitação
                telegram_send_typing(chat_id)

                # Processar com Claude
                response = ask_claude(text)

                # Enviar resposta
                telegram_send(chat_id, response)
                log(f"Resposta: {response[:80]}...")

        except KeyboardInterrupt:
            log("Encerrando...")
            telegram_send(CHAT_ID, "🔴 Assistente Conecta PRO desligando.")
            break
        except Exception as e:
            log(f"Erro no loop: {e}")
            time.sleep(5)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
