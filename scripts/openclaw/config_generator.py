#!/usr/bin/env python3
"""
Config Generator for OpenClaw - Gerador interativo de configuração.

Ajuda usuários a criar arquivo openclaw.json com configurações
personalizadas de forma interativa.

Author: Conecta PRO Team
Date: 2026-02-02
"""

import json
from pathlib import Path


def generate_config_interactive():
    """Gera configuração interativamente via prompts."""
    print("=" * 70)
    print("  OpenClaw Config Generator - Gerador de Configuração")
    print("=" * 70)
    print()

    config = {"checks": {}, "notifications": {}, "retention": {}}

    # Configurações de checks
    print("📋 Configuração de Checks")
    print()

    checks_config = {
        "backend_tests": {"default_timeout": 120, "description": "Testes backend (pytest)"},
        "frontend_tests": {"default_timeout": 120, "description": "Testes frontend (vitest)"},
        "backend_lint": {"default_timeout": 60, "description": "Linting backend (ruff)"},
        "frontend_lint": {"default_timeout": 60, "description": "Linting frontend (eslint)"},
        "security_bandit": {"default_timeout": 60, "description": "Security scan (bandit)"},
        "gitleaks": {"default_timeout": 60, "description": "Secret scanning (gitleaks)"},
        "npm_audit": {"default_timeout": 60, "description": "NPM vulnerability audit"},
        "pip_audit": {"default_timeout": 60, "description": "Pip vulnerability audit"},
        "coverage": {"default_timeout": 180, "description": "Code coverage analysis"},
        "health": {"default_timeout": 30, "description": "Health checks dos serviços"},
        "docker_status": {"default_timeout": 15, "description": "Status containers Docker"},
        "disk_space": {"default_timeout": 5, "description": "Espaço em disco"},
        "lighthouse": {"default_timeout": 120, "description": "Performance web (lighthouse)"},
    }

    for check_name, check_info in checks_config.items():
        enabled_input = input(f"Habilitar {check_info['description']}? (s/N): ").strip().lower()
        enabled = enabled_input == "s"

        timeout_input = input(f"  Timeout (padrão: {check_info['default_timeout']}s): ").strip()
        timeout = int(timeout_input) if timeout_input else check_info["default_timeout"]

        config["checks"][check_name] = {"enabled": enabled, "timeout": timeout}

        # Configurações específicas
        if check_name == "coverage" and enabled:
            min_cov = input("  Cobertura mínima exigida (padrão: 60%): ").strip()
            config["checks"][check_name]["min_coverage"] = int(min_cov) if min_cov else 60

        if check_name == "disk_space" and enabled:
            min_free = input("  Mínimo de GB livres (padrão: 5GB): ").strip()
            config["checks"][check_name]["min_free_gb"] = int(min_free) if min_free else 5

        print()

    # Notificações
    print("🔔 Configuração de Notificações")
    print()

    discord_webhook = input("Discord webhook URL (deixe vazio para desabilitar): ").strip()
    if discord_webhook:
        config["notifications"]["discord_webhook"] = discord_webhook

    slack_webhook = input("Slack webhook URL (deixe vazio para desabilitar): ").strip()
    if slack_webhook:
        config["notifications"]["slack_webhook"] = slack_webhook

    teams_webhook = input("Teams webhook URL (deixe vazio para desabilitar): ").strip()
    if teams_webhook:
        config["notifications"]["teams_webhook"] = teams_webhook

    notify_on_input = input("Notificar em quais status? (fail,error,warn - padrão: fail,error): ").strip()
    notify_on = notify_on_input.split(",") if notify_on_input else ["fail", "error"]
    config["notifications"]["notify_on"] = [s.strip() for s in notify_on]

    print()

    # Retenção
    print("📦 Configuração de Retenção")
    print()

    reports_days_input = input("Manter relatórios por quantos dias? (padrão: 30): ").strip()
    config["retention"]["reports_days"] = int(reports_days_input) if reports_days_input else 30

    logs_days_input = input("Manter logs por quantos dias? (padrão: 14): ").strip()
    config["retention"]["logs_days"] = int(logs_days_input) if logs_days_input else 14

    print()

    # Ciclo
    print("⏱️ Configuração de Ciclo")
    print()

    interval_input = input("Intervalo entre ciclos no modo daemon (segundos, padrão: 3600): ").strip()
    config["cycle_interval_seconds"] = int(interval_input) if interval_input else 3600

    print()

    # Salvar
    output_path = Path("config/openclaw.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print(f"✅ Configuração salva em: {output_path}")
    print()
    print("Para usar:")
    print(f"  python3 scripts/openclaw/runner.py --config {output_path}")
    print("=" * 70)


def generate_config_minimal():
    """Gera configuração mínima sem interação."""
    config = {
        "cycle_interval_seconds": 3600,
        "checks": {
            "backend_tests": {"enabled": True, "timeout": 120},
            "frontend_tests": {"enabled": True, "timeout": 120},
            "backend_lint": {"enabled": True, "timeout": 60},
            "frontend_lint": {"enabled": True, "timeout": 60},
            "security_bandit": {"enabled": True, "timeout": 60},
            "gitleaks": {"enabled": True, "timeout": 60},
            "npm_audit": {"enabled": True, "timeout": 60},
            "pip_audit": {"enabled": True, "timeout": 60},
            "coverage": {"enabled": True, "timeout": 180, "min_coverage": 60},
            "health": {"enabled": True, "timeout": 30},
            "docker_status": {"enabled": True, "timeout": 15},
            "disk_space": {"enabled": True, "timeout": 5, "min_free_gb": 5},
            "lighthouse": {"enabled": False, "timeout": 120},
        },
        "notifications": {
            "discord_webhook": "",
            "slack_webhook": "",
            "teams_webhook": "",
            "notify_on": ["fail", "error"],
        },
        "retention": {"reports_days": 30, "logs_days": 14},
    }

    output_path = Path("config/openclaw.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✅ Configuração mínima salva em: {output_path}")
    return output_path


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--minimal":
        generate_config_minimal()
    else:
        generate_config_interactive()


if __name__ == "__main__":
    main()
