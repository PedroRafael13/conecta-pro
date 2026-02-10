# Ambiente de Execução — Conecta PRO

**Última atualização:** 2026-02-09 por Claude Opus 4.6

## Onde Você Está
- **Ambiente:** HOST (VPS Ubuntu 24.04 LTS)
- **NÃO é container Docker.** Não use paths como `/app/`.
- **Usuário:** root
- **Shell:** bash

## Python
- **Executável:** `/opt/conecta-pro/backend/venv/bin/python` (Python 3.12)
- **SEMPRE ativar venv ANTES de rodar qualquer comando Python:**
  ```bash
  cd /opt/conecta-pro/backend && source venv/bin/activate
  ```
- **SEM venv:** `python3` do sistema NÃO tem: defusedxml, faker, e outras deps do projeto
- **COM venv:** Tudo disponível (defusedxml, faker, pytest, ruff, bandit, etc.)

## Node.js / Frontend
- **Diretório:** `/opt/conecta-pro/frontend`
- **Node:** instalado globalmente
- **Pacotes:** em `node_modules/` (npm install já executado)

## Docker
- **9 containers rodando** (conecta-pro-backend, frontend, postgres, redis, nginx, celery workers)
- **Container backend:** usa `/app/` como working dir e tem deps diferentes
- **ATENÇÃO:** Host e container podem ter versões diferentes de pacotes (ex: python-jose vs PyJWT)

## Caminhos Importantes
```
/opt/conecta-pro/                    # Raiz do projeto
├── backend/                          # FastAPI + Python
│   ├── venv/                         # Virtualenv (SEMPRE ativar)
│   ├── tests/                        # Testes pytest
│   │   └── _orphaned/               # Testes desabilitados (NÃO rodam)
│   ├── modules/                      # Módulos de negócio
│   └── core/                         # Core (auth, models, etc.)
├── frontend/                         # Next.js + React + TypeScript
│   ├── src/                          # Código fonte
│   │   ├── api/generated/            # NUNCA EDITAR (gerado por Orval)
│   │   └── types/generated/          # NUNCA EDITAR (gerado por Orval)
│   └── node_modules/                 # Deps npm
├── .comms/                           # Comunicação inter-IA
├── .kimi/                            # Configuração e regras Kimi
├── .agents/                          # Skills e AGENTS.md
└── scripts/                          # Scripts operacionais
```

## Comandos EXATOS (copiar e colar)

### Backend
```bash
# Ativar venv (OBRIGATÓRIO antes de qualquer comando Python)
cd /opt/conecta-pro/backend && source venv/bin/activate

# Ruff (linting)
cd /opt/conecta-pro/backend && source venv/bin/activate && ruff check .

# Pytest collection
cd /opt/conecta-pro/backend && source venv/bin/activate && python -m pytest --collect-only -q

# Pytest run completo
cd /opt/conecta-pro/backend && source venv/bin/activate && python -m pytest --tb=no -q

# Pytest módulo específico
cd /opt/conecta-pro/backend && source venv/bin/activate && python -m pytest tests/domains/financial/ -v

# Alembic
cd /opt/conecta-pro/backend && source venv/bin/activate && alembic heads

# Bandit
cd /opt/conecta-pro/backend && source venv/bin/activate && bandit -r . -ll -q
```

### Frontend
```bash
# TypeScript check
cd /opt/conecta-pro/frontend && npx tsc --noEmit

# ESLint (SEMPRE usar este, NUNCA `next lint`)
cd /opt/conecta-pro/frontend && npx eslint . --no-error-on-unmatched-pattern

# Build
cd /opt/conecta-pro/frontend && npm run build
```

### Verificação completa
```bash
/opt/conecta-pro/scripts/verify-all.sh          # Completa (~2min)
/opt/conecta-pro/scripts/verify-quick.sh         # Rápida (~30s, sem Bandit/test run)
FULL_TEST=true /opt/conecta-pro/scripts/verify-all.sh  # Com test run (~15min)
```

### Atalhos disponíveis (se `.bashrc` carregado)
```bash
cpb        # cd backend + ativa venv automaticamente
cpro       # cd /opt/conecta-pro
cpf        # cd frontend
verify     # verify-all.sh
verify-full # verify-all.sh com test run completo
```

### Auto-venv
O venv é ativado AUTOMATICAMENTE ao entrar em `/opt/conecta-pro/backend/`.
Se usar `cd` direto, o `PROMPT_COMMAND` do `.bashrc` cuida disso.
Para scripts, SEMPRE ativar explicitamente: `source venv/bin/activate`.
