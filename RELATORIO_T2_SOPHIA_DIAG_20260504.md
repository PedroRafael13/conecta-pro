# RELATÓRIO T2 — DIAGNÓSTICO SOPHIA MODELO
**Data:** 2026-05-04
**Sessão:** tmux-t2 | **Módulo:** gedeon/sophia (read-only)
**Branch:** feature/people-management-reorganization
**Início:** 15:10:20 | **Fim:** 15:14:06

---

## 1. Ocorrências do modelo deprecated

```
backend/tests/_orphaned/test_llm_provider.py:30:
  assert LLMModel.CLAUDE_3_HAIKU.value == "claude-3-haiku-20240307"

backend/modules/gedeon/agents/sophia.py:8:
  Motor: Anthropic API (claude-3-haiku) + fallback dense 1536 dims  ← docstring

backend/modules/gedeon/agents/sophia.py:38:
  ANTHROPIC_MODEL = "claude-3-haiku-20240307"  ← CONSTANTE CAUSADORA DO ERRO

backend/modules/gedeon/agents/sophia.py:574:
  Motor: Anthropic claude-3-haiku (primário) + dense 1536 fallback.  ← docstring

backend/modules/ai/conversation/services/llm_provider.py:28:
  CLAUDE_3_HAIKU = "claude-3-haiku-20240307"  ← enum, não usado diretamente
```

---

## 2. sophia.py — contexto completo do uso do modelo

O modelo é referenciado em **3 locais funcionais** dentro de `sophia.py`:

| Linha | Uso | Contexto |
|-------|-----|---------|
| 38 | `ANTHROPIC_MODEL = "claude-3-haiku-20240307"` | Constante global — **fonte do erro** |
| `__init__` | `model=ANTHROPIC_MODEL, max_tokens=5` | Teste de conectividade no startup |
| `busca_semantica` | `model=ANTHROPIC_MODEL, max_tokens=100` | Extração de termos semânticos |
| `perguntar_linguagem_natural` | `model=ANTHROPIC_MODEL, max_tokens=200` | Resposta em linguagem natural |

---

## 3. Imports e setup Anthropic em sophia.py

```python
# linha 585-592
api_key = os.getenv("ANTHROPIC_API_KEY", "")
if not api_key:
    logger.info("SOPHIA v2.0: ANTHROPIC_API_KEY não configurada — usando dense fallback")
    ...
    import anthropic
    self._client = anthropic.Anthropic(api_key=api_key)
```

- Usa `anthropic.Anthropic` (síncrono, não `AsyncAnthropic`)
- API key lida de `ANTHROPIC_API_KEY` — **existe no `.env`** ✅
- Modelo **não lido do env** — constante hardcoded na linha 38

---

## 4. Variáveis de ambiente

| Arquivo | Variável | Valor |
|---------|----------|-------|
| `.env` | `LLM_MODEL` | `claude-haiku-4-5-20251001` ← modelo correto já definido |
| `.env` | `ANTHROPIC_API_KEY` | `sk-ant-api03-...` (presente) |
| `.env` | `ANTHROPIC_MODEL` | `claude-3-5-sonnet-20241022` |
| `backend/.env` | `LLM_MODEL` | `gpt-4o-mini` |

**Diagnóstico:** `.env` já tem `LLM_MODEL=claude-haiku-4-5-20251001`. `sophia.py` ignora essa variável — usa constante hardcoded.

---

## 5. Todos os arquivos que usam Anthropic

| Arquivo | Status modelo |
|---------|---------------|
| `backend/modules/gedeon/agents/sophia.py` | 🔴 `claude-3-haiku-20240307` hardcoded — deprecated |
| `backend/modules/ai/conversation/services/llm_provider.py` | ✅ usa `settings.LLM_MODEL` via env |
| `backend/modules/people_management/human_resources/services/resume_parser_service.py` | ✅ `claude-sonnet-4-20250514` — válido |

---

## 6. Logs do warning SOPHIA

Erro ocorre a cada restart do container (teste de conectividade no `__init__`):

```
2026-05-02 15:35:48 SOPHIA v2.0 startup: 617 documentos indexados, motor=sophia_dense_1536
SOPHIA v2.0: Anthropic indisponível (Error code: 404 - model: claude-3-haiku-20240307) — usando dense fallback

2026-05-03 20:11:55 SOPHIA v2.0 startup: 617 documentos indexados, motor=sophia_dense_1536
SOPHIA v2.0: Anthropic indisponível (Error code: 404 - model: claude-3-haiku-20240307) — usando dense fallback

2026-05-04 00:33:33 SOPHIA v2.0 startup: 617 documentos indexados, motor=sophia_dense_1536
SOPHIA v2.0: Anthropic indisponível (Error code: 404 - model: claude-3-haiku-20240307) — usando dense fallback
```

Padrão: **sempre** cai no fallback. A cada reinício do backend.

---

## 7. Endpoint /sophia/status

```
HTTP 200

{
  "versao": "2.0",
  "motor_ativo": "sophia_dense_1536",
  "using_anthropic": false,
  "dimensao_embedding": 1536,
  "total_documentos": 617,
  "documentos_com_embedding_v2": 617,
  "modelo_embedding": "sophia_dense_1536",
  "status": "operacional",
  "modulos_escopo": ["dp","rh","ged","operacional","fiscal","contratos","licitacoes","financeiro"],
  "distribuicao_modulos": {
    "dp": 338, "operacoes": 48, "financeiro": 89, "fiscal": 64,
    "rh": 31, "ged": 30, "licitacoes": 12, "contratos": 3, "operacional": 2
  }
}
```

---

## Mapa do Fix (NÃO aplicado — diagnóstico apenas)

**Arquivo:** `backend/modules/gedeon/agents/sophia.py`
**Linha:** 38
**Mudança:**
```python
# ANTES (deprecated, causa 404 na Anthropic):
ANTHROPIC_MODEL = "claude-3-haiku-20240307"

# DEPOIS (lê do .env, fallback para haiku-4-5):
ANTHROPIC_MODEL = os.getenv("LLM_MODEL", "claude-haiku-4-5-20251001")
```

**Impacto:** 1 linha. Após `docker cp` + `kill -HUP 1`, SOPHIA passa de `using_anthropic: false` para `true`, motor premium ativo.

**Arquivos secundários (não urgentes):**
- `llm_provider.py:28` — enum CLAUDE_3_HAIKU desatualizado (não causa erro em prod)
- `sophia.py` docstrings linha 8 e 574 — mencionam "claude-3-haiku" (cosmético)
