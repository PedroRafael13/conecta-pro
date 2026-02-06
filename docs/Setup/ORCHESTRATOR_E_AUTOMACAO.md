# 🎯 ORCHESTRATOR E AUTOMAÇÃO COMPLETA

## SISTEMA QUE COORDENA OS 3 AGENTES

---

## 🎼 ORCHESTRATOR PRINCIPAL

**Arquivo:** `/opt/erp-conecta-mais/tools/orchestrator.py`

```python
"""
ORCHESTRATOR - Coordena Developer, Auditor e Validator
"""

import sys
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import logging

# Imports dos agentes
from code.developer_agent import DeveloperAgent
from auditor.auditor_agent import AuditorAgent
from validator.validator_agent import ValidatorAgent

# Logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/erp-conecta-mais/logs/orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Orquestra o fluxo: Developer → Auditor → Validator
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tasks_queue = []
        self.completed_tasks = []
        self.failed_tasks = []
        self.max_retries = 3
    
    def execute_task(self, task: Dict) -> bool:
        """
        Executa uma tarefa completa passando pelos 3 agentes
        
        task = {
            "id": "TASK-001",
            "name": "CRM - Gestão de Leads",
            "module": "commercial",
            "requirements": ["RF-CRM-001", "RF-CRM-002"],
            "priority": "high"
        }
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 INICIANDO TAREFA: {task['name']} (ID: {task['id']})")
        logger.info(f"{'='*60}\n")
        
        task['started_at'] = datetime.now().isoformat()
        task['retry_count'] = 0
        
        # Loop de retry
        while task['retry_count'] < self.max_retries:
            # FASE 1: DEVELOPER
            developer_success, developer_result = self._run_developer(task)
            
            if not developer_success:
                task['retry_count'] += 1
                logger.warning(f"⚠️  Developer falhou. Tentativa {task['retry_count']}/{self.max_retries}")
                continue
            
            # FASE 2: AUDITOR
            auditor_success, auditor_result = self._run_auditor(task, developer_result)
            
            if not auditor_success:
                task['retry_count'] += 1
                logger.warning(f"⚠️  Auditor rejeitou. Tentativa {task['retry_count']}/{self.max_retries}")
                # Feedback para developer
                task['auditor_feedback'] = auditor_result.get('issues', [])
                continue
            
            # FASE 3: VALIDATOR
            validator_success, validator_result = self._run_validator(task, auditor_result)
            
            if not validator_success:
                task['retry_count'] += 1
                logger.warning(f"⚠️  Validator rejeitou. Tentativa {task['retry_count']}/{self.max_retries}")
                # Feedback para developer
                task['validator_feedback'] = validator_result.get('issues', [])
                continue
            
            # ✅ SUCESSO! Todas as fases passaram
            task['status'] = 'COMPLETED'
            task['completed_at'] = datetime.now().isoformat()
            task['results'] = {
                'developer': developer_result,
                'auditor': auditor_result,
                'validator': validator_result
            }
            
            self.completed_tasks.append(task)
            self._save_task_report(task)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"✅ TAREFA CONCLUÍDA COM SUCESSO: {task['name']}")
            logger.info(f"{'='*60}\n")
            
            return True
        
        # ❌ FALHOU após max_retries
        task['status'] = 'FAILED'
        task['failed_at'] = datetime.now().isoformat()
        self.failed_tasks.append(task)
        
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ TAREFA FALHOU: {task['name']}")
        logger.error(f"{'='*60}\n")
        
        return False
    
    def _run_developer(self, task: Dict) -> tuple:
        """
        Executa Developer Agent
        """
        logger.info("🤖 FASE 1: DEVELOPER AGENT")
        logger.info("-" * 60)
        
        module_path = self.project_root / "backend" / "modules" / task['module']
        
        developer = DeveloperAgent(module_path)
        success, result = developer.develop(task)
        
        if success:
            logger.info("✅ Developer: APROVADO")
        else:
            logger.error(f"❌ Developer: FALHOU - {result.get('error')}")
        
        return success, result
    
    def _run_auditor(self, task: Dict, developer_result: Dict) -> tuple:
        """
        Executa Auditor Agent
        """
        logger.info("\n🔍 FASE 2: AUDITOR AGENT")
        logger.info("-" * 60)
        
        module_path = self.project_root / "backend" / "modules" / task['module']
        
        auditor = AuditorAgent(module_path)
        success, result = auditor.audit(developer_result)
        
        if success:
            logger.info(f"✅ Auditor: APROVADO (Score: {result.get('score')}/100)")
        else:
            logger.error(f"❌ Auditor: REJEITADO - {result.get('error')}")
            logger.error(f"Issues: {result.get('issues')}")
        
        return success, result
    
    def _run_validator(self, task: Dict, auditor_result: Dict) -> tuple:
        """
        Executa Validator Agent
        """
        logger.info("\n✅ FASE 3: VALIDATOR AGENT")
        logger.info("-" * 60)
        
        module_path = self.project_root / "backend" / "modules" / task['module']
        
        validator = ValidatorAgent(module_path)
        success, result = validator.validate(auditor_result)
        
        if success:
            logger.info("✅ Validator: APROVADO - TAREFA ENTREGUE!")
        else:
            logger.error(f"❌ Validator: REJEITADO - {result.get('error')}")
            logger.error(f"Issues: {result.get('issues')}")
        
        return success, result
    
    def _save_task_report(self, task: Dict):
        """
        Salva relatório detalhado da tarefa
        """
        report_dir = self.project_root / "reports"
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"{task['id']}_report.json"
        
        with open(report_file, 'w') as f:
            json.dump(task, f, indent=2)
        
        logger.info(f"📄 Relatório salvo: {report_file}")
    
    def execute_sprint(self, sprint_tasks: List[Dict]):
        """
        Executa múltiplas tarefas (sprint completo)
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🏃 INICIANDO SPRINT COM {len(sprint_tasks)} TAREFAS")
        logger.info(f"{'='*60}\n")
        
        for task in sprint_tasks:
            self.execute_task(task)
        
        # Relatório final do sprint
        self._generate_sprint_report()
    
    def _generate_sprint_report(self):
        """
        Gera relatório consolidado do sprint
        """
        total = len(self.completed_tasks) + len(self.failed_tasks)
        completed = len(self.completed_tasks)
        failed = len(self.failed_tasks)
        success_rate = (completed / total * 100) if total > 0 else 0
        
        logger.info(f"\n{'='*60}")
        logger.info("📊 RELATÓRIO DO SPRINT")
        logger.info(f"{'='*60}")
        logger.info(f"Total de tarefas: {total}")
        logger.info(f"Concluídas: {completed} ✅")
        logger.info(f"Falhadas: {failed} ❌")
        logger.info(f"Taxa de sucesso: {success_rate:.1f}%")
        logger.info(f"{'='*60}\n")


# ═══════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════

def main():
    """
    Interface de linha de comando
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='ERP Conecta Mais - Orchestrator')
    parser.add_argument('--task', help='Execute single task from JSON file')
    parser.add_argument('--sprint', help='Execute sprint from JSON file')
    parser.add_argument('--module', help='Module name')
    
    args = parser.parse_args()
    
    project_root = Path("/opt/erp-conecta-mais")
    orchestrator = Orchestrator(project_root)
    
    if args.task:
        # Executar tarefa única
        with open(args.task) as f:
            task = json.load(f)
        
        success = orchestrator.execute_task(task)
        sys.exit(0 if success else 1)
    
    elif args.sprint:
        # Executar sprint
        with open(args.sprint) as f:
            sprint_tasks = json.load(f)
        
        orchestrator.execute_sprint(sprint_tasks)
    
    else:
        print("Use --task ou --sprint")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## 📝 EXEMPLO DE ARQUIVO DE TAREFA

**Arquivo:** `/opt/erp-conecta-mais/tasks/task_001_crm_leads.json`

```json
{
  "id": "TASK-001",
  "name": "CRM - Gestão de Leads",
  "module": "commercial",
  "requirements": [
    "RF-CRM-001: Captura de Leads",
    "RF-CRM-002: Qualificação Automática (IA)",
    "RF-CRM-003: Distribuição Inteligente"
  ],
  "files_to_create": [
    "models/lead.py",
    "schemas/lead_schema.py",
    "services/lead_service.py",
    "repositories/lead_repository.py",
    "controllers/lead_controller.py"
  ],
  "tests_to_create": [
    "tests/unit/test_lead_model.py",
    "tests/unit/test_lead_service.py",
    "tests/integration/test_lead_api.py"
  ],
  "priority": "high",
  "estimated_hours": 16
}
```

---

## 📝 EXEMPLO DE ARQUIVO DE SPRINT

**Arquivo:** `/opt/erp-conecta-mais/sprints/sprint_01.json`

```json
[
  {
    "id": "TASK-001",
    "name": "CRM - Gestão de Leads",
    "module": "commercial",
    "requirements": ["RF-CRM-001", "RF-CRM-002", "RF-CRM-003"],
    "priority": "high"
  },
  {
    "id": "TASK-002",
    "name": "CRM - Gestão de Oportunidades",
    "module": "commercial",
    "requirements": ["RF-CRM-005", "RF-CRM-006", "RF-CRM-007"],
    "priority": "high"
  },
  {
    "id": "TASK-003",
    "name": "Autenticação e Autorização",
    "module": "core",
    "requirements": ["RF-SEC-001", "RF-SEC-002"],
    "priority": "critical"
  }
]
```

---

## 🔄 CI/CD PIPELINE AUTOMÁTICO

### GitHub Actions Workflow

**Arquivo:** `.github/workflows/ci-cd.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  # ═══════════════════════════════════════════════════════════
  # JOB 1: BUILD & TEST
  # ═══════════════════════════════════════════════════════════
  build-and-test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: erp_user
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: erp_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
          pip install -r backend/requirements-dev.txt
      
      - name: Run linters
        run: |
          cd backend
          black --check .
          isort --check .
          pylint modules/
          mypy modules/
      
      - name: Run security scan
        run: |
          cd backend
          bandit -r modules/
          safety check
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://erp_user:test_password@localhost:5432/erp_test
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd backend
          pytest -v --cov --cov-report=xml --cov-report=term-missing
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
          fail_ci_if_error: true
  
  # ═══════════════════════════════════════════════════════════
  # JOB 2: SECURITY AUDIT
  # ═══════════════════════════════════════════════════════════
  security-audit:
    runs-on: ubuntu-latest
    needs: build-and-test
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'
      
      - name: Run OWASP Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'ERP Conecta Mais'
          path: '.'
          format: 'ALL'
  
  # ═══════════════════════════════════════════════════════════
  # JOB 3: BUILD DOCKER IMAGE
  # ═══════════════════════════════════════════════════════════
  build-docker:
    runs-on: ubuntu-latest
    needs: [build-and-test, security-audit]
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: |
            conectamais/erp-backend:latest
            conectamais/erp-backend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
  
  # ═══════════════════════════════════════════════════════════
  # JOB 4: DEPLOY TO STAGING
  # ═══════════════════════════════════════════════════════════
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build-docker
    if: github.ref == 'refs/heads/develop'
    
    steps:
      - name: Deploy to staging
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd /opt/erp-conecta-mais
            docker-compose pull
            docker-compose up -d
            docker-compose exec -T backend alembic upgrade head
  
  # ═══════════════════════════════════════════════════════════
  # JOB 5: DEPLOY TO PRODUCTION
  # ═══════════════════════════════════════════════════════════
  deploy-production:
    runs-on: ubuntu-latest
    needs: build-docker
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/erp-conecta-mais
            docker-compose pull
            docker-compose up -d --no-deps backend
            docker-compose exec -T backend alembic upgrade head
      
      - name: Run smoke tests
        run: |
          # Aguardar serviço subir
          sleep 30
          # Testar health endpoint
          curl -f https://api.conectamaistech.com.br/health || exit 1
```

---

## 🔧 MAKEFILE PARA AUTOMAÇÃO LOCAL

**Arquivo:** `/opt/erp-conecta-mais/Makefile`

```makefile
.PHONY: help setup dev test lint security audit validate deploy

# ═══════════════════════════════════════════════════════════
# HELP
# ═══════════════════════════════════════════════════════════
help:
	@echo "ERP Conecta Mais - Makefile"
	@echo ""
	@echo "Comandos disponíveis:"
	@echo "  make setup          - Setup inicial do ambiente"
	@echo "  make dev            - Rodar ambiente de desenvolvimento"
	@echo "  make test           - Rodar testes"
	@echo "  make lint           - Rodar linters"
	@echo "  make security       - Security scan"
	@echo "  make audit          - Code audit"
	@echo "  make validate       - Validação final"
	@echo "  make deploy         - Deploy"
	@echo "  make task TASK=001  - Executar tarefa específica"
	@echo "  make sprint SPRINT=01 - Executar sprint completo"

# ═══════════════════════════════════════════════════════════
# SETUP
# ═══════════════════════════════════════════════════════════
setup:
	@echo "🔧 Setup inicial..."
	./scripts/setup_server.sh
	./scripts/create_structure.sh
	./scripts/setup_python.sh
	./scripts/setup_postgres.sh
	docker-compose up -d
	cd backend && alembic upgrade head
	@echo "✅ Setup concluído!"

# ═══════════════════════════════════════════════════════════
# DEVELOPMENT
# ═══════════════════════════════════════════════════════════
dev:
	@echo "🚀 Iniciando ambiente de desenvolvimento..."
	docker-compose up -d postgres redis mongodb
	cd backend && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# ═══════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════
test:
	@echo "🧪 Executando testes..."
	cd backend && pytest -v --cov --cov-report=term-missing --cov-report=html

test-unit:
	cd backend && pytest tests/unit -v

test-integration:
	cd backend && pytest tests/integration -v

test-e2e:
	cd backend && pytest tests/e2e -v

# ═══════════════════════════════════════════════════════════
# LINTING
# ═══════════════════════════════════════════════════════════
lint:
	@echo "🔍 Executando linters..."
	cd backend && black .
	cd backend && isort .
	cd backend && pylint modules/
	cd backend && mypy modules/

# ═══════════════════════════════════════════════════════════
# SECURITY
# ═══════════════════════════════════════════════════════════
security:
	@echo "🔒 Security scan..."
	cd backend && bandit -r modules/
	cd backend && safety check

# ═══════════════════════════════════════════════════════════
# CODE AUDIT
# ═══════════════════════════════════════════════════════════
audit:
	@echo "🔍 Code audit..."
	python tools/auditor/auditor_agent.py --module $(MODULE)

# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════
validate:
	@echo "✅ Validação final..."
	python tools/validator/validator_agent.py --module $(MODULE)

# ═══════════════════════════════════════════════════════════
# TASKS & SPRINTS
# ═══════════════════════════════════════════════════════════
task:
	@echo "🚀 Executando tarefa $(TASK)..."
	python tools/orchestrator.py --task tasks/task_$(TASK).json

sprint:
	@echo "🏃 Executando sprint $(SPRINT)..."
	python tools/orchestrator.py --sprint sprints/sprint_$(SPRINT).json

# ═══════════════════════════════════════════════════════════
# DEPLOY
# ═══════════════════════════════════════════════════════════
deploy-staging:
	@echo "🚀 Deploy para staging..."
	./scripts/deploy_staging.sh

deploy-production:
	@echo "🚀 Deploy para production..."
	./scripts/deploy_production.sh

# ═══════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
```

---

## 🚀 COMO USAR

### 1. Executar Tarefa Única

```bash
cd /opt/erp-conecta-mais

# Executar tarefa específica
make task TASK=001

# Ou diretamente
python tools/orchestrator.py --task tasks/task_001_crm_leads.json
```

### 2. Executar Sprint Completo

```bash
# Executar sprint
make sprint SPRINT=01

# Ou diretamente
python tools/orchestrator.py --sprint sprints/sprint_01.json
```

### 3. Desenvolvimento Local

```bash
# Setup inicial (primeira vez)
make setup

# Rodar ambiente de desenvolvimento
make dev

# Em outro terminal: rodar testes
make test

# Linters
make lint

# Security scan
make security
```

---

## 📊 MONITORAMENTO E LOGS

Todos os logs ficam em:
- `/opt/erp-conecta-mais/logs/orchestrator.log`
- `/opt/erp-conecta-mais/logs/developer.log`
- `/opt/erp-conecta-mais/logs/auditor.log`
- `/opt/erp-conecta-mais/logs/validator.log`

Relatórios em:
- `/opt/erp-conecta-mais/reports/`

---

