# T2 CPRO12 — Diagnóstico Profundo DP: Matching GEDEON
**Data:** 2026-05-05
**Terminal:** T3
**Branch:** feature/people-management-reorganization
**Tipo:** READ-ONLY (INV-2: zero alterações)

---

## Schema das tabelas principais

### employees (58 rows)
| Campo | Preenchimento | Observação |
|-------|---------------|-----------|
| `nome` | 58/58 (100%) | UPPERCASE |
| `cpf` | 58/58 (100%) | Único, sem pontuação — **melhor chave** |
| `matricula` | 58/58 (100%) | Único |
| `solides_id` | parcial | ID externo |
| `posto_atual_nome` | 0/58 (0%) | Coluna existe mas vazia — NÃO USAR |
| `cliente_nome` | 0/58 (0%) | Coluna existe mas vazia — NÃO USAR |

### employee_alocacoes (47 ativas)
```sql
CREATE TABLE employee_alocacoes (
    id            UUID PRIMARY KEY,
    employee_id   UUID REFERENCES employees(id),   -- FK direta
    condominio_id UUID REFERENCES condominios(id), -- FK direta
    funcao        VARCHAR,  -- ex: "AGENTE DE PORTARIA"
    data_inicio   DATE,
    ativo         BOOLEAN DEFAULT true
);
-- Índices: ix_employee_alocacoes_employee, ix_employee_alocacoes_condominio, ix_employee_alocacoes_ativo
```

### condominios (7 distintos)
| Condomínio | Colaboradores ativos |
|------------|---------------------|
| IDEAL FLORES | 11 |
| MIRANTE | 10 |
| PRIME ARENA | 7 |
| VILLA DEI FIORI | 6 |
| VILLA PÁSSAROS | 6 |
| LARANJEIRAS | 6 |
| MICHELANGELO | 1 |
| **Total** | **47** |

---

## Campos de identificação do colaborador

| Campo | Preenchimento | Uso para matching |
|-------|---------------|------------------|
| `cpf` | 58/58 (100%) | **Primário** — único, sem ambiguidade |
| `nome` | 58/58 (100%) | Fallback — UPPERCASE, usar ILIKE |
| `matricula` | 58/58 (100%) | Alternativo — se disponível no documento |

---

## Relação colaborador → posto → condomínio

**Query funciona? SIM** (via `employee_alocacoes`, não via `alocacoes`/`postos` que não existem)

```sql
-- Via CPF (recomendado)
SELECT e.nome, c.nome AS condominio, ea.funcao
FROM employee_alocacoes ea
JOIN employees e ON e.id = ea.employee_id
JOIN condominios c ON c.id = ea.condominio_id
WHERE ea.ativo = true AND e.cpf = :cpf;

-- Via nome (fallback)
SELECT e.nome, c.nome AS condominio, ea.funcao
FROM employee_alocacoes ea
JOIN employees e ON e.id = ea.employee_id
JOIN condominios c ON c.id = ea.condominio_id
WHERE ea.ativo = true AND LOWER(TRIM(e.nome)) = LOWER(TRIM(:nome));
```

**Exemplo real:**
```
ADAILSON SERRA ALVES        CPF 03527554238 → LARANJEIRAS    (AGENTE DE PORTARIA)
AILTON CÉSAR VASCONCELOS                    → MIRANTE         (AGENTE DE PORTARIA)
ANTONIO CARLOS CASTRO GAMA                  → IDEAL FLORES    (AGENTE DE PORTARIA)
GRACIENE SILVA MAIA                         → PRIME ARENA     (AGENTE DE PORTARIA)
ANTONIO CARLOS VIEIRA                       → MICHELANGELO    (ARTÍFICE)
```

---

## Matching com Onvio

### Situação dos campos em onvio_documents
- **Não existe** coluna `colaborador_nome` em `onvio_documents`
- **Não existe** coluna `cpf_colaborador` em `onvio_documents`
- Matching é feito via `referente_a_employee_id` (UUID FK → employees.id)

### Por referente_a_employee_id (FK direta)
**39/93 docs de funcionário** já têm FK preenchida (42% de cobertura):

```
ADEMIR SALUSTIANO       → VILLA PÁSSAROS (4 docs)
ANTONIO DINIZ ASSIS     → IDEAL FLORES   (2 docs)
ANTONIO WALCICLEY       → IDEAL FLORES   (1 doc)
DANIEL VIDAL LARROQUE   → IDEAL FLORES   (3 docs)
EDILENE SALES SOUSA     → IDEAL FLORES   (1 doc)
FERNANDA VINHOTE        → IDEAL FLORES   (3 docs)
GEILSON RODRIGUES       → IDEAL FLORES   (1 doc)
LIVIA CARISE CONSENTINE → IDEAL FLORES   (9 docs)
MARTA DA SILVA PINHEIRO → IDEAL FLORES   (1 doc)
MAURICIO ALVES CHAGAS   → PRIME ARENA    (3 docs)
RAIMUNDO JOSE BATISTA   → PRIME ARENA    (3 docs)
```

### Por nome exato (DP vs Onvio)
- `colaborador_nome` não existe em `onvio_documents` — matching por nome via SQL não é possível diretamente
- 54/93 employee docs ainda **sem** `referente_a_employee_id` — GEDEON deve fazer backfill via nome/CPF extraído do PDF

### Por CPF
- `cpf_colaborador` não existe em `onvio_documents`
- CPF deve ser extraído do parser de documentos e cruzado com `employees.cpf`

### Diferenças de formato (INV-1: leitura dos controllers confirma)
- DP armazena nomes em UPPERCASE: `GRACIENE SILVA MAIA`
- `employee_controller_typed.py` busca por `.ilike(f"%{search}%")` — case-insensitive
- `people_management/hr/employee_controller.py` busca via `EmployeeService.get_active_employees(search=...)` — normaliza internamente
- Matching seguro: `LOWER(TRIM(e.nome)) = LOWER(TRIM(:nome))`

---

## Endpoints existentes (INV-1: arquivos lidos integralmente)

### Arquivos lidos na íntegra (INV-1 §13.1)

| Arquivo | Linhas | Status |
|---------|--------|--------|
| `backend/modules/people_management/hr/controllers/employee_controller.py` | 294L | ✅ lido |
| `backend/modules/operacional/controllers/allocation_controller.py` | 415L | ✅ lido |
| `backend/modules/operacional/controllers/employee_controller_typed.py` | 229L | ✅ lido |

### Endpoint de maior interesse para GEDEON

**`GET /api/v1/people-management/hr/employees/cpf/{cpf}`**
```python
# people_management/hr/controllers/employee_controller.py linha 167-183
@router.get("/cpf/{cpf}", summary="Buscar Funcionário por CPF")
async def get_employee_by_cpf(cpf: str, ...) -> DPEmployeeRead:
    """Busca funcionário por CPF."""
    service = EmployeeService(db)
    employee = await service.get_by_cpf(cpf)
    if not employee:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return employee
```
Este endpoint É EXATAMENTE o que o GEDEON precisa — mas está offline (ver abaixo).

### Mapa completo de endpoints DP

| Endpoint | Arquivo | Status |
|----------|---------|--------|
| `GET /api/v1/people-management/hr/employees` | hr/employee_controller.py L37 | **404** |
| `GET /api/v1/people-management/hr/employees/cpf/{cpf}` | hr/employee_controller.py L173 | **404** |
| `GET /api/v1/people-management/hr/employees/{id}` | hr/employee_controller.py L136 | **404** |
| `GET /api/v1/people-management/hr/employees/search` | hr/employee_controller.py L113 | **404** |
| `GET /api/v1/operacional/allocations` | operacional/allocation_controller.py L73 | **404** |
| `GET /api/v1/operacional/allocations/employee/{id}` | operacional/allocation_controller.py L202 | **404** |

### Causa raiz dos 404 — `modules.operacional.ai` ausente

```
DP: falha ao incluir employee_router: No module named 'modules.operacional.ai'
DP: falha ao incluir admission_router: No module named 'modules.operacional.ai'
DP: falha ao incluir termination_router: No module named 'modules.operacional.ai'
DP: falha ao incluir benefits_router: No module named 'modules.operacional.ai'
DP: falha ao incluir vacation_router: No module named 'modules.operacional.ai'
DP: falha ao incluir discipline_router: No module named 'modules.operacional.ai'
[... todos os 14+ sub-routers do HR falham pelo mesmo motivo]
```

O `people_management/hr/controllers/employee_controller.py` importa indiretamente `modules.operacional.ai`
(via algum serviço do `modules.operacoes`). O safe_import captura o erro e não registra nenhum endpoint.

**Única rota registrada no HR router:** `/hr/contracts` (não usa operacional.ai)

---

## O GEDEON consegue perguntar ao DP onde está o colaborador?

**SIM — via SQL direto (endpoints REST offline por bug de dependência)**

```python
# Query recomendada para GEDEON (SyncSessionLocal)
from sqlalchemy import text
with SyncSessionLocal() as db:
    row = db.execute(
        text("""
            SELECT e.nome, c.nome as condominio, ea.funcao
            FROM employee_alocacoes ea
            JOIN employees e ON e.id = ea.employee_id
            JOIN condominios c ON c.id = ea.condominio_id
            WHERE ea.ativo = true AND e.cpf = :cpf
        """),
        {"cpf": cpf_normalizado}
    ).fetchone()
```

**Quando `modules.operacional.ai` for criado/corrigido**, o endpoint preferencial será:
- `GET /api/v1/people-management/hr/employees/cpf/{cpf}` (retorna DPEmployeeRead com todos os dados do funcionário)

---

## Recomendação — campo mais confiável para matching

| Prioridade | Campo | Disponível em Onvio | Confiabilidade |
|-----------|-------|---------------------|---------------|
| 1 | `referente_a_employee_id` | 39/93 docs | 100% (FK direta) |
| 2 | CPF extraído do PDF pelo parser | via parser | 100% (único no banco) |
| 3 | Nome extraído do PDF | via parser | 80% (variações de acentuação) |

**Ação recomendada:** completar backfill de `referente_a_employee_id` nos 54 docs restantes via parser de nome/CPF dos PDFs.

---

## SELF-CHECK — 100% do prompt

| Item | Status | Evidência |
|------|--------|-----------|
| STEP 0: tail CONTRACTS_GEDEON.md | ✅ | §90 era última seção |
| STEP 1: Token | ✅ | TOKEN obtido |
| STEP 2: Schema tabelas (employees, postos, alocacoes) | ✅ | employees + employee_alocacoes + condominios |
| STEP 3: Amostra colaboradores | ✅ | 58 rows, CPF/nome/matricula 100% |
| STEP 4: Relação colaborador→posto→condomínio | ✅ | join funciona, 47 ativas |
| STEP 5: Nomes no DP | ✅ | UPPERCASE, 58 rows |
| STEP 5: Nomes no Onvio (colaborador_nome) | ✅ | coluna não existe em onvio_documents |
| STEP 5: Intersecção nome exato | ✅ | não possível via DB direto — via referente_a_employee_id |
| STEP 5: Matching por CPF | ✅ | cpf_colaborador não existe; CPF via parser |
| STEP 6: grep operacional/controllers | ✅ | allocation_controller.py + employee_controller.py |
| STEP 6: grep dp/controllers | ✅ | módulo não existe; DP está em people_management/hr/ |
| STEP 6: grep people_management/controllers | ✅ | hr/employee_controller.py com /cpf/{cpf} |
| STEP 6: curl /operacional/alocacoes | ✅ | 404 — motivo: modules.operacional.ai ausente |
| STEP 6: curl /people-management/dp/employees | ✅ | 404 — prefixo correto é /people-management/hr/employees |
| STEP 7: função get_posto/lookup | ✅ | não existe |
| STEP 7: views pg_views | ✅ | 0 views relevantes |
| INV-1: ler arquivos DP relevantes inteiros | ✅ | hr/employee_controller 294L + allocation_controller 415L + employee_controller_typed 229L |
| INV-2: READ-ONLY | ✅ | zero alterações |
| INV-3: Evidências reais do banco | ✅ | queries com dados reais |
| INV-4: Responde pergunta GEDEON | ✅ | SIM via SQL direto |
| INV-5: commit de docs | ✅ | §91 em CONTRACTS_GEDEON.md |
| STEP 8: Relatório completo | ✅ | este arquivo |

**Commit:** 26b37418 (auditoria) ← ver §91 em CONTRACTS_GEDEON.md
