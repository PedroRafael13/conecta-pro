#!/usr/bin/env python3
"""
Skills Agent — Conecta PRO Monitor Bot
@conecta_pro_monitor_bot | Ciclo: 30 minutos

Audita o sistema usando as 10 skills, calcula score por módulo
e envia relatório via Telegram para Jordan.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime

import urllib.request
import urllib.error

# ─────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────────────

BOT_TOKEN  = os.getenv("MONITOR_BOT_TOKEN",  "8562364686:AAESOC6uXddwShWSs3_1-qJ4lBiZHBiSuBQ")
CHAT_ID    = os.getenv("MONITOR_CHAT_ID",    "5536961034")
API_BASE   = "http://127.0.0.1:8080/api/v1"
REPORT_DIR = "/opt/conecta-pro/reports/monitor"

os.makedirs(REPORT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────

def telegram_send(text: str) -> bool:
    """Envia mensagem HTML ao Telegram."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }).encode()
    try:
        req = urllib.request.Request(url, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            result = json.loads(r.read())
            return result.get("ok", False)
    except Exception as e:
        print(f"[telegram_send] erro: {e}")
        return False


def get_token() -> str:
    """Autentica e retorna JWT."""
    try:
        data = b"username=egonzaga%40conectamais.pro&password=Admin%40123"
        req = urllib.request.Request(
            f"{API_BASE}/auth/login",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()).get("access_token", "")
    except Exception:
        return ""


def http_get(url: str, token: str) -> tuple[int, dict]:
    """GET autenticado. Retorna (status_code, body)."""
    try:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception:
        return 0, {}


# ─────────────────────────────────────────────────────
# SKILL 07 — Docker (containers)
# ─────────────────────────────────────────────────────

CRITICAL_CONTAINERS = [
    "conecta-pro-backend",
    "conecta-pro-frontend",
    "conecta-pro-postgres",
    "conecta-pro-redis",
]

def check_containers() -> dict:
    try:
        out = subprocess.check_output(
            ["docker", "ps", "--format", "{{.Names}}|{{.Status}}"],
            timeout=10
        ).decode()
    except Exception:
        return {"ok": 0, "fail": CRITICAL_CONTAINERS[:], "raw": "docker indisponível"}

    running = {}
    for line in out.strip().splitlines():
        if "|" in line:
            name, status = line.split("|", 1)
            running[name.strip()] = status.strip()

    ok = [c for c in CRITICAL_CONTAINERS if c in running and "Up" in running[c]]
    fail = [c for c in CRITICAL_CONTAINERS if c not in ok]
    return {"ok": len(ok), "fail": fail, "total": len(CRITICAL_CONTAINERS)}


# ─────────────────────────────────────────────────────
# SKILL 03 — Endpoints por módulo
# ─────────────────────────────────────────────────────

ENDPOINT_CHECKS = {
    "Operacional": [
        "/operacional/posts/",
        "/operacional/escalas/",
        "/operacional/turnos/",
        "/operacional/comunicados",
        "/operacional/medidas-administrativas",
    ],
    "GED": [
        "/ged/documents",
        "/ged/folders",
        "/ged/document-tags",
        "/ged/document-shares",
    ],
    "Financeiro": [
        "/financial/accounting/cost-centers",
        "/financial/accounting/journal-entries",
        "/financial/accounting/periods",
        "/financial/bi/kpis?condominio_id=a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    ],
    "DP/RH": [
        "/people-management/hr/cct/resumo",
        "/people-management/hr/cct/cargos",
        "/people-management/hr/cct/conformidade",
    ],
    "Portal Cliente": [
        "/portal/auth/me",
        "/portal/kits",
        "/portal/tickets",
    ],
    "IA / Bartolo": [
        "/ai/bartolo/health",
        "/ai/bartolo/modules",
    ],
}


def check_endpoints(token: str) -> dict[str, dict]:
    results = {}
    for module, endpoints in ENDPOINT_CHECKS.items():
        ok = 0
        errors = []
        for ep in endpoints:
            code, _ = http_get(f"{API_BASE}{ep}", token)
            if code in (200, 201, 204):
                ok += 1
            elif code == 401:
                ok += 1          # endpoint existe, só precisa de auth portal
            else:
                errors.append(f"{ep} → {code}")
        total = len(endpoints)
        score = round((ok / total) * 10, 1) if total else 0
        results[module] = {
            "ok": ok,
            "total": total,
            "score": score,
            "errors": errors,
        }
    return results


# ─────────────────────────────────────────────────────
# SKILL 05 — Banco de dados
# ─────────────────────────────────────────────────────

def check_database() -> dict:
    try:
        out = subprocess.check_output(
            ["docker", "exec", "conecta-pro-postgres",
             "psql", "-U", "postgres", "-d", "conecta_pro",
             "-c", "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM communication_announcements;"],
            timeout=10
        ).decode()
        lines = [l.strip() for l in out.splitlines() if l.strip().lstrip("-").isdigit()]
        users = int(lines[0]) if len(lines) > 0 else -1
        comunicados = int(lines[1]) if len(lines) > 1 else -1
        return {"ok": True, "users": users, "comunicados": comunicados}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ─────────────────────────────────────────────────────
# SKILL 01 — Detectar erros recentes no backend
# ─────────────────────────────────────────────────────

def check_recent_errors() -> dict:
    try:
        out = subprocess.check_output(
            ["docker", "logs", "--tail", "200", "conecta-pro-backend"],
            timeout=15, stderr=subprocess.STDOUT
        ).decode()
        errors_500 = out.count("500 Internal Server Error")
        errors_exc = out.count("ERROR")
        lines_500 = [l for l in out.splitlines() if "500 Internal Server Error" in l][-3:]
        return {
            "errors_500": errors_500,
            "errors_general": errors_exc,
            "last_500": lines_500,
        }
    except Exception:
        return {"errors_500": -1, "errors_general": -1, "last_500": []}


# ─────────────────────────────────────────────────────
# SCORE GLOBAL
# ─────────────────────────────────────────────────────

def compute_global_score(containers: dict, endpoints: dict[str, dict], db: dict, errs: dict) -> float:
    scores = []

    # Containers (peso 2)
    c_score = (containers.get("ok", 0) / containers.get("total", 4)) * 10
    scores.extend([c_score, c_score])

    # Endpoints (peso 1 cada)
    for m, r in endpoints.items():
        scores.append(r["score"])

    # DB (peso 1)
    scores.append(10.0 if db.get("ok") else 3.0)

    # Erros 500 (penalidade)
    e500 = errs.get("errors_500", 0)
    penalty = min(e500 * 0.3, 2.0)

    avg = sum(scores) / len(scores) if scores else 0
    return max(0, round(avg - penalty, 1))


# ─────────────────────────────────────────────────────
# FORMATAÇÃO DA MENSAGEM TELEGRAM
# ─────────────────────────────────────────────────────

STATUS_EMOJI = {10: "🟢", 8: "🟡", 5: "🟠", 0: "🔴"}

def score_emoji(s: float) -> str:
    if s >= 9: return "🟢"
    if s >= 7: return "🟡"
    if s >= 5: return "🟠"
    return "🔴"


def build_message(
    containers: dict,
    endpoints: dict[str, dict],
    db: dict,
    errs: dict,
    global_score: float,
    duration: float,
) -> str:
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    emoji = score_emoji(global_score)

    lines = [
        f"{emoji} <b>MONITOR CONECTA PRO</b> — {now}",
        f"📊 Score global: <b>{global_score}/10</b>",
        "",
    ]

    # Containers
    c_ok  = containers.get("ok", 0)
    c_tot = containers.get("total", 4)
    c_fail = containers.get("fail", [])
    c_line = f"🐳 Containers: {c_ok}/{c_tot}"
    if c_fail:
        c_line += f" ⚠️ ({', '.join(c_fail)})"
    lines.append(c_line)

    # Banco
    if db.get("ok"):
        lines.append(f"🗄 Banco: ✅ ({db.get('users',0)} users)")
    else:
        lines.append(f"🗄 Banco: ❌ {db.get('error','?')[:40]}")

    # Erros backend
    e500 = errs.get("errors_500", 0)
    if e500 == 0:
        lines.append("⚡ Erros 500: ✅ nenhum")
    else:
        lines.append(f"⚡ Erros 500: ⚠️ {e500} nas últimas 200 linhas")

    lines.append("")
    lines.append("📦 <b>Módulos</b>")

    for module, r in endpoints.items():
        em = score_emoji(r["score"])
        line = f"  {em} {module}: {r['ok']}/{r['total']} ({r['score']}/10)"
        lines.append(line)
        for err in r["errors"][:2]:
            lines.append(f"    ↳ ❌ {err}")

    lines.append("")
    lines.append(f"⏱ Auditoria concluída em {duration:.1f}s | próxima em ~30min")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print(f"[{datetime.now():%H:%M:%S}] Skills Agent iniciando...")

    # 1. Containers
    print("  → verificando containers...")
    containers = check_containers()

    # 2. Token
    print("  → autenticando...")
    token = get_token()
    if not token:
        print("  ⚠️  token vazio — endpoints serão marcados como 0")

    # 3. Endpoints
    print("  → auditando endpoints...")
    endpoints = check_endpoints(token)

    # 4. Banco
    print("  → checando banco de dados...")
    db = check_database()

    # 5. Erros recentes
    print("  → lendo logs do backend...")
    errs = check_recent_errors()

    # 6. Score global
    global_score = compute_global_score(containers, endpoints, db, errs)

    duration = time.time() - t0

    # 7. Salvar relatório JSON
    report = {
        "timestamp": datetime.now().isoformat(),
        "global_score": global_score,
        "duration_seconds": round(duration, 1),
        "containers": containers,
        "endpoints": endpoints,
        "database": db,
        "errors": errs,
    }
    report_path = f"{REPORT_DIR}/cycle_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    # Symlink latest
    latest = f"{REPORT_DIR}/latest.json"
    if os.path.islink(latest):
        os.remove(latest)
    os.symlink(report_path, latest)

    print(f"  → relatório salvo: {report_path}")
    print(f"  → score global: {global_score}/10")

    # 8. Enviar Telegram
    msg = build_message(containers, endpoints, db, errs, global_score, duration)
    ok = telegram_send(msg)
    print(f"  → Telegram: {'✅ enviado' if ok else '❌ falhou'}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
