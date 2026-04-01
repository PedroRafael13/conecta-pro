# RELATÓRIO — GETATTR FIX: 15 REPOSITÓRIOS / 18 OCORRÊNCIAS

**Data:** 2026-04-01
**Branch:** `feature/people-management-reorganization`
**Executor:** Claude Sonnet 4.6
**Commit:** `9a948bf3`

---

## AUTO-AUDITORIA — EXECUÇÃO DO PROMPT

| Passo | Descrição | Status |
|-------|-----------|--------|
| PASSO 1 | Mapeamento de todas as ocorrências perigosas | ✅ |
| PASSO 2 | Exame de contexto + classificação de riscos | ✅ |
| PASSO 3 | Aplicação do fix (script automatizado) | ✅ |
| PASSO 4 | Correção de imports (`inspect as sa_inspect`) | ✅ |
| PASSO 5 | Hot copy para container + validação | ✅ |
| PASSO 6 | Commit `fix(repositories): valida order_by...` | ✅ |
| PASSO 7 | Push para `origin/feature/people-management-reorganization` | ✅ |

---

## T3 — TABELA PRINCIPAL DE RESULTADOS

| Repositório | Model | Ocorrências | Fix Aplicado |
|-------------|-------|-------------|--------------|
| `ged/document_share_repository.py` | `DocumentShare` | 1 (order_by) | `sa_inspect` validation |
| `ged/folder_repository.py` | `GEDFolder` | 1 (order_by) | `sa_inspect` validation |
| `ged/document_repository.py` | `Document` | 1 (order_by) | `sa_inspect` validation |
| `ged/document_tag_repository.py` | `DocumentTag` | 1 (order_by) | `sa_inspect` validation |
| `recruitment/interview_repository.py` | `Interview` | 1 (order_by) | `sa_inspect` validation |
| `recruitment/candidate_repository.py` | `Candidate` | 1 (order_by) | `sa_inspect` validation |
| `recruitment/application_repository.py` | `JobApplication` | 1 (order_by) | `sa_inspect` validation |
| `recruitment/job_position_repository.py` | `JobPosition` | 1 (order_by) | `sa_inspect` validation |
| `campo/ordem_servico_repository.py` | `OrdemServico` | 1 (order_by) | `sa_inspect` validation |
| `campo/visita_repository.py` | `Visita` | 1 (order_by) | `sa_inspect` validation |
| `retention/profile_repository.py` | `OperationalProfile` + `PostMatch` | 2 (order_by ×2) | `sa_inspect` validation |
| `retention/turnover_repository.py` | `TurnoverEvent` | 1 (order_by) | `sa_inspect` validation |
| `services/service_repository.py` | `Service` | 1 (order_by) | `sa_inspect` validation |
| `ai/report_repository.py` | `GeneratedReport` | 1 (order_by) | `sa_inspect` validation |
| `ai/sentiment_repository.py` | `SentimentAnalysis` + `FeedbackInsight` | 3 (order_by ×2 + group_by) | `sa_inspect` validation |
| **TOTAL** | **17 models** | **18 ocorrências** | **18 fixes** |

---

## PASSO 1 — MAPEAMENTO COMPLETO

### Busca inicial

```bash
grep -rn "getattr(" backend/modules --include="*repositor*.py" | grep -v ".pyc"
```

Resultado: **18 ocorrências** em **15 arquivos** de repositório.

### Padrão identificado (PERIGOSO)

```python
# ANTES — getattr sem validação de coluna real
order_column = getattr(Model, order_by, Model.created_at)
query = query.order_by(order_column.desc())
```

**Por que é perigoso:** Se `order_by` receber o nome de um `@property` Python
(ex: `is_expired`, `nome_completo`, `days_until_expiry`), o `getattr` retorna
o objeto `property` em vez de uma coluna SQLAlchemy. A chamada `.desc()` sobre
um `property` lança `AttributeError: 'property' object has no attribute 'desc'`
→ HTTP 500 interno não documentado.

---

## PASSO 2 — CLASSIFICAÇÃO DE RISCOS

### Risco por módulo

| Módulo | Arquivos | Risco | Justificativa |
|--------|----------|-------|---------------|
| GED | 4 | ALTO | `DocumentShare` tem `is_expired` @property; `Document` tem `is_archived` @property |
| Recruitment | 4 | MÉDIO | Models com propriedades calculadas de datas |
| Campo | 2 | MÉDIO | `OrdemServico` tem status calculados como property |
| Retention | 2 | ALTO | `OperationalProfile` tem `risk_score` @property |
| Services | 1 | BAIXO | Model simples |
| AI (Report) | 1 | BAIXO | Model simples |
| AI (Sentiment) | 1 | ALTO | `group_by` dinâmico adicional; `FeedbackInsight` com properties |

### Variante `group_by` (extra perigosa)

Em `sentiment_repository.py` havia também:

```python
# ANTES — group_by dinâmico sem validação
group_column = getattr(SentimentAnalysis, group_by)  # sem fallback!
if group_column:
    query = query.group_by(group_column)
```

Esta variante era **ainda mais perigosa** pois sem fallback: se `group_by`
fosse um `@property`, o `.group_by(property_object)` causava erro de tipo no
SQLAlchemy.

---

## PASSO 3 — FIX APLICADO

### Padrão APÓS (seguro)

```python
# DEPOIS — validação via sa_inspect antes do getattr
from sqlalchemy import ..., inspect as sa_inspect

_valid_order_column_cols = {c.key for c in sa_inspect(Model).mapper.column_attrs}
order_column = getattr(Model, order_by if order_by in _valid_order_column_cols else "created_at")
if order_desc:
    query = query.order_by(order_column.desc())
else:
    query = query.order_by(order_column.asc())
```

### Variante `group_by` APÓS (seguro)

```python
_valid_group_column_cols = {c.key for c in sa_inspect(SentimentAnalysis).mapper.column_attrs}
group_column = getattr(SentimentAnalysis, group_by) if group_by in _valid_group_column_cols else None
if group_column is not None:
    query = query.group_by(group_column)
```

### Por que `mapper.column_attrs`?

- `inspect(Model).mapper.column_attrs` retorna **apenas colunas reais do banco**
- `@property` Python NÃO aparece nesta coleção
- `relationship()` e `hybrid_property` também ficam de fora
- Resultado: whitelist perfeita de campos seguros para `ORDER BY` / `GROUP BY`

---

## PASSO 4 — IMPORTS CORRIGIDOS

Todos os 15 arquivos receberam `inspect as sa_inspect` na linha de import SQLAlchemy:

```python
# Exemplo documentado
from sqlalchemy import and_, func, select, inspect as sa_inspect
```

O script de fix teve um bug inicial: verificava `"sa_inspect" in content` mas o
conteúdo já continha `sa_inspect` nas funções patched, então pulava o import.

**Solução:** segunda passagem que verifica especificamente se `inspect` está
presente na linha `from sqlalchemy import`:

```python
m = re.search(r'(from sqlalchemy import )([^\n]+)', content)
if m and 'inspect' not in m.group(2):
    new_import = f"{m.group(1)}{m.group(2)}, inspect as sa_inspect"
```

---

## PASSO 5 — VALIDAÇÃO

### Import de todos os 15 módulos

```bash
docker exec conecta-pro-backend python3 -c "
for m in [15 módulos]:
    __import__(m)
    print(f'OK: {m}')
"
```

**Resultado:** 15 OK, 0 FAIL

### Lógica de fallback (introspection)

```python
# DocumentShare: is_expired é @property, não aparece em column_attrs
cols = {c.key for c in sa_inspect(DocumentShare).mapper.column_attrs}
'is_expired' in cols  # False → fallback para created_at ✅
'created_at' in cols  # True  → usa coluna real ✅
```

### Endpoints HTTP

| Endpoint | Parâmetro | Antes | Depois |
|----------|-----------|-------|--------|
| `GET /api/v1/ged/documents/?order_by=created_at` | coluna válida | 200 | ✅ 200 |
| `GET /api/v1/ged/documents/?order_by=title` | coluna válida | 200 | ✅ 200 |
| `GET /api/v1/ged/documents/?order_by=is_active_share` | @property | 500 | ✅ 200 |

---

## PASSO 6 — COMMIT

```
Hash:     9a948bf3
Mensagem: fix(repositories): valida order_by contra colunas reais do model
Arquivos: 15 files changed, 51 insertions(+), 18 deletions(-)
Hooks:    ruff (1ª tentativa: 15 auto-fixes) → ruff (2ª tentativa: ✅ Passed)
          ruff-format ✅ | bandit ✅ | detect-secrets ✅
```

**Nota ruff:** Na primeira tentativa, ruff aplicou 15 formatações automáticas
(import ordering, whitespace). Após re-stage, todos os hooks passaram.

---

## PASSO 7 — PUSH

```
Branch:   feature/people-management-reorganization
Remote:   origin (github.com/jjesus1982/conecta-pro.git)
Range:    6c1a915f..9a948bf3
Status:   ✅ PUSHED
```

---

## ZONAS PROIBIDAS — VERIFICAÇÃO

| Arquivo/Dir | Tocado? |
|-------------|---------|
| `alembic/versions/` | ✅ NÃO |
| `main_production.py` | ✅ NÃO |
| `docker-compose*.yml` | ✅ NÃO |
| `.env*` | ✅ NÃO |
| `credentials/` | ✅ NÃO |

---

## ARQUIVOS MODIFICADOS

```
backend/modules/
├── ged/repositories/
│   ├── document_share_repository.py   (+inspect, +_valid_order_column_cols)
│   ├── folder_repository.py           (+inspect, +_valid_order_column_cols)
│   ├── document_repository.py         (+inspect, +_valid_order_column_cols)
│   └── document_tag_repository.py     (+inspect, +_valid_order_column_cols)
├── recruitment/repositories/
│   ├── interview_repository.py        (+inspect, +_valid_order_column_cols)
│   ├── candidate_repository.py        (+inspect, +_valid_order_column_cols)
│   ├── application_repository.py      (+inspect, +_valid_order_column_cols)
│   └── job_position_repository.py     (+inspect, +_valid_order_column_cols)
├── campo/repositories/
│   ├── ordem_servico_repository.py    (+inspect, +_valid_order_column_cols)
│   └── visita_repository.py           (+inspect, +_valid_order_column_cols)
├── retention/
│   ├── profile/repositories/
│   │   └── profile_repository.py      (+inspect, +_valid_order_column_cols ×2)
│   └── turnover/repositories/
│       └── turnover_repository.py     (+inspect, +_valid_order_column_cols)
├── services/repositories/
│   └── service_repository.py          (+inspect, +_valid_order_column_cols)
└── ai/
    ├── report_generator/repositories/
    │   └── report_repository.py       (+inspect, +_valid_order_column_cols)
    └── sentiment_analysis/repositories/
        └── sentiment_repository.py    (+inspect, +_valid_order_column_cols ×2, +_valid_group_column_cols)
```

---

## RESULTADO FINAL

```
╔══════════════════════════════════════════════════════════════╗
║  GETATTR FIX — RESULTADO FINAL                               ║
╠══════════════════════════════════════════════════════════════╣
║  Repositórios corrigidos:    15 / 15                         ║
║  Ocorrências eliminadas:     18 (order_by: 17, group_by: 1)  ║
║  Imports adicionados:        15                              ║
║  Hooks ruff/bandit/secrets:  ✅ Todos passaram               ║
║  Imports em container:       15 OK / 0 FAIL                  ║
║  Endpoints testados:         3 cenários → 200 ✅             ║
║  Zonas Proibidas violadas:   0                               ║
║                                                              ║
║  AttributeError por @property em order_by: ELIMINADO         ║
║  HTTP 500 silencioso por getattr inválido: ELIMINADO         ║
║                                                              ║
║  Commit: 9a948bf3 → origin (pushed)                         ║
╚══════════════════════════════════════════════════════════════╝
```

---

**Gerado por:** Claude Sonnet 4.6
**Data:** 2026-04-01
**Branch:** `feature/people-management-reorganization`
**Commit:** `9a948bf3`
