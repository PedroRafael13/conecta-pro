# RELATORIO D5.3.1 — Auditoria §42.4: SefazAMClient + PrefeituraManausClient
**Data:** 2026-04-28
**Branch:** feature/people-management-reorganization

---

## 1. Timestamps

| Marco | Horário |
|-------|---------|
| T+0 (pré-voo) | 17:18:19 |
| T+25 (decisão STEP 3) | ~17:28 |
| T+final | ~17:35 |

---

## 2. STEP 1 — Auditoria SefazAMClient

Arquivo: `backend/modules/bidding/integrations/receita_federal/sefaz_am_client.py`

| Pergunta | Resposta |
|----------|----------|
| P1. Try/except captura erro? | SIM — `for url_base in SEFAZ_URLS: try/except Exception: continue` |
| P2. Em erro, retorna? | `regular=None` + `requer_manual=True` — não False, não True |
| P3. Fallback BrasilAPI? | NÃO — cai em bloco final "portal inacessivel" |
| P4. Fallback afirma regular=True via CNPJ? | N/A — sem BrasilAPI |
| P5. verificar_regularidade trata None? | SIM — `resultado.get("regular", False)` retorna `None` quando chave existe com valor None; `apto_licitar=None` |

Fluxo portal inacessível (linha ~162):
```python
return {
    "regular": None,      # ← §42.4 satisfeito
    "requer_manual": True,
    "situacao": "requer_manual",
    ...
}
```

verificar_regularidade (linha ~189):
```python
"apto_licitar": resultado.get("regular", False),  # → None quando regular=None
```

---

## 3. STEP 2 — Auditoria PrefeituraManausClient

Arquivo: `backend/modules/bidding/integrations/receita_federal/prefeitura_manaus_client.py`

Estrutura idêntica ao SefazAMClient. Mesmas respostas P1–P5.

Fluxo portal inacessível:
```python
return {
    "regular": None,      # ← §42.4 satisfeito
    "requer_manual": True,
    "situacao": "requer_manual",
    ...
}
```

---

## 4. STEP 3 — Tabela de Decisão

| Client | Tem fallback inseguro? | Fallback afirma regular=True via CNPJ? | verificar_regularidade trata None? | Decisão |
|--------|------------------------|----------------------------------------|-------------------------------------|---------|
| SefazAMClient | NÃO | N/A | SIM | **OK** |
| PrefeituraManausClient | NÃO | N/A | SIM | **OK** |

**Critério D5.3.1:**
- Nenhum dos dois usa BrasilAPI → §42.4 não pode ser violado por eles
- Portal inacessível → `regular=None` (não `False`) → sem falso negativo de irregularidade
- `verificar_regularidade`: `.get("regular", False)` retorna `None` quando chave existe com `None` → `apto_licitar=None` ✅

---

## 5. STEP 4 — Fixes aplicados

**Nenhum.** Ambos os clients já satisfazem §42.4. Regra: "se não tá quebrado, não conserta."

---

## 6. STEP 5 — Validação + Pytest

Pytest: apenas testes D5.1+D5.2+D5.3 (sem novos testes — nenhum fix aplicado).

```
test_crf_client_fallback.py      4/4 PASS  (D5.1)
test_cnd_federal_fallback.py     4/4 PASS  (D5.2)
test_cndt_client_fallback.py     5/5 PASS  (D5.3)
======================== 13 passed ========================
```

Sem deploy necessário (zero mudança de código).

---

## 7. Tabela §42.4 Final — 5/5 clients

| Client | Fonte direta | Fallback quando portal cai | regular=None | Status |
|--------|--------------|---------------------------|--------------|--------|
| `CRFFGTSClient` | Caixa/FGTS | BrasilAPI `get_cnpj()` | ✅ | D5.1 |
| `CNDFederalClient` | RFB/PGFN | BrasilAPI `get_cnpj()` | ✅ | D5.2 |
| `CNDTTrabalhistaClient` | TST | BrasilAPI `get_cnpj()` | ✅ | D5.3 |
| `SefazAMClient` | Sefaz-AM | Bloco manual (`requer_manual=True`) | ✅ | D5.3.1 auditado |
| `PrefeituraManausClient` | SEMEF/Manaus | Bloco manual (`requer_manual=True`) | ✅ | D5.3.1 auditado |

**§42.4 aplicado a 5/5 clients. Princípio consolidado antes do D5.4.**

---

## 8. Tempo total

~17min (T+0 17:18 → T+final ~17:35). Hard limit 45min — margem de ~28min.

---

## 9. Próximo passo

**D5.4 desbloqueado:** todos os 5 clients §42.4-compliant.
CertidoesUpdaterService pode integrar todos sem risco de afirmar regularidade
baseado em fallback inseguro.
