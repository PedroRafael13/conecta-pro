# ERP Conecta Mais V2.0

Sistema ERP completo para gestão de empresas de segurança.

## Status do Projeto

**Sprint Atual:** Sprint 0 - Core
**Progresso:** 5%

## Stack Tecnológica

### Backend
- Python 3.12 + FastAPI
- SQLAlchemy + Alembic
- PostgreSQL 16
- Redis 7

### Frontend
- Next.js 16 + React 19
- TypeScript + Tailwind

## Estrutura do Projeto

```
/opt/erp-conecta-mais/
├── backend/
│   ├── api/           # Endpoints REST
│   ├── core/          # Núcleo do sistema
│   │   ├── auth/      # Autenticação JWT
│   │   ├── cache/     # Redis cache
│   │   ├── config/    # Configurações
│   │   ├── database/  # Conexão PostgreSQL
│   │   ├── logging/   # Sistema de logs
│   │   ├── models/    # SQLAlchemy models
│   │   └── schemas/   # Pydantic schemas
│   ├── modules/       # Módulos de negócio
│   │   ├── commercial/
│   │   ├── financial/
│   │   ├── hr/
│   │   └── operations/
│   ├── tests/         # Testes pytest
│   └── alembic/       # Migrações
├── frontend/          # Next.js app
├── docs/              # Documentação
├── sessions/          # Histórico de desenvolvimento
└── backups/           # Backups do banco
```

## Desenvolvimento

Projeto desenvolvido com assistência do Claude Code.

- **Histórico:** `sessions/SESSION_MANAGER.md`
- **Progresso:** `docs/PROGRESSO_GERAL.md`

## Execução

```bash
# Ativar ambiente
cd /opt/erp-conecta-mais/backend
source venv/bin/activate

# Rodar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Rodar testes
pytest -v --cov
```

## Licença

Proprietário - Conecta Mais
