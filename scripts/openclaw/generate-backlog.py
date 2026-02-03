#!/usr/bin/env python3
"""
Generate Backlog - Extrai tarefas do código e gera backlog.json
Usado pelo OpenClaw para priorizar trabalho
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict

WORKSPACE = Path("/opt/conecta-pro")
OUTPUT_FILE = WORKSPACE / "scripts/openclaw/backlog.json"


def run_cmd(cmd: str) -> tuple[int, str]:
    """Executa comando e retorna (code, output)"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=WORKSPACE)
        return result.returncode, result.stdout
    except:
        return 1, ""


def extract_todos() -> List[Dict]:
    """Extrai TODOs/FIXMEs do código"""
    tasks = []
    code, output = run_cmd("grep -rn 'TODO\\|FIXME\\|XXX\\|HACK' --include='*.py' --include='*.ts' --include='*.tsx' backend/ frontend/ 2>/dev/null | head -200")

    if code == 0:
        for line in output.split('\n'):
            if not line.strip():
                continue
            parts = line.split(':', 2)
            if len(parts) >= 3:
                tasks.append({
                    "type": "todo",
                    "file": parts[0],
                    "line": int(parts[1]) if parts[1].isdigit() else 0,
                    "description": parts[2].strip()[:200],
                    "priority": "P2",
                    "estimated_time": "30min"
                })

    return tasks


def check_failing_tests() -> List[Dict]:
    """Verifica testes falhando"""
    tasks = []

    # Backend tests
    code, output = run_cmd("cd backend && python -m pytest tests/ --tb=no -q 2>&1 | tail -20")
    if "FAILED" in output or "ERROR" in output:
        tasks.append({
            "type": "fix_tests",
            "component": "backend",
            "description": "Testes backend falhando",
            "priority": "P1",
            "estimated_time": "1h"
        })

    # Frontend tests
    code, output = run_cmd("cd frontend && npm run test:run 2>&1 | tail -20")
    if "FAIL" in output or "ERROR" in output:
        tasks.append({
            "type": "fix_tests",
            "component": "frontend",
            "description": "Testes frontend falhando",
            "priority": "P1",
            "estimated_time": "1h"
        })

    return tasks


def check_coverage() -> List[Dict]:
    """Verifica cobertura de testes"""
    tasks = []

    # Backend coverage
    code, output = run_cmd("cd backend && python -m pytest --cov=backend --cov-report=term 2>&1 | grep 'TOTAL'")
    if code == 0 and output:
        try:
            coverage = int(output.split()[-1].replace('%', ''))
            if coverage < 80:
                tasks.append({
                    "type": "increase_coverage",
                    "component": "backend",
                    "description": f"Cobertura backend: {coverage}% (meta: 80%)",
                    "current_coverage": coverage,
                    "target_coverage": 80,
                    "priority": "P1",
                    "estimated_time": "2h"
                })
        except:
            pass

    return tasks


def check_lint_errors() -> List[Dict]:
    """Verifica erros de lint"""
    tasks = []

    # Backend lint (ruff)
    code, output = run_cmd("cd backend && ruff check . --statistics 2>&1 | tail -10")
    if code != 0:
        error_count = output.count('\n')
        if error_count > 0:
            tasks.append({
                "type": "fix_lint",
                "component": "backend",
                "description": f"Corrigir {error_count} erros de lint (ruff)",
                "priority": "P2",
                "estimated_time": "1h"
            })

    # Frontend lint (eslint)
    code, output = run_cmd("cd frontend && npm run lint 2>&1 | tail -10")
    if "warning" in output.lower() or "error" in output.lower():
        tasks.append({
            "type": "fix_lint",
            "component": "frontend",
            "description": "Corrigir warnings/errors do eslint",
            "priority": "P2",
            "estimated_time": "1h"
        })

    return tasks


def check_security() -> List[Dict]:
    """Verifica vulnerabilidades de segurança"""
    tasks = []

    # Backend security (bandit)
    code, output = run_cmd("cd backend && bandit -r . -ll -f txt 2>&1 | grep -E 'Issue:|Severity:' | head -20")
    if "Issue:" in output:
        issue_count = output.count("Issue:")
        tasks.append({
            "type": "fix_security",
            "component": "backend",
            "description": f"Corrigir {issue_count} vulnerabilidades (High/Low)",
            "priority": "P0" if "High" in output else "P1",
            "estimated_time": "2h"
        })

    # Dependencies vulnerabilities (safety)
    code, output = run_cmd("cd backend && safety check --json 2>&1")
    if '"vulnerabilities"' in output:
        try:
            data = json.loads(output)
            vuln_count = len(data.get("vulnerabilities", []))
            if vuln_count > 0:
                tasks.append({
                    "type": "fix_dependencies",
                    "component": "backend",
                    "description": f"Atualizar {vuln_count} dependências vulneráveis",
                    "priority": "P1",
                    "estimated_time": "1h"
                })
        except:
            pass

    return tasks


def check_type_errors() -> List[Dict]:
    """Verifica erros de tipo (TypeScript)"""
    tasks = []

    code, output = run_cmd("cd frontend && npm run type-check 2>&1")
    if code != 0:
        error_count = output.count("error TS")
        if error_count > 0:
            tasks.append({
                "type": "fix_types",
                "component": "frontend",
                "description": f"Corrigir {error_count} erros TypeScript",
                "priority": "P2",
                "estimated_time": "2h"
            })

    return tasks


def check_incomplete_modules() -> List[Dict]:
    """Verifica módulos incompletos (baseado em TODO patterns)"""
    tasks = []

    # Verificar endpoints faltantes (comentados no código)
    code, output = run_cmd("grep -r '# TODO.*endpoint' --include='*.py' backend/modules/ 2>/dev/null | wc -l")
    if code == 0 and output.strip():
        count = int(output.strip())
        if count > 0:
            tasks.append({
                "type": "implement_endpoints",
                "component": "backend",
                "description": f"Implementar {count} endpoints faltantes",
                "priority": "P1",
                "estimated_time": f"{count * 30}min"
            })

    return tasks


def main():
    """Gera backlog completo"""
    print("🔍 Analisando codebase...")

    all_tasks = []

    print("  ├─ Extraindo TODOs...")
    all_tasks.extend(extract_todos())

    print("  ├─ Verificando testes...")
    all_tasks.extend(check_failing_tests())

    print("  ├─ Verificando cobertura...")
    all_tasks.extend(check_coverage())

    print("  ├─ Verificando lint...")
    all_tasks.extend(check_lint_errors())

    print("  ├─ Verificando segurança...")
    all_tasks.extend(check_security())

    print("  ├─ Verificando tipos...")
    all_tasks.extend(check_type_errors())

    print("  └─ Verificando módulos incompletos...")
    all_tasks.extend(check_incomplete_modules())

    # Ordenar por prioridade
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    all_tasks.sort(key=lambda x: priority_order.get(x.get("priority", "P3"), 3))

    # Salvar
    with open(OUTPUT_FILE, 'w') as f:
        json.dump({
            "generated_at": str(Path(__file__).stat().st_mtime),
            "total_tasks": len(all_tasks),
            "by_priority": {
                "P0": sum(1 for t in all_tasks if t.get("priority") == "P0"),
                "P1": sum(1 for t in all_tasks if t.get("priority") == "P1"),
                "P2": sum(1 for t in all_tasks if t.get("priority") == "P2"),
                "P3": sum(1 for t in all_tasks if t.get("priority") == "P3"),
            },
            "tasks": all_tasks
        }, f, indent=2)

    print(f"\n✅ Backlog gerado: {len(all_tasks)} tarefas")
    print(f"   📁 Arquivo: {OUTPUT_FILE}")
    print(f"\n📊 Por prioridade:")
    print(f"   P0 (Crítico):  {sum(1 for t in all_tasks if t.get('priority') == 'P0')}")
    print(f"   P1 (Alta):     {sum(1 for t in all_tasks if t.get('priority') == 'P1')}")
    print(f"   P2 (Média):    {sum(1 for t in all_tasks if t.get('priority') == 'P2')}")
    print(f"   P3 (Baixa):    {sum(1 for t in all_tasks if t.get('priority') == 'P3')}")

    return len(all_tasks)


if __name__ == "__main__":
    count = main()
    exit(0 if count >= 0 else 1)
