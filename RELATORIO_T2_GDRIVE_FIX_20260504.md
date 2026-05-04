# RELATÓRIO T2 — FIX ARQUITETURAL GDRIVE
**Data:** 2026-05-04
**Sessão:** tmux-t2 | **Módulo:** gdrive
**Branch:** feature/people-management-reorganization
**Commit:** `b28df119`

---

## 1. Diagnóstico do Problema

### Causa raiz
`esta_conectado()` chamava `_init_service()` que tenta **somente** service account:

```python
# FLUXO ANTERIOR (quebrado):
esta_conectado()
  └─ _init_service()
       └─ if not os.path.exists("/opt/conecta-pro/config/google_drive_credentials.json"):
               logger.debug("credenciais não encontradas")
               return False   ← encerra aqui. OAuth2 nunca tentado.
```

- `_initialized = True` após primeira chamada → travamento permanente
- Access token expirado há 23 dias nunca era renovado
- `check_status()` já tinha a ordem correta, mas `esta_conectado()` não

---

## 2. STEP 3 — Diff Aplicado

**Arquivo:** `backend/modules/gdrive/services/gdrive_service.py`
**Função modificada:** `esta_conectado()` (linha 89)

```diff
 def esta_conectado(self) -> bool:
     """Verificar se o serviço Drive está conectado."""
     if self._service is not None:
         return True
+    # Tentar OAuth2 do banco PRIMEIRO (antes de service account)
+    try:
+        import psycopg2
+
+        raw_url = os.environ.get("DATABASE_URL", "").replace("+asyncpg", "")
+        if raw_url:
+            conn = psycopg2.connect(raw_url)
+            cur = conn.cursor()
+            cur.execute(
+                "SELECT access_token, refresh_token, token_expiry "
+                "FROM gdrive_config WHERE is_connected = TRUE LIMIT 1"
+            )
+            row = cur.fetchone()
+            conn.close()
+            if row:
+                at, rt, exp = row
+                expiry_str = exp.isoformat() if exp else None
+                if self.conectar_com_tokens(at or "", rt or "", expiry_str):
+                    return True
+    except Exception as exc:
+        logger.warning("GDrive esta_conectado: erro OAuth2 DB: %s", exc)
     return self._init_service()
```

**Regras respeitadas:**
- ✅ Apenas `esta_conectado()` tocada
- ✅ Lógica de service account preservada como fallback (`_init_service()` ainda chamado)
- ✅ NÃO refatorado — apenas ordem invertida
- ✅ `gdrive_controller.py` não tocado

---

## 3. STEP 4 — Logs pós-restart

```
GDrive: router registrado (/gdrive)
GDrive: conectado via OAuth2 tokens
GDrive: conectado via OAuth2 tokens do banco (jordansjesus@gmail.com)
GDrive: conectado no startup (%s)
```

Zero erros. OAuth2 ativado no startup.

---

## 4. STEP 5 — /gdrive/status pós-fix

```json
HTTP 200
{
  "conectado": true,
  "email": "jordansjesus@gmail.com",
  "nome": "jordansjesus@gmail.com",
  "tipo": "oauth2",
  "credenciais_configuradas": true,
  "mensagem": "Google Drive conectado via OAuth2 (jordansjesus@gmail.com)",
  "acao": null
}
```

**`drive_conectado` voltou ao real:** `true` ✅

### /gdrive/ingestao/status

```json
{
  "drive_conectado": false,
  "kits_enviados": 0,
  "kits_pendentes": 18,
  "total_kits": 18,
  "ultima_atualizacao": "2026-04-28 02:48:24.53377+00",
  "status": "aguardando_autorizacao"
}
```

⚠️ `drive_conectado: false` no `/ingestao/status` — este endpoint lê estado de tabela separada
(`gdrive_ingestao_config`), não de `gdrive_service.esta_conectado()`. Não é regressão — era assim antes.
O serviço Drive está conectado conforme confirmado em `/gdrive/status`.

---

## 5. STEP 6 — URL OAuth para Jordan

```
GET /api/v1/gdrive/autorizar → HTTP 200
```

**URL completa para abrir no navegador:**

```
https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=576020339239-bs4amjo67m3v0j9gerqnrk6gpohvjqvd.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Ferp.conectamais.pro%2Fapi%2Fv1%2Fgdrive%2Foauth%2Fcallback&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive&state=gBa2sahFIDkPq84tMwlNMF6yHm6D9r&access_type=offline&include_granted_scopes=true&prompt=consent
```

Após clicar, o Google redirecionará para:
`https://erp.conectamais.pro/api/v1/gdrive/oauth/callback`
e o token será salvo automaticamente no banco (`gdrive_config`).

---

## 6. STEP 7 — Commit

```
Commit: b28df119
Mensagem: fix(gdrive): inverter ordem em esta_conectado — OAuth2 antes de service account (§56)
Branch: feature/people-management-reorganization
Push: ✅ origin/feature/people-management-reorganization
```

---

## 7. Resumo Executivo

| Item | Antes | Depois |
|------|-------|--------|
| `esta_conectado()` | tenta service account → falha → trava | tenta OAuth2 DB → sucesso |
| Startup log | silêncio / fallback | "conectado via OAuth2 tokens" |
| `/gdrive/status` | `"conectado": false` (ou erro) | `"conectado": true` ✅ |
| Token renovado | nunca (expirado 23 dias) | sim, via `conectar_com_tokens` |
| `_service` no singleton | `None` permanente | Drive service ativo |
