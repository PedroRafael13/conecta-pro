# RELATORIO D5.3 — CNDT TST: Investigação + ROTA-FALLBACK + §42.4
**Data:** 2026-04-28
**Branch:** feature/people-management-reorganization
**Commits:** `325ae5f7` (docs v1.46) · `071d8f01` (código)

---

## 1. Timestamps

| Marco | Horário |
|-------|---------|
| T+0 (pré-voo) | 16:10:25 |
| T+30 (decisão STEP 3) | ~16:20 |
| T+final (push) | ~16:35 |

---

## 2. STEP 1 — Código lido

**`cndt_client.py` (antes D5.3):**
- URLs: `CONSULTA_URL=inicio.faces` (GET), `API_CONSULTA_URL=gerarCertidao` (POST)
- GET session + POST com `numCnpjCpf`/`tipoPessoa=J` — sem ViewState, sem cookie
- Erros retornavam `regular: False` (bug semântico — devia ser None)
- Sem BrasilAPI fallback
- `verificar_debitos()` sem tripartite (apto_licitar=False quando regular=None)

**`cnd_client.py` (referência D5.2):**
- Padrão: imports módulo + `_fallback_brasilapi` + `verificar_regularidade` tripartite

---

## 3. STEP 2 — Investigação TST (4 chamadas curl)

```
curl 1: HEAD inicio.faces          → HTTP 200 ✅
curl 2: GET  inicio.faces          → HTTP 200, 5897 bytes
  - Form: POST /inicio.faces, 2 buttons (Emitir/Validar), ViewState
  - SEM campo CNPJ (form multi-step JSF)
  - reCAPTCHA API carregada (script src)
curl 3: POST /inicio.faces (step→2) → HTTP 200, 21218 bytes
  - gerarCertidaoForm:cpfCnpj (text) ← campo CNPJ encontrado
  - resposta (text) ← captcha imagem: "Digite os caracteres da imagem"
  - tokenDesafio (hidden, value="") ← VAZIO, populado via JavaScript
  - reCAPTCHA: 3 menções no HTML
```

**Achados decisivos:**
- `tokenDesafio` vazio sem JavaScript → impossível obter o token sem browser headless
- Captcha de imagem customizado do TST (não Google reCAPTCHA, mas token JS-dependente)
- Cloudflare: NÃO detectado

---

## 4. STEP 3 — Decisão

```
Portal vivo (GET 200)?              SIM
URL canônica do form:               https://cndt-certidao.tst.jus.br/inicio.faces
ViewState extraído?                 SIM
Captcha/reCAPTCHA detectado?        SIM — captcha imagem TST (resposta+tokenDesafio)
Cloudflare/anti-bot detectado?      NÃO
Inputs step 1:                      hidden form-id, 2 submit, ViewState
Inputs step 2:                      gerarCertidaoForm:cpfCnpj, resposta, tokenDesafio
POST tentado?                       SIM (step1→step2, HTTP 200)
POST status:                        200 text/html (form CNPJ + captcha)
POST resposta reconhecível?         FORM DE ENTRADA (tokenDesafio vazio/JS)

[x] ROTA-FALLBACK: tokenDesafio requer JavaScript — impossível sem Playwright.
    Captcha detectado = critério ROTA-FALLBACK atendido.
```

---

## 5. STEP 4 — Diff resumido

| O que mudou | Antes | Depois |
|-------------|-------|--------|
| Imports | `asyncio`, `httpx` (sem BrasilAPI) | `BrasilAPIClient`, exceções (módulo) |
| `consultar_cndt()` | GET+POST TST + `regular=False` em erros | `return await self._fallback_brasilapi()` |
| `_fallback_brasilapi()` | Não existia | Adicionado: `regular=None`, `cnpj_ativo_rfb`, `fonte="BrasilAPI (fallback)"` |
| `verificar_regularidade()` | Não existia | Tripartite True/False/None → `apto_licitar=bool|None` |
| `verificar_debitos()` | `apto_licitar=False` quando None | `apto_licitar=bool(regular) if regular is not None else None` |
| `_request_with_retry()` | Presente | Removido (não necessário) |
| `_parse_resultado_cndt()` | Presente | Removido (ROTA-FALLBACK) |

---

## 6. STEP 5 — Pytest + commits

```
# Pytest D5.1+D5.2+D5.3 no container:
test_cndt_client_fallback.py::test_cndt_url_aponta_para_tst_jus_br           PASS
test_cndt_client_fallback.py::test_cndt_fallback_brasilapi_regular_none       PASS
test_cndt_client_fallback.py::test_cndt_fallback_total_retorna_regular_none   PASS
test_cndt_client_fallback.py::test_verificar_regularidade_tripartite_none     PASS
test_cndt_client_fallback.py::test_cndt_fallback_cnpj_baixado_cnpj_ativo_rfb_false PASS
test_crf_client_fallback.py  (4 testes D5.1)                                  PASS
test_cnd_federal_fallback.py (4 testes D5.2)                                  PASS
======================== 13 passed in 7.17s ========================

Live test §42.4:
  fonte: BrasilAPI (fallback)
  regular: None
  situacao: indeterminado_portal_indisponivel
  cnpj_ativo_rfb: True
  ✅ §42.4 OK — fallback retorna regular=None

Commits:
  325ae5f7  docs(integrations): CONTRATO v1.46 — §44 D5.3 CNDT TST
  071d8f01  fix(integrations): D5.3 CNDTTrabalhistaClient + §42.4 (3/3 clients)
  Push: ✅ origin/feature/people-management-reorganization
```

---

## 7. Tabela §42.4 — 3/3 clients

| Client | Portal | Fallback BrasilAPI | regular=None | Status |
|--------|--------|-------------------|-------------|--------|
| `CRFFGTSClient` | Caixa/FGTS | ✅ `get_cnpj()` | ✅ | D5.1 |
| `CNDFederalClient` | RFB/PGFN | ✅ `get_cnpj()` | ✅ | D5.2 |
| `CNDTTrabalhistaClient` | TST | ✅ `get_cnpj()` | ✅ | D5.3 |

**§42.4 aplicado a 3/3 clients. Princípio consolidado.**

---

## 8. Cenário identificado

**ROTA-FALLBACK** — Portal TST usa formulário JSF multi-step com captcha de imagem
customizado. O campo `tokenDesafio` é populado por JavaScript ao exibir o captcha,
tornando o fluxo inacessível via HTTP puro (httpx).

Não é Google reCAPTCHA (sem `data-sitekey`/`g-recaptcha-response`), mas o
efeito é equivalente: requer execução de JS para gerar o token de desafio.

---

## 9. Backlog D5.6 — Pista para Playwright

Para emissão real via Playwright:
1. `await page.goto("https://cndt-certidao.tst.jus.br/inicio.faces")`
2. `await page.click('input[value="Emitir Certidão"]')` → step 2
3. `await page.fill('input[name="gerarCertidaoForm:cpfCnpj"]', cnpj)`
4. Aguardar captcha imagem renderizar e `tokenDesafio` ser populado
5. Resolver captcha (manual ou serviço OCR para imagem simples)
6. `await page.click('input[value="Emitir Nova Certidão"]')`
7. Parse do HTML de resposta com `_parse_resultado_cndt()`

Cookie de sessão: `cookies.txt` do curl confirma que sessão persiste via cookie JSF.
