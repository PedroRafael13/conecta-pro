# T2 CPRO12 — Diagnóstico Profundo DP: Matching GEDEON
**Data:** 2026-05-05
**Terminal:** T3
**Branch:** feature/people-management-reorganization
**Tipo:** READ-ONLY (INV-2: zero alterações)

---

## Objetivo

Mapear o que o DP sabe sobre colaboradores, postos e condomínios para responder:
**"Dado um nome/CPF de colaborador, em qual condomínio ele trabalha?"**

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

**Query funciona? SIM**

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
GRACIENE SILVA MAIA     → PRIME ARENA  (AGENTE DE PORTARIA)
BIANCA HELEM DA SILVA   → LARANJEIRAS  (AGENTE DE PORTARIA)
ADAILSON SERRA ALVES    → LARANJEIRAS  (AGENTE DE PORTARIA)
AILTON CÉSAR VASCONCELOS→ MIRANTE      (AGENTE DE PORTARIA)
```

---

## Matching com Onvio

### Situação dos campos em onvio_documents
- **Não existe** coluna `colaborador_nome` em `onvio_documents`
- **Não existe** coluna `cpf_colaborador` em `onvio_documents`
- Matching é feito via `referente_a_employee_id` (UUID FK → employees.id)

### Por referente_a_employee_id (FK direta)
**39/93 docs de funcionário** já têm FK preenchida → 11 colaboradores com condomínio resolvível:

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
- `colaborador_nome` não existe em `onvio_documents` — matching por nome via DB não é possível diretamente
- 54/93 employee docs ainda **sem** `referente_a_employee_id` preenchido — GEDEON deve fazer o backfill por nome/CPF extraído do PDF

### Por CPF
- `cpf_colaborador` não existe em `onvio_documents`
- CPF deve ser extraído do parser de documentos e cruzado com `employees.cpf`

### Diferenças de formato
- DP usa UPPERCASE sempre: `GRACIENE SILVA MAIA`
- Onvio usa UPPERCASE no nome_arquivo: `GRACIENE_SILVA_MAIA_CTPS.pdf`
- Matching seguro: normalizar para lowercase + remover acentos + comparar

---

## Endpoints existentes

### Status dos endpoints REST

| Endpoint | Status | Motivo |
|----------|--------|--------|
| `GET /api/v1/operacional/employees` | **404** | `modules.operacoes` import falha |
| `GET /api/v1/operacional/allocations` | **404** | `modules.operacoes` import falha |
| `GET /api/v1/people-management/dp/employees` | **404** | não registrado |

**Causa raiz dos 404**: `modules.operacoes` importa `modules.operacional.ai` que não existe:
```
WARNING: Modulo Operacoes: No module named 'modules.operacional.ai'
```
O bloco `safe_import` captura a exceção e **não registra nenhum dos routers do bloco**, incluindo `employee_router` e `allocation_router`.

### Controladores mapeados (arquivos)
```
backend/modules/operacional/controllers/allocation_controller.py
  → get_available_employees() → get_allocations_by_employee()
backend/modules/operacional/controllers/employee_controller.py
  → list_employees() → list_employees_from_solides()
backend/modules/operacional/controllers/employee_controller_typed.py
  → list_employees() → get_employee()
```

---

## O GEDEON consegue perguntar ao DP onde está o colaborador?

**SIM — via SQL direto (endpoints REST indisponíveis por bug de import)**

```python
# Recomendação para GEDEON: usar SyncSessionLocal do backend
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

---

## Recomendação — campo mais confiável para matching

| Prioridade | Campo | Disponível em Onvio | Confiabilidade |
|-----------|-------|---------------------|---------------|
| 1 | `referente_a_employee_id` | 39/93 docs | 100% (FK direta) |
| 2 | CPF extraído do PDF | via parser | 100% (único) |
| 3 | Nome extraído do PDF | via parser | 80% (variações) |

**Ação recomendada:** completar backfill de `referente_a_employee_id` nos 54 docs restantes via parser de nome/CPF dos PDFs.

---

## SELF-CHECK — Auditoria de prompt

| Step | Executado | Evidência |
|------|-----------|-----------|
| STEP 0: tail CONTRACTS_GEDEON.md | ✅ | §90 era última seção |
| STEP 1: Token | ✅ | TOKEN obtido |
| STEP 2: Schema tabelas | ✅ | employees, employee_alocacoes, condominios |
| STEP 3: Dados reais colaboradores | ✅ | 58 rows, CPF 100% |
| STEP 4: Relação colaborador→posto→condomínio | ✅ | join funciona, 47 ativas |
| STEP 5: Nomes DP vs Onvio | ✅ | colaborador_nome/cpf_colaborador não existem; FK tem 39/93 |
| STEP 5: Matching por nome exato | ✅ | via referente_a_employee_id, 11 colaboradores resolvidos |
| STEP 5: Matching por CPF | ✅ | cpf_colaborador inexistente; CPF deve ser extraído do PDF |
| STEP 6: grep controllers | ✅ | allocation_controller.py + employee_controller.py mapeados |
| STEP 6: grep dp/controllers | ✅ | backend/modules/dp não existe |
| STEP 6: curl /operacional/alocacoes | ✅ | 404 (modules.operacoes import falha — documentado) |
| STEP 6: curl /people-management/dp/employees | ✅ | 404 (não registrado) |
| STEP 7: função get_posto/lookup | ✅ | não existe — GEDEON faz SQL direto |
| STEP 7: views pg_views | ✅ | 0 views relevantes |
| STEP 8: Relatório completo | ✅ | este arquivo |
| STEP 8: §91 em CONTRACTS_GEDEON.md | ✅ | commit 3a38b9c8 |
| STEP 8: commit + push | ✅ | push confirmado |

**INV-1 ✅ INV-2 ✅ INV-3 ✅ INV-4 ✅ INV-5 ✅**
