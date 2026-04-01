# CONTEXTO — Conecta PRO
## Gerado automaticamente em 01/04/2026 01:50
## VPS: srv1134814.hstgr.cloud (82.25.75.74)

## INFRAESTRUTURA
- Backend: FastAPI · Docker · porta 8080
- Frontend: Next.js 16 · PM2 · porta 3001
- ERP: https://erp.conectamais.pro
- GitHub: https://github.com/jjesus1982/conecta-pro
- Branch: feature/people-management-reorganization
- Container: conecta-pro-backend

## TOKEN
```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)
```

## DADOS REAIS
- Funcionários ativos: OCI runtime exec failed: exec failed: unable to start container process: exec: "psql": executable file not found in $PATH
- Kits documentais: OCI runtime exec failed: exec failed: unable to start container process: exec: "psql": executable file not found in $PATH
- Clientes GED ativos: OCI runtime exec failed: exec failed: unable to start container process: exec: "psql": executable file not found in $PATH
- MRR: R$ 272.086,96
- Regime: LUCRO REAL (CNPJ 1) | SIMPLES NACIONAL em abertura (CNPJ 2)

## STATUS DOS MÓDULOS
- GED: 4/4
- Financeiro: 0/1
- DP/RH: 1/1
- Operacional: 1/1

## ÚLTIMOS COMMITS
```
23910a0d feat(agents): ciclo completo 13 orquestradores — score 9.7/10
d3ad0508 fix(dp+ged): is_active no schema HR, trailing slash GED e UUID validation kits/send
84a5f77d fix(agents/fin): corrige endpoints financeiros — score 0.0→10.0/10
b6578010 fix(auth): HTTPBearer auto_error=False → retorna 401 em vez de 403 sem credenciais
cf016974 fix(agents/bugs): corrige executive_dashboard auth + clients vazio + comunicados 500
266d075b Revert "fix(security): ruff format — controllers LGPD e config"
f66cfb8a fix(security): ruff format — controllers LGPD e config
35e7134e fix(bugs): corrige executive_dashboard auth + crm/clients 404 + comunicados/nao-lidos 500
```

## BUGS CORRIGIDOS (sessão 2026-04-01)
- T1: Auth token compartilhado → isolado por usuário
- T2: Agentes financeiro · orquestradores criados
- T3: executive_dashboard sem auth → 401 correto
- T4: crm/clients trailing slash · comunicados nao-lidos 500→200
- T5: is_active no schema HR · GED trailing slash · kits UUID→422

## AGENTES (47 total, 8 orquestradores)
- /opt/conecta-pro/agents/core/base_agent.py
- /opt/conecta-pro/agents/core/base_orchestrator.py
- /opt/conecta-pro/agents/modules/ (dp_agentes, op_ged_agentes, fin_fiscal_agentes, extra_agentes)
- /opt/conecta-pro/agents/orchestrator_geral.py (auto-descobre orquestradores)

## ZONAS PROIBIDAS
alembic/versions/ · main_production.py · docker-compose*.yml · .env* · credentials/

## HOT COPY (padrão)
```bash
docker cp /opt/conecta-pro/backend/modules/[mod]/[file].py \
  $CONTAINER:/app/modules/[mod]/[file].py
docker restart $CONTAINER && sleep 25
```

## BUILD FRONTEND (padrão — serializado)
```bash
cd /opt/conecta-pro/frontend
NODE_OPTIONS=--max-old-space-size=8192 npx next build 2>&1 | tail -15
pm2 restart conecta-pro-frontend --update-env && pm2 save && sleep 8
```
