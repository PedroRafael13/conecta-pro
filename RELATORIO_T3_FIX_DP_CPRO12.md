# T3 Fix DP CPRO12 — Endpoints HR Online
**Data:** 2026-05-05
**Terminal:** T3
**Branch:** feature/people-management-reorganization

---

## operacional.ai no container

| Estado | Situação |
|--------|----------|
| **Antes** | Ausente — `ModuleNotFoundError: No module named 'modules.operacional.ai'` |
| **Depois** | Presente — `__init__.py`, `controller.py`, `stubs.py` |

**Conteúdo do módulo (INV-1 lido antes de copiar):**
- `stubs.py` — 23 dataclasses de compatibilidade (AbsencePrediction, CoveragePredictorAgent, etc.)
- `controller.py` — router vazio (`APIRouter(prefix="/ai")`) — sem lógica de negócio
- `__init__.py` — exporta stubs + ai_router

**Comando executado:**
```bash
docker exec conecta-pro-backend find /app/modules/operacional/ -name "*.pyc" -path "*ai*" -delete
docker cp backend/modules/operacional/ai/ conecta-pro-backend:/app/modules/operacional/ai/
docker exec conecta-pro-backend kill -9 1  # SIGKILL → uvicorn recarregou automaticamente
```

**Log confirmando restart:**
```
2026-05-05 15:50:40 INFO — Modulo Operacoes: OK (Operacional + Campo)
```

---

## INV-7 — 6 Endpoints HR testados após fix

| Endpoint | HTTP | Resultado |
|----------|------|-----------|
| `GET /api/v1/people-management/hr/employees/cpf/03527554238` | **200** ✅ | ADAILSON SERRA ALVES encontrado |
| `GET /api/v1/people-management/hr/employees` | **200** ✅ | lista paginada de funcionários |
| `GET /api/v1/people-management/hr/employees/search?q=GRACIENE` | **200** ✅ | GRACIENE SILVA MAIA encontrada |
| `GET /api/v1/people-management/hr/employees/{id}` | **200** ✅ | dados completos do funcionário |
| `GET /api/v1/operacional/allocations/` | **200** ✅ | lista de alocações |
| `GET /api/v1/operacional/allocations/employee/{id}` | **200** ✅ | alocações de ADAILSON |

**Observação:** `GET /operacional/allocations` (sem trailing slash) → 404 (comportamento padrão FastAPI para routers com path `"/"`).

---

## Endpoint GEDEON — INV-4 e INV-9

`GET /api/v1/people-management/hr/employees/cpf/{cpf}` retornou **200** → **endpoint extra NÃO criado** (INV-9).

Para obter `condominio_nome`, GEDEON deve encadear:
1. `GET /people-management/hr/employees/cpf/{cpf}` → obtém `employee_id`
2. `GET /operacional/allocations/employee/{employee_id}` → obtém `post_id` da alocação ativa
3. Query SQL: `SELECT c.nome FROM condominios c JOIN posts p ON p.condominio_id = c.id WHERE p.id = :post_id`

Ou diretamente via SQL (mais eficiente):
```sql
SELECT e.nome, c.nome as condominio, ea.funcao
FROM employee_alocacoes ea
JOIN employees e ON e.id = ea.employee_id
JOIN condominios c ON c.id = ea.condominio_id
WHERE ea.ativo = true AND e.cpf = :cpf
```

---

## Commits

| Hash | Mensagem |
|------|----------|
| `706f9bc7` | `docs(contracts): §92+§94 — commitado em conjunto com T4 (CPRO12 T3+T4)` |
| ver abaixo | `chore(deploy): operacional.ai hot-copy → backend container (§92)` |
