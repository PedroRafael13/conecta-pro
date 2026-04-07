# CLAUDE.md — Conecta PRO ERP
**Última atualização:** 2026-04-01
**Branch ativa:** feature/people-management-reorganization
**Responsável:** Jordan Jesus (jjesus@conectamais.pro)

## Visão Geral
ERP proprietário para empresas de segurança e tecnologia.
Compete com SAP/NetSuite/Salesforce com compliance brasileiro nativo.

**Empresa:** Conecta Mais — Segurança e Tecnologia
**CNPJ:** 35.710.481/0001-03 | Lucro Real desde 01/2026
**MRR:** R$ 272.086,96 | 52 funcionários | 13 clientes ativos

## Infraestrutura
| Item | Valor |
|------|-------|
| VPS | srv1134814.hstgr.cloud (82.25.75.74) — Hostinger KV4 |
| Backend | FastAPI + PostgreSQL + Redis · porta 8080 |
| Frontend | Next.js 16 + React 19 + TypeScript + Tailwind · porta 3001 |
| Path | /opt/conecta-pro/ |
| SSH | tmux sessions t1–t5 |

## Arquitetura
```
/opt/conecta-pro/
├── backend/          # FastAPI + SQLAlchemy
├── frontend/         # Next.js 16
├── agents/           # Sistema de agentes 24h
│   ├── core/         # BaseAgent + BaseOrchestrator
│   ├── modules/      # 13 orquestradores + 80 agentes
│   └── orchestrator_geral.py
├── skills/           # 10 skills de auditoria
├── reports/          # Relatórios dos ciclos
└── logs/             # Logs do sistema
```

## Sistema de Agentes 24h
- **80 agentes** em **13 orquestradores**
- Ciclo: a cada 30min via cron
- Score atual: **10.0/10** (2026-04-01)
- Alertas via Telegram: @conecta_pro_monitor_bot

## Módulos do ERP
| Módulo | Score | Status |
|--------|-------|--------|
| Departamento Pessoal | 10/10 | ✅ |
| Recursos Humanos | 10/10 | ✅ |
| Ponto Eletrônico | 10/10 | ✅ |
| Financeiro | 10/10 | ✅ |
| Fiscal & Contábil | 10/10 | ✅ |
| Operacional | 10/10 | ✅ |
| GED — Kits Documentais | 10/10 | ✅ |
| Inteligência | 10/10 | ✅ |
| Negócios (CRM + Marketing + Licitações) | 10/10 | ✅ |
| Saúde Ocupacional | 10/10 | ✅ |
| Portais | 10/10 | ✅ |
| Equipamentos | 10/10 | ✅ |
| Administrativo | 10/10 | ✅ |

## Auditorias de Qualidade (Skills 01-10)
| Skill | Score | Status |
|-------|-------|--------|
| 01 Debugger | corrigido | ✅ |
| 02 Code Review | 9.3/10 | ✅ |
| 03 API RESTful | 6.2/10 | 🔄 em correção |
| 04 Testes | 4.1/10 | 🔄 pendente |
| 05 Banco | 6.4/10 | 🔄 em correção |
| 06 Auth | 5.7/10 | 🔄 em correção |
| 07 Docker | 5.8/10 | 🔄 pendente |
| 08 CI/CD | 9.5/10 | ✅ |
| 09 UX | 6.9/10 | 🔄 em correção |
| 10 Docs | 5.2/10 | 🔄 este fix |

## Comandos Essenciais
```bash
# Token de autenticação
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Container backend
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)

# Hot copy backend (não rebuild)
docker cp /opt/conecta-pro/backend/modules/ $CONTAINER:/app/modules/
docker exec $CONTAINER kill -HUP 1

# Build frontend (serializado — nunca simultâneo)
cd /opt/conecta-pro/frontend
NODE_OPTIONS=--max-old-space-size=4096 npm run build
pm2 restart all

# Rodar ciclo de agentes manualmente
cd /opt/conecta-pro
python3 agents/orchestrator_geral.py
```

## Zonas Proibidas
| Path | Motivo |
|------|--------|
| `alembic/versions/` | Migrations — nunca editar manualmente |
| `main_production.py` | Entry point produção — nunca modificar |
| `docker-compose*.yml` | Orquestração — nunca modificar |
| `.env*` | Variáveis de ambiente — nunca commitar |
| `credentials/` | Chaves e certificados — nunca tocar |

## Regras de Trabalho
- Sempre usar `127.0.0.1`, nunca `localhost`
- Terminais via `tmux attach -t tN` (t1–t5)
- Frontend builds: serializados, nunca simultâneos
- Backend changes: hot copy via `docker cp`, nunca rebuild completo
- Commit após cada correção com mensagem descritiva
- Rate limit de auth: 5 req/min — usar token compartilhado nos agentes
- Pré-commit hooks ativos: ruff, detect-secrets, bandit

---

## Regras de Governança para Sessões Autônomas

> **Contexto:** Em 2026-04-05 ocorreram 3 reverts automáticos (65c3ce14, f87e9c5b,
> f866cc6a) causados por sessões tmux paralelas revertendo commits de outros módulos.
> Estas regras são obrigatórias para todas as sessões Claude Code.

### Escopo de módulo obrigatório
Cada sessão Claude DEVE declarar no início qual módulo está editando.
Uma sessão que trabalha em `ged/` NÃO deve tocar em arquivos de `rh/`,
`operacional/`, `financeiro/` ou qualquer outro módulo não declarado.

### Proibição absoluta de git revert
Nenhuma sessão Claude pode executar `git revert` sem confirmação
explícita de Jordan Jesus no chat.
Antes de reverter qualquer coisa, a sessão DEVE escrever:
```
AGUARDANDO APROVAÇÃO: pretendo executar git revert <hash> porque <motivo>.
Confirma? (sim/não)
```
E aguardar resposta antes de prosseguir.

### Proibição de git push para main/develop
Sessões autônomas não podem fazer push direto para main ou develop.
Todo commit deve ficar na branch de trabalho declarada no início da sessão.

### Verificação de conflito antes de commit
Antes de qualquer `git commit`, executar:
```bash
git diff --name-only HEAD
```
e verificar se algum arquivo modificado pertence a módulo diferente do declarado.
Se sim, remover esse arquivo do stage e registrar no relatório final.

### Identificação da sessão
Todo commit de sessão autônoma DEVE incluir no final da mensagem:
```
[session: tmux-<id>] [module: <nome>]
```
Exemplo: `fix(ged): correção E2E [session: tmux-t1] [module: ged]`

### Como desfazer um commit com segurança (quando autorizado por Jordan)

**NUNCA usar:**
```bash
git revert <hash-de-outro-módulo>
git reset --hard
```

**Usar apenas (quando Jordan autorizar explicitamente):**
```bash
# Desfazer o último commit mantendo as mudanças em stage:
git reset --soft HEAD~1

# Ou, se Jordan autorizou reverter um commit específico:
git revert <hash> --no-edit
# Seguido de push para a branch de trabalho — NUNCA para main/develop
```

### Resolução de conflito entre sessões
Se uma sessão detectar que seu commit foi revertido por outra sessão:
1. **NÃO re-aplicar automaticamente**
2. Notificar Jordan com:
   ```
   ATENÇÃO: commit <hash> foi revertido por <hash-revert>.
   Aguardo sua instrução para re-aplicar ou descartar.
   ```
3. Aguardar confirmação antes de qualquer ação

## REGRAS DE GOVERNANÇA GIT — IMUTÁVEIS

### PROIBIDO ABSOLUTO (nenhuma sessão pode executar)
- git revert [qualquer commit]
- git reset --hard
- git reset --soft
- git push --force
- git push --force-with-lease

### QUANDO ENCONTRAR CONFLITO
1. PARAR imediatamente
2. Reportar ao Jordan Jesus no chat
3. Aguardar instrução explícita
4. NUNCA resolver conflito com revert automático

### BRANCHES PROTEGIDAS
- `main` — NUNCA commitar diretamente
- `develop` — NUNCA commitar diretamente
- `feature/*` — permitido commitar e push

### ZONAS PROIBIDAS
- alembic/versions/
- docker-compose*.yml
- .env*
- credentials/
- main_production.py (só com autorização explícita)

*Regras estabelecidas por Jordan Jesus em 2026-04-07.
Aplicam-se a TODAS as sessões Claude Code sem exceção.*
