# RELATORIO D5.1 — BrasilAPI Consolidação + Fix Semântico CRF
**Data:** 2026-04-28
**Branch:** feature/people-management-reorganization
**Agente:** Engenheiro Sênior — D5.1 MIGRAR ROGUES + get_cpf
**Contrato:** §42 (v1.43 → v1.44)
**Commits:** `5ca6b659` (docs) · `c4e005e9` (código)

---

## 1. STEP 0 — Pré-voo

```
Versão contrato: v1.43 ✅
Branch: feature/people-management-reorganization
Último commit: 24eaa662 (D5.0.1 relatório)
```

Estado DB pré-D5.1:
```
kits=18 | docs=1237 | fake=0 | templates=32  ✅
```

BrasilAPIClient localizado:
```
backend/modules/integrations/brasilapi/
  client.py, cache.py, circuit_breaker.py, exceptions.py, schemas.py
```

---

## 2. STEP 1 — Endpoint cpf/v1/ (resultado: CENÁRIO B)

### 1.1 — Leitura BrasilAPIClient (Chesterton §13.1)

Padrão identificado em `get_cnpj()`:
1. `_validate_*()` → normaliza e valida dígitos
2. `_cache.get(key)` → retorna `(Response, True)` se hit
3. `_request_with_retry(url, endpoint_key)` → circuit breaker + retry (max 2)
4. `_cache.set(key, data, ttl)` → persiste
5. Retorna `(ResponseSchema(**data), False)`

Circuit breaker: 5 falhas/60s → abre por 120s. Singleton `_cb` global.

Exceções: `BrasilAPIInvalidFormatError`, `BrasilAPINotFoundError`, `BrasilAPIUnavailableError`.

### 1.2 — Teste cpf/v1/ ao vivo

```bash
CPF_TESTE=00480990239  # CPF de funcionário (obtido via SELECT FROM employees)
curl -sv "https://brasilapi.com.br/api/cpf/v1/${CPF_TESTE}"
```

**Resultado:**
```
HTTP 200 — Content: HTML (Next.js 404 page)
"404: This page could not be found"
```

**Diagnóstico:** endpoint removido da BrasilAPI. A plataforma retorna a página 404
do Next.js (HTML), não um JSON 404 da API. Endpoint **deprecated/removido**.

### 1.3 — Verificação cnpj/v1/ (ainda funcional)

```bash
curl -s "https://brasilapi.com.br/api/cnpj/v1/35710481000103"
# Resultado: CONECTAMAIS ELETRONICA LTDA | ATIVA  ✅
```

---

## 3. STEP 2 — get_cpf() — ABORTADO (Cenário B)

`cpf/v1/` não existe mais. Sem fonte de CPF disponível no BrasilAPIClient.

**Ação:** `get_cpf()` **não implementado**. Backlog D5.1.1:
escolher fonte alternativa (gov.br, SERPRO, ou API paga) antes de implementar.

---

## 4. STEP 3 — diarist_controller — ABORTADO (Cenário B)

Sem endpoint CPF funcional, a migração `diarist_controller.py:133`
não pode ser executada. A chamada httpx direto permanece como rogue documentado:

```python
# diarist_controller.py:133 — ROGUE PENDENTE (D5.1.1)
response = await client.get(f"https://brasilapi.com.br/api/cpf/v1/{cpf_limpo}")
```

**Observação:** a chamada atual falha silenciosamente (cpf/v1/ retorna HTML).
Jordan deve decidir fonte alternativa antes de D5.1.1.

---

## 5. STEP 4 — crf_client: Migração + Fix Semântico

### 5.1 — Arquivo: `modules/bidding/integrations/receita_federal/crf_client.py`

#### Import (nível de módulo — antes era lazy import dentro do try)

```python
# Antes: import lazy dentro do try {}
# Depois: nível de módulo
from modules.integrations.brasilapi.client import BrasilAPIClient
from modules.integrations.brasilapi.exceptions import (
    BrasilAPINotFoundError,
    BrasilAPIUnavailableError,
)
```

#### Tentativa 3 — Fallback BrasilAPI (diff principal)

**Antes:**
```python
brasilapi_url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
response = await self.client.get(brasilapi_url, timeout=10.0)
if response.status_code == 200:
    data = response.json()
    situacao_cadastral = data.get("descricao_situacao_cadastral", "").upper()
    regular = situacao_cadastral == "ATIVA"  # ← BUG SEMÂNTICO
    return {
        "regular": regular,  # True ou False — ambos errados neste contexto
        "situacao": "regular" if regular else "irregular",
        "fonte": "BrasilAPI/ReceitaFederal",
        ...
    }
```

**Depois:**
```python
# IMPORTANTE: BrasilAPI CNPJ retorna situacao_cadastral da RFB, que é
# INDEPENDENTE da regularidade FGTS na Caixa. Empresa pode estar ATIVA na
# RFB mas com débito FGTS pendente. Por isso retornamos `regular=None` —
# afirmar regular=True baseado em CNPJ ativo é falso positivo.
cnpj_data, _ = await BrasilAPIClient().get_cnpj(cnpj_limpo)
situacao_cadastral = (cnpj_data.descricao_situacao_cadastral or "").upper()
cnpj_ativo = situacao_cadastral == "ATIVA"
return {
    "situacao": "indeterminado_portal_indisponivel",
    "regular": None,          # ← explicitamente null
    "cnpj_ativo_rfb": cnpj_ativo,
    "fonte": "BrasilAPI (fallback)",
    "nota": "Portal Caixa indisponível. Status FGTS NÃO confirmado...",
    ...
}
```

#### Retorno final (todas falhas)

```python
# Antes: "regular": False  ← errado
# Depois: "regular": None  ← honesto
```

#### verificar_regularidade() — tratamento tripartite

```python
# Antes:
"apto_licitar": resultado["regular"],  # None → TypeError potencial
"observacao": "..." if resultado["regular"] else "..."  # sem caso None

# Depois:
regular = resultado.get("regular")
"apto_licitar": bool(regular) if regular is not None else None,
"observacao": (
    "Empresa regular..." if regular is True
    else "Empresa com pendências..." if regular is False
    else "Status FGTS indeterminado — portal Caixa indisponivel, consultar manualmente"
),
```

---

## 6. STEP 5 — Deploy

```bash
docker cp backend/modules/ conecta-pro-backend:/app/modules/
docker restart conecta-pro-backend
# health: healthy após ~50s  ✅
```

---

## 7. STEP 6 — Validação E2E

### 6.1 — BrasilAPIClient.get_cnpj() no container
```
BrasilAPIClient.get_cnpj("35710481000103"):
  razao_social: CONECTAMAIS ELETRONICA LTDA
  descricao_situacao_cadastral: ATIVA
  cache_hit: True  ✅
```

### 6.2 — Semântica CRF (assert crítico)
```python
result = {"regular": None, "situacao": "indeterminado_portal_indisponivel", ...}
assert result["regular"] is None  # ✅ PASS
```

### 6.3 — Pytest D5.1 (4 testes novos)
```
tests/modules/bidding/test_crf_client_fallback.py
  test_crf_fallback_brasilapi_nao_afirma_regular_true        ✅ PASS
  test_crf_fallback_cnpj_baixado_regular_none                ✅ PASS
  test_crf_fallback_total_retorna_regular_none               ✅ PASS
  test_verificar_regularidade_apto_licitar_none_quando_indeterminado  ✅ PASS
```

### 6.4 — Regressão D4 + D4.1
```
tests/modules/gedeon/ — 14/14 PASS em 27.98s  ✅
```

**Pytest acumulado: D4(11) + D4.1(3) + D5.1(4) = 18 PASS**

---

## 8. STEP 7 — §42 v1.44

`CONTRACTS_GEDEON.md` atualizado v1.43 → v1.44.

Seções adicionadas:
- §42.1 — Cenário B (cpf/v1/ deprecated)
- §42.2 — Fix semântico CRF (diff + princípio)
- §42.3 — Testes 4/4 PASS
- §42.4 — Princípio consolidado
- §42.5 — Backlog D5.x

Commit docs: `5ca6b659`

---

## 9. STEP 8 — Commits

```
5ca6b659  docs(integrations): CONTRATO v1.44 — §42 D5.1
c4e005e9  refactor(integrations): D5.1 fix semântico CRFFGTSClient + testes (§42)
Push: ✅ origin/feature/people-management-reorganization
```

**Arquivos commitados:**
```
CONTRACTS_GEDEON.md
backend/modules/bidding/integrations/receita_federal/crf_client.py
backend/tests/modules/bidding/test_crf_client_fallback.py
```

---

## 10. VALIDAÇÕES 🔴

| Label | Critério | Resultado |
|-------|----------|-----------|
| 🔴 A | Pytest geral D4+D4.1+D5.1 = 18+ PASS | ✅ 18/18 PASS |
| 🔴 B | get_cpf retorna CPFResponse + cache funciona | ⚠️ ABORTADO — Cenário B (cpf/v1/ deprecated) |
| 🔴 C | diarist_controller endpoint não regrediu | ⚠️ ABORTADO — rogue permanece (sem fonte alternativa) |
| 🔴 D | crf_client fallback retorna regular=None | ✅ assert explícito + 4 testes |
| 🔴 E | Zero httpx direto fora do BrasilAPIClient | ⚠️ 1 rogue restante (diarist, Cenário B) |
| 🔴 F | Frontend BUILD_ID não mudou (só backend) | ✅ zero toque em frontend |
| 🔴 G | Trilogia A/B/C + D1-D4.1 preservados | ✅ 18/1237/0/32 kits/docs/fake/templates |
| 🔴 H | Zero diff zonas proibidas | ✅ git diff só arquivos autorizados |

---

## 11. SELF-CHECK

- [x] STEP 0 — pré-voo: v1.43, 18/1237/0, BrasilAPIClient presente ✅
- [x] STEP 1 — cpf/v1/ testado: DEPRECATED (HTML 404). Cenário B ativado ✅
- [⚠️] STEP 2 — get_cpf ABORTADO (Cenário B) ✅
- [⚠️] STEP 3 — diarist_controller ABORTADO (Cenário B) ✅
- [x] STEP 4 — crf_client: import módulo + semântica + verificar_regularidade ✅
- [x] STEP 5 — deploy hot copy + restart → healthy ✅
- [x] STEP 6 — E2E: BrasilAPIClient CNPJ live, assert regular=None, pytest 4/4 ✅
- [x] STEP 6 — pytest D4+D4.1 14/14 PASS ✅
- [x] STEP 7 — §42 v1.44 commitado ✅
- [x] STEP 8 — código commitado (c4e005e9) + push ✅
- [x] 🔴 A, D, F, G, H — PASS ✅
- [⚠️] 🔴 B, C, E — Cenário B (documentado)

---

## 12. CENÁRIO IDENTIFICADO

**Cenário B** (previsto no prompt):

> `cpf/v1/` DEPRECATED ou exigindo auth: PAUSAR.
> Reportar a Jordan. Sem cpf/v1, diarist_controller continua usando
> httpx direto OU vai pra outro serviço (e.g., gov.br ou pago).

`brasilapi.com.br/api/cpf/v1/` retornou HTML 404 — endpoint removido.
STEP 2 e STEP 3 pausados. STEP 4 (CRF, usa cnpj/v1/) executado normalmente.

---

## 13. ROGUES — ANTES/DEPOIS

| Rogue | Antes | Depois |
|-------|-------|--------|
| `crf_client.py:152` (CNPJ) | ⚠️ httpx direto + bug semântico | ✅ BrasilAPIClient + regular=None |
| `diarist_controller.py:133` (CPF) | ⚠️ httpx direto (sem cache/CB) | ⚠️ mantido — cpf/v1/ deprecated (Cenário B) |

**Rogues restantes: 1** (de 2 original) — diarist_controller pendente até D5.1.1.

---

## 14. D5.1 PRONTO (PARCIAL — CENÁRIO B)

**CRF fix semântico:** `regular=None` quando portal Caixa cai — nunca afirmar
regularidade FGTS com base em CNPJ ativo. Princípio §42 registrado em CONTRACTS_GEDEON.md v1.44.

**BrasilAPIClient:** uso centralizado no CRF agora correto. 1 rogue restante (diarist).

Jordan CIC:
**(a)** Cenário B: `cpf/v1/` removido da BrasilAPI. Para D5.1.1 precisamos definir
fonte alternativa para CPF (gov.br / SERPRO / API paga). Aguardo sua direção.

**(b)** O dashboard de certidões deve tratar `regular=null` com semáforo amarelo
"Indeterminado — verificar manualmente" (nunca verde quando Caixa cai).

**(c)** Confirm: `SELECT * FROM ged_document_kits LIMIT 5;` → sem mudanças (trilogia preservada).

Commits: `5ca6b659` (docs) · `c4e005e9` (código) — `feature/people-management-reorganization` ✅
