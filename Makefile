# Conecta PRO - Makefile
# Automacao de desenvolvimento, testes, qualidade e deploy
# ============================================================================

.PHONY: help setup dev test lint security deploy clean
.DEFAULT_GOAL := help

# Variaveis
PROJECT_ROOT := /opt/conecta-pro
BACKEND_DIR  := $(PROJECT_ROOT)/backend
FRONTEND_DIR := $(PROJECT_ROOT)/frontend
PYTHON       := python3
DOCKER_COMP  := docker compose

# ============================================================================
# HELP
# ============================================================================
help:
	@echo ""
	@echo "Conecta PRO - Makefile"
	@echo "============================================================================"
	@echo ""
	@echo "  SETUP & DESENVOLVIMENTO"
	@echo "  --------------------------------------------------------------------------"
	@echo "  make setup            - Setup inicial do ambiente"
	@echo "  make dev              - Rodar backend em modo dev (uvicorn --reload)"
	@echo "  make dev-frontend     - Rodar frontend em modo dev (next dev)"
	@echo "  make shell            - Acessar shell Python"
	@echo ""
	@echo "  DOCKER"
	@echo "  --------------------------------------------------------------------------"
	@echo "  make up               - Subir todos os containers"
	@echo "  make down             - Parar todos os containers"
	@echo "  make restart          - Restart todos os containers"
	@echo "  make rebuild SVC=x    - Rebuild e restart de um servico"
	@echo "  make logs SVC=x       - Logs de um servico (ou todos)"
	@echo "  make ps               - Status dos containers"
	@echo ""
	@echo "  TESTES & QUALIDADE"
	@echo "  --------------------------------------------------------------------------"
	@echo "  make test             - Testes backend (pytest)"
	@echo "  make test-unit        - Testes unitarios"
	@echo "  make test-cov         - Testes com cobertura (min 60%)"
	@echo "  make test-frontend    - Testes frontend (vitest)"
	@echo "  make lint             - Lint backend (ruff) + frontend (eslint)"
	@echo "  make lint-fix         - Auto-fix lint"
	@echo "  make security         - Security scan (bandit)"
	@echo "  make type-check       - Type check frontend (tsc)"
	@echo ""
	@echo "  OPENCLAW"
	@echo "  --------------------------------------------------------------------------"
	@echo "  make openclaw         - Ciclo completo do OpenClaw"
	@echo "  make openclaw-health  - Apenas health checks"
	@echo "  make openclaw-report  - Exibir ultimo relatorio"
	@echo "  make openclaw-daemon  - Iniciar modo daemon"
	@echo "  make openclaw-install - Instalar servico systemd"
	@echo ""
	@echo "  DATABASE"
	@echo "  --------------------------------------------------------------------------"
	@echo "  make db-migrate       - Executar migracoes (alembic upgrade head)"
	@echo "  make db-revision MSG=x- Nova revisao de migracao"
	@echo "  make db-downgrade     - Reverter ultima migracao"
	@echo ""
	@echo "  INFRAESTRUTURA"
	@echo "  --------------------------------------------------------------------------"
	@echo "  make nginx-reload     - Reload do Nginx"
	@echo "  make nginx-test       - Testar config do Nginx"
	@echo "  make ssl-init         - Inicializar SSL (Let's Encrypt)"
	@echo "  make ssl-renew        - Renovar certificado SSL"
	@echo "  make monitoring-up    - Subir stack de monitoring"
	@echo "  make monitoring-down  - Parar stack de monitoring"
	@echo ""
	@echo "  DEPLOY"
	@echo "  --------------------------------------------------------------------------"
	@echo "  make deploy-staging   - Deploy para staging"
	@echo "  make deploy-prod      - Deploy para production"
	@echo ""
	@echo "  UTILIDADES"
	@echo "  --------------------------------------------------------------------------"
	@echo "  make clean            - Limpar caches e temporarios"
	@echo "  make health           - Health check rapido dos servicos"
	@echo "  make notify MSG=x CH=discord - Enviar notificacao"
	@echo ""

# ============================================================================
# SETUP
# ============================================================================
setup:
	@echo "Setup inicial do ambiente..."
	@mkdir -p $(PROJECT_ROOT)/{logs,reports,uploads,credentials}
	@mkdir -p $(PROJECT_ROOT)/logs/{openclaw,nginx}
	@mkdir -p $(PROJECT_ROOT)/reports/openclaw
	@cd $(BACKEND_DIR) && pip install -r requirements.txt
	@echo "Setup concluido!"

setup-dev: setup
	@echo "Instalando dependencias de desenvolvimento..."
	@cd $(BACKEND_DIR) && pip install ruff bandit pytest pytest-cov pytest-asyncio httpx
	@cd $(FRONTEND_DIR) && npm install
	@echo "Dev setup concluido!"

# ============================================================================
# DESENVOLVIMENTO
# ============================================================================
dev:
	@echo "Iniciando backend em modo dev..."
	@cd $(BACKEND_DIR) && $(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8080

dev-frontend:
	@echo "Iniciando frontend em modo dev..."
	@cd $(FRONTEND_DIR) && npm run dev

shell:
	@cd $(BACKEND_DIR) && $(PYTHON)

# ============================================================================
# DOCKER
# ============================================================================
up:
	@cd $(PROJECT_ROOT) && $(DOCKER_COMP) up -d

down:
	@cd $(PROJECT_ROOT) && $(DOCKER_COMP) down

restart:
	@cd $(PROJECT_ROOT) && $(DOCKER_COMP) restart

rebuild:
ifndef SVC
	$(error SVC nao definido. Use: make rebuild SVC=backend)
endif
	@cd $(PROJECT_ROOT) && $(DOCKER_COMP) build $(SVC) --no-cache && $(DOCKER_COMP) up -d $(SVC)

logs:
ifdef SVC
	@cd $(PROJECT_ROOT) && $(DOCKER_COMP) logs -f $(SVC)
else
	@cd $(PROJECT_ROOT) && $(DOCKER_COMP) logs -f --tail=100
endif

ps:
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=conecta-pro"

# ============================================================================
# TESTES
# ============================================================================
test:
	@echo "Executando testes backend..."
	@cd $(BACKEND_DIR) && $(PYTHON) -m pytest tests/ -v --tb=short

test-unit:
	@cd $(BACKEND_DIR) && $(PYTHON) -m pytest tests/ -v -k "not integration"

test-integration:
	@cd $(BACKEND_DIR) && $(PYTHON) -m pytest tests/ -v -k "integration"

test-cov:
	@echo "Executando testes com cobertura..."
	@cd $(BACKEND_DIR) && $(PYTHON) -m pytest tests/ -v \
		--cov=modules --cov=core --cov=api --cov=domains \
		--cov-report=term-missing --cov-report=html \
		--cov-fail-under=60

test-frontend:
	@echo "Executando testes frontend..."
	@cd $(FRONTEND_DIR) && npx vitest run

# ============================================================================
# LINTING
# ============================================================================
lint:
	@echo "Lint backend (ruff)..."
	@cd $(BACKEND_DIR) && $(PYTHON) -m ruff check .
	@echo "Lint frontend (eslint)..."
	@cd $(FRONTEND_DIR) && npx eslint . --max-warnings=0 2>/dev/null || true
	@echo "Lint concluido!"

lint-fix:
	@echo "Auto-fix backend (ruff)..."
	@cd $(BACKEND_DIR) && $(PYTHON) -m ruff check --fix .
	@cd $(BACKEND_DIR) && $(PYTHON) -m ruff format .
	@echo "Auto-fix frontend (eslint)..."
	@cd $(FRONTEND_DIR) && npx eslint . --fix 2>/dev/null || true
	@echo "Formatacao corrigida!"

type-check:
	@echo "Type check frontend..."
	@cd $(FRONTEND_DIR) && npx tsc --noEmit

# ============================================================================
# SECURITY
# ============================================================================
security:
	@echo "Security scan (bandit)..."
	@cd $(BACKEND_DIR) && $(PYTHON) -m bandit -r modules/ core/ api/ -ll || true

# ============================================================================
# OPENCLAW
# ============================================================================
openclaw:
	@$(PYTHON) $(PROJECT_ROOT)/scripts/openclaw/runner.py

openclaw-health:
	@$(PYTHON) $(PROJECT_ROOT)/scripts/openclaw/runner.py --only health

openclaw-report:
	@$(PYTHON) $(PROJECT_ROOT)/scripts/openclaw/runner.py --report

openclaw-daemon:
	@$(PYTHON) $(PROJECT_ROOT)/scripts/openclaw/runner.py --daemon

openclaw-install:
	@sudo bash $(PROJECT_ROOT)/scripts/openclaw/install.sh

# ============================================================================
# DATABASE
# ============================================================================
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

# ============================================================================
# INFRAESTRUTURA
# ============================================================================
nginx-reload:
	@docker exec conecta-pro-nginx nginx -s reload

nginx-test:
	@docker exec conecta-pro-nginx nginx -t

ssl-init:
	@sudo bash $(PROJECT_ROOT)/scripts/init-letsencrypt.sh

ssl-renew:
	@sudo certbot renew --quiet --deploy-hook 'docker exec conecta-pro-nginx nginx -s reload'

monitoring-up:
	@cd $(PROJECT_ROOT)/monitoring && $(DOCKER_COMP) up -d

monitoring-down:
	@cd $(PROJECT_ROOT)/monitoring && $(DOCKER_COMP) down

# ============================================================================
# DEPLOY
# ============================================================================
deploy-staging:
	@echo "Deploy para staging..."
	@cd $(PROJECT_ROOT) && $(DOCKER_COMP) pull
	@cd $(PROJECT_ROOT) && $(DOCKER_COMP) build
	@cd $(PROJECT_ROOT) && $(DOCKER_COMP) up -d
	@echo "Deploy staging concluido!"

deploy-prod:
	@echo "Deploy para production..."
	@cd $(PROJECT_ROOT) && $(DOCKER_COMP) pull
	@cd $(PROJECT_ROOT) && $(DOCKER_COMP) build --no-cache
	@cd $(PROJECT_ROOT) && $(DOCKER_COMP) up -d
	@docker exec conecta-pro-nginx nginx -s reload 2>/dev/null || true
	@echo "Deploy production concluido!"

# ============================================================================
# UTILIDADES
# ============================================================================
clean:
	@echo "Limpando caches e temporarios..."
	@find $(PROJECT_ROOT) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find $(PROJECT_ROOT) -type f -name "*.pyc" -delete 2>/dev/null || true
	@find $(PROJECT_ROOT) -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find $(PROJECT_ROOT) -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find $(PROJECT_ROOT) -type d -name ".next" -path "*/frontend/.next" -exec rm -rf {} + 2>/dev/null || true
	@find $(PROJECT_ROOT) -type d -name "node_modules/.cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Limpeza concluida!"

health:
	@echo "Health check dos servicos..."
	@$(PYTHON) $(PROJECT_ROOT)/scripts/openclaw/runner.py --only health 2>&1 || true

notify:
ifndef MSG
	$(error MSG nao definido. Use: make notify MSG="texto" CH=discord)
endif
	@bash $(PROJECT_ROOT)/scripts/notify.sh $(or $(CH),all) "$(MSG)"
