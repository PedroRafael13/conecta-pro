#!/usr/bin/env python3
"""
CTO Monitor Bot — Bot Telegram bidirecional do CTO Autônomo.

Bot: @conecta_pro_monitor_bot (8562364686)
Jordan: TELEGRAM_CHAT_ID=5536961034

Comandos:
  /start       Boas-vindas
  /ajuda       Lista de comandos
  /status      Estado geral do sistema
  /tickets     Tickets abertos
  /ticket XXXX Detalhe de um ticket
  /sistema     Métricas do servidor
  /padroes     Padrões aprendidos
  /aprovado    Aprovar ação pendente
  /recusado    Recusar ação pendente

Linguagem natural: Redis caiu? Postgres lento? Celery parou?
"""
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# ─── Paths ────────────────────────────────────────────────────────────────────
PROJECT_DIR = Path("/opt/conecta-pro")
AGENTS_DIR  = PROJECT_DIR / "agents"
CTO_DIR     = AGENTS_DIR / "cto"
CORE_DIR    = AGENTS_DIR / "core"

sys.path.insert(0, str(CTO_DIR))
sys.path.insert(0, str(CORE_DIR))

# ─── Credenciais ──────────────────────────────────────────────────────────────
MONITOR_BOT_TOKEN = os.getenv(
    "MONITOR_BOT_TOKEN",
    "8562364686:AAESOC6uXddwShWSs3_1-qJ4lBiZHBiSuBQ",  # pragma: allowlist secret
)
JORDAN_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "5536961034"))

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CTO-BOT] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(CTO_DIR / "monitor_bot.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("cto_bot")

# ─── Estado global ────────────────────────────────────────────────────────────
_acao_pendente: Optional[dict] = None  # {"tipo", "cmd", "ticket_num", "conf"}
_last_update_id: int = 0


# ─── Telegram helpers ─────────────────────────────────────────────────────────

def _tg(method: str, payload: dict, timeout: int = 10) -> dict:
    """Chama API Telegram via curl."""
    import urllib.request, urllib.parse
    url = f"https://api.telegram.org/bot{MONITOR_BOT_TOKEN}/{method}"
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data,
                                  headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        logger.error(f"Telegram API error ({method}): {e}")
        return {}


def send(text: str, chat_id: int = JORDAN_CHAT_ID,
         keyboard: Optional[list] = None, parse_mode: str = "Markdown") -> bool:
    payload: dict = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }
    if keyboard:
        payload["reply_markup"] = {
            "keyboard": [[{"text": k} for k in row] for row in keyboard],
            "one_time_keyboard": True,
            "resize_keyboard": True,
        }
    r = _tg("sendMessage", payload)
    return r.get("ok", False)


def get_updates(offset: int = 0, timeout: int = 3) -> list:
    r = _tg("getUpdates", {"offset": offset, "timeout": timeout, "limit": 10})
    return r.get("result", [])


# ─── CTOBrain (lazy) ──────────────────────────────────────────────────────────
_brain = None

def get_brain():
    global _brain
    if _brain is None:
        try:
            from brain import CTOBrain
            _brain = CTOBrain()
        except Exception as e:
            logger.error(f"CTOBrain load error: {e}")
    return _brain


# ─── AutoRemediator (lazy) ────────────────────────────────────────────────────
_remediator = None

def get_remediator():
    global _remediator
    if _remediator is None:
        try:
            from auto_remediator import AutoRemediator
            _remediator = AutoRemediator()
        except Exception as e:
            logger.error(f"AutoRemediator load error: {e}")
    return _remediator


# ─── Handlers ─────────────────────────────────────────────────────────────────

def cmd_start(chat_id: int):
    send(
        "🤖 *CTO Autônomo Online*\n\n"
        "Olá Jordan! Estou monitorando a Conecta Mais 24h.\n\n"
        "Use /ajuda para ver os comandos disponíveis.",
        chat_id=chat_id,
    )


def cmd_ajuda(chat_id: int):
    send(
        "*Comandos disponíveis:*\n\n"
        "`/status` — Estado geral do sistema\n"
        "`/tickets` — Tickets abertos\n"
        "`/ticket CTO-0001` — Detalhe de um ticket\n"
        "`/sistema` — CPU, RAM, disco, swap\n"
        "`/padroes` — Padrões aprendidos\n"
        "`/diagnostico [tipo]` — Investigar causa raiz\n"
        "`/relatorio` — Relatório matinal agora\n"
        "`/aprender` — Atualizar conhecimento do banco\n"
        "`/anomalias` — Ver mudanças detectadas\n\n"
        "*Linguagem natural:*\n"
        "Apenas descreva o problema:\n"
        "_Redis caiu_, _Postgres lento_, _Celery parou_\n\n"
        "Quando eu propor uma ação, responda *sim* ou *não*.",
        chat_id=chat_id,
    )


def cmd_status(chat_id: int):
    brain = get_brain()
    if not brain:
        send("❌ CTOBrain indisponível.", chat_id=chat_id)
        return

    try:
        texto = brain.resumo_para_telegram()
        send(texto, chat_id=chat_id)
    except Exception as e:
        send(f"❌ Erro ao gerar status: {e}", chat_id=chat_id)


def cmd_tickets(chat_id: int):
    brain = get_brain()
    if not brain:
        send("❌ CTOBrain indisponível.", chat_id=chat_id)
        return

    abertos = brain.listar_tickets(status="aberto", limit=10)
    if not abertos:
        send("✅ Nenhum ticket aberto.", chat_id=chat_id)
        return

    linhas = [f"📋 *{len(abertos)} ticket(s) aberto(s):*\n"]
    for t in abertos:
        sev_emoji = {"critica": "🔴", "alta": "🟠", "media": "🟡", "baixa": "🟢"}.get(
            t.get("severidade", "media"), "⚪"
        )
        linhas.append(
            f"{sev_emoji} `{t['numero']}` — {t['titulo'][:50]}\n"
            f"   _Cat: {t.get('categoria', '?')} | {t['criado_em'][:10]}_"
        )
    send("\n".join(linhas), chat_id=chat_id)


def cmd_ticket(chat_id: int, numero: str):
    brain = get_brain()
    if not brain:
        send("❌ CTOBrain indisponível.", chat_id=chat_id)
        return

    numero = numero.upper().strip()
    ticket_file = CTO_DIR / "tickets" / f"{numero}.json"
    if not ticket_file.exists():
        send(f"❌ Ticket `{numero}` não encontrado.", chat_id=chat_id)
        return

    t = json.loads(ticket_file.read_text())
    sev_emoji = {"critica": "🔴", "alta": "🟠", "media": "🟡", "baixa": "🟢"}.get(
        t.get("severidade", "media"), "⚪"
    )
    status_emoji = "✅" if t["status"] == "resolvido" else "🔄"

    linhas = [
        f"*{t['numero']}* {sev_emoji}",
        f"*{t['titulo']}*\n",
        f"Status: {status_emoji} {t['status']}",
        f"Categoria: {t.get('categoria', '?')}",
        f"Criado: {t['criado_em'][:16].replace('T', ' ')}",
    ]
    if t.get("causa_raiz"):
        linhas.append(f"\n*Causa:* {t['causa_raiz']}")
    if t.get("solucao_proposta"):
        linhas.append(f"*Solução:* {t['solucao_proposta']}")
    if t.get("resolvido_em"):
        linhas.append(f"Resolvido: {t['resolvido_em'][:16].replace('T', ' ')}")

    hist = t.get("historico", [])[-3:]
    if hist:
        linhas.append(f"\n*Histórico ({len(t['historico'])} entradas):*")
        for h in hist:
            linhas.append(f"  • {h['timestamp'][:16].replace('T', ' ')} — {h['acao'][:60]}")

    send("\n".join(linhas), chat_id=chat_id)


def cmd_sistema(chat_id: int):
    def _r(cmd):
        try:
            return subprocess.run(cmd, shell=True, capture_output=True,
                                  text=True, timeout=10).stdout.strip()
        except Exception:
            return "?"

    load   = _r("cat /proc/loadavg | awk '{print $1, $2, $3}'")
    mem    = _r("free -b | awk '/^Mem:/ {printf \"%.1f/%.1f GB (%.0f%%)\", $3/1073741824, $2/1073741824, $3/$2*100}'")
    disk   = _r("df -h / | tail -1 | awk '{print $3\"/\"$2\" (\"$5\")\"}'")
    swap   = _r("free -b | awk '/^Swap:/ {if($2>0) printf \"%.1f/%.1f GB\", $3/1073741824, $2/1073741824; else print \"sem swap\"}'")
    uptime = _r("uptime -p")

    # Containers críticos
    cnames = ["conecta-pro-backend", "conecta-pro-postgres",
              "conecta-pro-redis", "conecta-pro-frontend"]
    container_lines = []
    for cn in cnames:
        st = _r(f"docker inspect --format '{{{{.State.Status}}}}' {cn} 2>/dev/null")
        emoji = "✅" if st == "running" else "❌"
        container_lines.append(f"  {emoji} `{cn.replace('conecta-pro-','')}` {st or 'N/A'}")

    send(
        f"💻 *Sistema — {datetime.now().strftime('%d/%m %H:%M')}*\n\n"
        f"Load: `{load}`\n"
        f"RAM:  `{mem}`\n"
        f"Disk: `{disk}`\n"
        f"Swap: `{swap}`\n"
        f"Up:   `{uptime}`\n\n"
        "*Containers:*\n" + "\n".join(container_lines),
        chat_id=chat_id,
    )


def cmd_padroes(chat_id: int):
    padroes_file = AGENTS_DIR / "knowledge" / "patterns_learned.json"
    if not padroes_file.exists():
        send("📭 Nenhum padrão aprendido ainda.", chat_id=chat_id)
        return

    try:
        data = json.loads(padroes_file.read_text())
    except Exception as e:
        send(f"❌ Erro ao ler padrões: {e}", chat_id=chat_id)
        return

    if not data:
        send("📭 Nenhum padrão aprendido ainda.", chat_id=chat_id)
        return

    linhas = [f"🧠 *{len(data)} Padrões Aprendidos:*\n"]
    for nome, p in sorted(data.items(), key=lambda x: x[1].get("confidence", 0), reverse=True)[:10]:
        conf = p.get("confidence", 0)
        bar  = "█" * int(conf / 20) + "░" * (5 - int(conf / 20))
        linhas.append(
            f"`{nome}`\n"
            f"  Conf: {bar} {conf:.0f}/100 | Ocorr: {p.get('occurrences', 0)}"
        )
        if p.get("preventive_command"):
            linhas.append(f"  Cmd: `{p['preventive_command'][:50]}`")

    send("\n".join(linhas), chat_id=chat_id)


def handle_natural_language(text: str, chat_id: int):
    """Diagnóstico de linguagem natural + proposta de ação."""
    global _acao_pendente

    brain = get_brain()
    remediator = get_remediator()

    if not brain:
        send("❌ CTOBrain indisponível para diagnóstico.", chat_id=chat_id)
        return

    diag = brain.diagnosticar(text)

    # Criar ticket
    ticket = brain.criar_ticket(
        titulo=text[:60],
        descricao=text,
        severidade=diag.get("urgencia", "media"),
        categoria="incidente",
        causa_raiz=diag.get("causa_raiz", ""),
        solucao_proposta=diag.get("solucao_recomendada", ""),
        auto_resolvido=False,
        requer_jordan=diag.get("requer_jordan", False),
    )

    urgencia = diag.get("urgencia", "media")
    urg_emoji = {"critica": "🔴", "alta": "🟠", "media": "🟡", "baixa": "🟢"}.get(urgencia, "⚪")

    msg_linhas = [
        f"{urg_emoji} *Diagnóstico — {ticket['numero']}*\n",
        f"*Causa:* {diag.get('causa_raiz', 'Não identificada')}",
        f"*Contexto:* {diag.get('contexto_negocio', '')}",
        f"*Solução:* {diag.get('solucao_recomendada', '')}",
    ]

    # Verificar ações disponíveis
    acoes = diag.get("acoes_possiveis", [])
    tipo = _inferir_tipo(text)

    pode_remediar = (
        remediator is not None
        and tipo is not None
        and remediator.pode_remediar(tipo)
        and not diag.get("requer_jordan", False)
    )

    if pode_remediar:
        _acao_pendente = {
            "tipo": tipo,
            "ticket": ticket["numero"],
            "conf": 70.0,
        }
        msg_linhas.append(
            f"\n🤔 *Posso executar a remediação automaticamente.*\n"
            f"Tipo: `{tipo}`\n"
            f"Confirma? Responda *sim* ou *não*"
        )
        send("\n".join(msg_linhas), chat_id=chat_id,
             keyboard=[["sim", "não"]])
    else:
        if acoes:
            msg_linhas.append("\n*Ações manuais sugeridas:*")
            for a in acoes[:3]:
                msg_linhas.append(f"  `{a}`")
        if diag.get("requer_jordan"):
            msg_linhas.append("\n⚠️ *Requer intervenção manual de Jordan.*")
        send("\n".join(msg_linhas), chat_id=chat_id)


def handle_aprovacao(aprovado: bool, chat_id: int):
    """Processa aprovação/recusa de ação pendente."""
    global _acao_pendente

    if not _acao_pendente:
        send("ℹ️ Nenhuma ação pendente no momento.", chat_id=chat_id)
        return

    acao = _acao_pendente
    _acao_pendente = None
    brain = get_brain()
    remediator = get_remediator()

    if not aprovado:
        send(f"✋ Ação recusada. Ticket `{acao['ticket']}` permanece aberto.", chat_id=chat_id)
        if brain:
            brain.atualizar_ticket(acao["ticket"], "Ação recusada por Jordan", "aberto")
        return

    send(f"⚙️ Executando remediação para `{acao['tipo']}`...", chat_id=chat_id)

    if not remediator:
        send("❌ AutoRemediator indisponível.", chat_id=chat_id)
        return

    resultado = remediator.remediar(acao["tipo"], confidence=acao["conf"])

    if resultado["sucesso"]:
        send(
            f"✅ *Remediação concluída!*\n"
            f"Tipo: `{acao['tipo']}`\n"
            f"Tempo: `{resultado.get('tempo_s', 0):.1f}s`\n"
            f"Saída: `{str(resultado.get('saida', ''))[:200]}`",
            chat_id=chat_id,
        )
        if brain:
            brain.atualizar_ticket(
                acao["ticket"],
                f"Remediação executada: {acao['tipo']}",
                "resolvido",
                resultado=str(resultado.get("saida", ""))[:200],
            )
    else:
        send(
            f"❌ *Remediação falhou*\n"
            f"Motivo: {resultado.get('motivo', 'erro desconhecido')}\n"
            f"Ticket `{acao['ticket']}` permanece aberto.",
            chat_id=chat_id,
        )


def _inferir_tipo(texto: str) -> Optional[str]:
    """Mapeia texto livre para tipo de remediação."""
    t = texto.lower()
    if "redis" in t:
        return "RedisDown"
    if any(k in t for k in ["swap", "memoria", "memory", "oom", "ram"]):
        return "SwapHigh"
    if "celery" in t:
        return "CeleryUnhealthy"
    if any(k in t for k in ["postgres", "pg ", "banco", "db "]):
        return "PostgresConnectionLost"
    if any(k in t for k in ["pm2", "frontend", "next"]):
        return "PM2ExcessiveRestarts"
    if any(k in t for k in ["disco", "disk", "espaço", "space"]):
        return "DiskSpaceLow"
    if any(k in t for k in ["cpu", "load", "lento", "slow"]):
        return "HighMemoryUsage"
    return None


# ─── Comandos Sprint 2 ───────────────────────────────────────────────────────

def cmd_diagnostico(chat_id: int, tipo: str):
    """Diagnóstico avançado sob demanda — correlaciona logs, commits e banco."""
    send("🔍 Investigando... aguarde.", chat_id=chat_id)
    brain = get_brain()
    if not brain:
        send("❌ CTOBrain indisponível.", chat_id=chat_id)
        return
    try:
        diag = brain.diagnosticar_avancado(tipo, contexto={"tipo": tipo})
        evidencias = diag.get("evidencias", [])
        msg = (
            f"🔍 *Diagnóstico: {tipo}*\n\n"
            f"*Causa raiz:* {diag.get('causa_raiz','?')[:150]}\n"
        )
        if evidencias:
            msg += "\n*Evidências:*\n"
            for e in evidencias[:3]:
                msg += f"  • {e[:80]}\n"
        acao = diag.get("acao_recomendada", "") or diag.get("solucao_recomendada", "")
        if acao:
            msg += f"\n💡 *Ação:* {acao[:120]}"
        conf = diag.get("confianca", 0)
        if conf:
            msg += f"\n📊 Confiança: {conf}%"
        if diag.get("requer_jordan"):
            msg += "\n⚠️ _Requer ação manual_"
        send(msg, chat_id=chat_id)
    except Exception as e:
        send(f"⚠️ Erro no diagnóstico: {e}", chat_id=chat_id)


def cmd_relatorio(chat_id: int):
    """Envia relatório matinal sob demanda."""
    send("📊 Gerando relatório...", chat_id=chat_id)
    try:
        import sys as _sys
        _sys.path.insert(0, str(CTO_DIR))
        from relatorio_matinal import gerar_relatorio
        relatorio = gerar_relatorio()
        send(relatorio, chat_id=chat_id)
    except Exception as e:
        send(f"⚠️ Erro ao gerar relatório: {e}", chat_id=chat_id)


def cmd_aprender(chat_id: int):
    """Força ciclo de aprendizado contínuo agora."""
    send("🧠 Aprendendo com o banco...", chat_id=chat_id)
    brain = get_brain()
    if not brain:
        send("❌ CTOBrain indisponível.", chat_id=chat_id)
        return
    try:
        resultado  = brain.executar_aprendizado()
        mudancas   = resultado.get("mudancas", [])
        snap_m     = resultado.get("snapshot", {}).get("metricas", {})
        func_ativ  = (snap_m.get("funcionarios") or {}).get("ativos", "?")
        msg = (
            f"✅ *Aprendizado concluído*\n\n"
            f"Snapshot salvo\n"
            f"Funcionários ativos: {func_ativ}\n"
            f"Mudanças detectadas: {len(mudancas)}"
        )
        if mudancas:
            msg += "\n\n*Mudanças:*"
            for m in mudancas[:4]:
                emoji = {"critica": "🔴", "alta": "⚠️"}.get(m["urgencia"], "ℹ️")
                msg += f"\n  {emoji} {m['mensagem']}"
        send(msg, chat_id=chat_id)
    except Exception as e:
        send(f"⚠️ Erro no aprendizado: {e}", chat_id=chat_id)


def cmd_anomalias(chat_id: int):
    """Lista mudanças e anomalias detectadas recentemente."""
    f = CTO_DIR / "memory" / "mudancas_detectadas.json"
    if not f.exists():
        send("ℹ️ Nenhuma anomalia registrada ainda.", chat_id=chat_id)
        return
    try:
        historico = json.loads(f.read_text())
        if not historico:
            send("✅ Sem anomalias registradas.", chat_id=chat_id)
            return
        recentes = historico[-5:]
        msg = "📈 *Anomalias recentes:*\n\n"
        for entry in recentes:
            ts = entry["timestamp"][:16].replace("T", " ")
            msg += f"_{ts}_\n"
            for m in entry["mudancas"][:3]:
                emoji = {"critica": "🔴", "alta": "⚠️"}.get(m["urgencia"], "ℹ️")
                msg += f"  {emoji} {m['mensagem']}\n"
            msg += "\n"
        send(msg, chat_id=chat_id)
    except Exception as e:
        send(f"⚠️ Erro: {e}", chat_id=chat_id)


# ─── Loop principal ───────────────────────────────────────────────────────────

def processar_update(update: dict):
    """Processa um update do Telegram."""
    msg = update.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text    = msg.get("text", "").strip()

    if not chat_id or not text:
        return

    # Segurança: só Jordan pode usar
    if chat_id != JORDAN_CHAT_ID:
        send("⛔ Acesso restrito.", chat_id=chat_id)
        logger.warning(f"Acesso negado para chat_id={chat_id}")
        return

    logger.info(f"Mensagem recebida: {text[:80]!r}")

    tl = text.lower().strip()

    # Aprovação de ação pendente
    if tl in ("sim", "s", "yes", "aprovado", "/aprovado"):
        handle_aprovacao(True, chat_id)
        return
    if tl in ("não", "nao", "n", "no", "recusado", "/recusado"):
        handle_aprovacao(False, chat_id)
        return

    # Comandos
    if tl.startswith("/start"):
        cmd_start(chat_id)
    elif tl.startswith("/ajuda") or tl.startswith("/help"):
        cmd_ajuda(chat_id)
    elif tl.startswith("/status"):
        cmd_status(chat_id)
    elif tl.startswith("/tickets"):
        cmd_tickets(chat_id)
    elif tl.startswith("/ticket"):
        parts = text.split(maxsplit=1)
        if len(parts) > 1:
            cmd_ticket(chat_id, parts[1])
        else:
            send("Uso: `/ticket CTO-0001`", chat_id=chat_id)
    elif tl.startswith("/sistema"):
        cmd_sistema(chat_id)
    elif tl.startswith("/padroes"):
        cmd_padroes(chat_id)
    elif tl.startswith("/diagnostico"):
        parts = text.split(maxsplit=1)
        tipo = parts[1] if len(parts) > 1 else "geral"
        cmd_diagnostico(chat_id, tipo)
    elif tl.startswith("/relatorio"):
        cmd_relatorio(chat_id)
    elif tl.startswith("/aprender"):
        cmd_aprender(chat_id)
    elif tl.startswith("/anomalias"):
        cmd_anomalias(chat_id)
    else:
        # Linguagem natural
        handle_natural_language(text, chat_id)


def run():
    global _last_update_id
    logger.info("CTO Monitor Bot iniciando...")

    # Notificação de startup
    brain = get_brain()
    if brain:
        try:
            resumo = brain.resumo_para_telegram()
            send(
                f"🚀 *CTO Autônomo — Sprint 2 Online*\n\n"
                f"{resumo}\n\n"
                f"Novos: /diagnostico /relatorio /aprender /anomalias\n"
                f"Use /ajuda para todos os comandos.",
            )
            logger.info("Startup notification enviada.")
        except Exception as e:
            logger.error(f"Startup notification error: {e}")
    else:
        send("🤖 CTO Monitor Bot online. CTOBrain indisponível — verificar logs.")

    logger.info(f"Polling getUpdates a cada 3s para chat_id={JORDAN_CHAT_ID}")

    while True:
        try:
            updates = get_updates(offset=_last_update_id + 1)
            for upd in updates:
                _last_update_id = upd["update_id"]
                processar_update(upd)
        except KeyboardInterrupt:
            logger.info("Bot encerrado por KeyboardInterrupt.")
            break
        except Exception as e:
            logger.error(f"Loop error: {e}")
        time.sleep(3)


if __name__ == "__main__":
    run()
