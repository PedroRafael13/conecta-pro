---
name: debugger-ged-causa-raiz
description: Framework sistemático de debugging para o módulo GED do Conecta PRO — isolar causa raiz de bugs em kits documentais, assinaturas, certidões, uploads e envios. Evita tentativas ad-hoc e previne recorrência.
---

# Debugger Sistemático — Módulo GED

## Quando usar
- Bug em kits documentais persiste após tentativas ad-hoc
- Endpoint GED retorna 500, 404 ou dados errados de forma intermitente
- Upload ou download de documento falha silenciosamente
- Assinatura eletrônica retorna 401 inesperado
- Dropdown de clientes vazio no modal

## Setup rápido

```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)
KIT_ID="2826deb4-722a-4d77-bc87-8af375240eef"      # Ideal Flores
CLIENT_ID="4db583b6-815a-494f-a1e3-0c62fa81eca9"   # Ideal Flores
```

## Prompt de debugging (preencher e usar)

```
Você é engenheiro sênior especialista em debugging sistemático — FastAPI + PostgreSQL + Next.js.

Stack GED: FastAPI · PostgreSQL · tabelas ged_document_kits / ged_clients / ged_documents / ged_certidoes
Módulo: GED — Gestão Eletrônica de Documentos
URL base: http://127.0.0.1:8080/api/v1/ged/

**Descrição do bug:** [o que está acontecendo]
**Endpoint afetado:** [GET/POST /api/v1/ged/...]
**Comportamento esperado:** [o que deveria retornar]
**Comportamento real:** [o que está retornando — status HTTP + body]
**Frequência:** [sempre / intermitente / só após deploy]
**Quando começou:** [sempre existiu / após fix X / após migração Y]
**O que já tentou:** [hot copy, restart, rollback...]
**Logs relevantes:** [docker logs $CONTAINER --tail 30]
**Última mudança antes do bug:** [arquivo editado, commit]

Entregue:

**1. Reprodução**
- Comando curl mínimo que reproduz o bug
- Condições necessárias (token, UUID válido, dados no banco)

**2. Isolamento por camada GED**
- Frontend (Next.js /ged/*) → erro no console?
- Backend (FastAPI /api/v1/ged/*) → erro nos logs do container?
- Banco (PostgreSQL tabelas ged_*) → query retorna dado correto direto no psql?
- Infra (Docker/PM2) → container respondendo?

**3. Top 5 hipóteses — ordenadas por probabilidade GED**
Para cada:
- Hipótese
- Teste em ≤5 min
- O que confirma / descarta

**4. Plano passo a passo**
1. [Verificar X — se true: causa Y. Se false: ir para 2]
2. ...

**5. Ferramentas específicas GED**
- Logs: docker logs $CONTAINER --tail 50 | grep -i "ged\|kit\|document"
- Banco: docker exec $CONTAINER psql -U postgres -d conectapro -c "SELECT..."
- Curl: curl com token e UUID real do Ideal Flores

**6. Correção + hot copy**
Fix + comando docker cp + restart

**7. Prevenção**
Teste curl de regressão para esse bug específico
```

## Bugs históricos do GED — checar primeiro

```bash
# BUG RECORRENTE 1: rota /{id} capturando /search como UUID
curl -sf "http://127.0.0.1:8080/api/v1/ged/documents/search" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
# Esperado: 200. Se 422/500 → rota /search está DEPOIS de /{id}

# BUG RECORRENTE 2: trailing slash causando 404
curl -sf -o /dev/null -w "%{http_code}" \
  "http://127.0.0.1:8080/api/v1/ged/clients"
# Esperado: 200. Se 404 → testar sem barra final

# BUG RECORRENTE 3: client_name NULL nos kits
curl -sf "http://127.0.0.1:8080/api/v1/ged/kits" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys,json
kits = json.load(sys.stdin)
lista = kits if isinstance(kits, list) else kits.get('data', kits.get('kits', []))
nulos = [k for k in lista if not k.get('client_name')]
print(f'Kits sem client_name: {len(nulos)}/{len(lista)}')
"
# Esperado: 0. Se > 0 → JOIN ged_clients ausente no controller

# BUG RECORRENTE 4: dropdown vazio (useEffect sem isOpen)
# Verificar no frontend: /ged/kits/page.tsx
grep -n "useEffect" /opt/conecta-pro/frontend/src/app/modulos/gestao-pessoas/ged/kits/page.tsx \
  2>/dev/null | head -10

# BUG RECORRENTE 5: namespace antigo /people-management/ged
grep -rn "people-management/ged" \
  /opt/conecta-pro/frontend/src/ 2>/dev/null | head -5
# Esperado: nenhum resultado

# BUG RECORRENTE 6: assinatura 401 com token válido
curl -sf -o /dev/null -w "%{http_code}" \
  "http://127.0.0.1:8080/api/v1/ged/document-signatures/stats/summary" \
  -H "Authorization: Bearer $TOKEN"
# Esperado: 200
```

## Diagnóstico rápido completo GED

```bash
echo "=== DIAGNÓSTICO GED $(date '+%H:%M:%S') ==="

ENDPOINTS=(
  "GET /api/v1/ged/kits"
  "GET /api/v1/ged/clients"
  "GET /api/v1/ged/documents/search"
  "GET /api/v1/ged/config/drive"
  "GET /api/v1/ged/config/schedule"
  "GET /api/v1/ged/config/email-templates"
  "GET /api/v1/ged/config/document-types"
  "GET /api/v1/ged/reports/monthly"
  "GET /api/v1/ged/document-signatures/stats/summary"
  "GET /api/v1/ged/montar/condominios"
  "GET /api/v1/ged/kit-real/$KIT_ID/checklist"
)

PASS=0; FAIL=0
for EP in "${ENDPOINTS[@]}"; do
  METHOD=$(echo $EP | cut -d' ' -f1)
  PATH=$(echo $EP | cut -d' ' -f2)
  STATUS=$(curl -sf -o /dev/null -w "%{http_code}" \
    -X $METHOD "http://127.0.0.1:8080$PATH" \
    -H "Authorization: Bearer $TOKEN")
  if [ "$STATUS" = "200" ]; then
    echo "  ✅ $METHOD $PATH → $STATUS"
    ((PASS++))
  else
    echo "  ❌ $METHOD $PATH → $STATUS"
    ((FAIL++))
  fi
done

echo ""
echo "Resultado: $PASS OK · $FAIL FALHA"

echo ""
echo "=== LOGS RECENTES GED ==="
docker logs $CONTAINER --tail 20 2>&1 \
  | grep -i "ged\|kit\|document\|error\|exception" | head -15
```
---
name: code-review-ged
description: Checklist estruturado de code review para o módulo GED do Conecta PRO. Usar antes de declarar qualquer submódulo GED como 10/10. Cobre controllers, services, modelos, frontend e banco.
---

# Code Review — Módulo GED

## Setup

```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)
KIT_ID="2826deb4-722a-4d77-bc87-8af375240eef"
```

## Checklist completo GED (15 pontos)

### 1. FUNCIONALIDADE — 11 endpoints obrigatórios (5 pontos)

```bash
python3 << 'PYEOF'
import subprocess, json

TOKEN = subprocess.run(
  "curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login "
  "-H 'Content-Type: application/x-www-form-urlencoded' "
  "-d 'username=jjesus@conectamais.pro&password=Jordan0612' "
  "| python3 -c \"import sys,json; print(json.load(sys.stdin)['access_token'])\"",
  shell=True, capture_output=True, text=True
).stdout.strip()

KIT_ID = "2826deb4-722a-4d77-bc87-8af375240eef"

ENDPOINTS = [
  ("GET", f"/api/v1/ged/kits",                              200, "Listar kits"),
  ("GET", f"/api/v1/ged/clients",                           200, "Listar clientes"),
  ("GET", f"/api/v1/ged/documents/search",                  200, "Busca documentos"),
  ("GET", f"/api/v1/ged/config/drive",                      200, "Config Drive"),
  ("GET", f"/api/v1/ged/config/schedule",                   200, "Config Agendamento"),
  ("GET", f"/api/v1/ged/config/email-templates",            200, "Templates e-mail"),
  ("GET", f"/api/v1/ged/config/document-types",             200, "Tipos de documento"),
  ("GET", f"/api/v1/ged/reports/monthly",                   200, "Relatório mensal"),
  ("GET", f"/api/v1/ged/document-signatures/stats/summary", 200, "Stats assinaturas"),
  ("GET", f"/api/v1/ged/kit-real/{KIT_ID}/checklist",       200, "Checklist kit"),
  ("GET", f"/api/v1/ged/montar/condominios",                200, "Montar condomínios"),
]

passou = 0
for method, path, esperado, desc in ENDPOINTS:
  status = subprocess.run(
    f'curl -sf -o /dev/null -w "%{{http_code}}" '
    f'-X {method} "http://127.0.0.1:8080{path}" '
    f'-H "Authorization: Bearer {TOKEN}"',
    shell=True, capture_output=True, text=True
  ).stdout.strip()
  ok = status == str(esperado)
  icon = "✅" if ok else "❌"
  print(f"  {icon} {method} {path} → {status} ({desc})")
  if ok: passou += 1

print(f"\nFuncionalidade: {passou}/{len(ENDPOINTS)}")
PYEOF
```

```bash
# [ ] Dados reais: kits com client_name (não null)
curl -sf "http://127.0.0.1:8080/api/v1/ged/kits" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys,json
d=json.load(sys.stdin)
kits=d if isinstance(d,list) else d.get('data',d.get('kits',[]))
nulos=[k for k in kits if not k.get('client_name')]
total=len(kits)
print(f'Kits totais: {total} | Sem client_name: {len(nulos)}')
[print(f'  ⚠️  kit {k[\"id\"][:8]}... sem cliente') for k in nulos]
"

# [ ] Checklist Ideal Flores: esperado 19+ tipos de documento
curl -sf "http://127.0.0.1:8080/api/v1/ged/kit-real/$KIT_ID/checklist" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys,json
d=json.load(sys.stdin)
total=d.get('total_tipos',d.get('total',0))
print(f'Tipos de documento no kit: {total} (esperado ≥19)')
"

# [ ] UUID inválido retorna 404, não 500
STATUS=$(curl -sf -o /dev/null -w "%{http_code}" \
  "http://127.0.0.1:8080/api/v1/ged/kits/00000000-0000-0000-0000-000000000000" \
  -H "Authorization: Bearer $TOKEN")
echo "UUID inválido retorna: $STATUS (esperado 404)"

# [ ] Lista vazia retorna [] não null
curl -sf "http://127.0.0.1:8080/api/v1/ged/documents/search?q=xyzxyz999" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys,json
d=json.load(sys.stdin)
docs=d if isinstance(d,list) else d.get('data',d.get('documents',[]))
print(f'Busca inexistente retorna: {type(docs).__name__} com {len(docs)} itens (esperado lista vazia)')
"
```

### 2. SEGURANÇA (3 pontos)

```bash
echo "=== SEGURANÇA GED ==="
for EP in \
  "/api/v1/ged/kits" \
  "/api/v1/ged/clients" \
  "/api/v1/ged/documents/search" \
  "/api/v1/ged/reports/monthly"; do

  # Sem token
  S1=$(curl -sf -o /dev/null -w "%{http_code}" \
    "http://127.0.0.1:8080$EP")
  # Token inválido
  S2=$(curl -sf -o /dev/null -w "%{http_code}" \
    "http://127.0.0.1:8080$EP" \
    -H "Authorization: Bearer token_invalido_123")

  if [ "$S1" = "401" ] && [ "$S2" = "401" ]; then
    echo "  ✅ $EP → sem token: $S1 | token inválido: $S2"
  else
    echo "  ❌ $EP → sem token: $S1 | token inválido: $S2 (esperado 401)"
  fi
done
```

### 3. PERFORMANCE (3 pontos)

```bash
echo "=== PERFORMANCE GED ==="
# Medir tempo de resposta dos endpoints principais
for EP in \
  "/api/v1/ged/kits" \
  "/api/v1/ged/reports/monthly" \
  "/api/v1/ged/kit-real/$KIT_ID/checklist"; do

  TIME=$(curl -sf -o /dev/null -w "%{time_total}" \
    "http://127.0.0.1:8080$EP" \
    -H "Authorization: Bearer $TOKEN")
  MS=$(echo "$TIME * 1000" | bc 2>/dev/null || echo "N/A")
  echo "  $EP → ${TIME}s"
done

# Verificar N+1 queries (kits com JOIN ou sem)
docker exec $CONTAINER psql -U postgres -d conectapro -t -c "
SELECT
  LEFT(query, 100) as query,
  calls,
  ROUND(mean_exec_time::numeric, 1) as media_ms
FROM pg_stat_statements
WHERE query ILIKE '%ged%'
  AND mean_exec_time > 50
ORDER BY mean_exec_time DESC
LIMIT 5;" 2>/dev/null || echo "pg_stat_statements não disponível"
```

### 4. ERROR HANDLING (2 pontos)

```bash
echo "=== ERROR HANDLING GED ==="
# 404 com mensagem clara
curl -sf "http://127.0.0.1:8080/api/v1/ged/kits/uuid-invalido" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys,json
try:
  d=json.load(sys.stdin)
  detail=d.get('detail',{})
  msg=detail.get('message',detail) if isinstance(detail,dict) else detail
  print(f'404 message: {msg}')
except: print('Resposta não é JSON válido — verificar')
"

# 422 em POST sem campos obrigatórios
curl -sf -X POST "http://127.0.0.1:8080/api/v1/ged/kits" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' \
  | python3 -c "
import sys,json
try:
  d=json.load(sys.stdin)
  print(f'POST sem body retorna: {json.dumps(d)[:100]}')
except: print('Sem resposta JSON')
" 2>/dev/null
```

### 5. FRONTEND GED (2 pontos)

```bash
echo "=== FRONTEND GED ==="
# [ ] Namespace antigo não existe mais
COUNT=$(grep -rn "people-management/ged" \
  /opt/conecta-pro/frontend/src/ 2>/dev/null | wc -l)
[ "$COUNT" = "0" ] \
  && echo "  ✅ Namespace limpo (0 refs ao namespace antigo)" \
  || echo "  ❌ $COUNT referências ao namespace antigo ainda existem"

# [ ] useEffect com isOpen nos modais de kit
grep -n "useEffect" \
  /opt/conecta-pro/frontend/src/app/modulos/gestao-pessoas/ged/kits/page.tsx \
  2>/dev/null | head -5

# [ ] Arquivos de página GED existem
for PAGE in \
  "ged/page.tsx" \
  "ged/kits/page.tsx" \
  "ged/clientes/page.tsx" \
  "ged/documentos/page.tsx" \
  "ged/certidoes/page.tsx" \
  "ged/assinaturas/page.tsx" \
  "ged/envios/page.tsx" \
  "ged/relatorios/page.tsx" \
  "ged/configuracoes/page.tsx"; do
  BASE="/opt/conecta-pro/frontend/src/app/modulos/gestao-pessoas"
  [ -f "$BASE/$PAGE" ] \
    && echo "  ✅ $PAGE" \
    || echo "  ❌ $PAGE — ARQUIVO AUSENTE"
done
```

## Scoring

```
15/15 → 10/10 ✅ Submódulo fechado
13-14 → 9/10  🟡 Corrigir pendências menores
10-12 → 7/10  🟠 Trabalho necessário
< 10  → < 7   🔴 Não fechar — bugs críticos
```

## Bugs recorrentes GED — verificar sempre

```bash
# B1: client_name NULL → falta JOIN ged_clients no SELECT
# B2: /documents/search 500 → rota /{id} antes de /search
# B3: trailing slash → prefix="/ged/clients/" causa 404
# B4: dropdown vazio → useEffect([], []) sem isOpen
# B5: namespace antigo → /people-management/ged/* no frontend
# B6: assinaturas 401 → get_current_user ausente no endpoint
# B7: kits fantasmas → mês/ano sem filtro correto no assembler
```

## Relatório de review obrigatório

```
MÓDULO REVISADO: GED — [submódulo]
DATA: [data]
PONTUAÇÃO: [X]/15

ITENS APROVADOS:
- [lista]

ITENS REPROVADOS:
- [bug] → fix necessário: [descrição]

DECLARAÇÃO: [10/10 APROVADO / REPROVADO — corrigir X antes de fechar]
```
---
name: design-api-ged
description: Padrões de design de API e auditoria de endpoints do módulo GED do Conecta PRO. Usar ao criar novos endpoints GED, auditar respostas incorretas e garantir consistência entre os controllers ged_controller, ged_config_controller e document_controller.
---

# Design de API RESTful — Módulo GED

## Mapa completo de endpoints GED

```
BASE: http://127.0.0.1:8080/api/v1/ged/

── KITS DOCUMENTAIS ──────────────────────────────────────
GET    /kits                          → listar todos os kits
POST   /kits                          → criar novo kit
GET    /kits/{id}                     → detalhe do kit
PUT    /kits/{id}                     → atualizar kit
POST   /kits/{id}/send                → enviar kit ao cliente
POST   /kits/{id}/approve             → aprovar/concluir kit
GET    /kits/{id}/download-zip        → baixar ZIP do kit completo
GET    /kit-real/{id}/checklist       → checklist com documentos reais

── MONTAGEM AUTOMÁTICA ───────────────────────────────────
GET    /montar/condominios            → listar condomínios para montar
POST   /montar/auto                   → disparar montagem automática

── CLIENTES / CONDOMÍNIOS ────────────────────────────────
GET    /clients                       → listar clientes GED (12 ativos)
GET    /clients/{id}                  → detalhe do cliente

── DOCUMENTOS ────────────────────────────────────────────
GET    /documents/search              → busca full-text (ANTES de /{id})
GET    /documents/{id}                → detalhe do documento
POST   /documents                     → upload de documento
DELETE /documents/{id}                → remover documento

── CERTIDÕES ─────────────────────────────────────────────
GET    /certidoes                     → listar certidões da empresa
POST   /certidoes                     → adicionar certidão
PUT    /certidoes/{id}                → renovar certidão
DELETE /certidoes/{id}                → remover certidão

── ASSINATURAS ───────────────────────────────────────────
GET    /document-signatures/stats/summary → resumo de assinaturas
GET    /document-signatures           → listar pendências de assinatura
POST   /document-signatures/{id}/sign → assinar documento

── CONFIGURAÇÕES ─────────────────────────────────────────
GET    /config/drive                  → status integração Google Drive
POST   /config/drive/connect          → conectar Google Drive (OAuth)
GET    /config/schedule               → configuração de agendamento
PUT    /config/schedule               → salvar agendamento
GET    /config/email-templates        → templates de e-mail
PUT    /config/email-templates/{id}   → editar template
GET    /config/document-types         → tipos de documento cadastrados
POST   /config/document-types         → adicionar tipo de documento

── RELATÓRIOS ────────────────────────────────────────────
GET    /reports/monthly               → relatório mensal (março/2026)
GET    /reports/kits                  → relatório por kit
GET    /reports/certidoes             → relatório de certidões
```

## Padrões obrigatórios GED

### Nomenclatura

```
✅ CORRETO:
GET    /api/v1/ged/kits
GET    /api/v1/ged/kits/{id}
GET    /api/v1/ged/documents/search    ← /search ANTES de /{id}
GET    /api/v1/ged/clients             ← sem trailing slash
POST   /api/v1/ged/kits/{id}/send      ← ação como sub-recurso

❌ ERRADO:
GET    /api/v1/ged/getKits             ← verbo no path
GET    /api/v1/ged/clients/            ← trailing slash → 404
GET    /api/v1/ged/documents/{id}      ← antes de /search → captura "search" como UUID
GET    /api/v1/people-management/ged/  ← namespace antigo → 404
```

### Padrão de resposta — kits

```python
# GET /kits — lista de kits com client_name obrigatório
{
  "kits": [                         # ou "data" — manter consistente
    {
      "id": "uuid",
      "client_id": "uuid",
      "client_name": "Condomínio Ideal Flores da Cidade",  # NUNCA null
      "reference_month": "2026-03",
      "status": "em_montagem",      # ou "concluido"
      "progress": 0.42,             # 0.0 a 1.0
      "total_documents": 19,
      "signed_documents": 8,
      "created_at": "2026-03-01T00:00:00Z"
    }
  ],
  "total": 13,
  "meta": {
    "concluidos": 1,
    "em_montagem": 12
  }
}

# GET /kits/{id} — detalhe com checklist
{
  "id": "uuid",
  "client_name": "Condomínio Ideal Flores da Cidade",
  "reference_month": "2026-03",
  "status": "concluido",
  "documents": [
    {
      "id": "uuid",
      "type": "contracheque",
      "employee_name": "João Silva",
      "status": "assinado",
      "uploaded_at": "2026-03-15T10:00:00Z",
      "download_url": "/api/v1/ged/documents/{id}/download"
    }
  ],
  "total_documents": 19,
  "signed_documents": 19
}
```

### Padrão de resposta — erro

```python
# 404 — kit não encontrado
raise HTTPException(
    status_code=404,
    detail={
        "code": "KIT_NOT_FOUND",
        "message": f"Kit com ID '{kit_id}' não encontrado."
    }
)

# 422 — campos obrigatórios ausentes
raise HTTPException(
    status_code=422,
    detail={
        "code": "VALIDATION_ERROR",
        "message": "Dados inválidos para criação do kit.",
        "fields": {
            "client_id": "Cliente é obrigatório",
            "reference_month": "Mês de referência é obrigatório"
        }
    }
)

# 409 — kit do mês já existe para esse cliente
raise HTTPException(
    status_code=409,
    detail={
        "code": "KIT_ALREADY_EXISTS",
        "message": "Já existe um kit para este cliente em março/2026."
    }
)
```

### Padrão de router FastAPI — GED

```python
# ged_controller.py
# ✅ CORRETO — sem trailing slash
router = APIRouter(
    prefix="/ged",
    tags=["GED — Kits Documentais"]
)

# ✅ CORRETO — /search antes de /{id}
@router.get("/documents/search")
async def search_documents(...): ...

@router.get("/documents/{document_id}")
async def get_document(...): ...

# ❌ ERRADO — /{id} antes de /search
@router.get("/documents/{document_id}")  # captura "search" como UUID!
async def get_document(...): ...

@router.get("/documents/search")          # nunca alcançado
async def search_documents(...): ...
```

## Setup de auditoria

```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Listar todos os endpoints GED registrados
curl -sf "http://127.0.0.1:8080/openapi.json" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys,json
d=json.load(sys.stdin)
paths={k:v for k,v in d.get('paths',{}).items() if '/ged' in k.lower()}
print(f'Endpoints GED registrados: {len(paths)}')
for path,methods in sorted(paths.items()):
  for m in methods:
    if m in ['get','post','put','delete','patch']:
      print(f'  {m.upper()} {path}')
" 2>/dev/null
```

## Checklist para novo endpoint GED

```
[ ] Prefixo: router = APIRouter(prefix="/ged/[recurso]") — sem barra final
[ ] /search registrada ANTES de /{id} se ambas existem
[ ] Requer autenticação: Depends(get_current_user)
[ ] client_name populado via JOIN ged_clients (nunca null)
[ ] Retorna 404 com code/message para UUID inválido
[ ] Retorna 422 para campos obrigatórios ausentes
[ ] Registrado em main_production.py
[ ] Testado via curl com token real e KIT_ID real
[ ] Commitado: fix(ged): descrição precisa
```

## Auditoria de inconsistências GED × banco

```bash
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)

# Kits sem cliente vinculado no banco
docker exec $CONTAINER psql -U postgres -d conectapro -t -c "
SELECT COUNT(*) as kits_sem_cliente
FROM ged_document_kits gk
LEFT JOIN ged_clients gc ON gk.client_id = gc.id
WHERE gc.id IS NULL;" 2>/dev/null

# Documentos sem kit vinculado
docker exec $CONTAINER psql -U postgres -d conectapro -t -c "
SELECT COUNT(*) as docs_orfaos
FROM ged_documents gd
LEFT JOIN ged_document_kits gk ON gd.kit_id = gk.id
WHERE gk.id IS NULL;" 2>/dev/null

# Certidões vencidas
docker exec $CONTAINER psql -U postgres -d conectapro -t -c "
SELECT name, expiry_date,
  CASE WHEN expiry_date < NOW() THEN '🔴 VENCIDA'
       WHEN expiry_date < NOW() + INTERVAL '30 days' THEN '🟡 VENCE EM BREVE'
       ELSE '✅ VÁLIDA'
  END as status
FROM ged_certidoes
ORDER BY expiry_date;" 2>/dev/null
```
---
name: testes-ged
description: Bateria de testes automatizados para o módulo GED do Conecta PRO — backend FastAPI com pytest e testes E2E via curl. Cobre todos os 11 endpoints críticos, cenários de erro, dados reais (Ideal Flores) e testes de regressão dos bugs já corrigidos.
---

# Testes Automatizados — Módulo GED

## Setup

```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)

# IDs de referência
KIT_ID="2826deb4-722a-4d77-bc87-8af375240eef"        # Ideal Flores
CLIENT_ID="4db583b6-815a-494f-a1e3-0c62fa81eca9"     # Ideal Flores
```

## Bateria de testes E2E via curl (execução rápida)

```bash
python3 << 'PYEOF'
import subprocess, json

def run(cmd):
    return subprocess.run(cmd, shell=True,
        capture_output=True, text=True, timeout=15).stdout.strip()

TOKEN = run("""curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=jjesus@conectamais.pro&password=Jordan0612' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" """)

KIT_ID   = "2826deb4-722a-4d77-bc87-8af375240eef"
CLIENT_ID = "4db583b6-815a-494f-a1e3-0c62fa81eca9"

TESTES = [
  # (descrição, método, path, esperado, requer_auth)
  # ── ENDPOINTS PRINCIPAIS ──
  ("Listar kits",                     "GET", "/api/v1/ged/kits",                              200, True),
  ("Listar clientes",                 "GET", "/api/v1/ged/clients",                           200, True),
  ("Busca documentos",                "GET", "/api/v1/ged/documents/search",                  200, True),
  ("Config Drive",                    "GET", "/api/v1/ged/config/drive",                      200, True),
  ("Config Agendamento",              "GET", "/api/v1/ged/config/schedule",                   200, True),
  ("Templates e-mail",                "GET", "/api/v1/ged/config/email-templates",            200, True),
  ("Tipos de documento",              "GET", "/api/v1/ged/config/document-types",             200, True),
  ("Relatório mensal",                "GET", "/api/v1/ged/reports/monthly",                   200, True),
  ("Stats assinaturas",               "GET", "/api/v1/ged/document-signatures/stats/summary", 200, True),
  ("Checklist Ideal Flores",          "GET", f"/api/v1/ged/kit-real/{KIT_ID}/checklist",      200, True),
  ("Montar condomínios",              "GET", "/api/v1/ged/montar/condominios",                200, True),
  # ── SEGURANÇA ──
  ("Kits sem token = 401",            "GET", "/api/v1/ged/kits",                              401, False),
  ("Clientes sem token = 401",        "GET", "/api/v1/ged/clients",                           401, False),
  ("Relatório sem token = 401",       "GET", "/api/v1/ged/reports/monthly",                   401, False),
  # ── ERROR HANDLING ──
  ("UUID inválido = 404",             "GET", "/api/v1/ged/kits/00000000-0000-0000-0000-000000000000", 404, True),
  # ── BUSCA ──
  ("Busca vazia retorna lista",       "GET", "/api/v1/ged/documents/search?q=teste",          200, True),
]

pass_count = 0
fail_count = 0

print("=" * 60)
print("TESTES GED — CONECTA PRO")
print("=" * 60)

for desc, method, path, esperado, auth in TESTES:
    headers = f'-H "Authorization: Bearer {TOKEN}"' if auth else ""
    status = run(
        f'curl -sf -o /dev/null -w "%{{http_code}}" '
        f'-X {method} "http://127.0.0.1:8080{path}" {headers}'
    )
    ok = status == str(esperado)
    icon = "✅" if ok else "❌"
    print(f"  {icon} {desc}")
    if not ok:
        print(f"     → esperado {esperado}, obtido {status}")
    if ok: pass_count += 1
    else: fail_count += 1

total = pass_count + fail_count
pct = round(pass_count / total * 100)
print(f"\n{'='*60}")
print(f"RESULTADO: {pass_count}/{total} ({pct}%)")
print(f"{'='*60}")
PYEOF
```

## Testes de dados reais

```bash
echo "=== VALIDAÇÃO DE DADOS REAIS ==="

# T1: 13 kits no sistema
TOTAL_KITS=$(curl -sf "http://127.0.0.1:8080/api/v1/ged/kits" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys,json
d=json.load(sys.stdin)
kits=d if isinstance(d,list) else d.get('kits',d.get('data',[]))
print(len(kits))")
echo "Kits totais: $TOTAL_KITS (esperado ≥13)"

# T2: 12 clientes GED
TOTAL_CLIENTES=$(curl -sf "http://127.0.0.1:8080/api/v1/ged/clients" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys,json
d=json.load(sys.stdin)
clientes=d if isinstance(d,list) else d.get('clients',d.get('data',[]))
print(len(clientes))")
echo "Clientes GED: $TOTAL_CLIENTES (esperado 12)"

# T3: Kit Ideal Flores com ≥19 tipos de documento
TIPOS=$(curl -sf \
  "http://127.0.0.1:8080/api/v1/ged/kit-real/$KIT_ID/checklist" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(d.get('total_tipos',d.get('total',0)))")
echo "Tipos de doc Ideal Flores: $TIPOS (esperado ≥19)"

# T4: client_name presente em todos os kits
curl -sf "http://127.0.0.1:8080/api/v1/ged/kits" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys,json
d=json.load(sys.stdin)
kits=d if isinstance(d,list) else d.get('kits',d.get('data',[]))
nulos=[k.get('id','?')[:8] for k in kits if not k.get('client_name')]
if nulos: print(f'❌ {len(nulos)} kits sem client_name: {nulos}')
else: print(f'✅ Todos os {len(kits)} kits têm client_name')
"

# T5: Certidões — 3 válidas, 1 vencida (Alvará PF)
curl -sf "http://127.0.0.1:8080/api/v1/ged/certidoes" \
  -H "Authorization: Bearer $TOKEN" 2>/dev/null \
  | python3 -c "
import sys,json
from datetime import datetime
try:
  d=json.load(sys.stdin)
  certs=d if isinstance(d,list) else d.get('certidoes',d.get('data',[]))
  now=datetime.now()
  validas=sum(1 for c in certs if c.get('expiry_date','9999') > now.strftime('%Y-%m-%d'))
  vencidas=len(certs)-validas
  print(f'Certidões: {len(certs)} total | {validas} válidas | {vencidas} vencidas')
except Exception as e: print(f'Erro: {e}')
" 2>/dev/null || echo "Endpoint certidões não disponível"

# T6: Relatório mensal com dados reais de março/2026
curl -sf "http://127.0.0.1:8080/api/v1/ged/reports/monthly" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'Relatório: {json.dumps(d)[:200]}')
"
```

## Testes de regressão — bugs já corrigidos

```bash
echo "=== REGRESSÃO GED ==="

# R1: /documents/search não retorna 500 (rota /search antes de /{id})
S=$(curl -sf -o /dev/null -w "%{http_code}" \
  "http://127.0.0.1:8080/api/v1/ged/documents/search" \
  -H "Authorization: Bearer $TOKEN")
[ "$S" = "200" ] \
  && echo "✅ R1: /documents/search → 200" \
  || echo "❌ R1: /documents/search → $S (bug P2 voltou)"

# R2: /ged/clients sem trailing slash retorna 200
S=$(curl -sf -o /dev/null -w "%{http_code}" \
  "http://127.0.0.1:8080/api/v1/ged/clients" \
  -H "Authorization: Bearer $TOKEN")
[ "$S" = "200" ] \
  && echo "✅ R2: /ged/clients → 200" \
  || echo "❌ R2: /ged/clients → $S (bug P3 voltou)"

# R3: client_name não é null
NULOS=$(curl -sf "http://127.0.0.1:8080/api/v1/ged/kits" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys,json
d=json.load(sys.stdin)
kits=d if isinstance(d,list) else d.get('kits',d.get('data',[]))
print(sum(1 for k in kits if not k.get('client_name')))
")
[ "$NULOS" = "0" ] \
  && echo "✅ R3: client_name presente em todos os kits" \
  || echo "❌ R3: $NULOS kits com client_name null (bug P1 voltou)"

# R4: assinaturas não retorna 401
S=$(curl -sf -o /dev/null -w "%{http_code}" \
  "http://127.0.0.1:8080/api/v1/ged/document-signatures/stats/summary" \
  -H "Authorization: Bearer $TOKEN")
[ "$S" = "200" ] \
  && echo "✅ R4: assinaturas → 200" \
  || echo "❌ R4: assinaturas → $S (bug B10 voltou)"

# R5: namespace antigo ausente no frontend
COUNT=$(grep -rn "people-management/ged" \
  /opt/conecta-pro/frontend/src/ 2>/dev/null | wc -l)
[ "$COUNT" = "0" ] \
  && echo "✅ R5: namespace antigo limpo" \
  || echo "❌ R5: $COUNT referências namespace antigo (bug NS voltou)"

echo ""
echo "Regressão concluída."
```

## Testes pytest para o container

```python
# /opt/conecta-pro/backend/tests/integration/test_ged.py
import pytest
from httpx import AsyncClient

KIT_ID    = "2826deb4-722a-4d77-bc87-8af375240eef"
CLIENT_ID = "4db583b6-815a-494f-a1e3-0c62fa81eca9"

@pytest.fixture
async def auth_headers():
    from app.main import app
    async with AsyncClient(app=app, base_url="http://test") as c:
        r = await c.post("/api/v1/auth/login", data={
            "username": "jjesus@conectamais.pro",
            "password": "Jordan0612" # pragma: allowlist secret
        })
        token = r.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

class TestGEDEndpoints:
    async def test_listar_kits(self, auth_headers):
        from app.main import app
        async with AsyncClient(app=app, base_url="http://test") as c:
            r = await c.get("/api/v1/ged/kits", headers=auth_headers)
        assert r.status_code == 200
        d = r.json()
        kits = d if isinstance(d, list) else d.get("kits", d.get("data", []))
        assert len(kits) >= 13

    async def test_kits_tem_client_name(self, auth_headers):
        from app.main import app
        async with AsyncClient(app=app, base_url="http://test") as c:
            r = await c.get("/api/v1/ged/kits", headers=auth_headers)
        d = r.json()
        kits = d if isinstance(d, list) else d.get("kits", d.get("data", []))
        nulos = [k for k in kits if not k.get("client_name")]
        assert len(nulos) == 0, f"{len(nulos)} kits sem client_name"

    async def test_checklist_ideal_flores(self, auth_headers):
        from app.main import app
        async with AsyncClient(app=app, base_url="http://test") as c:
            r = await c.get(
                f"/api/v1/ged/kit-real/{KIT_ID}/checklist",
                headers=auth_headers
            )
        assert r.status_code == 200
        d = r.json()
        total = d.get("total_tipos", d.get("total", 0))
        assert total >= 19, f"Esperado ≥19 tipos, obtido {total}"

    async def test_documents_search_nao_500(self, auth_headers):
        from app.main import app
        async with AsyncClient(app=app, base_url="http://test") as c:
            r = await c.get(
                "/api/v1/ged/documents/search",
                headers=auth_headers
            )
        assert r.status_code == 200  # não 500 nem 422

    async def test_sem_token_retorna_401(self):
        from app.main import app
        async with AsyncClient(app=app, base_url="http://test") as c:
            r = await c.get("/api/v1/ged/kits")
        assert r.status_code == 401

    async def test_uuid_invalido_retorna_404(self, auth_headers):
        from app.main import app
        async with AsyncClient(app=app, base_url="http://test") as c:
            r = await c.get(
                "/api/v1/ged/kits/00000000-0000-0000-0000-000000000000",
                headers=auth_headers
            )
        assert r.status_code == 404
```

```bash
# Executar no container
docker exec $CONTAINER bash -c \
  "cd /app && python -m pytest tests/integration/test_ged.py -v 2>&1" \
  | tail -20
```
---
name: modelagem-banco-ged
description: Auditoria e boas práticas de banco de dados para o módulo GED do Conecta PRO. Cobre as tabelas ged_document_kits, ged_clients, ged_documents e ged_certidoes — queries, índices, integridade referencial e diagnóstico de inconsistências.
---

# Modelagem de Banco — Módulo GED

## Setup

```bash
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)
KIT_ID="2826deb4-722a-4d77-bc87-8af375240eef"
CLIENT_ID="4db583b6-815a-494f-a1e3-0c62fa81eca9"
```

## Tabelas GED — estrutura e contagens

```bash
echo "=== TABELAS GED ==="
for TABELA in \
  "ged_document_kits" \
  "ged_clients" \
  "ged_documents" \
  "ged_certidoes" \
  "ged_document_signatures" \
  "ged_send_history"; do

  COUNT=$(docker exec $CONTAINER psql -U postgres -d conectapro -t -c \
    "SELECT COUNT(*) FROM $TABELA;" 2>/dev/null | tr -d ' ')
  if [ -n "$COUNT" ] && [ "$COUNT" != "" ]; then
    echo "  ✅ $TABELA → $COUNT registros"
  else
    echo "  ⚠️  $TABELA → tabela não existe ou vazia"
  fi
done
```

## Estrutura detalhada das tabelas

```bash
# ged_document_kits
docker exec $CONTAINER psql -U postgres -d conectapro -c "
\d+ ged_document_kits" 2>/dev/null

# ged_clients
docker exec $CONTAINER psql -U postgres -d conectapro -c "
\d+ ged_clients" 2>/dev/null

# ged_documents
docker exec $CONTAINER psql -U postgres -d conectapro -c "
\d+ ged_documents" 2>/dev/null

# ged_certidoes
docker exec $CONTAINER psql -U postgres -d conectapro -c "
\d+ ged_certidoes" 2>/dev/null
```

## Diagnóstico de dados do GED

```bash
echo "=== DIAGNÓSTICO DADOS GED ==="

# 1. Kits por status
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT
  status,
  COUNT(*) as qtd,
  MIN(reference_month) as mais_antigo,
  MAX(reference_month) as mais_recente
FROM ged_document_kits
GROUP BY status
ORDER BY qtd DESC;" 2>/dev/null

# 2. Kits com client_name (via JOIN)
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT
  gk.id,
  gk.status,
  gk.reference_month,
  gc.name as client_name,
  CASE WHEN gc.id IS NULL THEN '⚠️ SEM CLIENTE' ELSE '✅' END as check
FROM ged_document_kits gk
LEFT JOIN ged_clients gc ON gk.client_id = gc.id
ORDER BY gk.created_at DESC
LIMIT 15;" 2>/dev/null

# 3. Documentos por kit (Ideal Flores)
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT
  document_type,
  status,
  COUNT(*) as qtd
FROM ged_documents
WHERE kit_id = '$KIT_ID'
GROUP BY document_type, status
ORDER BY document_type;" 2>/dev/null

# 4. Certidões com status de vencimento
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT
  name,
  document_type,
  expiry_date,
  CASE
    WHEN expiry_date < CURRENT_DATE THEN '🔴 VENCIDA'
    WHEN expiry_date < CURRENT_DATE + INTERVAL '30 days' THEN '🟡 VENCE EM BREVE'
    ELSE '✅ VÁLIDA'
  END as status_vencimento,
  CURRENT_DATE - expiry_date::date as dias_vencida
FROM ged_certidoes
ORDER BY expiry_date;" 2>/dev/null

# 5. Kits sem cliente vinculado (orphans)
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT COUNT(*) as kits_orfaos
FROM ged_document_kits gk
LEFT JOIN ged_clients gc ON gk.client_id = gc.id
WHERE gc.id IS NULL;" 2>/dev/null

# 6. Documentos sem kit vinculado
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT COUNT(*) as docs_orfaos
FROM ged_documents gd
LEFT JOIN ged_document_kits gk ON gd.kit_id = gk.id
WHERE gk.id IS NULL;" 2>/dev/null

# 7. Clientes GED × clientes CRM (sincronização)
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT
  gc.name as cliente_ged,
  c.name as cliente_crm,
  CASE WHEN c.id IS NULL THEN '⚠️ SEM MATCH CRM'
       ELSE '✅ SINCRONIZADO'
  END as sync
FROM ged_clients gc
LEFT JOIN clients c ON LOWER(gc.name) LIKE '%' || LOWER(SPLIT_PART(c.name,' ',1)) || '%'
ORDER BY gc.name;" 2>/dev/null
```

## Criar índices de performance para GED

```bash
docker exec $CONTAINER psql -U postgres -d conectapro -c "
-- Índice para busca de kits por cliente
CREATE INDEX IF NOT EXISTS idx_ged_kits_client_id
  ON ged_document_kits(client_id);

-- Índice para kits por mês de referência
CREATE INDEX IF NOT EXISTS idx_ged_kits_reference_month
  ON ged_document_kits(reference_month);

-- Índice para kits por status
CREATE INDEX IF NOT EXISTS idx_ged_kits_status
  ON ged_document_kits(status);

-- Índice para documentos por kit
CREATE INDEX IF NOT EXISTS idx_ged_docs_kit_id
  ON ged_documents(kit_id);

-- Índice para documentos por tipo
CREATE INDEX IF NOT EXISTS idx_ged_docs_type
  ON ged_documents(document_type);

-- Índice para certidões por vencimento (alertas)
CREATE INDEX IF NOT EXISTS idx_ged_certidoes_expiry
  ON ged_certidoes(expiry_date)
  WHERE expiry_date IS NOT NULL;

-- Índice para busca full-text de documentos
CREATE INDEX IF NOT EXISTS idx_ged_docs_search
  ON ged_documents USING gin(to_tsvector('portuguese', COALESCE(name, '')));

ANALYZE;
" 2>/dev/null
echo "✅ Índices GED criados/verificados"
```

## Backup antes de operações críticas no GED

```bash
# SEMPRE fazer backup antes de UPDATE/DELETE em produção
TIMESTAMP=$(date +%Y%m%d_%H%M)
docker exec $CONTAINER psql -U postgres -d conectapro -c "
CREATE TABLE IF NOT EXISTS ged_document_kits_backup_$TIMESTAMP
  AS SELECT * FROM ged_document_kits;
CREATE TABLE IF NOT EXISTS ged_documents_backup_$TIMESTAMP
  AS SELECT * FROM ged_documents;
SELECT 'Backup criado: $TIMESTAMP' as resultado;"

echo "Backup criado: ged_document_kits_backup_$TIMESTAMP"
echo "Backup criado: ged_documents_backup_$TIMESTAMP"
```

## Modelos SQLAlchemy GED — padrão de referência

```python
# /opt/conecta-pro/backend/modules/ged/models/ged_document_kit.py
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from core.database import Base

class GedDocumentKit(Base):
    __tablename__ = "ged_document_kits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True),
                       ForeignKey("ged_clients.id", ondelete="CASCADE"),
                       nullable=False)
    reference_month = Column(String(7), nullable=False)  # "2026-03"
    status = Column(
        Enum("em_montagem", "concluido", "enviado",
             name="ged_kit_status"),
        default="em_montagem", nullable=False
    )
    progress = Column(Float, default=0.0)
    total_documents = Column(Integer, default=0)
    signed_documents = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True),
                        default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    client = relationship("GedClient", back_populates="kits")
    documents = relationship("GedDocument", back_populates="kit",
                              cascade="all, delete-orphan")
```

## Queries de diagnóstico avançado

```bash
# Verificar kits duplicados (mesmo cliente + mesmo mês)
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT
  client_id,
  reference_month,
  COUNT(*) as duplicatas
FROM ged_document_kits
GROUP BY client_id, reference_month
HAVING COUNT(*) > 1
ORDER BY duplicatas DESC;" 2>/dev/null

# Verificar progresso real dos kits (calculado no banco)
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT
  gk.id,
  gc.name as cliente,
  gk.reference_month,
  gk.status,
  COUNT(gd.id) as total_docs,
  COUNT(gd.id) FILTER (WHERE gd.status = 'assinado') as assinados,
  ROUND(
    COUNT(gd.id) FILTER (WHERE gd.status = 'assinado')::numeric
    / NULLIF(COUNT(gd.id), 0) * 100, 1
  ) as pct_completo
FROM ged_document_kits gk
JOIN ged_clients gc ON gk.client_id = gc.id
LEFT JOIN ged_documents gd ON gd.kit_id = gk.id
GROUP BY gk.id, gc.name, gk.reference_month, gk.status
ORDER BY pct_completo DESC NULLS LAST;" 2>/dev/null
```
---
name: autenticacao-ged
description: Auditoria de autenticação e autorização dos endpoints do módulo GED do Conecta PRO. Verificar proteção JWT em todos os 11+ endpoints, detectar endpoints expostos sem token e validar fluxo de assinatura eletrônica.
---

# Autenticação e Autorização — Módulo GED

## Setup

```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)
```

## Auditoria de segurança — todos os endpoints GED

```bash
python3 << 'PYEOF'
import subprocess, json

def run(cmd, timeout=10):
    return subprocess.run(cmd, shell=True,
        capture_output=True, text=True, timeout=timeout).stdout.strip()

TOKEN = run("""curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=jjesus@conectamais.pro&password=Jordan0612' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" """)

KIT_ID = "2826deb4-722a-4d77-bc87-8af375240eef"

ENDPOINTS_GED = [
  f"/api/v1/ged/kits",
  f"/api/v1/ged/clients",
  f"/api/v1/ged/documents/search",
  f"/api/v1/ged/config/drive",
  f"/api/v1/ged/config/schedule",
  f"/api/v1/ged/config/email-templates",
  f"/api/v1/ged/config/document-types",
  f"/api/v1/ged/reports/monthly",
  f"/api/v1/ged/document-signatures/stats/summary",
  f"/api/v1/ged/kit-real/{KIT_ID}/checklist",
  f"/api/v1/ged/montar/condominios",
]

print("=" * 60)
print("AUDITORIA DE SEGURANÇA — GED")
print("=" * 60)

vulneraveis = []
protegidos  = []

for path in ENDPOINTS_GED:
    # 1. Sem token
    s_sem = run(f'curl -sf -o /dev/null -w "%{{http_code}}" '
                f'"http://127.0.0.1:8080{path}"')
    # 2. Token inválido
    s_inv = run(f'curl -sf -o /dev/null -w "%{{http_code}}" '
                f'"http://127.0.0.1:8080{path}" '
                f'-H "Authorization: Bearer TOKEN_INVALIDO_123"')
    # 3. Com token válido
    s_ok  = run(f'curl -sf -o /dev/null -w "%{{http_code}}" '
                f'"http://127.0.0.1:8080{path}" '
                f'-H "Authorization: Bearer {TOKEN}"')

    ok = (s_sem == "401" and s_inv == "401" and s_ok == "200")
    icon = "✅" if ok else "❌"
    print(f"  {icon} {path}")
    print(f"     sem token: {s_sem} | token inválido: {s_inv} | válido: {s_ok}")

    if ok: protegidos.append(path)
    else:  vulneraveis.append((path, s_sem, s_inv, s_ok))

print(f"\n{'='*60}")
print(f"Protegidos: {len(protegidos)}/{len(ENDPOINTS_GED)}")
if vulneraveis:
    print(f"\n⚠️ VULNERABILIDADES:")
    for path, s1, s2, s3 in vulneraveis:
        if s1 != "401": print(f"  🔓 {path} — sem token retorna {s1}")
        if s3 != "200": print(f"  🔒 {path} — token válido retorna {s3} (deve ser 200)")
PYEOF
```

## Padrão de autenticação nos controllers GED

```python
# ✅ CORRETO — todo endpoint GED deve ter get_current_user
from core.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db

@router.get("/kits")
async def listar_kits(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)  # ← OBRIGATÓRIO
):
    pass

@router.get("/kit-real/{kit_id}/checklist")
async def checklist_kit(
    kit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)  # ← OBRIGATÓRIO
):
    pass

# ❌ ERRADO — endpoint GED sem autenticação
@router.get("/clients")
async def listar_clientes(db: AsyncSession = Depends(get_db)):
    # ← Qualquer pessoa pode listar clientes da empresa!
    pass
```

## Verificar assinaturas eletrônicas — fluxo de auth

```bash
echo "=== ASSINATURAS ELETRÔNICAS ==="

# Endpoint stats/summary (deve retornar 200 com token)
S=$(curl -sf -o /dev/null -w "%{http_code}" \
  "http://127.0.0.1:8080/api/v1/ged/document-signatures/stats/summary" \
  -H "Authorization: Bearer $TOKEN")
echo "Stats summary com token válido: $S (esperado 200)"

# Sem token (deve retornar 401)
S=$(curl -sf -o /dev/null -w "%{http_code}" \
  "http://127.0.0.1:8080/api/v1/ged/document-signatures/stats/summary")
echo "Stats summary sem token: $S (esperado 401)"

# Conteúdo das stats de assinatura
curl -sf \
  "http://127.0.0.1:8080/api/v1/ged/document-signatures/stats/summary" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'Stats assinaturas: {json.dumps(d, indent=2)[:300]}')
"
```

## Verificar usuário atual nos endpoints GED

```bash
# Decodificar token para confirmar usuário
python3 -c "
import base64, json
token = '$TOKEN'
parts = token.split('.')
payload = parts[1] + '=' * (4 - len(parts[1]) % 4)
decoded = json.loads(base64.b64decode(payload))
print(f'Usuário: {decoded.get(\"name\",\"?\")}'    )
print(f'Email:   {decoded.get(\"sub\",\"?\")}'     )
print(f'Role:    {decoded.get(\"role\",\"?\")}'    )
print(f'Expira:  {decoded.get(\"exp\",\"?\")}'     )
" 2>/dev/null

# Verificar usuário no banco
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT id, name, email, role, is_active
FROM users
WHERE email = 'jjesus@conectamais.pro';" 2>/dev/null
```

## Checklist de auth GED

```
[ ] GET /ged/kits — 401 sem token
[ ] GET /ged/clients — 401 sem token
[ ] GET /ged/documents/search — 401 sem token
[ ] GET /ged/config/drive — 401 sem token
[ ] GET /ged/config/schedule — 401 sem token
[ ] GET /ged/reports/monthly — 401 sem token
[ ] GET /ged/document-signatures/stats/summary — 401 sem token
[ ] GET /ged/kit-real/{id}/checklist — 401 sem token
[ ] GET /ged/montar/condominios — 401 sem token
[ ] POST /ged/kits — 401 sem token
[ ] PUT /ged/kits/{id} — 401 sem token
[ ] Todos retornam 200 com token válido
[ ] Token expirado retorna 401 (não 500)
```
---
name: docker-deploy-ged
description: Protocolo de hot copy e deploy para o módulo GED do Conecta PRO. Cobre os arquivos modificáveis do GED, sequência correta de hot copy para backend e build para frontend, e diagnóstico de containers quando o GED para de responder.
---

# Docker e Deploy — Módulo GED

## Estrutura de arquivos do GED

```
backend/modules/ged/
├── controllers/
│   ├── ged_controller.py          ← kits, clientes, download ZIP
│   ├── ged_config_controller.py   ← config drive/schedule/templates/types
│   └── document_controller.py     ← documentos, /search
├── models/
│   ├── ged_document_kit.py
│   ├── ged_client.py
│   └── ged_document.py
└── services/
    └── kit_assembly_service.py    ← montagem automática

frontend/src/app/modulos/gestao-pessoas/ged/
├── page.tsx                       ← Dashboard GED
├── kits/page.tsx                  ← Lista de kits
├── clientes/page.tsx
├── documentos/page.tsx
├── certidoes/page.tsx
├── assinaturas/page.tsx
├── envios/page.tsx
├── relatorios/page.tsx
└── configuracoes/page.tsx
```

## Setup

```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)
GED_BACK="/opt/conecta-pro/backend/modules/ged"
GED_FRONT="/opt/conecta-pro/frontend/src/app/modulos/gestao-pessoas/ged"
```

## Hot copy — GED backend (padrão)

```bash
# Após editar qualquer controller do GED:

# Controller de kits
docker cp $GED_BACK/controllers/ged_controller.py \
  $CONTAINER:/app/modules/ged/controllers/ged_controller.py
docker restart $CONTAINER && sleep 8

# Controller de config
docker cp $GED_BACK/controllers/ged_config_controller.py \
  $CONTAINER:/app/modules/ged/controllers/ged_config_controller.py
docker restart $CONTAINER && sleep 8

# Controller de documentos
docker cp $GED_BACK/controllers/document_controller.py \
  $CONTAINER:/app/modules/ged/controllers/document_controller.py
docker restart $CONTAINER && sleep 8

# Serviço de montagem
docker cp $GED_BACK/services/kit_assembly_service.py \
  $CONTAINER:/app/modules/ged/services/kit_assembly_service.py
docker restart $CONTAINER && sleep 8

# Validar após hot copy
echo "Validando endpoints GED..."
for EP in \
  "/api/v1/ged/kits" \
  "/api/v1/ged/clients" \
  "/api/v1/ged/documents/search"; do
  S=$(curl -sf -o /dev/null -w "%{http_code}" \
    "http://127.0.0.1:8080$EP" \
    -H "Authorization: Bearer $TOKEN")
  echo "  $EP → $S"
done
```

## Hot copy múltiplos arquivos GED (quando fix afeta vários)

```bash
# Copiar todos os controllers do GED de uma vez
for FILE in \
  "controllers/ged_controller.py" \
  "controllers/ged_config_controller.py" \
  "controllers/document_controller.py" \
  "services/kit_assembly_service.py"; do
  docker cp "$GED_BACK/$FILE" \
    "$CONTAINER:/app/modules/ged/$FILE" \
    && echo "✅ Copiado: $FILE" \
    || echo "❌ Falhou: $FILE"
done
docker restart $CONTAINER && sleep 8
echo "✅ Backend GED atualizado"
```

## Build frontend GED (quando há mudança de página)

```bash
# Verificar RAM antes do build
free -m | awk '/^Mem:/{print "RAM livre: " $4 "MB (mínimo recomendado: 1000MB)"}'

# Build serializado (NUNCA dois builds simultâneos)
cd /opt/conecta-pro/frontend
NODE_OPTIONS=--max-old-space-size=4096 npm run build 2>&1 | tail -20

# Se build OK, reiniciar PM2
pm2 restart conecta-pro-frontend --update-env && pm2 save && sleep 8

# Validar frontend GED
curl -sf -o /dev/null -w "Frontend GED: %{http_code}\n" \
  "https://erp.conectamais.pro/modulos/gestao-pessoas/ged"
```

## Diagnóstico quando GED para de responder

```bash
echo "=== DIAGNÓSTICO GED ==="

# 1. Container rodando?
docker ps --filter ancestor=conecta-pro-backend \
  --format "{{.Names}} | {{.Status}}"

# 2. Backend respondendo?
curl -sf -o /dev/null -w "Backend: %{http_code}\n" \
  "http://127.0.0.1:8080/docs"

# 3. Erros recentes no container
docker logs $CONTAINER --tail 30 2>&1 \
  | grep -i "error\|exception\|traceback\|ged\|kit" | head -20

# 4. Endpoint GED específico
curl -sf "http://127.0.0.1:8080/api/v1/ged/kits" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys, json
try:
  d = json.load(sys.stdin)
  kits = d if isinstance(d, list) else d.get('kits', d.get('data', []))
  print(f'✅ GED respondendo: {len(kits)} kits')
except Exception as e:
  print(f'❌ Resposta inválida: {e}')
"

# 5. PM2 e frontend
pm2 list | grep "conecta-pro-frontend"
```

## Recuperar GED travado

```bash
# GED retornando 500 — verificar import quebrado
docker logs $CONTAINER --tail 50 2>&1 | \
  grep -A3 "ImportError\|ModuleNotFoundError\|SyntaxError"

# Solução: verificar sintaxe do arquivo antes do hot copy
python3 -m py_compile $GED_BACK/controllers/ged_controller.py \
  && echo "✅ Sintaxe OK" \
  || echo "❌ Erro de sintaxe — NÃO fazer hot copy"

# GED retornando 404 — verificar registro no main_production.py
grep -n "ged" /opt/conecta-pro/backend/main_production.py | head -10

# Frontend GED com erro 500 — verificar build
pm2 logs conecta-pro-frontend --lines 20 --nostream 2>/dev/null | \
  grep -i "error\|ged" | head -10
```

## Health check completo GED

```bash
python3 << 'PYEOF'
import subprocess, datetime

def chk(nome, cmd):
    r = subprocess.run(cmd, shell=True,
        capture_output=True, text=True, timeout=10)
    ok = "200" in r.stdout or r.returncode == 0
    print(f"  {'✅' if ok else '❌'} {nome}")
    return ok

TOKEN = subprocess.run(
    "curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login "
    "-H 'Content-Type: application/x-www-form-urlencoded' "
    "-d 'username=jjesus@conectamais.pro&password=Jordan0612' "
    "| python3 -c \"import sys,json; print(json.load(sys.stdin)['access_token'])\"",
    shell=True, capture_output=True, text=True
).stdout.strip()

print(f"\n=== HEALTH CHECK GED {datetime.datetime.now().strftime('%H:%M:%S')} ===")

checks = [
    ("Backend /docs", 'curl -sf -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/docs | grep 200'),
    ("GED kits",     f'curl -sf -o /dev/null -w "%{{http_code}}" http://127.0.0.1:8080/api/v1/ged/kits -H "Authorization: Bearer {TOKEN}" | grep 200'),
    ("GED clients",  f'curl -sf -o /dev/null -w "%{{http_code}}" http://127.0.0.1:8080/api/v1/ged/clients -H "Authorization: Bearer {TOKEN}" | grep 200'),
    ("GED reports",  f'curl -sf -o /dev/null -w "%{{http_code}}" http://127.0.0.1:8080/api/v1/ged/reports/monthly -H "Authorization: Bearer {TOKEN}" | grep 200'),
    ("Frontend GED", 'curl -sf -o /dev/null -w "%{http_code}" https://erp.conectamais.pro/modulos/gestao-pessoas/ged | grep -E "200|307"'),
    ("PM2 online",   'pm2 list | grep -q "online"'),
]

resultados = [chk(n, c) for n, c in checks]
print(f"\nGED: {sum(resultados)}/{len(resultados)} OK")
PYEOF
```

---
name: pipeline-ged
description: Protocolo de commit, versionamento e deploy para o módulo GED do Conecta PRO. Padrão de mensagens de commit GED, sequência de deploy segura, rollback por arquivo e histórico de fixes rastreáveis.
---

# 08 — Pipeline CI/CD — Módulo GED

## Arquivos GED no repositório

```
backend/modules/ged/
  controllers/ged_controller.py
  controllers/ged_config_controller.py
  controllers/document_controller.py
  models/ged_document_kit.py  ·  ged_client.py  ·  ged_document.py
  services/kit_assembly_service.py

frontend/src/app/modulos/gestao-pessoas/ged/
  page.tsx  ·  kits/page.tsx  ·  clientes/page.tsx  ·  documentos/page.tsx
  certidoes/page.tsx  ·  assinaturas/page.tsx  ·  envios/page.tsx
  relatorios/page.tsx  ·  configuracoes/page.tsx
```

## Setup

```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)
```

## Padrão de commit GED — exemplos reais

```bash
# ✅ BONS — descritivos, rastreáveis
git commit -m "fix(ged): client_name NULL nos kits — LEFT JOIN ged_clients no SELECT"
git commit -m "fix(ged): /documents/search 500 — rota /search registrada antes de /{id}"
git commit -m "fix(ged): trailing slash /clients/ → 404 — prefix sem barra final"
git commit -m "fix(ged): dropdown clientes vazio — useEffect com isOpen como dependência"
git commit -m "fix(ged): assinaturas 401 — get_current_user adicionado ao endpoint"
git commit -m "fix(ged): namespace /people-management/ged → /ged em 8 arquivos frontend"
git commit -m "fix(ged): kits fantasmas removidos — filtro mês/ano no assembler"
git commit -m "feat(ged): endpoint /ged/reports/monthly criado — dados reais março/2026"
git commit -m "feat(ged): download ZIP kit funcionando — stream response corrigido"
git commit -m "chore(ged): índices criados — idx_ged_kits_client_id, idx_ged_docs_kit_id"

# ❌ RUINS
git commit -m "fix bug ged"
git commit -m "update kits"
```

## Deploy seguro GED — protocolo completo

```bash
# PASSO 1 — Estado limpo antes de qualquer mudança
cd /opt/conecta-pro
git status
git log --oneline -3

# PASSO 2 — Verificar sintaxe antes do hot copy (nunca subir código quebrado)
python3 -m py_compile backend/modules/ged/controllers/ged_controller.py \
  && echo "✅ Sintaxe OK" || echo "❌ ERRO DE SINTAXE — não fazer hot copy"

# PASSO 3 — Hot copy backend GED
GED_BACK="/opt/conecta-pro/backend/modules/ged"
for FILE in \
  "controllers/ged_controller.py" \
  "controllers/ged_config_controller.py" \
  "controllers/document_controller.py" \
  "services/kit_assembly_service.py"; do
  docker cp "$GED_BACK/$FILE" "$CONTAINER:/app/modules/ged/$FILE" \
    && echo "✅ $FILE" || echo "❌ $FILE"
done
docker restart $CONTAINER && sleep 8

# PASSO 4 — Validar 11 endpoints GED
PASS=0
for EP in \
  "/api/v1/ged/kits" \
  "/api/v1/ged/clients" \
  "/api/v1/ged/documents/search" \
  "/api/v1/ged/config/drive" \
  "/api/v1/ged/config/schedule" \
  "/api/v1/ged/config/email-templates" \
  "/api/v1/ged/config/document-types" \
  "/api/v1/ged/reports/monthly" \
  "/api/v1/ged/document-signatures/stats/summary" \
  "/api/v1/ged/montar/condominios"; do
  S=$(curl -sf -o /dev/null -w "%{http_code}" \
    "http://127.0.0.1:8080$EP" -H "Authorization: Bearer $TOKEN")
  [ "$S" = "200" ] && echo "✅ $EP" && ((PASS++)) || echo "❌ $EP → $S"
done
echo "Passou: $PASS/10"

# PASSO 5 — Build frontend SE houve mudança em páginas GED
cd /opt/conecta-pro/frontend
NODE_OPTIONS=--max-old-space-size=4096 npm run build 2>&1 | tail -10
pm2 restart conecta-pro-frontend --update-env && pm2 save && sleep 8

# PASSO 6 — Commit e push
cd /opt/conecta-pro
git add -A
git commit -m "fix(ged): [DESCRIÇÃO PRECISA]"
git push origin feature/people-management-reorganization
git log --oneline -3
```

## Rollback GED por arquivo

```bash
# Ver commits que tocaram arquivos GED
git log --oneline -- backend/modules/ged/ | head -10
git log --oneline -- frontend/src/app/modulos/gestao-pessoas/ged/ | head -10

# Rollback de controller específico para commit anterior
HASH="[hash_do_commit_bom]"
git checkout $HASH -- backend/modules/ged/controllers/ged_controller.py
docker cp backend/modules/ged/controllers/ged_controller.py \
  $CONTAINER:/app/modules/ged/controllers/ged_controller.py
docker restart $CONTAINER && sleep 8

# Verificar após rollback
curl -sf -o /dev/null -w "Após rollback: %{http_code}\n" \
  "http://127.0.0.1:8080/api/v1/ged/kits" \
  -H "Authorization: Bearer $TOKEN"
```

## Estado atual do repositório

```bash
cd /opt/conecta-pro
git log --oneline -10
git status --short
git diff --stat HEAD~1 HEAD -- backend/modules/ged/ \
  frontend/src/app/modulos/gestao-pessoas/ged/
```

---
name: ux-acessibilidade-ged
description: Auditoria de UX, qualidade visual e acessibilidade do frontend do módulo GED do Conecta PRO. Cobre todos os submódulos visuais — Dashboard, Kits, Clientes, Documentos, Certidões, Assinaturas, Envios, Relatórios e Configurações — com padrões de correção.
---

# 09 — UX e Qualidade Visual — Módulo GED

## Design System (referência)

```
Azul primário:  #1E3A5F  (fundo sidebar, headers)
Laranja acento: #F97316  (botões primários, badges ativos)
Branco:         #FFFFFF  (cards, modais)
Cinza claro:    #F8F9FB  (fundo de página)
Texto primário: #111827
Texto secundário: #6B7280
Sucesso:        #10B981  (status concluído)
Erro:           #EF4444  (status vencido, falha)
Aviso:          #F59E0B  (vence em breve)
```

## Checklist visual por submódulo GED

### Dashboard /ged
```
[ ] Métricas (total kits, concluídos, em montagem) com números reais
[ ] Cards de kits recentes com client_name visível (não UUID)
[ ] Certidões com badge colorido: ✅ Válida / 🟡 Vence em breve / 🔴 Vencida
[ ] Ações rápidas ("Montar Kits", "Nova Certidão") com feedback toast
[ ] Loading spinner enquanto dados carregam (não tela em branco)
[ ] Sem texto "undefined" ou "null" visível em nenhum campo
```

### Kits Documentais /ged/kits
```
[ ] Listagem com nome do cliente visível em todas as linhas
[ ] Barra de progresso colorida: laranja (em andamento), verde (concluído)
[ ] Badge de status legível: "Em Montagem" / "Concluído" / "Enviado"
[ ] Botão "Novo Kit" — cor laranja #F97316, texto branco
[ ] Modal "Novo Kit": fundo branco opaco (NÃO transparente/marrom)
[ ] Dropdown de clientes populado ao abrir o modal
[ ] Filtros por mês/status/cliente visualmente separados
[ ] Botão "Montar Kits" com ícone e toast de confirmação
[ ] Ação "Ver" navega para /ged/kits/{id}
[ ] Botão "Voltar" funciona e retorna para /ged/kits
```

### Detalhes do Kit /ged/kits/{id}
```
[ ] Nome do cliente no título da página (não UUID)
[ ] Checklist de documentos com ícone por tipo
[ ] Status de cada documento: Pendente / Assinado / Aprovado
[ ] Contador "X de Y documentos assinados" visível
[ ] Download ZIP — botão com ícone de download, feedback de progresso
[ ] Upload — área de drag-and-drop ou botão claro
[ ] Histórico de ações com timestamps legíveis
```

### Certidões /ged/certidoes
```
[ ] Cards com cor de borda por status de vencimento
[ ] Data de vencimento formatada em pt-BR (dd/mm/aaaa)
[ ] Ícone de alerta 🔴 para Alvará PF vencido desde 28/02/2026
[ ] Botão "Renovar" visível e funcional
[ ] Upload de nova certidão — formulário claro com campo de data
```

### Configurações /ged/configuracoes
```
[ ] Abas claramente separadas: Drive / Agendamento / E-mail / Tipos
[ ] Status do Drive: "Não configurado" com botão "Conectar Google Drive"
[ ] Formulário de agendamento com campos rotulados
[ ] Toast de confirmação ao salvar qualquer configuração
[ ] Sem erros 500 ao carregar a página
```

## Padrões de correção — bugs visuais comuns GED

### Modal com fundo transparente/marrom
```tsx
// ❌ ERRADO — fundo marrom semitransparente, texto ilegível
<div className="bg-amber-900/50 rounded p-4 text-black">

// ✅ CORRETO — fundo branco sólido, sombra, borda
<div className="fixed inset-0 bg-black/70 z-50
                flex items-center justify-center p-4">
  <div className="bg-white rounded-xl shadow-2xl
                  border border-gray-200 p-6 max-w-lg w-full">
    <h2 className="text-gray-900 font-bold text-lg mb-4">{titulo}</h2>
    {/* conteúdo */}
    <div className="flex justify-end gap-2 mt-4">
      <button className="px-4 py-2 bg-white border border-gray-300
                         text-gray-700 rounded-lg hover:bg-gray-50">
        Cancelar
      </button>
      <button className="px-4 py-2 bg-[#F97316] text-white
                         rounded-lg hover:bg-orange-600">
        Confirmar
      </button>
    </div>
  </div>
</div>
```

### Dropdown de clientes vazio no modal
```tsx
// ❌ ERRADO — busca só na montagem do componente, modal abre vazio
useEffect(() => {
  fetchClientes()
}, [])

// ✅ CORRETO — busca quando modal abre
const [isModalOpen, setIsModalOpen] = useState(false)
const [clientes, setClientes] = useState([])

useEffect(() => {
  if (!isModalOpen) return
  fetch('/api/v1/ged/clients', {
    headers: { Authorization: `Bearer ${token}` }
  })
    .then(r => r.json())
    .then(data => {
      const lista = Array.isArray(data) ? data
                  : data.clients || data.data || []
      setClientes(lista)
    })
}, [isModalOpen])
```

### Loading state — evitar tela em branco
```tsx
// ✅ CORRETO — sempre mostrar loading enquanto busca
const [loading, setLoading] = useState(true)

if (loading) return (
  <div className="flex items-center justify-center h-64">
    <div className="animate-spin w-8 h-8 border-2
                    border-[#F97316] border-t-transparent rounded-full"/>
    <span className="ml-3 text-gray-500">Carregando kits...</span>
  </div>
)
```

### Badge de status dos kits
```tsx
// ✅ CORRETO — cores consistentes com design system
const badgeStatus = {
  em_montagem: "bg-orange-100 text-orange-700 border border-orange-200",
  concluido:   "bg-green-100  text-green-700  border border-green-200",
  enviado:     "bg-blue-100   text-blue-700   border border-blue-200",
}

<span className={`px-2 py-1 rounded-full text-xs font-medium
                  ${badgeStatus[kit.status] || "bg-gray-100 text-gray-600"}`}>
  {kit.status === "em_montagem" ? "Em Montagem"
   : kit.status === "concluido"  ? "Concluído"
   : kit.status === "enviado"    ? "Enviado"
   : kit.status}
</span>
```

## Auditoria visual via linha de comando

```bash
# Verificar erros de TypeScript que causam problemas visuais
cd /opt/conecta-pro/frontend
npx tsc --noEmit 2>&1 | grep -i "ged\|kit\|client" | head -20

# Verificar referências ao namespace antigo
grep -rn "people-management/ged" src/ 2>/dev/null | wc -l
# Esperado: 0

# Verificar se todas as páginas GED existem
for PAGE in \
  "ged/page.tsx" \
  "ged/kits/page.tsx" \
  "ged/clientes/page.tsx" \
  "ged/documentos/page.tsx" \
  "ged/certidoes/page.tsx" \
  "ged/assinaturas/page.tsx" \
  "ged/envios/page.tsx" \
  "ged/relatorios/page.tsx" \
  "ged/configuracoes/page.tsx"; do
  FILE="src/app/modulos/gestao-pessoas/$PAGE"
  [ -f "$FILE" ] && echo "✅ $PAGE" || echo "❌ AUSENTE: $PAGE"
done

# Verificar tamanho das páginas GED (pesadas = lentas)
find .next/static -name "*.js" 2>/dev/null \
  | xargs ls -la 2>/dev/null \
  | sort -k5 -rn | head -5
```

## Bugs visuais GED — verificar sempre

```
[ ] Modal Novo Kit: fundo branco opaco (não marrom transparente)
[ ] Dropdown clientes: useEffect com isOpen como dependência
[ ] client_name visível em todas as linhas da listagem (não UUID)
[ ] Botão Voltar nos detalhes do kit: navega para /ged/kits
[ ] Toast após: Montar Kits / Salvar Config / Criar Kit / Concluir Kit
[ ] Loading spinner enquanto kits carregam
[ ] Certidão vencida: badge vermelho visível (Alvará PF desde 28/02/2026)
[ ] Texto preto sobre fundo branco (não cinza sobre cinza)
[ ] Barra de progresso reflete documentos assinados reais
```

---
name: documentacao-ged
description: Geração de relatório de sessão, scorecard final e contexto para novo chat do módulo GED do Conecta PRO. Usar ao final de cada sessão de auditoria GED para registrar estado, bugs corrigidos e próximos passos.
---

# 10 — Documentação e Relatório de Sessão — Módulo GED

## Gerar relatório completo da sessão GED

```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)
KIT_ID="2826deb4-722a-4d77-bc87-8af375240eef"

python3 << 'PYEOF'
import subprocess, json, datetime

def run(cmd):
    return subprocess.run(cmd, shell=True,
        capture_output=True, text=True, timeout=20).stdout.strip()

TOKEN = run("""curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=jjesus@conectamais.pro&password=Jordan0612' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" """)

CONTAINER = run("docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1")

KIT_ID = "2826deb4-722a-4d77-bc87-8af375240eef"

def ep(path, method="GET"):
    return run(f'curl -sf -o /dev/null -w "%{{http_code}}" '
               f'-X {method} "http://127.0.0.1:8080{path}" '
               f'-H "Authorization: Bearer {TOKEN}"')

def db(sql):
    return run(f'docker exec {CONTAINER} psql -U postgres '
               f'-d conectapro -t -c "{sql}"').strip()

# Testar todos os endpoints GED
ENDPOINTS_GED = [
    ("/api/v1/ged/kits",                              "Kits"),
    ("/api/v1/ged/clients",                           "Clientes"),
    ("/api/v1/ged/documents/search",                  "Busca docs"),
    ("/api/v1/ged/config/drive",                      "Config Drive"),
    ("/api/v1/ged/config/schedule",                   "Agendamento"),
    ("/api/v1/ged/config/email-templates",            "Templates e-mail"),
    ("/api/v1/ged/config/document-types",             "Tipos doc"),
    ("/api/v1/ged/reports/monthly",                   "Relatório mensal"),
    ("/api/v1/ged/document-signatures/stats/summary", "Assinaturas"),
    (f"/api/v1/ged/kit-real/{KIT_ID}/checklist",      "Checklist"),
    ("/api/v1/ged/montar/condominios",                "Montar"),
]

resultados = []
for path, desc in ENDPOINTS_GED:
    status = ep(path)
    ok = status == "200"
    resultados.append((desc, path, status, ok))

pass_count = sum(1 for *_, ok in resultados if ok)

# Dados reais do banco
total_kits    = db("SELECT COUNT(*) FROM ged_document_kits")
total_clientes = db("SELECT COUNT(*) FROM ged_clients")
concluidos    = db("SELECT COUNT(*) FROM ged_document_kits WHERE status='concluido'")
em_montagem   = db("SELECT COUNT(*) FROM ged_document_kits WHERE status='em_montagem'")
total_docs    = db("SELECT COUNT(*) FROM ged_documents")
certidoes_v   = db("SELECT COUNT(*) FROM ged_certidoes WHERE expiry_date >= CURRENT_DATE")
certidoes_ex  = db("SELECT COUNT(*) FROM ged_certidoes WHERE expiry_date < CURRENT_DATE")

# Últimos commits que tocaram o GED
commits = run("git -C /opt/conecta-pro log --oneline -8 "
              "-- backend/modules/ged/ "
              "frontend/src/app/modulos/gestao-pessoas/ged/")

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

relatorio = f"""# RELATÓRIO E2E — MÓDULO GED
## Gerado em: {now}
## Container: {CONTAINER}
## Branch: feature/people-management-reorganization

---

## ENDPOINTS GED ({pass_count}/{len(ENDPOINTS_GED)} passando)

| Descrição | Endpoint | Status |
|-----------|----------|--------|
"""

for desc, path, status, ok in resultados:
    icon = "✅" if ok else "❌"
    relatorio += f"| {icon} {desc} | {path} | {status} |\n"

relatorio += f"""
---

## DADOS REAIS DO BANCO

| Métrica | Valor |
|---------|-------|
| Total de kits | {total_kits} |
| Kits concluídos | {concluidos} |
| Kits em montagem | {em_montagem} |
| Total de documentos | {total_docs} |
| Clientes GED | {total_clientes} |
| Certidões válidas | {certidoes_v} |
| Certidões vencidas | {certidoes_ex} |

---

## SCORECARD POR SUBMÓDULO

| Submódulo | URL | Score |
|-----------|-----|-------|
| Dashboard | /ged | /10 |
| Clientes/Condomínios | /ged/clientes | /10 |
| Kits Documentais | /ged/kits | /10 |
| Detalhes do Kit | /ged/kits/{{id}} | /10 |
| Documentos | /ged/documentos | /10 |
| Certidões | /ged/certidoes | /10 |
| Assinaturas | /ged/assinaturas | /10 |
| Envios | /ged/envios | /10 |
| Relatórios | /ged/relatorios | /10 |
| Configurações | /ged/configuracoes | /10 |
| **GERAL** | | **/10** |

---

## BUGS CORRIGIDOS NESTA SESSÃO

| # | Descrição | Arquivo | Status |
|---|-----------|---------|--------|
| B01 | | | ✅ |

---

## ALERTAS REAIS (não são bugs de sistema)

- 🔴 Alvará de Funcionamento (Segurança Privada) — vencido desde 28/02/2026
  → Renovar junto à SESEG / Polícia Federal
- 🟡 Google Drive — não configurado (OAuth pendente)
- 🟡 WebSocket /operacional/alertas — 503 aceitável (3x/30s)

---

## IDs DE REFERÊNCIA

- kit_id Ideal Flores: 2826deb4-722a-4d77-bc87-8af375240eef
- client_id Ideal Flores: 4db583b6-815a-494f-a1e3-0c62fa81eca9

---

## ÚLTIMOS COMMITS GED

```
{commits}
```

---

## ZONAS PROIBIDAS — nunca modificar
alembic/versions/ · main_production.py · docker-compose*.yml · .env* · credentials/

## HOT COPY GED (padrão)
```bash
GED_BACK="/opt/conecta-pro/backend/modules/ged"
docker cp $GED_BACK/controllers/ged_controller.py \\
  $CONTAINER:/app/modules/ged/controllers/ged_controller.py
docker restart $CONTAINER && sleep 8
```

## PRÓXIMOS PASSOS
- [ ] Completar testes E2E de todos os submódulos pendentes
- [ ] Integrar Google Drive OAuth
- [ ] Renovar Alvará PF (ação Jordan)
"""

output_path = "/opt/conecta-pro/RELATORIO_E2E_GED.md"
with open(output_path, "w") as f:
    f.write(relatorio)

print(f"✅ Relatório gerado: {output_path}")
print(f"   Endpoints: {pass_count}/{len(ENDPOINTS_GED)} OK")
print(f"   Kits: {total_kits} | Docs: {total_docs} | Certidões: {certidoes_v} válidas, {certidoes_ex} vencidas")
print(f"\nPara baixar no Mac:")
print(f"scp root@82.25.75.74:{output_path} ~/Desktop/")
PYEOF
```

## Documentar endpoints GED disponíveis

```bash
# Listar todos os endpoints /ged registrados no sistema
curl -sf "http://127.0.0.1:8080/openapi.json" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
paths = {k: v for k, v in d.get('paths', {}).items() if '/ged' in k}
print(f'Endpoints GED registrados: {len(paths)}')
for path, methods in sorted(paths.items()):
    for m in methods:
        if m in ['get','post','put','delete','patch']:
            summary = methods[m].get('summary', '')
            print(f'  {m.upper():6} {path}  ← {summary}')
" 2>/dev/null
```

## Scorecard de referência — GED

```
╔══════════════════════════════════════════════════════════╗
║   GED — GESTÃO ELETRÔNICA DE DOCUMENTOS                 ║
║   SCORECARD FINAL                                        ║
╠══════════════════════════════════════════════════════════╣
║ Submódulo              Score Inicial  Score Atual        ║
║ Dashboard GED          8/10           /10                ║
║ Clientes/Condomínios   7/10           /10                ║
║ Kits Documentais       2/10 → 9/10    /10                ║
║ Detalhes do Kit        9/10           /10                ║
║ Documentos/Busca       6/10           /10                ║
║ Certidões              9/10           /10                ║
║ Assinaturas            5/10           /10                ║
║ Envios/WhatsApp        7/10           /10                ║
║ Relatórios             0/10           /10                ║
║ Configurações          6/10           /10                ║
╠══════════════════════════════════════════════════════════╣
║ GERAL                  7/10           /10                ║
╠══════════════════════════════════════════════════════════╣
║ Endpoints: 11/11 passando ✅                             ║
║ Bugs corrigidos (histórico): 15+                        ║
║ Meta: 10/10 em todos os submódulos                      ║
╚══════════════════════════════════════════════════════════╝
```

## Contexto para novo chat

```
Cole no início do novo chat:

"Continuando auditoria E2E do módulo GED do Conecta PRO.
Arquivo de contexto atualizado em: /opt/conecta-pro/RELATORIO_E2E_GED.md
Branch: feature/people-management-reorganization
Score atual: [X]/10 — submódulos pendentes: [lista]
Próximo: [submódulo]"
```
