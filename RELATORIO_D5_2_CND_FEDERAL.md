# RELATORIO D5.2 — Fix CNDFederalClient URL + Fallback Semântico
**Data:** 2026-04-28
**Branch:** feature/people-management-reorganization
**Agente:** Engenheiro Sênior — D5.2 Fix CND Federal Endpoint
**Contrato:** §43 (v1.44 → v1.45)
**Commits:** `ed0a27a6` (docs) · `6886fbbf` (código)

---

## 1. STEP 0 — Pré-voo

```
Versão contrato: v1.44 ✅
Branch: feature/people-management-reorganization
Último commit: dc971b4f (D5.1 auditoria)
```

Estado DB pré-D5.2:
```
kits=18 | docs=1237 | fake=0 | templates=32  ✅
```

CNDFederalClient localizado:
```
backend/modules/bidding/integrations/receita_federal/cnd_client.py
```

---

## 2. STEP 1 — Investigação Endpoint RFB (resultado: CENÁRIO C)

### 1.1 — URL antiga (stale desde ~03/2025)

```bash
curl -sv "https://solucoes.receita.fazenda.gov.br/..."
# Resultado: HTTP 301 → https://servicos.receitafederal.gov.br/...
# Destino: HTTP 404
```

**Diagnóstico:** `solucoes.receita.fazenda.gov.br` retorna 404 desde março/2025.
Domínio unificado em `receitafederal.gov.br`.

### 1.2 — URL nova testada

```bash
curl -sv "https://servicos.receitafederal.gov.br/servico/certidoes/"
# Resultado: HTTP 200 — HTML com hCaptcha
# Sem form de input CNPJ, sem endpoint programático
```

**Diagnóstico:** Portal novo exige login gov.br vinculado ao CNPJ matriz.
Sem OAuth2 configurado, Tentativa 1 sempre falha → sempre cai no fallback.

### 1.3 — H2: Endereços alternativos testados

```bash
curl "https://servicos.receitafederal.gov.br/api/certidoes/v1/?cnpj=..."
# HTTP 404

curl "https://cav.receita.fazenda.gov.br/solucoes/certidoes?cnpj=..."
# HTTP 302 → login gov.br
```

**Conclusão:** Cenário C — sem API pública. Emissão real aguarda D5.2.1 (OAuth2 gov.br).
Princípio §42.4 aplicado ao CNDFederalClient.

---

## 3. STEP 2 — Fix CNDFederalClient

### 3.1 — Arquivo: `modules/bidding/integrations/receita_federal/cnd_client.py`

#### URLs atualizadas

```python
# Antes (stale/404 desde ~03/2025):
BASE_URL_RFB = "https://servicos.receita.fazenda.gov.br"
# CONSULTA_URL era URL antiga 404

# Depois (D5.2):
BASE_URL_RFB = "https://servicos.receitafederal.gov.br"
CONSULTA_URL = "https://servicos.receitafederal.gov.br/servico/certidoes/"
```

#### Imports no nível de módulo (patch-friendly)

```python
from modules.integrations.brasilapi.client import BrasilAPIClient
from modules.integrations.brasilapi.exceptions import (
    BrasilAPINotFoundError,
    BrasilAPIUnavailableError,
)
```

#### consultar_cnd() — 2 tentativas (antes: 0)

```python
# Tentativa 1: portal RFB direto (falha sem auth gov.br)
try:
    response = await self._request_with_retry("GET", self.CONSULTA_URL, params={"cnpj": cnpj_limpo})
    if response.status_code == 200:
        parsed = self._parse_resultado_cnd(response.text, cnpj_limpo)
        if parsed.get("tipo_certidao") is not None:
            return parsed
except Exception as exc:
    logger.debug("CND Federal portal direto falhou: %s", exc)

# Tentativa 2: fallback BrasilAPI (§42.4 — regular=None)
cnpj_data, _ = await BrasilAPIClient().get_cnpj(cnpj_limpo)
situacao_cadastral = (cnpj_data.descricao_situacao_cadastral or "").upper()
cnpj_ativo = situacao_cadastral == "ATIVA"
return {
    "situacao": "indeterminado_portal_indisponivel",
    "regular": None,   # §42.4: NUNCA afirmar CND regular via fallback
    "cnpj_ativo_rfb": cnpj_ativo,
    "fonte": "BrasilAPI (fallback)",
    "nota": "Portal RFB indisponível ou exige login gov.br. Status CND/PGFN NÃO confirmado...",
}
```

#### verificar_regularidade() — tripartite

```python
# Antes: sem case None
# Depois:
regular = resultado.get("regular")
return {
    "apto_licitar": bool(regular) if regular is not None else None,
    "observacao": (
        "Empresa regular junto à RFB/PGFN" if regular is True
        else "Empresa com débitos federais pendentes" if regular is False
        else "Status CND federal indeterminado — portal RFB indisponivel, "
             "consultar manualmente em servicos.receitafederal.gov.br"
    ),
}
```

---

## 4. STEP 3 — Deploy

```bash
CONTAINER=conecta-pro-backend
docker cp backend/modules/bidding/integrations/receita_federal/cnd_client.py \
  $CONTAINER:/app/modules/bidding/integrations/receita_federal/cnd_client.py
docker restart $CONTAINER
# health: healthy após ~50s  ✅
```

---

## 5. STEP 4 — Validação E2E

### 4.1 — Teste live (container)

```python
from modules.bidding.integrations.receita_federal.cnd_client import CNDFederalClient
client = CNDFederalClient()
result = await client.consultar_cnd("35710481000103")
# regular=None, situacao=indeterminado_portal_indisponivel, cnpj_ativo_rfb=True  ✅
assert result["regular"] is None  # §42.4 PASS
```

### 4.2 — Pytest D5.2 (4 novos testes)

```
tests/modules/bidding/test_cnd_federal_fallback.py
  test_cnd_federal_url_atualizada                                          ✅ PASS
  test_cnd_federal_fallback_brasilapi_regular_none                         ✅ PASS
  test_cnd_federal_fallback_total_retorna_regular_none                     ✅ PASS
  test_verificar_regularidade_apto_licitar_none_quando_indeterminado       ✅ PASS
```

### 4.3 — Pytest bidding/ completo

```
tests/modules/bidding/  →  74/74 PASS  ✅
(inclui test_crf_client_fallback.py D5.1 + test_cnd_federal_fallback.py D5.2)
```

---

## 6. STEP 5 — Documentação §43 / CONTRACTS_GEDEON.md v1.44 → v1.45

```
CONTRACTS_GEDEON.md: v1.44 → v1.45 ✅
§43 adicionado:
  §43.1 — Cenário C (sem API pública RFB)
  §43.2 — Fix CNDFederalClient (URLs + imports + consultar_cnd + verificar_regularidade)
  §43.3 — Testes D5.2 (4 novos, 4/4 PASS)
  §43.4 — Princípio §42.4 reafirmado para todos os clientes de certidão
  §43.5 — Backlog D5.x atualizado (D5.2 ✅, D5.2.1 OAuth2 adicionado)
```

Commit docs: `ed0a27a6`

---

## 7. STEP 6 — Commits

```
ed0a27a6  docs(integrations): CONTRATO v1.45 — §43 D5.2 fix CND Federal endpoint
6886fbbf  refactor(integrations): D5.2 fix CNDFederalClient URL + fallback semântico (§43)
Push: ✅ origin/feature/people-management-reorganization
```

**Arquivos commitados:**
```
CONTRACTS_GEDEON.md
backend/modules/bidding/integrations/receita_federal/cnd_client.py
backend/tests/modules/bidding/test_cnd_federal_fallback.py
```

---

## 8. ROGUES — ANTES/DEPOIS

| Rogue | Antes | Depois |
|-------|-------|--------|
| `crf_client.py:154` (CNPJ) | ⚠️ httpx direto + bug semântico | ✅ BrasilAPIClient + regular=None (D5.1) |
| `cnd_client.py` (URL stale) | ⚠️ URL 404 + sem fallback | ✅ URL nova + BrasilAPIClient + regular=None (D5.2) |
| `diarist_controller.py:133` (CPF) | ⚠️ httpx direto (cpf/v1/ deprecated) | ⚠️ mantido — Cenário B (D5.1.1) |

**Rogues restantes: 1** (diarist_controller — cpf/v1/ deprecated, aguarda fonte alternativa)

---

## 9. VALIDAÇÕES 🔴

| Label | Critério | Resultado |
|-------|----------|-----------|
| 🔴 A | Pytest bidding/ preservado + 4 novos D5.2 | ✅ 74/74 PASS |
| 🔴 B | CONSULTA_URL não contém domínio 404 antigo | ✅ `receitafederal.gov.br` presente |
| 🔴 C | consultar_cnd fallback retorna regular=None | ✅ assert explícito + 4 testes |
| 🔴 D | verificar_regularidade apto_licitar=None quando regular=None | ✅ |
| 🔴 E | Zero httpx direto em cnd_client.py | ✅ BrasilAPIClient (módulo) |
| 🔴 F | Frontend BUILD_ID não mudou | ✅ zero toque em frontend |
| 🔴 G | Trilogia preservada | ✅ 18/1237/0/32 kits/docs/fake/templates |
| 🔴 H | Zero diff zonas proibidas | ✅ git diff só arquivos autorizados |

---

## 10. SELF-CHECK

- [x] STEP 0 — pré-voo: v1.44, 18/1237/0, CNDFederalClient presente ✅
- [x] STEP 1 — curl RFB: URL antiga 404, nova exige auth. Cenário C ✅
- [x] STEP 2 — cnd_client.py: URL + imports + consultar_cnd + verificar_regularidade ✅
- [x] STEP 3 — deploy hot copy + restart → healthy ✅
- [x] STEP 4 — E2E: regular=None live, pytest 4/4 D5.2, 74/74 bidding ✅
- [x] STEP 5 — §43 v1.45 commitado (ed0a27a6) ✅
- [x] STEP 6 — código commitado (6886fbbf) + push ✅
- [x] 🔴 A, B, C, D, E, F, G, H — PASS ✅

---

## 11. CENÁRIO IDENTIFICADO

**Cenário C** (previsto no prompt):

> Portal RFB tem mudança de URL ou exige auth: PAUSAR emissão real.
> Atualizar URL + adicionar fallback BrasilAPI com regular=None.
> Emissão real aguarda D5.2.1 (OAuth2 gov.br).

`servicos.receitafederal.gov.br/servico/certidoes/` retorna HTML + hCaptcha.
Sem endpoint de CNPJ público. STEP de OAuth2 postergado para D5.2.1.

---

## 12. TABELA §42.4 — STATUS DOS CLIENTES

| Cliente | Portal | Fallback BrasilAPI | regular=None |
|---------|--------|-------------------|-------------|
| `CRFFGTSClient` | Caixa/FGTS | ✅ `BrasilAPIClient().get_cnpj()` | ✅ D5.1 |
| `CNDFederalClient` | RFB/PGFN | ✅ `BrasilAPIClient().get_cnpj()` | ✅ D5.2 |
| `CNDTTrabalhistaClient` | TST | ⚠️ pendente ViewState fix | 🔄 D5.3 |

---

## 13. D5.2 PRONTO

**URL CND Federal:** `servicos.receitafederal.gov.br/servico/certidoes/` (substituiu 404 antigo).

**Fallback semântico:** `regular=None` quando portal RFB indisponível — nunca afirmar
regularidade CND baseado em CNPJ ativo na RFB (§42.4).

**Pytest:** 74/74 bidding PASS. 4 novos testes D5.2.

Jordan CIC:
**(a)** Cenário C: portal RFB exige login gov.br. Para D5.2.1 precisamos implementar
OAuth2 gov.br no `cnd_client.py` para emissão real. Aguardo sua direção de priorização.

**(b)** O dashboard de certidões deve tratar `regular=null` com semáforo amarelo
"Indeterminado — verificar manualmente" (D5.5).

**(c)** Backlog D5.3: `CNDTTrabalhistaClient` tem bug de ViewState JSF — mesmo
fix semântico de regular=None + BrasilAPIClient pendente.

Commits: `ed0a27a6` (docs) · `6886fbbf` (código) — `feature/people-management-reorganization` ✅
