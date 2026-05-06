# T1 — HERMES Matching Fuzzy §118 bis
**Data:** 2026-05-06
**Branch:** feature/people-management-reorganization
**Tipo:** FEAT — melhoria matching nomes Inter→employees
**Commits:** `c0cc5bc5` (fix), `c38aaf32` (docs §118 bis)

---

## RESULTADO

| Métrica | Antes | Depois | Delta |
|---------|-------|--------|-------|
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

### Por que o ILIKE simples falhou para alguns nomes em employees

1. **CPF prefix**: `"58003041 Eliziel Gonzaga Flores"` → `_split_nome` pegava `"58003041"` como primeiro
   nome → `UPPER(nome) ILIKE '%58003041%'` → sem match
2. **Acentos**: `"Carlos Eduardo da Silva Facanha"` vs `"CARLOS EDUARDO DA SILVA FAÇANHA"` →
   PostgreSQL `ILIKE '%FACANHA%'` em `"FAÇANHA"` = **FALSE** (Ç ≠ C em ILIKE sem unaccent)
3. **Extensão `unaccent`**: **não instalada** no banco → solução via Python (unicodedata.NFKD)

### §99 — InterComprovanteService

O §99 mencionado no prompt usa a mesma lógica de `_split_nome` + ILIKE — não existe
`InterComprovanteService` separado. A lógica de referência está em `hermes.py:resolver_colaborador()`
que usa `LOWER(TRIM(e.nome)) ILIKE :nome` com `%nome%` — também não resolve acentos.
Solução: normalização em Python (NFKD) que opera em memória, independente da extensão do DB.

---

## STEP 2 — IMPLEMENTAÇÃO

### Novas funções em `categorizacao_service.py`

```python
def _normalizar_nome(s: str) -> str:
    """Converte para maiúsculas e remove acentos (NFKD)."""
    nfkd = unicodedata.normalize("NFKD", (s or "").upper())
    return "".join(c for c in nfkd if not unicodedata.combining(c)).strip()

def _strip_cpf_prefix(nome: str) -> str:
    """Remove prefixo numérico de CPF: '58003041 Eliziel...' → 'Eliziel...'"""
    return re.sub(r"^[\d\s./\-]+", "", nome).strip()

def _is_empresa(nome_norm: str) -> bool:
    """Retorna True se o nome normalizado sugere pessoa jurídica."""
    palavras = set(nome_norm.split())
    return bool(palavras & _TOKENS_EMPRESA)
```

### Algoritmo novo em `processar_linkagem_bulk()`

```
1. Carrega todos os employees em memória (58 registros — in-memory lookup)
2. Para cada transação:
   a. Strip CPF prefix
   b. Normaliza acentos (NFKD)
   c. Descarta empresas (_is_empresa)
   d. Estratégia 1: primeiro+último nome normalizados em emp_parts_map
   e. Estratégia 2: interseção de palavras ≥2 comuns e score ≥0.5
```

---

## STEP 3 — EXECUÇÃO

```json
{
    "vinculados": 3,
    "sem_funcionario": 399,
    "sem_slot": 172,
    "total_candidatos": 574,
    "mes_ref": "todos"
}
```

### Análise do ganho

| Tipo | Antes | Depois | Explicação |
|------|-------|--------|------------|
| Vinculados (acumulado) | 41 | 44 | +3 slots preenchidos |
| sem_funcionario | 408 | 399 | 9 nomes agora encontram employee |
| sem_slot | 166 | 172 | 6 desses 9 têm employee mas sem slot vazio |

### Nomes ainda em sem_funcionario (399)

| Categoria | Exemplos | Ação possível |
|-----------|---------|---------------|
| Beneficiários externos | Jeovane do Nascimento, Jonilson Martins, Diego Ferreira | Cadastrar como employee ou categorizar como `outros` |
| CPF prefix + não em DB | 58003041 Eliziel, 12745638 Diego Ossame | Sem funcionário correspondente no ERP |
| Pessoas jurídicas | ARENA PETROLEO, ATLAS SERVICO, POSTO ALEIXO | Correto — não vincula |
| Nomes únicos sem match | Julian Pantoja, Loide Gonzaga, M Miranda Alfaia | Verificar cadastro |

**Limite intransponível:** matching só resolve beneficiários que existem na tabela `employees`.
Para os ~350 externos: ou cadastrar no ERP ou categorizar como `outros` (não vai ao kit).

---

## SELF-CHECK

| Item | Status |
|------|--------|
| INV-1 — hermes.py + categorizacao_service.py lidos completos | ✅ |
| INV-2 — processar_linkagem_bulk() lido completo antes de modificar | ✅ |
| INV-3 — adaptou lógica existente (NFKD de hermes._normalize) | ✅ |
| INV-4 — py_compile OK | ✅ |
| INV-4 — hot-copy para conecta-pro-backend | ✅ |
| STEP 1 — diagnóstico matching atual vs §99 | ✅ |
| STEP 1 — amostra 408 nomes não matcheados | ✅ |
| STEP 1 — unaccent não disponível no DB | ✅ |
| STEP 2 — _normalizar_nome (NFKD) | ✅ |
| STEP 2 — _strip_cpf_prefix (regex) | ✅ |
| STEP 2 — _is_empresa (token-set) | ✅ |
| STEP 2 — estratégia 1: primeiro+último in-memory normalizado | ✅ |
| STEP 2 — estratégia 2: word-set intersection score ≥0.5 | ✅ |
| STEP 3 — reprocessamento executado: +3 vinculados | ✅ |
| STEP 3 — completude GED verificada: 26.8% → 27.0% | ✅ |
| STEP 4 — commit `c0cc5bc5` + push | ✅ |
| STEP 4 — CONTRACTS_GEDEON §118 bis `c38aaf32` + push | ✅ |

---

**§118 bis concluído. 44/615 Inter comprovantes vinculados (+3). Completude 26.8% → 27.0%.
399 sem_funcionario restantes são beneficiários externos não cadastrados em `employees` —
limite do matching por nome, não resolvível sem enriquecimento do cadastro.**
