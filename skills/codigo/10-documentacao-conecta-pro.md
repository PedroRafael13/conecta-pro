---
name: documentacao-conecta-pro
description: Gerar documentação técnica completa do Conecta PRO — README do módulo, documentação de endpoints, changelog de sessão e relatório de status para novos chats. Usar ao final de cada sessão para garantir continuidade e contexto para próximos trabalhos.
---

# Documentação — Conecta PRO

## Quando usar
- Final de sessão — gerar relatório de contexto para novo chat
- Ao criar novo módulo — documentar endpoints e estrutura
- Antes de abrir novo chat — exportar estado atual do sistema
- Ao fechar módulo como 10/10 — registrar o que foi feito

## Gerar relatório de sessão completo (para novo chat)

```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)

python3 << 'PYEOF'
import subprocess, json, datetime

def run(cmd):
    r = subprocess.run(cmd, shell=True,
        capture_output=True, text=True, timeout=30)
    return r.stdout.strip()

TOKEN = run("""curl -sf -X POST \
  http://127.0.0.1:8080/api/v1/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=jjesus@conectamais.pro&password=Jordan0612' \
  | python3 -c "import sys,json; \
    print(json.load(sys.stdin)['access_token'])" """)

CONTAINER = run("docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1")

def db(sql):
    return run(f'docker exec {CONTAINER} psql -U postgres \
      -d conectapro -t -c "{sql}"')

def ep(path):
    return run(f'curl -sf -o /dev/null -w "%{{http_code}}" '
               f'"http://127.0.0.1:8080{path}" '
               f'-H "Authorization: Bearer {TOKEN}"')

# Últimos commits
commits = run("git -C /opt/conecta-pro log --oneline -10")

# Status dos módulos principais
modulos = {
    "GED": ["/api/v1/ged/kits", "/api/v1/ged/clients",
            "/api/v1/ged/reports/monthly"],
    "Financeiro": ["/api/v1/financial/receivables"],
    "CCT": ["/api/v1/hr/cct/resumo"],
    "Auth": ["/api/v1/auth/login"],
}

scores = {}
for mod, endpoints in modulos.items():
    passing = sum(1 for e in endpoints if ep(e) == "200")
    scores[mod] = f"{passing}/{len(endpoints)}"

# Dados reais do banco
total_func = db("SELECT COUNT(*) FROM employees WHERE status='ativo'")
total_clientes = db("SELECT COUNT(*) FROM clients WHERE status='ativo' 2>/dev/null")
total_kits = db("SELECT COUNT(*) FROM ged_document_kits")

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

relatorio = f"""# CONTEXTO — Conecta PRO
## Gerado automaticamente em {now}
## VPS: srv1134814.hstgr.cloud (82.25.75.74)

## INFRAESTRUTURA
- Backend: FastAPI · Docker · porta 8080
- Frontend: Next.js 16 · PM2 · porta 3001
- ERP: https://erp.conectamais.pro
- GitHub: https://github.com/jjesus1982/conecta-pro
- Branch: feature/people-management-reorganization
- Container: {CONTAINER}

## TOKEN
```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \\
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \\
  --format '{{{{.Names}}}}' | head -1)
```

## DADOS REAIS
- Funcionários ativos: {total_func.strip()}
- Kits documentais: {total_kits.strip()}
- MRR: R$ 272.086,96
- Clientes: 11 ativos

## STATUS DOS MÓDULOS
{chr(10).join(f"- {mod}: {score}" for mod, score in scores.items())}

## ÚLTIMOS COMMITS
```
{commits}
```

## ZONAS PROIBIDAS
alembic/versions/ · main_production.py · docker-compose*.yml · .env* · credentials/

## HOT COPY (padrão)
```bash
docker cp /opt/conecta-pro/backend/modules/[mod]/[file].py \\
  $CONTAINER:/app/modules/[mod]/[file].py
docker restart $CONTAINER && sleep 8
```

## BUILD FRONTEND (padrão — serializado)
```bash
cd /opt/conecta-pro/frontend
NODE_OPTIONS=--max-old-space-size=4096 npm run build 2>&1 | tail -15
pm2 restart conecta-pro-frontend --update-env && pm2 save && sleep 8
```
"""

with open("/opt/conecta-pro/CONTEXTO_SESSAO.md", "w") as f:
    f.write(relatorio)

print("✅ Relatório gerado: /opt/conecta-pro/CONTEXTO_SESSAO.md")
print(f"   Container: {CONTAINER}")
print(f"   Módulos: {scores}")
PYEOF

# Exibir e disponibilizar para download
cat /opt/conecta-pro/CONTEXTO_SESSAO.md
echo ""
echo "Para baixar no Mac:"
echo "scp root@82.25.75.74:/opt/conecta-pro/CONTEXTO_SESSAO.md ~/Desktop/"
```

## Documentar novo módulo

```bash
# Gerar documentação de endpoints de um módulo
TOKEN=$(...)
MODULO="[nome]"  # ex: ged, financeiro, operacional

curl -sf "http://127.0.0.1:8080/openapi.json" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
modulo = '$MODULO'
paths = {k: v for k, v in d['paths'].items()
         if modulo in k.lower()}
print(f'## Endpoints do módulo {modulo.upper()}')
print(f'Total: {len(paths)} endpoints\n')
for path, methods in sorted(paths.items()):
    for method, info in methods.items():
        if method in ['get','post','put','delete','patch']:
            desc = info.get('summary','Sem descrição')
            print(f'{method.upper()} {path}')
            print(f'  → {desc}')
" 2>/dev/null
```

## Scorecard final de módulo

```
╔══════════════════════════════════════════════╗
║   [NOME DO MÓDULO] — RELATÓRIO FINAL        ║
╠══════════════════════════════════════════════╣
║ Endpoints: [X]/[Y] passando (HTTP 200)      ║
║ Auth: [✅/❌] todos protegidos               ║
║ Dados reais: [✅/❌] sem mocks               ║
║ Error handling: [✅/❌] 404/422 corretos     ║
║ Frontend: [✅/❌] zero erros no console      ║
╠══════════════════════════════════════════════╣
║ Bugs corrigidos esta sessão:                ║
║   - [bug 1]                                 ║
║   - [bug 2]                                 ║
╠══════════════════════════════════════════════╣
║ Score: [X]/10  [✅ FECHADO / 🔄 PENDENTE]  ║
╚══════════════════════════════════════════════╝
```
