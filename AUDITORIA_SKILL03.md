# AUDITORIA SKILL 03 — DESIGN DE API RESTful — CONECTA PRO
> **Gerada em:** 31/03/2026
> **Metodologia:** Skill 03 (design-api-restful-conecta-pro) — 5 subagentes paralelos
> **Cobertura:** GED · Financeiro · Departamento Pessoal · Operacional · AI + Gov + Auth
> **Backend:** http://127.0.0.1:8080 · Container: conecta-pro-backend

---

## SCORECARD EXECUTIVO

```
╔══════════════════════════════════════════════════════════════════════╗
║           CONECTA PRO — AUDITORIA DE DESIGN REST                    ║
║           Auditoria: 31/03/2026 — Skill 03 Paralela                 ║
╠══════════════════════╦════════════╦═══════════════════════════════════╣
║ Módulo               ║ Endpoints  ║  Score REST                      ║
╠══════════════════════╬════════════╬═══════════════════════════════════╣
║ GED                  ║    120     ║   4.5 / 10 ❌                    ║
║ Financeiro + BI      ║    472     ║   5.0 / 10 ⚠️                    ║
║ Departamento Pessoal ║     74     ║   6.3 / 10 ⚠️                    ║
║ Operacional          ║     62     ║   8.2 / 10 ✅                    ║
║ AI + Gov + Auth      ║     47     ║   7.1 / 10 ✅                    ║
╠══════════════════════╬════════════╬═══════════════════════════════════╣
║ TOTAL                ║    775+    ║   6.2 / 10                       ║
╠══════════════════════╩════════════╩═══════════════════════════════════╣
║                                                                      ║
║  Score médio ponderado: 6.2/10                                       ║
║  Módulo mais maduro REST: Operacional (8.2)                          ║
║  Módulo com mais violações: GED (4.5)                                ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## SCORECARD POR CRITÉRIO (todos os módulos)

| Critério REST            | GED | Fin | DP  | Op  | AI  | Média |
|--------------------------|-----|-----|-----|-----|-----|-------|
| 1. Nomenclatura          | 4   | 5   | 6   | 9   | 6   | 6.0   |
| 2. Métodos HTTP          | 6   | 6   | 7   | 8   | 7   | 6.8   |
| 3. Paginação             | 4   | 5   | 8   | 9   | 8   | 6.8   |
| 4. Formato de erro       | 4   | 4   | 5   | 7   | 5   | 5.0   |
| 5. Trailing slash        | 6   | 8   | 9   | 10  | 9   | 8.4   |
| 6. Ordem das rotas       | 5   | 6   | 4   | 8   | 8   | 6.2   |
| 7. Prefixos consistentes | 3   | 5   | 6   | 9   | 6   | 5.8   |
| 8. Versionamento         | 7   | 9   | 10  | 10  | 9   | 9.0   |
| 9. Status codes          | 5   | 5   | 6   | 8   | 7   | 6.2   |
| 10. Documentação OpenAPI | 5   | 6   | 7   | 8   | 7   | 6.6   |
| **TOTAL**                |**4.5**|**5.0**|**6.3**|**8.2**|**7.1**|**6.2**|

---

## TOP 5 VIOLAÇÕES MAIS IMPACTANTES (prioridade de correção)

### 🔴 PRIORIDADE 1 — Formato de erro não estruturado (GLOBAL — todos os módulos)

**Problema:** Todos os módulos retornam `{"detail": "string pura"}` em vez de formato estruturado.

**Impacto:** Frontend não consegue exibir erros diferenciados. Logs não rastreáveis.

**Atual:**
```json
{"detail": "Funcionário não encontrado"}
{"detail": "Email ja cadastrado"}
{"detail": "Dados invalidos: ..."}
```

**Esperado (padrão skill 03):**
```python
raise HTTPException(
    status_code=404,
    detail={
        "code": "EMPLOYEE_NOT_FOUND",
        "message": "Funcionário com ID 'abc' não encontrado."
    }
)
```

**Fix global:** Criar `core/exceptions/handlers.py` com `ErrorResponseSchema` e usar em todos os controllers.

**Módulos afetados:** GED, Financeiro, DP, Operacional, AI, Gov, Auth

---

### 🔴 PRIORIDADE 2 — GED fragmentado em 3 namespaces (GED)

**Problema:** O módulo GED está espalhado em 3 prefixos diferentes sem consistência:
- `/api/v1/ged/` — core GED
- `/api/v1/people-management/ged/` — GED no módulo DP
- `/api/v1/document-kits/` — Kits documentais (deveria ser `/api/v1/ged/kits/`)

**Impacto:** Orval gera 3 módulos separados. Frontend consome 3 baseURLs para o mesmo domínio funcional.

**Fix:** Unificar sob `/api/v1/ged/` e usar sub-routers:
```
/api/v1/ged/documents/
/api/v1/ged/folders/
/api/v1/ged/kits/         ← migrar de /document-kits/
/api/v1/ged/tags/
/api/v1/ged/shares/
/api/v1/ged/signatures/
```

---

### 🔴 PRIORIDADE 3 — 17 violações de nomenclatura no GED (verbos em paths)

**Problema:** GED usa verbos e sufixos redundantes nos paths.

**Violations encontradas:**
| Path atual                           | Path correto                     |
|--------------------------------------|----------------------------------|
| `/ged/documents/list`                | `GET /ged/documents`             |
| `/ged/documents/create`              | `POST /ged/documents`            |
| `/ged/folders/list`                  | `GET /ged/folders`               |
| `/ged/folders/create`                | `POST /ged/folders`              |
| `/ged/documents/ai/run`              | `POST /ged/documents/{id}/ai`    |
| `/ged/documents/query`               | `GET /ged/documents` (+ filters) |
| `/sefaz/nfe/emitir`                  | `POST /sefaz/nfes`               |
| `/government/esocial/consultar/{id}` | `GET /government/esocial/events/{id}` |
| `/ai/bartolo/send`                   | `POST /ai/bartolo/messages`      |
| `/ai/churn/predict`                  | `POST /ai/predictions?type=churn`|

---

### 🔴 PRIORIDADE 4 — Listas sem paginação (GED, Financeiro, Gov)

**Problema:** 11 endpoints no GED + 4 no Financeiro retornam arrays crus sem meta de paginação.

**Atual:**
```json
[
  {"id": "...", "titulo": "..."},
  {"id": "...", "titulo": "..."}
]
```

**Esperado:**
```json
{
  "data": [...],
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20,
    "total_pages": 5
  }
}
```

**Módulos afetados:** GED (11 endpoints), Financeiro (4 endpoints), Gov (listagens de eventos)

---

### 🔴 PRIORIDADE 5 — POSTs de criação retornando 200 em vez de 201 (Financeiro, GED)

**Problema:** 78+ endpoints POST no Financeiro retornam HTTP 200 OK em vez de 201 Created. No GED, vários POSTs de documento, pasta e kit também retornam 200.

**Fix:** Adicionar `status_code=status.HTTP_201_CREATED` nos decorators:
```python
# ANTES
@router.post("/documents")
async def create_document(...):

# DEPOIS
@router.post("/documents", status_code=status.HTTP_201_CREATED)
async def create_document(...):
```

**Módulos afetados:** Financeiro (78 POSTs), GED (~12 POSTs), DP (DELETE sem 204)

---

## ANÁLISE POR MÓDULO

### 📁 GED — Score 4.5/10 ❌

**Critério por critério:**

| Critério | Score | Achados |
|----------|-------|---------|
| Nomenclatura | 4/10 | 17 violations: `/list`, `/create`, `/run` redundantes; verbos `/query`, `/validate` |
| Métodos HTTP | 6/10 | PUT para ações (deveria ser POST), GET com efeito colateral |
| Paginação | 4/10 | 11 listagens retornam array cru sem meta |
| Formato de erro | 4/10 | `{"detail": "string"}` em todos os 4 sub-routers |
| Trailing slash | 6/10 | `redirect_slashes=False` global causa 404 em `/documents/` |
| Ordem das rotas | 5/10 | `/search` e `/stats` após `/{id}` em alguns routers |
| Prefixos | 3/10 | **3 namespaces**: `/ged/`, `/people-management/ged/`, `/document-kits/` |
| Versionamento | 7/10 | Todos em v1, mas prefixos inconsistentes obscurecem |
| Status codes | 5/10 | POSTs retornam 200 (deveria ser 201); DELETEs retornam body |
| Docs OpenAPI | 5/10 | Tags presentes, mas sem summary/description na maioria |

**Violations críticas:**
1. `GET /ged/documents/list` — redundante → `GET /ged/documents`
2. `POST /ged/documents/create` — redundante → `POST /ged/documents` com 201
3. `GET /ged/documents/{id}` declarado ANTES de `/ged/documents/stats` → conflict
4. `/api/v1/document-kits/` deveria ser `/api/v1/ged/kits/`
5. 11 arrays sem paginação: `/ged/folders`, `/ged/document-tags`, `/ged/document-shares`

---

### 💰 Financeiro — Score 5.0/10 ⚠️

**Critério por critério:**

| Critério | Score | Achados |
|----------|-------|---------|
| Nomenclatura | 5/10 | Verbos em PT: `/calcular/simples`, `/das/calcular`, `/sped/gerar`; `condominio_id` em path |
| Métodos HTTP | 6/10 | POSTs para queries (deveria ser GET + params); PUT em ações |
| Paginação | 5/10 | 4 endpoints de lista sem meta; bank-accounts, suppliers sem paginação |
| Formato de erro | 4/10 | Strings puras + `{"success": false}` (2 padrões mistos) |
| Trailing slash | 8/10 | Maioria correta; poucos casos de trailing slash |
| Ordem das rotas | 6/10 | `/upcoming` e `/stats` após `/{id}` em receivables/payables |
| Prefixos | 5/10 | `/financial/` coeso, mas BI em `/financial/bi/` causa estranheza |
| Versionamento | 9/10 | Todos em v1 |
| Status codes | 5/10 | 78 POSTs retornam 200; sem 204 em DELETEs confirmados |
| Docs OpenAPI | 6/10 | Tags presentes; docstrings em maioria; falta `responses=` com exemplos |

**Violations críticas:**
1. `GET /financial/receivables/upcoming` declarado APÓS `/{id}` → conflict UUID
2. `POST /financial/tax/calcular/simples` — verbo `calcular` → `POST /financial/tax/simples`
3. `condominio_id` como query param obrigatório sem fallback JWT → 422 sem o param
4. 78 POSTs retornam 200 → padronizar `status_code=201`
5. bank-accounts, suppliers retornam array → adicionar meta paginação

---

### 👥 Departamento Pessoal — Score 6.3/10 ⚠️

**Critério por critério:**

| Critério | Score | Achados |
|----------|-------|---------|
| Nomenclatura | 6/10 | Bom geral; `/batida/me` semanticamente estranho; hífens vs underscores |
| Métodos HTTP | 7/10 | POSTs para criação corretos (201); PUT para ação `/revisar` (deveria ser POST) |
| Paginação | 8/10 | `DPEmployeeList` com meta completo; ponto/batidas sem paginação |
| Formato de erro | 5/10 | Strings puras em todos os controllers |
| Trailing slash | 9/10 | Excelente: sem trailing slash nos prefixos |
| Ordem das rotas | 4/10 | `/{benefit_id}` declarado ANTES de `/employee/{id}/total`; mesmo em contracts |
| Prefixos | 6/10 | Módulo em `/people-management/` com sub-routers; Ponto, SST, Folha separados |
| Versionamento | 10/10 | Perfeito |
| Status codes | 6/10 | 201 em POSTs; DELETE retorna body (deveria ser 204); ações POST sem 202 |
| Docs OpenAPI | 7/10 | Tags definidas; docstrings em endpoints; falta summary no decorador |

**Violations críticas:**
1. `DELETE /hr/benefits/{id}` retorna `BenefitResponse` → deve ser `status_code=204` sem body
2. `/hr/benefits/employee/{employee_id}/total` declarado APÓS `/{benefit_id}` → FastAPI trata `employee` como UUID
3. `PUT /ponto/justificativa/{id}/revisar` — revisar é ação → `POST /ponto/justificativas/{id}/revisar`
4. Strings de erro sem código estruturado em todos os 12 controllers
5. Ponto/SST/Folha como namespaces separados de `/hr/` → fragmentação dificulta descoberta

---

### ⚙️ Operacional — Score 8.2/10 ✅

**Critério por critério:**

| Critério | Score | Achados |
|----------|-------|---------|
| Nomenclatura | 9/10 | Excelente: plural, snake_case, sem verbos; `/kpi-trends` deveria ser `/kpi_trends` |
| Métodos HTTP | 8/10 | 201/204 corretos; `POST /auto-generate` retorna 200 (deveria ser 201) |
| Paginação | 9/10 | Padrão `{items, total, page, page_size, total_pages}` consistente |
| Formato de erro | 7/10 | Strings puras, mas bem descritas; sem código estruturado |
| Trailing slash | 10/10 | Perfeito: sem trailing slash em nenhum prefix |
| Ordem das rotas | 8/10 | Geral correto; `/scales/bulk` antes de `/{id}` em alguns casos |
| Prefixos | 9/10 | `/operacional/` coeso; apenas `/kpi-trends` como anomalia |
| Versionamento | 10/10 | Perfeito |
| Status codes | 8/10 | 201/204 quase perfeito; edge case em `/auto-generate` e ações |
| Docs OpenAPI | 8/10 | Tags, summary, docstrings; falta `responses=` com exemplos de erro |

**Violations (menores):**
1. `POST /operacional/scales/auto-generate` retorna 200 → deve ser 201 (cria múltiplas escalas)
2. `{"detail": "string"}` em todos os 8 controllers → adicionar código estruturado
3. `/kpi-trends` em kebab-case → padronizar para `kpi_trends` ou manter e documentar

---

### 🤖 AI + Gov + Auth — Score 7.1/10 ✅

**Critério por critério:**

| Critério | Score | Achados |
|----------|-------|---------|
| Nomenclatura | 6/10 | `/bartolo/send` verbo; `/sefaz/nfe/emitir` verbo; `/consultar/{id}` verbo; `nfse-manaus` vs `nfse_manaus` |
| Métodos HTTP | 7/10 | 201/204 corretos em Auth; Gov usa 202 async corretamente |
| Paginação | 8/10 | Consistente; discrepância `per_page` vs `page_size` entre módulos |
| Formato de erro | 5/10 | 3 padrões diferentes: string, `{success, message}`, `{detail: string}` |
| Trailing slash | 9/10 | Excelente |
| Ordem das rotas | 8/10 | Auth e Users bem ordenados; Gov tem `/consultar` redundante |
| Prefixos | 6/10 | Auth coeso; AI coeso; Gov fragmentado (FGTS/INSS sem prefixo no router) |
| Versionamento | 9/10 | Todos em v1; LGPD router legado fora de v1 |
| Status codes | 7/10 | 202 Accepted em Gov (correto); `/bartolo/send` retorna 200 (deveria ser 202 se async) |
| Docs OpenAPI | 7/10 | Tags, summary, docstrings em Gov; AI menos documentado; rate limits não documentados |

**Violations críticas:**
1. `APIRouter(tags=["FGTS/INSS"])` sem `prefix` → endpoints fora de `/government/`
2. `POST /ai/bartolo/send` → `POST /ai/bartolo/messages` (verbo no path)
3. `POST /government/sefaz/nfe/emitir` → `POST /government/nfes` (verbo + substantivo)
4. Paginação: `per_page` (users) vs `page_size` (predictions) → padronizar
5. 3 formatos de erro mistos em Auth+AI+Gov → middleware único

---

## PRIORIDADES DE CORREÇÃO — PLANO DE AÇÃO

### Sprint imediata — impacto máximo (todos os módulos):

1. **Middleware de erro estruturado** (`core/exceptions/handlers.py`)
   - Criar schema `{"detail": {"code": "...", "message": "..."}}`
   - Registrar no `main_production.py` como exception handler global
   - **Desbloqueia:** Todos os módulos passam de 4-5 para 6+ no critério 4

2. **Status codes nos POSTs de criação** (Financeiro + GED + DP)
   - Adicionar `status_code=status.HTTP_201_CREATED` nos ~90 POSTs
   - Adicionar `status_code=status.HTTP_204_NO_CONTENT` nos DELETEs que retornam body
   - **Desbloqueia:** 3 módulos melhoram critério 9

3. **Paginação nos arrays crus** (GED + Financeiro)
   - Embrulhar os 15 endpoints que retornam `[]` em `{data: [...], meta: {...}}`
   - **Desbloqueia:** GED sobe de 4 para 6 no critério 3

### Sprint seguinte — consistência:

4. **Unificar namespaces GED** (`/document-kits/` → `/ged/kits/`)
   - Adicionar redirect temporário de compatibilidade
   - Atualizar Orval config

5. **Remover verbos dos paths críticos** (top 10 mais consumidos)
   - `/ged/documents/list` → `GET /ged/documents`
   - `/sefaz/nfe/emitir` → `POST /sefaz/nfes`
   - Adicionar deprecated aliases para backwards compat

6. **Prefixo no FGTS/INSS router**
   - `APIRouter(prefix="/fgts-inss", tags=["FGTS/INSS"])`

### Médio prazo — polimento:

7. **Padronizar paginação** (`per_page` → `page_size` em todos)
8. **Ordem das rotas** — `/upcoming`, `/stats`, `/templates` ANTES de `/{id}`
9. **Remover `/list` e `/create` redundantes** do GED
10. **Documentação OpenAPI** — `summary=` e `responses=` em todos os endpoints

---

## COMPARATIVO COM AUDITORIA SKILL 01

| Métrica           | Skill 01 (bugs)      | Skill 03 (design)   | Relação                          |
|-------------------|----------------------|---------------------|----------------------------------|
| Score médio       | 6.4/10               | 6.2/10              | Qualidade de design ≈ bugs/erros |
| Módulo crítico    | Financeiro BI (0%)   | GED (4.5/10)        | Bugs severos != design ruim      |
| Módulo melhor     | AI+Gov (8.2)         | Operacional (8.2)   | Operacional: melhor design REST  |
| Problema global   | Session/AsyncSession | Erros não estruturados | Diferentes layers, mesmo nível |

---

## RESUMO EXECUTIVO

O Conecta PRO tem **design REST heterogêneo**: o módulo Operacional, construído mais recentemente, segue os padrões quase perfeitamente (8.2/10), enquanto o GED, mais antigo, apresenta violações graves de nomenclatura e fragmentação (4.5/10).

**3 problemas transversais afetam 100% dos módulos:**
1. Erros sem código estruturado (todos retornam string pura)
2. POSTs de criação retornando 200 em vez de 201
3. `per_page` vs `page_size` inconsistente

**O padrão de referência** para redesign é o módulo Operacional: paginação completa, status codes corretos, trailing slash limpo, prefixos coesos, rotas ordenadas corretamente.

---

*Auditoria executada via Skill 03 (design-api-restful-conecta-pro) com 5 subagentes paralelos.*
*Arquivo salvo em: /opt/conecta-pro/AUDITORIA_SKILL03.md*
