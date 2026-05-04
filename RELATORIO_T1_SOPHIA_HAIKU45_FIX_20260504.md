# RELATÓRIO T1 — SOPHIA HAIKU 4.5 FIX
**Data:** 2026-05-04
**Sessão:** tmux-t1 | **Módulo:** gedeon/sophia
**Branch:** feature/people-management-reorganization
**Commit:** `6c91be4a`

---

## 1. Objetivo

Substituir o modelo deprecated `claude-3-haiku-20240307` (HTTP 404 na Anthropic desde 19/04/2026)
pela constante lida do `.env` (`LLM_MODEL=claude-haiku-4-5-20251001`).

---

## 2. STEP 1 — Estado Anterior Confirmado

```
# sophia.py linha 38 (antes):
ANTHROPIC_MODEL = "claude-3-haiku-20240307"

# .env vars relevantes:
LLM_MODEL=claude-haiku-4-5-20251001       ← modelo correto já definido
ANTHROPIC_API_KEY=sk-ant-api03-*** REDACTED ***
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022  ← não usado por sophia.py
```

`import os` confirmado na linha 27 do arquivo.

---

## 3. STEP 2 — Fix Aplicado

**Arquivo:** `backend/modules/gedeon/agents/sophia.py`
**Linha:** 38
**Mudança (cirúrgica — 1 linha):**

```python
# ANTES:
ANTHROPIC_MODEL = "claude-3-haiku-20240307"

# DEPOIS:
ANTHROPIC_MODEL = os.getenv("LLM_MODEL", "claude-haiku-4-5-20251001")
```

Backup criado: `backend/modules/gedeon/agents/sophia.py.bak`

---

## 4. STEP 4 — Deploy

```bash
docker cp backend/modules/gedeon/agents/sophia.py \
  conecta-pro-backend:/app/modules/gedeon/agents/sophia.py
docker restart conecta-pro-backend
```

---

## 5. STEP 5 — Validação via Logs

```
# Startups ANTERIORES ao fix (todos com fallback):
2026-05-03 20:11:55  SOPHIA v2.0 startup: 617 documentos, motor=sophia_dense_1536
SOPHIA v2.0: Anthropic indisponível (Error code: 404 - model: claude-3-haiku-20240307) — usando dense fallback

2026-05-04 00:33:33  SOPHIA v2.0 startup: 617 documentos, motor=sophia_dense_1536
SOPHIA v2.0: Anthropic indisponível (Error code: 404 - model: claude-3-haiku-20240307) — usando dense fallback

# Startup APÓS o fix:
2026-05-04 17:11:46  SOPHIA v2.0 startup: 617 documentos, motor=anthropic_haiku_1536  ✅
2026-05-04 17:11:47  SOPHIA v2.0 startup: 617 documentos, motor=anthropic_haiku_1536  ✅
```

Zero mensagens "Anthropic indisponível" após o restart.

---

## 6. STEP 6 — Validação via Endpoint `/sophia/status`

```json
HTTP 200

{
  "versao": "2.0",
  "motor_ativo": "anthropic_haiku_1536",
  "using_anthropic": true,
  "dimensao_embedding": 1536,
  "total_documentos": 617,
  "documentos_com_embedding_v2": 617,
  "modelo_embedding": "anthropic_haiku_1536",
  "status": "operacional",
  "modulos_escopo": ["dp","rh","ged","operacional","fiscal","contratos","licitacoes","financeiro"],
  "distribuicao_modulos": {
    "contratos": 3, "dp": 338, "financeiro": 89, "fiscal": 64,
    "ged": 30, "licitacoes": 12, "operacional": 2, "operacoes": 48, "rh": 31
  }
}
```

**Resultado:** `"using_anthropic": true` ✅ — motor premium ativo.

---

## 7. STEP 7 — Commit e Push

```
Commit: 6c91be4a
Mensagem: fix(sophia): Haiku 3 deprecated → Haiku 4.5 via env (§55)
Branch: feature/people-management-reorganization
Push: ✅ origin/feature/people-management-reorganization
```

---

## 8. Resumo Executivo

| Item | Antes | Depois |
|------|-------|--------|
| `ANTHROPIC_MODEL` | `"claude-3-haiku-20240307"` (hardcoded, deprecated) | `os.getenv("LLM_MODEL", "claude-haiku-4-5-20251001")` |
| `motor_ativo` | `sophia_dense_1536` (fallback) | `anthropic_haiku_1536` (premium) |
| `using_anthropic` | `false` | `true` |
| Erro no startup | `HTTP 404 - model not found` | nenhum |
| Arquivos modificados | — | 1 linha em `sophia.py` |

**Impacto:** SOPHIA passou de busca semântica puramente vetorial (fallback) para motor Anthropic
Haiku 4.5 com extração de termos semânticos e resposta em linguagem natural.
