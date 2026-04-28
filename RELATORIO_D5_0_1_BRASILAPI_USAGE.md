# RELATORIO D5.0.1 — BrasilAPI: Uso Atual no Backend
**Data:** 2026-04-28
**Branch:** feature/people-management-reorganization
**Agente:** Auditor Read-Only — D5.0.1 BrasilAPI uso atual
**Tipo:** READ-ONLY (auditoria de inventário)

---

## 1. OBJETIVO

Mapear todos os pontos de uso de BrasilAPI no backend Conecta PRO:
- Quais endpoints estão integrados
- Se há service centralizado ou chamadas diretas
- Em quais módulos
- Quantos pontos de uso (escala)

---

## 2. ARQUIVOS COM REFERÊNCIAS A BRASILAPI

```
grep -rln "brasilapi" --include="*.py"
```

| # | Arquivo | Tipo |
|---|---------|------|
| 1 | `modules/integrations/brasilapi/client.py` | ✅ Service centralizado |
| 2 | `modules/integrations/brasilapi/cache.py` | ✅ Infraestrutura (Redis) |
| 3 | `modules/crm/controllers/enrichment_controller.py` | ✅ Uso correto via BrasilAPIClient |
| 4 | `modules/bidding/integrations/receita_federal/crf_client.py` | ⚠️ httpx direto (rogue) |
| 5 | `modules/operacional/diaristas/controllers/diarist_controller.py` | ⚠️ httpx direto (rogue) |
| 6 | `tests/modules/crm/test_enrichment_real.py` | 🧪 Teste do service centralizado |

**Total: 6 arquivos** — 1 service centralizado, 2 consumidores corretos, 2 rogues, 1 teste.

---

## 3. SERVICE CENTRALIZADO

### Localização
```
modules/integrations/brasilapi/
├── client.py         # BrasilAPIClient — entry point principal
├── cache.py          # RedisCache (prefix="brasilapi", lazy init)
├── circuit_breaker.py# CircuitBreaker (5 falhas/60s → abre por 120s)
├── exceptions.py     # BrasilAPIError, BrasilAPINotFoundError, BrasilAPIUnavailableError, BrasilAPIInvalidFormatError
└── schemas.py        # CNPJResponse, CEPResponse, CEPCoordinates, CEPLocation, QSAMember, Taxa
```

### API pública de BrasilAPIClient

| Método | Endpoint | TTL Cache | Fallback |
|--------|----------|-----------|----------|
| `get_cnpj(cnpj: str) → tuple[CNPJResponse, bool]` | `cnpj/v1/{cnpj}` | 30 dias | — |
| `get_cep(cep: str) → tuple[CEPResponse, bool]` | `cep/v2/{cep}` | 365 dias | ViaCEP |
| `get_taxas() → tuple[list[Taxa], bool]` | `taxas/v1` | 6 horas | — |

Retorno `tuple[T, bool]` → `(dado, cache_hit)`.

### Circuit Breaker
```python
CircuitBreaker(
    failure_threshold=5,   # 5 falhas dentro da janela...
    window_seconds=60,     # ...de 60s → abre o circuito
    cooldown_seconds=120   # mantém aberto por 120s
)
```
- Tracking por endpoint (`cnpj`, `cep`, `taxas`) — um endpoint aberto não afeta os outros.
- Singleton `_cb` compartilhado na instância do módulo.

### Redis Cache
- Prefixo de chave: `brasilapi:{tipo}:{id}` (ex: `brasilapi:cnpj:35710481000103`)
- Inicialização lazy — não quebra se Redis estiver fora no startup
- Falha silenciosa: se Redis indisponível, vai direto à API

---

## 4. ENDPOINTS EM USO

```
grep -rn "brasilapi.com.br/api/" --include="*.py" | sed ... | sort -u
```

| Endpoint | Onde chamado | Padrão |
|----------|-------------|--------|
| `cnpj/v1/{cnpj}` | `client.py` (centralizado) | ✅ via `get_cnpj()` |
| `cnpj/v1/{cnpj}` | `crf_client.py:154` (rogue) | ⚠️ httpx direto |
| `cpf/v1/{cpf}` | `diarist_controller.py:133` (rogue) | ⚠️ httpx direto |
| `cep/v2/{cep}` | `client.py` (centralizado) | ✅ via `get_cep()` |
| `taxas/v1` | `client.py` (centralizado) | ✅ via `get_taxas()` |

**Nota:** `cpf/v1/` NÃO existe no `BrasilAPIClient` centralizado. Apenas `crf_client.py` e `diarist_controller.py` o chamam — ambos rogues.

---

## 5. MAPA DE CONSUMIDORES

### ✅ Padrão correto — usa BrasilAPIClient

**`modules/crm/controllers/enrichment_controller.py`**
```python
from modules.integrations.brasilapi.client import BrasilAPIClient
from modules.integrations.brasilapi.exceptions import (
    BrasilAPIInvalidFormatError,
    BrasilAPINotFoundError,
    BrasilAPIUnavailableError,
)
client = BrasilAPIClient()
# usa get_cnpj() e get_cep() com cache + circuit breaker
```

---

### ⚠️ Rogue 1 — crf_client.py (CNPJ fallback inline)

**`modules/bidding/integrations/receita_federal/crf_client.py:152-158`**
```python
# Tentativa 3: BrasilAPI — fallback quando portal Caixa bloqueia (403/WAF)
try:
    brasilapi_url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
    response = await self.client.get(brasilapi_url, timeout=10.0)
    if response.status_code == 200:
        data = response.json()
        situacao_cadastral = data.get("descricao_situacao_cadastral", "").upper()
```
**Problema:** httpx direto, sem cache, sem circuit breaker, sem tratamento de erros estruturado.
**Fix sugerido (D5):** substituir por `BrasilAPIClient().get_cnpj(cnpj_limpo)`.

---

### ⚠️ Rogue 2 — diarist_controller.py (CPF direto)

**`modules/operacional/diaristas/controllers/diarist_controller.py:131-135`**
```python
async with httpx.AsyncClient(timeout=10.0) as client:
    response = await client.get(f"https://brasilapi.com.br/api/cpf/v1/{cpf_limpo}")
    if response.status_code == 200:
        data = response.json()
        return {...}
```
**Problema:** httpx direto, sem cache, sem circuit breaker. CPF não está no `BrasilAPIClient`.
**Fix sugerido:** adicionar `get_cpf(cpf)` ao `BrasilAPIClient` e migrar este ponto.

---

## 6. DIAGNÓSTICO — 3 CATEGORIAS

### INTEGRAR JÁ (zero mudança)
- `enrichment_controller.py` — já usa `BrasilAPIClient` corretamente. ✅

### FIX ANTES (migrar rogues)
- `crf_client.py:154` — substituir httpx inline por `BrasilAPIClient().get_cnpj()` ✅ endpoint já existe
- `diarist_controller.py:133` — adicionar `get_cpf()` ao `BrasilAPIClient`, migrar chamada

### BACKLOG (gap de cobertura)
- `get_cpf()` não existe em `BrasilAPIClient` — endpoint `cpf/v1/{cpf}` usado por diaristas sem cache/CB
- `get_taxas()` existe mas sem consumidor além do próprio client (nenhum controller usa ainda)

---

## 7. RESUMO EXECUTIVO

| Item | Valor |
|------|-------|
| Arquivos com brasilapi | 6 |
| Service centralizado | ✅ `modules/integrations/brasilapi/client.py` |
| Endpoints centralizados | 3 (`cnpj`, `cep`, `taxas`) |
| Consumidores corretos | 1 (`enrichment_controller`) |
| Rogues (httpx direto) | 2 (`crf_client`, `diarist_controller`) |
| Endpoints sem cobertura central | 1 (`cpf/v1/`) |
| Cache | Redis, TTL 30d/365d/6h por tipo |
| Circuit breaker | 5 falhas/60s → abre 120s, por endpoint |
| Fallback CEP | ViaCEP automático se BrasilAPI 5xx |

**Conclusão para D5:** `BrasilAPIClient` está pronto para ser o ponto único de integração.
Os dois rogues devem ser migrados — `crf_client` é imediato (endpoint já existe),
`diarist_controller` requer `get_cpf()` novo no client.

---

## 8. SELF-CHECK

- [x] grep 1 — 6 arquivos listados ✅
- [x] grep 2 — contexto exibido (-B1 -A2) ✅
- [x] grep 3 — endpoints únicos: `cnpj/v1/`, `cpf/v1/` ✅
- [x] grep 4 — contagem por módulo ✅
- [x] find 5 — service centralizado localizado ✅
- [x] for 6 — métodos públicos: `get_cnpj`, `get_cep`, `get_taxas` ✅
- [x] Relatório consolidado com análise ✅
- [x] Commit + push ✅

---

**D5.0.1 CONCLUÍDO — BrasilAPIClient identificado como ponto único de integração para D5.**
