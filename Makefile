# ERP Conecta Mais - Makefile
# Automacao de desenvolvimento, testes e deploy

.PHONY: help setup dev test lint security audit validate deploy clean

# Variaveis
PROJECT_ROOT := /opt/erp-conecta-mais
BACKEND_DIR := $(PROJECT_ROOT)/backend
PYTHON := $(BACKEND_DIR)/venv/bin/python
PIP := $(BACKEND_DIR)/venv/bin/pip

# ═══════════════════════════════════════════════════════════
# HELP
# ═══════════════════════════════════════════════════════════
help:
	@echo ""
	@echo "ERP Conecta Mais - Makefile"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@echo "Comandos disponiveis:"
	@echo ""
	@echo "  SETUP & DESENVOLVIMENTO"
	@echo "  ─────────────────────────────────────────────────────────"
	@echo "  make setup          - Setup inicial do ambiente"
	@echo "  make dev            - Rodar ambiente de desenvolvimento"
	@echo "  make shell          - Acessar shell Python"
	@echo ""
	@echo "  TESTES & QUALIDADE"
	@echo "  ─────────────────────────────────────────────────────────"
	@echo "  make test           - Rodar todos os testes"
	@echo "  make test-unit      - Rodar testes unitarios"
	@echo "  make test-cov       - Testes com cobertura"
	@echo "  make lint           - Rodar linters (black, isort)"
	@echo "  make lint-fix       - Corrigir formatacao automaticamente"
	@echo "  make security       - Security scan (bandit)"
	@echo ""
	@echo "  AGENTES DE AUTOMACAO"
	@echo "  ─────────────────────────────────────────────────────────"
	@echo "  make audit MODULE=core     - Executar Auditor Agent"
	@echo "  make validate MODULE=core  - Executar Validator Agent"
	@echo "  make task TASK=001         - Executar tarefa especifica"
	@echo "  make sprint SPRINT=01      - Executar sprint completo"
	@echo ""
	@echo "  DEPLOY"
	@echo "  ─────────────────────────────────────────────────────────"
	@echo "  make deploy-staging    - Deploy para staging"
	@echo "  make deploy-production - Deploy para production"
	@echo ""
	@echo "  OUTROS"
	@echo "  ─────────────────────────────────────────────────────────"
	@echo "  make clean          - Limpar arquivos temporarios"
	@echo "  make logs           - Ver logs do orchestrator"
	@echo "  make health         - Health check do sistema"
	@echo ""

# ═══════════════════════════════════════════════════════════
# SETUP
# ═══════════════════════════════════════════════════════════
setup:
	@echo "Setup inicial do ambiente..."
	@mkdir -p $(PROJECT_ROOT)/{logs,reports,tasks,sprints}
	@cd $(BACKEND_DIR) && python3 -m venv venv
	@$(PIP) install --upgrade pip
	@$(PIP) install -r $(BACKEND_DIR)/requirements.txt
	@echo "Setup concluido!"

setup-dev: setup
	@echo "Instalando dependencias de desenvolvimento..."
	@$(PIP) install black isort pylint mypy bandit pytest pytest-cov pytest-asyncio radon
	@echo "Dev setup concluido!"

# ═══════════════════════════════════════════════════════════
# DESENVOLVIMENTO
# ═══════════════════════════════════════════════════════════
dev:
	@echo "Iniciando ambiente de desenvolvimento..."
	@cd $(BACKEND_DIR) && $(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8080

shell:
	@cd $(BACKEND_DIR) && $(PYTHON)

# ═══════════════════════════════════════════════════════════
# TESTES
# ═══════════════════════════════════════════════════════════
test:
	@echo "Executando testes..."
	@cd $(BACKEND_DIR) && $(PYTHON) -m pytest tests/ -v --tb=short

test-unit:
	@cd $(BACKEND_DIR) && $(PYTHON) -m pytest tests/unit -v

test-integration:
	@cd $(BACKEND_DIR) && $(PYTHON) -m pytest tests/integration -v

test-cov:
	@echo "Executando testes com cobertura..."
	@cd $(BACKEND_DIR) && $(PYTHON) -m pytest tests/ -v --cov=core --cov=api --cov-report=term-missing --cov-report=html

# ═══════════════════════════════════════════════════════════
# LINTING
# ═══════════════════════════════════════════════════════════
lint:
	@echo "Executando linters..."
	@cd $(BACKEND_DIR) && $(PYTHON) -m black --check .
	@cd $(BACKEND_DIR) && $(PYTHON) -m isort --check-only .
	@echo "Lint OK!"

lint-fix:
	@echo "Corrigindo formatacao..."
	@cd $(BACKEND_DIR) && $(PYTHON) -m black .
	@cd $(BACKEND_DIR) && $(PYTHON) -m isort .
	@echo "Formatacao corrigida!"

# ═══════════════════════════════════════════════════════════
# SECURITY
# ═══════════════════════════════════════════════════════════
security:
	@echo "Security scan..."
	@cd $(BACKEND_DIR) && $(PYTHON) -m bandit -r core/ api/ -ll || true

# ═══════════════════════════════════════════════════════════
# AGENTES DE AUTOMACAO
# ═══════════════════════════════════════════════════════════
audit:
ifndef MODULE
	$(error MODULE nao definido. Use: make audit MODULE=core)
endif
	@echo "Executando Auditor Agent no modulo $(MODULE)..."
	@cd $(PROJECT_ROOT)/tools && $(PYTHON) auditor/auditor_agent.py --module $(MODULE)

validate:
ifndef MODULE
	$(error MODULE nao definido. Use: make validate MODULE=core)
endif
	@echo "Executando Validator Agent no modulo $(MODULE)..."
	@cd $(PROJECT_ROOT)/tools && $(PYTHON) validator/validator_agent.py --module $(MODULE)

task:
ifndef TASK
	$(error TASK nao definido. Use: make task TASK=001)
endif
	@echo "Executando tarefa $(TASK)..."
	@cd $(PROJECT_ROOT)/tools && $(PYTHON) orchestrator.py --task $(PROJECT_ROOT)/tasks/task_$(TASK).json

sprint:
ifndef SPRINT
	$(error SPRINT nao definido. Use: make sprint SPRINT=01)
endif
	@echo "Executando sprint $(SPRINT)..."
	@cd $(PROJECT_ROOT)/tools && $(PYTHON) orchestrator.py --sprint $(PROJECT_ROOT)/sprints/sprint_$(SPRINT).json

# ═══════════════════════════════════════════════════════════
# DEPLOY
# ═══════════════════════════════════════════════════════════
deploy-staging:
	@echo "Deploy para staging..."
	@echo "TODO: Implementar deploy staging"

deploy-production:
	@echo "Deploy para production..."
	@echo "TODO: Implementar deploy production"

# ═══════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════
clean:
	@echo "Limpando arquivos temporarios..."
	@find $(PROJECT_ROOT) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find $(PROJECT_ROOT) -type f -name "*.pyc" -delete 2>/dev/null || true
	@find $(PROJECT_ROOT) -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find $(PROJECT_ROOT) -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Limpeza concluida!"

logs:
	@echo "Ultimas 50 linhas do log do orchestrator:"
	@tail -50 $(PROJECT_ROOT)/logs/orchestrator.log 2>/dev/null || echo "Log nao encontrado"

health:
	@echo "Health check..."
	@$(PYTHON) $(PROJECT_ROOT)/scripts/health_monitor.py --api-url http://localhost:8080 || echo "Health check falhou"

# ═══════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════
db-migrate:
	@echo "Executando migracoes..."
	@cd $(BACKEND_DIR) && $(PYTHON) -m alembic upgrade head

db-revision:
ifndef MSG
	$(error MSG nao definido. Use: make db-revision MSG="descricao")
endif
	@cd $(BACKEND_DIR) && $(PYTHON) -m alembic revision --autogenerate -m "$(MSG)"

db-downgrade:
	@cd $(BACKEND_DIR) && $(PYTHON) -m alembic downgrade -1
