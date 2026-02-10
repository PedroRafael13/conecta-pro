# 🤖 AGENTS.md - Conecta PRO v2.0
## Configuração Kimi CLI v1.9.0

---

## 📋 Contexto do Projeto

**Conecta PRO** é um ERP completo para empresas de Vigilância e Segurança Patrimonial.

| Aspecto | Detalhe |
|---------|---------|
| **Versão** | 2.0.0 |
| **Backend** | Python 3.12 + FastAPI 0.115.6 |
| **Frontend** | Next.js 16.1.6 + React 19.2.4 + TypeScript 5.9.3 |
| **Database** | PostgreSQL 16 + Redis 7 |
| **Task Queue** | Celery 5.4.0 + Redis |
| **Módulos Backend** | 33 |
| **Módulos Frontend** | 21 |

---

## 🏗️ Estrutura de Diretórios

### Backend (`/opt/conecta-pro/backend/`)
```
modules/                         # 33 módulos de negócio
├── ai/                         # IA/ML (OCR, Fraud Detection)
├── analytics/                  # Analytics e dashboards
├── audit/                      # Auditoria
├── automation/                 # Automações e workflows
├── bidding/                    # Licitações
├── campo/                      # Operações de campo
├── clients/                    # Clientes
├── config/                     # Configurações do sistema
├── core/                       # Core (auth, security, database)
├── crm/                        # CRM 360°
├── document_kits/              # Kits documentais
├── documents/                  # Documentos
├── equipment_management/       # Gestão de equipamentos
├── fase5/                      # Módulo Fase 5
├── financial/                  # Financeiro (483 endpoints)
├── ged/                        # Gestão Eletrônica de Documentos
├── government_integrations/    # eSocial, SEFAZ, NFS-e
├── health_occupational/        # Saúde Ocupacional
├── hr/                         # RH
├── integrations/               # Integrações externas
├── lgpd/                       # LGPD compliance
├── mobile/                     # API Mobile
├── monitoring/                 # Monitoramento e métricas
├── notifications/              # Notificações
├── operacional/                # Operações (postos, escalas, rondas)
├── recruitment/                # Recrutamento
├── reimbursement/              # Reembolsos
├── reports/                    # Relatórios
├── retention/                  # Retenção de dados
├── scheduler/                  # Agendador de tarefas
├── search/                     # Busca unificada
├── security_lgpd/              # Segurança + LGPD
└── services/                   # Serviços compartilhados

main.py                    # Entry point FastAPI
requirements.txt           # Dependências Python
alembic/                   # Migrations
```

### Frontend (`/opt/conecta-pro/frontend/`)
```
src/
├── app/modulos/           # 21 módulos
│   ├── crm/
│   ├── operacional/
│   ├── financeiro/
│   ├── licitacoes/
│   └── ...
├── components/ui/         # UI Components
├── hooks/                 # Custom hooks
├── api/                   # Orval generated clients
└── types/generated/       # Types gerados
```

---

## 🔄 Padrão de Camadas (OBRIGATÓRIO)

### Backend
```
Controller → Service → Repository → Model
```

**Exemplo:**
```python
# modules/crm/controllers/client_controller.py
@router.post("/clients", response_model=ClientResponse)
async def create_client(
    data: ClientCreate,
    service: ClientService = Depends(get_client_service)
):
    return await service.create(data)

# modules/crm/services/client_service.py
class ClientService:
    def __init__(self, repo: ClientRepository):
        self._repo = repo

    async def create(self, data: ClientCreate) -> Client:
        return await self._repo.create(data)

# modules/crm/repositories/client_repository.py
class ClientRepository:
    async def create(self, data: ClientCreate) -> Client:
        async with get_session() as session:
            ...
```

### Frontend (Arquitetura de Hooks)
```
Page → Root Hook → Wrapper → Orval Hook → customInstance
```

**Exemplo:**
```typescript
// app/modulos/crm/page.tsx
export default function CRMPage() {
  const { clients } = useCRM(); // Root hook
  return <ClientList data={clients} />;
}

// hooks/useCRM.ts (consolidado)
export function useCRM() {
  const { data: clients } = useGetClients(); // Orval hook
  return { clients };
}
```

---

## 🐳 Containers Docker

### Serviços Principais (5)
```bash
conecta-pro-backend      # FastAPI
conecta-pro-frontend     # Next.js
conecta-pro-postgres     # PostgreSQL 16
conecta-pro-redis        # Redis 7
conecta-pro-nginx        # Nginx reverse proxy
```

### Celery Workers (8) — via docker-compose.celery.yml
```bash
conecta-pro-celery-priority       # Filas: gov.esocial, gov.fgts
conecta-pro-celery-sefaz          # Filas: gov.sefaz.nfe, gov.sefaz.cte, gov.sefaz.mdfe
conecta-pro-celery-nfse           # Filas: gov.nfse
conecta-pro-celery-batch          # Filas: batch processing
conecta-pro-celery-integrations   # Filas: integrations
conecta-pro-celery-operacional    # Filas: operacional
conecta-pro-celery-beat           # Scheduler de tarefas periódicas
conecta-pro-flower                # Monitoramento Celery (UI)
```

### Comandos Docker Essenciais
```bash
# Ver status
docker ps --filter "name=conecta"

# Logs
docker logs -f conecta-pro-backend
docker logs -f conecta-pro-celery-default

# Shell
docker exec -it conecta-pro-backend bash
docker exec -it conecta-pro-postgres psql -U conecta_user conecta_pro

# Restart
docker restart conecta-pro-backend
docker restart conecta-pro-celery-default

# Build
cd /opt/conecta-pro && docker-compose build backend
```

---

## 🧪 Comandos de Desenvolvimento

### Backend
```bash
cd /opt/conecta-pro/backend

# Ativar venv
source venv/bin/activate

# Executar
python main.py
# ou
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Testes
pytest --cov=modules --cov-report=term-missing
pytest tests/modules/crm/ -v

# Migrations
alembic revision --autogenerate -m "descricao"
alembic upgrade head
alembic downgrade -1

# Linting
ruff check modules/
ruff check --fix modules/
black modules/
mypy modules/

# Código morto
vulture modules/ --min-confidence 80
```

### Frontend
```bash
cd /opt/conecta-pro/frontend

# Dev
npm run dev

# Build
npm run build

# Testes
npm run test:coverage
npm run test:e2e

# Type checking
npm run type-check

# Linting
npm run lint

# Orval (gerar APIs)
npm run api:generate
npm run orval:crm
npm run orval:financial
```

---

## 🔌 Integração Orval (CRÍTICO)

### Fluxo
1. Backend expõe OpenAPI em `/openapi.json`
2. Orval lê e gera hooks/tipos
3. NUNCA editar arquivos gerados manualmente

### Estrutura Gerada
```
src/
├── api/generated/         # Hooks React Query gerados
│   ├── auth.ts
│   ├── crm.ts
│   ├── financial.ts
│   ├── models/            # Types gerados
│   └── ...
└── types/generated/       # Types adicionais
```

### Regras
- ✅ Sempre usar hooks do Orval
- ✅ Customização via `src/lib/api.ts` (mutator) e `src/lib/api-client.ts`
- ❌ NUNCA editar arquivos em `src/api/generated/*`
- ❌ NUNCA editar arquivos em `src/types/generated/*`

---

## ⚠️ Problemas Conhecidos

### 1. Dessincronização Banco/Models
**Sintoma:** Erros de coluna inexistente
**Solução:**
```bash
# Verificar migrations pendentes
alembic current
alembic history

# Gerar migration de sync
alembic revision --autogenerate -m "sync models"

# Aplicar
alembic upgrade head
```

### 2. Celery Beat Parado
**Sintoma:** Tarefas agendadas não executam
**Solução:**
```bash
docker restart conecta-pro-celery-beat
docker logs conecta-pro-celery-beat
```

### 3. Bare Except
**ANTES (errado):**
```python
try:
    ...
except:  # ❌ NUNCA
    ...
```

**DEPOIS (correto):**
```python
try:
    ...
except SpecificException as e:  # ✅
    logger.error(f"Erro: {e}")
```

### 4. Enums PT vs EN
**ANTES (errado):**
```python
class Status(Enum):
    ATIVO = "ativo"  # ❌ pt
```

**DEPOIS (correto):**
```python
class Status(str, Enum):
    ACTIVE = "active"  # ✅ en
    ATIVO = "ativo"    # ✅ pt (se necessário)
```

---

## 🔒 Regras de Segurança

### JWT
```python
from modules.core.services.auth_service import get_current_user

@router.get("/protected")
async def protected(
    current_user: User = Depends(get_current_user)
):
    ...
```

### Rate Limiting
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
async def login(...):
    ...
```

### LGPD
- Módulos `lgpd/` e `security_lgpd/` existem
- Campos `is_active`, `deleted_at` para soft delete
- Logs de auditoria em `modules/audit/`

---

## 📝 Padrões de Código

### Python (Backend)
- **Imports:** `isort` (ordem: stdlib, third-party, local)
- **Formatação:** `black` (88 chars)
- **Tipagem:** `mypy` strict
- **Async:** Sempre usar `async/await` para I/O
- **Logging:** Usar `loguru` ou `logging`

### TypeScript (Frontend)
- **Strict:** `strict: true` no tsconfig
- **Componentes:** Function components + hooks
- **Estado:** Zustand (client) + React Query (server)
- **Forms:** RHF + Zod
- **Estilo:** Tailwind + Radix UI

---

## ✅ Checklist Antes de Qualquer Mudança

- [ ] Ler este AGENTS.md
- [ ] Verificar container: `docker ps --filter "name=conecta"`
- [ ] Rodar testes: `pytest` (backend) / `npm run test` (frontend)
- [ ] Type checking: `mypy modules/` / `npm run type-check`
- [ ] Linting: `ruff check modules/` / `npm run lint`
- [ ] Verificar migrations: `alembic current`

---

## 🔗 Endpoints por Módulo (Resumo)

| Módulo | Endpoints | Controllers |
|--------|-----------|-------------|
| financial | ~483 | 17 |
| crm | ~200 | 8 |
| operacional | ~130 | 14 |
| hr | ~150 | 10 |
| government_integrations | ~120 | 6 |
| documents | ~80 | 5 |
| ... | ... | ... |

---

## 📊 Métricas de Qualidade (Auditoria Pente Fino)

| Métrica | Valor | Meta |
|---------|-------|------|
| Cobertura Backend | 43.37% | >80% |
| Cobertura Frontend | 84.51% | >80% ✅ |
| Testes Backend | 6892 | - |
| Testes Frontend | 1985 | - |
| Bare Except | 0 | 0 ✅ |
| Rate Limiting | 40 | >0 ✅ |
| Security Headers | 0 | >0 ❌ |

---

## 🏆 REGRA DE OURO — QUALIDADE 99%+

> ⚠️ **MANDATÓRIO — NÃO NEGOCIÁVEL**

### Padrão de Qualidade Obrigatório

| Métrica | Mínimo Aceitável | Obrigatório |
|---------|------------------|-------------|
| **Cobertura de Testes** | 99% | ✅ SIM |
| **Type Safety** | 100% (strict mode) | ✅ SIM |
| **Linting** | 0 erros, 0 warnings | ✅ SIM |
| **Code Review** | Aprovação obrigatória | ✅ SIM |
| **Documentação** | 100% das APIs públicas | ✅ SIM |

### Checklist Pré-Commit (OBRIGATÓRIO)

Antes de qualquer commit:

- [ ] **Testes passando** — `pytest` (backend) ou `npm test` (frontend) = 100% pass
- [ ] **Cobertura 99%+** — `pytest --cov` ≥ 99% | `npm run test:coverage` ≥ 99%
- [ ] **Type checking** — `mypy` (backend) | `tsc --noEmit` (frontend) = 0 erros
- [ ] **Linting** — `ruff` (backend) | `eslint` (frontend) = 0 erros, 0 warnings
- [ ] **Security scan** — `bandit` (backend) | `npm audit` (frontend) = 0 críticos
- [ ] **Code review** — Revisado por outra IA ou humano
- [ ] **Documentação** — Docstrings (Python) | TSDoc (TypeScript) atualizadas

### Política de Erros

```
Qualidade < 99% = ❌ REJEITADO AUTOMATICAMENTE
Qualidade < 95% = ❌ NÃO PASSA DE JEITO NENHUM
Qualidade < 90% = 🚫 NEM CONSIDERAR
```

### Processo de Garantia de Qualidade

1. **Primeira Passada** — Implementar funcionalidade
2. **Testes** — Escrever testes unitários + integração (cobertura 99%+)
3. **Type Check** — Garantir 100% type safety
4. **Lint** — Corrigir todos erros e warnings
5. **Security** — Verificar vulnerabilidades
6. **Review** — Outra IA revisa (Claude ↔ Kimi)
7. **Documentação** — Atualizar docs
8. **Commit** — Só então commitar

### Frases Proibidas

❌ "Depois eu arrumo"
❌ "É só um teste"
❌ "Funciona, tá bom"
❌ "Cobertura 80% tá ok"
❌ "Só mais esse warning"

### Frases Obrigatórias

✅ "Vou aumentar a cobertura para 99%"
✅ "Deixe-me refatorar para 100% type safety"
✅ "Vou adicionar mais testes de edge case"
✅ "Revisando código antes de commitar"

---

## 🆘 Comandos de Emergência

```bash
# Reset completo (CUIDADO!)
cd /opt/conecta-pro
docker-compose down -v
docker-compose up -d --build

# Backup banco
docker exec conecta-pro-postgres pg_dump -U postgres conecta_pro > backup.sql

# Restore banco
docker exec -i conecta-pro-postgres psql -U postgres conecta_pro < backup.sql

# Limpar cache
redis-cli -h localhost FLUSHALL
```

---

## 🎯 Skills Disponíveis

Ver diretório: `/opt/conecta-pro/.agents/skills/`

| Skill | Descrição |
|-------|-----------|
| backend-dev | Desenvolvimento Python/FastAPI |
| frontend-dev | Next.js/React/TypeScript |
| orval-codegen | Geração de APIs |
| database | PostgreSQL/Redis/Migrations |
| docker-ops | Gerenciamento containers |
| deploy | Deploy e rollback |
| test-runner | Testes pytest/vitest |
| debug | Debugging sistemático |
| code-review | Review de código |
| financial | Módulo financeiro |
| operacional | Módulo operacional |
| government-integrations | Integrações governo |
| git-workflow | Git e commits |
| security-audit | Auditoria segurança |
| comms | Comunicação com Claude Opus 4.6 |

---

## 🔗 Comunicação com Claude Opus 4.6

Você trabalha em conjunto com **Claude Opus 4.6** no mesmo servidor.
Diretório de comunicação: `/opt/conecta-pro/.comms/`

### INÍCIO DE SESSÃO (OBRIGATÓRIO)
Ao iniciar qualquer sessão, SEMPRE:
1. Ler `/opt/conecta-pro/.comms/HANDOFF.md` → onde paramos
2. Ler `/opt/conecta-pro/.comms/BACKLOG.md` → tarefas pendentes
3. Ler últimas mensagens: `tail -10 /opt/conecta-pro/.comms/messages/claude-out.jsonl`

### Enviar Mensagem para Claude
```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","from":"kimi","to":"claude","type":"status","id":"kimi-'$(date +%s)'","reply_to":null,"priority":"normal","subject":"ASSUNTO","content":"CONTEÚDO"}' >> /opt/conecta-pro/.comms/messages/kimi-out.jsonl
```

### Ler Mensagens do Claude
```bash
tail -5 /opt/conecta-pro/.comms/messages/claude-out.jsonl
```

### Arquivos Compartilhados
| Arquivo | Propósito |
|---------|-----------|
| `.comms/HANDOFF.md` | Onde paramos (ler ao iniciar) |
| `.comms/BACKLOG.md` | Tarefas pendentes |
| `.comms/DECISIONS.md` | Decisões de arquitetura |
| `.comms/SESSION_LOG.md` | Log cronológico |
| `.comms/PROTOCOL.md` | Regras completas |

### Regras
- Ler mensagens antes de começar trabalho novo
- Responder mensagens pendentes do Claude
- Registrar ações no SESSION_LOG.md
- Ao encerrar: atualizar HANDOFF.md e BACKLOG.md

---

## REGRAS OPERACIONAIS OBRIGATÓRIAS (v3.0)

> **ATENÇÃO:** Esta seção foi adicionada pelo Claude Opus 4.6 após auditoria.
> Estas regras são NÃO NEGOCIÁVEIS. Descumprir qualquer uma invalida o trabalho.

### Início de Sessão OBRIGATÓRIO
**ANTES de fazer qualquer coisa**, ler nesta ordem:
1. `/opt/conecta-pro/.kimi/SESSION-START.md` — checklist de início
2. `/opt/conecta-pro/.kimi/ENVIRONMENT.md` — onde você está e comandos exatos
3. `/opt/conecta-pro/.kimi/REGRAS-OPERACIONAIS.md` — 13 regras obrigatórias
4. `/opt/conecta-pro/.kimi/ERROS-PASSADOS.md` — erros anteriores para NÃO repetir
5. `/opt/conecta-pro/.comms/BASELINE.json` — números reais do projeto

### Referência de Comandos
Arquivo: `/opt/conecta-pro/.kimi/commands-reference.json`
Contém TODOS os comandos corretos. **SEMPRE usar estes comandos, NUNCA improvisar.**

### Verificação Obrigatória
**ANTES e DEPOIS de cada tarefa:**
```bash
/opt/conecta-pro/scripts/verify-all.sh
```
Se exit code = 1 após seu trabalho → REGRESSÃO detectada → REVERTER e reportar.

### Regras Resumidas (detalhes em `.kimi/REGRAS-OPERACIONAIS.md`)
1. **NUNCA mentir sobre números** — incluir comando e output exato
2. **SEMPRE ativar venv** — `source venv/bin/activate` antes de Python
3. **NUNCA mover testes para _orphaned/** — usar `@pytest.mark.xfail` ou `skip`
4. **NUNCA deletar configs** — conftest.py, pytest.ini, etc. são intocáveis
5. **VERIFICAR antes e depois** — `verify-all.sh` é obrigatório
6. **ESLint = `npx eslint .`** — NUNCA usar `next lint`
7. **Reportar honestamente** — formato padronizado com ANTES/DEPOIS
8. **NUNCA editar gerados** — `src/api/generated/`, `src/types/generated/`
9. **Commits com escopo** — `tipo(escopo): descrição com métricas`
10. **Se piorou, reverte** — NUNCA continuar em cima de regressão
11. **Scope limitado** — só fazer o que foi pedido
12. **Comunicar cada commit** — reportar ao Claude via `.comms/messages/`
13. **Impacto cruzado** — grep antes de renomear, verificar collection após

### Qualificação de Números
**SEMPRE** qualificar scope nos reports:
- ERRADO: "376 testes estáveis"
- CERTO: "376 testes passam dos que eu modifiquei. Projeto total: 4689/6468 (72.5%)"

### Formato de Report Obrigatório
```
TASK: [nome]
MÉTRICAS ANTES: (output do verify-all.sh)
MÉTRICAS DEPOIS: (output do verify-all.sh)
DELTA: (o que melhorou/piorou)
ARQUIVOS MODIFICADOS: [lista]
ARQUIVOS DELETADOS/MOVIDOS: [lista ou "nenhum"]
```

---

*Última atualização: 2026-02-09*
*Versão: 3.0.0 — com regras operacionais obrigatórias e framework de verificação*
