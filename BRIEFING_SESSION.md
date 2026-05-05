# BRIEFING EXECUTIVO — Conecta PRO

> **Para:** Proxima sessao Claude Code
> **Gerado em:** 2026-03-22 03:30 UTC
> **Projeto:** /opt/conecta-pro/
> **Branch:** feature/people-management-reorganization
> **Tag:** post-cleanup-2026-03-19 (commit f60879b0)

---

## 1. CONTEXTO DO PROJETO

**Empresa:** CONECTAMAIS ELETRONICA LTDA (Conecta Mais)
- CNPJ: 35.710.481/0001-03
- Regime: Simples Nacional
- Setor: Vigilancia, seguranca patrimonial e tecnologia
- Sede: Manaus/AM
- CEO: Jordan Jesus (jjesus@conectamais.pro / Jordan0612)
- Contabilidade: Portte Contabil (usa Dominio Sistemas / TOTVS)

**Sistema:** Conecta PRO — ERP proprietario completo
- URL producao: https://erp.conectamais.pro
- VPS: srv1134814.hstgr.cloud (IP 82.25.75.74)
- Path: /opt/conecta-pro/
- OS: Ubuntu 24.04 LTS (kernel 6.8.0-94-generic)
- RAM: 31 GB | Disco: 387 GB (14% usado)

**Stack:**
- Backend: Python 3.12 + FastAPI 0.115.6 + SQLAlchemy 2.0.36 + Alembic
- Frontend: Next.js 16.1 + React 19 + TypeScript 5.9 + Tailwind + TanStack Query
- Database: PostgreSQL 16 (max_connections=150, pool_pre_ping, pool_recycle=1800)
- Cache: Redis 7 (socket_timeout=5s, retry_on_timeout, max_connections=50)
- Queue: Celery 5.4 (6 workers especializados + beat + flower)
- Monitoring: Prometheus + Grafana + Alertmanager + Loki + Telegram bot
- IA: Bartolo (GPT-4/Claude) + OpenClaw (agentes autonomos)
- Deploy: Docker Compose + PM2 (frontend) + nginx (reverse proxy + SSL)

**Numeros:**
- 46 modulos backend (37 ativos + 9 agregadores)
- 3.244 endpoints REST
- 495 modelos de banco
- 636.784 linhas de codigo backend
- 212 paginas frontend
- 22 containers Docker
- 20 integracoes externas
- 52 funcionarios ativos no banco
- 24 rubricas de folha cadastradas
- 156 beneficios ativos

---

## 2. ESTADO ATUAL DO SISTEMA

### Scores de Producao
```
Backend:        10/10 (seguranca, infra, codigo)
Frontend:        8.5/10 (funcional, CSP, HSTS)
Infra:           9.5/10 (pool, graceful, healthcheck)
Monitoring:     10/10 (Prometheus + Alertmanager + Telegram + OpenClaw)
Multi-Agent:    10/10 (3 agentes + memoria persistente)
Testes:          5.3/10 (53% coverage — meta 60%)
```

### Containers (21 rodando)
```
HEALTHY (20):
  conecta-pro-backend, conecta-pro-postgres, conecta-pro-redis
  conecta-pro-celery-priority, celery-sefaz, celery-nfse
  conecta-pro-celery-batch, celery-integrations, celery-operacional
  conecta-pro-flower
  conecta-pro-postgres-staging, redis-staging
  erp-alertmanager, erp-loki
  erp-prometheus, erp-node-exporter, erp-postgres-exporter
  erp-redis-exporter, erp-grafana, erp-promtail

UNHEALTHY (cosmetico, funcional):
  conecta-pro-celery-beat — healthcheck ps|grep falha, mas tasks sao enviadas normalmente

NAO RODANDO VIA DOCKER:
  Frontend via PM2 (porta 3001) — NAO usar docker para frontend
```

### PM2
```
conecta-pro-frontend   PID 57220   11h up   157 restarts   68.5 MB
telegram-assistant     PID 10730   33h up   0 restarts     67.8 MB
```

### URLs
```
Producao:    https://erp.conectamais.pro (HTTP/2, CSP, HSTS)
API:         https://erp.conectamais.pro/api/v1/
Health:      http://localhost:8080/health/detailed
Flower:      http://localhost:5555 (admin/admin123)
Grafana:     http://localhost:3000 (admin/senha no .env)
Prometheus:  http://localhost:9090
Alertmanager: http://localhost:9093
Dashboard:   https://erp.conectamais.pro/agents/dashboard
```

---

## 3. SCORES DOS 8 MODULOS DE GESTAO DE PESSOAS

| # | Modulo | Score | Status | Detalhe |
|---|--------|-------|--------|---------|
| 1 | Departamento Pessoal | 8/10 | ✅ | 49 endpoints, CLT calculator, folha com 12 rubricas |
| 2 | Recursos Humanos | 7.5/10 | ✅ | 49 endpoints, avaliacao 360, carreira, treinamentos |
| 3 | GED Kits Documentais | 9/10 | ✅ | 218 endpoints, geracao mensal automatica |
| 4 | Operacoes | 9/10 | ✅ | 245 endpoints, escalas, diaristas, IA operacional |
| 5 | Saude Ocupacional | 8.5/10 | ✅ | 92 endpoints, PCMSO/PPRA/EPIs/CAT, CCT 2026 |
| 6 | Ponto Eletronico | 2.5/10 | ❌ | PunchService in-memory, 7 paginas MOCK |
| 7 | Portal Funcionario | 8/10 | ✅ | 32 endpoints, auth propria CPF+JWT |
| 8 | Area do Cliente | 8/10 | ✅ | 12 endpoints, tickets, download kits |

**Media geral: 7.6/10 — Bloqueador: Ponto Eletronico**

---

## 4. COMPARATIVO DOMINIO vs CONECTA PRO

Validacao com PDFs reais do Dominio Sistemas (12/2025, 01/2026, 02/2026):

### Fevereiro 2026
| Item | Dominio | Conecta PRO | Diferenca |
|------|---------|-------------|-----------|
| Funcionarios | 47 | 52 | +5 (admitidos apos fechamento Dominio) |
| Bruto | R$ 98.640 | R$ 87.410 | -R$ 11.230 (faltam HE reais, adicionais) |
| INSS | R$ 6.485 | R$ 6.682 | +R$ 197 (5 func a mais) |
| VT | incluido | R$ 5.244 | ✅ Implementado |
| Beneficios | incluido | R$ 676 | ✅ Implementado |
| Total Descontos | R$ 35.863 | R$ 12.603 | -R$ 23.260 (faltam consignados, pensoes) |
| Liquido | R$ 62.776 | R$ 74.806 | +R$ 12.030 |

### INSS e IRRF
- Calculo INSS progressivo 2026: ✅ CORRETO (clt_calculator.py, Decimal precision)
- Calculo IRRF progressivo 2026: ✅ CORRETO (nenhum func atinge faixa atualmente)
- FGTS 8%: ✅ CORRETO (R$ 6.992,81 vs Dominio R$ 6.992,80 — diff R$ 0,01)

### Rubricas Implementadas (12)
| Tipo | Rubrica | Fonte | Status |
|------|---------|-------|--------|
| Provento | Salario Base | employees.salario_base | ✅ |
| Provento | Hora Extra 50% | overtime_records | ✅ |
| Provento | Hora Extra 100% | overtime_records | ✅ |
| Provento | Adicional Noturno 20% | overtime_records (night) | ✅ |
| Provento | DSR sobre Extras | Calculado | ✅ |
| Provento | Periculosidade 30% | employees flag | ✅ |
| Desconto | INSS Progressivo | Tabela 2026 | ✅ |
| Desconto | IRRF | Tabela 2026 | ✅ |
| Desconto | VT 4% | Todos funcionarios | ✅ |
| Desconto | Beneficios | employee_benefits | ✅ |
| Desconto | Faltas | solides_absences | ✅ |
| Desconto | Atrasos | solides_absences | ✅ |

### Gap: R$ 23K em descontos faltantes
Causa: HE reais nao lancadas em overtime_records + consignados + pensoes + outros descontos do Dominio.

---

## 5. PENDENCIAS PRIORITARIAS

| # | Modulo | Item | Prioridade | Impacto |
|---|--------|------|------------|---------|
| 1 | Ponto | PunchService in-memory → AsyncSession | Alta | Batidas nao persistem |
| 2 | Ponto | 7 paginas frontend MOCK → APIs reais | Alta | Modulo inacessivel |
| 3 | Folha | Importar HE reais do Dominio/ponto | Media | Gap R$ 11K no bruto |
| 4 | Folha | Consignados e pensoes alimenticias | Media | Gap R$ 23K nos descontos |
| 5 | Folha | Contracheque PDF | Media | Funcionarios precisam |
| 6 | Integracoes | Solides sync real | Media | Endpoint stub |
| 7 | Integracoes | eSocial producao (tpAmb=1) | Media | Ainda em homologacao |
| 8 | Integracoes | FGTS Digital transmissao | Media | Sem integracao real |
| 9 | Infra | SENTRY_DSN configurar | Media | Zero error monitoring |
| 10 | Infra | S3 backup offsite | Media | Backups so locais |
| 11 | Testes | Coverage 53% → 60% | Baixa | Faltam ~17K linhas |
| 12 | RH | Tabela surveys clima | Baixa | Endpoint retorna [] |
| 13 | SST | LTCAT e PPP | Baixa | Documentos faltantes |
| 14 | SST | health_occupational sync→async | Baixa | Inconsistencia |

---

## 6. MULTI-AGENT SYSTEMS

### Componentes Ativos
| Componente | Arquivo | Cron | Status |
|-----------|---------|------|--------|
| Knowledge Builder | agents/knowledge_builder.py | Manual | Mapeia 37 modulos |
| Pattern Learner | agents/pattern_learner.py | Diario 03:00 | Aprende padroes |
| Preventive Action | agents/preventive_action.py | Cada 15min | Acoes preventivas |
| Context Builder | agents/context_builder.py | Cada 2min | Contexto real-time |
| Dashboard API | agents/dashboard_api.py | Cada 2min | Dados para dashboard |
| Telegram Assistant | agents/telegram_assistant.py | PM2 24/7 | Bot conversacional |
| Action Executor | agents/action_executor.py | Sob demanda | Executa acoes |
| Conversation Memory | agents/conversation_memory.py | Em memoria | Historico conversas |

### OpenClaw (Backend)
- Webhook: /api/v1/ai/openclaw/alert-webhook
- Memoria: openclaw_interventions + openclaw_patterns + openclaw_knowledge_base
- Fluxo: Alerta → consulta padrao (>80% confianca?) → age ou diagnostica → aprende
- Telegram bot: conectapro_alertas_bot (ID 8343886201, chat 5536961034)

### Dashboard
- URL: https://erp.conectamais.pro/agents/dashboard
- Dados: agents/dashboard_data.json (atualizado a cada 2min)
- HTML: agents/dashboard.html (estatico servido por nginx)

---

## 7. INFRAESTRUTURA

### tmux
Nao ha sessoes tmux persistentes. Usar terminais diretos.

### PM2
```bash
pm2 list                           # Ver processos
PORT=3001 pm2 restart conecta-pro-frontend --update-env   # Restart frontend
pm2 save                           # Salvar para reboot
```

### Crons Ativos
```
0 3 * * *      backup_database.sh              # Backup PG diario
30 3 * * *     backup_retention.sh             # Limpeza > 30 dias
*/5 * * * *    metrics_collector.sh            # Metricas custom
0 3 * * *      run_pattern_learner.sh          # Aprendizado padroes
*/15 * * * *   run_preventive_action.sh        # Acoes preventivas
*/2 * * * *    dashboard_api.py                # Dashboard data
*/2 * * * *    context_builder.py              # Contexto real-time
*/15 * * * *   check-conectado-health.sh       # Health check externo
```

### Deploy Padrao
```bash
# Backend
cd /opt/conecta-pro && docker compose build backend --no-cache
chmod -R 777 /opt/conecta-pro/logs/
docker compose up -d backend
# Aguardar ~3min para startup

# Frontend
cd /opt/conecta-pro/frontend
NODE_OPTIONS=--max-old-space-size=8192 npx next build
PORT=3001 pm2 restart conecta-pro-frontend --update-env
pm2 save
```

### Backups
- Local: /opt/conecta-pro/backups/postgresql/ (diario 03:00, retencao 30d)
- Offsite S3: NAO CONFIGURADO (pendente)
- Backup mais recente: verificar com `ls -lt backups/postgresql/ | head -3`

---

## 8. CONTEXTO TECNICO IMPORTANTE

### Credenciais
```
Admin: jjesus@conectamais.pro / Jordan0612
Alt:   egonzaga@conectamais.pro / Admin@123
Rate limit auth: 5 req/min (Redis-backed)
JWT: HS256, 30min expiry, 7d refresh
```

### Bugs Conhecidos e Solucoes
| Bug | Causa | Solucao Aplicada |
|-----|-------|-----------------|
| /api/v1/clients 500 | Model `type` vs DB `client_type` | Raw SQL + sync session |
| Trailing slash → 403 | Redirect perde Authorization | Adicionado `/` em 20+ paginas |
| PPRA 500 | 11 colunas faltantes no banco | ALTER TABLE |
| celery-beat unhealthy | Healthcheck ps grep | Cosmetico, funcional |
| Startup 503 (3min) | VPS lenta | nginx retry 2x + pagina amigavel + axios retry |

### Dessincronizacao Model ↔ DB (CRITICO)
Varios modelos SQLAlchemy tem campos que NAO existem no banco real:
- `clients.type` → banco tem `client_type` (CORRIGIDO com raw SQL)
- `condominiums.phone`, `condominiums.is_active` vs banco `ativo`
- `document_kits.extra_metadata` nao existe no banco
- Solucao geral: usar raw SQL via `text()` para queries criticas

### Zonas Proibidas
| Zona | Motivo |
|------|--------|
| backend/modules/financial/* | 72K linhas, compliance fiscal |
| backend/modules/government_integrations/* | Regulatorio eSocial/SEFAZ |
| backend/alembic/versions/* | 90+ migrations, chain fragil |
| backend/main_production.py | Entry point, module loader |
| docker-compose*.yml | Infra producao |
| .env* | Segredos |
| backend/core/ | Auth, DB, config |
| credentials/ | Certificado A1 (valido ate jan/2027) |

### Integracoes
| Integracao | Status | Detalhe |
|-----------|--------|---------|
| eSocial | Homologacao (tpAmb=2) | Gera XML S-2200/S-2299, sem transmissao |
| SEFAZ | Config existe | NF-e/CT-e via SOAP/XML com cert A1 |
| NFS-e Manaus | Config existe | ABRASF 2.04, codigo 11.02 |
| Solides | Stub | Endpoint sync existe, nao implementado |
| Dominio Sistemas | Validacao | Comparamos folhas — export parcial |
| Cora Banking | Config existe | API REST |
| Inter Banking | Config existe | API REST |
| WhatsApp (Evolution) | Config existe | Notificacoes |
| OpenAI GPT-4 | Ativo | Bartolo assistente |
| Anthropic Claude | Fallback | LLM secundario |

### CCT 2026 SINDECOMPRESTS/SINDICOND-AM
- Registro MTE: AM000613/2025
- Vigencia: 01/01/2026 a 31/12/2026
- 50 cargos com pisos salariais implementados
- Reajuste: 7,1% (geral) e 4,5% (administrativo)
- Piso geral: R$ 1.670,00
- Implementado em: modules/cct/ (33 arquivos, 3.141 linhas)
- Usado por: folha, portal do funcionario, SST

---

## 9. HISTORICO DE DECISOES IMPORTANTES

### Decisoes Arquiteturais
1. **Orval para tipos** — tipos TypeScript gerados automaticamente do OpenAPI (35 modulos)
2. **Estrategia hibrida** — Orval gera tipos, services/hooks manuais
3. **CondominioContext** — provider global com persistencia localStorage
4. **Raw SQL para clients** — contorna dessincronizacao model/DB
5. **PM2 para frontend** — Docker frontend desabilitado (conflito porta 3001)
6. **sync Session para clients** — modulo usa ORM sync, nao async
7. **clt_calculator.py** — Decimal precision para calculos trabalhistas
8. **OpenClaw memoria PostgreSQL** — 3 tabelas para aprendizado continuo

### O que foi rejeitado
1. **Migrar clients para async** — muito risco de regressao, raw SQL e mais seguro
2. **Remover output:standalone** — necessario para Docker build
3. **Aumentar pool_size do backend** — reduzimos Celery workers em vez disso
4. **Remover modulos agregadores** — sao necessarios para organizar 46 modulos

### Padroes de Qualidade Exigidos
- Pre-commit: ruff + ruff-format + bandit + detect-secrets + gitleaks
- Build frontend: 0 erros TypeScript, 212 paginas
- Commits: mensagens em portugues, tipo convencional (feat/fix/refactor/docs)
- Seguranca: CSP, HSTS, CORS restrito, proxy trust 127.0.0.1, /docs desabilitado
- Testes: 9.173 passando, coverage 53%
- Deploy: backup antes, backend antes de frontend, sem deploy em horario de pico

---

## 10. COMANDOS ESSENCIAIS

```bash
# Login e teste
TOKEN=$(curl -sf -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Testar endpoints
curl -sf "http://localhost:8080/api/v1/clients/?skip=0&limit=3" -H "Authorization: Bearer $TOKEN"
curl -sf "http://localhost:8080/health/detailed" | python3 -m json.tool

# Build + Deploy
cd /opt/conecta-pro/frontend && NODE_OPTIONS=--max-old-space-size=8192 npx next build
PORT=3001 pm2 restart conecta-pro-frontend --update-env && pm2 save

cd /opt/conecta-pro && docker compose build backend --no-cache
chmod -R 777 logs/ && docker compose up -d backend

# Git
git add -A && git commit -m "feat: descricao" && git push origin feature/people-management-reorganization
git tag -f post-cleanup-2026-03-19 HEAD && git push origin --tags --force

# Monitoring
docker logs conecta-pro-backend --tail 50
docker exec conecta-pro-postgres psql -U postgres -d conecta_pro
```

---

**IMPORTANTE:** O backend leva ~3 minutos para subir nesta VPS. Sempre aguardar `curl -sf http://localhost:8080/health` retornar antes de testar endpoints. O nginx tem retry 2x + pagina 503 amigavel com auto-reload.
