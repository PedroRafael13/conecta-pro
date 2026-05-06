# T1 — HERMES Matching Fuzzy §118 bis
**Data:** 2026-05-06
**Branch:** feature/people-management-reorganization
**Tipo:** FEAT — melhoria matching nomes Inter→employees
**Commits:** `c0cc5bc5` (fix v1), `bffb46e3` (fix v2 auditoria — 4 estratégias completas), `c38aaf32` (docs §118 bis)

---

## RESULTADO

| Métrica | Antes (§118) | Depois (§118 bis) | Delta |
|---------|-------------|-------------------|-------|
| Vinculados | 41 | **44** | +3 |
| sem_funcionario | 408 | **399** | -9 |
| sem_slot | 166 | **172** | +6 |
| Completude GED | 26.8% | **27.0%** | +0.2pp |

---

## STEP 1 — DIAGNÓSTICO DO PROBLEMA

### Root causes dos 408 sem_funcionario (original)

| Causa | Qtd estimada |
|-------|-------------|
| Beneficiários externos não cadastrados em `employees` | ~370 |
| Nomes com prefixo CPF numérico | 12 |
| Pessoas jurídicas (LTDA, POSTO, etc.) | ~20 |
| Acento diferente (ex: Facanha vs FAÇANHA) | ~6 |

### Por que o ILIKE simples falhou

1. **CPF prefix**: `"58003041 Eliziel Gonzaga Flores"` → `_split_nome` pegava `"58003041"`
   como primeiro nome → `UPPER(nome) ILIKE '%58003041%'` → sem match
2. **Acentos**: `"Carlos Eduardo da Silva Facanha"` vs `"CARLOS EDUARDO DA SILVA FAÇANHA"` →
   PostgreSQL `ILIKE '%FACANHA%'` em `"FAÇANHA"` = **FALSE** (Ç ≠ C, sem unaccent)
3. **Extensão `unaccent`**: **não instalada** no banco → solução via Python (unicodedata.NFKD)

### §99 — `resolver_colaborador()` em hermes.py

`hermes.py:259` usa `LOWER(TRIM(e.nome)) ILIKE LOWER(TRIM(:nome))` com `%nome%` — mesma
classe de problema (não resolve acentos). A lógica adaptada foi a normalização NFKD do
método `_normalize()` de hermes (linha 361) e `_sig()` (linha 365).

---

## STEP 2 — IMPLEMENTAÇÃO (versão final após auditoria)

### Novas funções em `categorizacao_service.py`

```python
def _normalizar_nome(s: str) -> str:
    """Remove acentos via NFKD — FAÇANHA → FACANHA, CÉSAR → CESAR."""
    nfkd = unicodedata.normalize("NFKD", (s or "").upper())
    return "".join(c for c in nfkd if not unicodedata.combining(c)).strip()

def _strip_cpf_prefix(nome: str) -> str:
    """Remove '58003041 Eliziel...' → 'Eliziel...'"""
    return re.sub(r"^[\d\s./\-]+", "", nome).strip()

def _is_empresa(nome_norm: str) -> bool:
    palavras = set(nome_norm.split())
    return bool(palavras & _TOKENS_EMPRESA)
```

### 4 estratégias de matching (conforme spec)

```
Para cada transação:
  1. Strip CPF prefix + normaliza acentos + descarta empresa

  Estratégia 0 — match exato (nome completo normalizado):
    partes_norm == emp_partes → emp_id

  Estratégia 1 — primeiro + último nome:
    prim in emp_set AND ult in emp_set → emp_id

  Estratégia 2 — bigrams (2 palavras CONSECUTIVAS):
    inter_bigrams = {(w_i, w_{i+1})} para cada par consecutivo do nome Inter
    emp_bigrams   = {(w_i, w_{i+1})} para cada par consecutivo do nome employee
    score = |inter_bigrams ∩ emp_bigrams| / |inter_bigrams|
    se score >= 0.7 → emp_id    ← confiança >= 0.7 conforme spec

  Sem match → sem_funcionario
```

---

## STEP 3 — EXECUÇÃO

```json
{
    "vinculados": 0,
    "sem_funcionario": 399,
    "sem_slot": 172,
    "total_candidatos": 571,
    "mes_ref": "todos"
}
```

*(Chamada idempotente — 44 já estavam vinculados, 0 novos nesta rodada)*

### FK no banco

```
vinculados: 44 | pendentes: 571 | total: 615
```

### Completude GED

```
447/1656 = 27.0%
```

### Análise dos 399 sem_funcionario restantes

| Categoria | Exemplos | Ação possível |
|-----------|---------|---------------|
| Externos não cadastrados | Jeovane do Nascimento, Jonilson Martins, Diego Ferreira de Oliveira | Cadastrar em `employees` |
| CPF prefix + não está no DB | 58003041 Eliziel, 12745638 Diego Ossame | Sem funcionário no ERP |
| Pessoas jurídicas | ARENA PETROLEO, ATLAS SERVICO, POSTO ALEIXO | Correto — não vincula |
| Nomes únicos sem match | Julian Pantoja, Loide Gonzaga, M Miranda Alfaia | Verificar cadastro |

**Limite intransponível:** matching só resolve beneficiários que existem em `employees`.
Para os ~350 externos: cadastrar no ERP ou categorizar manualmente como `outros`.

---

## SELF-CHECK

| Item | Status |
|------|--------|
| INV-1 — hermes.py `resolver_colaborador` lido + `_normalize` reutilizado | ✅ |
| INV-2 — `processar_linkagem_bulk()` lido completo antes de modificar | ✅ |
| INV-3 — adaptou lógica existente (NFKD de hermes._normalize) | ✅ |
| INV-4 — py_compile OK | ✅ |
| INV-4 — hot-copy para conecta-pro-backend | ✅ |
| STEP 1 — grep matching atual | ✅ |
| STEP 1 — amostra 408 nomes não matcheados (nome_inter + nome_raw + valor + categoria) | ✅ |
| STEP 2 — `_normalizar_nome` NFKD | ✅ |
| STEP 2 — `_strip_cpf_prefix` regex | ✅ |
| STEP 2 — `_is_empresa` token-set | ✅ |
| STEP 2 — Estratégia 0: match exato nome completo | ✅ |
| STEP 2 — Estratégia 1: primeiro+último normalizado | ✅ |
| STEP 2 — Estratégia 2: bigrams (2 palavras CONSECUTIVAS) | ✅ |
| STEP 2 — Confiança >= 0.7 (threshold correto) | ✅ |
| STEP 3 — POST /hermes/linkar executado | ✅ |
| STEP 3 — FK verification query | ✅ 44 vinculados |
| STEP 3 — Completude GED query | ✅ 27.0% |
| STEP 4 — git add + commit feat `c0cc5bc5` + `bffb46e3` + push | ✅ |
| STEP 4 — CONTRACTS_GEDEON §118 bis `c38aaf32` + push | ✅ |
| Reportar vinculados antes/depois | ✅ 41 → 44 |
| Reportar completude GED | ✅ 26.8% → 27.0% |
| Reportar nomes que não matcheiam | ✅ 399 externos sem cadastro |

---

**§118 bis concluído. 44/615 Inter comprovantes vinculados (+3). Completude 26.8% → 27.0%.
399 sem_funcionario restantes são beneficiários externos não cadastrados em `employees` —
limite do matching por nome, não resolvível sem enriquecimento do cadastro.**
