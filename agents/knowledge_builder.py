#!/usr/bin/env python3
"""
Knowledge Builder — Conecta PRO Multi-Agent System

Mapeia TODOS os 46 modulos do backend, containers, integracoes externas,
dependencias e trafego. Gera agent_knowledge_base.json.

Uso:
    python3 agents/knowledge_builder.py              # Build completo
    python3 agents/knowledge_builder.py --discover   # Apenas containers
    python3 agents/knowledge_builder.py --traffic    # Apenas trafego
    python3 agents/knowledge_builder.py --modules    # Apenas modulos
"""

import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path("/opt/conecta-pro")
BACKEND_DIR = PROJECT_DIR / "backend"
MODULES_DIR = BACKEND_DIR / "modules"
KB_FILE = PROJECT_DIR / "agent_knowledge_base.json"
NGINX_LOG = Path("/var/log/nginx/access.log")


def run(cmd: str, timeout: int = 30) -> str:
    try:
        result = subprocess.run(  # noqa: S602  # nosec B602
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, Exception):
        return ""


# =============================================================================
# CONTAINER DISCOVERY
# =============================================================================


def discover_containers() -> list[dict]:
    raw = run("docker ps -a --format '{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}'")
    if not raw:
        return []

    containers = []
    roles = {
        "postgres": "database", "redis": "cache", "backend": "api",
        "frontend": "frontend", "celery-beat": "scheduler", "celery": "worker",
        "flower": "monitor", "prometheus": "monitoring", "grafana": "monitoring",
        "loki": "logging", "promtail": "logging", "alertmanager": "alerting",
        "exporter": "exporter", "staging": "staging",
    }

    for line in raw.splitlines():
        parts = line.split("|")
        if len(parts) < 4:
            continue
        name, image, status, ports = parts[0], parts[1], parts[2], parts[3]

        role = "unknown"
        for key, val in roles.items():
            if key in name and ("exporter" not in name or key == "exporter"):
                if key in ("postgres", "redis") and ("exporter" in name or "staging" in name):
                    role = "exporter" if "exporter" in name else "staging"
                else:
                    role = val
                break

        health = "unknown"
        sl = status.lower()
        if "healthy" in sl:
            health = "healthy"
        elif "unhealthy" in sl:
            health = "unhealthy"
        elif "up" in sl:
            health = "running"

        containers.append({
            "name": name, "image": image.split(":")[0],
            "role": role, "health": health,
            "ports": ports if ports else None,
        })

    return containers


# =============================================================================
# MODULE SCANNER — mapeia todos os 46 modulos
# =============================================================================

# Criticidade por modulo (baseada em impacto de negocio)
MODULE_CRITICALITY = {
    # Critical — indisponibilidade causa perda de receita ou multa
    "financial": "critical", "operacional": "critical",
    "government_integrations": "critical", "fiscal": "critical",
    "fiscal_contabil": "critical",
    # High — impacta operacao diaria
    "crm": "high", "hr": "high", "people_management": "high",
    "clients": "high", "ged": "high", "document_kits": "high",
    "cct": "high", "empresas": "high",
    # Medium — degradacao aceitavel por horas
    "notifications": "medium", "bidding": "medium",
    "equipment_management": "medium", "recruitment": "medium",
    "reimbursement": "medium", "analytics": "medium",
    "reports": "medium", "services": "medium", "campo": "medium",
    "integrations": "medium", "health_occupational": "medium",
    "scheduler": "medium", "mobile": "medium",
    # Low — nao impacta producao diretamente
    "ai": "low", "audit": "low", "config": "low", "monitoring": "low",
    "automation": "low", "retention": "low", "security_lgpd": "low",
    "documents": "low", "fase5": "low", "client_portal": "low",
    "lgpd": "low",
    # Scaffold — modulos vazios/placeholder
    "operacoes": "scaffold", "core": "scaffold", "comercial": "scaffold",
    "pessoas": "scaffold", "gestao": "scaffold", "financeiro": "scaffold",
    "tecnico": "scaffold", "inteligencia": "scaffold", "cadastros": "scaffold",
}

# Integracoes externas por modulo
EXTERNAL_INTEGRATIONS = {
    "government_integrations": [
        {"name": "eSocial", "type": "gov_api", "protocol": "REST/XML", "env": "ESOCIAL_ENVIRONMENT"},
        {"name": "SEFAZ", "type": "gov_api", "protocol": "SOAP/XML", "env": "SEFAZ_ENVIRONMENT"},
        {"name": "NFS-e Manaus", "type": "gov_api", "protocol": "SOAP/ABRASF 2.04"},
        {"name": "NFS-e Nacional", "type": "gov_api", "protocol": "REST/JSON", "env": "NFSE_NACIONAL_ENVIRONMENT"},
        {"name": "FGTS Digital", "type": "gov_api", "protocol": "REST"},
        {"name": "EFD-Reinf", "type": "gov_api", "protocol": "XML"},
        {"name": "DCTFWeb", "type": "gov_api", "protocol": "REST"},
        {"name": "SPED Fiscal/Contabil", "type": "gov_api", "protocol": "TXT/Layout"},
        {"name": "Gov.br OAuth", "type": "oauth", "protocol": "OAuth2"},
        {"name": "e-CAC", "type": "gov_api", "protocol": "REST"},
        {"name": "Simples Nacional", "type": "gov_api", "protocol": "REST"},
    ],
    "integrations": [
        {"name": "Solides", "type": "hr_platform", "protocol": "REST/Webhook", "env": "SOLIDES_API_TOKEN"},
        {"name": "Dominio Sistemas (TOTVS)", "type": "accounting", "protocol": "REST"},
    ],
    "ai": [
        {"name": "OpenAI GPT-4", "type": "llm", "protocol": "REST", "env": "OPENAI_API_KEY"},
        {"name": "Anthropic Claude", "type": "llm", "protocol": "REST", "env": "ANTHROPIC_API_KEY"},
    ],
    "campo": [
        {"name": "ViaCEP", "type": "address_lookup", "protocol": "REST"},
        {"name": "Google Maps", "type": "geocoding", "protocol": "REST", "env": "GOOGLE_MAPS_API_KEY"},
    ],
    "notifications": [
        {"name": "Evolution API (WhatsApp)", "type": "messaging", "protocol": "REST", "env": "WHATSAPP_API_ENABLED"},
    ],
    "financial": [
        {"name": "Cora Banking", "type": "banking", "protocol": "REST", "env": "CORA_API_KEY"},
        {"name": "Inter Banking", "type": "banking", "protocol": "REST", "env": "INTER_API_KEY"},
    ],
}


def scan_module(mod_path: Path) -> dict:
    """Escaneia um modulo e retorna metadados."""
    name = mod_path.name

    py_files = list(mod_path.rglob("*.py"))
    py_files = [f for f in py_files if "__pycache__" not in str(f)]

    total_lines = 0
    for f in py_files:
        try:
            total_lines += sum(1 for _ in open(f))
        except Exception:
            pass

    # Contar modelos (classes com __tablename__)
    model_count = 0
    model_names = []
    for f in py_files:
        try:
            content = f.read_text()
            tables = re.findall(r'__tablename__\s*=\s*["\'](\w+)["\']', content)
            model_count += len(tables)
            model_names.extend(tables)
        except Exception:
            pass

    # Contar controllers/routers
    controller_files = [f for f in py_files if "controller" in f.name or "router" in f.name]

    # Contar endpoints (@router.get/post/put/delete/patch)
    endpoint_count = 0
    for f in py_files:
        try:
            content = f.read_text()
            endpoint_count += len(re.findall(r'@router\.(get|post|put|patch|delete)\(', content))
        except Exception:
            pass

    # Detectar dependencias internas (imports de outros modulos)
    internal_deps = set()
    for f in py_files:
        try:
            content = f.read_text()
            for m in re.findall(r'from modules\.(\w+)', content):
                if m != name:
                    internal_deps.add(m)
        except Exception:
            pass

    # Detectar uso de DB, Redis, Celery
    infra_deps = set()
    for f in py_files:
        try:
            content = f.read_text()
            if "get_db" in content or "AsyncSession" in content or "Session" in content:
                infra_deps.add("postgresql")
            if "redis" in content.lower() or "cache" in content.lower():
                infra_deps.add("redis")
            if "celery" in content.lower() or "@shared_task" in content or "delay(" in content:
                infra_deps.add("celery")
        except Exception:
            pass

    criticality = MODULE_CRITICALITY.get(name, "unknown")
    external = EXTERNAL_INTEGRATIONS.get(name, [])

    return {
        "name": name,
        "files": len(py_files),
        "lines": total_lines,
        "models": model_count,
        "tables": model_names[:10],  # Top 10
        "controllers": len(controller_files),
        "endpoints": endpoint_count,
        "criticality": criticality,
        "internal_dependencies": sorted(internal_deps),
        "infrastructure": sorted(infra_deps),
        "external_integrations": external,
    }


def scan_all_modules() -> list[dict]:
    """Escaneia todos os modulos do backend."""
    modules = []
    for mod_path in sorted(MODULES_DIR.iterdir()):
        if mod_path.is_dir() and not mod_path.name.startswith(("__", ".")):
            modules.append(scan_module(mod_path))
    return modules


# =============================================================================
# TRAFFIC ANALYSIS
# =============================================================================


def analyze_traffic() -> dict:
    if not NGINX_LOG.exists():
        return {"error": "nginx log not found", "peak_hours": [], "top_endpoints": []}

    hour_counts = Counter()
    endpoint_counts = Counter()
    status_counts = Counter()
    total = 0

    pattern = re.compile(
        r'\[(\d{2}/\w{3}/\d{4}):(\d{2}):\d{2}:\d{2}.*?"(\w+)\s+(/[^\s]*)\s+HTTP/[\d.]+"'
        r"\s+(\d{3})"
    )

    try:
        with open(NGINX_LOG) as f:
            for line in f:
                m = pattern.search(line)
                if not m:
                    continue
                total += 1
                hour = int(m.group(2))
                path = m.group(4)
                status = m.group(5)

                hour_counts[hour] += 1
                status_counts[status[:1] + "xx"] += 1

                # Normalizar path (remover UUIDs)
                norm = re.sub(
                    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                    "{id}", path,
                )
                norm = re.sub(r"/\d+(?=/|$)", "/{id}", norm)
                # Remover query strings com tokens
                norm = re.sub(r"\?.*", "", norm)
                if norm.startswith("/api/"):
                    endpoint_counts[norm] += 1
    except Exception:
        pass

    peak_hours_utc = [h for h, _ in hour_counts.most_common(5)]
    peak_hours_brt = sorted([(h - 4) % 24 for h in peak_hours_utc])

    return {
        "total_requests": total,
        "peak_hours_utc": sorted(peak_hours_utc),
        "peak_hours_brt": peak_hours_brt,
        "top_endpoints": [
            {"path": p, "count": c} for p, c in endpoint_counts.most_common(20)
        ],
        "status_distribution": dict(status_counts.most_common()),
        "analyzed_at": datetime.now(tz=None).astimezone().isoformat(),
    }


# =============================================================================
# DEPENDENCY GRAPH
# =============================================================================


def build_dependency_graph(containers: list[dict]) -> dict:
    return {
        "frontend": {"depends_on": ["backend"], "port": 3001},
        "backend": {"depends_on": ["postgres", "redis"], "port": 8080},
        "celery_workers": {
            "depends_on": ["redis", "postgres"],
            "workers": [
                "celery-batch", "celery-beat", "celery-integrations",
                "celery-nfse", "celery-operacional", "celery-priority", "celery-sefaz",
            ],
        },
        "postgres": {"depends_on": [], "port": 5432},
        "redis": {"depends_on": [], "port": 6379},
        "nginx": {"depends_on": ["frontend", "backend"], "ports": [80, 443]},
    }


# =============================================================================
# BUILD KNOWLEDGE BASE
# =============================================================================


def build_knowledge_base() -> dict:
    print("[*] Discovering containers...")
    containers = discover_containers()

    print("[*] Building dependency graph...")
    deps = build_dependency_graph(containers)

    print("[*] Scanning all 46 backend modules...")
    modules = scan_all_modules()

    # Separar modulos ativos vs scaffold
    active_modules = [m for m in modules if m["criticality"] != "scaffold"]
    scaffold_modules = [m for m in modules if m["criticality"] == "scaffold"]

    # Calcular totais
    total_endpoints = sum(m["endpoints"] for m in modules)
    total_models = sum(m["models"] for m in modules)
    total_lines = sum(m["lines"] for m in modules)

    print(f"    Modulos ativos: {len(active_modules)}")
    print(f"    Modulos scaffold: {len(scaffold_modules)}")
    print(f"    Total endpoints: {total_endpoints}")
    print(f"    Total modelos: {total_models}")
    print(f"    Total linhas: {total_lines:,}")

    print("[*] Analyzing traffic patterns...")
    traffic = analyze_traffic()

    # Coletar todas as integracoes externas
    all_integrations = {}
    for m in modules:
        for ext in m.get("external_integrations", []):
            all_integrations[ext["name"]] = {
                "module": m["name"],
                **ext,
            }

    kb = {
        "version": "2.0.0",
        "built_at": datetime.now(tz=None).astimezone().isoformat(),
        "system": {
            "name": "Conecta PRO",
            "environment": "production",
            "domain": "erp.conectamais.pro",
            "total_modules": len(modules),
            "active_modules": len(active_modules),
            "scaffold_modules": len(scaffold_modules),
            "total_endpoints": total_endpoints,
            "total_models": total_models,
            "total_lines": total_lines,
        },
        "containers": containers,
        "dependencies": deps,
        "modules": {m["name"]: m for m in active_modules},
        "scaffold_modules": [m["name"] for m in scaffold_modules],
        "external_integrations": all_integrations,
        "criticality_order": [
            {
                "level": "critical",
                "modules": [m["name"] for m in active_modules if m["criticality"] == "critical"],
                "components": ["postgres", "redis", "backend", "nginx"],
            },
            {
                "level": "high",
                "modules": [m["name"] for m in active_modules if m["criticality"] == "high"],
                "components": ["celery_workers", "frontend"],
            },
            {
                "level": "medium",
                "modules": [m["name"] for m in active_modules if m["criticality"] == "medium"],
                "components": ["flower"],
            },
            {
                "level": "low",
                "modules": [m["name"] for m in active_modules if m["criticality"] == "low"],
                "components": ["monitoring", "staging"],
            },
        ],
        "traffic": traffic,
        "peak_hours": {
            "known_brt": ["07:00-09:00", "17:00-19:00"],
            "from_logs": traffic.get("peak_hours_brt", []),
        },
        "operational_rules": [
            {"rule": "no_deploy_during_peak", "severity": "high",
             "description": "Nao executar deploys entre 07:00-09:00 e 17:00-19:00 BRT"},
            {"rule": "backup_before_deploy", "severity": "critical",
             "description": "Sempre fazer backup do banco antes de qualquer deploy"},
            {"rule": "backend_before_frontend", "severity": "high",
             "description": "Deploiar backend antes do frontend"},
            {"rule": "financial_zone_proibida", "severity": "critical",
             "description": "Nao editar backend/modules/financial/ sem testes — compliance fiscal"},
            {"rule": "government_zone_proibida", "severity": "critical",
             "description": "Nao editar backend/modules/government_integrations/ — regulatorio"},
        ],
    }

    return kb


def save_kb(kb: dict) -> None:
    with open(KB_FILE, "w") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"\n[+] Knowledge base salva: {KB_FILE}")
    print(f"    Versao: {kb['version']}")
    print(f"    Modulos mapeados: {kb['system']['active_modules']}/{kb['system']['total_modules']}")
    print(f"    Endpoints: {kb['system']['total_endpoints']}")
    print(f"    Modelos: {kb['system']['total_models']}")
    print(f"    Integracoes externas: {len(kb['external_integrations'])}")
    print(f"    Containers: {len(kb['containers'])}")
    if kb["traffic"].get("total_requests"):
        print(f"    Requests analisados: {kb['traffic']['total_requests']}")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--full"

    if mode == "--discover":
        print(json.dumps(discover_containers(), indent=2))
    elif mode == "--traffic":
        print(json.dumps(analyze_traffic(), indent=2))
    elif mode == "--modules":
        modules = scan_all_modules()
        for m in modules:
            if m["criticality"] != "scaffold":
                print(f"  {m['name']:30s} | {m['endpoints']:4d} endpoints | {m['models']:3d} models | {m['lines']:6d} lines | {m['criticality']}")
    else:
        kb = build_knowledge_base()
        save_kb(kb)


if __name__ == "__main__":
    main()
