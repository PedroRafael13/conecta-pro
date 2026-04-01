---
name: design-api-restful-conecta-pro
description: Auditoria e padrões de design de API para os 200+ endpoints do Conecta PRO. Usar para auditar endpoints existentes, criar novos endpoints corretos, e garantir consistência em toda a API do sistema.
---

# Design de API RESTful — Conecta PRO

## Contexto da API
- Base URL: `https://erp.conectamais.pro/api/v1`
- Auth: JWT Bearer token
- 200+ endpoints distribuídos em 33 módulos
- Stack: FastAPI + PostgreSQL
- Padrão de resposta: JSON

## Quando usar
- Ao criar novos endpoints
- Ao auditar endpoints que retornam dados incorretos
- Quando frontend não consegue consumir o endpoint
- Ao padronizar respostas entre módulos

## Padrões obrigatórios do Conecta PRO

### Nomenclatura de rotas
```
✅ CORRETO:
GET    /api/v1/ged/kits              → listar kits
GET    /api/v1/ged/kits/{id}         → detalhe do kit
POST   /api/v1/ged/kits              → criar kit
PUT    /api/v1/ged/kits/{id}         → atualizar kit
DELETE /api/v1/ged/kits/{id}         → remover kit

❌ ERRADO:
GET /api/v1/ged/getKits              → verbo no path
GET /api/v1/ged/kits/                → trailing slash
GET /api/v1/peopleManagement/ged     → camelCase no path
GET /api/v1/ged/{id}/kits            → id antes do recurso filho
```

### Padrão de resposta — lista
```python
# FastAPI — retorno de lista com paginação
@router.get("/kits")
async def listar_kits(
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    offset = (page - 1) * per_page
    total = await db.scalar(select(func.count(Kit.id)))
    items = await db.execute(
        select(Kit).offset(offset).limit(per_page)
    )
    return {
        "data": items.scalars().all(),
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": ceil(total / per_page)
        }
    }
```

### Padrão de resposta — erro
```python
# SEMPRE retornar erro estruturado — nunca string pura
# 404 — recurso não encontrado
raise HTTPException(
    status_code=404,
    detail={
        "code": "KIT_NOT_FOUND",
        "message": f"Kit com ID '{kit_id}' não encontrado."
    }
)

# 422 — validação falhou
raise HTTPException(
    status_code=422,
    detail={
        "code": "VALIDATION_ERROR",
        "message": "Dados inválidos.",
        "fields": {"client_id": "Cliente obrigatório"}
    }
)

# 500 — nunca vazar stack trace
# FastAPI com exception_handler no main_production.py
```

### Padrão de router no FastAPI
```python
# CORRETO — sem trailing slash no prefix
router = APIRouter(
    prefix="/ged/kits",
    tags=["GED — Kits Documentais"]
)

# CORRETO — registrar no main_production.py
api_router.include_router(
    kits_router,
    prefix="/api/v1",
    tags=["GED"]
)

# ERRADO — causa 307 redirect silencioso
router = APIRouter(prefix="/ged/kits/")
```

## Auditoria de endpoints existentes

```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Listar TODOS os endpoints registrados
curl -sf "http://127.0.0.1:8080/openapi.json" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
paths = d.get('paths', {})
print(f'Total de endpoints: {len(paths)}')
for path, methods in sorted(paths.items()):
    for m in methods:
        if m in ['get','post','put','delete','patch']:
            print(f'  {m.upper()} {path}')
" 2>/dev/null

# Verificar endpoints que retornam erro
curl -sf "http://127.0.0.1:8080/openapi.json" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys, json, subprocess
d = json.load(sys.stdin)
erros = []
for path, methods in d.get('paths', {}).items():
    if 'get' in methods:
        r = subprocess.run([
            'curl', '-sf', '-o', '/dev/null',
            '-w', '%{http_code}',
            f'http://127.0.0.1:8080{path}',
            '-H', 'Authorization: Bearer \$TOKEN'
        ], capture_output=True, text=True)
        if r.stdout not in ['200', '401']:
            erros.append(f'{r.stdout} → GET {path}')
for e in erros:
    print(f'  ❌ {e}')
print(f'Endpoints com problema: {len(erros)}')
" 2>/dev/null
```

## Checklist de novo endpoint

Antes de criar qualquer endpoint novo:
```
[ ] Path em snake_case e plural: /api/v1/[modulo]/[recursos]
[ ] Método HTTP correto: GET=listar/ler, POST=criar, PUT=atualizar, DELETE=remover
[ ] Requer autenticação: Depends(get_current_user)
[ ] Sem trailing slash no prefix do router
[ ] Rota /search ANTES de /{id} se ambas existem
[ ] Retorna estrutura consistente: {data: ..., meta: ...} para listas
[ ] Erros em formato: {code: "...", message: "..."}
[ ] Registrado no main_production.py com try/except
[ ] Testado via curl após hot copy
[ ] Commitado com mensagem descritiva
```

## Módulos e prefixos padronizados

```
/api/v1/ged/           → GED — Gestão Eletrônica de Documentos
/api/v1/financial/     → Financeiro
/api/v1/hr/            → Recursos Humanos / CCT
/api/v1/operacional/   → Operações
/api/v1/government/    → Integrações Governamentais
/api/v1/ai/            → Bartolo AI / Intelligence Hub
/api/v1/auth/          → Autenticação
/api/v1/people-management/ → Gestão de Pessoas (legado — migrar para módulos específicos)
```
