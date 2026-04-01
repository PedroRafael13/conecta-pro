# 🚀 Guia de Onboarding - Conecta PRO

> **Bem-vindo ao time!** Este guia vai te ajudar a configurar o ambiente de desenvolvimento do Conecta PRO em poucos minutos.

---

## 📋 Pré-requisitos

### Softwares Obrigatórios

| Software | Versão Mínima | Download |
|----------|---------------|----------|
| Docker | 24.0+ | [docker.com](https://docs.docker.com/get-docker/) |
| Docker Compose | 2.20+ | Incluso no Docker Desktop |
| Node.js | 20.x LTS | [nodejs.org](https://nodejs.org/) |
| Python | 3.11+ | [python.org](https://python.org) |
| Git | 2.40+ | [git-scm.com](https://git-scm.com/) |

### Verificação de Pré-requisitos

```bash
# Verifique se tudo está instalado
docker --version           # Docker version 24.0.x
docker compose version     # Docker Compose version v2.20.x
node --version             # v20.x.x
python3 --version          # Python 3.11.x
git --version              # git version 2.40.x
```

### Opcionais (Recomendados)

- **VS Code** com extensões:
  - Python
  - ESLint
  - Prettier
  - Docker
  - Thunder Client (para testes de API)
- **pgAdmin** ou **DBeaver** (para gerenciar PostgreSQL)
- **Redis Insight** (para visualizar cache Redis)

---

## 🛠️ Setup Passo a Passo

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-org/conecta-pro.git
cd conecta-pro
```

### 2. Configure as Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
# Mínimo necessário para desenvolvimento:
```

**Configurações mínimas para desenvolvimento:**

```env
# Application
APP_NAME=Conecta PRO
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Backend
BACKEND_PORT=8080

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=conecta_pro
POSTGRES_PORT=5432

# Redis
REDIS_PORT=6379
REDIS_TTL=3600

# JWT Security
JWT_SECRET_KEY=dev_secret_key_32_chars_minimum_ok
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# APIs Externas (opcional para desenvolvimento)
WHATSAPP_API_ENABLED=false
GOOGLE_MAPS_ENABLED=false
```

### 3. Inicie a Infraestrutura com Docker

```bash
# Inicie PostgreSQL e Redis
docker compose up -d postgres redis

# Verifique se os containers estão rodando
docker compose ps
```

**Saída esperada:**
```
NAME                   IMAGE                STATUS
conecta-pro-postgres   postgres:16-alpine   Up 10 seconds (healthy)
conecta-pro-redis      redis:7-alpine       Up 10 seconds (healthy)
```

### 4. Setup do Backend

```bash
# Acesse o diretório do backend
cd backend

# Crie o ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Execute as migrações do banco de dados
alembic upgrade head

# (Opcional) Popule com dados de exemplo
python scripts/seed_dev_data.py
```

**Principais dependências do backend:**
- FastAPI 0.115.6 - Framework web
- SQLAlchemy 2.0.36 - ORM de banco de dados
- Alembic 1.14.0 - Migrações de banco
- Celery 5.4.0 - Filas de tarefas
- Redis 5.2.1 - Cache e broker

### 5. Setup do Frontend

```bash
# Acesse o diretório do frontend
cd ../frontend

# Instale as dependências
npm install

# Gere os clientes da API (requer backend rodando)
npm run api:generate
```

**Principais tecnologias do frontend:**
- Next.js 14 - Framework React
- TypeScript - Tipagem estática
- Tailwind CSS - Estilização
- Orval - Gerador de clientes API
- React Query - Gerenciamento de estado servidor

### 6. Inicie o Servidor de Desenvolvimento

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 7. Acesse a Aplicação

- 🌐 **Frontend:** http://localhost:3000
- 🔧 **API Docs:** http://localhost:8080/docs
- 📊 **Adminer (DB):** http://localhost:8081 (se configurado)

---

## ⌨️ Comandos Úteis

### Docker

```bash
# Iniciar todos os serviços
docker compose up -d

# Ver logs
docker compose logs -f backend
docker compose logs -f postgres

# Parar todos os serviços
docker compose down

# Parar e remover volumes (⚠️ cuidado - apaga dados!)
docker compose down -v

# Rebuildar containers
docker compose up -d --build
```

### Backend

```bash
# Acesse o diretório
cd backend
source venv/bin/activate

# Executar migrações
alembic upgrade head

# Criar nova migração
alembic revision --autogenerate -m "descrição"

# Reverter última migração
alembic downgrade -1

# Executar testes
pytest
pytest -xvs tests/test_specific.py

# Formatar código
black app/
ruff check app/

# Type checking
mypy app/
```

### Frontend

```bash
# Acesse o diretório
cd frontend

# Desenvolvimento
npm run dev

# Build de produção
npm run build

# Linting
npm run lint

# Type checking
npm run type-check

# Gerar clientes API específicos
npm run orval:core
npm run orval:clients
npm run orval:hr

# Analisar bundle
npm run analyze
```

### Banco de Dados

```bash
# Acessar PostgreSQL via Docker
docker exec -it conecta-pro-postgres psql -U postgres -d conecta_pro

# Comandos úteis no psql
\dt              # Listar tabelas
\d users         # Descrever tabela
\q               # Sair

# Backup
docker exec conecta-pro-postgres pg_dump -U postgres conecta_pro > backup.sql

# Restore
docker exec -i conecta-pro-postgres psql -U postgres -d conecta_pro < backup.sql
```

### Redis

```bash
# Acessar CLI Redis
docker exec -it conecta-pro-redis redis-cli

# Comandos úteis
KEYS *           # Listar todas as chaves
FLUSHALL         # Limpar todo o cache (⚠️ cuidado!)
INFO             # Informações do servidor
```

---

## 🐛 Troubleshooting Comum

### Erro: "Port already in use"

```bash
# Encontre o processo usando a porta
lsof -i :8080
# ou
netstat -tlnp | grep 8080

# Mate o processo
kill -9 <PID>
```

### Erro: "Module not found" no backend

```bash
# Reinstale as dependências
cd backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Erro: "Connection refused" para PostgreSQL

```bash
# Verifique se o container está rodando
docker compose ps

# Se estiver unhealthy, verifique os logs
docker compose logs postgres

# Recrie o container
docker compose down
docker compose up -d postgres

# Verifique a conexão
docker exec -it conecta-pro-postgres pg_isready -U postgres
```

### Erro: "Cannot find module" no frontend

```bash
# Limpe o cache e reinstale
cd frontend
rm -rf node_modules package-lock.json
npm install

# Se persistir, limpe também o cache do Next.js
rm -rf .next
npm run dev
```

### Erro: Alembic "Can't locate revision"

```bash
# Reset completo (⚠️ apaga dados!)
docker compose down -v
docker compose up -d postgres
cd backend
alembic upgrade head
```

### Erro: "permission denied" no Docker

```bash
# Linux - adicione seu usuário ao grupo docker
sudo usermod -aG docker $USER
# Faça logout e login novamente
```

### Frontend não conecta ao backend

1. Verifique se o backend está rodando: `curl http://localhost:8080/health`
2. Confira se `CORS_ORIGINS` no `.env` inclui `http://localhost:3000`
3. Verifique se não há firewall bloqueando a porta

### Hot reload não funciona

```bash
# Frontend - force reload
npm run dev -- --turbo

# Backend - use watchgod
uvicorn app.main:app --reload --reload-dir ./app
```

---

## 📁 Estrutura do Projeto

```
conecta-pro/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/            # Rotas e endpoints
│   │   ├── core/           # Configurações
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── schemas/        # Pydantic models
│   │   ├── services/       # Lógica de negócio
│   │   └── main.py         # Entry point
│   ├── alembic/            # Migrações
│   ├── tests/              # Testes
│   └── requirements.txt    # Dependências
├── frontend/               # Next.js App
│   ├── src/
│   │   ├── app/           # App Router (Next.js 14)
│   │   ├── components/    # Componentes React
│   │   ├── lib/           # Utilitários
│   │   └── hooks/         # Custom hooks
│   ├── orval.config.ts    # Config geração API
│   └── package.json
├── docker-compose.yml     # Orquestração
├── .env.example           # Template de variáveis
└── docs/                  # Documentação
```

---

## 🧪 Rodando Testes

### Backend

```bash
cd backend
source venv/bin/activate

# Todos os testes
pytest

# Com cobertura
pytest --cov=app --cov-report=html

# Testes específicos
pytest tests/test_auth.py -xvs

# Testes de integração
pytest tests/integration/ -m integration
```

### Frontend

```bash
cd frontend

# Testes unitários
npm test

# Testes E2E (se configurado)
npm run test:e2e
```

---

## 🚀 Comandos para Produção

```bash
# Build completo
docker compose -f docker-compose.yml up -d --build

# Verificar saúde
curl https://erp.conectamais.pro/api/v1/health

# Logs em produção
docker compose logs -f --tail 100
```

---

## 💡 Dicas de Produtividade

1. **Use Make:** Existe um `Makefile` na raiz com comandos comuns:
   ```bash
   make help        # Lista comandos disponíveis
   make dev         # Inicia ambiente de dev
   make test        # Roda todos os testes
   make migrate     # Executa migrações
   ```

2. **Aliases úteis** (adicione ao `.bashrc` ou `.zshrc`):
   ```bash
   alias cp-up='docker compose up -d'
   alias cp-down='docker compose down'
   alias cp-logs='docker compose logs -f'
   alias cp-be='cd /opt/conecta-pro/backend && source venv/bin/activate'
   alias cp-fe='cd /opt/conecta-pro/frontend'
   ```

3. **VS Code Snippets:** Configure snippets para padrões comuns do projeto

---

## 📚 Recursos Adicionais

- [Documentação da API](http://localhost:8080/docs)
- [CHANGELOG.md](../CHANGELOG.md) - Histórico de mudanças
- [CLAUDE.md](../CLAUDE.md) - Contexto do projeto para IA
- [AGENTS.md](../AGENTS.md) - Guia para agentes de código

---

## ❓ Precisa de Ajuda?

1. Consulte a documentação em `/docs`
2. Verifique issues no GitHub
3. Pergunte no canal `#dev-conecta-pro` no Slack
4. Abra um ticket no Jira se encontrar bugs

---

**Happy coding! 🎉**

*Última atualização: Fevereiro 2026*
