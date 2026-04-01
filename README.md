# Conecta PRO — ERP para Segurança e Tecnologia

Sistema ERP proprietário para gestão de empresas de segurança patrimonial.

## Status do Projeto

**Versão:** 1.0.0-rc | **Progresso:** 95% | **Última atualização:** 2026-04-01
**Score de Qualidade:** 10.0/10 (80 agentes, 13 módulos monitorados 24h)

## Stack Tecnológica

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Backend | Python + FastAPI + SQLAlchemy | 3.12 / 0.115 / 2.0 |
| Frontend | Next.js + React + TypeScript + Tailwind | 16 / 19 / 5 / 4 |
| Database | PostgreSQL + Redis | 16 / 7 |
| Task Queue | Celery + APScheduler | 5.4 / 3.10 |
| Auth | JWT (HS256) | — |

## Estrutura do Projeto

```
/opt/conecta-pro/
├── backend/           # FastAPI + SQLAlchemy
│   ├── api/           # Endpoints REST
│   ├── core/          # Núcleo (auth, cache, db, logging)
│   ├── modules/       # 9 módulos agregadores de negócio
│   └── alembic/       # Migrações de banco
├── frontend/          # Next.js 16 app
├── agents/            # Sistema de agentes autônomos 24h
│   ├── core/          # BaseAgent + BaseOrchestrator
│   └── modules/       # 13 orquestradores + 80 agentes
├── docs/              # Documentação técnica
│   └── RUNBOOK.md     # Runbook de incidentes
├── reports/           # Relatórios dos ciclos de monitoramento
└── logs/              # Logs do sistema
```

## Execução

```bash
# Backend (via Docker — não reinicializar manualmente)
docker ps | grep conecta-pro-backend

# Frontend
pm2 status
pm2 restart all

# Ciclo de monitoramento manual
cd /opt/conecta-pro
python3 agents/orchestrator_geral.py

# Token de autenticação
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

## Documentação

- **Arquitetura:** `docs/ARCHITECTURE.md`
- **Runbook de Incidentes:** `docs/RUNBOOK.md`
- **Módulos e API:** `docs/MODULES_GUIDE.md`
- **Guia do Desenvolvedor:** `CLAUDE.md`
- **Changelog:** `CHANGELOG.md`

## Licença

Proprietário — Conecta Mais (CNPJ 35.710.481/0001-03)
