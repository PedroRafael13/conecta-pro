---
name: code-review-conecta-pro
description: Checklist estruturado de code review para fechar módulos do Conecta PRO com qualidade real. Usar antes de declarar qualquer módulo como 10/10. Avalia funcionalidade, segurança, performance, error handling e frontend.
---

# Code Review Estruturado — Conecta PRO

## Quando usar
- Antes de declarar qualquer módulo como 10/10
- Após implementar um fix para validar que não quebrou nada
- Ao revisar endpoints novos ou modificados
- Antes de fazer git commit no final de uma sessão

## Protocolo de review

```
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)
```

## Checklist completo (15 pontos)

### 1. FUNCIONALIDADE (obrigatório — 5 pontos)
```bash
# Testar TODOS os endpoints do módulo
curl -sf "http://127.0.0.1:8080/api/v1/[endpoint]" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Verificar dados REAIS (não zeros, não mocks)
# [ ] Todos os endpoints retornam HTTP 200
# [ ] Dados são reais do banco (não R$ 0,00, não listas vazias)
# [ ] UUID inválido retorna 404 (não 500)
# [ ] Lista vazia retorna [] (não null)
# [ ] Campos obrigatórios faltando retorna 422
```

### 2. SEGURANÇA (obrigatório — 3 pontos)
```bash
# Testar sem token — deve retornar 401
curl -sf -o /dev/null -w "%{http_code}" \
  "http://127.0.0.1:8080/api/v1/[endpoint]"

# Testar com token inválido — deve retornar 401
curl -sf -o /dev/null -w "%{http_code}" \
  "http://127.0.0.1:8080/api/v1/[endpoint]" \
  -H "Authorization: Bearer token_invalido"

# [ ] Endpoint sem token → 401 (nunca 200)
# [ ] Endpoint com token inválido → 401
# [ ] Nenhuma query usa f-string com input do usuário
```

### 3. PERFORMANCE (obrigatório — 3 pontos)
```bash
# Verificar queries lentas
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC LIMIT 10;" 2>/dev/null

# [ ] Nenhuma query demora mais de 200ms
# [ ] Listas com muitos itens têm limit/paginação
# [ ] Sem N+1 queries (verificar no log do banco)
```

### 4. ERROR HANDLING (obrigatório — 2 pontos)
```bash
# Verificar se erros têm mensagem clara
curl -sf "http://127.0.0.1:8080/api/v1/[endpoint]/uuid-invalido" \
  -H "Authorization: Bearer $TOKEN"

# [ ] 404 com mensagem clara em português
# [ ] 500 nunca vaza stack trace para o cliente
```

### 5. FRONTEND (obrigatório — 2 pontos)
```bash
# Verificar no browser: DevTools Console
# [ ] Zero erros vermelhos no console
# [ ] Zero chamadas a /people-management/ged/* (namespace antigo)
# [ ] Dados reais renderizando na tela
# [ ] Formulários validam antes de submeter
```

## Scoring
```
15/15 → 10/10 ✅ Módulo fechado
13-14/15 → 9/10 🟡 Quase lá — corrigir pendências
10-12/15 → 7/10 🟠 Necessita trabalho
< 10/15  → < 7  🔴 Não fechar — bugs críticos presentes
```

## Bugs recorrentes no Conecta PRO — verificar sempre

```python
# BUG 1: status 'paga' vs 'pago' — verificar enum no banco
docker exec $CONTAINER psql -U postgres -d conectapro -c \
  "SELECT DISTINCT status FROM receivable_accounts LIMIT 10;"

# BUG 2: trailing slash — endpoints sem barra final
# CORRETO: router = APIRouter(prefix="/modulo")
# ERRADO:  router = APIRouter(prefix="/modulo/")

# BUG 3: rota /{id} antes de /search — FastAPI captura 'search' como UUID
# CORRETO: /documents/search ANTES de /documents/{id}
# ERRADO:  /documents/{id} ANTES de /documents/search

# BUG 4: useEffect sem dependência correta no frontend
# Dropdown vazio = useEffect não dispara ao abrir modal
# CORRETO: useEffect(() => { fetch() }, [isOpen])
# ERRADO:  useEffect(() => { fetch() }, [])
```

## Relatório de review obrigatório
```
MÓDULO REVISADO: [nome]
PONTUAÇÃO: [X]/15
ITENS APROVADOS: [lista]
ITENS REPROVADOS: [lista com fix necessário]
DECLARAÇÃO: [10/10 aprovado / reprovado — corrigir X]
```
