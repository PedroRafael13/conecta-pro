# 📚 Documentação Técnica - Conecta PRO v2.0

> Sistema ERP Enterprise para Gestão de Vigilância e Facilities

---

## 🚀 Comece Aqui

| Documento | Descrição | Público-Alvo |
|-----------|-----------|--------------|
| [ONBOARDING.md](./ONBOARDING.md) | Guia de configuração do ambiente de desenvolvimento | Novos desenvolvedores |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Visão geral da arquitetura e stack tecnológica | Arquitetos, Tech Leads |
| [MODULES_GUIDE.md](./MODULES_GUIDE.md) | Guia completo dos 34 módulos do sistema | Product Owners, Analistas |

---

## 📖 Referências de API

### APIs Core
| Documento | Módulos | Endpoints |
|-----------|---------|-----------|
| [API_REFERENCE_CORE_AUTH.md](./API_REFERENCE_CORE_AUTH.md) | Core, Autenticação | 17+ endpoints |
| [API_REFERENCE_FINANCIAL.md](./API_REFERENCE_FINANCIAL.md) | Financeiro, Fiscal, BI | 160+ endpoints |
| [API_REFERENCE_OPERACIONAL.md](./API_REFERENCE_OPERACIONAL.md) | Operacional, Escalas, Diaristas | 95+ endpoints |
| [API_REFERENCE_CRM_CLIENTS.md](./API_REFERENCE_CRM_CLIENTS.md) | CRM, Clientes, Comissões | 130+ endpoints |

**Total documentado:** 400+ endpoints REST

---

## 🏗️ Arquitetura e Design

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Arquitetura geral do sistema
  - Stack tecnológica
  - Diagramas Mermaid
  - Camadas (Clean Architecture)
  - Fluxo de dados
  - Integrações externas

---

## 📋 Guias de Módulos

- [MODULES_GUIDE.md](./MODULES_GUIDE.md) - Guia completo dos 34 módulos
  - Visão geral por categoria
  - Matriz de integração
  - Fluxos de negócio
  - Dependências técnicas

### Categorias de Módulos

| Categoria | Módulos | Status |
|-----------|---------|--------|
| **Comercial** | CRM, Clientes, Serviços, Recrutamento, Retenção | ✅ Completo |
| **Operacional** | Operacional, Campo, Agendador, Mobile, Monitoramento | ✅ Completo |
| **RH** | HR, Payroll, Saúde Ocupacional | ✅ Completo |
| **Financeiro** | Financial, BI, Reembolso, Licitações | ✅ Completo |
| **Documentação** | GED, Documentos, Document Kits, LGPD, Auditoria | ✅ Completo |
| **IA/Automação** | AI, Analytics, Automação, Fase5 | 🔄 Evolução |
| **Integrações** | Government, Banking, Notificações, Search | ✅ Completo |

---

## 🔒 Segurança e Conformidade

### 🚨 Patches de Correção CRÍTICOS

| Patch | Descrição | Status | Aplicação |
|-------|-----------|--------|-----------|
| [patches/PATCH_01_DEPENDENCIES.sh](./patches/PATCH_01_DEPENDENCIES.sh) | Atualização CVEs python-jose, next, react | 🔴 **CRÍTICO** | `chmod +x && ./PATCH_01_DEPENDENCIES.sh` |
| [patches/PATCH_02_SQL_INJECTION.py](./patches/PATCH_02_SQL_INJECTION.py) | Whitelist contra SQL Injection | 🔴 **CRÍTICO** | Copiar para `core/security/` |
| [patches/PATCH_03_LGPD_ENDPOINT.py](./patches/PATCH_03_LGPD_ENDPOINT.py) | Endpoint de exclusão LGPD | 🔴 **CRÍTICO** | Copiar para `modules/lgpd/` |
| [patches/PATCH_04_LOG_MASKING.py](./patches/PATCH_04_LOG_MASKING.py) | Mascaramento PII em logs | 🟠 **ALTO** | Copiar para `core/security/` |
| [patches/PATCH_05_DOCKER_SECURITY.yml](./patches/PATCH_05_DOCKER_SECURITY.yml) | Docker Compose hardenizado | 🟠 **ALTO** | Substituir docker-compose.yml |
| [patches/README.md](./patches/README.md) | **GUIA DE APLICAÇÃO** | 📖 | **COMECE AQUI** |

**⚠️ ATENÇÃO:** Execute os patches na ordem correta. Veja [patches/README.md](./patches/README.md).

### Documentação de Segurança

| Documento | Propósito | Prioridade |
|-----------|-----------|------------|
| [SECURITY_INDEX.md](./SECURITY_INDEX.md) | Central de segurança completa | 🔴 CRÍTICO |
| [SECURITY_CODE_AUDIT.md](./SECURITY_CODE_AUDIT.md) | Auditoria de código - vulnerabilidades | 🔴 CRÍTICO |
| [SECURITY_DEPENDENCIES.md](./SECURITY_DEPENDENCIES.md) | CVEs em dependências | 🔴 CRÍTICO |
| [LGPD_COMPLIANCE.md](./LGPD_COMPLIANCE.md) | Conformidade com LGPD | 🟠 ALTA |
| [SECURITY_CONFIGURATION.md](./SECURITY_CONFIGURATION.md) | Configurações de segurança | 🟠 ALTA |
| [SECURITY_ROADMAP.md](./SECURITY_ROADMAP.md) | Plano de remediação | 🟡 MÉDIA |

---

## 🔄 Changelog e Releases

- [CHANGELOG_AUTO.md](./CHANGELOG_AUTO.md) - Histórico de mudanças automatizado
  - Análise de 186+ commits
  - Categorização automática (Features, Fixes, Refactoring)
  - Timeline de desenvolvimento

---

## 🛠️ Desenvolvimento

### Setup do Ambiente
```bash
# 1. Clone o repositório
git clone <repo-url> conecta-pro
cd conecta-pro

# 2. Configure variáveis de ambiente
cp .env.example .env

# 3. Inicie a infraestrutura
docker-compose up -d postgres redis

# 4. Setup backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload

# 5. Setup frontend
cd frontend
npm install
npm run dev
```

**Acesse:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8080/docs
- Health Check: http://localhost:8080/health

### Comandos Úteis

| Comando | Descrição |
|---------|-----------|
| `npm run build` | Build do frontend |
| `npm run type-check` | Verificação TypeScript |
| `npm run test:e2e` | Testes E2E com Playwright |
| `pytest` | Testes backend |
| `alembic revision --autogenerate -m "desc"` | Nova migration |
| `docker-compose logs -f` | Logs dos serviços |

---

## 📊 Estatísticas do Projeto

| Métrica | Valor |
|---------|-------|
| **Módulos** | 34 |
| **Endpoints API** | 400+ |
| **Linhas de Código Backend** | ~150.000 |
| **Linhas de Código Frontend** | ~75.000 |
| **Tecnologias** | Python, TypeScript, React, PostgreSQL, Redis |
| **Documentos** | 8 arquivos |

---

## 🧩 Stack Tecnológica

### Backend
- **Framework:** FastAPI 0.115
- **Python:** 3.12
- **ORM:** SQLAlchemy 2.0
- **Database:** PostgreSQL 16
- **Cache:** Redis 7
- **Task Queue:** Celery
- **Migrations:** Alembic

### Frontend
- **Framework:** Next.js 16
- **React:** 19
- **Language:** TypeScript 5.x
- **Styling:** Tailwind CSS 4.x
- **UI Components:** Radix UI
- **State:** Zustand
- **Query:** TanStack Query

### DevOps
- **Container:** Docker & Docker Compose
- **Proxy:** Nginx
- **Versionamento:** Git

---

## 🔐 Segurança

- Autenticação JWT com refresh tokens
- Rate limiting por endpoint
- CORS configurável
- Headers de segurança (HSTS, CSP, X-Frame)
- Validação de inputs com Pydantic
- SQL Injection prevention (SQLAlchemy ORM)

---

## 🤝 Contribuição

1. Leia o [ONBOARDING.md](./ONBOARDING.md)
2. Entenda a [ARQUITETURA](./ARCHITECTURE.md)
3. Consulte o [MODULES_GUIDE.md](./MODULES_GUIDE.md) para contexto de negócio
4. Verifique a [API Reference](#referências-de-api) para integrações

---

## 📞 Suporte

- **Documentação Existente:** Veja também `CLAUDE.md` e `AGENTS.md` na raiz
- **Issues:** [GitHub Issues](https://github.com/...)
- **Wiki:** [Confluence/Notion interno]

---

*Documentação gerada automaticamente em 2026-02-05*

*Conecta PRO v2.0 - ERP para Vigilância e Facilities*
