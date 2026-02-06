# Conecta PRO - Backend

> **Stack:** Python 3.12 + FastAPI 0.115.6 + SQLAlchemy 2.0.36 + PostgreSQL 16 + Redis 7
> **Entry point prod:** `main_production.py` | **Entry point dev:** `main.py`
> **Última atualização:** 27/01/2026

---

## Arquitetura

```
backend/
├── main_production.py          # Entry point produção (uvicorn)
├── main.py                     # Entry point dev
├── core/
│   ├── config/
│   │   ├── settings.py         # Pydantic Settings (env vars centralizadas)
│   │   └── credentials.py      # Credenciais gov (certificado, eSocial, SEFAZ)
│   ├── auth/                   # JWT authentication
│   ├── cache/                  # Redis operations
│   ├── database/
│   │   └── session.py          # AsyncSession (FastAPI) + SyncSession (Celery)
│   ├── logging/                # Loguru structured logging
│   ├── models/
│   │   ├── base.py             # Base, BaseModel, TimestampMixin, SoftDeleteMixin
│   │   └── user.py             # User model
│   ├── schemas/                # Auth/User Pydantic schemas
│   ├── security/               # Hashing, JWT utils
│   └── monitoring/             # Prometheus metrics
├── modules/                    # 32 módulos de negócio
├── infrastructure/             # Message bus + Persistence
├── alembic/                    # Migrations
│   ├── env.py                  # Importa todos os models para autogenerate
│   └── versions/               # 16+ migrations
├── tests/                      # pytest (unit, integration, e2e)
├── requirements.txt            # ~80 dependências
├── pyproject.toml              # Black, isort, pylint config
└── Dockerfile                  # Multi-stage (builder + runtime)
```

---

## Padrão de Camadas por Módulo

```
modules/{modulo}/
├── models/          # SQLAlchemy ORM (herdam BaseModel)
├── schemas/         # Pydantic v2 DTOs (from_attributes = True)
├── controllers/     # FastAPI routers (endpoints)
├── repositories/    # Data access layer (queries async)
├── services/        # Business logic
└── [submodulos]/    # Funcionalidades específicas
```

---

## Base Model

```python
# core/models/base.py
class BaseModel(Base):
    __abstract__ = True
    id: Mapped[uuid.UUID]        # UUID v4, primary key
    created_at: Mapped[datetime]  # server_default=func.now()
    updated_at: Mapped[datetime]  # onupdate=func.now()
    is_active: Mapped[bool]       # default=True

class TimestampMixin:  # created_at + updated_at
class SoftDeleteMixin: # is_active + deleted_at
```

---

## Database Session

```python
# core/database/session.py

# Async (FastAPI endpoints)
engine = create_async_engine(settings.database_url)  # asyncpg
async_session_factory = async_sessionmaker(engine, class_=AsyncSession)
async def get_db() -> AsyncGenerator[AsyncSession, None]: ...

# Sync (Celery tasks)
sync_engine = create_engine(url.replace("+asyncpg", ""))  # psycopg2
SyncSessionLocal = sessionmaker(bind=sync_engine)
def get_sync_db(): ...  # context manager
```

---

## Settings (Pydantic)

```python
# core/config/settings.py
class Settings(BaseSettings):
    # App
    app_name, app_version, debug, environment
    # Server
    host="0.0.0.0", port=8080
    # Database
    database_url (PostgreSQL+asyncpg), pool_size=10, max_overflow=20
    # Redis
    redis_url, redis_ttl=3600
    # JWT
    secret_key, algorithm="HS256", access_token_expire_minutes=30, refresh_token_expire_days=7
    # CORS, Logging (json), Sentry
```

---

## Módulos (32 total)

| Módulo | Prefixo API | Descrição |
|--------|-------------|-----------|
| **operacional** | `/api/v1/operacional` | Postos, escalas, turnos, colaboradores, rondas, diaristas, ocorrências |
| **clients** | `/api/v1/clients` | Clientes + Condomínios |
| **crm** | `/api/v1/crm` | Leads, oportunidades, propostas, contratos, comissões |
| **financial** | `/api/v1/financial` | Contabilidade, contas, bancos, cashflow, compras, estoque |
| **hr** | `/api/v1/hr` | RH, ponto, folha, portal, REP, analytics |
| **ged** | `/api/v1/ged` | Gestão eletrônica de documentos |
| **document_kits** | `/api/v1/document-kits` | Kits documentais + scheduler mensal |
| **government_integrations** | `/api/v1/government` | eSocial, SEFAZ, NFS-e, FGTS, SPED |
| **notifications** | `/api/v1/notifications` | Push notifications + triggers |
| **ai/bartolo** | `/api/v1/ai` | Assistente IA (GPT-4) |
| **bidding** | `/api/v1/bidding` | Licitações |
| **recruitment** | `/api/v1/recruitment` | Recrutamento |
| **analytics** | - | Analytics e dashboards |
| **audit** | - | Auditoria |
| **security_lgpd** | - | LGPD compliance |
| **reports** | - | Geração de relatórios |
| **scheduler** | - | Agendamento de tarefas |
| automation, campo, config, documents, equipment_management, health_occupational, integrations, mobile, monitoring, reimbursement, retention, search, services, fase5 | - | Outros módulos |

---

## Routers Registrados (main_production.py)

Usa `safe_import()` para carregamento dinâmico com fallback:

```python
def safe_import(module_path: str, router_name: str = "router"):
    """Importa módulo com fallback - não quebra o app se módulo falhar."""
```

**Routers do operacional (11):** post, scale, scale_template, shift, allocation, employee, substitution, time_bank, reports, kpi_trends, occurrence

**Routers do financial (13):** accounting, supplier, payable, customer, receivable_category, receivable, billing_rule, bank_account, bank_transaction, bank_reconciliation, cashflow, purchase, inventory

**Routers do CRM (6):** lead, opportunity, proposal, contract, commission, dashboard

---

## Integrações Governamentais

```
modules/government_integrations/
├── core/                          # Managers e engines
│   ├── certificate_manager.py     # Certificados A1
│   ├── xml_signer.py              # XMLDSig
│   ├── nfse_manaus.py             # ABRASF 2.04 (SOAP)
│   ├── nfse_nacional.py           # Padrão Nacional (REST, prep 2026)
│   ├── esocial_transmitter.py
│   ├── sefaz_manager.py
│   ├── fgts_digital.py
│   ├── efd_reinf.py, dctfweb.py
│   ├── sped_fiscal.py, sped_contabil.py
│   ├── cte.py, mdfe.py
│   ├── govbr.py, ecac.py
│   └── simples_nacional.py
├── controllers/                   # REST endpoints
├── services/                      # Business logic
└── schemas/                       # Validação
```

**NFS-e Manaus:** ABRASF 2.04, SOAP/XML, código 11.02 (vigilância, ISS 5%)
**Sync:** 12 serviços gov, sync em background, agendamento configurável

---

## Celery Workers

| Worker | Fila | Responsabilidade |
|--------|------|-----------------|
| celery-priority | priority | eSocial, FGTS |
| celery-sefaz | sefaz | NF-e, CT-e, MDF-e |
| celery-nfse | nfse | NFS-e local |
| celery-operacional | operacional | Tasks operacionais |
| celery-batch | batch | Processamento em lote |
| celery-integrations | integrations | Integrações externas |
| celery-beat | - | Scheduler |

---

## Dependências Principais

| Categoria | Pacotes |
|-----------|---------|
| Framework | fastapi 0.115.6, uvicorn 0.34.0, pydantic 2.10.4 |
| ORM | sqlalchemy 2.0.36, alembic 1.14.0, asyncpg 0.30.0, psycopg2-binary 2.9.10 |
| Cache/Queue | redis 5.2.1, celery 5.4.0, apscheduler 3.10.4 |
| Auth | python-jose 3.3.0, passlib 1.7.4, bcrypt 4.2.1, pyotp 2.9.0 |
| Monitoring | sentry-sdk 1.40.0, loguru 0.7.3, slowapi 0.1.9 |
| Data | pandas 2.2.3, scikit-learn 1.6.0, numpy 1.26.4 |
| HTTP/AI | httpx 0.28.1, aiohttp 3.11.11, openai 1.0+ |
| Security | cryptography 42.0+, pyOpenSSL 24.0+, defusedxml 0.7.1 |
| XML | lxml 5.0+ |
| Testing | pytest 8.3.4, pytest-asyncio 0.25.0, pytest-cov 6.0.0 |
| Code | black 24.10.0, isort 5.13.2, pylint 3.3.2, mypy 1.14.0 |

---

## Code Quality

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ["py312"]

[tool.isort]
profile = "black"
line_length = 100
known_first_party = ["core", "modules"]

[tool.pylint]
max-line-length = 100
```

---

## Problemas Conhecidos

1. **Dessincronização Banco/Models** — Campos no model que não existem no banco:
   - `document_kits.extra_metadata` (nao existe)
   - `condominiums.phone`, `condominiums.phone_portaria` (nao existem)
   - `condominiums.is_active` no model vs `ativo` no banco
   - `condominiums.type` removido do model, existe como `condominium_type` no banco
   - Workaround: raw SQL via `sqlalchemy.text()` em alguns services

2. **Alembic env.py** — Importa models manualmente (não autodescoberta). Ao criar novo model, adicionar import no `alembic/env.py`.

---

## Comandos

```bash
# Rebuild + restart
docker compose build backend --no-cache && docker compose up -d backend

# Logs
docker logs -f conecta-pro-backend

# Shell no container
docker exec -it conecta-pro-backend bash

# PostgreSQL
docker exec -it conecta-pro-postgres psql -U postgres -d conecta_pro

# Testes
python3 -m pytest tests/ -v
python3 -m pytest tests/test_nfse_manaus.py -v

# Migrations
alembic revision --autogenerate -m "Descrição"
alembic upgrade head
alembic downgrade -1

# Health
curl http://localhost:8080/health
```
