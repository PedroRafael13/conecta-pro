# 🔧 BACKLOG DE CORREÇÕES - CONECTA PRO

**Data:** 2026-02-11
**Prioridade:** P0 (Crítico) > P1 (Alto) > P2 (Médio)

---

## 🚨 P0 - CRÍTICO (Resolver antes do Deploy)

### P0.1: Remover Senha Default do Docker Compose
**Arquivo:** `docker-compose.yml`, `docker-compose.celery.yml`
**Problema:** Senha Redis exposta `conecta_redis_2024`

```yaml
# ANTES (Inseguro)
REDIS_PASSWORD: ${REDIS_PASSWORD:-conecta_redis_2024}

# DEPOIS (Seguro)
REDIS_PASSWORD: ${REDIS_PASSWORD}
```

**Solução:**
1. Remover defaults de senhas
2. Criar `.env.production` seguro
3. Usar Docker Secrets se possível

**Esforço:** 30 minutos
**Impacto:** 🔴 Crítico (Segurança)

---

### P0.2: Limpar Arquivos .env.backup do Git
**Arquivos:**
- `backend/.env.backup.20260206-051657`
- `backend/.env.backup-20260206-042337`
- `frontend/.env.local.backup.*`

**Comandos:**
```bash
# Remover do git (manter no .gitignore)
git rm --cached backend/.env.backup*
git rm --cached frontend/.env.local.backup*
echo "*.backup*" >> .gitignore
git commit -m "security: remove backup env files"
```

**Esforço:** 15 minutos
**Impacto:** 🔴 Crítico (Segurança)

---

### P0.3: Criar .env.example para Backend
**Arquivo:** `backend/.env.example` (não existe)

**Conteúdo sugerido:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/conecta_pro

# Redis
REDIS_PASSWORD=change_me_in_production
REDIS_URL=redis://:change_me@localhost:6379/0

# JWT
SECRET_KEY=generate_strong_secret_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS (se aplicável)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET=

# Email
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=

# Outros
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Esforço:** 20 minutos
**Impacto:** 🟡 Médio (DX)

---

### P0.4: Corrigir Erros TypeScript em Testes
**Arquivos afetados:**
- `frontend/src/hooks/__tests__/useNotifications.test.ts` (15 erros)
- `frontend/src/hooks/__tests__/useReimbursement.test.ts` (3 erros)
- `frontend/src/lib/__tests__/api-interceptors.test.ts` (7 erros)

**Erros comuns:**
```typescript
// Problema: Property 'wrapper' does not exist
// Solução: Tipar corretamente ou usar renderHook direto

// Problema: Type 'string' is not assignable to type 'Error'
// Solução: Usar new Error('mensagem')
```

**Esforço:** 2 horas
**Impacto:** 🟡 Médio (Qualidade)

---

### P0.5: Fix Ruff Error A003
**Arquivo:** `modules/ai/report_generator/models/report_section.py:203`

**Problema:** `id` shadowing builtin Python

**Solução:**
```python
# Já tem noqa, mas melhor renomear
remote_side=[id],  # noqa: A003  # <- Atual
remote_side=[section_id],  # <- Sugerido
```

**Esforço:** 5 minutos
**Impacto:** 🟢 Baixo (Lint)

---

## ⚠️ P1 - ALTO (Resolver na primeira semana)

### P1.1: Criar Testes E2E Críticos
**Framework:** Playwright

**Prioridade:**
1. Fluxo de Login/Auth
2. Criar Reembolso → Aprovar
3. Registrar Ocorrência

**Esforço:** 8 horas
**Impacto:** 🟡 Alto (Confiabilidade)

---

### P1.2: Implementar Tracing Distribuído
**Ferramenta:** Jaeger ou Zipkin

**Onde adicionar:**
- Middleware FastAPI
- Chamadas externas
- Tarefas Celery

**Esforço:** 4 horas
**Impacto:** 🟡 Alto (Observabilidade)

---

### P1.3: Configurar CDN para Assets
**Opções:**
- CloudFront (AWS)
- Cloudflare
- Vercel Edge

**O que colocar no CDN:**
- Imagens
- CSS/JS estáticos
- Fontes
- Documentos GED

**Esforço:** 3 horas
**Impacto:** 🟡 Alto (Performance)

---

### P1.4: Revisar N+1 Queries
**Ferramenta:** `pytest-django` ou logs SQLAlchemy

**Onde verificar:**
- Listagens com relacionamentos
- Relatórios
- Dashboards

**Esforço:** 4 horas
**Impacto:** 🟡 Alto (Performance)

---

### P1.5: Adicionar Rate Limiting Específico
**Arquivo:** `backend/RATE_LIMITING.md` existe, verificar implementação

**Endpoints críticos:**
- /api/v1/auth/* (strict)
- /api/v1/upload/* (moderate)
- /api/v1/reports/* (relaxed)

**Esforço:** 3 horas
**Impacto:** 🟡 Alto (Segurança)

---

## 📋 P2 - MÉDIO (Resolver no primeiro mês)

### P2.1: Documentação de Arquitetura (ADRs)
**Criar:** `docs/architecture/`

**ADRs necessários:**
1. Escolha de FastAPI vs Django
2. Estrutura modular (Clean Architecture)
3. Decisão de PostgreSQL + Redis
4. Estratégia de filas (Celery)

**Esforço:** 6 horas
**Impacto:** 🟢 Médio (Manutenibilidade)

---

### P2.2: Runbooks de Operações
**Criar:** `docs/runbooks/`

**Runbooks:**
1. Deploy em produção
2. Rollback de emergência
3. Escalar serviços
4. Limpar cache Redis
5. Debugar filas Celery

**Esforço:** 4 horas
**Impacto:** 🟢 Médio (Operação)

---

### P2.3: Melhorar Logs Estruturados
**Atual:** Logs textuais (`erp.log`)

**Objetivo:** JSON structured logging
```json
{
  "timestamp": "2026-02-11T23:00:00Z",
  "level": "INFO",
  "service": "conecta-pro",
  "trace_id": "abc-123",
  "user_id": "user-456",
  "message": "Reembolso criado",
  "context": {"request_id": "req-789"}
}
```

**Esforço:** 3 horas
**Impacto:** 🟢 Médio (Observabilidade)

---

### P2.4: Chaos Engineering
**Ferramenta:** Chaos Monkey ou Gremlin

**Cenários:**
1. Matar container PostgreSQL
2. Simular latência Redis
3. Corromper mensagens Celery

**Esforço:** 8 horas
**Impacto:** 🟢 Médio (Resiliência)

---

### P2.5: Clean Code - Reduzir Complexidade
**Ferramenta:** `radon` ou `xenon`

**Arquivos com complexidade alta:**
- Verificar com: `radon cc backend/ -a -nc`
- Target: Nenhum arquivo com rank F

**Esforço:** 8 horas
**Impacto:** 🟢 Médio (Manutenibilidade)

---

## 📊 RESUMO DE ESFORÇO

| Prioridade | Quantidade | Esforço Total | Prazo |
|------------|------------|---------------|-------|
| P0 | 5 itens | ~5 horas | Antes do deploy |
| P1 | 5 itens | ~22 horas | 1ª semana |
| P2 | 5 itens | ~29 horas | 1º mês |
| **Total** | **15 itens** | **~56 horas** | **~6 semanas** |

---

## 🎯 SPRINT RECOMENDADA (Próximos 5 dias)

### Dia 1: Segurança P0
- [ ] P0.1: Remover senhas defaults
- [ ] P0.2: Limpar .env.backup

### Dia 2: Qualidade P0
- [ ] P0.3: Criar .env.example
- [ ] P0.4: Fix TypeScript (parte 1)

### Dia 3: Qualidade P0
- [ ] P0.4: Fix TypeScript (parte 2)
- [ ] P0.5: Fix Ruff A003

### Dia 4: E2E P1
- [ ] P1.1: Setup Playwright
- [ ] P1.1: Teste E2E Login

### Dia 5: E2E P1
- [ ] P1.1: Teste E2E Reembolso
- [ ] Revisão final

---

## ✅ DEFINIÇÃO DE PRONTO (Definition of Done)

Para cada item:
- [ ] Código implementado
- [ ] Testes passando
- [ ] Revisado por peer
- [ ] Documentado (se necessário)
- [ ] Deploy em staging validado

---

*Última atualização: 2026-02-11*
