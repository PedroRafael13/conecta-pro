#!/usr/bin/env python3
"""
OpenClaw - Main Agent Loop
Engenheiro de Software Autônomo 24/7 para Conecta PRO

Este script roda em loop infinito:
1. Gera backlog de tarefas
2. Prioriza tarefas
3. Executa tarefas (via LLM)
4. Testa e valida
5. Commita e pusha
6. Reporta progresso
7. Aguarda próximo ciclo
"""

import os
import sys
import time
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import anthropic  # ou openai

# =============================================================================
# Configuração
# =============================================================================

WORKSPACE = Path(os.getenv("OPENCLAW_WORK_DIR", "/workspace"))
INTERVAL = int(os.getenv("OPENCLAW_INTERVAL", 3600))  # 1 hora
MIN_COVERAGE = float(os.getenv("MIN_TEST_COVERAGE", 70))
MAX_TASKS_PER_CYCLE = int(os.getenv("MAX_TASKS_PER_CYCLE", 8))
MAX_TIME_PER_TASK = int(os.getenv("MAX_TIME_PER_TASK", 1800))  # 30min

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(WORKSPACE / "logs/openclaw/agent.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("openclaw")

# =============================================================================
# Utility Functions
# =============================================================================

def run_command(cmd: str, cwd: Optional[Path] = None) -> tuple[int, str, str]:
    """Executa comando shell e retorna (returncode, stdout, stderr)"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or WORKSPACE,
            capture_output=True,
            text=True,
            timeout=300  # 5min max
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timeout"
    except Exception as e:
        return 1, "", str(e)


def heartbeat():
    """Atualiza heartbeat file para health check"""
    Path("/tmp/openclaw-heartbeat").touch()


def send_notification(message: str, level: str = "info"):
    """Envia notificação Discord/Slack"""
    webhook = os.getenv("DISCORD_WEBHOOK") or os.getenv("SLACK_WEBHOOK")
    if not webhook:
        return

    colors = {
        "success": "3066993",  # Green
        "info": "3447003",     # Blue
        "warning": "15105570", # Yellow
        "error": "15158332",   # Red
        "critical": "10038562" # Dark Red
    }

    payload = {
        "embeds": [{
            "title": f"🤖 OpenClaw Agent",
            "description": message,
            "color": int(colors.get(level, colors["info"])),
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Conecta PRO"}
        }]
    }

    try:
        import httpx
        httpx.post(webhook, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Falha ao enviar notificação: {e}")


# =============================================================================
# Backlog Generation
# =============================================================================

def generate_backlog() -> List[Dict]:
    """Gera backlog de tarefas priorizadas"""
    logger.info("📋 Gerando backlog de tarefas...")

    tasks = []

    # 1. Extrair TODOs do código
    logger.info("  ├─ Extraindo TODOs...")
    code, stdout, stderr = run_command(
        "grep -r 'TODO\\|FIXME\\|XXX\\|HACK' --include='*.py' --include='*.ts' --include='*.tsx' backend/ frontend/ | head -100"
    )
    if code == 0:
        for line in stdout.split('\n'):
            if line.strip():
                parts = line.split(':', 2)
                if len(parts) >= 3:
                    tasks.append({
                        "type": "todo",
                        "file": parts[0],
                        "line": parts[1],
                        "description": parts[2].strip(),
                        "priority": "P2"
                    })

    # 2. Verificar testes falhando
    logger.info("  ├─ Verificando testes...")
    code, stdout, stderr = run_command(
        "cd backend && python -m pytest tests/ -v --tb=short --maxfail=5",
        cwd=WORKSPACE / "backend"
    )
    if code != 0:
        tasks.append({
            "type": "fix_tests",
            "description": "Testes backend falhando",
            "details": stderr,
            "priority": "P1"
        })

    # 3. Verificar cobertura de testes
    logger.info("  ├─ Verificando cobertura...")
    code, stdout, stderr = run_command(
        "cd backend && python -m pytest tests/ --cov=backend --cov-report=json",
        cwd=WORKSPACE / "backend"
    )
    if code == 0:
        coverage_file = WORKSPACE / "backend/coverage.json"
        if coverage_file.exists():
            with open(coverage_file) as f:
                data = json.load(f)
                total_coverage = data.get("totals", {}).get("percent_covered", 0)
                if total_coverage < MIN_COVERAGE:
                    tasks.append({
                        "type": "increase_coverage",
                        "description": f"Cobertura baixa: {total_coverage:.1f}% (meta: {MIN_COVERAGE}%)",
                        "current": total_coverage,
                        "target": MIN_COVERAGE,
                        "priority": "P1"
                    })

    # 4. Lint errors
    logger.info("  ├─ Verificando lint...")
    code, stdout, stderr = run_command(
        "cd backend && ruff check . --output-format=json",
        cwd=WORKSPACE / "backend"
    )
    if code != 0 and stdout:
        try:
            lint_errors = json.loads(stdout)
            for error in lint_errors[:20]:  # Top 20 erros
                tasks.append({
                    "type": "lint",
                    "file": error.get("filename"),
                    "description": error.get("message"),
                    "priority": "P2"
                })
        except:
            pass

    # 5. Security vulnerabilities
    logger.info("  ├─ Verificando segurança...")
    code, stdout, stderr = run_command(
        "cd backend && bandit -r . -f json -ll",
        cwd=WORKSPACE / "backend"
    )
    if code != 0 and stdout:
        try:
            security_issues = json.loads(stdout)
            for issue in security_issues.get("results", [])[:10]:
                tasks.append({
                    "type": "security",
                    "file": issue.get("filename"),
                    "description": issue.get("issue_text"),
                    "severity": issue.get("issue_severity"),
                    "priority": "P0" if issue.get("issue_severity") == "HIGH" else "P1"
                })
        except:
            pass

    # Ordenar por prioridade
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    tasks.sort(key=lambda x: priority_order.get(x.get("priority", "P3"), 3))

    logger.info(f"✅ Backlog gerado: {len(tasks)} tarefas")
    logger.info(f"  ├─ P0 (Crítico): {sum(1 for t in tasks if t.get('priority') == 'P0')}")
    logger.info(f"  ├─ P1 (Alta): {sum(1 for t in tasks if t.get('priority') == 'P1')}")
    logger.info(f"  ├─ P2 (Média): {sum(1 for t in tasks if t.get('priority') == 'P2')}")
    logger.info(f"  └─ P3 (Baixa): {sum(1 for t in tasks if t.get('priority') == 'P3')}")

    # Salvar backlog
    backlog_file = WORKSPACE / "scripts/openclaw/backlog.json"
    with open(backlog_file, 'w') as f:
        json.dump(tasks, f, indent=2)

    return tasks


# =============================================================================
# Task Execution (AI-powered)
# =============================================================================

def execute_task_with_ai(task: Dict) -> bool:
    """Executa uma tarefa usando Claude/GPT"""
    logger.info(f"🤖 Executando tarefa: {task.get('description', 'N/A')[:80]}...")

    if not ANTHROPIC_API_KEY:
        logger.error("❌ ANTHROPIC_API_KEY não configurada!")
        return False

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        # Construir prompt baseado no tipo de tarefa
        prompt = build_task_prompt(task)

        # Chamar Claude
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=4096,
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Processar resposta
        result_text = response.content[0].text

        logger.info("✅ Tarefa concluída pelo AI")
        logger.debug(f"Resposta: {result_text[:200]}...")

        return True

    except Exception as e:
        logger.error(f"❌ Erro ao executar tarefa: {e}")
        return False


def build_task_prompt(task: Dict) -> str:
    """Constrói prompt para o LLM baseado no tipo de tarefa"""

    base_context = f"""
Você é o OpenClaw, engenheiro de software sênior do Conecta PRO.

WORKSPACE: {WORKSPACE}
MISSÃO: Ler em {WORKSPACE}/OPENCLAW_MISSION.md

TAREFA ATUAL:
Tipo: {task.get('type')}
Prioridade: {task.get('priority')}
Descrição: {task.get('description')}
"""

    if task.get('type') == 'todo':
        return base_context + f"""
Arquivo: {task.get('file')}
Linha: {task.get('line')}

INSTRUÇÕES:
1. Ler o arquivo indicado
2. Entender o TODO/FIXME
3. Implementar a solução
4. Escrever testes se necessário
5. Commitar com mensagem descritiva

Use as ferramentas Bash, Read, Edit, Write conforme necessário.
"""

    elif task.get('type') == 'fix_tests':
        return base_context + f"""
Detalhes do erro:
{task.get('details', 'N/A')[:500]}

INSTRUÇÕES:
1. Analisar o erro dos testes
2. Identificar a causa raiz
3. Corrigir o problema
4. Rodar testes novamente para confirmar
5. Commitar a correção
"""

    elif task.get('type') == 'increase_coverage':
        return base_context + f"""
Cobertura atual: {task.get('current', 0):.1f}%
Meta: {task.get('target', MIN_COVERAGE)}%

INSTRUÇÕES:
1. Identificar funções/módulos sem testes
2. Escrever testes unitários para aumentar cobertura
3. Focar em código crítico primeiro
4. Rodar pytest com --cov para verificar
5. Commitar novos testes
"""

    elif task.get('type') == 'security':
        return base_context + f"""
Arquivo: {task.get('file')}
Severidade: {task.get('severity')}

INSTRUÇÕES:
1. Analisar a vulnerabilidade reportada
2. Implementar correção segura
3. Verificar se não quebrou nada (rodar testes)
4. Commitar com prefixo "security:"
"""

    else:
        return base_context + "\nINSTRUÇÕES: Analise e resolva a tarefa da melhor forma possível."


# =============================================================================
# Main Loop
# =============================================================================

def main_cycle():
    """Executa um ciclo completo de trabalho"""
    cycle_start = time.time()
    logger.info("=" * 80)
    logger.info(f"🚀 OPENCLAW CYCLE INICIADO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    try:
        # 1. Gerar backlog
        tasks = generate_backlog()

        if not tasks:
            logger.info("✅ Nenhuma tarefa pendente! Sistema está perfeito. 🎉")
            send_notification("✅ Nenhuma tarefa pendente! Sistema está perfeito. 🎉", "success")
            return

        # 2. Executar top N tarefas
        tasks_to_execute = tasks[:MAX_TASKS_PER_CYCLE]
        logger.info(f"📝 Executando {len(tasks_to_execute)} tarefas de {len(tasks)} no backlog")

        completed = 0
        failed = 0

        for i, task in enumerate(tasks_to_execute, 1):
            task_start = time.time()
            logger.info(f"\n🎯 Tarefa {i}/{len(tasks_to_execute)}")
            logger.info(f"   Tipo: {task.get('type')}")
            logger.info(f"   Prioridade: {task.get('priority')}")
            logger.info(f"   Descrição: {task.get('description', 'N/A')[:100]}")

            success = execute_task_with_ai(task)

            task_duration = time.time() - task_start

            if success:
                completed += 1
                logger.info(f"   ✅ Concluída em {task_duration:.1f}s")
            else:
                failed += 1
                logger.error(f"   ❌ Falhou após {task_duration:.1f}s")

            # Safety: não exceder tempo máximo por tarefa
            if task_duration > MAX_TIME_PER_TASK:
                logger.warning(f"   ⚠️ Tarefa excedeu tempo limite ({MAX_TIME_PER_TASK}s)")

        # 3. Relatório do ciclo
        cycle_duration = time.time() - cycle_start
        logger.info("\n" + "=" * 80)
        logger.info("📊 RELATÓRIO DO CICLO")
        logger.info("=" * 80)
        logger.info(f"Tarefas completadas: {completed}/{len(tasks_to_execute)}")
        logger.info(f"Tarefas falhadas: {failed}/{len(tasks_to_execute)}")
        logger.info(f"Duração total: {cycle_duration:.1f}s ({cycle_duration/60:.1f}min)")
        logger.info(f"Backlog restante: {len(tasks) - completed}")
        logger.info("=" * 80)

        # 4. Notificar
        if completed > 0:
            send_notification(
                f"✅ Ciclo concluído!\n"
                f"• Completadas: {completed}/{len(tasks_to_execute)}\n"
                f"• Falhadas: {failed}\n"
                f"• Backlog restante: {len(tasks) - completed}\n"
                f"• Duração: {cycle_duration/60:.1f}min",
                "success" if failed == 0 else "warning"
            )

    except Exception as e:
        logger.error(f"❌ Erro crítico no ciclo: {e}", exc_info=True)
        send_notification(
            f"🚨 ERRO CRÍTICO\n```{str(e)[:200]}```",
            "critical"
        )


def main():
    """Loop principal infinito"""
    logger.info("🤖 OpenClaw Agent iniciado!")
    logger.info(f"📁 Workspace: {WORKSPACE}")
    logger.info(f"⏱️ Intervalo: {INTERVAL}s ({INTERVAL/60:.0f}min)")
    logger.info(f"🎯 Cobertura mínima: {MIN_COVERAGE}%")
    logger.info(f"📊 Max tarefas por ciclo: {MAX_TASKS_PER_CYCLE}")

    send_notification(
        "🤖 OpenClaw Agent iniciado!\n"
        f"• Intervalo: {INTERVAL/60:.0f}min\n"
        f"• Meta cobertura: {MIN_COVERAGE}%\n"
        f"• Max tarefas/ciclo: {MAX_TASKS_PER_CYCLE}",
        "info"
    )

    cycle_count = 0

    while True:
        try:
            cycle_count += 1
            heartbeat()  # Health check

            logger.info(f"\n{'='*80}")
            logger.info(f"CICLO #{cycle_count}")
            logger.info(f"{'='*80}\n")

            main_cycle()

            logger.info(f"\n⏳ Aguardando {INTERVAL}s até próximo ciclo...\n")
            time.sleep(INTERVAL)

        except KeyboardInterrupt:
            logger.info("\n\n👋 OpenClaw Agent encerrado pelo usuário")
            send_notification("👋 OpenClaw Agent foi parado manualmente", "info")
            break
        except Exception as e:
            logger.error(f"❌ Erro no loop principal: {e}", exc_info=True)
            send_notification(f"🚨 Erro no loop principal\n```{str(e)[:200]}```", "error")
            logger.info("⏳ Aguardando 5min antes de retry...")
            time.sleep(300)


if __name__ == "__main__":
    main()
