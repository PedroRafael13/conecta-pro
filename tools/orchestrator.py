"""
ORCHESTRATOR - Coordena Developer, Auditor e Validator
Pipeline: Developer -> Auditor -> Validator
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import logging

# Configurar logging
log_dir = Path("/opt/erp-conecta-mais/logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "orchestrator.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("Orchestrator")

# Imports dos agentes
from code.developer_agent import DeveloperAgent
from auditor.auditor_agent import AuditorAgent
from validator.validator_agent import ValidatorAgent


class Orchestrator:
    """
    Orquestra o fluxo: Developer -> Auditor -> Validator
    Com retry automatico e relatorios detalhados.
    """

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path("/opt/erp-conecta-mais")
        self.tasks_queue: List[Dict] = []
        self.completed_tasks: List[Dict] = []
        self.failed_tasks: List[Dict] = []
        self.max_retries = 3

    def execute_task(self, task: Dict[str, Any]) -> bool:
        """
        Executa uma tarefa completa passando pelos 3 agentes.

        Args:
            task: Dicionario com informacoes da tarefa
                {
                    "id": "TASK-001",
                    "name": "CRM - Gestão de Leads",
                    "module": "commercial",
                    "requirements": ["RF-CRM-001", "RF-CRM-002"],
                    "priority": "high"
                }

        Returns:
            bool: True se tarefa concluida com sucesso
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"INICIANDO TAREFA: {task['name']} (ID: {task['id']})")
        logger.info(f"{'='*60}\n")

        task["started_at"] = datetime.now().isoformat()
        task["retry_count"] = 0

        # Loop de retry
        while task["retry_count"] < self.max_retries:
            # FASE 1: DEVELOPER
            logger.info("\n" + "-" * 60)
            logger.info("FASE 1: DEVELOPER AGENT")
            logger.info("-" * 60)

            developer_success, developer_result = self._run_developer(task)

            if not developer_success:
                task["retry_count"] += 1
                logger.warning(
                    f"Developer falhou. Tentativa {task['retry_count']}/{self.max_retries}"
                )
                continue

            # FASE 2: AUDITOR
            logger.info("\n" + "-" * 60)
            logger.info("FASE 2: AUDITOR AGENT")
            logger.info("-" * 60)

            auditor_success, auditor_result = self._run_auditor(task, developer_result)

            if not auditor_success:
                task["retry_count"] += 1
                logger.warning(
                    f"Auditor rejeitou. Tentativa {task['retry_count']}/{self.max_retries}"
                )
                task["auditor_feedback"] = auditor_result.get("issues", [])
                continue

            # FASE 3: VALIDATOR
            logger.info("\n" + "-" * 60)
            logger.info("FASE 3: VALIDATOR AGENT")
            logger.info("-" * 60)

            validator_success, validator_result = self._run_validator(
                task, auditor_result
            )

            if not validator_success:
                task["retry_count"] += 1
                logger.warning(
                    f"Validator rejeitou. Tentativa {task['retry_count']}/{self.max_retries}"
                )
                task["validator_feedback"] = validator_result.get("issues", [])
                continue

            # SUCESSO! Todas as fases passaram
            task["status"] = "COMPLETED"
            task["completed_at"] = datetime.now().isoformat()
            task["results"] = {
                "developer": developer_result,
                "auditor": auditor_result,
                "validator": validator_result,
            }

            self.completed_tasks.append(task)
            self._save_task_report(task)

            logger.info(f"\n{'='*60}")
            logger.info(f"TAREFA CONCLUIDA COM SUCESSO: {task['name']}")
            logger.info(f"{'='*60}\n")

            return True

        # FALHOU apos max_retries
        task["status"] = "FAILED"
        task["failed_at"] = datetime.now().isoformat()
        self.failed_tasks.append(task)

        logger.error(f"\n{'='*60}")
        logger.error(f"TAREFA FALHOU: {task['name']}")
        logger.error(f"{'='*60}\n")

        return False

    def _run_developer(self, task: Dict[str, Any]) -> tuple:
        """Executa Developer Agent."""
        module_path = self.project_root / "backend" / "modules" / task.get("module", "core")

        developer = DeveloperAgent(module_path)
        success, result = developer.develop(task)

        if success:
            logger.info("Developer: APROVADO")
        else:
            logger.error(f"Developer: FALHOU - {result.get('errors', [])}")

        return success, result

    def _run_auditor(self, task: Dict[str, Any], developer_result: Dict) -> tuple:
        """Executa Auditor Agent."""
        module_path = self.project_root / "backend" / "modules" / task.get("module", "core")

        auditor = AuditorAgent(module_path)
        success, result = auditor.audit(developer_result)

        if success:
            logger.info(f"Auditor: APROVADO (Score: {result.get('score')}/100)")
        else:
            logger.error(f"Auditor: REJEITADO - {result.get('issues', [])}")

        return success, result

    def _run_validator(self, task: Dict[str, Any], auditor_result: Dict) -> tuple:
        """Executa Validator Agent."""
        module_path = self.project_root / "backend" / "modules" / task.get("module", "core")

        validator = ValidatorAgent(module_path)
        success, result = validator.validate(auditor_result)

        if success:
            logger.info("Validator: APROVADO - TAREFA ENTREGUE!")
        else:
            logger.error(f"Validator: REJEITADO - {result.get('issues', [])}")

        return success, result

    def _save_task_report(self, task: Dict[str, Any]):
        """Salva relatorio detalhado da tarefa."""
        report_dir = self.project_root / "reports"
        report_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"{task['id']}_{timestamp}_report.json"

        with open(report_file, "w") as f:
            json.dump(task, f, indent=2, default=str)

        logger.info(f"Relatorio salvo: {report_file}")

    def execute_sprint(self, sprint_tasks: List[Dict[str, Any]]):
        """
        Executa multiplas tarefas (sprint completo).

        Args:
            sprint_tasks: Lista de tarefas do sprint
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"INICIANDO SPRINT COM {len(sprint_tasks)} TAREFAS")
        logger.info(f"{'='*60}\n")

        for i, task in enumerate(sprint_tasks, 1):
            logger.info(f"\n[{i}/{len(sprint_tasks)}] Processando: {task.get('name')}")
            self.execute_task(task)

        # Relatorio final do sprint
        self._generate_sprint_report()

    def _generate_sprint_report(self):
        """Gera relatorio consolidado do sprint."""
        total = len(self.completed_tasks) + len(self.failed_tasks)
        completed = len(self.completed_tasks)
        failed = len(self.failed_tasks)
        success_rate = (completed / total * 100) if total > 0 else 0

        logger.info(f"\n{'='*60}")
        logger.info("RELATORIO DO SPRINT")
        logger.info(f"{'='*60}")
        logger.info(f"Total de tarefas: {total}")
        logger.info(f"Concluidas: {completed}")
        logger.info(f"Falhadas: {failed}")
        logger.info(f"Taxa de sucesso: {success_rate:.1f}%")
        logger.info(f"{'='*60}\n")

        # Salvar relatorio
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": total,
            "completed": completed,
            "failed": failed,
            "success_rate": success_rate,
            "completed_tasks": [t.get("id") for t in self.completed_tasks],
            "failed_tasks": [t.get("id") for t in self.failed_tasks],
        }

        report_dir = self.project_root / "reports"
        report_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"sprint_{timestamp}_summary.json"

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Relatorio do sprint salvo: {report_file}")


def main():
    """Interface de linha de comando."""
    import argparse

    parser = argparse.ArgumentParser(description="ERP Conecta Mais - Orchestrator")
    parser.add_argument("--task", help="Execute single task from JSON file")
    parser.add_argument("--sprint", help="Execute sprint from JSON file")
    parser.add_argument("--project-root", default="/opt/erp-conecta-mais", help="Project root path")

    args = parser.parse_args()

    project_root = Path(args.project_root)
    orchestrator = Orchestrator(project_root)

    if args.task:
        # Executar tarefa unica
        task_file = Path(args.task)
        if not task_file.exists():
            # Tentar em tasks/
            task_file = project_root / "tasks" / args.task
        if not task_file.exists():
            print(f"Arquivo nao encontrado: {args.task}")
            sys.exit(1)

        with open(task_file) as f:
            task = json.load(f)

        success = orchestrator.execute_task(task)
        sys.exit(0 if success else 1)

    elif args.sprint:
        # Executar sprint
        sprint_file = Path(args.sprint)
        if not sprint_file.exists():
            # Tentar em sprints/
            sprint_file = project_root / "sprints" / args.sprint
        if not sprint_file.exists():
            print(f"Arquivo nao encontrado: {args.sprint}")
            sys.exit(1)

        with open(sprint_file) as f:
            sprint_tasks = json.load(f)

        orchestrator.execute_sprint(sprint_tasks)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
