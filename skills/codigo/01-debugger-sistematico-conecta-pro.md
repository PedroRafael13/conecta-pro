---
name: debugger-sistematico-conecta-pro
description: Framework sistemático de debugging para o Conecta PRO — identifica causa raiz de bugs no FastAPI, PostgreSQL, Redis e Next.js antes de tentar qualquer correção. Usar SEMPRE que Jordan reportar um erro, bug ou comportamento inesperado.
---

# Debugger Sistemático — Conecta PRO

## Stack do sistema
- Backend: FastAPI + PostgreSQL + Redis + Celery · porta 8080
- Frontend: Next.js 16 + React 19 + TypeScript + Tailwind · porta 3001
- Container: Docker (conecta-pro-backend)
- PM2: conecta-pro-frontend
- VPS: srv1134814.hstgr.cloud (82.25.75.74)

## Regra de ouro
NUNCA corrigir sem reproduzir. NUNCA assumir onde está o bug sem testar.
A causa raiz raramente está onde parece.

## Quando usar
- Jordan reporta qualquer erro, bug ou comportamento inesperado
- Endpoint retorna status inesperado
- Frontend mostra dados errados ou zerados
- Modal não abre, botão não funciona
- Qualquer comportamento diferente do esperado

## Protocolo obrigatório

```
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)

# PASSO 1 — REPRODUZIR via curl ANTES de qualquer coisa
curl -sf -X [METHOD] "http://127.0.0.1:8080/api/v1/[ENDPOINT]" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool

# PASSO 2 — VER LOG REAL DO ERRO
docker logs $CONTAINER --tail 30 2>/dev/null \
  | grep -i "error\|exception\|traceback\|500" | head -20

# PASSO 3 — VERIFICAR O BANCO SE FOR DADO ERRADO
docker exec $CONTAINER psql -U postgres -d conectapro -c \
  "SELECT [campos relevantes] FROM [tabela] WHERE [condição] LIMIT 5;"

# PASSO 4 — HIPÓTESES (top 3, mais provável primeiro)
# H1: [hipótese mais provável] → testar em 2 min
# H2: [segunda hipótese] → testar se H1 falhar
# H3: [terceira hipótese] → testar se H2 falhar

# PASSO 5 — CORRIGIR a causa raiz (nunca o sintoma)
# Hot copy backend:
docker cp /opt/conecta-pro/backend/[arquivo] \
  $CONTAINER:/app/[arquivo]
docker restart $CONTAINER && sleep 8

# PASSO 6 — VALIDAR com curl
curl -sf -X [METHOD] "http://127.0.0.1:8080/api/v1/[ENDPOINT]" \
  -H "Authorization: Bearer $TOKEN"
echo "HTTP Status: $?"
```

## Árvore de decisão por tipo de bug

### Bug: endpoint retorna 404
1. Verificar se a rota está registrada no main_production.py
2. Verificar se o prefix do router está correto
3. Verificar se há trailing slash problem (redirect_slashes=False)

### Bug: endpoint retorna 500
1. Ver o log do container: `docker logs $CONTAINER --tail 20`
2. Identificar o Traceback completo
3. Verificar se é problema de coluna/tabela no banco
4. Verificar se é import faltando

### Bug: dados zerados no frontend (R$ 0,00, listas vazias)
1. Testar o endpoint diretamente via curl — dados chegam do backend?
2. Se sim → problema no frontend (parsing, campo errado, useEffect)
3. Se não → problema no backend (query retorna vazio, campo errado)

### Bug: formulário não submete / modal não abre
1. Abrir DevTools → Console → ver erros JavaScript
2. Abrir DevTools → Network → ver se o request foi feito
3. Se request não foi feito → problema no handler do frontend
4. Se request foi feito mas falhou → problema no backend

### Bug: autenticação 401
1. Verificar se o token está sendo enviado no header
2. Verificar se o token não expirou
3. Verificar se o endpoint requer autenticação diferente

## Zonas proibidas — nunca modificar
`alembic/versions/` · `main_production.py` · `docker-compose*.yml` · `.env*` · `credentials/`

## Relatório final obrigatório
```
ANTES: [comportamento com bug]
CAUSA RAIZ: [o que causou]
FIX: [o que foi alterado]
DEPOIS: [comportamento correto confirmado via curl]
```
