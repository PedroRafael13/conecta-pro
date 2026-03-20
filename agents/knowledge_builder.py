#!/usr/bin/env python3
"""
Knowledge Builder — Conecta PRO Multi-Agent System

Constrói e atualiza a base de conhecimento do sistema:
- Mapeia containers Docker e dependências
- Analisa logs nginx para horários de pico
- Mapeia módulos frontend → endpoints backend
- Gera agent_knowledge_base.json

Uso:
    python3 agents/knowledge_builder.py              # Build completo
    python3 agents/knowledge_builder.py --discover   # Apenas discovery
    python3 agents/knowledge_builder.py --traffic    # Apenas análise de tráfego
"""

import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path("/opt/conecta-pro")
KB_FILE = PROJECT_DIR / "agent_knowledge_base.json"
NGINX_LOG = Path("/var/log/nginx/access.log")


def run(cmd: str, timeout: int = 30) -> str:
    """Executa comando shell e retorna stdout."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, Exception):
        return ""


def discover_containers() -> list[dict]:
    """Mapeia todos os containers Docker com status e dependências."""
    raw = run(
        "docker ps -a --format '{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}'"
    )
    if not raw:
        return []

    containers = []
    for line in raw.splitlines():
        parts = line.split("|")
        if len(parts) < 4:
            continue
        name, image, status, ports = parts[0], parts[1], parts[2], parts[3]

        # Determinar role
        role = "unknown"
        if "postgres" in name and "exporter" not in name and "staging" not in name:
            role = "database"
        elif "redis" in name and "exporter" not in name and "staging" not in name:
            role = "cache"
        elif "backend" in name and "celery" not in name:
            role = "api"
        elif "frontend" in name:
            role = "frontend"
        elif "celery-beat" in name:
            role = "scheduler"
        elif "celery" in name:
            role = "worker"
        elif "flower" in name:
            role = "monitor"
        elif "prometheus" in name:
            role = "monitoring"
        elif "grafana" in name:
            role = "monitoring"
        elif "loki" in name or "promtail" in name:
            role = "logging"
        elif "alertmanager" in name:
            role = "alerting"
        elif "exporter" in name:
            role = "exporter"
        elif "staging" in name:
            role = "staging"

        # Health
        health = "unknown"
        if "healthy" in status.lower():
            health = "healthy"
        elif "unhealthy" in status.lower():
            health = "unhealthy"
        elif "up" in status.lower():
            health = "running"

        containers.append(
            {
                "name": name,
                "image": image.split(":")[0],
                "role": role,
                "health": health,
                "ports": ports if ports else None,
            }
        )

    return containers


def build_dependency_graph(containers: list[dict]) -> dict:
    """Constrói grafo de dependências entre componentes."""
    return {
        "frontend": {
            "depends_on": ["backend"],
            "type": "http",
            "port": 3001,
            "note": "PM2 Next.js → Backend API via nginx",
        },
        "backend": {
            "depends_on": ["postgres", "redis"],
            "type": "tcp",
            "port": 8080,
            "note": "FastAPI → PostgreSQL (asyncpg) + Redis (cache/sessions)",
        },
        "celery_workers": {
            "depends_on": ["redis", "postgres"],
            "type": "amqp",
            "note": "Celery workers consomem de Redis broker, escrevem em PostgreSQL",
            "workers": [
                "celery-batch",
                "celery-beat",
                "celery-integrations",
                "celery-nfse",
                "celery-operacional",
                "celery-priority",
                "celery-sefaz",
            ],
        },
        "postgres": {
            "depends_on": [],
            "type": "tcp",
            "port": 5432,
            "note": "PostgreSQL 16 — banco principal",
        },
        "redis": {
            "depends_on": [],
            "type": "tcp",
            "port": 6379,
            "note": "Redis 7 — cache, sessions, Celery broker",
        },
        "nginx": {
            "depends_on": ["frontend", "backend"],
            "type": "http",
            "ports": [80, 443],
            "note": "Reverse proxy, SSL termination, rate limiting",
        },
        "monitoring": {
            "depends_on": ["prometheus", "grafana", "loki", "alertmanager"],
            "type": "http",
            "note": "Stack de observabilidade",
        },
    }


def analyze_traffic() -> dict:
    """Analisa logs nginx para identificar horários de pico e endpoints mais acessados."""
    if not NGINX_LOG.exists():
        return {"error": "nginx log not found", "peak_hours": [], "top_endpoints": []}

    hour_counts = Counter()
    endpoint_counts = Counter()
    status_counts = Counter()
    total = 0

    # Regex para combined log format
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

                # Normalizar path (remover UUIDs e IDs)
                norm = re.sub(
                    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                    "{id}",
                    path,
                )
                norm = re.sub(r"/\d+(?=/|$)", "/{id}", norm)
                if norm.startswith("/api/"):
                    endpoint_counts[norm] += 1
    except Exception:
        pass

    # Horários de pico (top 5 horas UTC → converter para BRT/AMT)
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
        "analyzed_at": datetime.utcnow().isoformat() + "Z",
    }


def map_frontend_to_backend() -> list[dict]:
    """Mapeia módulos frontend → endpoints backend consumidos."""
    return [
        {
            "frontend_module": "dashboard",
            "path": "/dashboard",
            "backend_endpoints": ["/api/v1/operacional", "/api/v1/notifications"],
            "criticality": "high",
        },
        {
            "frontend_module": "operacional",
            "path": "/modulos/operacional",
            "backend_endpoints": ["/api/v1/operacional"],
            "criticality": "critical",
            "note": "252 endpoints — postos, escalas, turnos, alocações, diaristas",
        },
        {
            "frontend_module": "financeiro",
            "path": "/modulos/financeiro",
            "backend_endpoints": ["/api/v1/financial"],
            "criticality": "critical",
            "note": "466 endpoints — contas, pagamentos, conciliação, compras",
        },
        {
            "frontend_module": "crm",
            "path": "/modulos/crm",
            "backend_endpoints": ["/api/v1/crm"],
            "criticality": "high",
            "note": "100 endpoints — leads, propostas, contratos",
        },
        {
            "frontend_module": "ged",
            "path": "/modulos/documentos",
            "backend_endpoints": ["/api/v1/ged", "/api/v1/document-kits"],
            "criticality": "high",
            "note": "193 endpoints — documentos, pastas, kits",
        },
        {
            "frontend_module": "rh",
            "path": "/modulos/rh",
            "backend_endpoints": ["/api/v1/people-management", "/api/v1/recruitment"],
            "criticality": "high",
            "note": "722 endpoints — DP, folha, ponto, SST, recrutamento",
        },
        {
            "frontend_module": "reembolso",
            "path": "/modulos/reembolso",
            "backend_endpoints": ["/api/v1/reimbursements"],
            "criticality": "medium",
            "note": "26 endpoints — solicitações, aprovações, pagamentos",
        },
        {
            "frontend_module": "government",
            "path": "/modulos/fiscal",
            "backend_endpoints": ["/api/v1/government", "/api/v1/fiscal", "/api/v1/empresas"],
            "criticality": "critical",
            "note": "255 endpoints — NFS-e, eSocial, SEFAZ, certidões",
        },
        {
            "frontend_module": "clientes",
            "path": "/modulos/clientes",
            "backend_endpoints": ["/api/v1/clients"],
            "criticality": "high",
            "note": "50 endpoints — clientes, condomínios, contratos",
        },
        {
            "frontend_module": "equipamentos",
            "path": "/modulos/equipamentos",
            "backend_endpoints": ["/api/v1/equipment", "/api/v1/comodatos", "/api/v1/maintenances"],
            "criticality": "medium",
            "note": "73 endpoints — equipamentos, comodato, manutenção",
        },
        {
            "frontend_module": "bartolo",
            "path": "/modulos/assistente",
            "backend_endpoints": ["/api/v1/ai"],
            "criticality": "low",
            "note": "19 endpoints — assistente IA, wizards",
        },
        {
            "frontend_module": "analytics",
            "path": "/modulos/analytics",
            "backend_endpoints": ["/api/v1/analytics", "/api/v1/reports"],
            "criticality": "medium",
            "note": "64 endpoints — dashboards, KPIs, relatórios",
        },
        {
            "frontend_module": "notificacoes",
            "path": "/modulos/notificacoes",
            "backend_endpoints": ["/api/v1/notifications"],
            "criticality": "medium",
            "note": "76 endpoints — push, alertas, centro de notificações",
        },
        {
            "frontend_module": "licitacoes",
            "path": "/modulos/licitacoes",
            "backend_endpoints": ["/api/v1/bidding"],
            "criticality": "medium",
            "note": "87 endpoints — editais, propostas, agentes IA",
        },
    ]


def build_knowledge_base() -> dict:
    """Constrói a base de conhecimento completa."""
    print("[*] Discovering containers...")
    containers = discover_containers()

    print("[*] Building dependency graph...")
    deps = build_dependency_graph(containers)

    print("[*] Analyzing traffic patterns...")
    traffic = analyze_traffic()

    print("[*] Mapping frontend → backend...")
    modules = map_frontend_to_backend()

    kb = {
        "version": "1.0.0",
        "built_at": datetime.utcnow().isoformat() + "Z",
        "system": {
            "name": "Conecta PRO",
            "environment": "production",
            "domain": "erp.conectamais.pro",
            "total_endpoints": 2847,
        },
        "containers": containers,
        "dependencies": deps,
        "criticality_order": [
            {
                "level": "critical",
                "components": ["postgres", "redis", "backend", "nginx"],
                "modules": ["financeiro", "operacional", "government"],
                "note": "Indisponibilidade causa perda de receita ou multas",
            },
            {
                "level": "high",
                "components": ["celery_workers", "frontend"],
                "modules": ["crm", "rh", "ged", "clientes", "dashboard"],
                "note": "Impacta operação diária mas não causa perda imediata",
            },
            {
                "level": "medium",
                "components": ["flower", "monitoring"],
                "modules": ["reembolso", "equipamentos", "analytics", "notificacoes", "licitacoes"],
                "note": "Degradação aceitável por horas",
            },
            {
                "level": "low",
                "components": ["staging", "exporters"],
                "modules": ["bartolo"],
                "note": "Não impacta produção",
            },
        ],
        "peak_hours": {
            "known_brt": ["07:00-09:00", "17:00-19:00"],
            "note": "Horário comercial Manaus (AMT/BRT-1). Evitar deploys nesses horários.",
            "from_logs": traffic.get("peak_hours_brt", []),
        },
        "traffic": traffic,
        "frontend_backend_map": modules,
        "operational_rules": [
            {
                "rule": "no_deploy_during_peak",
                "description": "Não executar deploys entre 07:00-09:00 e 17:00-19:00 BRT",
                "severity": "high",
            },
            {
                "rule": "backup_before_deploy",
                "description": "Sempre fazer backup do banco antes de qualquer deploy",
                "severity": "critical",
            },
            {
                "rule": "backend_before_frontend",
                "description": "Deploiar backend antes do frontend (APIs devem existir antes do UI consumir)",
                "severity": "high",
            },
            {
                "rule": "restart_celery_monthly",
                "description": "Reiniciar workers Celery mensalmente (memory leaks observados após 30d)",
                "severity": "medium",
            },
            {
                "rule": "check_disk_before_build",
                "description": "Verificar disco antes de build Docker (build cache pode consumir 80GB+)",
                "severity": "high",
            },
            {
                "rule": "financial_zone_proibida",
                "description": "Não editar backend/modules/financial/ sem testes — compliance fiscal",
                "severity": "critical",
            },
            {
                "rule": "government_zone_proibida",
                "description": "Não editar backend/modules/government_integrations/ — regulatório",
                "severity": "critical",
            },
        ],
    }

    return kb


def save_kb(kb: dict) -> None:
    """Salva knowledge base em JSON."""
    with open(KB_FILE, "w") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)
    print(f"[+] Knowledge base salva: {KB_FILE}")
    print(f"    Containers: {len(kb['containers'])}")
    print(f"    Módulos mapeados: {len(kb['frontend_backend_map'])}")
    print(f"    Regras operacionais: {len(kb['operational_rules'])}")
    if kb["traffic"].get("total_requests"):
        print(f"    Requests analisados: {kb['traffic']['total_requests']}")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--full"

    if mode == "--discover":
        containers = discover_containers()
        print(json.dumps(containers, indent=2))
    elif mode == "--traffic":
        traffic = analyze_traffic()
        print(json.dumps(traffic, indent=2))
    else:
        kb = build_knowledge_base()
        save_kb(kb)


if __name__ == "__main__":
    main()
